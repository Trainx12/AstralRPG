package astral;

import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import net.milkbowl.vault.economy.Economy;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.function.Consumer;
import java.util.regex.*;

/** Private, plain chest UI. All player/economy access is on the primary thread.
 * No native inventory movement is allowed: deposits are explicit, journalled clicks.
 */
public final class AstralBazar extends JavaPlugin implements Listener {
    public record Product(String id,String name,String category,long min,long max,ItemStack item) {}
    record Equipment(ItemStack item,int tier,String identity) {}
    final Map<String,Product> products=new LinkedHashMap<>();
    final List<Equipment> equipment=new ArrayList<>();
    final Map<Integer,Long> equipmentPrices=new HashMap<>();
    final Map<UUID,Consumer<String>> inputs=new HashMap<>();
    final Set<UUID> busy=new HashSet<>();
    final Map<UUID,Long> lastClick=new HashMap<>();
    Economy economy;
    BazarStore store;
    NamespacedKey receipt;
    boolean paused, healthy=true;
    String lastBackup="";

    public static final class Screen implements InventoryHolder {
        final Map<Integer,Runnable> actions=new HashMap<>();
        Inventory inv;
        String basket="";
        Consumer<Integer> deposit;
        @Override public Inventory getInventory(){return inv;}
    }
    @Override public void onEnable(){
        try {
            saveDefaultConfig();saveResourceIfMissing("productos.yml");
            receipt=new NamespacedKey(this,"transfer_receipt");
            var registration=getServer().getServicesManager().getRegistration(Economy.class);
            if(registration==null)throw new IllegalStateException("Falta proveedor EssentialsX/Vault.");
            economy=registration.getProvider();loadCatalog();
            Map<String,BazarStore.Product> definitions=new HashMap<>();
            products.forEach((id,p)->definitions.put(id,new BazarStore.Product(id,p.min,p.max)));
            store=new BazarStore(getDataFolder().toPath().resolve("bazar.sqlite"),definitions);
            paused=getConfig().getBoolean("pausado",false);
            // A basket belongs to a window, not a permanent lock; after restart all return.
            store.sql("UPDATE claims SET basket='' WHERE basket<>''");
            recoverMoney();
            getServer().getPluginManager().registerEvents(this,this);
            getCommand("bazar").setExecutor(this);
            Bukkit.getScheduler().runTaskTimer(this,this::clock,1200,1200);
            Bukkit.getScheduler().runTaskTimer(this,()->{if(!paused&&healthy)try{store.drain();}catch(Exception e){failure(e);}},20,20);
            getLogger().info("Bazar privado listo: "+products.size()+" productos. publico="+getConfig().getBoolean("publico"));
        } catch(Exception e){getLogger().log(java.util.logging.Level.SEVERE,"No se pudo iniciar Bazar; deshabilitado",e);getServer().getPluginManager().disablePlugin(this);}
    }
    void saveResourceIfMissing(String name){if(!getDataFolder().toPath().resolve(name).toFile().exists())saveResource(name,false);}
    static long cents(double d){if(!Double.isFinite(d)||d<0||d>1e12)throw new IllegalArgumentException("Importe inválido.");return java.math.BigDecimal.valueOf(d).movePointRight(2).setScale(0,java.math.RoundingMode.HALF_UP).longValueExact();}
    static long price(String s){try{return new java.math.BigDecimal(s.replace(',','.')).movePointRight(2).longValueExact();}catch(Exception e){throw new IllegalArgumentException("Usá un precio con hasta dos decimales.");}}
    static String money(long c){return String.format(Locale.forLanguageTag("es-AR"),"$%,.2f",c/100.0);}
    void loadCatalog()throws Exception {
        var cfg=YamlConfiguration.loadConfiguration(getDataFolder().toPath().resolve("productos.yml").toFile());
        var section=Objects.requireNonNull(cfg.getConfigurationSection("productos"));
        for(String id:section.getKeys(false)){
            var c=section.getConfigurationSection(id);
            ItemStack item=Bukkit.getItemFactory().createItemStack(c.getString("item"));
            if(!item.hasItemMeta()||!item.getItemMeta().getAsComponentString().contains("astral"))throw new IllegalArgumentException("Producto sin marca: "+id);
            long min=cents(Math.max(c.getDouble("minimo"),c.getDouble("piso_server"))),max=cents(c.getDouble("maximo"));
            if(min<1||max<min)throw new IllegalArgumentException("Rango inválido: "+id);
            products.put(id,new Product(id,c.getString("nombre"),c.getString("categoria"),min,max,item));
        }
        var eq=Objects.requireNonNull(cfg.getConfigurationSection("equipo"));
        for(String id:eq.getKeys(false)){
            var c=eq.getConfigurationSection(id);var item=Bukkit.getItemFactory().createItemStack(c.getString("item"));
            equipment.add(new Equipment(item,c.getInt("tier"),identity(item)));
        }
        for(int t=1;t<=10;t++)equipmentPrices.put(t,cents(getConfig().getDouble("equipo-precios."+t)));
    }
    // Extract the astral compound with balanced braces (never an unrelated PDC id).
    static String identity(ItemStack item){
        if(item==null||!item.hasItemMeta())return "";
        String s=item.getItemMeta().getAsComponentString();
        Matcher m=Pattern.compile("(?:\\{|,)\\s*astral\\s*:\\s*\\{").matcher(s);
        if(!m.find())return "";int start=m.end(),depth=1;boolean quoted=false,escape=false;
        for(int i=start;i<s.length();i++){
            char ch=s.charAt(i);if(escape){escape=false;continue;}if(ch=='\\'){escape=true;continue;}
            if(ch=='\"'){quoted=!quoted;continue;}
            if(!quoted){
                if(ch=='{')depth++;
                if(ch=='}'&&--depth==0){
                    String compound=s.substring(start,i);var fields=new TreeMap<String,String>();
                    Matcher f=Pattern.compile("(?:^|,)\\s*(id|type|tier|w|set|piece|tool)\\s*:\\s*(\"[^\"]*\"|[a-zA-Z0-9_.]+)").matcher(compound);
                    while(f.find())fields.put(f.group(1),f.group(2));
                    if(!fields.containsKey("id")||!fields.containsKey("type"))return "";
                    var model=item.getItemMeta().getItemModel();
                    return fields.toString()+" model="+model;
                }
            }
        }
        return "";
    }

    Product product(ItemStack item){if(item==null)return null;for(var p:products.values())if(p.item.isSimilar(item))return p;return null;}
    Equipment gear(ItemStack item){String ident=identity(item);if(ident.isEmpty())return null;for(var e:equipment)if(e.item.getType()==item.getType()&&e.identity.equals(ident))return e;return null;}
    boolean improved(ItemStack item,Equipment e){return !item.isSimilar(e.item);}
    String owner(Player p){return p.getUniqueId().toString();}
    void say(CommandSender p,String s){p.sendMessage("§6Bazar §7» §f"+s);}
    boolean allowed(Player p){return getConfig().getBoolean("publico",false)||p.hasPermission("astral.bazar.usar");}
    void check(Player p){if(!allowed(p))throw new IllegalArgumentException("Próximamente.");if(paused||!healthy)throw new IllegalArgumentException("Bazar pausado; tus bienes siguen guardados.");
        try{if(store.pending().stream().anyMatch(t->t.owner().equals(owner(p))))throw new IllegalArgumentException("Transferencia pendiente de conciliación; avisá al administrador.");}
        catch(java.sql.SQLException e){throw new IllegalStateException(e);}
    }
    void failure(Exception e){healthy=false;paused=true;getConfig().set("pausado",true);saveConfig();getLogger().log(java.util.logging.Level.SEVERE,"Bazar pausado para proteger transferencias",e);}
    void act(Player p,Runnable r){
        if(!busy.add(p.getUniqueId()))return;
        try{check(p);r.run();}catch(IllegalArgumentException e){say(p,e.getMessage());}
        catch(Exception e){failure(e);say(p,"Operación detenida. Avisá al administrador; no repitas transferencias.");}
        finally{busy.remove(p.getUniqueId());}
    }
    interface Checked{void run()throws Exception;}
    void checked(Checked r){try{r.run();}catch(RuntimeException e){throw e;}catch(Exception e){throw new RuntimeException(e);}}

    @Override public boolean onCommand(CommandSender sender,Command cmd,String label,String[] args){
        if(args.length>0&&args[0].equalsIgnoreCase("admin")){
            if(!sender.hasPermission("astral.bazar.admin")){say(sender,"Sin permiso.");return true;}
            try{
                String sub=args.length>1?args[1]:"";
                switch(sub){
                    case "pausar"->{paused=true;getConfig().set("pausado",true);saveConfig();say(sender,"Pausado.");}
                    case "reanudar"->{if(!healthy||!store.pending().isEmpty())throw new IllegalArgumentException("Hay transferencias sin resolver; revisar journal y recibos antes de reanudar.");paused=false;getConfig().set("pausado",false);saveConfig();say(sender,"Reanudado (se conserva el acceso privado).");}
                    case "recargar"->{reloadConfig();paused=getConfig().getBoolean("pausado")||!healthy;say(sender,"Config recargada. Cambios de catálogo requieren reinicio para preservar órdenes.");}
                    case "ver"->{if(args.length<3)throw new IllegalArgumentException("/bazar admin ver <jugador>");var op=Bukkit.getOfflinePlayer(args[2]);String id=op.getUniqueId().toString();say(sender,"UUID "+id+" saldo "+money(store.wallet(id))+"; órdenes "+store.orders(id)+"; retiros "+store.claims(id).size());}
                    case "cancelar"->{if(args.length<3)throw new IllegalArgumentException("/bazar admin cancelar <orden>");long id=Long.parseLong(args[2]);store.cancel(store.find(id).owner(),id);say(sender,"Cancelada; devolución para retirar.");}
                    default->say(sender,"/bazar admin pausar|reanudar|ver <jugador>|cancelar <orden>|recargar");
                }
            }catch(Exception e){say(sender,e.getMessage());}return true;
        }
        if(!(sender instanceof Player p)){say(sender,"Solo jugadores.");return true;}
        if(!allowed(p)){say(p,"Próximamente.");return true;}
        if(args.length>0&&args[0].equalsIgnoreCase("entrada")){
            var input=inputs.remove(p.getUniqueId());if(input==null){say(p,"No hay una entrada pendiente.");return true;}
            String text=String.join(" ",Arrays.copyOfRange(args,1,args.length));act(p,()->input.accept(text));return true;
        }
        act(p,()->home(p));return true;
    }
    Screen screen(Player p,String title,int rows){
        Screen s=new Screen();s.inv=Bukkit.createInventory(s,rows*9,title);return s;
    }
    void button(Screen s,int slot,Material mat,String name,Runnable action,String...lore){
        ItemStack item=new ItemStack(mat);var meta=item.getItemMeta();meta.setDisplayName("§e"+name);meta.setLore(Arrays.stream(lore).map(x->"§7"+x).toList());item.setItemMeta(meta);s.inv.setItem(slot,item);if(action!=null)s.actions.put(slot,action);
    }
    void nav(Player p,Screen s,Runnable back){int n=s.inv.getSize();button(s,n-9,Material.ARROW,"Volver",back);button(s,n-1,Material.BARRIER,"Cerrar",p::closeInventory);}
    void open(Player p,Screen s){p.openInventory(s.inv);}
    void home(Player p){
        Screen s=screen(p,"Bazar - Categorias",4);int slot=10;
        for(String cat:products.values().stream().map(Product::category).distinct().toList())button(s,slot++,Material.CHEST,cat,()->listing(p,cat,"",0));
        button(s,20,Material.COMPASS,"Buscar",()->ask(p,"Nombre del producto",text->listing(p,"",text,0)));
        button(s,22,Material.BOOK,"Mis órdenes y retiros",()->orders(p,0));
        button(s,24,Material.IRON_SWORD,"Vender equipo al server",()->equipmentScreen(p,"eq-"+UUID.randomUUID()));
        button(s,35,Material.BARRIER,"Cerrar",p::closeInventory);open(p,s);
    }
    void listing(Player p,String cat,String search,int page){
        List<Product> list=products.values().stream().filter(x->(cat.isEmpty()||cat.equals(x.category))&&(search.isEmpty()||normalize(x.name).contains(normalize(search)))).toList();
        Screen s=screen(p,"Bazar - Productos",6);int start=page*45;
        for(int i=0;i<45&&start+i<list.size();i++){Product x=list.get(start+i);button(s,i,x.item.getType(),x.name,()->detail(p,x),x.category,"Rango "+money(x.min)+" a "+money(x.max));}
        nav(p,s,()->home(p));if(page>0)button(s,48,Material.ARROW,"Anterior",()->listing(p,cat,search,page-1));
        if(start+45<list.size())button(s,50,Material.ARROW,"Siguiente",()->listing(p,cat,search,page+1));open(p,s);
    }
    static String normalize(String s){return java.text.Normalizer.normalize(s.toLowerCase(Locale.ROOT),java.text.Normalizer.Form.NFD).replaceAll("\\p{M}","");}
    void detail(Player p,Product x){checked(()->{
        Screen s=screen(p,"Bazar - Producto",6);
        button(s,4,x.item.getType(),x.name,null,"Rango: "+money(x.min)+" - "+money(x.max),"Promedio 1h: $"+store.average(x.id,1),"Promedio 24h: $"+store.average(x.id,24),"Cada operación muestra las 7 mejores puntas.");
        for(boolean buy:List.of(true,false)){
            List<BazarStore.Level> book=store.book(x.id,buy);
            for(int i=0;i<book.size();i++){var l=book.get(i);button(s,(buy?10:19)+i,Material.PAPER,(buy?"Compra ":"Venta ")+money(l.price()),null,l.qty()+" unidades en "+l.orders()+" órdenes");}
        }
        button(s,28,Material.GOLD_INGOT,"Comprar al instante",()->amount(p,x,true,true));
        button(s,30,Material.EMERALD,"Vender al instante",()->amount(p,x,false,true));
        button(s,32,Material.WRITABLE_BOOK,"Orden de compra",()->amount(p,x,true,false));
        button(s,34,Material.WRITABLE_BOOK,"Oferta de venta",()->amount(p,x,false,false));
        button(s,40,Material.BOOK,"Mis órdenes",()->orders(p,0));nav(p,s,()->home(p));open(p,s);
    });}
    int count(Player p,Product x){int n=0;for(var it:p.getInventory().getStorageContents())if(it!=null&&x.item.isSimilar(it))n+=it.getAmount();return n;}
    long best(Product x,boolean buy)throws Exception {var b=store.book(x.id,buy);return b.isEmpty()?(buy?x.min:x.max):b.getFirst().price();}
    void amount(Player p,Product x,boolean buy,boolean instant){
        Screen s=screen(p,"Bazar - Cantidad",3);int slot=10;
        for(int n:List.of(1,16,64,160))button(s,slot++,Material.PAPER,Integer.toString(n),()->choosePrice(p,x,buy,instant,n));
        button(s,15,Material.CHEST,buy?"Todo lo que alcanza":"Todo lo que tengo",()->checked(()->{
            long unit=instant?(buy?x.max:x.min):best(x,buy);
            int n=buy?(int)Math.min(71680,(cents(economy.getBalance(p))+store.wallet(owner(p)))/Math.max(1,unit)):
                Math.min(71680,count(p,x)+store.available(owner(p),x.id));
            if(instant&&buy)n=affordable(p,x);
            choosePrice(p,x,buy,instant,n);
        }));
        button(s,16,Material.NAME_TAG,"A mano",()->ask(p,"Cantidad (1 a 71680)",text->{int n;try{n=Integer.parseInt(text);}catch(Exception e){throw new IllegalArgumentException("Cantidad inválida.");}choosePrice(p,x,buy,instant,n);}));
        nav(p,s,()->detail(p,x));open(p,s);
    }
    int affordable(Player p,Product x)throws Exception {
        long budget=cents(economy.getBalance(p))+store.wallet(owner(p));int n=0;
        // Quote exact depth; no charging the maximum price for unavailable liquidity.
        try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=0 AND remaining>0 AND owner<>? ORDER BY price,id LIMIT 256")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next()&&n<71680){long price=r.getLong(1);int take=(int)Math.min(Math.min(71680-n,r.getInt(2)),budget/price);n+=take;budget-=take*price;if(take<r.getInt(2))break;}}
        }return n;
    }
    void choosePrice(Player p,Product x,boolean buy,boolean instant,int qty){
        if(qty<1||qty>71680)throw new IllegalArgumentException("Cantidad: 1 a 71.680; puede no haber liquidez.");
        if(instant){confirm(p,x,buy,true,qty,buy?x.max:x.min);return;}
        checked(()->{
            long b=best(x,buy);Screen s=screen(p,"Bazar - Precio",3);
            button(s,11,Material.GOLD_NUGGET,"Igual al mejor: "+money(b),()->confirm(p,x,buy,false,qty,b));
            long better=buy?b+10:b-10;
            button(s,13,Material.GOLD_INGOT,buy?"Mejor +0,1":"Mejor -0,1",()->confirm(p,x,buy,false,qty,better),"Venta: bajar $0,10 para quedar primero.");
            button(s,15,Material.NAME_TAG,"A mano",()->ask(p,"Precio por unidad",text->confirm(p,x,buy,false,qty,price(text))));
            nav(p,s,()->amount(p,x,buy,false));open(p,s);
        });
    }
    void confirm(Player p,Product x,boolean buy,boolean instant,int qty,long price){
        if(price<x.min||price>x.max)throw new IllegalArgumentException("Precio fuera de rango: "+money(x.min)+" - "+money(x.max));
        Screen s=screen(p,"Bazar - Confirmar orden",3);
        String action=(buy?"Comprar":"Vender")+(instant?" al instante":" mediante orden");
        long estimate;
        try{estimate=instant?(buy?quote(p,x,qty):sellQuote(p,x,qty)):Math.multiplyExact(price,qty);}
        catch(Exception e){throw new IllegalStateException(e);}
        button(s,13,x.item.getType(),action+" "+qty+" "+x.name,null,"Límite por unidad: "+money(price),(instant?"Total estimado disponible: ":"Total reservado: ")+money(estimate),instant?"Puede variar al confirmar según la liquidez.":"Sin vencimiento.","Impuesto vendedor: 1,25%; redondeo acumulado al centavo.","No negocia con tus propias órdenes.");
        button(s,11,Material.LIME_WOOL,"Confirmar",()->checked(()->{
            // Invalidate this window before touching resources: packets cannot submit twice.
            s.actions.clear();p.closeInventory();
            if(buy){long needed=instant?quote(p,x,qty):Math.multiplyExact(price,qty);if(needed==0)throw new IllegalArgumentException("No hay ofertas de venta.");
                fund(p,Math.max(0,needed-store.wallet(owner(p))));
                // Instant orders reserve a depth quote rather than qty * max. Use a
                // separate exact execution with refund of unused cash.
                if(instant){instantBuy(p,x,qty);orders(p,0);return;}
            } else depositProduct(p,x,Math.max(0,qty-store.available(owner(p),x.id)));
            long id=store.create(owner(p),x.id,buy,qty,price,instant);say(p,"Operación #"+id+" guardada; resultados en Mis órdenes.");orders(p,0);
        }));
        button(s,15,Material.RED_WOOL,"Volver",()->detail(p,x));open(p,s);
    }
    long quote(Player p,Product x,int qty)throws Exception {
        long sum=0;int left=qty;
        try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=0 AND remaining>0 AND owner<>? ORDER BY price,id LIMIT 256")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next()&&left>0){int n=Math.min(left,r.getInt(2));sum=Math.addExact(sum,Math.multiplyExact(n,r.getLong(1)));left-=n;}}
        }return sum;
    }
    long sellQuote(Player p,Product x,int qty)throws Exception {
        long gross=0;int left=qty;
        try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=1 AND remaining>0 AND owner<>? ORDER BY price DESC,id LIMIT 256")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next()&&left>0){int n=Math.min(left,r.getInt(2));gross+=n*r.getLong(1);left-=n;}}
        }return gross-BazarStore.tax(gross);
    }
    void instantBuy(Player p,Product x,int qty)throws Exception {
        // Each operation is bounded and runs in one SQLite transaction, reserving
        // actual price levels. No inventory/Vault operations occur inside a match.
        store.tx(()->{
            var levels=new ArrayList<long[]>();
            try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=0 AND remaining>0 AND owner<>? ORDER BY price,id LIMIT 256")){
                BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next())levels.add(new long[]{r.getLong(1),r.getInt(2)});}
            }
            int left=qty;for(var l:levels){
                if(left==0)break;int n=Math.min(left,(int)l[1]);store.create(owner(p),x.id,true,n,l[0],true);left-=n;
            }return null;
        });say(p,"Compra instantánea guardada; retirala en Mis órdenes.");
    }
    void ask(Player p,String prompt,Consumer<String> callback){p.closeInventory();inputs.put(p.getUniqueId(),callback);say(p,prompt+": escribí /bazar entrada <valor> (o /bazar para volver).");}
    void orders(Player p,int page){checked(()->{
        var all=store.orders(owner(p));Screen s=screen(p,"Bazar - Mis ordenes",6);
        for(int i=0;i<36&&page*36+i<all.size();i++){var o=all.get(page*36+i);Product x=products.get(o.product());
            button(s,i,Material.PAPER,"#"+o.id()+" "+(o.buy()?"Compra ":"Venta ")+(x==null?o.product():x.name),()->orderDetail(p,o.id()),"Llenadas "+o.filled()+" / "+o.quantity()+"; restan "+o.remaining(),o.cancelled()?"Cancelada":"Precio "+money(o.price()),"Clic para ver/cancelar");}
        button(s,39,Material.CHEST,"Retirar productos y devoluciones",()->withdrawals(p,0));
        button(s,41,Material.GOLD_INGOT,"Retirar plata: "+money(store.wallet(owner(p))),()->checked(()->{pay(p,store.wallet(owner(p)));orders(p,page);}));
        nav(p,s,()->home(p));if(page>0)button(s,48,Material.ARROW,"Anterior",()->orders(p,page-1));if((page+1)*36<all.size())button(s,50,Material.ARROW,"Siguiente",()->orders(p,page+1));open(p,s);
    });}
    void orderDetail(Player p,long id){checked(()->{var o=store.find(id);if(!o.owner().equals(owner(p)))throw new IllegalArgumentException("Orden ajena.");Screen s=screen(p,"Bazar - Orden",3);
        button(s,13,Material.PAPER,"Orden #"+id,null,"Llenadas "+o.filled()+" / "+o.quantity()+"; restan "+o.remaining(),o.cancelled()?"Cancelada":"Activa/completada","Plata de ventas "+money(o.gross()-o.tax()),"Impuesto "+money(o.tax()),"Lo conseguido está en retiros y saldo.");
        button(s,11,Material.RED_WOOL,"Cancelar y devolver restante",()->checked(()->{s.actions.clear();store.cancel(owner(p),id);orders(p,0);}));
        nav(p,s,()->orders(p,0));open(p,s);});}
    void withdrawals(Player p,int page){checked(()->{
        var claims=store.claims(owner(p)).stream().filter(c->c.basket().isEmpty()).toList();Screen s=screen(p,"Bazar - Retiros",6);
        for(int i=0;i<45&&page*45+i<claims.size();i++){var c=claims.get(page*45+i);ItemStack it=claimItem(c);button(s,i,it.getType(),c.product()+" x"+c.qty(),()->checked(()->{s.actions.clear();withdraw(p,c);withdrawals(p,page);}));}
        nav(p,s,()->orders(p,0));if(page>0)button(s,48,Material.ARROW,"Anterior",()->withdrawals(p,page-1));if((page+1)*45<claims.size())button(s,50,Material.ARROW,"Siguiente",()->withdrawals(p,page+1));open(p,s);
    });}
    ItemStack claimItem(BazarStore.Claim c){return c.item()!=null?ItemStack.deserializeBytes(c.item()):Objects.requireNonNull(products.get(c.product()),"Producto retirado del catálogo: "+c.product()).item.clone();}
    void equipmentScreen(Player p,String basket){checked(()->{
        Screen s=screen(p,"Bazar - Vender equipo",6);s.basket=basket;s.deposit=slot->checked(()->{
            ItemStack item=p.getInventory().getItem(slot);Equipment e=gear(item);
            if(e==null)throw new IllegalArgumentException("Solo armas y armaduras Astrales. No historia, mochilas, mascotas, cosméticos, taladros ni oficios.");
            deposit(p,slot,item.getAmount(),"equipo",basket);refreshEquipment(p,s);
        });refreshEquipment(p,s);nav(p,s,()->home(p));open(p,s);
    });}
    void refreshEquipment(Player p,Screen s)throws Exception {
        for(int i=0;i<45;i++)s.inv.setItem(i,null);
        long total=0;boolean improvements=false;int slot=0;
        for(var c:store.claims(owner(p)))if(c.basket().equals(s.basket)){
            ItemStack item=claimItem(c);Equipment e=gear(item);if(e==null)throw new IllegalArgumentException("Equipo inválido.");
            total+=equipmentPrices.get(e.tier)*c.qty();improvements|=improved(item,e);
            if(slot<45){item.setAmount(Math.min(c.qty(),item.getMaxStackSize()));s.inv.setItem(slot++,item);}
        }
        String b=s.basket;long value=total;boolean warn=improvements;
        button(s,49,Material.LIME_WOOL,"Confirmar venta: "+money(total),()->{if(value<=0)throw new IllegalArgumentException("Elegí equipo de tu inventario inferior.");confirmEquipment(p,s,b,value,warn);},"Clic en el inventario inferior para depositar piezas.","Al cerrar vuelve todo; si no entra, queda para retirar.",warn?"Este lote tiene mejoras. En la Subasta vale más.":"Conviene más vender en la Subasta.");
    }
    void confirmEquipment(Player p,Screen old,String basket,long total,boolean warn){
        // Keep custody in SQLite when switching windows; close must not return it.
        old.basket="";Screen s=screen(p,"Bazar - Confirmar equipo",3);s.basket=basket;
        button(s,13,Material.ANVIL,warn?"Este ítem tiene mejoras. En la Subasta vale más.":"Vender equipo al servidor",null,"¿Vender igual por "+money(total)+"?","Se pierden encantamientos, gemas, reforja y mejoras.");
        button(s,11,Material.LIME_WOOL,"Sí, vender por "+money(total),()->checked(()->{
            s.actions.clear();Map<Long,Integer> tiers=new HashMap<>();
            for(var c:store.claims(owner(p)))if(c.basket().equals(basket)){var e=gear(claimItem(c));if(e==null)throw new IllegalArgumentException("Equipo inválido");tiers.put(c.id(),e.tier);}
            store.sellEquipment(owner(p),basket,equipmentPrices,tiers);s.basket="";say(p,"Equipo vendido: "+money(total)+" para retirar.");orders(p,0);
        }));button(s,15,Material.RED_WOOL,"No, devolver todo",p::closeInventory);open(p,s);
    }

    void fund(Player p,long amount)throws Exception {
        if(amount<=0)return;if(amount>cents(economy.getBalance(p)))throw new IllegalArgumentException("Plata insuficiente.");
        long id=store.prepare(owner(p),"money_in",amount,economy.getBalance(p),0,"",0,null,"");
        var response=economy.withdrawPlayer(p,amount/100.0);
        store.settle(id,response.transactionSuccess());if(!response.transactionSuccess())throw new IllegalArgumentException("Vault rechazó el cobro: "+response.errorMessage);
    }
    void pay(Player p,long amount)throws Exception {
        if(amount<=0){say(p,"No hay plata para retirar.");return;}
        long id=store.prepare(owner(p),"money_out",amount,economy.getBalance(p),0,"",0,null,"");
        var response=economy.depositPlayer(p,amount/100.0);store.settle(id,response.transactionSuccess());
        if(!response.transactionSuccess())throw new IllegalArgumentException("Vault rechazó el retiro; el saldo sigue guardado.");say(p,"Retiraste "+money(amount));
    }
    void depositProduct(Player p,Product x,int amount)throws Exception {
        if(count(p,x)<amount)throw new IllegalArgumentException("No tenés suficientes productos idénticos; no se aceptan vanilla, renombrados ni mejorados.");
        for(int slot=0;slot<36&&amount>0;slot++){var it=p.getInventory().getItem(slot);if(it!=null&&x.item.isSimilar(it)){int n=Math.min(amount,it.getAmount());deposit(p,slot,n,x.id,"");amount-=n;}}
    }
    void deposit(Player p,int slot,int qty,String product,String basket)throws Exception {
        ItemStack it=p.getInventory().getItem(slot);if(it==null||qty<1||qty>it.getAmount())throw new IllegalArgumentException("El ítem ya no está.");
        ItemStack unit=it.clone();unit.setAmount(1);
        long id=store.prepare(owner(p),"item_in",0,0,0,product,qty,unit.serializeAsBytes(),basket);
        ItemStack rest=it.clone();rest.setAmount(it.getAmount()-qty);p.getInventory().setItem(slot,rest.getAmount()==0?null:rest);
        p.getPersistentDataContainer().set(receipt,PersistentDataType.LONG,id);p.saveData();store.settle(id,true);
    }
    void withdraw(Player p,BazarStore.Claim c)throws Exception {
        ItemStack unit=claimItem(c);int free=0,max=unit.getMaxStackSize();
        for(ItemStack it:p.getInventory().getStorageContents())if(it==null||it.getType().isAir())free+=max;else if(it.isSimilar(unit))free+=Math.max(0,max-it.getAmount());
        int qty=Math.min(free,c.qty());if(qty==0){say(p,"Inventario lleno. Todo sigue para retirar.");return;}
        long id=store.prepare(owner(p),"item_out",0,0,c.id(),c.product(),qty,null,"");
        int left=qty;while(left>0){ItemStack stack=unit.clone();int n=Math.min(max,left);stack.setAmount(n);if(!p.getInventory().addItem(stack).isEmpty())throw new IllegalStateException("Inventario cambió durante retiro");left-=n;}
        p.getPersistentDataContainer().set(receipt,PersistentDataType.LONG,id);p.saveData();store.settle(id,true);say(p,"Retiraste "+qty+"; el resto sigue guardado.");
    }
    void recoverMoney()throws Exception {
        for(var t:store.pending())if(t.kind().startsWith("money_")){
            double balance=economy.getBalance(Bukkit.getOfflinePlayer(UUID.fromString(t.owner())));
            double expected=t.before()+(t.kind().equals("money_in")?-1:1)*t.cents()/100.0;
            if(Math.abs(balance-expected)<0.005)store.settle(t.id(),true);
            else if(Math.abs(balance-t.before())<0.005)store.settle(t.id(),false);
            else {paused=true;healthy=false;getConfig().set("pausado",true);saveConfig();getLogger().severe("Pago ambiguo journal #"+t.id()+"; requiere conciliación con Essentials. No se repite.");}
        }
    }
    @EventHandler public void join(PlayerJoinEvent event){Player p=event.getPlayer();Bukkit.getScheduler().runTask(this,()->checked(()->{
        for(var t:store.pending())if(t.owner().equals(owner(p))&&t.kind().startsWith("item_")){
            long saved=p.getPersistentDataContainer().getOrDefault(receipt,PersistentDataType.LONG,0L);store.settle(t.id(),saved==t.id());
            if(!t.basket().isEmpty())store.releaseBasket(owner(p),t.basket());
        }
        if(allowed(p)&&(store.wallet(owner(p))>0||!store.claims(owner(p)).isEmpty()))say(p,"Tenés cosas para retirar en el Bazar.");
    }));}
    @EventHandler public void quit(PlayerQuitEvent e){inputs.remove(e.getPlayer().getUniqueId());lastClick.remove(e.getPlayer().getUniqueId());}
    @EventHandler(priority=EventPriority.HIGHEST) public void click(InventoryClickEvent e){
        if(!(e.getView().getTopInventory().getHolder() instanceof Screen s))return;
        e.setCancelled(true);if(!(e.getWhoClicked() instanceof Player p))return;
        if(e.getClick()!=ClickType.LEFT&&e.getClick()!=ClickType.RIGHT)return;
        long now=System.nanoTime(),prev=lastClick.getOrDefault(p.getUniqueId(),0L);if(now-prev<180_000_000L)return;lastClick.put(p.getUniqueId(),now);
        int raw=e.getRawSlot();if(raw<0)return;
        Runnable action=raw<s.inv.getSize()?s.actions.get(raw):null;
        if(action==null&&s.deposit!=null&&raw>=s.inv.getSize()&&e.getClickedInventory()==p.getInventory())action=()->s.deposit.accept(e.getSlot());
        if(action!=null){Runnable selected=action;Bukkit.getScheduler().runTask(this,()->{if(p.isOnline()&&p.getOpenInventory().getTopInventory()==s.inv)act(p,selected);});}
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void drag(InventoryDragEvent e){if(e.getView().getTopInventory().getHolder() instanceof Screen)e.setCancelled(true);}
    @EventHandler public void close(InventoryCloseEvent e){if(e.getInventory().getHolder() instanceof Screen s&&!s.basket.isEmpty()&&e.getPlayer() instanceof Player p){String b=s.basket;s.basket="";try{
        store.releaseBasket(owner(p),b);for(var c:store.claims(owner(p)))if(c.product().equals("equipo")&&c.basket().isEmpty())withdraw(p,c);
    }catch(Exception ex){failure(ex);say(p,"La devolución sigue guardada; requiere revisión del administrador.");}}}
    void clock(){
        try{
            ZoneId zone=ZoneId.of(getConfig().getString("respaldo-zona","America/Argentina/Buenos_Aires"));var now=ZonedDateTime.now(zone);
            String day=now.toLocalDate().toString();LocalTime at=LocalTime.parse(getConfig().getString("respaldo-hora","04:45"));
            if(!day.equals(lastBackup)&&!now.toLocalTime().isBefore(at)){
                Path dir=getDataFolder().toPath().resolve("backups");Files.createDirectories(dir);Path dest=dir.resolve(day+".sqlite");
                if(!Files.exists(dest))Bukkit.getScheduler().runTaskAsynchronously(this,()->{try{store.backup(dest);}catch(Exception e){getLogger().log(java.util.logging.Level.SEVERE,"Fallo respaldo Bazar",e);}});
                lastBackup=day;
            }
        }catch(Exception e){getLogger().log(java.util.logging.Level.SEVERE,"Reloj Bazar",e);}
    }
    @Override public void onDisable(){
        for(Player p:Bukkit.getOnlinePlayers())if(p.getOpenInventory().getTopInventory().getHolder() instanceof Screen)p.closeInventory();
        if(store!=null)try{store.close();}catch(Exception e){getLogger().severe(e.toString());}
    }
}
