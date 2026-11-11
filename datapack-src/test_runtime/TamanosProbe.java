package astraltest;

import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import io.lumine.mythic.bukkit.MythicBukkit;
import kr.toxicity.model.api.BetterModel;
import java.util.*;

/** Solo Paper local: medidas y montaje reales; no sustituye un cliente grafico. */
public final class TamanosProbe extends JavaPlugin {
    int failures=0, tested=0;
    final List<Entity> spawned=new ArrayList<>();
    void check(boolean ok,String detail) {
        if(!ok)failures++;
        getLogger().info("TAMANOS "+(ok?"PASS ":"FAIL ")+detail);
    }
    @Override public boolean onCommand(CommandSender sender,Command command,String label,String[] args) {
        if(args.length>0 && args[0].equals("result")) {
            getLogger().info("TAMANOS RESULT tested="+tested+" failures="+failures);
            for(var e:spawned)if(e.isValid())e.remove();
            return true;
        }
        String mid=args[0];double expected=Double.parseDouble(args[1]);boolean mounted=args.length>2;
        var world=Bukkit.getWorlds().getFirst();var at=new Location(world,1000+tested*30,-60,1000);
        world.getChunkAt(at).setForceLoaded(true);
        world.getBlockAt(at.clone().subtract(0,1,0)).setType(Material.STONE);
        final LivingEntity entity;
        try {entity=(LivingEntity)MythicBukkit.inst().getAPIHelper().spawnMythicMob(mid,at);}
        catch(Exception ex){check(false,"spawn "+mid+": "+ex);return true;}
        entity.setAI(false);entity.setInvulnerable(true);entity.setGravity(false);spawned.add(entity);tested++;
        Spider spider=mounted?world.spawn(at,Spider.class):null;
        if(spider!=null){spider.setAI(false);spider.setGravity(false);spawned.add(spider);spider.addPassenger(entity);}
        Bukkit.getScheduler().runTaskLater(this,()->{
            var attr=entity.getAttribute(Attribute.SCALE);double actual=attr==null?-1:attr.getBaseValue();
            var registry=BetterModel.registryOrNull(entity.getUniqueId());
            check(Math.abs(actual-expected)<0.000001,mid+" mounted="+mounted+" scale="+actual+" expected="+expected+" height="+entity.getHeight()+" playerReference=1.8");
            check(registry!=null && registry.displays().count()>0,mid+" model displays loaded");
            if(spider!=null)check(entity.getVehicle()==spider,mid+" remains passenger without scale multiplier");
        },30);
        return true;
    }
}
