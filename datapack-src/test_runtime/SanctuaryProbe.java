package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.command.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.event.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
import io.lumine.mythic.bukkit.MythicBukkit;
import io.lumine.mythic.bukkit.events.MythicMobSpawnEvent;

/** Ensayo de estado, con jugador simulado y IA congelada. No prueba combate ni imagen. */
public final class SanctuaryProbe extends JavaPlugin implements Listener {
    World world; Player player; int failures, checks;
    final String[] ids={"cangrejo","chaman","momia","yeti","golem_forja"};
    final double[][] points={{233.5,57,1.5},{299.5,57,37.5},{267.5,57,106.5},{197.5,57,36.5},{247.5,57,19.5}};
    void check(boolean ok,String message) {checks++;if(!ok)failures++;getLogger().info("SANCTUARY "+(ok?"PASS ":"FAIL ")+message);}
    public void onEnable(){Bukkit.getPluginManager().registerEvents(this,this);}
    @EventHandler public void spawn(MythicMobSpawnEvent event){
        if(event.getEntity() instanceof LivingEntity e){e.setAI(false);e.setGravity(false);}
    }
    List<LivingEntity> mobs(String name){
        var result=new ArrayList<LivingEntity>();
        for(var mob:MythicBukkit.inst().getMobManager().getActiveMobs())
            if(mob.getType().getInternalName().equals(name) && !mob.isDead())
                result.add((LivingEntity)mob.getEntity().getBukkitEntity());
        return result;
    }
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var handle=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),"SanctuaryProbe");
        var fake=new ServerPlayer(server,handle,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        fake.setPos(0,100,0);handle.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);field.setAccessible(true);
            ((Map)field.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setOp(true);p.setInvulnerable(true);p.setGravity(false);return p;
    }
    boolean clear(double[] p,int width,int height){
        int x=(int)Math.floor(p[0]),y=(int)p[1],z=(int)Math.floor(p[2]);
        for(int dx=-width/2;dx<=width/2;dx++)for(int dz=-width/2;dz<=width/2;dz++){
            if(!world.getBlockAt(x+dx,y-1,z+dz).getType().isSolid())return false;
            for(int h=0;h<height;h++)if(!world.getBlockAt(x+dx,y+h,z+dz).isEmpty())return false;
        }return true;
    }
    public boolean onCommand(CommandSender sender,Command cmd,String label,String[] args){
      try {
        switch(args[0]){
        case "start" -> {
            world=Bukkit.getWorld(NamespacedKey.minecraft("santuario_azeroth"));
            check(world!=null,"dimension del datapack cargada");if(world==null)return true;
            getLogger().info("SANCTUARY world name="+world.getName()+" key="+world.getKey());
            check(world.getForceLoadedChunks().size()==169,"169 chunks del recorrido cargados por datapack");
            var type=((CraftWorld)world).getHandle().dimensionType();
            check(type.skybox().toString().equalsIgnoreCase("end"),"skybox End: "+type.skybox());
            check(!type.hasEnderDragonFight() && world.getEnderDragonBattle()==null,"sin pelea de dragon");
            check(world.getHighestBlockYAt(1000,1000)<world.getMinHeight()+1,"generacion vacia fuera del mapa");
            for(int i=0;i<5;i++)check(clear(points[i],5,9),"piso 5x5 y aire 9: "+ids[i]);
            check(clear(new double[]{247.5,57,14.5},1,3),"llegada segura");
            check(clear(new double[]{247.5,57,23.5},1,3) && clear(new double[]{249.5,57,23.5},1,3),"cofre y guia seguros");
            player=fake();player.setGameMode(GameMode.SURVIVAL);
            Bukkit.dispatchCommand(player,"mazmorras santuario");
            Bukkit.getScheduler().runTaskLater(this,()->check(player.getWorld()==world && player.getLocation().distance(new Location(world,247.5,57,14.5))<.1,"comando de viaje del menu"),30);
            world.getChunkAt(15,1).setForceLoaded(true);
            MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_santuario_control_sala1",new Location(world,247.5,57,19.5));
        }
        case "wave" -> {
            int i=Integer.parseInt(args[1]);var found=mobs("astral_santuario_"+ids[i]+"_eco");
            check(found.size()==1,"oleada "+(i+1)+" un Ancestral: "+found.size());
            if(found.size()==1){
                var e=found.getFirst();var p=points[i];
                check(e.getLocation().distance(new Location(world,p[0],p[1],p[2]))<.1,"aparicion exacta "+ids[i]);
                check(e.getHealth()>0 && world.getBlockAt(e.getLocation().subtract(0,1,0)).getType().isSolid(),"jefe vivo sobre piso");
                e.setHealth(0);
            }
            // Ayudantes de fases/afijos no se combaten en este ensayo de estado.
            for(var e:new ArrayList<>(world.getLivingEntities())) {
                if(e instanceof Player || e instanceof ArmorStand || e.isDead())continue;
                var active=MythicBukkit.inst().getMobManager().getActiveMob(e.getUniqueId());
                if(active.isPresent() && active.get().getType().getInternalName().startsWith("astral_santuario_"))continue;
                e.setHealth(0);
            }
            getLogger().info("SANCTUARY alive="+world.getLivingEntities().stream().filter(e->!e.isDead()).map(e->e.getType()+":"+e.getName()).toList());
        }
        case "final" -> {
            check(mobs("astral_santuario_cofre").size()==1,"cofre final unico");
            check(mobs("astral_santuario_guia").size()==1,"guia final unico");
            player.teleport(new Location(world,247.5,-5,14.5));
        }
        case "rescue" -> {
            getLogger().info("SANCTUARY rescue location="+player.getLocation()+" mode="+player.getGameMode());
            check(player.getWorld()==world && player.getLocation().distance(new Location(world,247.5,57,14.5))<.1,"rescate al Santuario");
            check(player.getHealth()>0 && player.getFallDistance()==0,"rescate sin muerte ni caida acumulada");
            player.teleport(new Location(Bukkit.getWorlds().getFirst(),0,100,0));
        }
        case "result" -> {
            check(mobs("astral_santuario_cofre").isEmpty() && mobs("astral_santuario_guia").isEmpty(),"reset al abandonar");
            getLogger().info("SANCTUARY RESULT checks="+checks+" failures="+failures);
        }
        }
      }catch(Exception ex){check(false,ex.toString());ex.printStackTrace();}
      return true;
    }
}
