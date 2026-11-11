package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import io.lumine.mythic.bukkit.MythicBukkit;
import io.lumine.mythic.api.skills.placeholders.PlaceholderString;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.CraftServer;
import org.bukkit.craftbukkit.CraftWorld;
import com.mojang.authlib.GameProfile;

/** Jugador simulado exclusivamente local; nunca se instala en produccion. */
public final class UrgenteProbe extends JavaPlugin {
    Player player;
    int failures;
    void move(Location destination) {
        var from=player.getLocation();
        player.teleport(destination);
        // Un cliente real informa movimiento tras confirmar el teletransporte.
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerMoveEvent(player,from,destination));
    }
    void check(boolean ok,String detail) {
        if(!ok)failures++;
        getLogger().info("URGENTE "+(ok?"PASS ":"FAIL ")+detail);
    }
    void petCheck(String pid,String stage,boolean expected) {
        var pets=MythicBukkit.inst().getMobManager().getActiveMobs().stream().filter(m ->
            m.getType().getInternalName().equals("astral_pet_"+pid) && !m.getEntity().isDead()).toList();
        boolean ok=expected?pets.size()==1:pets.isEmpty();
        if(expected && pets.size()==1) {
            var pet=pets.getFirst();var e=pet.getEntity().getBukkitEntity();
            ok &= pet.getOwnerUUID().isPresent() && pet.getOwnerUUID().get().equals(player.getUniqueId())
                && e.getWorld().equals(player.getWorld())
                && e.getLocation().distance(player.getLocation())<(stage.equals("invocar")?8:25);
        }
        check(ok,"pet="+pid+" stage="+stage+" count="+pets.size()+" player="+player.getLocation()+" pets="+
            pets.stream().map(p -> p.getEntity().getBukkitEntity().getLocation().toString()).toList());
    }
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        try {
            var api=MythicBukkit.inst().getAPIHelper();
            if(args[0].equals("player")) {
                var server=((CraftServer)Bukkit.getServer()).getServer();
                var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
                var other=Bukkit.createWorld(new WorldCreator("urgente_mascotas").type(WorldType.FLAT).generateStructures(false));
                for(var bw:List.of(world.getWorld(),other)) {
                    bw.getChunkAt(0,0).setForceLoaded(true);bw.getChunkAt(1,0).setForceLoaded(true);
                    for(int x=-32;x<=64;x++)for(int z=-32;z<=32;z++) {
                        bw.getBlockAt(x,-61,z).setType(Material.STONE);
                        for(int y=-60;y<=-56;y++)bw.getBlockAt(x,y,z).setType(Material.AIR);
                    }
                }
                var profile=new GameProfile(UUID.randomUUID(),"AstralProbe");
                var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
                var connection=new Connection(PacketFlow.SERVERBOUND);
                connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
                connection.channel.pipeline().addLast("packet_handler",connection);
                connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
                fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
                fake.setPos(0,-60,0);
                world.addNewPlayer(fake);
                var list=server.getPlayerList();
                list.players.add(fake);
                for(String name:List.of("playersByUUID","playersByName")) {
                    var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(name);field.setAccessible(true);
                    ((Map)field.get(list)).put(name.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
                }
                player=fake.getBukkitEntity();player.setOp(true);
                player.setInvulnerable(true);
                MythicBukkit.inst().getPlayerManager().loadProfile(player);
                kr.toxicity.model.api.BetterModel.platform().playerManager().player(
                    kr.toxicity.model.api.bukkit.platform.BukkitAdapter.adapt(player));
                player.teleport(new Location(Bukkit.getWorlds().getFirst(),0,-60,0));
                getLogger().info("URGENTE player online="+player.isOnline()+" lookup="+(Bukkit.getPlayer("AstralProbe")!=null));
            } else if(args[0].equals("vars")) {
                api.castSkill(player,"URGENTE_VARIABLE",meta -> {
                    Bukkit.getScheduler().runTaskLater(this,()-> {
                        for(String s:List.of("<global.pet_owner>","<global.var.pet_owner>"))
                            getLogger().info("URGENTE placeholder "+s+" = ["+PlaceholderString.of(s).get(meta)+"]");
                    },1);
                });
            } else if(args[0].equals("pet")) {
                String pid=args[1];int n=Integer.parseInt(args[2]);
                player.addAttachment(this,"astral.mascota."+pid,true);
                var board=Bukkit.getScoreboardManager().getMainScoreboard();
                for(String obj:List.of("mascota","petsel","petkills","pxp_"+pid,"plv_"+pid,"pmod_"+pid))
                    if(board.getObjective(obj)==null)board.registerNewObjective(obj,"dummy");
                board.getObjective("petkills").getScore("#nivel").setScore(25);
                board.getObjective("pxp_"+pid).getScore(player.getName()).setScore(0);
                board.getObjective("mascota").getScore(player.getName()).setScore(n);
                board.getObjective("plv_"+pid).getScore(player.getName()).setScore(1);
                var control=api.spawnMythicMob("astral_mascotas_control",new Location(Bukkit.getWorlds().getFirst(),30,-60,0));
                getLogger().info("URGENTE permission="+player.hasPermission("astral.mascota."+pid)+" dead="+player.isDead()+" valid="+player.isValid()+" name="+player.getName()+" request="+board.getObjective("mascota").getScore(player.getName()).getScore());
                getLogger().info("URGENTE cast="+api.castSkill(control,"MASC_INVOCAR_"+pid,player,control.getLocation(),List.of(player),List.of(),1,meta -> {
                    meta.setIsAsync(false);
                    var skill=MythicBukkit.inst().getSkillManager().getSkill("MASC_INVOCAR_"+pid).get();
                    getLogger().info("URGENTE usable="+skill.isUsable(meta,io.lumine.mythic.core.skills.SkillTriggers.API)+" caster="+meta.getCaster().getEntity().getName()+" targets="+meta.getEntityTargets());
                }));
                for(int tick:List.of(30,100)) Bukkit.getScheduler().runTaskLater(this,()-> {
                    int found=0;
                    for(var m:MythicBukkit.inst().getMobManager().getActiveMobs())
                        if(m.getType().getInternalName().equals("astral_pet_"+pid)) {
                            found++;getLogger().info("URGENTE pet="+pid+" owner="+m.getOwnerUUID()+" alive="+!m.getEntity().isDead()+" loc="+m.getEntity().getBukkitEntity().getLocation());
                        }
                    getLogger().info("URGENTE pet="+pid+" tick="+tick+" found="+found+" selected="+board.getObjective("petsel").getScore(player.getName()).getScore());
                },tick);
                Bukkit.getScheduler().runTaskLater(this,()->petCheck(pid,"invocar",true),100);
                Bukkit.getScheduler().runTaskLater(this,()->move(player.getLocation().add(30,0,0)),105);
                Bukkit.getScheduler().runTaskLater(this,()->petCheck(pid,"seguir",true),150);
                Bukkit.getScheduler().runTaskLater(this,()->move(new Location(
                    player.getWorld().equals(Bukkit.getWorlds().getFirst())?Bukkit.getWorld("urgente_mascotas"):Bukkit.getWorlds().getFirst(),0,-60,0)),155);
                Bukkit.getScheduler().runTaskLater(this,()->petCheck(pid,"mundo",true),210);
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    board.getObjective("mascota").getScore(player.getName()).setScore(98);
                    api.castSkill(control,"MASC_GUARDAR",player,control.getLocation(),List.of(player),List.of(),1);
                },215);
                Bukkit.getScheduler().runTaskLater(this,()-> {petCheck(pid,"guardar",false);control.remove();},250);
            } else if(args[0].equals("progress")) {
                var w=Bukkit.createWorld(new WorldCreator("mina").type(WorldType.FLAT).generateStructures(false));
                w.getChunkAt(0,0).setForceLoaded(true);w.getChunkAt(1,0).setForceLoaded(true);
                var c=w.spawn(new Location(w,0,-60,0),ArmorStand.class);c.setGravity(false);c.setCustomName("Control Campamento Minero");c.addScoreboardTag("mina.on");
                var c2=w.spawn(new Location(w,30,-60,0),ArmorStand.class);c2.setGravity(false);c2.setCustomName("Control Lago Subterraneo");c2.addScoreboardTag("mina.on");
                var board=Bukkit.getScoreboardManager().getMainScoreboard();
                for(var e:List.of(c,c2)) {
                    board.getObjective("ad.wave").getScore(e.getUniqueId().toString()).setScore(2);
                    board.getObjective("ad.max").getScore(e.getUniqueId().toString()).setScore(4);
                }
                var e=w.spawn(new Location(w,2,-60,0),Pig.class);e.setAI(false);e.setGravity(false);e.addScoreboardTag("ad.mina.sala1");
                String storage="astral:tanda2/mina/sala1";
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"data modify storage "+storage+" queue set value [{fn:'astral:test'},{fn:'astral:test'}]");
                move(new Location(w,0,-60,0));
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"function astral:tanda2/ui_tick");
                var bar=Bukkit.getBossBar(NamespacedKey.fromString("astral:tanda2/mina/sala1"));
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    check(board.getObjective("ad.room").getScore(player.getName()).getScore()==1,"progress room1");
                    check(board.getObjective("ad.left").getScore(player.getName()).getScore()==3,"progress pending plus alive");
                    check(bar!=null && bar.getPlayers().contains(player) && Math.abs(bar.getProgress()-.75)<.001,"progress bar 3/4");
                    e.remove();
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"function astral:tanda2/ui_tick");
                },2);
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    check(Math.abs(bar.getProgress()-.5)<.001,"progress bar decreases 2/4");
                    move(new Location(w,30,-60,0));
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"function astral:tanda2/ui_tick");
                },4);
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    check(board.getObjective("ad.room").getScore(player.getName()).getScore()==2 && !bar.getPlayers().contains(player),"progress room isolation");
                    move(new Location(Bukkit.getWorlds().getFirst(),0,-60,0));
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"function astral:tanda2/ui_tick");
                },6);
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    check(board.getObjective("ad.room").getScore(player.getName()).getScore()==0 && !bar.getPlayers().contains(player),"progress leaves world");
                    c.remove();c2.remove();
                },8);
            } else if(args[0].equals("death")) {
                String mid=args[1];
                Bukkit.getWorlds().getFirst().getChunkAt(6,6).setForceLoaded(true);
                move(new Location(Bukkit.getWorlds().getFirst(),100,-60,85));
                var e=(LivingEntity)api.spawnMythicMob(mid,new Location(Bukkit.getWorlds().getFirst(),100,-60,100));
                e.setAI(false);
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    var registry=kr.toxicity.model.api.tracker.EntityTrackerRegistry.registry(e.getUniqueId());
                    if(registry==null) {check(false,"death="+mid+" no tracker");return;}
                    registry.spawn(kr.toxicity.model.api.bukkit.platform.BukkitAdapter.adapt(player));
                    var tracker=registry.first();
                    String[] firstPose={null};
                    e.setHealth(0);
                    for(int tick:List.of(1,8,15,24))Bukkit.getScheduler().runTaskLater(this,()-> {
                        check(tick<16?!tracker.isClosed():tracker.isClosed(),"death="+mid+" tick="+tick+" closed="+tracker.isClosed()+" removal="+tracker.forRemoval());
                        if(!tracker.isClosed())try {
                            // BetterModel manda transformaciones por paquete; los datos
                            // Bukkit del display no contienen esa pose por jugador.
                            String pose=tracker.bone("death_root").worldRotation(player.getUniqueId()).toString();
                            if(tick==1)firstPose[0]=pose;
                            if(tick==8)check(!pose.equals(firstPose[0]),"death="+mid+" displays move players="+tracker.playerCount());
                            getLogger().info("URGENTE death="+mid+" tick="+tick+" pose="+pose);
                        } catch(Exception ex) {check(false,"death sample "+ex);}
                    },tick);
                },20);
            } else if(args[0].equals("result")) {
                getLogger().info("URGENTE RESULT failures="+failures);
            }
        } catch(Exception e) {e.printStackTrace();}
        return true;
    }
}
