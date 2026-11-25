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
        getLogger().info("BAZ RESULT checks="+checks+" failures="+failures);Bukkit.shutdown();
    },40,20);}
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
        s.credit("r1",1000000);s.credit("r2",1000000);s.create("r1",x.id(),true,2,px,true);s.create("r2",x.id(),true,2,px,true);
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
        ok(a.getWorld().getEntitiesByClass(org.bukkit.entity.Item.class).isEmpty(),"sin tirar equipo al piso");
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
