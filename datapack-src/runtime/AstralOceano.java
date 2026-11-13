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
import org.bukkit.loot.Lootable;
import org.bukkit.inventory.ItemStack;
import org.bukkit.potion.*;
import java.util.regex.*;

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
    long nextRegen; boolean regenerating; double bowDamage;

    @Override public void onEnable() {
        saveDefaultConfig();
        world = getConfig().getString("mundo", "oceano");
        everyMs = getConfig().getLong("regenerar-cada-horas", 72) * 3600_000L;
        warnMinutes = getConfig().getIntegerList("avisos-minutos");
        nextRegen = getConfig().getLong("proxima-regeneracion", 0);
        if (nextRegen == 0) { nextRegen = System.currentTimeMillis() + everyMs; save(); }
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::clock, 20 * 30, 20 * 30);
        Bukkit.getScheduler().runTaskTimer(this, this::waterSet, 20, 10);
        bowDamage = getConfig().getDouble("arco-dano", 2957);
        loadFosa();
        Bukkit.getScheduler().runTaskTimer(this, this::fosaTick, 40, 10);
    }

    void save() { getConfig().set("proxima-regeneracion", nextRegen); saveConfig(); }

    @Override public ChunkGenerator getDefaultWorldGenerator(String worldName, String id) { return "vacio".equals(id) ? new Vacio() : new Gen(); }

    static final class Vacio extends ChunkGenerator { }

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
            int[][] cols = new int[16][16];
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
                cols[x][z] = f;
                for (int y = CEIL_WATER + 1; y < CEIL_TOP; y++) data.setBlock(x, y, z, y == CEIL_WATER + 1 ? Material.DARK_PRISMARINE : Material.STONE);
                data.setBlock(x, CEIL_TOP, z, Material.BEDROCK);
            }
            ores(info.getSeed(), cx, cz, cols, data, min);
        }

        // Entrada a la Fosa del Crustaceo (oceano_fosa.ENTRADA): sin cartel, en el fondo.
        static int gateX = -430, gateZ = 470;
        void gate(int cx, int cz, int[][] cols, ChunkData data) {
            if (cx != gateX >> 4 || cz != gateZ >> 4) return;
            int lx = gateX & 15, lz = gateZ & 15, f = cols[lx][lz];
            for (int dx = -2; dx <= 2; dx++) for (int dz = -2; dz <= 2; dz++) {
                int x = lx + dx, z = lz + dz;
                if (x < 0 || x > 15 || z < 0 || z > 15) continue;
                data.setBlock(x, f, z, Math.abs(dx) <= 1 && Math.abs(dz) <= 1 ? Material.CRYING_OBSIDIAN : Material.DARK_PRISMARINE);
                if (Math.abs(dx) == 2 && Math.abs(dz) == 2) for (int y = f + 1; y <= f + 4; y++) data.setBlock(x, y, z, Material.DARK_PRISMARINE);
            }
            data.setBlock(lx, f + 5, lz, Material.SEA_LANTERN);
        }

        // Menas (oceano_items.py): vetas dentro de la roca, deterministas por chunk.
        static final BlockData PERLA = Bukkit.createBlockData("minecraft:note_block[instrument=banjo,note=22,powered=false]");
        static final BlockData CORAL = Bukkit.createBlockData("minecraft:note_block[instrument=banjo,note=23,powered=false]");
        void ores(long seed, int cx, int cz, int[][] cols, ChunkData data, int min) {
            Random r = new Random(seed ^ (cx * 341873128712L) ^ (cz * 132897987541L));
            vein(r, 2, 3, 20, cols, data, min, PERLA);
            vein(r, 1, 10, 38, cols, data, min, CORAL);
        }
        void vein(Random r, int count, int fromDepth, int toDepth, int[][] cols, ChunkData data, int min, BlockData ore) {
            for (int k = 0; k < count; k++) {
                int x = 1 + r.nextInt(14), z = 1 + r.nextInt(14), y = cols[x][z] - fromDepth - r.nextInt(toDepth - fromDepth);
                for (int n = 3 + r.nextInt(3); n > 0; n--) {
                    if (y > min + 2) {
                        Material m = data.getType(x, y, z);
                        if (m == Material.STONE || m == Material.DEEPSLATE) data.setBlock(x, y, z, ore);
                    }
                    switch (r.nextInt(3)) { case 0 -> x = Math.max(0, Math.min(15, x + r.nextInt(3) - 1)); case 1 -> y += r.nextInt(3) - 1; default -> z = Math.max(0, Math.min(15, z + r.nextInt(3) - 1)); }
                }
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
            // La entrada va despues de la arena del fondo (si no, la tapa).
            if (cx == gateX >> 4 && cz == gateZ >> 4) {
                int[][] cols = new int[16][16];
                for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) cols[x][z] = floor(cx * 16 + x, cz * 16 + z);
                gate(cx, cz, cols, data);
            }
        }
        @Override public int getBaseHeight(WorldInfo info, Random random, int x, int z, HeightMap map) { init(info.getSeed()); return floor(x, z) + 1; }
        @Override public BiomeProvider getDefaultBiomeProvider(WorldInfo info) { return new Biomes(); }
        @Override public List<BlockPopulator> getDefaultPopulators(World world) { return List.of(new Chests()); }
        @Override public boolean shouldGenerateDecorations() { return true; }
        @Override public boolean shouldGenerateStructures() { return true; }
        @Override public boolean shouldGenerateMobs() { return true; }
        @Override public boolean shouldGenerateCaves() { return false; }
        @Override public Location getFixedSpawnLocation(World w, Random random) { init(w.getSeed()); return new Location(w, 0.5, floor(0, 0) + 2, 0.5); }
    }

    // Cofres al azar en el fondo (1 cada ~5 chunks), con la tabla astral:chests/oceano.
    static final class Chests extends BlockPopulator {
        @Override public void populate(WorldInfo info, Random random, int cx, int cz, LimitedRegion region) {
            if (random.nextInt(5) != 0) return;
            int x = cx * 16 + 2 + random.nextInt(12), z = cz * 16 + 2 + random.nextInt(12);
            int y = CEIL_WATER;
            while (y > info.getMinHeight() + 2 && region.getType(x, y, z) == Material.WATER) y--;
            if (!region.getType(x, y, z).isSolid() || y >= CEIL_WATER - 2) return;
            org.bukkit.block.data.type.Chest data = (org.bukkit.block.data.type.Chest) Bukkit.createBlockData(Material.CHEST);
            data.setWaterlogged(true);
            data.setFacing(List.of(BlockFace.NORTH, BlockFace.SOUTH, BlockFace.EAST, BlockFace.WEST).get(random.nextInt(4)));
            region.setBlockData(x, y + 1, z, data);
            if (region.getBlockState(x, y + 1, z) instanceof Lootable chest) {
                chest.setLootTable(Bukkit.getLootTable(NamespacedKey.fromString("astral:chests/oceano")), random.nextLong());
                ((BlockState) chest).update(true, false);
            }
        }
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
            Material.FIRE, Material.SOUL_FIRE, Material.SCAFFOLDING, Material.SLIME_BLOCK, Material.HONEY_BLOCK, Material.NOTE_BLOCK);

    static boolean ore(Block b) {
        if (b.getType() != Material.NOTE_BLOCK || !(b.getBlockData() instanceof org.bukkit.block.data.type.NoteBlock n)) return false;
        return n.getInstrument() == Instrument.BANJO && (n.getNote().getId() == 22 || n.getNote().getId() == 23);
    }

    // El texto de componentes trae espacios ("tool: \"drill\""): las busquedas los toleran.
    static final Pattern ID = Pattern.compile("[{,]\\s*id:\\s*\"([a-z0-9_]+)\""), TIER = Pattern.compile("tier:\\s*([0-9]+)"),
        DRILL = Pattern.compile("tool:\\s*\"drill\""), AGUA = Pattern.compile("set:\\s*\"agua\"");
    static String components(ItemStack it) { return it == null || !it.hasItemMeta() ? "" : it.getItemMeta().getAsComponentString(); }
    static String astralId(ItemStack it) { Matcher m = ID.matcher(components(it)); return m.find() ? m.group(1) : ""; }
    static int drillTier(ItemStack it) {
        String c = components(it);
        if (!DRILL.matcher(c).find()) return 0;
        Matcher m = TIER.matcher(c); return m.find() ? Integer.parseInt(m.group(1)) : 0;
    }

    // Las menas no cambian de estado: sin actualizaciones de fisica ni afinacion con clic derecho.
    @EventHandler(ignoreCancelled = true) public void physics(BlockPhysicsEvent e) { if (here(e.getBlock().getWorld()) && ore(e.getBlock())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void tune(PlayerInteractEvent e) {
        if (e.getAction() == Action.RIGHT_CLICK_BLOCK && e.getClickedBlock() != null && here(e.getClickedBlock().getWorld()) && e.getClickedBlock().getType() == Material.NOTE_BLOCK) e.setCancelled(true);
    }
    // Fuera del oceano, un bloque de nota afinado como mena (banjo 22/23) suelta solo el bloque de nota.
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void fakeOre(BlockBreakEvent e) {
        if (here(e.getBlock().getWorld()) || !ore(e.getBlock())) return;
        e.setDropItems(false);
        if (e.getPlayer().getGameMode() != GameMode.CREATIVE)
            e.getBlock().getWorld().dropItemNaturally(e.getBlock().getLocation().add(0.5, 0.5, 0.5), new ItemStack(Material.NOTE_BLOCK));
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void mineOre(BlockBreakEvent e) {
        if (!here(e.getBlock().getWorld()) || !ore(e.getBlock()) || builder(e.getPlayer())) return;
        if (drillTier(e.getPlayer().getInventory().getItemInMainHand()) < 3) {
            e.setCancelled(true); deny(e.getPlayer(), "esta mena necesita un taladro de amatista o mejor.");
        }
    }

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

    // ----------------------------------------------------------------------------------- set de agua
    static int waterPieces(Player p) {
        int n = 0;
        for (ItemStack it : p.getInventory().getArmorContents()) if (AGUA.matcher(components(it)).find()) n++;
        return n;
    }

    /** Casco: vision nocturna bajo el agua. Set completo: respiracion infinita (en cualquier mundo). */
    void waterSet() {
        for (Player p : Bukkit.getOnlinePlayers()) {
            int n = waterPieces(p);
            if (n == 0) continue;
            if (p.isUnderWater() && AGUA.matcher(components(p.getInventory().getHelmet())).find())
                p.addPotionEffect(new PotionEffect(PotionEffectType.NIGHT_VISION, 260, 0, true, false, true));
            if (n == 4 && p.getRemainingAir() < p.getMaximumAir()) p.setRemainingAir(p.getMaximumAir());
        }
    }

    // Arco de agua: clic derecho dispara un chorro (tridente de agua que no se recoge), sin flechas.
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = false) public void waterBow(PlayerInteractEvent e) {
        if (e.getAction() != Action.RIGHT_CLICK_AIR && e.getAction() != Action.RIGHT_CLICK_BLOCK) return;
        if (e.getHand() != org.bukkit.inventory.EquipmentSlot.HAND) return;
        ItemStack it = e.getItem();
        if (!"agua_arco".equals(astralId(it))) return;
        e.setCancelled(true);
        Player p = e.getPlayer();
        if (p.hasCooldown(it)) return;
        p.setCooldown(it, 14);
        Trident t = p.launchProjectile(Trident.class, p.getEyeLocation().getDirection().multiply(2.6));
        t.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
        t.addScoreboardTag("astral.chorro");
        t.setGlowing(false);
        p.getWorld().playSound(p.getLocation(), Sound.ENTITY_DROWNED_SHOOT, 0.8f, 1.4f);
        p.getWorld().spawnParticle(Particle.BUBBLE_COLUMN_UP, p.getEyeLocation(), 12, 0.2, 0.2, 0.2, 0.05);
        Bukkit.getScheduler().runTaskLater(this, () -> { if (t.isValid()) t.remove(); }, 60);
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true) public void chorro(EntityDamageByEntityEvent e) {
        if (e.getDamager() instanceof Trident t && t.getScoreboardTags().contains("astral.chorro")) e.setDamage(bowDamage);
    }

    @EventHandler public void chorroHit(ProjectileHitEvent e) {
        if (e.getEntity() instanceof Trident t && t.getScoreboardTags().contains("astral.chorro")) {
            t.getWorld().spawnParticle(Particle.SPLASH, t.getLocation(), 20, 0.3, 0.3, 0.3, 0.1);
            Bukkit.getScheduler().runTask(this, t::remove);
        }
    }

    // ----------------------------------------------------------------------------------- Fosa del Crustaceo
    List<String> fosaWorlds = List.of(); double[] fosaArrival, fosaBoss; List<double[]> fosaPoints = new ArrayList<>();
    List<Map<String, Integer>> fosaWaves = new ArrayList<>(); String fosaBossType; int[] gate = {-430, 470};
    final Map<String, Integer> wave = new HashMap<>();         // mundo -> oleada actual (0 = esperando)
    final Map<String, Long> waveAt = new HashMap<>();          // mundo -> cuando empezar la proxima
    final Map<UUID, Long> gateCooldown = new HashMap<>();

    static double[] xyz(String s) { String[] p = s.split(","); return new double[]{Double.parseDouble(p[0]), Double.parseDouble(p[1]), Double.parseDouble(p[2])}; }

    void loadFosa() {
        var c = getConfig().getConfigurationSection("fosa");
        if (c == null) return;
        fosaWorlds = c.getStringList("mundos");
        fosaArrival = xyz(c.getString("llegada", "4.5,112,93.5"));
        fosaBoss = xyz(c.getString("jefe-en", "4.5,112,110.5"));
        fosaBossType = c.getString("jefe", "astral_fosa_cangrejo");
        String[] g = c.getString("entrada", "-430,470").split(",");
        gate = new int[]{Integer.parseInt(g[0].trim()), Integer.parseInt(g[1].trim())};
        Gen.gateX = gate[0]; Gen.gateZ = gate[1];
        for (String pt : c.getStringList("puntos")) fosaPoints.add(xyz(pt));
        for (String w : c.getStringList("oleadas")) {
            Map<String, Integer> m = new LinkedHashMap<>();
            for (String part : w.split(",")) { String[] kv = part.split(":"); m.put(kv[0].trim(), Integer.parseInt(kv[1].trim())); }
            fosaWaves.add(m);
        }
    }

    boolean fosa(World w) { return w != null && fosaWorlds.contains(w.getName()); }

    static boolean fighting(Player p) { return p.getGameMode() == GameMode.SURVIVAL || p.getGameMode() == GameMode.ADVENTURE; }

    List<Entity> waveMobs(World w) {
        List<Entity> out = new ArrayList<>();
        for (Entity e : w.getEntities()) if (e.getScoreboardTags().contains("fosa.mob") || e.getScoreboardTags().contains("fosa.jefe")) if (!e.isDead()) out.add(e);
        return out;
    }

    void fosaTick() {
        long now = System.currentTimeMillis();
        for (String name : fosaWorlds) {
            World w = Bukkit.getWorld(name);
            if (w == null) continue;
            List<Player> players = w.getPlayers().stream().filter(AstralOceano::fighting).toList();
            if (players.isEmpty()) {
                if (wave.getOrDefault(name, 0) != 0 || !waveMobs(w).isEmpty()) { waveMobs(w).forEach(Entity::remove); wave.put(name, 0); waveAt.remove(name); }
                continue;
            }
            // Respiracion: adentro solo sirve el set de agua completo (pociones, Respiracion, tortuga y conducto no).
            for (Player p : players) breatheFosa(p);
            int cur = wave.getOrDefault(name, 0);
            if (cur == 0) { wave.put(name, -1); waveAt.put(name, now + 6000); title(players, "Fosa del Crustaceo", "Sin el set de agua completo, te ahogas"); continue; }
            if (cur == -1) { if (now >= waveAt.get(name)) spawnWave(w, 1, players.size()); continue; }
            if (cur > fosaWaves.size()) continue;                    // jefe derrotado: espera los 8 minutos (mazfin)
            if (!waveMobs(w).isEmpty()) continue;
            if (!waveAt.containsKey(name)) {
                if (cur == fosaWaves.size()) {                       // murio el jefe
                    wave.put(name, cur + 1);
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mazfin " + name);
                    title(players, "Fosa conquistada", "Derrotaron al Cangrejo de la Fosa");
                    continue;
                }
                waveAt.put(name, now + 4000);
                players.forEach(p -> broadcastTo(p, "&bOleada &f" + cur + "/" + fosaWaves.size() + " &bsuperada. Viene otra..."));
            } else if (now >= waveAt.get(name)) { waveAt.remove(name); spawnWave(w, cur + 1, players.size()); }
        }
    }

    void title(List<Player> ps, String a, String b) {
        for (Player p : ps) p.showTitle(net.kyori.adventure.title.Title.title(
            net.kyori.adventure.text.Component.text(a, net.kyori.adventure.text.format.NamedTextColor.AQUA),
            net.kyori.adventure.text.Component.text(b, net.kyori.adventure.text.format.NamedTextColor.GRAY)));
    }

    void spawnWave(World w, int n, int players) {
        wave.put(w.getName(), n); waveAt.remove(w.getName());
        Map<String, Integer> def = fosaWaves.get(n - 1);
        Random r = new Random();
        double mult = 1 + 0.5 * (players - 1);
        for (var e : def.entrySet()) {
            if (e.getKey().equals("jefe")) {
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mm mobs spawn " + fosaBossType + " 1 " + w.getName() + "," + fosaBoss[0] + "," + fosaBoss[1] + "," + fosaBoss[2]);
                w.getPlayers().forEach(p -> broadcastTo(p, "&b&lEl Cangrejo de la Fosa despierta."));
                continue;
            }
            int count = (int) Math.ceil(e.getValue() * mult);
            for (int i = 0; i < count; i++) {
                double[] pt = fosaPoints.get(r.nextInt(fosaPoints.size()));
                Location at = new Location(w, pt[0] + 0.5, pt[1], pt[2] + 0.5);
                String type = e.getKey().equals("drowned_tridente") ? "drowned" : e.getKey();
                Entity mob = w.spawnEntity(at, EntityType.valueOf(type.toUpperCase(Locale.ROOT)));
                mob.addScoreboardTag("fosa.mob");
                if (mob instanceof Mob m) {
                    m.setRemoveWhenFarAway(false);
                    if (e.getKey().equals("drowned_tridente")) m.getEquipment().setItemInMainHand(new ItemStack(Material.TRIDENT));
                    Player near = null; double best = Double.MAX_VALUE;
                    for (Player p : w.getPlayers()) if (fighting(p) && p.getLocation().distanceSquared(at) < best) { best = p.getLocation().distanceSquared(at); near = p; }
                    if (near != null) m.setTarget(near);
                }
            }
        }
        if (!def.containsKey("jefe")) w.getPlayers().forEach(p -> broadcastTo(p, "&bOleada &f" + n + "/" + fosaWaves.size()));
    }

    void breatheFosa(Player p) {
        if (waterPieces(p) == 4) return;                             // el set completo ya rellena el aire
        p.removePotionEffect(PotionEffectType.WATER_BREATHING);
        p.removePotionEffect(PotionEffectType.CONDUIT_POWER);
        int air = p.getRemainingAir() - 15;                            // por encima de la Respiracion o el casco de tortuga
        if (air <= 0) {
            p.setRemainingAir(0);
            p.damage(2.0, org.bukkit.damage.DamageSource.builder(org.bukkit.damage.DamageType.DROWN).build());
        } else p.setRemainingAir(air);
    }

    // En la Fosa no se rompe ni se pone nada, y los guardianes ancianos no dan fatiga.
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void fosaBreak(BlockBreakEvent e) { if (fosa(e.getBlock().getWorld()) && !builder(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void fosaPlace(BlockPlaceEvent e) { if (fosa(e.getBlock().getWorld()) && !builder(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void fatigue(EntityPotionEffectEvent e) {
        if (e.getEntity() instanceof Player p && fosa(p.getWorld()) && e.getNewEffect() != null && e.getNewEffect().getType().equals(PotionEffectType.MINING_FATIGUE)) e.setCancelled(true);
    }

    // Entrada escondida: al llegar al fondo de obsidiana llorona, la corriente te lleva a la Fosa.
    @EventHandler(ignoreCancelled = true) public void gateMove(PlayerMoveEvent e) {
        Player p = e.getPlayer();
        if (!here(p.getWorld()) || e.getTo() == null) return;
        if (e.getFrom().getBlockX() == e.getTo().getBlockX() && e.getFrom().getBlockZ() == e.getTo().getBlockZ() && e.getFrom().getBlockY() == e.getTo().getBlockY()) return;
        if (Math.abs(e.getTo().getX() - gate[0] - 0.5) > 1.6 || Math.abs(e.getTo().getZ() - gate[1] - 0.5) > 1.6) return;
        Block below = e.getTo().getBlock().getRelative(BlockFace.DOWN);
        if (below.getType() != Material.CRYING_OBSIDIAN && below.getRelative(BlockFace.DOWN).getType() != Material.CRYING_OBSIDIAN) return;
        long now = System.currentTimeMillis();
        if (now - gateCooldown.getOrDefault(p.getUniqueId(), 0L) < 6000) return;
        gateCooldown.put(p.getUniqueId(), now);
        broadcastTo(p, "&bUna corriente helada te arrastra hacia la &fFosa del Crustaceo&b...");
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mazentrar " + p.getName() + " fosa");
    }

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
