package astral;

import java.sql.*;
import java.nio.file.*;
import java.util.*;

/** All money is integer cents. One serialized connection; each match is a transaction.
 * Custody (wallet/claims) is independent of Vault/player files. Transfers use a durable
 * journal in AstralBazar; an ambiguous external transfer is never automatically replayed.
 */
public final class BazarStore implements AutoCloseable {
    public record Product(String id, long min, long max) {}
    public record Order(long id, String owner, String product, boolean buy, int quantity,
                        int remaining, long price, long gross, long tax, int filled, boolean cancelled) {}
    public record Claim(long id, String owner, String product, int qty, byte[] item, String basket) {}
    public record Transfer(long id, String owner, String kind, long cents, double before,
                           long claim, String product, int qty, byte[] item, String basket) {}
    public record Level(long price, int qty, int orders) {}
    public record Fill(int qty, long gross, long tax) {}
    final Connection db;
    final Map<String,Product> products;
    boolean dynamicEnabled=true;
    public record Range(long min,long max,int lowDirection,int highDirection) {
        public String arrow(){return (lowDirection>0||highDirection>0?"↑":"")+(lowDirection<0||highDirection<0?"↓":"");}
    }
    public BazarStore(Path file, Map<String,Product> products) throws Exception {
        this.products = products;
        db = DriverManager.getConnection("jdbc:sqlite:" + file.toAbsolutePath());
        sql("PRAGMA journal_mode=WAL"); sql("PRAGMA synchronous=FULL"); sql("PRAGMA busy_timeout=3000");
        sql("CREATE TABLE IF NOT EXISTS wallet(owner TEXT PRIMARY KEY,cents INTEGER NOT NULL CHECK(cents>=0))");
        sql("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,owner TEXT NOT NULL,product TEXT NOT NULL,buy INTEGER NOT NULL,quantity INTEGER NOT NULL,remaining INTEGER NOT NULL CHECK(remaining>=0),price INTEGER NOT NULL,gross INTEGER NOT NULL DEFAULT 0,tax INTEGER NOT NULL DEFAULT 0,filled INTEGER NOT NULL DEFAULT 0,cancelled INTEGER NOT NULL DEFAULT 0)");
        sql("CREATE INDEX IF NOT EXISTS book ON orders(product,buy,price,id) WHERE remaining>0");
        sql("CREATE INDEX IF NOT EXISTS owners ON orders(owner,remaining)");
        sql("CREATE TABLE IF NOT EXISTS claims(id INTEGER PRIMARY KEY AUTOINCREMENT,owner TEXT NOT NULL,product TEXT NOT NULL,qty INTEGER NOT NULL CHECK(qty>=0),item BLOB,basket TEXT NOT NULL DEFAULT '')");
        sql("CREATE INDEX IF NOT EXISTS claims_owner ON claims(owner,basket,product)");
        boolean hasOrder=false;
        try(var q=db.createStatement();var r=q.executeQuery("PRAGMA table_info(claims)")){while(r.next())if(r.getString("name").equals("order_id"))hasOrder=true;}
        if(!hasOrder)sql("ALTER TABLE claims ADD COLUMN order_id INTEGER NOT NULL DEFAULT 0");
        sql("CREATE TABLE IF NOT EXISTS order_credit(order_id INTEGER PRIMARY KEY,owner TEXT NOT NULL,cents INTEGER NOT NULL CHECK(cents>=0))");
        sql("CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,product TEXT,buyer TEXT,seller TEXT,qty INTEGER,price INTEGER,tax INTEGER,at INTEGER)");
        sql("CREATE INDEX IF NOT EXISTS history ON trades(product,at)");
        sql("CREATE TABLE IF NOT EXISTS journal(id INTEGER PRIMARY KEY AUTOINCREMENT,owner TEXT,kind TEXT,cents INTEGER,before_balance REAL,claim_id INTEGER,product TEXT,qty INTEGER,item BLOB,basket TEXT,state TEXT NOT NULL DEFAULT 'pending')");
        sql("CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,at INTEGER,owner TEXT,action TEXT,detail TEXT)");
        sql("CREATE TABLE IF NOT EXISTS price_limits(product TEXT PRIMARY KEY,min INTEGER NOT NULL,max INTEGER NOT NULL,low_idle INTEGER NOT NULL DEFAULT 0,high_idle INTEGER NOT NULL DEFAULT 0,day TEXT NOT NULL DEFAULT '',low_dir INTEGER NOT NULL DEFAULT 0,high_dir INTEGER NOT NULL DEFAULT 0)");
        for(var p:products.values())sql("INSERT OR IGNORE INTO price_limits(product,min,max) VALUES(?,?,?)",p.id,p.min,p.max);
    }
    public synchronized Range range(String id)throws SQLException {
        var p=products.get(id);if(p==null)throw new IllegalArgumentException("Producto desconocido");
        if(!dynamicEnabled)return new Range(p.min,p.max,0,0);
        try(var q=db.prepareStatement("SELECT min,max,low_dir,high_dir FROM price_limits WHERE product=?")) {
            bind(q,id);try(var r=q.executeQuery()){if(r.next())return new Range(r.getLong(1),r.getLong(2),r.getInt(3),r.getInt(4));}
        }return new Range(p.min,p.max,0,0);
    }
    /** Single fixed 24h window, committed once per product/day. Never replay missed days. */
    public synchronized void adjustRanges(String day,long end,double cap)throws Exception {
        if(!dynamicEnabled)return;
        if(!Double.isFinite(cap)||cap<1||cap>100)throw new IllegalArgumentException("Tope dinámico inválido");
        tx(()->{
            for(var p:products.values()) {
                long min,max;int lowIdle,highIdle;
                try(var q=db.prepareStatement("SELECT * FROM price_limits WHERE product=?")) {
                    bind(q,p.id);try(var r=q.executeQuery()){
                        if(!r.next()||r.getString("day").compareTo(day)>=0)continue;
                        min=r.getLong("min");max=r.getLong("max");lowIdle=r.getInt("low_idle");highIdle=r.getInt("high_idle");
                    }
                }
                long total=0,low=0,high=0;
                Set<String> lb=new HashSet<>(),ls=new HashSet<>(),hb=new HashSet<>(),hs=new HashSet<>();
                long edge=(max-min)/20;
                try(var q=db.prepareStatement("SELECT buyer,seller,qty,price FROM trades WHERE product=? AND at>=? AND at<? AND qty>0 AND buyer<>seller")) {
                    bind(q,p.id,end-86400000L,end);try(var r=q.executeQuery()){while(r.next()) {
                        long qty=r.getLong(3),price=r.getLong(4);total+=qty;
                        if(price>=max-edge){high+=qty;hb.add(r.getString(1));hs.add(r.getString(2));}
                        if(price<=min+edge){low+=qty;lb.add(r.getString(1));ls.add(r.getString(2));}
                    }}
                }
                boolean up=total>0&&high*2>=total&&hb.size()>=3&&hs.size()>=3;
                boolean down=total>0&&low*2>=total&&lb.size()>=3&&ls.size()>=3;
                // Only qualifying diverse activity resets inactivity; one player cannot pin a moved limit.
                highIdle=up?0:Math.min(3,highIdle+1);lowIdle=down?0:Math.min(3,lowIdle+1);
                long nextMax=max,nextMin=min;
                if(up)nextMax=Math.min((long)Math.floor(p.max*cap),Math.max(max+1,Math.round(max*1.05)));
                else if(highIdle>=3)nextMax=Math.max(p.max,Math.round(max*.95));
                if(down)nextMin=Math.max(1,Math.min(min-1,Math.round(min*.95)));
                else if(lowIdle>=3)nextMin=Math.min(p.min,Math.round(min*1.05));
                nextMax=Math.max(p.max,Math.min((long)Math.floor(p.max*cap),nextMax));
                nextMin=Math.min(p.min,nextMin);
                sql("UPDATE price_limits SET min=?,max=?,low_idle=?,high_idle=?,day=?,low_dir=?,high_dir=? WHERE product=?",nextMin,nextMax,lowIdle,highIdle,day,Long.compare(nextMin,min),Long.compare(nextMax,max),p.id);
                audit("server","price_limits",p.id+" "+day+" "+nextMin+".."+nextMax);
            }
            return null;
        });
    }
    public synchronized void sql(String s, Object... args) throws SQLException {
        try (var q=db.prepareStatement(s)) { bind(q,args); q.execute(); }
    }
    static void bind(PreparedStatement q,Object...args) throws SQLException {
        for(int i=0;i<args.length;i++) q.setObject(i+1,args[i]);
    }
    long scalar(String s,Object...args) throws SQLException {
        try(var q=db.prepareStatement(s)) {bind(q,args);try(var r=q.executeQuery()){return r.next()?r.getLong(1):0;}}
    }
    long insert(String s,Object...args) throws SQLException {sql(s,args); return scalar("SELECT last_insert_rowid()");}
    interface Work<T>{T run() throws Exception;}
    synchronized <T>T tx(Work<T> w) throws Exception {
        if(!db.getAutoCommit())return w.run();
        db.setAutoCommit(false);
        try {T result=w.run();db.commit();return result;}
        catch(Exception e){db.rollback();throw e;}
        finally {db.setAutoCommit(true);}
    }
    void audit(String owner,String action,String detail) throws SQLException {
        sql("INSERT INTO audit(at,owner,action,detail) VALUES(?,?,?,?)",System.currentTimeMillis(),owner,action,detail);
    }
    public synchronized long wallet(String owner) throws SQLException {return scalar("SELECT cents FROM wallet WHERE owner=?",owner);}
    void credit(String owner,long n) throws SQLException {
        sql("INSERT INTO wallet(owner,cents) VALUES(?,?) ON CONFLICT(owner) DO UPDATE SET cents=cents+excluded.cents",owner,n);
    }
    void debit(String owner,long n) throws Exception {
        debit(owner,n,0);
    }
    void debit(String owner,long n,long preferred) throws Exception {
        if(n<0||wallet(owner)<n)throw new IllegalArgumentException("Plata insuficiente en el Bazar.");
        sql("UPDATE wallet SET cents=cents-? WHERE owner=?",n,owner);
        var credits=new ArrayList<long[]>();
        try(var q=db.prepareStatement("SELECT order_id,cents FROM order_credit WHERE owner=? AND cents>0 ORDER BY (order_id=?) DESC,order_id")){
            bind(q,owner,preferred);try(var r=q.executeQuery()){while(r.next())credits.add(new long[]{r.getLong(1),r.getLong(2)});}
        }
        long left=n;for(var c:credits){long take=Math.min(left,c[1]);sql("UPDATE order_credit SET cents=cents-? WHERE order_id=?",take,c[0]);left-=take;if(left==0)break;}
    }
    void creditOrder(String owner,long n,long order)throws SQLException {
        credit(owner,n);sql("INSERT INTO order_credit(order_id,owner,cents) VALUES(?,?,?) ON CONFLICT(order_id) DO UPDATE SET cents=cents+excluded.cents",order,owner,n);
    }
    public synchronized long orderMoney(String owner,long order)throws SQLException{return scalar("SELECT cents FROM order_credit WHERE owner=? AND order_id=?",owner,order);}
    public synchronized long claimOrder(long claim)throws SQLException{return scalar("SELECT order_id FROM claims WHERE id=?",claim);}
    public synchronized Set<Long> claimableOrders(String owner)throws SQLException {
        Set<Long> out=new HashSet<>();try(var q=db.prepareStatement("SELECT DISTINCT order_id FROM claims WHERE owner=? AND qty>0 AND basket='' UNION SELECT order_id FROM order_credit WHERE owner=? AND cents>0")){
            bind(q,owner,owner);try(var r=q.executeQuery()){while(r.next())out.add(r.getLong(1));}
        }return out;
    }
    long claimOrder(String owner,String product,int qty,long order)throws SQLException {
        long id=claim(owner,product,qty,null,"");if(id>0)sql("UPDATE claims SET order_id=? WHERE id=?",order,id);return id;
    }
    public synchronized List<Order> orders(String owner) throws SQLException {
        var out=new ArrayList<Order>();
        try(var q=db.prepareStatement("SELECT * FROM orders WHERE owner=? ORDER BY (remaining>0) DESC,id DESC LIMIT 100")){
            bind(q,owner);try(var r=q.executeQuery()){while(r.next())out.add(order(r));}
        }return out;
    }
    static Order order(ResultSet r)throws SQLException{return new Order(r.getLong("id"),r.getString("owner"),r.getString("product"),r.getBoolean("buy"),r.getInt("quantity"),r.getInt("remaining"),r.getLong("price"),r.getLong("gross"),r.getLong("tax"),r.getInt("filled"),r.getBoolean("cancelled"));}
    public synchronized List<Level> book(String product,boolean buy)throws SQLException {
        var out=new ArrayList<Level>();
        try(var q=db.prepareStatement("SELECT price,SUM(remaining),COUNT(*) FROM orders WHERE product=? AND buy=? AND remaining>0 GROUP BY price ORDER BY price "+(buy?"DESC":"ASC")+" LIMIT 7")){
            bind(q,product,buy);try(var r=q.executeQuery()){while(r.next())out.add(new Level(r.getLong(1),r.getInt(2),r.getInt(3)));}
        }return out;
    }
    public synchronized List<Claim> claims(String owner)throws SQLException {
        var out=new ArrayList<Claim>();
        try(var q=db.prepareStatement("SELECT * FROM claims WHERE owner=? AND qty>0 ORDER BY id")) {
            bind(q,owner);try(var r=q.executeQuery()){while(r.next())out.add(new Claim(r.getLong("id"),owner,r.getString("product"),r.getInt("qty"),r.getBytes("item"),r.getString("basket")));}
        }return out;
    }
    long claim(String owner,String product,int qty,byte[] item,String basket)throws SQLException {
        if(qty<=0)return 0;
        return insert("INSERT INTO claims(owner,product,qty,item,basket) VALUES(?,?,?,?,?)",owner,product,qty,item,basket);
    }
    public synchronized int available(String owner,String product)throws SQLException {
        return (int)scalar("SELECT COALESCE(SUM(qty),0) FROM claims WHERE owner=? AND product=? AND basket=''",owner,product);
    }
    void consume(String owner,String product,int qty)throws Exception {
        if(available(owner,product)<qty)throw new IllegalArgumentException("No tenés suficientes productos idénticos.");
        int left=qty;
        for(var c:claims(owner))if(c.basket.isEmpty()&&c.product.equals(product)&&left>0){int n=Math.min(left,c.qty);sql("UPDATE claims SET qty=qty-? WHERE id=?",n,c.id);left-=n;}
    }
    public static long tax(long gross){return (Math.multiplyExact(gross,125)+5000)/10000;}
    public synchronized long create(String owner,String id,boolean buy,int qty,long price,boolean instant)throws Exception {
        return tx(()->{
            Product p=products.get(id);
            if(p==null)throw new IllegalArgumentException("Producto no habilitado; solo materiales Astrales.");
            if(qty<1||qty>71680)throw new IllegalArgumentException("Cantidad: 1 a 71.680.");
            // Old makers remain executable when reference limits change.
            // Bounds apply to new resting orders; instant prices come from the book.
            var bounds=range(id);
            if(price<1||(!instant&&(price<bounds.min||price>bounds.max)))throw new IllegalArgumentException("Precio fuera de rango.");
            if(!instant&&scalar("SELECT COUNT(*) FROM orders WHERE owner=? AND remaining>0",owner)>=14)throw new IllegalArgumentException("Tope de 14 órdenes abiertas.");
            if(buy)debit(owner,Math.multiplyExact(price,qty));else consume(owner,id,qty);
            long oid=insert("INSERT INTO orders(owner,product,buy,quantity,remaining,price) VALUES(?,?,?,?,?,?)",owner,id,buy,qty,qty,price);
            match(oid);
            if(instant)cancelInternal(owner,oid);
            audit(owner,instant?"instant":"order",oid+" "+id+" "+qty+" @ "+price);
            return oid;
        });
    }
    Order find(long id)throws SQLException {
        try(var q=db.prepareStatement("SELECT * FROM orders WHERE id=?")){bind(q,id);try(var r=q.executeQuery()){if(!r.next())throw new IllegalArgumentException("Orden inexistente.");return order(r);}}
    }
    void match(long id)throws Exception {
        Order taker=find(id);int left=taker.remaining;
        // Bound work on the primary thread. Unfilled quantity remains in the book.
        var makers=new ArrayList<Order>();
        try(var q=db.prepareStatement("SELECT * FROM orders WHERE product=? AND buy=? AND remaining>0 AND id<>? AND owner<>? AND price "+(taker.buy?"<=":" >=")+" ? ORDER BY price "+(taker.buy?"ASC":"DESC")+",id ASC LIMIT 256")){
            bind(q,taker.product,!taker.buy,id,taker.owner,taker.price);
            try(var r=q.executeQuery()){while(r.next())makers.add(order(r));}
        }
        for(Order maker:makers){
            if(left==0)break;
            int n=Math.min(left,maker.remaining);long gross=Math.multiplyExact(maker.price,n);
            Order seller=taker.buy?maker:find(taker.id);String buyer=taker.buy?taker.owner:maker.owner;
            // Cumulative rounding per sell order prevents splitting fills to evade tax.
            long fee=tax(seller.gross+gross)-seller.tax;
            creditOrder(seller.owner,gross-fee,seller.id);claimOrder(buyer,taker.product,n,taker.buy?taker.id:maker.id);
            if(taker.buy)creditOrder(buyer,Math.multiplyExact(taker.price-maker.price,n),taker.id);
            sql("UPDATE orders SET remaining=remaining-?,filled=filled+? WHERE id IN (?,?)",n,n,id,maker.id);
            sql("UPDATE orders SET gross=gross+?,tax=tax+? WHERE id=?",gross,fee,seller.id);
            sql("INSERT INTO trades(product,buyer,seller,qty,price,tax,at) VALUES(?,?,?,?,?,?,?)",taker.product,buyer,seller.owner,n,maker.price,fee,System.currentTimeMillis());
            audit(buyer,"match",id+"/"+maker.id+" qty="+n+" gross="+gross+" tax="+fee);left-=n;
        }
    }
    public synchronized void drain()throws Exception {
        // Finish large books in bounded batches, once per second, including offline owners.
        long id=scalar("SELECT t.id FROM orders t WHERE t.remaining>0 AND EXISTS (SELECT 1 FROM orders m WHERE m.product=t.product AND m.buy<>t.buy AND m.owner<>t.owner AND m.remaining>0 AND m.id<t.id AND ((t.buy=1 AND m.price<=t.price) OR (t.buy=0 AND m.price>=t.price))) ORDER BY t.id LIMIT 1");
        if(id>0)tx(()->{match(id);return null;});
    }
    public synchronized void cancel(String owner,long id)throws Exception {tx(()->{cancelInternal(owner,id);audit(owner,"cancel",Long.toString(id));return null;});}
    void cancelInternal(String owner,long id)throws Exception {
        Order o=find(id);if(!o.owner.equals(owner))throw new IllegalArgumentException("Esa orden no es tuya.");
        if(o.remaining>0){if(o.buy)creditOrder(owner,Math.multiplyExact(o.remaining,o.price),id);else claimOrder(owner,o.product,o.remaining,id);sql("UPDATE orders SET remaining=0,cancelled=1 WHERE id=?",id);}
    }
    public synchronized void releaseBasket(String owner,String basket)throws Exception {
        tx(()->{sql("UPDATE claims SET basket='' WHERE owner=? AND basket=?",owner,basket);return null;});
    }
    public synchronized void sellEquipment(String owner,String basket,Map<Integer,Long> values,Map<Long,Integer> tiers)throws Exception {
        tx(()->{
            long total=0;for(Claim c:claims(owner))if(c.basket.equals(basket)){
                Integer t=tiers.get(c.id);if(t==null||!values.containsKey(t))throw new IllegalArgumentException("Equipo no habilitado.");
                total=Math.addExact(total,Math.multiplyExact(values.get(t),c.qty));
                sql("UPDATE claims SET qty=0 WHERE id=?",c.id);
            }
            credit(owner,total);audit(owner,"equipment",basket+" cents="+total);return null;
        });
    }
    public synchronized long prepare(String owner,String kind,long cents,double before,long claim,String product,int qty,byte[] item,String basket)throws Exception {
        return tx(()->{
            if(scalar("SELECT COUNT(*) FROM journal WHERE owner=? AND state='pending'",owner)>0)throw new IllegalStateException("Transferencia pendiente de revisión.");
            if(kind.equals("money_out")&&wallet(owner)<cents)throw new IllegalArgumentException("Saldo insuficiente.");
            if(kind.equals("item_out")&&scalar("SELECT qty FROM claims WHERE id=? AND owner=?",claim,owner)<qty)throw new IllegalArgumentException("Retiro no disponible.");
            return insert("INSERT INTO journal(owner,kind,cents,before_balance,claim_id,product,qty,item,basket) VALUES(?,?,?,?,?,?,?,?,?)",owner,kind,cents,before,claim,product,qty,item,basket);
        });
    }
    public synchronized List<Transfer> pending()throws SQLException {
        var out=new ArrayList<Transfer>();try(var q=db.createStatement();var r=q.executeQuery("SELECT * FROM journal WHERE state='pending'")){
            while(r.next())out.add(new Transfer(r.getLong("id"),r.getString("owner"),r.getString("kind"),r.getLong("cents"),r.getDouble("before_balance"),r.getLong("claim_id"),r.getString("product"),r.getInt("qty"),r.getBytes("item"),r.getString("basket")));
        }return out;
    }
    public synchronized void settle(long id,boolean applied)throws Exception {
        tx(()->{
            Transfer t=pending().stream().filter(x->x.id==id).findFirst().orElse(null);if(t==null)return null;
            if(applied)switch(t.kind){
                case "money_in"->credit(t.owner,t.cents);
                case "money_out"->debit(t.owner,t.cents,t.basket.startsWith("order:")?Long.parseLong(t.basket.substring(6)):0);
                case "item_in"->claim(t.owner,t.product,t.qty,t.item,t.basket);
                case "item_out"->sql("UPDATE claims SET qty=qty-? WHERE id=?",t.qty,t.claim);
                default->throw new IllegalStateException("Transferencia desconocida");
            }
            sql("UPDATE journal SET state=? WHERE id=?",applied?"done":"aborted",id);
            audit(t.owner,applied?"transfer":"aborted",t.kind+" #"+id);return null;
        });
    }
    public synchronized double average(String id,int hours)throws SQLException {
        try(var q=db.prepareStatement("SELECT SUM(price*qty)*1.0/SUM(qty) FROM trades WHERE product=? AND at>=?")){
            bind(q,id,System.currentTimeMillis()-hours*3600000L);try(var r=q.executeQuery()){return r.next()?r.getDouble(1)/100:0;}
        }
    }
    public synchronized void backup(Path file)throws SQLException {sql("VACUUM INTO '"+file.toAbsolutePath().toString().replace("'","''")+"'");}
    @Override public synchronized void close()throws SQLException {db.close();}
}
