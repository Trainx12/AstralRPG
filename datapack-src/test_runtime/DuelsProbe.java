package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Ensayo local de Duels + ventana /desafiar con dos jugadores NMS. Nunca va al server. */
public final class DuelsProbe extends JavaPlugin {
    Player a, b; int failures;
    static final String FLAT = "{\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:the_void\"}";
    // Duels lee arenas y lobby al habilitarse: los mundos tienen que existir antes (loadbefore).
    @Override public void onEnable() { for (String w : List.of("lobby", "arena", "arenas_tft")) world(w); }
    void check(boolean ok, String s) { if (!ok) failures++; getLogger().info("DUELS " + (ok ? "PASS " : "FAIL ") + s); }
    World world(String name) {
        var w = Bukkit.getWorld(name);
        return w != null ? w : Bukkit.createWorld(new WorldCreator(name).type(WorldType.FLAT).generatorSettings(FLAT).generateStructures(false));
    }
    void floor(World w, int cx, int y, int cz, int r) {
        for (int x = cx - r; x <= cx + r; x++) for (int z = cz - r; z <= cz + r; z++) w.getBlockAt(x, y, z).setType(Material.STONE);
    }
    Player fake(String name) throws Exception {
        var server = ((CraftServer) Bukkit.getServer()).getServer(); var w = ((CraftWorld) world("lobby")).getHandle();
        var profile = new GameProfile(UUID.randomUUID(), name); var fake = new ServerPlayer(server, w, profile, ClientInformation.createDefault());
        var connection = new Connection(PacketFlow.SERVERBOUND); connection.channel = new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler", connection); connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        fake.connection = new ServerGamePacketListenerImpl(server, connection, fake, CommonListenerCookie.createInitial(profile, false));
        fake.setPos(180.5, 98, 190.5); w.addNewPlayer(fake); var list = server.getPlayerList(); list.players.add(fake);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var f = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); f.setAccessible(true);
            ((Map) f.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fake);
        }
        // Sin cliente, nadie lee los paquetes: vaciar cada tick para que no se trabe el server.
        var ch = (io.netty.channel.embedded.EmbeddedChannel) connection.channel;
        Bukkit.getScheduler().runTaskTimer(this, () -> ch.releaseOutbound(), 1, 1);
        var p = fake.getBukkitEntity(); p.setGameMode(GameMode.SURVIVAL);
        // Duels carga los datos del jugador al entrar.
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(p, net.kyori.adventure.text.Component.empty()));
        return p;
    }
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command cmd, String label, String[] args) {
      try {
        switch (args[0]) {
        case "setup" -> {
            floor(world("lobby"), 180, 97, 190, 6);
            floor(world("arena"), -206, 72, -2371, 14);
            var tft = world("arenas_tft");
            for (int z : new int[]{-551, -283, -15}) floor(tft, -287, z == -551 ? 142 : 138, z, 14);
            a = fake("RetadorA"); b = fake("RivalB");
            a.getInventory().addItem(new ItemStack(Material.DIAMOND, 5)); b.getInventory().addItem(new ItemStack(Material.EMERALD, 7));
            check(Bukkit.getPluginManager().isPluginEnabled("Duels"), "Duels habilitado");
        }
        case "gui" -> {
            a.performCommand("desafiar");
            Bukkit.getScheduler().runTaskLater(this, () -> {
                var view = a.getOpenInventory();
                var head = view.getTopInventory().getItem(0);
                check(view.getTitle().contains("Desafiar"), "ventana Desafiar abierta: " + view.getTitle());
                check(head != null && head.getType() == Material.PLAYER_HEAD && head.getItemMeta().getDisplayName().contains("RivalB"), "cabeza de RivalB en el slot 0");
                var click = new InventoryClickEvent(view, InventoryType.SlotType.CONTAINER, 0, ClickType.LEFT, InventoryAction.PICKUP_ALL);
                Bukkit.getPluginManager().callEvent(click);
                check(click.isCancelled(), "clic cancelado (no se lleva la cabeza)");
            }, 5);
        }
        case "request" -> {
            var view = a.getOpenInventory();
            check(view.getType() == InventoryType.CHEST && !view.getTitle().contains("Desafiar"), "Duels abrio su ventana de pedido: " + view.getTitle());
            a.closeInventory();
        }
        case "start" -> {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "duels start RetadorA RivalB own_inventory " + args[1]);
        }
        case "inarena" -> {
            check(a.getWorld().getName().equals(args[1]) && b.getWorld().getName().equals(args[1]), "ambos en " + args[1] + ": " + a.getLocation() + " / " + b.getLocation());
            check(a.getLocation().distance(b.getLocation()) > 10, "enfrentados a distancia " + a.getLocation().distance(b.getLocation()));
            b.setHealth(0);
        }
        case "after" -> {
            check(a.getWorld().getName().equals("lobby") , "ganador vuelve al lobby: " + a.getLocation());
            if (b.isDead()) b.spigot().respawn();
            check(a.getInventory().contains(Material.DIAMOND, 5), "ganador conserva sus items");
        }
        case "loser" -> {
            check(b.getInventory().contains(Material.EMERALD, 7), "perdedor conserva sus items");
            check(b.getWorld().getName().equals("lobby"), "perdedor vuelve al lobby: " + b.getLocation());
        }
        case "result" -> getLogger().info("DUELS RESULT failures=" + failures);
        }
      } catch (Throwable ex) { failures++; getLogger().warning("DUELS FAIL " + ex); ex.printStackTrace(); }
      return true;
    }
}
