package astral;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.data.Waterlogged;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.event.world.ChunkPopulateEvent;
import org.bukkit.generator.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.noise.SimplexOctaveGenerator;

/**
 * Oceano Astral (generado por datapack-src/oceano.py).
 * - Generador "AstralOceano": todo agua entre el fondo y un techo de roca + bedrock (sin superficie).
 *   Usa biomas, decoraciones y estructuras vanilla del oceano (algas, corales, naufragios, ruinas).
 * - Sin aire: lo que queda de aire al poblar el chunk, al romper o al caer arena pasa a agua.
 *   No se pueden poner bloques que dejen respirar (puertas, carteles, esponjas, conductos...) ni usar baldes.
 * - Regeneracion cada N horas reales desde una copia limpia (plantilla) de las regiones.
 */
public final class AstralOceano extends JavaPlugin implements Listener {
    static final int FLOOR_BASE = 18, CEIL_WATER = 109, CEIL_TOP = 116;
    String world; long everyMs; List<Integer> warnMinutes;
    long nextRegen; boolean regenerating;

    @Override public void onEnable() {
        saveDefaultConfig();
        world = getConfig().getString("mundo", "oceano");
        everyMs = getConfig().getLong("regenerar-cada-horas", 72) * 3600_000L;
        warnMinutes = getConfig().getIntegerList("avisos-minutos");
        nextRegen = getConfig().getLong("proxima-regeneracion", 0);
        if (nextRegen == 0) { nextRegen = System.currentTimeMillis() + everyMs; save(); }
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::clock, 20 * 30, 20 * 30);
    }

    void save() { getConfig().set("proxima-regeneracion", nextRegen); saveConfig(); }

    @Override public ChunkGenerator getDefaultWorldGenerator(String worldName, String id) { return new Gen(); }

    // ----------------------------------------------------------------------------------- generador
    static final class Gen extends ChunkGenerator {
        SimplexOctaveGenerator hills, detail, caves;
        void init(long seed) {
            if (hills != null) return;
            hills = new SimplexOctaveGenerator(seed, 4); hills.setScale(1 / 160.0);
            detail = new SimplexOctaveGenerator(seed + 7, 3); detail.setScale(1 / 40.0);
            caves = new SimplexOctaveGenerator(seed + 13, 2); caves.setScale(1 / 28.0);
        }
        int floor(int x, int z) {
            double h = hills.noise(x, z, 0.5, 0.5, true), d = detail.noise(x, z, 0.5, 0.5, true);
            // Fosas profundas donde h es muy bajo; lomas y arrecifes donde es alto.
            double t = h < -0.45 ? (h + 0.45) * 70 : 0;
            return (int) Math.round(FLOOR_BASE + h * 22 + d * 5 + t);
        }
        @Override public void generateNoise(WorldInfo info, Random random, int cx, int cz, ChunkData data) {
            init(info.getSeed());
            int min = info.getMinHeight();
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
                int wx = cx * 16 + x, wz = cz * 16 + z, f = Math.max(min + 6, floor(wx, wz));
                data.setBlock(x, min, z, Material.BEDROCK);
                for (int y = min + 1; y <= f; y++) {
                    Material m = y < 0 ? Material.DEEPSLATE : Material.STONE;
                    // Cuevas inundadas debajo del fondo.
                    if (y < f - 3 && y > min + 4 && caves.noise(wx, y * 1.6, wz, 0.5, 0.5, true) > 0.55) m = Material.WATER;
                    data.setBlock(x, y, z, m);
                }
                for (int y = f + 1; y <= CEIL_WATER; y++) data.setBlock(x, y, z, Material.WATER);
                for (int y = CEIL_WATER + 1; y < CEIL_TOP; y++) data.setBlock(x, y, z, y == CEIL_WATER + 1 ? Material.DARK_PRISMARINE : Material.STONE);
                data.setBlock(x, CEIL_TOP, z, Material.BEDROCK);
            }
        }
        @Override public void generateSurface(WorldInfo info, Random random, int cx, int cz, ChunkData data) {
            init(info.getSeed());
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
                int f = floor(cx * 16 + x, cz * 16 + z);
                double d = detail.noise(cx * 16 + x, cz * 16 + z, 0.5, 0.5, true);
                Material top = d > 0.35 ? Material.GRAVEL : d < -0.4 ? Material.CLAY : Material.SAND;
                for (int y = f - 3; y <= f; y++) if (y > info.getMinHeight() + 1 && data.getType(x, y, z) != Material.WATER) data.setBlock(x, y, z, y == f ? top : Material.SAND);
            }
        }
        @Override public int getBaseHeight(WorldInfo info, Random random, int x, int z, HeightMap map) { init(info.getSeed()); return floor(x, z) + 1; }
        @Override public BiomeProvider getDefaultBiomeProvider(WorldInfo info) { return new Biomes(); }
        @Override public boolean shouldGenerateDecorations() { return true; }
        @Override public boolean shouldGenerateStructures() { return true; }
        @Override public boolean shouldGenerateMobs() { return true; }
        @Override public boolean shouldGenerateCaves() { return false; }
        @Override public Location getFixedSpawnLocation(World w, Random random) { init(w.getSeed()); return new Location(w, 0.5, floor(0, 0) + 2, 0.5); }
    }

    static final class Biomes extends BiomeProvider {
        static final List<Biome> LIST = List.of(Biome.WARM_OCEAN, Biome.LUKEWARM_OCEAN, Biome.DEEP_LUKEWARM_OCEAN, Biome.OCEAN, Biome.DEEP_OCEAN, Biome.COLD_OCEAN, Biome.DEEP_COLD_OCEAN);
        SimplexOctaveGenerator temp;
        @Override public Biome getBiome(WorldInfo info, int x, int y, int z) {
            if (temp == null) { temp = new SimplexOctaveGenerator(info.getSeed() + 31, 2); temp.setScale(1 / 600.0); }
            double t = temp.noise(x, z, 0.5, 0.5, true);
            int i = (int) Math.floor((t + 1) / 2 * LIST.size());
            return LIST.get(Math.max(0, Math.min(LIST.size() - 1, i)));
        }
        @Override public List<Biome> getBiomes(WorldInfo info) { return LIST; }
    }

    // ----------------------------------------------------------------------------------- sin aire
    boolean here(World w) { return w != null && w.getName().equals(world); }

    static boolean airy(Material m) { return m == Material.AIR || m == Material.CAVE_AIR; }

    void flood(Block b) {
        if (b.getY() > CEIL_WATER || b.getY() <= b.getWorld().getMinHeight()) return;
        if (airy(b.getType())) b.setType(Material.WATER, true);
        else if (b.getBlockData() instanceof Waterlogged wl && !wl.isWaterlogged()) { wl.setWaterlogged(true); b.setBlockData(wl, true); }
    }

    @EventHandler public void populate(ChunkPopulateEvent e) {
        if (!here(e.getWorld())) return;
        // Las decoraciones de un chunk (geodas, ruinas) pueden escribir en los vecinos ya limpios: se limpia el 3x3.
        World w = e.getWorld(); int cx = e.getChunk().getX(), cz = e.getChunk().getZ();
        Bukkit.getScheduler().runTask(this, () -> {
            for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++)
                if (w.isChunkLoaded(cx + dx, cz + dz)) sweep(w.getChunkAt(cx + dx, cz + dz));
        });
    }

    void sweep(Chunk c) {
        int min = c.getWorld().getMinHeight() + 1;
        for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) for (int y = min; y <= CEIL_WATER; y++) {
            Block b = c.getBlock(x, y, z);
            if (airy(b.getType())) b.setType(Material.WATER, false);
        }
    }

    static final Set<Material> BANNED = EnumSet.of(Material.SPONGE, Material.WET_SPONGE, Material.CONDUIT, Material.SOUL_SAND,
            Material.MAGMA_BLOCK, Material.PISTON, Material.STICKY_PISTON, Material.TNT, Material.ICE, Material.PACKED_ICE,
            Material.BLUE_ICE, Material.FROSTED_ICE, Material.SNOW, Material.SNOW_BLOCK, Material.POWDER_SNOW, Material.LAVA,
            Material.FIRE, Material.SOUL_FIRE, Material.SCAFFOLDING, Material.SLIME_BLOCK, Material.HONEY_BLOCK);

    void deny(Player p, String what) { if (!p.isOnline()) return; p.sendActionBar(net.kyori.adventure.text.Component.text("Oceano Astral: " + what, net.kyori.adventure.text.format.NamedTextColor.RED)); }

    boolean builder(Player p) { return p.getGameMode() == GameMode.CREATIVE && p.hasPermission("astral.oceano.editar"); }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void place(BlockPlaceEvent e) {
        if (!here(e.getBlock().getWorld()) || builder(e.getPlayer())) return;
        Material m = e.getBlockPlaced().getType();
        BlockData d = e.getBlockPlaced().getBlockData();
        // Solo bloques enteros (no dejan huecos de aire) o los que quedan inundados (losas, escaleras).
        String n = m.name();
        // Pedido del dueno: nada de puertas, trampillas, carteles, camas, antorchas, faroles, velas ni fogatas.
        boolean named = n.contains("SIGN") || n.contains("DOOR") || n.contains("BED") || n.contains("TORCH")
                || n.contains("LANTERN") || n.contains("CANDLE") || n.contains("CAMPFIRE") || n.contains("FENCE_GATE");
        boolean ok = !BANNED.contains(m) && !named && (m.isOccluding() || d instanceof Waterlogged);
        if (!ok) { e.setCancelled(true); deny(e.getPlayer(), "eso dejaria aire. Aca no se puede poner."); return; }
        if (d instanceof Waterlogged wl) { wl.setWaterlogged(true); e.getBlockPlaced().setBlockData(wl, false); }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true) public void broke(BlockBreakEvent e) {
        if (!here(e.getBlock().getWorld())) return;
        Block b = e.getBlock();
        Bukkit.getScheduler().runTask(this, () -> flood(b));
    }

    @EventHandler(ignoreCancelled = true) public void bucket(PlayerBucketEmptyEvent e) { if (here(e.getBlock().getWorld()) && !builder(e.getPlayer())) { e.setCancelled(true); deny(e.getPlayer(), "no se pueden usar baldes."); } }
    @EventHandler(ignoreCancelled = true) public void bucket(PlayerBucketFillEvent e) { if (here(e.getBlock().getWorld()) && !builder(e.getPlayer())) { e.setCancelled(true); deny(e.getPlayer(), "no se pueden usar baldes."); } }

    @EventHandler(ignoreCancelled = true) public void sponge(SpongeAbsorbEvent e) { if (here(e.getBlock().getWorld())) e.setCancelled(true); }

    @EventHandler(ignoreCancelled = true) public void vehicles(EntityPlaceEvent e) {
        if (here(e.getBlock().getWorld()) && (e.getEntity() instanceof Boat || e.getEntity() instanceof Minecart)) {
            e.setCancelled(true); if (e.getPlayer() != null) deny(e.getPlayer(), "no se pueden usar botes ni vagonetas.");
        }
    }

    @EventHandler(ignoreCancelled = true) public void falling(EntityChangeBlockEvent e) {
        if (!here(e.getBlock().getWorld()) || !(e.getEntity() instanceof FallingBlock)) return;
        Block b = e.getBlock();
        Bukkit.getScheduler().runTask(this, () -> flood(b));
    }

    @EventHandler(ignoreCancelled = true) public void explode(EntityExplodeEvent e) { if (here(e.getLocation().getWorld())) e.blockList().clear(); }
    @EventHandler(ignoreCancelled = true) public void explode(BlockExplodeEvent e) { if (here(e.getBlock().getWorld())) e.blockList().clear(); }
    @EventHandler(ignoreCancelled = true) public void fade(BlockFadeEvent e) { if (here(e.getBlock().getWorld())) { Block b = e.getBlock(); Bukkit.getScheduler().runTask(this, () -> flood(b)); } }

    // ----------------------------------------------------------------------------------- regeneracion
    void clock() {
        if (regenerating) return;
        long left = nextRegen - System.currentTimeMillis();
        for (int m : warnMinutes) {
            long at = m * 60_000L;
            if (left <= at && left > at - 30_000L) broadcast("&bEl Oceano Astral se regenera en &f" + m + (m == 1 ? " minuto" : " minutos") + "&b.");
        }
        if (left <= 0) regenerate(null);
    }

    void broadcast(String s) { Bukkit.broadcast(net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer.legacyAmpersand().deserialize(s)); }

    void broadcastTo(Player p, String s) { p.sendMessage(net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer.legacyAmpersand().deserialize(s)); }

    Path dir(World w) { return w.getWorldFolder().toPath(); }

    boolean regenerate(CommandSender who) {
        World w = Bukkit.getWorld(world);
        Path template = getDataFolder().toPath().resolve("plantilla");
        // Sin plantilla: se borran las regiones y el generador (misma semilla) las vuelve a crear iguales,
        // con menas, cofres y estructuras nuevas. Con plantilla (/oceano plantilla) se copia esa.
        if (w == null) { if (who != null) who.sendMessage("El mundo " + world + " no esta cargado."); return false; }
        regenerating = true;
        Path folder = dir(w);
        for (Player p : w.getPlayers()) Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "spawn " + p.getName());
        broadcast("&bEl Oceano Astral se esta regenerando...");
        Bukkit.getScheduler().runTaskLater(this, () -> {
            try {
                for (Player p : w.getPlayers()) p.teleport(Bukkit.getWorlds().get(0).getSpawnLocation());
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv unload " + world);
                if (Bukkit.getWorld(world) != null) Bukkit.unloadWorld(world, false);
                for (String sub : List.of("region", "entities", "poi")) {
                    Path target = folder.resolve(sub);
                    if (Files.isDirectory(target)) try (var s = Files.walk(target)) { s.sorted(java.util.Comparator.reverseOrder()).forEach(p -> p.toFile().delete()); }
                    Path from = template.resolve(sub);
                    if (Files.isDirectory(from)) {
                        Files.createDirectories(target);
                        try (var s = Files.list(from)) { for (Path f : s.toList()) Files.copy(f, target.resolve(f.getFileName()), StandardCopyOption.REPLACE_EXISTING); }
                    }
                }
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv load " + world);
                if (Bukkit.getWorld(world) == null) Bukkit.createWorld(new WorldCreator(world).generator("AstralOceano"));
                nextRegen = System.currentTimeMillis() + everyMs; save();
                broadcast("&aEl Oceano Astral se regenero: menas y cofres nuevos.");
                getLogger().info("Oceano regenerado desde " + template);
            } catch (IOException ex) {
                getLogger().severe("No se pudo regenerar: " + ex);
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv load " + world);
            } finally { regenerating = false; }
        }, 40);
        return true;
    }

    @Override public boolean onCommand(CommandSender s, Command c, String label, String[] a) {
        String sub = a.length == 0 ? "estado" : a[0];
        switch (sub) {
            case "entrar" -> {
                if (!(s instanceof Player p)) return true;
                World w = Bukkit.getWorld(world);
                if (w == null || regenerating) { p.sendMessage("El Oceano Astral no esta disponible ahora. Proba en un rato."); return true; }
                p.teleport(w.getSpawnLocation().add(0.5, 0, 0.5));
                p.showTitle(net.kyori.adventure.title.Title.title(
                    net.kyori.adventure.text.Component.text("Oceano Astral", net.kyori.adventure.text.format.NamedTextColor.AQUA),
                    net.kyori.adventure.text.Component.text("No hay superficie: cuida tu aire", net.kyori.adventure.text.format.NamedTextColor.GRAY)));
                broadcastTo(p, "&bOceano Astral&7: se recomienda ser &ftier 3&7 para minar y explorar. Los monstruos son &ftier 2&7.");
                broadcastTo(p, "&7Sirven las pociones de respiracion, el casco con &fRespiracion&7 y el de tortuga. &f/spawn&7 para volver.");
            }
            case "regenerar" -> { if (!s.hasPermission("astral.oceano.admin")) return false; s.sendMessage("Regenerando el Oceano Astral..."); regenerate(s); }
            case "plantilla" -> {
                // Guarda las regiones actuales como copia limpia (con el server sin jugadores en el oceano).
                if (!s.hasPermission("astral.oceano.admin")) return false;
                World w = Bukkit.getWorld(world);
                if (w == null) { s.sendMessage("Mundo no cargado."); return true; }
                w.save();
                Path template = getDataFolder().toPath().resolve("plantilla");
                try {
                    for (String d : List.of("region", "entities", "poi")) {
                        Path from = dir(w).resolve(d), to = template.resolve(d);
                        if (!Files.isDirectory(from)) continue;
                        Files.createDirectories(to);
                        try (var st = Files.list(from)) { for (Path f : st.toList()) Files.copy(f, to.resolve(f.getFileName()), StandardCopyOption.REPLACE_EXISTING); }
                    }
                    s.sendMessage("Plantilla guardada en " + template);
                } catch (IOException ex) { s.sendMessage("Error: " + ex); }
            }
            default -> {
                long left = Math.max(0, nextRegen - System.currentTimeMillis()) / 60000;
                s.sendMessage("Oceano Astral: se regenera en " + (left / 60) + " h " + (left % 60) + " min.");
            }
        }
        return true;
    }
}
