package astraltest;

import java.util.*;
import java.io.*;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.entity.*;
import org.bukkit.event.block.*;
import org.bukkit.inventory.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.event.block.Action;
import org.bukkit.plugin.java.JavaPlugin;

/** Ensayo local del Oceano Astral (genera, mide aire, prueba reglas, dibuja el fondo). Nunca va al server. */
public final class OceanoProbe extends JavaPlugin {
    int failures;
    void check(boolean ok, String s) { if (!ok) failures++; getLogger().info("OCE " + (ok ? "PASS " : "FAIL ") + s); }

    @Override public void onEnable() {
        Bukkit.getScheduler().runTaskLater(this, this::run, 40);
    }

    void run() {
        int radius = Integer.getInteger("oceano.radio", 96);
        World w = Bukkit.createWorld(new WorldCreator("oceano").generator("AstralOceano"));
        check(w != null, "mundo creado con el generador AstralOceano");
        int chunks = radius / 16;
        long t0 = System.currentTimeMillis();
        List<Chunk> loaded = new ArrayList<>();
        for (int cx = -chunks; cx < chunks; cx++) for (int cz = -chunks; cz < chunks; cz++) { Chunk c = w.getChunkAt(cx, cz); c.load(true); loaded.add(c); }
        getLogger().info("OCE generados " + loaded.size() + " chunks en " + (System.currentTimeMillis() - t0) + " ms");
        // Dejar que se pueblen (decoraciones) y medir despues.
        Bukkit.getScheduler().runTaskLater(this, () -> measure(w, radius), 200);
    }

    void measure(World w, int radius) {
        int air = 0, water = 0, inner = Math.min(radius - 24, 104); Map<String, Integer> where = new TreeMap<>();
        java.awt.image.BufferedImage img = new java.awt.image.BufferedImage(inner * 2, inner * 2, java.awt.image.BufferedImage.TYPE_INT_RGB);
        java.awt.image.BufferedImage side = new java.awt.image.BufferedImage(inner * 2, 190, java.awt.image.BufferedImage.TYPE_INT_RGB);
        Map<Material, Integer> floorMat = new HashMap<>();
        for (int x = -inner; x < inner; x++) for (int z = -inner; z < inner; z++) {
            int floor = -999;
            for (int y = w.getMinHeight() + 1; y <= 109; y++) {
                Material m = w.getBlockAt(x, y, z).getType();
                if (m == Material.AIR || m == Material.CAVE_AIR) { air++; where.merge(x / 32 + "," + y / 16 + "," + z / 32, 1, Integer::sum); }
                else if (m == Material.WATER) water++;
                else if (m != Material.KELP && m != Material.KELP_PLANT && m != Material.SEAGRASS && m != Material.TALL_SEAGRASS) floor = y;
            }
            Material top = floor > -999 ? w.getBlockAt(x, floor, z).getType() : Material.WATER;
            floorMat.merge(top, 1, Integer::sum);
            int g = Math.max(0, Math.min(255, (floor + 30) * 3));
            int rgb = top.name().contains("CORAL") ? 0xff6688 : top == Material.SAND ? (g << 16 | g << 8 | (g / 2)) : top == Material.GRAVEL ? (g << 16 | g << 8 | g) : (g / 3 << 16 | g / 2 << 8 | g);
            img.setRGB(x + inner, z + inner, rgb);
            if (z == 0) for (int y = -64; y < 126; y++) {
                Material m = w.getBlockAt(x, y, 0).getType();
                int c = m == Material.WATER ? 0x1a4a8a : (m == Material.AIR || m == Material.CAVE_AIR) ? 0xff0000 : m == Material.BEDROCK ? 0x222222 : 0x998877;
                side.setRGB(x + inner, 125 - y, c);
            }
        }
        check(air == 0, "sin aire debajo del techo: " + air + " bloques de aire (zonas " + where.keySet().stream().limit(8).toList() + ")");
        getLogger().info("OCE agua=" + water + " fondo=" + floorMat.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(8).toList());
        try { javax.imageio.ImageIO.write(img, "png", new File("oceano-fondo.png")); javax.imageio.ImageIO.write(side, "png", new File("oceano-corte.png")); } catch (IOException e) { getLogger().warning("" + e); }
        Location spawn = w.getSpawnLocation();
        check(spawn.getBlock().getType() == Material.WATER, "el punto de llegada es agua: " + spawn.getBlock().getType() + " en " + spawn.toVector());
        check(w.getBlockAt(5, 116, 5).getType() == Material.BEDROCK, "techo de bedrock en y=116");
        rules(w);
        tandaB(w, inner);
        // Regeneracion: guardar plantilla, romper el techo de llegada y regenerar.
        Location probe = new Location(w, 8, 115, 8);
        Material before = probe.getBlock().getType();
        probe.getBlock().setType(Material.GOLD_BLOCK);
        w.save();
        Bukkit.getScheduler().runTaskLater(this, () -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "oceano regenerar"), 80);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            World nw = Bukkit.getWorld("oceano");
            check(nw != null && nw != w, "el mundo se volvio a cargar despues de regenerar");
            if (nw != null) check(nw.getBlockAt(8, 115, 8).getType() == before, "la regeneracion devolvio el bloque original: " + nw.getBlockAt(8, 115, 8).getType());
            getLogger().info("OCE RESULT failures=" + failures); Bukkit.shutdown();
        }, 260);
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
        fp.setPos(0.5, 40, 0.5); lvl.addNewPlayer(fp); var list = server.getPlayerList(); list.players.add(fp);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var f = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); f.setAccessible(true);
            ((Map) f.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fp);
        }
        var ch = (io.netty.channel.embedded.EmbeddedChannel) connection.channel;
        Bukkit.getScheduler().runTaskTimer(this, () -> ch.releaseOutbound(), 1, 1);
        Bukkit.getScheduler().runTaskTimer(this, () -> { try { fp.doTick(); } catch (Throwable ignored) {} }, 1, 1);
        Player p = fp.getBukkitEntity(); p.setGameMode(GameMode.SURVIVAL); return p;
    }

    ItemStack astral(Player p, String id) {
        // Directo de la tabla del datapack (el jugador falso no recibe bien "loot give").
        var table = Bukkit.getLootTable(NamespacedKey.fromString("astral:item/" + id));
        var ctx = new org.bukkit.loot.LootContext.Builder(p.getLocation()).build();
        var items = table.populateLoot(new Random(1), ctx);
        return items.isEmpty() ? null : items.iterator().next();
    }

    void tandaB(World w, int inner) {
        int perla = 0, coral = 0, chests = 0, withLoot = 0;
        for (int x = -inner; x < inner; x++) for (int z = -inner; z < inner; z++) for (int y = -60; y < 60; y++) {
            Block b = w.getBlockAt(x, y, z);
            if (b.getType() == Material.NOTE_BLOCK && b.getBlockData() instanceof org.bukkit.block.data.type.NoteBlock n) {
                if (n.getNote().getId() == 22) perla++; else if (n.getNote().getId() == 23) coral++;
            } else if (b.getType() == Material.CHEST) { chests++; if (b.getState() instanceof org.bukkit.loot.Lootable l && l.getLootTable() != null) withLoot++; }
        }
        check(perla > 50 && coral > 20, "menas generadas: perla=" + perla + " coral=" + coral);
        check(chests > 3 && withLoot == chests, "cofres al azar con botin: " + withLoot + "/" + chests);
        try {
            Player p = fake(w, "Buzo2");
            Block ore = null;
            outer: for (int x = -40; x < 40; x++) for (int z = -40; z < 40; z++) for (int y = -40; y < 50; y++) {
                Block b = w.getBlockAt(x, y, z);
                if (b.getType() == Material.NOTE_BLOCK) { ore = b; break outer; }
            }
            ItemStack pick = astral(p, "agua_pico");
            p.getInventory().setItemInMainHand(pick);
            var ev = new BlockBreakEvent(ore, p); Bukkit.getPluginManager().callEvent(ev);
            check(ev.isCancelled(), "sin taladro no se mina la mena (con el pico de agua)");
            ItemStack drill = astral(p, "taladro_amatista");
            p.getInventory().setItemInMainHand(drill);
            var ev2 = new BlockBreakEvent(ore, p); Bukkit.getPluginManager().callEvent(ev2);
            check(!ev2.isCancelled(), "con taladro de amatista se mina la mena");
            ItemStack low = astral(p, "taladro_mitril");
            p.getInventory().setItemInMainHand(low);
            var ev3 = new BlockBreakEvent(ore, p); Bukkit.getPluginManager().callEvent(ev3);
            check(ev3.isCancelled(), "con taladro de mitril (tier 2) no se mina");
            Block o = ore;
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "execute in minecraft:oceano run loot spawn " + o.getX() + " 100 " + o.getZ()
                + " mine " + o.getX() + " " + o.getY() + " " + o.getZ() + " minecraft:netherite_pickaxe");
            Bukkit.getScheduler().runTaskLater(this, () -> {
                var drops = w.getNearbyEntities(new Location(w, o.getX(), 100, o.getZ()), 3, 3, 3).stream()
                    .filter(e -> e instanceof Item).map(e -> ((Item) e).getItemStack()).toList();
                check(drops.stream().anyMatch(d -> d.getType() == Material.PRISMARINE_CRYSTALS || d.getType() == Material.PRISMARINE_SHARD),
                      "la mena suelta su material: " + drops);
            }, 5);
            ItemStack[] armor = new ItemStack[4];
            String[] pieces = {"agua_boots", "agua_leggings", "agua_chestplate", "agua_helmet"};
            for (int i = 0; i < 4; i++) armor[i] = astral(p, pieces[i]);
            p.getInventory().clear(); p.getInventory().setArmorContents(armor);
            p.teleport(new Location(w, 0.5, 60, 0.5)); p.setRemainingAir(0);
            Player fp = p;
            Bukkit.getScheduler().runTaskLater(this, () -> {
                check(fp.getRemainingAir() >= fp.getMaximumAir() - 15, "set completo: respira sin limite (aire " + fp.getRemainingAir() + "/" + fp.getMaximumAir() + ")");
                check(fp.hasPotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION), "casco de agua: vision nocturna bajo el agua");
                double nado = fp.getAttribute(Attribute.WATER_MOVEMENT_EFFICIENCY).getValue();
                check(nado >= 0.99, "nado con 4 piezas: " + nado);
                ItemStack bow = astral(fp, "agua_arco");
                fp.getInventory().setItemInMainHand(bow);
                var click = new org.bukkit.event.player.PlayerInteractEvent(fp, Action.RIGHT_CLICK_AIR, bow, null, BlockFace.SELF, EquipmentSlot.HAND);
                Bukkit.getPluginManager().callEvent(click);
                long chorros = w.getEntitiesByClass(Trident.class).stream().filter(t -> t.getScoreboardTags().contains("astral.chorro")).count();
                check(chorros == 1 && !fp.getInventory().contains(Material.ARROW), "el arco de agua dispara un chorro sin flechas: " + chorros);
            }, 30);
        } catch (Throwable t) { check(false, "tanda B: " + t); t.printStackTrace(); }
    }

    void rules(World w) {
        // Reglas: se simulan los eventos de colocar y romper con un jugador falso de Bukkit.
        Block target = null;
        for (int y = 108; y > 0 && target == null; y--) if (w.getBlockAt(3, y, 3).getType() == Material.WATER && w.getBlockAt(3, y - 1, 3).getType().isSolid()) target = w.getBlockAt(3, y, 3);
        Player p = null;
        try {
            var server = ((org.bukkit.craftbukkit.CraftServer) Bukkit.getServer()).getServer();
            var lvl = ((org.bukkit.craftbukkit.CraftWorld) w).getHandle();
            var profile = new com.mojang.authlib.GameProfile(UUID.randomUUID(), "Buzo");
            p = new net.minecraft.server.level.ServerPlayer(server, lvl, profile, net.minecraft.server.level.ClientInformation.createDefault()).getBukkitEntity();
            p.setGameMode(GameMode.SURVIVAL);
        } catch (Throwable t) { check(false, "jugador falso: " + t); return; }
        for (Material m : List.of(Material.OAK_DOOR, Material.OAK_SIGN, Material.TORCH, Material.SPONGE, Material.CONDUIT, Material.STONE, Material.OAK_SLAB, Material.OAK_TRAPDOOR)) {
            BlockState before = target.getState();
            target.setType(m, false);
            var ev = new BlockPlaceEvent(target, before, target.getRelative(BlockFace.DOWN), new ItemStack(m), p, true, EquipmentSlot.HAND);
            Bukkit.getPluginManager().callEvent(ev);
            boolean allowed = m == Material.STONE || m == Material.OAK_SLAB;
            check(ev.isCancelled() != allowed, (allowed ? "se puede poner " : "no se puede poner ") + m);
            before.update(true, false);
        }
        var bucket = new org.bukkit.event.player.PlayerBucketFillEvent(p, target, target, BlockFace.UP, Material.BUCKET, new ItemStack(Material.BUCKET), EquipmentSlot.HAND);
        Bukkit.getPluginManager().callEvent(bucket);
        check(bucket.isCancelled(), "no se puede llenar un balde");
        Block stone = target.getRelative(BlockFace.DOWN);
        var br = new BlockBreakEvent(stone, p);
        Bukkit.getPluginManager().callEvent(br);
        stone.setType(Material.AIR, false);
        Block s2 = stone;
        Bukkit.getScheduler().runTaskLater(this, () -> check(s2.getType() == Material.WATER, "al romper queda agua: " + s2.getType()), 2);
    }
}
