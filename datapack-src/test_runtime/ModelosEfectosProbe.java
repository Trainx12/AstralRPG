package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;

/** Solo ensayo local. Nunca instalar en produccion. */
public final class ModelosEfectosProbe extends JavaPlugin {
    int failures;
    @Override public void onEnable() {
        // Solo el ensayo opcional de economia: proveedor Vault ficticio, sin dinero real.
        if(Boolean.getBoolean("astral.probe.economia")) try {
            Class type=Class.forName("net.milkbowl.vault.economy.Economy");
            Object provider=java.lang.reflect.Proxy.newProxyInstance(type.getClassLoader(),new Class[]{type},(proxy,method,args)->{
                if(method.getName().equals("getName"))return "AstralProbe";
                Class r=method.getReturnType();
                if(r==boolean.class)return true;
                if(r==double.class)return 1000000d;
                if(r==int.class)return 2;
                if(r==String.class)return "monedas";
                if(r==List.class)return List.of();
                return null;
            });
            Bukkit.getServicesManager().register(type,provider,this,org.bukkit.plugin.ServicePriority.Normal);
        }catch(Exception ex){throw new RuntimeException(ex);}
    }
    void check(boolean ok,String message) {
        if(!ok)failures++;
        getLogger().info("FX "+(ok?"PASS ":"FAIL ")+message);
    }
    long sprites(World w) {return w.getEntities().stream().filter(Entity::isValid).filter(e->e.getScoreboardTags().contains("astral.fx.sprite")).count();}
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command cmd, String label, String[] args) {
        try {
            World w=Bukkit.getWorlds().getFirst();
            w.getChunkAt(0,0).setForceLoaded(true);
            for(String plugin:List.of("AstralDecor","AstralEfectos","BetterModel","MythicMobs"))
                check(Bukkit.getPluginManager().isPluginEnabled(plugin),plugin+" activo");
            var ids=new ArrayList<>(List.of("frasco_xp_pequeno","frasco_xp_grande","frasco_xp_gigante","barril_xp","manzana_esmeralda","gancho"));
            for(int i=1;i<=10;i++)ids.add("cuchillo_"+i);
            for(String id:ids) {
                var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id));
                check(table!=null && !table.populateLoot(new Random(1),new org.bukkit.loot.LootContext.Builder(new Location(w,0,65,0)).build()).isEmpty(),"loot real "+id);
            }
            if(Boolean.getBoolean("astral.probe.economia")) {
                check(Bukkit.getPluginManager().isPluginEnabled("EconomyShopGUI"),"EconomyShopGUI real activo");
                Class api=Class.forName("me.gypopo.economyshopgui.api.EconomyShopGUIHook",true,Bukkit.getPluginManager().getPlugin("EconomyShopGUI").getClass().getClassLoader());
                var price=api.getMethod("getItemSellPrice",org.bukkit.inventory.ItemStack.class);
                w.getBlockAt(0,64,0).setType(Material.CHEST);
                var chest=(org.bukkit.block.Chest)w.getBlockAt(0,64,0).getState();
                var foods=List.of("cnk:food/dough","cnk:food/bread","astral:item/frasco_xp_gigante");
                for(int i=0;i<foods.size();i++)
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"loot replace block 0 64 0 container."+i+" loot "+foods.get(i));
                // Los comandos nativos despachados dentro de otro comando se
                // ejecutan cuando termina la cola actual, no antes de este retorno.
                Bukkit.getScheduler().runTaskLater(this,()->{
                    try {for(int i=0;i<foods.size();i++) {
                        var it=chest.getInventory().getItem(i);
                        check(it!=null,"loot de cocina generado "+foods.get(i));
                        if(it==null)continue;
                        Double value=(Double)price.invoke(null,it);
                        check(value==null || value<=0,"venta custom rechazada "+foods.get(i)+" precio="+value);
                    }}catch(Exception ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"FX FAIL economia",ex);}
                },2);
                for(Material mat:List.of(Material.BREAD,Material.POISONOUS_POTATO)) {
                    Double value=(Double)price.invoke(null,new org.bukkit.inventory.ItemStack(mat));
                    check(value!=null && value>0,"venta vanilla conserva precio "+mat+" precio="+value);
                }
            }
            for(String id:List.of("astral_goblin_vendedor","astral_golem_bosque_infinita","astral_golem_hielo_infinita","astral_golem_cristal_infinita","astral_pet_fenix","astral_santuario_trainx")) {
                var entity=io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob(id,new Location(w,8,65,0));
                check(entity!=null && entity.isValid(),"spawn "+id);
                if(entity!=null)Bukkit.getScheduler().runTaskLater(this,()->entity.remove(),30);
            }
            var console=Bukkit.getConsoleSender();
            Bukkit.dispatchCommand(console,"astralfx prueba on");
            Bukkit.dispatchCommand(console,"astralfx golpe "+w.getName()+" 0 65 0 7cff5a 4 fuego");
            Bukkit.dispatchCommand(console,"astralfx rayo "+w.getName()+" 0 65 0 8 65 0 d24bff arcano");
            Bukkit.dispatchCommand(console,"astralfx estela "+w.getName()+" 0 65 0 3fa8ff 2 agua");
            Bukkit.dispatchCommand(console,"summon marker 0 65 0 {Tags:[\"astral.fx\",\"fx.estallido\",\"fxc.7cff5a\"]}");
            Bukkit.getScheduler().runTaskLater(this,()->check(sprites(w)>0 && sprites(w)<=320,"dibujos creados dentro del tope: "+sprites(w)),2);
            Bukkit.getScheduler().runTaskLater(this,()->{
                check(sprites(w)==0,"dibujos eliminados tras 4 segundos");
                Bukkit.dispatchCommand(console,"astralfx prueba off");
                getLogger().info("FX RESULT failures="+failures);
            },80);
        } catch(Throwable ex) {failures++;getLogger().log(java.util.logging.Level.SEVERE,"FX FAIL exception",ex);}
        return true;
    }
}
