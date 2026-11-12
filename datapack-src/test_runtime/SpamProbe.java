package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import io.lumine.mythic.bukkit.MythicBukkit;

/** Ensayo local con el jugador NMS creado por UrgenteProbe; nunca instalar remoto. */
public final class SpamProbe extends JavaPlugin {
    int failures;
    Entity control;
    Player player;
    boolean second;
    void check(boolean ok,String label) {
        if(!ok)failures++;
        getLogger().info("SPAM "+(ok?"PASS ":"FAIL ")+label);
    }
    int clock(Entity e) {
        return Bukkit.getScoreboardManager().getMainScoreboard().getObjective("ad.clock").getScore(e.getUniqueId().toString()).getScore();
    }
    void move(Location loc) {player.teleport(loc);}
    void killRoom(World w,String tag) {
        for(Entity e:new ArrayList<>(w.getEntities()))
            if(e.getScoreboardTags().contains(tag))e.remove();
    }
    void later(long ticks,Runnable action) {Bukkit.getScheduler().runTaskLater(this,action,ticks);}
    Entity spawn(String type,Location loc) {
        try {return MythicBukkit.inst().getAPIHelper().spawnMythicMob(type,loc);}
        catch(Exception ex) {throw new IllegalStateException(ex);}
    }
    @Override public boolean onCommand(CommandSender sender,Command cmd,String label,String[] args) {
        if(args[0].equals("start")) {
            player=Bukkit.getPlayer("AstralProbe");
            World w=Bukkit.createWorld(new WorldCreator(getConfig().getString("world")).type(WorldType.FLAT).generateStructures(false));
            if(player==null || w==null)throw new IllegalStateException("Falta jugador o dimension");
            var api=MythicBukkit.inst().getAPIHelper();
            List<Double> pt=getConfig().getDoubleList("center");
            Location loc=new Location(w,pt.get(0),pt.get(1),pt.get(2));
            for(int x=loc.getBlockX()-96;x<=loc.getBlockX()+96;x+=16)
                for(int z=loc.getBlockZ()-96;z<=loc.getBlockZ()+96;z+=16)w.getChunkAt(x>>4,z>>4).setForceLoaded(true);
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute in minecraft:"+w.getName()+" run gamerule minecraft:spawn_mobs false");
            for(var raw:getConfig().getList("points")) {
                var point=(List<Number>)raw;
                int px=point.get(0).intValue(),py=point.get(1).intValue(),pz=point.get(2).intValue();
                for(int x=px-2;x<=px+2;x++)for(int z=pz-2;z<=pz+2;z++)
                    w.getBlockAt(x,py-1,z).setType(Material.STONE);
            }
            player.setAllowFlight(true);player.setFlying(true);
            control=spawn("astral_mina_control_sala1",loc);
            later(60,()-> {
                check(!control.getScoreboardTags().contains("mina.on") && clock(control)==0,"inactive controller untouched");
                move(loc);
            });
            later(110,()->check(clock(control)>0,"active controller clock advances automatically"));
            // Matar enemigos simula combate. La cola, timers y transiciones son reales.
            final int[] elapsed={0};
            Bukkit.getScheduler().runTaskTimer(this,task -> {
                elapsed[0]+=10;
                if(elapsed[0]<90)return;
                second|=control.getScoreboardTags().contains("mina.ola2");
                killRoom(w,"ad.mina.sala1");
                if(control.getScoreboardTags().contains("mina.fin") || elapsed[0]>=1800) {
                    check(second && control.getScoreboardTags().contains("mina.fin"),"automatic queue refill and both waves complete");
                    task.cancel();
                    control.remove();
                    control=spawn("astral_mina_control_sala1",loc);
                    move(loc);
                    later(40,()-> {
                        check(control.getScoreboardTags().contains("mina.on"),"new run starts before reset test");
                        move(new Location(Bukkit.getWorlds().getFirst(),0,-60,0));
                        later(240,()-> {
                            check(!control.getScoreboardTags().contains("mina.on") && clock(control)==0,"empty active room resets");
                            control.remove();
                            boss(w);
                        });
                    });
                }
            },0,10);
        }
        return true;
    }
    void boss(World w) {
        var api=MythicBukkit.inst().getAPIHelper();
        List<Double> pt=getConfig().getDoubleList("boss");
        Location loc=new Location(w,pt.get(0),pt.get(1),pt.get(2));
        w.getChunkAt(loc).setForceLoaded(true);
        Entity boss=spawn("astral_mina_control_"+getConfig().getString("boss_id"),loc);
        // La confirmacion de muerte real sigue siendo requisito de la victoria.
        boss.addScoreboardTag("mina.on");boss.addScoreboardTag("mina.ola1");
        boss.addScoreboardTag("mina.jefe.derrotado");
        move(loc);
        later(80,()-> {
            boolean chest=MythicBukkit.inst().getMobManager().getActiveMobs().stream().anyMatch(m ->
                m.getType().getInternalName().equals("astral_mina_cofre") && !m.getEntity().isDead());
            check(chest && boss.getScoreboardTags().contains("mina.fin"),"confirmed boss death opens chest");
            move(new Location(Bukkit.getWorlds().getFirst(),0,-60,0));
            later(240,()-> {
                check(!boss.getScoreboardTags().contains("mina.on"),"boss room resets");
                boss.remove();
                getLogger().info("SPAM RESULT failures="+failures);
            });
        });
    }
}
