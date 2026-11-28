package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.*;
import com.mojang.authlib.GameProfile;

/** Local only: real kills, skill rewards, XP orbs and two slime generations. */
public final class SpawnerXpProbe extends JavaPlugin implements Listener {
    Player player;
    int failures, checks;
    final Map<UUID, Integer> expected = new HashMap<>();
    final List<Slime> children = new ArrayList<>();
    boolean splitting;

    void check(boolean ok, String message) {
        checks++;
        if (!ok) failures++;
        getLogger().info("SPAWNERXP " + (ok ? "PASS " : "FAIL ") + message);
    }

    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getCommand("spawnerxpprobe").setExecutor((sender, cmd, label, args) -> {
            try {
                if (args[0].equals("player")) createPlayer();
                if (args[0].equals("run")) run();
            } catch (Throwable ex) { failures++; ex.printStackTrace(); }
            return true;
        });
    }

    void createPlayer() throws Exception {
        var server = ((CraftServer) Bukkit.getServer()).getServer();
        var world = ((CraftWorld) Bukkit.getWorlds().getFirst()).getHandle();
        var profile = new GameProfile(UUID.fromString("173b8ccf-b657-4093-bc4c-7c8527d0a502"), "TandaProbe");
        var fake = new ServerPlayer(server, world, profile, ClientInformation.createDefault());
        var connection = new Connection(PacketFlow.SERVERBOUND);
        connection.channel = new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler", connection);
        connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        fake.connection = new ServerGamePacketListenerImpl(server, connection, fake, CommonListenerCookie.createInitial(profile, false));
        fake.setPos(0, -59, 0);
        world.addNewPlayer(fake);
        var list = server.getPlayerList();
        list.players.add(fake);
        for (String name : List.of("playersByUUID", "playersByName")) {
            var field = net.minecraft.server.players.PlayerList.class.getDeclaredField(name);
            field.setAccessible(true);
            ((Map) field.get(list)).put(name.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fake);
        }
        player = fake.getBukkitEntity();
        player.setOp(true); player.setGameMode(GameMode.SURVIVAL); player.setInvulnerable(true);
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(player, net.kyori.adventure.text.Component.empty()));
        AuraSkillsApi.get().getUserManager().loadUser(player.getUniqueId());
        io.lumine.mythic.bukkit.MythicBukkit.inst().getPlayerManager().loadProfile(player);
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void prepare(EntityDeathEvent e) {
        if (expected.containsKey(e.getEntity().getUniqueId())) e.setDroppedExp(7);
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void death(EntityDeathEvent e) {
        Integer xp = expected.remove(e.getEntity().getUniqueId());
        if (xp != null) check(e.getDroppedExp() == xp, "death XP=" + e.getDroppedExp() + " expected=" + xp + " origin=" + e.getEntity().getEntitySpawnReason());
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void split(EntityTransformEvent e) {
        if (splitting && e.getTransformReason() == EntityTransformEvent.TransformReason.SPLIT)
            for (Entity child : e.getTransformedEntities()) children.add((Slime) child);
    }

    void run() {
        var world = player.getWorld();
        world.setDifficulty(Difficulty.NORMAL);
        // The NMS test player has no real client sending chunk subscriptions.
        for (int x = -1; x <= 1; x++) for (int z = -1; z <= 1; z++)
            world.getChunkAt(x, z).setForceLoaded(true);
        var user = AuraSkillsApi.get().getUser(player.getUniqueId());
        user.setSkillLevel(Skills.FIGHTING, 16);
        player.getInventory().clear();
        player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.IRON_SWORD));
        var reasons = List.of(CreatureSpawnEvent.SpawnReason.SPAWNER, CreatureSpawnEvent.SpawnReason.TRIAL_SPAWNER,
                CreatureSpawnEvent.SpawnReason.NATURAL, CreatureSpawnEvent.SpawnReason.CUSTOM,
                CreatureSpawnEvent.SpawnReason.SPAWNER_EGG, CreatureSpawnEvent.SpawnReason.BREEDING);
        killCase(reasons, 0);
    }

    void killCase(List<CreatureSpawnEvent.SpawnReason> reasons, int index) {
        if (index == reasons.size()) { splitCase(); return; }
        var reason = reasons.get(index);
        var world = player.getWorld();
        for (Entity e : world.getEntitiesByClass(ExperienceOrb.class)) e.remove();
        Zombie mob = world.spawn(player.getLocation().add(8, 0, 0), Zombie.class, reason);
        mob.setAI(false); mob.addScoreboardTag("astral.mt2");
        int xp = index < 2 ? 0 : 7;
        expected.put(mob.getUniqueId(), xp);
        double before = AuraSkillsApi.get().getUser(player.getUniqueId()).getSkillXp(Skills.FIGHTING);
        mob.damage(100000, player);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            double gain = AuraSkillsApi.get().getUser(player.getUniqueId()).getSkillXp(Skills.FIGHTING) - before;
            check(gain > 0, reason + " skill XP=" + gain);
            int orbs = world.getEntitiesByClass(ExperienceOrb.class).stream().mapToInt(ExperienceOrb::getExperience).sum();
            check(orbs == xp, reason + " real orbs=" + orbs);
            killCase(reasons, index + 1);
        }, 30); // Vanilla spawns XP orbs after the death animation (20 ticks).
    }

    void splitCase() {
        splitting = true;
        Slime parent = player.getWorld().spawn(player.getLocation().add(12, 0, 0), Slime.class, CreatureSpawnEvent.SpawnReason.SPAWNER);
        parent.setSize(4); parent.setAI(false);
        expected.put(parent.getUniqueId(), 0); parent.setHealth(0);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            List<Slime> first = List.copyOf(children); children.clear();
            check(!first.isEmpty(), "real first split");
            for (Slime child : first) { expected.put(child.getUniqueId(), 0); child.setHealth(0); }
            Bukkit.getScheduler().runTaskLater(this, () -> {
                List<Slime> second = List.copyOf(children); children.clear();
                check(!second.isEmpty(), "real second split");
                for (Slime child : second) { expected.put(child.getUniqueId(), 0); child.setHealth(0); }
                getLogger().info("SPAWNERXP RESULT failures=" + failures + " checks=" + checks);
            }, 30);
        }, 30);
    }
}
