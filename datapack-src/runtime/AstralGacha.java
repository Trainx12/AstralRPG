package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;

/** Cola pagada persistente. CrazyCrates elige y entrega cada premio antes del siguiente. */
final class AstralGacha {
    private final JavaPlugin plugin;
    private final NamespacedKey pending=new NamespacedKey("astral","gacha_pending");
    private final NamespacedKey flight=new NamespacedKey("astral","gacha_flight");
    private final NamespacedKey luck=new NamespacedKey("astral","suerte_hasta");
    private final Map<UUID,String> waiting=new HashMap<>();
    private static final Map<String,Integer> LIMITS=Map.of("gacha_rpg",50,"gacha_monturas",40,"gacha_cosmeticos",20);
    AstralGacha(JavaPlugin plugin) {
        this.plugin=plugin;
        Bukkit.getScheduler().runTaskTimer(plugin,()->{
            for(Player p:Bukkit.getOnlinePlayers())pump(p);
            waiting.keySet().removeIf(id->Bukkit.getPlayer(id)==null);
        },20,20);
    }
    void enqueue(Player p,String gid,int count) {
        boolean lucky=p.getPersistentDataContainer().getOrDefault(luck,PersistentDataType.LONG,0L)>System.currentTimeMillis();
        String data=data(p);
        save(p,data+(data.isEmpty()?"":";")+gid+","+count+","+lucky+",true");
        pump(p);
    }
    private String data(Player p){return p.getPersistentDataContainer().getOrDefault(pending,PersistentDataType.STRING,"");}
    private void save(Player p,String data) {
        if(data.isEmpty())p.getPersistentDataContainer().remove(pending);
        else p.getPersistentDataContainer().set(pending,PersistentDataType.STRING,data);
    }
    void ack(Player p,String gid) {
        if(!gid.equals(waiting.get(p.getUniqueId())))return;
        String[] jobs=data(p).split(";",2),job=jobs[0].split(",");
        int left=Integer.parseInt(job[1])-1;
        save(p,(left>0?job[0]+","+left+","+job[2]+",false"+(jobs.length>1?";":""):"")+(jobs.length>1?jobs[1]:""));
        waiting.remove(p.getUniqueId());
        p.getPersistentDataContainer().remove(flight);
        Bukkit.getScheduler().runTask(plugin,()->pump(p));
    }
    private Object crate(String name) throws ReflectiveOperationException {
        var cc=Bukkit.getPluginManager().getPlugin("CrazyCrates");
        if(cc==null || !cc.isEnabled())throw new IllegalStateException("CrazyCrates no disponible");
        Object platform=cc.getClass().getMethod("getPlatform").invoke(cc);
        Object manager=platform.getClass().getMethod("getCrateManager").invoke(platform);
        Object result=manager.getClass().getMethod("getCrateFromName",String.class).invoke(manager,name);
        if(result==null)throw new IllegalStateException("Falta caja "+name);
        return result;
    }
    private void pump(Player p) {
        if(!p.isOnline() || data(p).isEmpty() || waiting.containsKey(p.getUniqueId()))return;
        try {
            // AuthMe, si esta presente, debe haber autenticado al jugador al reanudar.
            var auth=Bukkit.getPluginManager().getPlugin("AuthMe");
            if(auth!=null) {
                var api=Class.forName("fr.xephi.authme.api.v3.AuthMeApi",true,auth.getClass().getClassLoader());
                if(!(boolean)api.getMethod("isAuthenticated",Player.class).invoke(api.getMethod("getInstance").invoke(null),p))return;
            }
            String[] job=data(p).split(";",2)[0].split(",");String gid=job[0];
            String objective="pity_"+gid.substring(6);
            var board=Bukkit.getScoreboardManager().getMainScoreboard();
            var obj=board.getObjective(objective);
            if(obj==null)obj=board.registerNewObjective(objective,org.bukkit.scoreboard.Criteria.DUMMY,objective);
            var score=obj.getScore(p.getName());int before=score.getScore();
            String recovery=p.getPersistentDataContainer().get(flight,PersistentDataType.STRING);
            if(recovery!=null) {
                // Reinicio/logout durante la animacion sin premio confirmado: repetir la misma tirada.
                String[] previous=recovery.split(",");
                if(previous[0].equals(gid)){before=Integer.parseInt(previous[1]);score.setScore(before);}
                p.getPersistentDataContainer().remove(flight);
            }
            boolean guaranteed=before+1>=LIMITS.get(gid);
            String name=gid+(guaranteed?"_garantia":"")+(Boolean.parseBoolean(job[2])?"_suerte":"");
            Object c=crate(name);
            Object cc=Bukkit.getPluginManager().getPlugin("CrazyCrates");
            Object platform=cc.getClass().getMethod("getPlatform").invoke(cc);
            Object cache=platform.getClass().getMethod("getCacheManager").invoke(platform);
            if((boolean)cache.getClass().getMethod("hasOpeningCrate",UUID.class).invoke(cache,p.getUniqueId()))return;
            // Resolver API antes de tocar el contador. No hay llaves diferidas ni mass-open.
            ClassLoader loader=c.getClass().getClassLoader();
            Class<?> prize=Class.forName("com.badbones69.crazycrates.paper.api.objects.Prize",true,loader);
            var give=Class.forName("com.badbones69.crazycrates.paper.api.PrizeManager",true,loader)
                .getMethod("givePrize",Player.class,c.getClass(),prize);
            boolean first=Boolean.parseBoolean(job[3]);
            if(first && p.getInventory().firstEmpty()<0)return;
            Object chosen=first?null:c.getClass().getMethod("pickPrize",Player.class).invoke(c,p);
            if(!first && chosen==null)throw new IllegalStateException("Sin premio disponible");
            p.getPersistentDataContainer().set(flight,PersistentDataType.STRING,gid+","+before);
            score.setScore(before+1);waiting.put(p.getUniqueId(),gid);
            if(first) {
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"crates forceopen "+name+" "+p.getName());
                var counter=score;
                int prior=before;
                Bukkit.getScheduler().runTaskLater(plugin,()->{
                    try {
                        if(waiting.containsKey(p.getUniqueId()) && !(boolean)cache.getClass()
                            .getMethod("hasOpeningCrate",UUID.class).invoke(cache,p.getUniqueId())) {
                            waiting.remove(p.getUniqueId());counter.setScore(prior);
                            p.getPersistentDataContainer().remove(flight);
                        }
                    }catch(ReflectiveOperationException ex){plugin.getLogger().warning(ex.toString());}
                },2);
            } else give.invoke(null,p,c,chosen);
        } catch(Exception ex) {
            // Conservar las tiradas compradas si falta el plugin o una caja; reintentar al reparar.
            plugin.getLogger().warning("Gacha pendiente para "+p.getName()+": "+ex.getClass().getSimpleName()+" "+ex.getMessage());
        }
    }
}
