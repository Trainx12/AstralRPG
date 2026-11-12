package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Ensayo local de la Mazmorra Infinita (Skript + datapack). Nunca va al server. */
public final class InfinitaProbe extends JavaPlugin {
    final Map<String, Player> p = new LinkedHashMap<>(); int failures;
    static final String FLAT = "{\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:the_void\"}";
    World world(String name) {
        var w = Bukkit.getWorld(name);
        return w != null ? w : Bukkit.createWorld(new WorldCreator(name).type(WorldType.FLAT).generatorSettings(FLAT).generateStructures(false));
    }
    @Override public void onEnable() {
        for (String w : List.of("lobby", "infinita", "infinita_2", "infinita_3", "infinita_4", "infinita_5", "infinita_6")) world(w);
        world("lobby").getBlockAt(0, 99, 0).setType(Material.STONE);
    }
    void check(boolean ok, String s) { if (!ok) failures++; getLogger().info("INF " + (ok ? "PASS " : "FAIL ") + s); }
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
        var player = fake.getBukkitEntity(); player.setGameMode(GameMode.SURVIVAL);
        // Invulnerable haria que los mobs no lo apunten: Resistencia maxima en su lugar.
        player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE, -1, 255, false, false)); return player;
    }
    void click(Player pl, int slot) {
        var view = pl.getOpenInventory();
        Bukkit.getPluginManager().callEvent(new InventoryClickEvent(view, InventoryType.SlotType.CONTAINER, slot, ClickType.LEFT, InventoryAction.PICKUP_ALL));
    }
    List<Entity> mobs(String w) {
        var out = new ArrayList<Entity>();
        for (var e : world(w).getEntities()) if (e.getScoreboardTags().contains("inf.mob")) out.add(e);
        return out;
    }
    String where(String n) { return p.get(n).getWorld().getName(); }
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command cmd, String label, String[] args) {
      try {
        if (cmd.getName().equals("spawn")) { var t = Bukkit.getPlayerExact(args[0]); if (t != null) t.teleport(new Location(world("lobby"), 0.5, 100, 0.5)); return true; }
        switch (args[0]) {
        case "setup" -> { for (String n : List.of("A", "B", "C")) p.put(n, fake("Inf" + n));
            p.get("A").performCommand("party invitar InfB"); p.get("B").performCommand("party aceptar"); }
        // Las ventanas son de DeluxeMenus (no esta en el ensayo): sus clics ejecutan infelegir por consola.
        case "tierA" -> { p.get("A").performCommand("infinita"); }
        case "pickA" -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "infelegir InfA tier 5");
        case "velA" -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "infelegir InfA vel 4");
        case "tierC" -> { p.get("C").performCommand("infinita"); }
        case "pickC" -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "infelegir InfC tier 1");
        case "velC" -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "infelegir InfC vel 1");
        case "inside" -> {
            check(where("A").equals("infinita") && where("B").equals("infinita"), "party A+B en la sala 1: " + where("A") + "/" + where("B"));
            check(where("C").equals("infinita_2"), "C solo en la sala 2: " + where("C"));
        }
        case "mobs" -> {
            var m1 = mobs("infinita"); var m2 = mobs("infinita_2");
            check(m1.size() >= 4, "sala 1 (Pesadilla, 2 jugadores) con mobs: " + m1.size());
            check(m2.size() >= 1 && m2.size() < m1.size(), "sala 2 (Facil, 1 jugador) con menos mobs: " + m2.size());
            check(m1.stream().allMatch(e -> e.getScoreboardTags().contains("astral.mt5")), "sala 1 todos tier V");
            check(m2.stream().allMatch(e -> e.getScoreboardTags().contains("astral.mt1")), "sala 2 todos tier I");
            check(m2.stream().allMatch(e -> e.getCustomName() != null && e.getCustomName().contains("[T1]")), "el cartel de la sala 2 dice [T1]: " + m2.stream().map(Entity::getCustomName).toList());
            var hp = m1.stream().filter(e -> e instanceof LivingEntity).mapToDouble(e -> ((LivingEntity) e).getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue()).max().orElse(0);
            check(hp > 10000, "vida tier V aplicada: " + hp);
            var types = new HashSet<String>(); for (var e : m1) types.add(e.getType().name());
            getLogger().info("INF tipos sala 1: " + types);
            var sin = m1.stream().filter(e -> e instanceof Mob && e.getTicksLived() > 40 && ((Mob) e).getTarget() == null).map(e -> e.getType().name()).toList();
            check(sin.isEmpty(), "todos (con mas de 2 s) tienen a un jugador como objetivo; sin objetivo: " + sin);
        }
        case "raise" -> {
            var m2 = mobs("infinita_2");
            check(m2.stream().anyMatch(e -> e.getScoreboardTags().contains("astral.mt2")), "sala 2 subio a tier II tras el tiempo");
        }
        case "boom" -> {
            var w = world("infinita");
            var floor = w.getBlockAt(5, 62, 5).getType();
            var cr = (Creeper) w.spawnEntity(new Location(w, 5.5, 63, 5.5), EntityType.CREEPER);
            cr.addScoreboardTag("inf.mob"); cr.setPowered(true); cr.setExplosionRadius(6);
            var z = (Zombie) w.spawnEntity(new Location(w, 7.5, 63, 5.5), EntityType.ZOMBIE); z.addScoreboardTag("inf.mob");
            double before = z.getHealth();
            cr.explode();
            Bukkit.getScheduler().runTaskLater(this, () -> {
                check(floor != Material.AIR && w.getBlockAt(5, 62, 5).getType() == floor, "la explosion no rompe el piso: " + w.getBlockAt(5, 62, 5).getType());
                check(z.isDead() || z.getHealth() >= before, "la explosion no lastima a otros mobs");
            }, 5);
        }
        case "leave" -> { for (String n : List.of("A", "B")) p.get(n).teleport(new Location(world("lobby"), 0.5, 100, 0.5)); }
        case "clean" -> check(mobs("infinita").isEmpty(), "sala 1 vacia se limpia: " + mobs("infinita").size());
        case "result" -> getLogger().info("INF RESULT failures=" + failures);
        }
      } catch (Throwable ex) { failures++; getLogger().warning("INF FAIL " + ex); ex.printStackTrace(); }
      return true;
    }
}
