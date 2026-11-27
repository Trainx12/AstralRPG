package astral;

import java.nio.file.*;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;

/** Runs against the actual Paper/Vault/Essentials runtime, never the remote server. */
public final class BazarProbe {
    final AstralBazar plugin;
    public BazarProbe(JavaPlugin plugin){this.plugin=(AstralBazar)plugin;}
    java.util.logging.Logger getLogger(){return plugin.getLogger();}
    java.io.File getDataFolder(){return new java.io.File(plugin.getDataFolder(),"probe");}
    public static final class Launcher extends JavaPlugin {
        @Override public void onEnable(){try{
            JavaPlugin target=(JavaPlugin)Bukkit.getPluginManager().getPlugin("AstralBazar");
            var type=Class.forName("astral.BazarProbe",true,target.getClass().getClassLoader());
            Object probe=type.getConstructor(JavaPlugin.class).newInstance(target);type.getMethod("start").invoke(probe);
        }catch(Exception e){throw new RuntimeException(e);}}
    }
    AstralBazar b;int checks,failures;Player a,z;
    void ok(boolean value,String label){checks++;if(!value){failures++;getLogger().severe("BAZ FAIL "+label);}else getLogger().info("BAZ OK "+label);}
    interface Task{void run()throws Exception;}
    void rejects(Task f,String label){try{f.run();ok(false,label);}catch(Exception e){ok(true,label);}}
    public void start(){Bukkit.getScheduler().runTaskTimer(plugin,()->{
        if(a!=null)return;var p=Bukkit.getPlayerExact("BazarUno");var q=Bukkit.getPlayerExact("BazarDos");if(p==null||q==null)return;a=p;z=q;b=(AstralBazar)Bukkit.getPluginManager().getPlugin("AstralBazar");
        try{run();}catch(Throwable e){failures++;getLogger().log(java.util.logging.Level.SEVERE,"BAZ EXCEPTION",e);}
        if(Files.exists(getDataFolder().toPath().resolve("crash.properties"))){asyncInputs();return;}
        finish();
    },40,20);}
    void finish(){getLogger().info("BAZ RESULT checks="+checks+" failures="+failures);Bukkit.shutdown();}
    void asyncInputs(){
        a.addAttachment(b,"astral.bazar.usar",true);String[] received={""};
        b.ask(a,"Chat real",text->received[0]=text);
        var event=new io.papermc.paper.event.player.AsyncChatEvent(false,a,new HashSet<>(),io.papermc.paper.chat.ChatRenderer.defaultRenderer(),net.kyori.adventure.text.Component.text("123,45"),net.kyori.adventure.text.Component.text("123,45"),null);
        Bukkit.getPluginManager().callEvent(event);ok(event.isCancelled(),"evento de chat no llega a espectadores");
        Bukkit.getScheduler().runTaskLater(plugin,()->{
            ok(received[0].equals("123,45")&&!b.inputs.containsKey(a.getUniqueId()),"chat ejecuta entrada una vez en hilo principal");
            b.ask(a,"Vencimiento real",text->received[0]="error");
            Bukkit.getScheduler().runTaskLater(plugin,()->{ok(!b.inputs.containsKey(a.getUniqueId())&&!b.inputDeadlines.containsKey(a.getUniqueId())&&received[0].equals("123,45"),"entrada vence realmente a los 30 segundos");finish();},610);
        },2);
    }
    void priceFlows()throws Exception {
        var x=b.products.get("corazon_shulker");var s=b.store;String u=b.owner(a),v=b.owner(z);long bid=x.min()+1000,ask=bid+2000;
        s.credit(v,1000000000000L);s.claim(v,x.id(),512,null,"");
        s.create(v,x.id(),true,512,bid,false);s.create(v,x.id(),false,512,ask,false);
        a.getInventory().clear();for(int i=0;i<4;i++){var stack=x.item().clone();stack.setAmount(64);a.getInventory().setItem(i,stack);}
        for(boolean buy:List.of(true,false))for(int option=0;option<4;option++){
            long expected=switch(option){case 0->b.best(x,buy);case 1->b.best(x,buy)+(buy?10:-10);case 2->b.marginPrice(x,buy);default->buy?bid+500:ask-500;};
            b.choosePrice(a,x,buy,false,64);var screen=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
            screen.actions.get(new int[]{10,12,14,16}[option]).run();
            if(option==3)b.onCommand(a,b.getCommand("bazar"),"bazar",new String[]{"entrada",Long.toString(expected/100)+"."+String.format("%02d",expected%100)});
            var confirm=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();confirm.actions.get(36).run();
            var order=s.orders(u).stream().filter(o->o.product().equals(x.id())).findFirst().orElseThrow();
            ok(order.buy()==buy&&order.quantity()==64&&order.price()==expected,"crear "+(buy?"compra":"venta")+" opción precio "+option);
            s.cancel(u,order.id());b.collectOrder(a,order.id());
        }
    }
    void categoryMigration()throws Exception {
        Path catalog=b.getDataFolder().toPath().resolve("productos.yml");byte[] saved=Files.readAllBytes(catalog);
        var cfg=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(catalog.toFile());
        Path db=getDataFolder().toPath().resolve("categorias.sqlite");Files.createDirectories(db.getParent());
        var defs=new HashMap<String,BazarStore.Product>();
        for(var p:b.products.values())defs.put(p.id(),new BazarStore.Product(p.id(),p.min(),p.max()));
        long order;String owner=b.owner(a);var product=b.products.get("netherita_fundida");
        try(var old=new BazarStore(db,defs)){
            old.credit(owner,product.min()*3);order=old.create(owner,product.id(),true,2,product.min(),false);
        }
        try{
            cfg.set("productos.netherita_fundida.categoria","Mineria");
            cfg.set("productos.netherita_reforzada.categoria","Mineria");
            for(String id:List.of("madera_estelar","palo_reforzado","perla_abisal","coral_astral"))cfg.set("productos."+id+".categoria","Bosque y pesca");
            cfg.set("productos.fragmento_astral.categoria","Categoria futura desconocida");cfg.save(catalog.toFile());
            b.products.clear();b.equipment.clear();b.loadCatalog();
            ok(b.products.get(product.id()).category().equals("Combate"),"catálogo Mineria carga en Combate");
            ok(b.products.get("fragmento_astral").category().equals("Especiales"),"categoría desconocida carga sin romper catálogo");
            try(var reopened=new BazarStore(db,defs)){
                var o=reopened.find(order);
                ok(o.product().equals(product.id())&&o.remaining()==2&&!o.cancelled(),"orden Mineria conserva ID y cantidad al reabrir SQLite");
                ok(reopened.wallet(owner)==product.min(),"migración conserva saldo reservado y libre");
                reopened.cancel(owner,order);ok(reopened.wallet(owner)==product.min()*3,"orden migrada se cancela y devuelve reserva");
            }
        }finally{Files.write(catalog,saved);b.products.clear();b.equipment.clear();b.loadCatalog();}
        ok(Arrays.equals(AstralBazar.CATS,new String[]{"Combate","Bosque","Oceano","Consumibles","Especiales"}),"cinco categorías en orden");
        for(var entry:Map.of("netherita_fundida","Combate","netherita_reforzada","Combate","madera_estelar","Bosque","palo_reforzado","Bosque","perla_abisal","Oceano","coral_astral","Oceano").entrySet())
            ok(b.products.get(entry.getKey()).category().equals(entry.getValue()),"categoría nueva "+entry.getKey());
        b.home(a);var home=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        ok(home.inv.getItem(0).getItemMeta().getDisplayName().contains("► Combate"),"Combate seleccionado por defecto");
        for(int slot:List.of(9,18)){
            home.actions.get(slot).run();var inv=a.getOpenInventory().getTopInventory();
            String cat=slot==9?"Bosque":"Oceano";int count=0;
            for(int i:AstralBazar.PRODUCT_SLOTS)if(inv.getItem(i)!=null){count++;String identity=AstralBazar.identity(inv.getItem(i));ok(b.products.values().stream().anyMatch(p->p.category().equals(cat)&&AstralBazar.identity(p.item()).equals(identity)),"filtro "+cat);}
            ok(count==2,"dos productos en "+cat);
        }
    }
    void run()throws Exception {
        String u=a.getUniqueId().toString(),v=z.getUniqueId().toString();
        Path crash=getDataFolder().toPath().resolve("crash.properties");
        if(Files.exists(crash)){
            var saved=new Properties();try(var input=Files.newInputStream(crash)){saved.load(input);}
            checks=Integer.parseInt(saved.getProperty("checks"));failures=Integer.parseInt(saved.getProperty("failures"));
            ok(b.store.available(u,"fragmento_astral")==Integer.parseInt(saved.getProperty("quantity")),"caída real JVM: bienes recuperados");
            ok(b.store.wallet(u)==Long.parseLong(saved.getProperty("wallet")),"caída real JVM: plata conservada");
            ok(b.store.pending().isEmpty(),"caída real JVM: journal resuelto al entrar");
            ok(a.getInventory().getItem(0)==null,"caída real JVM: inventario sin duplicación");
            try(var stmt=b.store.db.createStatement();var result=stmt.executeQuery("PRAGMA quick_check")){ok(result.next()&&result.getString(1).equals("ok"),"integridad SQLite tras caída");}
            return;
        }
        a.addAttachment(b,"astral.bazar.usar",true);
        ok(!b.getConfig().getBoolean("publico"),"oculto por defecto");
        b.onCommand(z,b.getCommand("bazar"),"bazar",new String[0]);
        ok(!(z.getOpenInventory().getTopInventory().getHolder() instanceof AstralBazar.Screen),"sin permiso no abre");
        ok(!z.hasPermission("astral.bazar.usar"),"default false incluso sin OP");
        ok(b.products.size()==88,"88 productos canónicos cargados sin errores");
        categoryMigration();
        var x=b.products.get("fragmento_astral");
        ok(x!=null&&b.product(x.item())==x,"producto canónico");
        ok(b.product(new ItemStack(Material.PAPER))==null,"vanilla rechazado");
        var renamed=x.item().clone();var meta=renamed.getItemMeta();meta.setDisplayName("trampa");renamed.setItemMeta(meta);
        ok(b.product(renamed)==null,"producto renombrado rechazado");
        var enchanted=x.item().clone();enchanted.addUnsafeEnchantment(org.bukkit.enchantments.Enchantment.UNBREAKING,1);
        ok(b.product(enchanted)==null,"producto encantado rechazado");
        for(var p:b.products.values()){ok(b.product(p.item())!=null,"identidad "+p.id());ok(p.min()>0&&p.max()>=p.min(),"rango "+p.id());}
        var cfg=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(b.getDataFolder().toPath().resolve("productos.yml").toFile());
        for(String id:List.of("cristal_caverna","geoda_estelar","fragmento_estelar","nucleo_meteorito"))ok(b.products.get(id).min()>=AstralBazar.cents(cfg.getDouble("productos."+id+".piso_server")),"piso "+id);
        for(String id:cfg.getConfigurationSection("equipo").getKeys(false)){
            ItemStack it=Bukkit.getItemFactory().createItemStack(cfg.getString("equipo."+id+".item"));
            ok(b.gear(it)!=null,"equipo "+id);
        }
        var s=b.store;long px=x.min()+100;long initial=100000000;
        s.credit(u,initial);s.credit(v,initial);s.claim(v,x.id(),100,null,"");
        long sell=s.create(v,x.id(),false,10,px,false);
        long buy=s.create(u,x.id(),true,4,px+100,false);
        ok(s.find(sell).remaining()==6,"llenado parcial");ok(s.find(buy).remaining()==0,"cruce inmediato");
        ok(s.available(u,x.id())==4,"retiro del comprador");ok(s.wallet(u)==initial-4*px,"reembolso diferencia precio");
        ok(s.wallet(v)==initial+4*px-BazarStore.tax(4*px),"impuesto exacto");
        long sell2=s.create(v,x.id(),false,10,px,false);s.create(u,x.id(),true,8,px,false);
        ok(s.find(sell).remaining()==0&&s.find(sell2).remaining()==8,"misma punta gana antigüedad");
        s.cancel(v,sell2);ok(s.available(v,x.id())==88,"cancelar devuelve solo restante");
        ok(s.find(sell2).filled()==2&&s.find(sell2).cancelled(),"avance conserva llenado al cancelar");
        long buy2=s.create(u,x.id(),true,5,px-10,false);long before=s.wallet(u);s.cancel(u,buy2);
        ok(s.wallet(u)==before+5*(px-10),"cancelar compra devuelve escrow");
        before=s.wallet(u);s.cancel(u,buy2);ok(s.wallet(u)==before,"cancelar doble sin duplicación");
        rejects(()->s.cancel(u,sell),"no cancelar orden ajena");
        rejects(()->s.create("pobre",x.id(),true,1,px,false),"plata insuficiente");
        rejects(()->s.create(u,"minecraft:iron_ingot",true,1,px,false),"orden vanilla rechazada");
        rejects(()->s.create(u,"espada_1",true,1,px,false),"nunca compra equipo");
        rejects(()->s.create(u,x.id(),true,71681,px,false),"máximo 71680");
        rejects(()->s.create(u,x.id(),true,0,px,false),"cantidad cero");
        rejects(()->s.create(u,x.id(),true,1,x.min()-1,false),"precio mínimo");
        rejects(()->s.create(u,x.id(),true,1,x.max()+1,false),"precio máximo");
        s.credit("limit",100000000000L);for(int i=0;i<14;i++)s.create("limit",x.id(),true,1,x.min(),false);
        rejects(()->s.create("limit",x.id(),true,1,x.min(),false),"tope 14");
        s.credit(u,100000000000L);long max=s.create(u,x.id(),true,71680,x.min(),false);ok(s.find(max).remaining()==71680,"acepta 71680");s.cancel(u,max);
        long same=s.create(u,x.id(),true,1,px,false);s.claim(u,x.id(),1,null,"");long own=s.create(u,x.id(),false,1,px,false);
        ok(s.find(same).remaining()==1&&s.find(own).remaining()==1,"sin auto negociación");s.cancel(u,same);s.cancel(u,own);
        // One maker, two buyers submitted on the primary thread; second never receives first's units.
        s.claim("seller",x.id(),3,null,"");long race=s.create("seller",x.id(),false,3,px,false);
        s.credit("r1",100000000000L);s.credit("r2",100000000000L);s.create("r1",x.id(),true,2,px,true);s.create("r2",x.id(),true,2,px,true);
        ok(s.available("r1",x.id())+s.available("r2",x.id())==3,"dos compradores misma orden sin dupe");
        ok(s.find(race).remaining()==0,"orden concurrente agotada");
        var liquid=b.products.get("coral_astral");s.claim("depth",liquid.id(),100,null,"");
        for(int i=0;i<9;i++)s.create("depth",liquid.id(),false,2,liquid.min()+i*10,false);
        long quote=b.quote(a,liquid,30);long cashBefore=s.wallet(u);int stockBefore=s.available(u,liquid.id());
        b.instantBuy(a,liquid,30);
        ok(s.available(u,liquid.id())==stockBefore+18,"instantánea consume nueve niveles y liquidez parcial");
        ok(s.wallet(u)==cashBefore-quote,"instantánea cobra profundidad exacta");
        long rollback=s.wallet(u);
        rejects(()->s.tx(()->{s.create(u,liquid.id(),true,1,liquid.min(),false);throw new IllegalStateException("rollback");}),"rollback de transacción anidada");
        ok(s.wallet(u)==rollback,"rollback conserva saldo");
        ok(BazarStore.tax(8000)==100&&BazarStore.tax(10000)==125,"impuesto 1,25% exacto en centavos");
        ok(s.average(x.id(),1)>0&&s.average(x.id(),24)>0,"historial hora/día");
        ok(s.book(x.id(),true).size()<=7&&s.book(x.id(),false).size()<=7,"siete puntas");
        // Actual Vault, inventory and durable transfers.
        b.economy.depositPlayer(a,1000000);double cash=b.economy.getBalance(a);long wallet=s.wallet(u);
        b.fund(a,10000);ok(Math.abs(b.economy.getBalance(a)-(cash-100))<.005&&s.wallet(u)==wallet+10000,"Vault cobra y guarda");
        b.pay(a,10000);ok(Math.abs(b.economy.getBalance(a)-cash)<.005&&s.wallet(u)==wallet,"Vault retira una vez");
        a.getInventory().clear();var stack=x.item().clone();stack.setAmount(16);a.getInventory().setItem(0,stack);
        before=s.available(u,x.id());b.deposit(a,0,16,x.id(),"");ok(a.getInventory().getItem(0)==null&&s.available(u,x.id())==before+16,"depósito con recibo");
        for(int i=0;i<36;i++)a.getInventory().setItem(i,new ItemStack(Material.STONE,64));
        var claim=s.claims(u).stream().filter(c->c.product().equals(x.id())).findFirst().orElseThrow();int amount=claim.qty();b.withdraw(a,claim);
        ok(s.claims(u).stream().filter(c->c.id()==claim.id()).findFirst().orElseThrow().qty()==amount,"inventario lleno conserva retiro");
        a.getInventory().setItem(0,null);b.withdraw(a,claim);ok(a.getInventory().getItem(0)!=null,"retiro solo lo que cabe");
        a.getInventory().clear();
        ItemStack weapon=Bukkit.getItemFactory().createItemStack(cfg.getString("equipo.espada_1.item"));
        String armorID=cfg.getConfigurationSection("equipo").getKeys(false).stream().filter(id->id.contains("helmet")&&cfg.getInt("equipo."+id+".tier")==3).findFirst().orElseThrow();
        ItemStack armor=Bukkit.getItemFactory().createItemStack(cfg.getString("equipo."+armorID+".item"));
        ok(b.gear(weapon).tier()==1&&b.gear(armor).tier()==3,"arma T1 armadura T3");
        weapon.addUnsafeEnchantment(org.bukkit.enchantments.Enchantment.UNBREAKING,1);ok(b.improved(weapon,b.gear(weapon)),"equipo encantado requiere confirmación");
        for(String id:List.of("gomera","fragmento_marea")){
            // source items not in the positive equipment catalog
            ok(!cfg.getConfigurationSection("equipo").contains(id),"historia excluida "+id);
        }
        ok(b.gear(new ItemStack(Material.DIAMOND_SWORD))==null,"equipo vanilla rechazado");
        ok(b.gear(new ItemStack(Material.PLAYER_HEAD))==null,"mochila mascota cosmético rechazados");
        ok(cfg.getConfigurationSection("equipo").getKeys(false).stream().noneMatch(id->id.startsWith("taladro_")||id.startsWith("motosierra_")||id.equals("agua_pico")),"oficios taladros motosierras fuera de lista");
        a.getInventory().setItem(0,weapon);b.deposit(a,0,1,"equipo","sale");a.getInventory().setItem(1,armor);b.deposit(a,1,1,"equipo","sale");
        var tiers=new HashMap<Long,Integer>();for(var c:s.claims(u))if(c.basket().equals("sale"))tiers.put(c.id(),b.gear(b.claimItem(c)).tier());
        wallet=s.wallet(u);s.sellEquipment(u,"sale",b.equipmentPrices,tiers);ok(s.wallet(u)==wallet+300000+1200000,"equipo paga T1 3000 + T3 12000");
        s.sellEquipment(u,"sale",b.equipmentPrices,tiers);ok(s.wallet(u)==wallet+1500000,"doble confirmar no paga dos veces");
        a.getInventory().setItem(0,armor);b.equipmentScreen(a,"close-test");b.deposit(a,0,1,"equipo","close-test");a.closeInventory();
        ok(Arrays.stream(a.getInventory().getStorageContents()).filter(Objects::nonNull).anyMatch(it->it.isSimilar(armor)),"cerrar sin confirmar devuelve equipo");
        a.getInventory().clear();a.getInventory().setItem(0,armor);b.equipmentScreen(a,"full-test");b.deposit(a,0,1,"equipo","full-test");for(int i=0;i<36;i++)a.getInventory().setItem(i,new ItemStack(Material.STONE,64));a.closeInventory();
        ok(s.claims(u).stream().anyMatch(c->c.product().equals("equipo")&&c.basket().isEmpty()),"cerrar lleno guarda equipo para retirar");
        ok(a.getWorld().getEntitiesByClass(org.bukkit.entity.Item.class).stream().noneMatch(i->i.getItemStack().isSimilar(armor)),"sin tirar equipo al piso");
        // 1.2.0: navegación y operaciones usando las acciones reales de cada ventana.
        a.getInventory().clear();z.addAttachment(b,"astral.bazar.usar",true);
        var y=b.products.get("nucleo_furia");long yp=y.min()+1000;
        s.credit(v,100000000000L);s.credit(u,100000000000L);
        b.home(a);var home=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        ok(!a.getOpenInventory().getTitle().equals("Bazar - Inicio")&&home.artwork,"inicio con diseno (glifo)");
        for(int i=0;i<5;i++)ok(home.actions.containsKey(i*9),"categoría columna "+i);
        ok(Arrays.stream(AstralBazar.PRODUCT_SLOTS).anyMatch(i->home.inv.getItem(i)!=null),"inicio ya muestra productos");
        for(int slot:new int[]{45,46,47,48,53})ok(home.actions.containsKey(slot),"inicio acción "+slot);
        b.listing(a,"Combate","",0);var listing=a.getOpenInventory().getTopInventory();
        var icon=listing.getItem(AstralBazar.PRODUCT_SLOTS[0]);
        ok(icon.getItemMeta().getLore().stream().noneMatch(l->l.contains("Rango")),"producto sin rango");
        ok(icon.getItemMeta().getLore().getFirst().contains("Comprar al instante"),"producto precio instantáneo");
        b.detail(a,y);var detail=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        ok(detail.artwork&&detail.inv.getItem(4)!=null&&detail.actions.containsKey(16),"producto con el item arriba y tarjetas anchas");
        for(int slot:new int[]{10,14,28,32,45,51})ok(detail.actions.containsKey(slot),"producto cuatro acciones y navegación "+slot);
        b.amount(a,y,true,true);var amountUI=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        for(int slot:new int[]{10,12,15,16})ok(amountUI.actions.containsKey(slot),"cantidad instantánea "+slot);
        b.amount(a,y,true,false);amountUI=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        ok(amountUI.inv.getItem(10).getItemMeta().getDisplayName().contains("64")&&amountUI.inv.getItem(13).getItemMeta().getDisplayName().contains("160")&&amountUI.inv.getItem(16).getItemMeta().getDisplayName().contains("1024"),"cantidades de órdenes 64/160/1024");
        ok(b.marginPrice(y,true)==0,"margen deshabilitado sin puntas");
        long bid=s.create(v,y.id(),true,100,yp,false);s.claim(v,y.id(),200,null,"");long ask=s.create(v,y.id(),false,100,yp+2000,false);
        ok(b.marginPrice(y,true)==yp+100&&b.marginPrice(y,false)==yp+1900,"5% desde ambos extremos del margen");
        b.choosePrice(a,y,true,false,64);var priceUI=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        for(int slot:new int[]{10,12,14,16})ok(priceUI.actions.containsKey(slot),"cuatro opciones precio "+slot);
        // Comprar: entrega inmediata; la contraparte conserva cobro por orden.
        a.getInventory().clear();double oldBalance=b.economy.getBalance(a);long oldWallet=s.wallet(u);
        b.confirm(a,y,true,true,3,y.max());var confirm=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();confirm.actions.get(36).run();
        ok(b.count(a,y)==3,"compra instantánea directo al inventario");
        ok(s.wallet(u)==0&&Math.abs(b.economy.getBalance(a)-(oldBalance+(oldWallet-3*(yp+2000))/100.0))<.01,"compra cobra precio real y devuelve diferencia al saldo");
        ok(s.orderMoney(v,ask)==3*(yp+2000)-BazarStore.tax(3*(yp+2000)),"venta contraparte cobra desde su orden");
        // Inventario lleno: no cae nada; Mis órdenes conserva y entrega después.
        for(int i=0;i<36;i++)a.getInventory().setItem(i,new ItemStack(Material.STONE,64));
        b.confirm(a,y,true,true,2,y.max());confirm=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();confirm.actions.get(36).run();
        ok(s.available(u,y.id())==2,"compra con inventario lleno queda para cobrar");
        a.getInventory().clear();b.collectAll(a);ok(b.count(a,y)==2&&s.available(u,y.id())==0,"cobrar todo recupera exceso");
        // Vender al instante todo; sobrante vuelve y el neto llega a Vault.
        a.getInventory().clear();var ys=y.item().clone();ys.setAmount(5);a.getInventory().setItem(0,ys);
        double tradeCash=b.economy.getBalance(a);b.detail(a,y);detail=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();detail.actions.get(14).run();
        confirm=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();confirm.actions.get(36).run();
        ok(b.count(a,y)==0&&Math.abs(b.economy.getBalance(a)-tradeCash-(5*yp-BazarStore.tax(5*yp))/100.0)<.01,"vender todo al instante paga al saldo");
        s.cancel(v,bid);bid=s.create(v,y.id(),true,2,yp,false);ys.setAmount(5);a.getInventory().setItem(0,ys);
        b.confirm(a,y,false,true,5,y.min());confirm=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();confirm.actions.get(36).run();
        ok(b.count(a,y)==3,"venta parcial devuelve sobrante al inventario");
        // Venta de inventario no toca equipo ni ítems vanilla.
        bid=s.create(v,y.id(),true,2,yp,false);a.getInventory().setItem(1,weapon);a.getInventory().setItem(2,new ItemStack(Material.PAPER,4));
        b.sellInventory(a);var invUI=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        ok(invUI.inv.getItem(0)!=null&&invUI.inv.getItem(49).getItemMeta().getDisplayName().contains("Confirmar"),"vender inventario resumen y total");
        tradeCash=b.economy.getBalance(a);invUI.actions.get(49).run();
        ok(b.count(a,y)==1&&a.getInventory().getItem(1).isSimilar(weapon)&&a.getInventory().getItem(2).getAmount()==4,"venta inventario conserva equipo vanilla y sobrante");
        ok(b.economy.getBalance(a)>tradeCash,"venta inventario paga directo");
        // Cobro por orden y cancelar sin repetir; productos de dos dueños.
        long buyerOrder=s.create(v,y.id(),true,2,yp,false);ys.setAmount(1);a.getInventory().setItem(0,ys);b.depositProduct(a,y,1);
        long sellerOrder=s.create(u,y.id(),false,1,yp,false);tradeCash=b.economy.getBalance(a);b.collectOrder(a,sellerOrder);
        ok(Math.abs(b.economy.getBalance(a)-tradeCash-(yp-BazarStore.tax(yp))/100.0)<.01,"cobrar dinero desde orden");
        tradeCash=b.economy.getBalance(a);b.collectOrder(a,sellerOrder);ok(b.economy.getBalance(a)==tradeCash,"orden no cobra dos veces");
        z.getInventory().clear();b.collectOrder(z,buyerOrder);ok(b.count(z,y)==1,"comprador cobra producto desde orden");
        rejects(()->b.collectOrder(a,buyerOrder),"cobro ajeno rechazado");
        b.orders(z,0);var ordersUI=(AstralBazar.Screen)z.getOpenInventory().getTopInventory().getHolder();
        int cancelSlot=-1;for(int i:ordersUI.rightActions.keySet())if(ordersUI.inv.getItem(i).getItemMeta().getDisplayName().contains("#"+buyerOrder+" "))cancelSlot=i;
        ok(cancelSlot>=0&&ordersUI.inv.getItem(45).getItemMeta().getDisplayName().contains("Cobrar todo"),"órdenes ventana única con cobrar todo y clic derecho");
        ordersUI.rightActions.get(cancelSlot).run();ok(s.find(buyerOrder).remaining()==0,"clic derecho cancela restante");
        // Entradas: comando conservado, cancelación, vencimiento y captura del chat.
        String[] inputValue={""};b.ask(a,"Prueba",text->inputValue[0]=text);b.onCommand(a,b.getCommand("bazar"),"bazar",new String[]{"entrada","12,34"});ok(inputValue[0].equals("12,34"),"entrada por comando compatible");
        b.ask(a,"Prueba",text->inputValue[0]="no");b.acceptInput(a,"cancelar");ok(inputValue[0].equals("12,34")&&!b.inputs.containsKey(a.getUniqueId()),"cancelar entrada sin callback");
        b.ask(a,"Prueba",text->inputValue[0]="no");b.inputDeadlines.put(a.getUniqueId(),System.currentTimeMillis()-1);b.acceptInput(a,"99");ok(inputValue[0].equals("12,34"),"entrada vencida rechazada");
        b.ask(a,"Prueba chat",text->{});
        var chat=new io.papermc.paper.event.player.AsyncChatEvent(false,a,new HashSet<>(),io.papermc.paper.chat.ChatRenderer.defaultRenderer(),net.kyori.adventure.text.Component.text("secreto"),net.kyori.adventure.text.Component.text("secreto"),null);
        b.chat(chat);ok(chat.isCancelled(),"chat capturado sin publicación");b.inputs.remove(a.getUniqueId());b.inputDeadlines.remove(a.getUniqueId());
        ok(a.getWorld().getEntitiesByClass(org.bukkit.entity.Item.class).stream().noneMatch(i->b.product(i.getItemStack())!=null),"ninguna operación tira productos al piso");
        // Abrir una copia exacta del esquema 1.1.0 con custodia, saldo y órdenes.
        Path oldDb=b.getDataFolder().toPath().resolve("legacy-110.sqlite");
        try(var legacy=java.sql.DriverManager.getConnection("jdbc:sqlite:"+oldDb);var q=legacy.createStatement()){
            q.execute("CREATE TABLE wallet(owner TEXT PRIMARY KEY,cents INTEGER NOT NULL)");q.execute("INSERT INTO wallet VALUES('legacy',12345)");
            q.execute("CREATE TABLE claims(id INTEGER PRIMARY KEY AUTOINCREMENT,owner TEXT,product TEXT,qty INTEGER,item BLOB,basket TEXT NOT NULL DEFAULT '')");q.execute("INSERT INTO claims(owner,product,qty) VALUES('legacy','"+y.id()+"',7)");
            q.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY AUTOINCREMENT,owner TEXT,product TEXT,buy INTEGER,quantity INTEGER,remaining INTEGER,price INTEGER,gross INTEGER DEFAULT 0,tax INTEGER DEFAULT 0,filled INTEGER DEFAULT 0,cancelled INTEGER DEFAULT 0)");
            q.execute("INSERT INTO orders(owner,product,buy,quantity,remaining,price) VALUES('legacy','"+y.id()+"',0,3,3,"+yp+")");
        }
        try(var legacy=new BazarStore(oldDb,s.products)){
            ok(legacy.wallet("legacy")==12345&&legacy.available("legacy",y.id())==7&&legacy.orders("legacy").size()==1,"migración 1.1.0 conserva saldo custodia y orden");
            legacy.cancel("legacy",1);ok(legacy.available("legacy",y.id())==10,"migración 1.1.0 puede cancelar y cobrar devolución");
            legacy.sql("UPDATE wallet SET owner=? WHERE owner='legacy'",u);legacy.sql("UPDATE claims SET owner=? WHERE owner='legacy'",u);legacy.sql("UPDATE orders SET owner=? WHERE owner='legacy'",u);
            a.getInventory().clear();double balance110=b.economy.getBalance(a);b.store=legacy;
            try{
                b.collectAll(a);ok(b.count(a,y)==10&&Math.abs(b.economy.getBalance(a)-balance110-123.45)<.01&&legacy.wallet(u)==0&&legacy.available(u,y.id())==0,"base 1.1.0 cobra inventario y saldo por UI nueva");
                long oldPrice=y.min()-1;
                legacy.sql("INSERT INTO orders(owner,product,buy,quantity,remaining,price) VALUES('oldSeller',?,0,2,2,?)",y.id(),oldPrice);
                b.fund(a,2*oldPrice);b.instantBuy(a,y,2);b.collectAll(a);
                ok(b.count(a,y)==12&&legacy.find(2).remaining()==0,"oferta 1.1.0 bajo mínimo nuevo sigue ejecutable");
            }
            finally{b.store=s;}
        }
        priceFlows();
        b.paused=true;rejects(()->b.check(a),"pausa bloquea operaciones");b.paused=false;
        b.home(a);var screen=(AstralBazar.Screen)a.getOpenInventory().getTopInventory().getHolder();
        for(ClickType type:List.of(ClickType.SHIFT_LEFT,ClickType.NUMBER_KEY,ClickType.DROP,ClickType.DOUBLE_CLICK,ClickType.SWAP_OFFHAND)){
            InventoryClickEvent event=type==ClickType.NUMBER_KEY?new InventoryClickEvent(a.getOpenInventory(),InventoryType.SlotType.CONTAINER,10,type,InventoryAction.HOTBAR_SWAP,0):new InventoryClickEvent(a.getOpenInventory(),InventoryType.SlotType.CONTAINER,10,type,InventoryAction.UNKNOWN);
            b.click(event);ok(event.isCancelled(),"bloqueo "+type);
        }
        var drag=new InventoryDragEvent(a.getOpenInventory(),new ItemStack(Material.STONE),new ItemStack(Material.STONE),false,Map.of(0,new ItemStack(Material.STONE)));b.drag(drag);ok(drag.isCancelled(),"arrastre bloqueado");a.closeInventory();
        // Real SQLite reopen after both journal boundaries; inventory receipt survives saveData.
        long j=s.prepare(u,"item_in",0,0,0,x.id(),7,x.item().serializeAsBytes(),"");
        a.getPersistentDataContainer().set(b.receipt,PersistentDataType.LONG,j);a.saveData();int prev=s.available(u,x.id());
        Path path=b.getDataFolder().toPath().resolve("bazar.sqlite");s.close();b.store=new BazarStore(path,s.products);var reopened=b.store;
        for(var t:reopened.pending())if(t.kind().equals("item_in"))reopened.settle(t.id(),a.getPersistentDataContainer().getOrDefault(b.receipt,PersistentDataType.LONG,0L)==t.id());
        ok(reopened.available(u,x.id())==prev+7,"reinicio tras recibo recupera una vez");reopened.settle(j,true);ok(reopened.available(u,x.id())==prev+7,"replay idempotente");
        j=reopened.prepare(u,"item_in",0,0,0,x.id(),9,x.item().serializeAsBytes(),"");reopened.settle(j,false);ok(reopened.available(u,x.id())==prev+7,"caída antes de guardar no acredita");
        j=reopened.prepare(u,"money_in",100,b.economy.getBalance(a),0,"",0,null,"");wallet=reopened.wallet(u);b.recoverMoney();ok(reopened.wallet(u)==wallet,"recuperar Vault sin cobro no acredita");
        j=reopened.prepare(u,"money_in",100,b.economy.getBalance(a),0,"",0,null,"");b.economy.withdrawPlayer(a,1);b.recoverMoney();ok(reopened.wallet(u)==wallet+100,"recuperar Vault cobrado acredita una vez");
        Path backup=b.getDataFolder().toPath().resolve("probe-backup.sqlite");reopened.backup(backup);ok(Files.size(backup)>0,"respaldo SQLite válido");
        // Abrupt process death after player save and before SQL settlement. The
        // runner starts the SAME server; PlayerJoin performs production recovery.
        a.getInventory().clear();a.getInventory().setItem(0,x.item().clone());
        long crashID=reopened.prepare(u,"item_in",0,0,0,x.id(),1,x.item().serializeAsBytes(),"");
        a.getInventory().setItem(0,null);a.getPersistentDataContainer().set(b.receipt,PersistentDataType.LONG,crashID);a.saveData();
        var saved=new Properties();saved.setProperty("checks",Integer.toString(checks));saved.setProperty("failures",Integer.toString(failures));
        saved.setProperty("quantity",Integer.toString(reopened.available(u,x.id())+1));saved.setProperty("wallet",Long.toString(reopened.wallet(u)));
        Files.createDirectories(getDataFolder().toPath());try(var output=Files.newOutputStream(crash)){saved.store(output,"Expected crash recovery");}
        getLogger().info("BAZ CRASH READY checks="+checks+" failures="+failures);Runtime.getRuntime().halt(0);
    }
}
