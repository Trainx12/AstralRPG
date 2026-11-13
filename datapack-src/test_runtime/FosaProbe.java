package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.potion.*;

/** Ensayo local de la Fosa del Crustaceo (entrada, respiracion, oleadas, jefe, fin). Nunca va al server. */
public final class FosaProbe extends JavaPlugin {
    int failures; Player a; World oceano, fosa;
    void check(boolean ok, String s) { if (!ok) failures++; getLogger().info("FOSA " + (ok ? "PASS " : "FAIL ") + s); }

    // La copia tiene que estar vacia hace 15 s (mazmorras_copias.LIBRE_TRAS) antes de recibir jugadores.
    @Override public void onEnable() {
        Bukkit.getScheduler().runTaskLater(this, () -> {
            oceano = Bukkit.createWorld(new WorldCreator("oceano").generator("AstralOceano"));
            fosa = Bukkit.createWorld(new WorldCreator("fosa").generator("AstralOceano:vacio"));
            for (int cx = -4; cx <= 3; cx++) for (int cz = 2; cz <= 9; cz++) fosa.setChunkForceLoaded(cx, cz, true);
        }, 40);
        Bukkit.getScheduler().runTaskLater(this, this::start, 600);
    }

    Player fake(World w, String name) throws Exception {
        var server = ((org.bukkit.craftbukkit.CraftServer) Bukkit.getServer()).getServer();
        var lvl = ((org.bukkit.craftbukkit.CraftWorld) w).getHandle();
        var profile = new com.mojang.authlib.GameProfile(UUID.randomUUID(), name);
        var fp = new net.minecraft.server.level.ServerPlayer(server, lvl, profile, net.minecraft.server.level.ClientInformation.createDefault());
        var connection = new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND);
        connection.channel = new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler", connection);
        connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        fp.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(server, connection, fp,
            net.minecraft.server.network.CommonListenerCookie.createInitial(profile, false));
        fp.setPos(0.5, 60, 0.5); lvl.addNewPlayer(fp); var list = server.getPlayerList(); list.players.add(fp);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var f = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); f.setAccessible(true);
            ((Map) f.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fp);
        }
        var ch = (io.netty.channel.embedded.EmbeddedChannel) connection.channel;
        Bukkit.getScheduler().runTaskTimer(this, () -> { ch.releaseOutbound(); try { fp.doTick(); } catch (Throwable ignored) {} }, 1, 1);
        Player p = fp.getBukkitEntity(); p.setGameMode(GameMode.SURVIVAL);
        p.addPotionEffect(new PotionEffect(PotionEffectType.RESISTANCE, -1, 255, false, false));
        return p;
    }

    ItemStack astral(Player p, String id) {
        var table = Bukkit.getLootTable(NamespacedKey.fromString("astral:item/" + id));
        var items = table.populateLoot(new Random(1), new org.bukkit.loot.LootContext.Builder(p.getLocation()).build());
        return items.isEmpty() ? null : items.iterator().next();
    }

    void later(int ticks, Runnable r) { Bukkit.getScheduler().runTaskLater(this, () -> { try { r.run(); } catch (Throwable t) { check(false, "" + t); t.printStackTrace(); } }, ticks); }

    void start() {
        try {
            check(fosa.getBlockAt(4, 112, 93).getType() == Material.WATER, "arena de la Fosa cargada (agua en la llegada)");
            // Entrada escondida en el oceano.
            Chunk gc = oceano.getChunkAt(-430 >> 4, 470 >> 4); gc.load(true);
            int top = 109; while (top > -60 && oceano.getBlockAt(-430, top, 470).getType() != Material.CRYING_OBSIDIAN) top--;
            check(oceano.getBlockAt(-430, top, 470).getType() == Material.CRYING_OBSIDIAN, "entrada escondida en -430,470: " + oceano.getBlockAt(-430, top, 470).getType());
            a = fake(oceano, "Buzo");
            Location from = new Location(oceano, -428.5, top + 1, 467.5), to = new Location(oceano, -429.5, top + 1, 470.5);
            a.teleport(to);
            Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerMoveEvent(a, from, to));
            later(20, () -> {
                check(a.getWorld().getName().equals("fosa"), "la grieta lleva a la Fosa: " + a.getWorld().getName());
                if (!a.getWorld().getName().equals("fosa")) {
                    getLogger().info("FOSA debug: mundos " + Bukkit.getWorlds().stream().map(World::getName).toList() + " | jugador en " + a.getLocation());
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mazentrar Buzo fosa");
                }
            });
            later(40, () -> {
                getLogger().info("FOSA debug: tras mazentrar directo el jugador esta en " + a.getWorld().getName());
                // Sin set: con pocion de respiracion igual se ahoga.
                a.addPotionEffect(new PotionEffect(PotionEffectType.WATER_BREATHING, 6000, 0));
                a.setRemainingAir(300);
                later(40, () -> {
                    check(!a.hasPotionEffect(PotionEffectType.WATER_BREATHING), "en la Fosa se anula la pocion de respiracion");
                    check(a.getRemainingAir() < 260, "sin set completo pierde aire: " + a.getRemainingAir());
                    ItemStack[] armor = new ItemStack[4]; String[] ids = {"agua_boots", "agua_leggings", "agua_chestplate", "agua_helmet"};
                    for (int i = 0; i < 4; i++) armor[i] = astral(a, ids[i]);
                    a.getInventory().setArmorContents(armor);
                    a.setRemainingAir(100);
                    later(40, () -> {
                        check(a.getRemainingAir() >= a.getMaximumAir() - 15, "con el set completo respira: " + a.getRemainingAir());
                        waves(1);
                    });
                });
            });
        } catch (Throwable t) { check(false, "inicio: " + t); t.printStackTrace(); finish(); }
    }

    void waves(int n) {
        later(n == 1 ? 60 : 120, () -> {
            List<Entity> mobs = new ArrayList<>();
            for (Entity e : fosa.getEntities()) if (e.getScoreboardTags().contains("fosa.mob") || e.getScoreboardTags().contains("fosa.jefe")) mobs.add(e);
            Map<String, Integer> types = new TreeMap<>();
            for (Entity e : mobs) types.merge(e.getType().name() + (e.getScoreboardTags().contains("fosa.jefe") ? "(jefe)" : ""), 1, Integer::sum);
            check(!mobs.isEmpty(), "oleada " + n + ": " + types);
            if (n == 1) {
                boolean tier3 = mobs.stream().filter(e -> e instanceof Monster).allMatch(e -> e.getScoreboardTags().contains("astral.mt3"));
                check(tier3, "los mobs de la Fosa son tier 3");
            }
            if (n == 4) {
                check(mobs.stream().anyMatch(e -> e.getScoreboardTags().contains("fosa.jefe")), "aparece el Cangrejo de la Fosa");
                mobs.forEach(Entity::remove);
                later(60, () -> { getLogger().info("FOSA fin de la mazmorra (mazfin enviado si arriba sale 'Ganaron')"); finish(); });
                return;
            }
            mobs.forEach(Entity::remove);
            waves(n + 1);
        });
    }

    void finish() { later(20, () -> { getLogger().info("FOSA RESULT failures=" + failures); Bukkit.shutdown(); }); }
}
