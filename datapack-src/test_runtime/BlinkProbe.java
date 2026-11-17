package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.event.*;
import org.bukkit.event.player.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.*;
import net.minecraft.network.protocol.game.*;
import com.mojang.authlib.GameProfile;

/** Solo ensayo local: captura en el listener NMS, sin cliente visual. */
public final class BlinkProbe extends JavaPlugin implements Listener {
    Player player; World expectedWorld; Location origin; int failures; boolean cancel; int charges,refunds;
    final List<Packet<?>> packets=new ArrayList<>();
    void check(boolean ok,String msg){if(!ok)failures++;getLogger().info("BLINK "+(ok?"PASS ":"FAIL ")+msg);}
    Player fake(World w) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)w).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),"BlinkProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false)) {
            @Override public void send(Packet<?> packet){packets.add(packet);}
            @Override public void send(Packet<?> packet,io.netty.channel.ChannelFutureListener listener){packets.add(packet);}
        };
        w.getChunkAt(0,0).setForceLoaded(true);fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }
    public void onEnable(){
        Bukkit.getPluginManager().registerEvents(this,this);
        // Doble de mana: verifica exactamente los comandos del Skript; no simula economia real.
        Bukkit.getCommandMap().register("auraskills",new org.bukkit.command.Command("mana") {
            public boolean execute(org.bukkit.command.CommandSender s,String label,String[] a){
                if(a.length>=3 && a[0].equals("remove") && a[2].equals("50"))charges++;
                if(a.length>=3 && a[0].equals("add") && a[2].equals("50"))refunds++;
                return true;
            }
        });
    }
    @EventHandler public void teleport(PlayerTeleportEvent e){if(cancel)e.setCancelled(true);}
    void cmd(String c){Bukkit.dispatchCommand(Bukkit.getConsoleSender(),c);}
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String l,String[] args){
      try {
        if(args[0].equals("start")) {
            World w=args[1].equals("lobby")?new WorldCreator(NamespacedKey.minecraft("lobby")).type(WorldType.FLAT)
                .generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}")
                .generateStructures(false).createWorld():Bukkit.getWorlds().getFirst();
            expectedWorld=w;
            player=fake(w);player.setRotation(-90,0);packets.clear();
            origin=player.getLocation();
            cmd("execute as BlinkProbe at @s run minecraft:tp @s ~12 ~0 ~0");
        } else if(args[0].equals("skill")) {
            getLogger().info("BLINK BASELINE "+expectedWorld.getName()+" respawn="+packets.stream().filter(p->p instanceof ClientboundRespawnPacket).count());
            check(player.getWorld().equals(expectedWorld),"vanilla mismo mundo "+expectedWorld.getName());
            check(Math.abs(player.getLocation().getX()-12)<0.02,"vanilla distancia 12");
            player.teleport(origin);packets.clear();charges=0;refunds=0;
            cmd("blinkskill BlinkProbe");
        } else if(args[0].equals("moved")) {
            check(Math.abs(player.getLocation().getX()-12)<0.02,"Destello distancia 12: "+player.getLocation());
            check(player.getWorld().equals(expectedWorld),"mundo conservado");
            check(player.getYaw()==-90 && player.getPitch()==0,"rotacion conservada");
            check(packets.stream().noneMatch(p->p instanceof ClientboundRespawnPacket),"sin RESPAWN");
            check(packets.stream().anyMatch(p->p instanceof ClientboundPlayerPositionPacket),"paquete de posicion registrado");
            check(charges==1 && refunds==0,"un debito de 50, sin devolucion");
            Location before=player.getLocation();packets.clear();
            cmd("astraldecor:astralblink "+player.getUniqueId()+" NaN 0 0");
            cmd("astraldecor:astralblink "+player.getUniqueId()+" 14 0 0");
            check(player.getLocation().distance(before)<0.01,"rechaza NaN y salto mayor de 13");
            player.setVelocity(new org.bukkit.util.Vector(0.2,0.1,0.3));
            cmd("astraldecor:astralblink "+player.getUniqueId()+" 0 0 0");
            check(player.getVelocity().distance(new org.bukkit.util.Vector(0.2,0.1,0.3))<0.0001,"conserva velocidad XYZ");
            player.setVelocity(new org.bukkit.util.Vector());
            Bukkit.dispatchCommand(player,"astraldecor:astralblink "+player.getUniqueId()+" 1 0 0");
            check(player.getLocation().distance(before)<0.01,"rechaza comando desde jugador");
            cancel=true;cmd("blinkskill BlinkProbe");
        } else if(args[0].equals("cancelled")) {
            check(Math.abs(player.getLocation().getX()-12)<0.02,"cancelacion conserva posicion");
            check(charges==2 && refunds==1,"cancelacion devuelve 50 una vez");
            check(packets.stream().noneMatch(p->p instanceof ClientboundRespawnPacket),"cancelacion sin RESPAWN");
            cancel=false;player.kick();
        } else if(args[0].equals("result"))getLogger().info("BLINK RESULT failures="+failures);
      }catch(Exception ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"BLINK FAIL",ex);}
      return true;
    }
}
