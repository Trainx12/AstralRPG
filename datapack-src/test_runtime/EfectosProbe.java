package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.event.player.*;
import org.bukkit.event.block.Action;
import org.bukkit.persistence.PersistentDataType;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Ensayo aislado de orientacion y preferencias con dos espectadores NMS. */
public final class EfectosProbe extends JavaPlugin {
    int failures;
    void check(boolean ok, String text) { if (!ok) failures++; getLogger().info("FXCFG " + (ok ? "PASS " : "FAIL ") + text); }
    Player fake(String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes(name.getBytes()),name);
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

    Object call(Object plugin, String name, Object... args) throws Exception {
        for (var m : plugin.getClass().getDeclaredMethods()) if (m.getName().equals(name) && m.getParameterCount() == args.length) {
            m.setAccessible(true); return m.invoke(plugin, args);
        }
        throw new NoSuchMethodException(name);
    }
    java.util.List<org.bukkit.entity.ItemDisplay> sprites(World w) {
        return w.getEntitiesByClass(org.bukkit.entity.ItemDisplay.class).stream().filter(e -> e.getScoreboardTags().contains("astral.fx.sprite")).toList();
    }
    void clear(World w) { for (var e : sprites(w)) e.remove(); }
    // Evita la cola diferida de dispatchCommand dentro de otro comando en Paper 26.1.
    void comando(Player p, String args) { Bukkit.getPluginCommand("efectos").execute(p, "efectos", args.split(" ")); }
    int score(Player p, String obj) { return Bukkit.getScoreboardManager().getMainScoreboard().getObjective(obj).getScore(p.getName()).getScore(); }
    public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command cmd, String label, String[] args) {
        try {
            Player a = fake("FxProbeA"), b = fake("FxProbeB");
            b.teleport(a.getLocation().add(4,0,0));
            var plugin = Bukkit.getPluginManager().getPlugin("AstralEfectos");
            var world = a.getWorld();
            Bukkit.getScoreboardManager().getMainScoreboard().resetScores(a.getName());
            Bukkit.getScoreboardManager().getMainScoreboard().resetScores(b.getName());
            call(plugin, "leer", a); call(plugin, "leer", b);
            var categories = Class.forName("astral.AstralEfectos$Categoria", true, plugin.getClass().getClassLoader()).getEnumConstants();
            String[] keys = {"armaduras", "armas", "bastones", "mascotas", "jefes"};
            String[] objs = {"armadura", "armas", "bastones", "mascotas", "jefes"};
            comando(a,"alto"); comando(b,"alto");
            for (int i=0; i<keys.length; i++) {
                String key=keys[i], obj="astral.fx."+objs[i]; Object cat=categories[i];
                check(score(a,obj)==1 && score(b,obj)==1, key+" activo sin score previo");
                comando(a,key+" off");
                check(score(a,obj)==0 && score(b,obj)==1,key+" preferencia individual");
                Object f=call(plugin,"fx",cat,a.getLocation(),"estrella",Color.WHITE,1f,1f,20,2,2,true);
                check(f!=null,key+" creado para segundo espectador");
                var display=sprites(world).getLast();
                check(!a.canSee(display) && b.canSee(display),key+" oculto solo a A");
                comando(b,key+" off");
                check(!b.canSee(display),key+" oculta dibujo vivo al cambiar");
                check(call(plugin,"fx",cat,a.getLocation(),"estrella",Color.WHITE,1f,1f,20,2,2,true)==null,key+" no crea sin espectadores");
                comando(a,key); check(score(a,obj)==1,key+" alterna a true");
                comando(a,key+" on"); check(score(a,obj)==1,key+" on idempotente");
                comando(a,key+" invalido"); check(score(a,obj)==1,key+" argumento invalido conserva valor");
                call(plugin,"leer",a); check(score(a,obj)==1,key+" relee persistencia");
                comando(b,key+" on"); clear(world);
            }
            Location origin=a.getEyeLocation(); origin.setYaw(90); origin.setPitch(30);
            a.teleport(new Location(world,0,100,0,90,30));
            origin=a.getEyeLocation();
            var dir=origin.getDirection();
            var right=dir.clone().crossProduct(new org.bukkit.util.Vector(0,1,0)).normalize().multiply(.36);
            var mouth=origin.clone().add(dir.clone().multiply(.9)).add(right).add(0,-.28,0);
            var end=origin.clone().add(dir.clone().multiply(25));
            call(plugin,"disparo",categories[2],mouth,end,Color.WHITE,"arcano",a);
            var beam=sprites(world).stream().filter(e->e.getItemStack().getItemMeta().getItemModel().getKey().equals("fx/rayo")).findFirst().orElseThrow();
            var actual=beam.getTransformation().getLeftRotation().transform(new org.joml.Vector3f(0,0,1));
            var expected=end.toVector().subtract(mouth.toVector()).normalize();
            check(beam.getLocation().getYaw()==0 && beam.getLocation().getPitch()==0,"entidad yaw y pitch cero con emisor yaw90 pitch30");
            check(actual.distance(new org.joml.Vector3f((float)expected.getX(),(float)expected.getY(),(float)expected.getZ()))<1e-5,"rotacion +Z coincide con direccion boca a mira");
            clear(world);
            // Raytrace real contra un blanco en el aire, sin un cliente conectado.
            var target=world.spawn(origin.clone().add(dir.clone().multiply(8)),org.bukkit.entity.Zombie.class);
            target.setAI(false); target.setGravity(false);
            call(plugin,"rayoDeBaston",origin.clone().add(dir.clone().multiply(.8)),Color.WHITE,"arcano");
            check(sprites(world).stream().anyMatch(e->e.getItemStack().getItemMeta().getItemModel().getKey().equals("fx/rayo") && e.getTransformation().getScale().z<15),"raytrace desde ojos impacta blanco antes de 25 bloques");
            target.remove(); clear(world);
            comando(a,"bajo"); comando(b,"bajo");
            check(call(plugin,"fx",categories[2],mouth,"estrella",Color.WHITE,1f,1f,20,1,2,true)==null,"Bajo no crea dibujos");
            getLogger().info("FXCFG RESULT failures="+failures);
        } catch(Throwable ex) { failures++; getLogger().log(java.util.logging.Level.SEVERE,"FXCFG FAIL exception",ex); }
        return true;
    }
}
