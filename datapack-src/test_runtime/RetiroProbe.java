package astraltest;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.event.player.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
/** Solo ensayo local: Skript real con doble del comando crates y jugador NMS. */
public final class RetiroProbe extends JavaPlugin {
    Player player;int failures,keys;org.bukkit.entity.Entity retired;
    public void onEnable(){keys=getConfig().getInt("keys",0);}
    void check(boolean ok,String s){if(!ok)failures++;getLogger().info("RET "+(ok?"PASS ":"FAIL ")+s);}
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("AstralRetiroProbe".getBytes()),"RetiroProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        world.getWorld().getChunkAt(0,0).setForceLoaded(true);fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }

    void join(){Bukkit.getPluginManager().callEvent(new PlayerJoinEvent(player,net.kyori.adventure.text.Component.empty()));}
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args){
      if(command.getName().equals("crates")){
        check(Arrays.equals(args,new String[]{"give","virtual","gacha_monturas","1","RetiroProbe","-s"}),"llave virtual exacta");
        keys++;getConfig().set("keys",keys);saveConfig();return true;
      }
      try { switch(args[0]) {
        case "start" -> {
          player=fake();player.setOp(false);
          var a=player.addAttachment(this);
          for(String p:List.of("lobo","zorro","fenix"))a.setPermission("astral.mascota."+p,true);
          for(String p:List.of("cuervo","golem","dragon"))a.setPermission("astral.mascota."+p,false);
          var b=Bukkit.getScoreboardManager().getMainScoreboard();
          if(b.getObjective("petsel")==null)b.registerNewObjective("petsel",org.bukkit.scoreboard.Criteria.DUMMY,net.kyori.adventure.text.Component.text("petsel"));
          for(String name:List.of("mascota","pxp_fenix"))if(b.getObjective(name)==null)b.registerNewObjective(name,org.bukkit.scoreboard.Criteria.DUMMY,net.kyori.adventure.text.Component.text(name));
          b.getObjective("petsel").getScore("RetiroProbe").setScore(1);
          b.getObjective("pxp_fenix").getScore("RetiroProbe").setScore(17);
          retired=player.getWorld().spawnEntity(player.getLocation(),org.bukkit.entity.EntityType.PIG);retired.addScoreboardTag("astral.pet.lobo");
          join();
        }
        case "check" -> {
          check(keys==2,"dos mascotas retiradas producen dos llaves; Fenix no compensa");
          check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective("petsel").getScore("RetiroProbe").getScore()==0,"seleccion retirada limpiada");
          check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective("pxp_fenix").getScore("RetiroProbe").getScore()==17,"XP de Fenix intacta");
          check(player.hasPermission("astral.mascota.fenix"),"permiso Fenix intacto");
          check(!retired.isValid(),"mascota retirada despawneada");
          join();
        }
        case "again" -> check(keys==2,"reingreso no duplica compensacion (tambien tras reinicio)");
        case "all" -> {
          var a=player.addAttachment(this);for(String p:List.of("cuervo","golem","dragon"))a.setPermission("astral.mascota."+p,true);join();
        }
        case "five" -> check(keys==5,"cinco mascotas retiradas total cinco llaves");
        case "persist" -> {check(keys==5,"llaves persistidas por doble");player=fake();player.setOp(false);var a=player.addAttachment(this);for(String p:List.of("lobo","cuervo","golem","zorro","dragon","fenix"))a.setPermission("astral.mascota."+p,true);join();}
        case "noextra" -> check(keys==5,"reinicio mantiene migracion unica por UUID y mascota");
        case "result" -> getLogger().info("RET RESULT failures="+failures);
      }}catch(Throwable e){failures++;getLogger().log(java.util.logging.Level.SEVERE,"RET FAIL exception",e);}return true;
    }
}
