package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.command.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.util.Vector;
import io.lumine.mythic.bukkit.MythicBukkit;
import kr.toxicity.model.api.BetterModel;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.*;
import com.mojang.authlib.GameProfile;

/** Solo ensayo Paper local; no instalar en el servidor del dueno. */
public final class DungeonFixProbe extends JavaPlugin implements Listener {
    int failures,checks; Player player; LivingEntity mob; int hits;
    void check(boolean ok,String text){checks++;if(!ok)failures++;getLogger().info("DUNGEON "+(ok?"PASS ":"FAIL ")+text);}
    void cmd(String text){Bukkit.dispatchCommand(Bukkit.getConsoleSender(),text);}
    void later(long tick,Runnable action){Bukkit.getScheduler().runTaskLater(this,()->{try{action.run();}catch(Throwable e){check(false,e.toString());e.printStackTrace();}},tick);}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void damage(EntityDamageByEntityEvent e){if(e.getEntity()==mob && e.getFinalDamage()>0)hits++;}
    Player fake(World w) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();var world=((CraftWorld)w).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),"DungeonProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);
        var ch=(io.netty.channel.embedded.EmbeddedChannel)connection.channel;
        Bukkit.getScheduler().runTaskTimer(this,()->ch.releaseOutbound(),1,1);
        return p;
    }
    @Override public void onEnable(){Bukkit.getPluginManager().registerEvents(this,this);}
    public boolean onCommand(CommandSender sender,Command command,String label,String[] args){
        try {
            if(args[0].equals("setup")) {
                var world=Bukkit.getWorlds().getFirst();player=fake(world);
                for(int x=-48;x<=48;x++)for(int z=-32;z<=32;z++)world.getBlockAt(x,99,z).setType(Material.STONE);
                world.getChunkAt(0,0).setForceLoaded(true);
            } else if(args[0].equals("model"))model(args[1]);
            else if(args[0].equals("ice"))ice();
            else if(args[0].equals("reset"))reset();
            else if(args[0].equals("result"))getLogger().info("DUNGEON RESULT checks="+checks+" failures="+failures);
        }catch(Throwable e){check(false,e.toString());e.printStackTrace();}
        return true;
    }
    void model(String mid){
        if(mob!=null)mob.remove();player.teleport(new Location(player.getWorld(),-40,105,0));
        mob=(LivingEntity)MythicBukkit.inst().getAPIHelper().spawnMythicMob(mid,new Location(player.getWorld(),0,100,0));
        mob.setGravity(false);var speed=mob.getAttribute(org.bukkit.attribute.Attribute.MOVEMENT_SPEED);if(speed!=null)speed.setBaseValue(0);
        later(15,()->{
            var registry=BetterModel.registryOrNull(mob.getUniqueId());
            var bone=registry==null?null:registry.first().bone("b_astral_hitbox");
            var physical=bone==null||bone.getHitBox()==null?null:Bukkit.getEntity(bone.getHitBox().uuid());
            check(physical!=null,mid+" caja fisica completa");if(physical==null)return;
            getLogger().info("DUNGEON BOX "+mid+" "+physical.getType()+" "+physical.getBoundingBox());
            for(int i=0;i<3;i++) {
                final int part=i;
                later(15+i*22,()->{
                    var box=physical.getBoundingBox();double y=box.getMinY()+box.getHeight()*(part==0?.12:part==1?.5:.88);
                    var start=new Location(mob.getWorld(),box.getMinX()-2,y,box.getCenterZ());
                    hits=0;mob.setNoDamageTicks(0);
                    var arrow=mob.getWorld().spawnArrow(start,new Vector(1,0,0),3,0);arrow.setShooter(player);arrow.setGravity(false);
                    later(8,()->check(hits>0,mid+" flecha zona="+part));
                    var eyes=start.clone().add(-3,-player.getEyeHeight(),0);eyes.setDirection(new Vector(1,0,0));player.teleport(eyes);
                    player.addScoreboardTag("astral.caster");
                    mob.getWorld().spawn(player.getEyeLocation(),Marker.class,m->m.addScoreboardTag("astral.spell.trace")).remove();
                    check(mob.getScoreboardTags().contains("astral.spell.model"),mid+" baston zona="+part);
                    player.removeScoreboardTag("astral.caster");
                });
            }
            later(85,()->{
                var box=physical.getBoundingBox();hits=0;mob.setNoDamageTicks(0);
                var trident=mob.getWorld().spawn(new Location(mob.getWorld(),box.getMinX()-2,box.getCenterY(),box.getCenterZ()),Trident.class);
                trident.setShooter(player);trident.setGravity(false);trident.setVelocity(new Vector(3,0,0));
                later(8,()->check(hits>0,mid+" tridente"));
            });
            later(105,()->{hits=0;mob.setNoDamageTicks(0);player.attack(physical);check(hits>0,mid+" cuerpo a cuerpo");});
        });
    }
    void ice(){
        var world=player.getWorld();for(int x=15;x<=21;x++)for(int z=15;z<=21;z++){world.getBlockAt(x,99,z).setType(Material.WATER);world.getBlockAt(x,100,z).setType(Material.AIR);}
        world.getBlockAt(18,99,18).setType(Material.STONE);
        cmd("execute positioned 18 100 18 run function astral:boss/chaman_ice");
        check(world.getBlockAt(19,99,18).getType()==Material.FROSTED_ICE,"agua superficial congela");
        check(world.getBlockAt(18,99,18).getType()==Material.STONE,"piso solido conservado");
        world.getBlockAt(19,99,18).setType(Material.FROSTED_ICE);world.getBlockAt(19,100,18).setType(Material.STONE);
        cmd("execute positioned 18 100 18 run function astral:boss/chaman_ice");
        check(world.getBlockAt(19,100,18).getType()==Material.STONE,"no altera bloques superiores");
    }
    void reset(){
        var world=player.getWorld();var a=world.spawn(new Location(world,30,100,0),ArmorStand.class);a.setCustomName("Control Claro de las raices");a.setGravity(false);
        var b=world.spawn(new Location(world,35,100,0),ArmorStand.class);b.setCustomName("Control Altar del Chaman");b.setGravity(false);
        for(var c:List.of(a,b))for(String t:List.of("bosque.on","bosque.ola2","bosque.fin","bosque.espera","bosque.jefe.derrotado"))c.addScoreboardTag(t);
        var old=world.spawn(new Location(world,33,100,0),Zombie.class);old.addScoreboardTag("ad.bosque.sala1");
        cmd("function astral:tanda2/bosque/fresh");
        later(2,()->{
            check(!old.isValid(),"restos de expedicion eliminados");
            check(a.getScoreboardTags().contains("bosque.ready")&&!a.getScoreboardTags().contains("bosque.ola2"),"entrada reinicia sala1");
            check(!b.getScoreboardTags().contains("bosque.ready")&&!b.getScoreboardTags().contains("bosque.on"),"sala2 bloqueada al entrar");
            a.remove();b.remove();
        });
    }
}
