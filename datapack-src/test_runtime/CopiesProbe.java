package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Ensayo local de las copias de mazmorra (Skript): party, copia libre, ocupada y salida por tiempo. */
public final class CopiesProbe extends JavaPlugin {
    final Map<String, Player> p = new LinkedHashMap<>(); int failures;
    static final String FLAT = "{\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:the_void\"}";
    World world(String name) {
        var w = Bukkit.getWorld(name);
        return w != null ? w : Bukkit.createWorld(new WorldCreator(name).type(WorldType.FLAT).generatorSettings(FLAT).generateStructures(false));
    }
    @Override public void onEnable() {
        for (String w : List.of("lobby", "mina", "mina_2", "mina_3", "mina_4", "mina_5", "mina_6")) {
            var world = world(w);
            for (int x = 5; x <= 15; x++) for (int z = -130; z <= -119; z++) world.getBlockAt(x, -46, z).setType(Material.STONE);
            world.getBlockAt(0, 99, 0).setType(Material.STONE);
        }
    }
    void check(boolean ok, String s) { if (!ok) failures++; getLogger().info("COPIES " + (ok ? "PASS " : "FAIL ") + s); }
    Player fake(String name) throws Exception {
        var server = ((CraftServer) Bukkit.getServer()).getServer(); var w = ((CraftWorld) world("lobby")).getHandle();
        var profile = new GameProfile(UUID.randomUUID(), name); var fake = new ServerPlayer(server, w, profile, ClientInformation.createDefault());
        var connection = new Connection(PacketFlow.SERVERBOUND); connection.channel = new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler", connection); connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        fake.connection = new ServerGamePacketListenerImpl(server, connection, fake, CommonListenerCookie.createInitial(profile, false));
        fake.setPos(0.5, 100, 0.5); w.addNewPlayer(fake); var list = server.getPlayerList(); list.players.add(fake);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var f = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); f.setAccessible(true);
            ((Map) f.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fake);
        }
        var ch = (io.netty.channel.embedded.EmbeddedChannel) connection.channel;
        Bukkit.getScheduler().runTaskTimer(this, () -> ch.releaseOutbound(), 1, 1);
        var player = fake.getBukkitEntity(); player.setGameMode(GameMode.SURVIVAL); return player;
    }
    String where(String n) { return p.get(n).getWorld().getName(); }
    void console(String c) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), c); }
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command cmd, String label, String[] args) {
      try {
        if (cmd.getName().equals("spawn")) {  // reemplazo local de Essentials /spawn
            var t = Bukkit.getPlayerExact(args[0]); if (t != null) t.teleport(new Location(world("lobby"), 0.5, 100, 0.5)); return true;
        }
        switch (args[0]) {
        case "setup" -> { for (String n : List.of("A", "B", "C", "D", "E", "F", "G", "H")) p.put(n, fake("Jug" + n)); }
        case "party" -> { p.get("A").performCommand("party invitar JugB"); p.get("B").performCommand("party aceptar"); }
        case "enter" -> { for (String n : args[1].split(",")) console("mazentrar Jug" + n + " mina"); }
        case "check1" -> {
            check(where("A").equals("mina") && where("B").equals("mina"), "party A+B juntos en la copia 1: " + where("A") + "/" + where("B"));
            check(where("C").equals("mina_2"), "C solo en la copia 2: " + where("C"));
            check(where("G").equals("mina_6"), "G en la copia 6: " + where("G"));
            check(where("H").equals("lobby"), "H sin copia libre queda en el lobby (ocupada): " + where("H"));
            var l = p.get("A").getLocation();
            check(Math.abs(l.getX() - 10.5) < 0.01 && Math.abs(l.getZ() + 124.5) < 0.01, "llega al punto de la sala 1: " + l);
        }
        case "fin" -> console("mazfin mina");
        case "check2" -> {
            check(where("A").equals("lobby") && where("B").equals("lobby"), "pasado el tiempo tras el jefe vuelven al spawn: " + where("A") + "/" + where("B"));
            check(where("C").equals("mina_2"), "las otras copias siguen jugando: " + where("C"));
        }
        case "check3" -> check(where("H").equals("mina"), "copia 1 libre otra vez: H entra ahi: " + where("H"));
        case "result" -> getLogger().info("COPIES RESULT failures=" + failures);
        }
      } catch (Throwable ex) { failures++; getLogger().warning("COPIES FAIL " + ex); ex.printStackTrace(); }
      return true;
    }
}
