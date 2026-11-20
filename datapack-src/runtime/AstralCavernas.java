package astral;

import org.bukkit.*;
import org.bukkit.block.Biome;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;
import org.bukkit.event.player.PlayerChangedWorldEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.block.BlockFace;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.generator.BiomeProvider;
import org.bukkit.generator.ChunkGenerator;
import org.bukkit.generator.WorldInfo;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scoreboard.Objective;
import org.bukkit.util.noise.SimplexOctaveGenerator;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Cavernas de Cristal Astrales (cavernas.py, tanda 7e). Todo lo configurable sale de config.yml (generado).
 * Generador propio (caverna cerrada con 5 zonas), vetas = bloque de nota en campana, campamento con tablero de
 * comisiones (atril) y venta (barril), mobs y mini jefes de MythicMobs aparecidos por el plugin, Polvo de Cristal
 * y regeneracion cada 3 dias (como AstralOceano).
 */
public final class AstralCavernas extends JavaPlugin implements Listener {
    static final int TECHO = 119, PISO_MIN = -50;
    static int radio = 500, corazonR = 150, campX = 0, campZ = -300, campY = 12;
    static final String[] ZONAS = {"amatista", "jade", "rubi", "zafiro", "corazon"};

    String world; long everyMs; List<Integer> warnMinutes; long nextRegen; boolean regenerating;
    int drillTier, polvoMin, mobsCerca, mobsTope, jefeCadaSeg; double jefeProb; long jefeEsperaMs; String permTumba;
    final Map<Integer, String> notaObjetivo = new HashMap<>();
    final Map<String, Double> precios = new HashMap<>();
    final Map<String, List<String>> golemsPorZona = new HashMap<>();
    final List<String> aranas = new ArrayList<>();
    final Map<String, String> jefePorZona = new HashMap<>(), nombreJefe = new HashMap<>(), nombreZona = new HashMap<>();
    final Map<String, Long> jefeMuerto = new HashMap<>();
    final List<Map<String, Object>> comisiones = new ArrayList<>();
    NamespacedKey polvoKey, comKey;

    // ------------------------------------------------------------------------------- arranque
    @Override public void onEnable() {
        saveDefaultConfig();
        var c = getConfig();
        world = c.getString("mundo", "cavernas_cristal");
        radio = c.getInt("radio", 500); corazonR = c.getInt("corazon", 150);
        List<Integer> camp = c.getIntegerList("campamento"); if (camp.size() == 2) { campX = camp.get(0); campZ = camp.get(1); }
        campY = c.getInt("camp-y", 12);
        everyMs = c.getLong("regenerar-cada-horas", 72) * 3600_000L;
        warnMinutes = c.getIntegerList("avisos-minutos");
        nextRegen = c.getLong("proxima-regeneracion", 0);
        if (nextRegen == 0) { nextRegen = System.currentTimeMillis() + everyMs; c.set("proxima-regeneracion", nextRegen); saveConfig(); }
        drillTier = c.getInt("taladro-tier", 4); polvoMin = c.getInt("polvo-minutos", 10);
        mobsCerca = c.getInt("mobs-cerca", 5); mobsTope = c.getInt("mobs-tope", 60);
        jefeCadaSeg = c.getInt("jefe-cada-seg", 60); jefeProb = c.getDouble("jefe-prob", 0.25);
        jefeEsperaMs = c.getLong("jefe-espera-min", 8) * 60_000L; permTumba = c.getString("permiso-tumba", "astral.fragmento.arena");
        ConfigurationSection notas = c.getConfigurationSection("notas");
        if (notas != null) for (String k : notas.getKeys(false)) {
            String obj = k.startsWith("gema_") ? k.substring(5).replace("_honda", "") : k;
            notaObjetivo.put(notas.getInt(k), obj);
        }
        ConfigurationSection pr = c.getConfigurationSection("precios");
        if (pr != null) for (String k : pr.getKeys(false)) precios.put(k, pr.getDouble(k));
        ConfigurationSection zs = c.getConfigurationSection("zonas");
        if (zs != null) for (String k : zs.getKeys(false)) nombreZona.put(k, zs.getString(k + ".color", "&f") + zs.getString(k + ".nombre", k));
        ConfigurationSection ms = c.getConfigurationSection("mobs");
        if (ms != null) for (String id : ms.getKeys(false)) {
            if ("arana".equals(ms.getString(id + ".clase"))) { aranas.add(id); continue; }
            for (String z : ms.getStringList(id + ".zonas")) golemsPorZona.computeIfAbsent(z, x -> new ArrayList<>()).add(id);
        }
        ConfigurationSection js = c.getConfigurationSection("jefes");
        if (js != null) for (String id : js.getKeys(false)) { jefePorZona.put(js.getString(id + ".zona"), id); nombreJefe.put(id, js.getString(id + ".nombre", id)); }
        for (Map<?, ?> m : c.getMapList("comisiones")) {
            Map<String, Object> x = new HashMap<>(); m.forEach((k, v) -> x.put(String.valueOf(k), v)); comisiones.add(x);
        }
        polvoKey = new NamespacedKey(this, "polvo_hasta"); comKey = new NamespacedKey(this, "comisiones");
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::clock, 20 * 30, 20 * 30);
        Bukkit.getScheduler().runTaskTimer(this, this::polvoTick, 20, 20);
        Bukkit.getScheduler().runTaskTimer(this, this::conteoTick, 40, 40);
        Bukkit.getScheduler().runTaskTimer(this, this::spawnTick, 100, 100);
        Bukkit.getScheduler().runTaskTimer(this, this::jefeTick, 20L * jefeCadaSeg, 20L * jefeCadaSeg);
        getLogger().info("Cavernas: " + notaObjetivo.size() + " vetas, " + comisiones.size() + " comisiones, " + jefePorZona.size() + " guardianes.");
    }

    @Override public ChunkGenerator getDefaultWorldGenerator(String worldName, String id) { return new Gen(); }

    // ------------------------------------------------------------------------------- zonas
    static String zona(double x, double z) {
        if (x * x + z * z < (double) corazonR * corazonR) return "corazon";
        double a = Math.toDegrees(Math.atan2(x, -z));            // 0 = norte (-z), 90 = este (+x)
        if (a >= -45 && a < 45) return "amatista";
        if (a >= 45 && a < 135) return "jade";
        if (a >= -135 && a < -45) return "zafiro";
        return "rubi";
    }
    static int zonaIdx(String z) { for (int i = 0; i < ZONAS.length; i++) if (ZONAS[i].equals(z)) return i; return 0; }
    static boolean enCampamento(int x, int z) { return Math.abs(x - campX) <= 9 && Math.abs(z - campZ) <= 9; }

    // base, acento, piso, luz de techo
    static final Material[][] PALETA = {
        {Material.TUFF, Material.CALCITE, Material.AMETHYST_BLOCK, Material.PEARLESCENT_FROGLIGHT},
        {Material.DEEPSLATE, Material.GREEN_TERRACOTTA, Material.MOSS_BLOCK, Material.VERDANT_FROGLIGHT},
        {Material.BLACKSTONE, Material.NETHERRACK, Material.MAGMA_BLOCK, Material.SHROOMLIGHT},
        {Material.DEEPSLATE, Material.PACKED_ICE, Material.SNOW_BLOCK, Material.SEA_LANTERN},
        {Material.SMOOTH_BASALT, Material.CALCITE, Material.BLACKSTONE, Material.OCHRE_FROGLIGHT}};
    static final Biome[] BIOMAS = {Biome.DRIPSTONE_CAVES, Biome.LUSH_CAVES, Biome.BASALT_DELTAS, Biome.FROZEN_PEAKS, Biome.THE_END};
    static final int LAGO_Y = 6;

    // ------------------------------------------------------------------------------- generador
    static final class Gen extends ChunkGenerator {
        SimplexOctaveGenerator hills, detail, ceil, pillars, tunnels, light;
        static final BlockData[] VETA = new BlockData[25];
        void init(long seed) {
            if (hills != null) return;
            hills = new SimplexOctaveGenerator(seed, 4); hills.setScale(1 / 140.0);
            detail = new SimplexOctaveGenerator(seed + 7, 3); detail.setScale(1 / 30.0);
            ceil = new SimplexOctaveGenerator(seed + 11, 3); ceil.setScale(1 / 70.0);
            pillars = new SimplexOctaveGenerator(seed + 17, 2); pillars.setScale(1 / 9.0);
            tunnels = new SimplexOctaveGenerator(seed + 23, 2); tunnels.setScale(1 / 26.0);
            light = new SimplexOctaveGenerator(seed + 31, 2); light.setScale(1 / 3.0);
            for (int n = 0; n < 25; n++) VETA[n] = Bukkit.createBlockData("minecraft:note_block[instrument=bell,note=" + n + ",powered=false]");
        }
        int floor(int x, int z) {
            if (enCampamento(x, z)) return campY;
            double h = hills.noise(x, z, 0.5, 0.5, true), d = detail.noise(x, z, 0.5, 0.5, true);
            double r = Math.sqrt((double) x * x + (double) z * z), dep = Math.max(0, 1 - r / corazonR);
            return Math.max(PISO_MIN + 4, (int) Math.round(8 + h * 18 + d * 5 - 52 * Math.pow(dep, 0.7)));
        }
        int ceiling(int x, int z, int f) {
            int top = f + 40 + (int) Math.round(ceil.noise(x, z, 0.5, 0.5, true) * 18);
            if (enCampamento(x, z) || Math.abs(x - campX) <= 12 && Math.abs(z - campZ) <= 12) top = Math.max(top, campY + 12);
            return Math.min(TECHO - 6, Math.max(f + 8, top));
        }
        boolean pilar(int x, int z) { return !(Math.abs(x - campX) <= 12 && Math.abs(z - campZ) <= 12) && pillars.noise(x, z, 0.5, 0.5, true) > 0.74; }

        @Override public void generateNoise(WorldInfo info, Random random, int cx, int cz, ChunkData data) {
            init(info.getSeed());
            int min = info.getMinHeight();
            int[][] fl = new int[16][16], ce = new int[16][16];
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
                int wx = cx * 16 + x, wz = cz * 16 + z;
                int zi = zonaIdx(zona(wx, wz)); Material[] pal = PALETA[zi];
                int f = floor(wx, wz), c = ceiling(wx, wz, f); fl[x][z] = f; ce[x][z] = c;
                boolean pil = pilar(wx, wz);
                data.setBlock(x, min, z, Material.BEDROCK);
                data.setBlock(x, TECHO, z, Material.BEDROCK);
                for (int y = min + 1; y < TECHO; y++) {
                    Material m;
                    if (y <= f || y >= c || pil) {
                        double t = tunnels.noise(wx, y * 1.5, wz, 0.5, 0.5, true);
                        if (y < f - 4 && y > min + 4 && t > 0.62) m = Material.CAVE_AIR;
                        else m = t > 0.3 ? pal[1] : pal[0];
                        if (y == f && !pil) m = pal[2];
                    } else if (zi == 3 && y <= LAGO_Y) m = Material.WATER;
                    else m = Material.CAVE_AIR;
                    data.setBlock(x, y, z, m);
                }
                // luces en el techo y cristales en el piso (sin antorchas)
                if (!pil && light.noise(wx, wz, 0.5, 0.5, true) > 0.62 && (wx * 31 + wz * 17 & 7) == 0) {
                    data.setBlock(x, c, z, pal[3]);
                    if (c + 1 < TECHO) data.setBlock(x, c + 1, z, pal[3]);
                }
                if (!pil && zi == 0 && data.getType(x, f + 1, z) == Material.CAVE_AIR && (wx * 13 + wz * 7 & 15) == 0)
                    data.setBlock(x, f + 1, z, Material.AMETHYST_CLUSTER);
            }
            if (!enCampamento(cx * 16 + 8, cz * 16 + 8)) vetas(info.getSeed(), cx, cz, fl, ce, data, min);
            campamento(cx, cz, data);
        }

        void campamento(int cx, int cz, ChunkData data) {
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
                int wx = cx * 16 + x, wz = cz * 16 + z;
                if (!enCampamento(wx, wz)) continue;
                int dx = wx - campX, dz = wz - campZ;
                boolean borde = Math.abs(dx) == 9 || Math.abs(dz) == 9;
                data.setBlock(x, campY, z, borde ? Material.POLISHED_BLACKSTONE_BRICKS : Material.POLISHED_DEEPSLATE);
                if (Math.abs(dx) == 6 && Math.abs(dz) == 6) data.setBlock(x, campY, z, Material.SEA_LANTERN);
                if (borde && (Math.abs(dx) + Math.abs(dz)) % 4 == 0) data.setBlock(x, campY + 1, z, Material.AMETHYST_CLUSTER);
                if (dx == -3 && dz == 2) data.setBlock(x, campY + 1, z, Bukkit.createBlockData("minecraft:lectern[facing=north]"));
                if (dx == 3 && dz == 2) data.setBlock(x, campY + 1, z, Material.BARREL);
            }
        }

        // Vetas deterministas por chunk: gemas de la zona, Cristal comun y Geoda honda.
        void vetas(long seed, int cx, int cz, int[][] fl, int[][] ce, ChunkData data, int min) {
            Random r = new Random(seed ^ (cx * 341873128712L) ^ (cz * 132897987541L));
            String z = zona(cx * 16 + 8, cz * 16 + 8);
            String[] gemas = switch (z) { case "amatista" -> new String[]{"amatista"}; case "jade" -> new String[]{"jade"};
                case "rubi" -> new String[]{"rubi", "topacio"}; case "zafiro" -> new String[]{"zafiro"}; default -> new String[]{"opalo", "onix"}; };
            for (String g : gemas) for (int k = 0; k < (gemas.length == 1 ? 4 : 2); k++) veta(r, data, fl, ce, min, notaGema(g), true, 2 + r.nextInt(3));
            for (int k = 0; k < 12; k++) veta(r, data, fl, ce, min, 14, false, 3 + r.nextInt(4));
            for (int k = z.equals("corazon") ? 2 : r.nextInt(2); k > 0; k--) veta(r, data, fl, ce, min, 15, false, 1 + r.nextInt(3));
        }
        static final String[] TIPOS = {"rubi", "zafiro", "jade", "topacio", "amatista", "opalo", "onix"};
        static int notaGema(String t) { for (int i = 0; i < TIPOS.length; i++) if (TIPOS[i].equals(t)) return i * 2; return 0; }
        void veta(Random r, ChunkData data, int[][] fl, int[][] ce, int min, int nota, boolean gema, int largo) {
            int x = 1 + r.nextInt(14), z = 1 + r.nextInt(14), f = fl[x][z], c = ce[x][z];
            int roll = r.nextInt(10);
            int y = roll < 5 ? f - r.nextInt(6) : roll < 8 ? c + r.nextInt(6) : min + 5 + r.nextInt(Math.max(1, f - min - 10));
            if (nota == 15) y = Math.min(y, -1 - r.nextInt(8));          // geoda: siempre honda
            for (int n = largo; n > 0; n--) {
                if (y > min + 1 && y < TECHO - 1) {
                    Material m = data.getType(x, y, z);
                    if (m.isSolid() && m != Material.BEDROCK && !m.name().contains("FROGLIGHT") && m != Material.SHROOMLIGHT
                            && m != Material.SEA_LANTERN && m != Material.NOTE_BLOCK)
                        data.setBlock(x, y, z, VETA[gema && y < 0 ? nota + 1 : nota]);
                }
                switch (r.nextInt(3)) { case 0 -> x = Math.max(0, Math.min(15, x + r.nextInt(3) - 1)); case 1 -> y += r.nextInt(3) - 1; default -> z = Math.max(0, Math.min(15, z + r.nextInt(3) - 1)); }
            }
        }

        @Override public BiomeProvider getDefaultBiomeProvider(WorldInfo info) {
            return new BiomeProvider() {
                @Override public Biome getBiome(WorldInfo i, int x, int y, int z) { return BIOMAS[zonaIdx(zona(x, z))]; }
                @Override public List<Biome> getBiomes(WorldInfo i) { return List.of(BIOMAS); }
            };
        }
        @Override public boolean shouldGenerateDecorations() { return false; }
        @Override public boolean shouldGenerateStructures() { return false; }
        @Override public boolean shouldGenerateMobs() { return false; }
        @Override public boolean shouldGenerateCaves() { return false; }
        @Override public boolean shouldGenerateSurface() { return false; }
        @Override public Location getFixedSpawnLocation(World w, Random random) { return new Location(w, campX + 0.5, campY + 1, campZ + 0.5); }
    }

    // ------------------------------------------------------------------------------- reglas
    boolean here(World w) { return w != null && w.getName().equals(world); }
    boolean builder(Player p) { return p.getGameMode() == GameMode.CREATIVE && p.hasPermission("astral.cavernas.editar"); }
    static int nota(Block b) {
        if (b.getType() != Material.NOTE_BLOCK || !(b.getBlockData() instanceof org.bukkit.block.data.type.NoteBlock n)) return -1;
        return n.getInstrument() == Instrument.BELL && n.getNote().getId() <= 15 ? n.getNote().getId() : -1;
    }
    void aviso(Player p, String s) { p.sendActionBar(color("&5Cavernas: &f" + s)); }
    static net.kyori.adventure.text.Component color(String s) { return net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer.legacyAmpersand().deserialize(s); }

    static final Pattern ID = Pattern.compile("[{,]\\s*id:\\s*\"([a-z0-9_]+)\""), TIER = Pattern.compile("tier:\\s*([0-9]+)"),
        DRILL = Pattern.compile("tool:\\s*\"drill\""), EQUIPO = Pattern.compile("type:\\s*\"(weapon|armor|staff)\"");
    static String comps(ItemStack it) { return it == null || !it.hasItemMeta() ? "" : it.getItemMeta().getAsComponentString(); }
    static String astralId(ItemStack it) { Matcher m = ID.matcher(comps(it)); return m.find() ? m.group(1) : ""; }
    static int tier(String c) { Matcher m = TIER.matcher(c); return m.find() ? Integer.parseInt(m.group(1)) : 0; }
    static int drillTier(ItemStack it) { String c = comps(it); return DRILL.matcher(c).find() ? tier(c) : 0; }

    @EventHandler(ignoreCancelled = true) public void physics(BlockPhysicsEvent e) { if (here(e.getBlock().getWorld()) && nota(e.getBlock()) >= 0) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void explode(EntityExplodeEvent e) { if (here(e.getLocation().getWorld())) e.blockList().clear(); }
    @EventHandler(ignoreCancelled = true) public void explode(BlockExplodeEvent e) { if (here(e.getBlock().getWorld())) e.blockList().clear(); }

    // Fuera de las Cavernas un bloque de nota afinado como veta solo devuelve el bloque de nota.
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void falsa(BlockBreakEvent e) {
        if (here(e.getBlock().getWorld()) || nota(e.getBlock()) < 0) return;
        e.setDropItems(false);
        if (e.getPlayer().getGameMode() != GameMode.CREATIVE) e.getBlock().getWorld().dropItemNaturally(e.getBlock().getLocation().add(.5, .5, .5), new ItemStack(Material.NOTE_BLOCK));
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void picar(BlockBreakEvent e) {
        if (!here(e.getBlock().getWorld()) || builder(e.getPlayer())) return;
        Block b = e.getBlock();
        if (enCampamento(b.getX(), b.getZ()) && b.getY() >= campY && b.getY() <= campY + 2) { e.setCancelled(true); aviso(e.getPlayer(), "el campamento no se rompe."); return; }
        int n = nota(b);
        if (n < 0) return;
        if (drillTier(e.getPlayer().getInventory().getItemInMainHand()) < drillTier) { e.setCancelled(true); aviso(e.getPlayer(), "las vetas se pican con taladro de Rubi o mejor."); return; }
        avance(e.getPlayer(), "veta", notaObjetivo.getOrDefault(n, ""), 1);
    }

    // Taladro en area (20/11): en las Cavernas lo hace el plugin (el datapack no pica aca). Rompe TODO lo del plano como
    // si lo picara el jugador (premios, comisiones, Polvo y campamento iguales). Piso/techo = cuadrado plano.
    static final Pattern AREA = Pattern.compile("area:\\s*([0-9]+)");
    boolean rompiendo;
    static int[] rango(int n, boolean mas) {
        int lo = n % 2 == 1 ? -(n / 2) : mas ? -(n / 2 - 1) : -(n / 2);
        int[] r = new int[n]; for (int i = 0; i < n; i++) r[i] = lo + i; return r;
    }
    static BlockFace cardinal(float yaw) {
        float y = ((yaw % 360) + 360) % 360;
        return y >= 45 && y < 135 ? BlockFace.WEST : y >= 135 && y < 225 ? BlockFace.NORTH : y >= 225 && y < 315 ? BlockFace.EAST : BlockFace.SOUTH;
    }
    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true) public void area(BlockBreakEvent e) {
        Player p = e.getPlayer();
        if (rompiendo || !here(e.getBlock().getWorld()) || p.isSneaking() || p.getGameMode() == GameMode.SPECTATOR) return;
        String c = comps(p.getInventory().getItemInMainHand());
        if (!DRILL.matcher(c).find()) return;
        Matcher m = AREA.matcher(c);
        int a = m.find() ? Integer.parseInt(m.group(1)) : 1;
        int[] d = switch (a) { case 2 -> new int[]{1, 2}; case 3 -> new int[]{2, 2}; case 4 -> new int[]{3, 3}; case 5 -> new int[]{4, 4}; default -> null; };
        if (d == null) return;
        Block b = e.getBlock(); Location eye = p.getEyeLocation();
        BlockFace f = cardinal(eye.getYaw());
        int fx = f.getModX(), fz = f.getModZ(), rx = -fz, rz = fx;      // adelante y derecha
        List<int[]> offs = new ArrayList<>();
        if (Math.abs(eye.getPitch()) >= 50) {                            // piso o techo: plano, crece hacia adelante
            for (int u : rango(d[0], true)) for (int v : rango(d[1], true)) offs.add(new int[]{u * rx + v * fx, 0, u * rz + v * fz});
        } else {                                                         // pared: crece hacia arriba salvo que este sobre la cabeza
            boolean arriba = b.getY() <= p.getLocation().getBlockY() + 1;
            for (int u : rango(d[0], true)) for (int v : rango(d[1], arriba)) offs.add(new int[]{u * rx, v, u * rz});
        }
        int bx = b.getX(), by = b.getY(), bz = b.getZ(); World w = b.getWorld();
        Bukkit.getScheduler().runTask(this, () -> {
            if (!p.isOnline() || !p.getWorld().equals(w)) return;
            rompiendo = true;
            try {
                for (int[] o : offs) {
                    if (o[0] == 0 && o[1] == 0 && o[2] == 0) continue;
                    Block x = w.getBlockAt(bx + o[0], by + o[1], bz + o[2]);
                    Material t = x.getType();
                    if (t.isAir() || x.isLiquid() || t == Material.BEDROCK || t == Material.BARRIER || t.getHardness() < 0) continue;
                    p.breakBlock(x);
                }
            } finally { rompiendo = false; }
        });
    }

    // Picando una veta (20/11): la roca es oscura y las grietas casi no se ven. Mientras se pica: chispas del color de
    // la gema, sonido de cristal y barra de avance en la barra de accion.
    static final Color[] COLOR_GEMA = {Color.fromRGB(0xff3b4f), Color.fromRGB(0x3b7bff), Color.fromRGB(0x3bdc6a), Color.fromRGB(0xffb52e),
        Color.fromRGB(0xb466ff), Color.fromRGB(0xf2ecff), Color.fromRGB(0x5a5a6e)};
    static Color colorNota(int n) { return n == 14 ? Color.fromRGB(0xc7a0ff) : n == 15 ? Color.fromRGB(0x7fe0ff) : COLOR_GEMA[Math.min(6, n / 2)]; }
    final Map<UUID, Integer> picando = new HashMap<>();
    @EventHandler(ignoreCancelled = true) public void empieza(BlockDamageEvent e) {
        Block b = e.getBlock(); Player p = e.getPlayer();
        int n = nota(b);
        if (!here(b.getWorld()) || n < 0 || e.getInstaBreak()) return;
        Integer viejo = picando.remove(p.getUniqueId()); if (viejo != null) Bukkit.getScheduler().cancelTask(viejo);
        Color col = colorNota(n); Location c = b.getLocation().add(.5, .5, .5);
        Particle.DustOptions dust = new Particle.DustOptions(col, 1.1f);
        float[] avance = {0}; int[] t = {0}; int[] id = {0};
        id[0] = Bukkit.getScheduler().scheduleSyncRepeatingTask(this, () -> {
            Block mira = p.isOnline() ? p.getTargetBlockExact(6) : null;
            if (mira == null || !mira.equals(b) || nota(b) < 0 || t[0]++ > 400) { parar(p, id[0]); return; }
            avance[0] = Math.min(1f, avance[0] + b.getBreakSpeed(p) * 2);
            // chispas en la cara que mira el jugador
            Location cara = c.clone().add(p.getEyeLocation().toVector().subtract(c.toVector()).normalize().multiply(0.55));
            b.getWorld().spawnParticle(Particle.DUST, cara, 4, .22, .22, .22, 0, dust);
            if (t[0] % 3 == 0) b.getWorld().spawnParticle(Particle.ELECTRIC_SPARK, cara, 2, .15, .15, .15, .02);
            if (t[0] % 2 == 0) b.getWorld().playSound(c, Sound.BLOCK_AMETHYST_BLOCK_HIT, .7f, .8f + avance[0] * .8f);
            barra(p).setProgress(Math.max(0, Math.min(1, avance[0])));
        }, 0, 2);
        picando.put(p.getUniqueId(), id[0]);
    }
    // Avance arriba de la pantalla (la barra de accion la pisa la de vida/mana de AuraSkills). Nunca YELLOW (BetterHud).
    final Map<UUID, org.bukkit.boss.BossBar> barras = new HashMap<>();
    org.bukkit.boss.BossBar barra(Player p) {
        return barras.computeIfAbsent(p.getUniqueId(), u -> {
            org.bukkit.boss.BossBar b = Bukkit.createBossBar("⛏ Picando veta", org.bukkit.boss.BarColor.PURPLE, org.bukkit.boss.BarStyle.SEGMENTED_12);
            b.addPlayer(p); return b; });
    }
    void sinBarra(Player p) { org.bukkit.boss.BossBar b = barras.remove(p.getUniqueId()); if (b != null) b.removeAll(); }
    void parar(Player p, int id) {
        Bukkit.getScheduler().cancelTask(id);
        picando.remove(p.getUniqueId(), id);
        sinBarra(p);
    }
    // El cliente adivina que la veta de al lado cambia de instrumento (el server ya no lo hace): se le reenvia la real.
    void reenviarVecinas(Block b) {
        List<Block> vs = new ArrayList<>();
        for (BlockFace f : new BlockFace[]{BlockFace.UP, BlockFace.DOWN, BlockFace.NORTH, BlockFace.SOUTH, BlockFace.EAST, BlockFace.WEST}) {
            Block v = b.getRelative(f); if (nota(v) >= 0) vs.add(v);
        }
        if (vs.isEmpty()) return;
        for (long d : new long[]{1, 5}) Bukkit.getScheduler().runTaskLater(this, () -> {
            for (Player q : b.getWorld().getPlayers()) {
                if (q.getLocation().distanceSquared(b.getLocation()) > 64 * 64) continue;
                for (Block v : vs) if (nota(v) >= 0) q.sendBlockChange(v.getLocation(), v.getBlockData());
            }
        }, d);
    }
    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true) public void vecinas(BlockBreakEvent e) {
        if (here(e.getBlock().getWorld())) reenviarVecinas(e.getBlock());
    }
    @EventHandler public void sale(org.bukkit.event.player.PlayerQuitEvent e) { sinBarra(e.getPlayer()); }
    @EventHandler public void suelta(BlockDamageAbortEvent e) {
        Integer id = picando.remove(e.getPlayer().getUniqueId()); if (id != null) Bukkit.getScheduler().cancelTask(id);
        sinBarra(e.getPlayer());
    }
    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true) public void rota(BlockBreakEvent e) {
        int n = nota(e.getBlock());
        if (!here(e.getBlock().getWorld()) || n < 0) return;
        Integer id = picando.remove(e.getPlayer().getUniqueId()); if (id != null) Bukkit.getScheduler().cancelTask(id);
        sinBarra(e.getPlayer());
        Location c = e.getBlock().getLocation().add(.5, .5, .5);
        c.getWorld().spawnParticle(Particle.DUST, c, 25, .35, .35, .35, 0, new Particle.DustOptions(colorNota(n), 1.4f));
        c.getWorld().playSound(c, Sound.BLOCK_AMETHYST_CLUSTER_BREAK, 1f, 1f);
    }

    // Luz (20/11): la caverna es cerrada y muy oscura; adentro hay vision nocturna (sin particulas ni icono).
    void luz(Player p) {
        PotionEffect pe = p.getPotionEffect(PotionEffectType.NIGHT_VISION);
        if (pe == null || pe.isAmbient() && pe.getDuration() < 300) p.addPotionEffect(new PotionEffect(PotionEffectType.NIGHT_VISION, 400, 0, true, false, false));
    }
    @EventHandler public void cambiaMundo(PlayerChangedWorldEvent e) {
        Player p = e.getPlayer();
        if (here(p.getWorld())) { luz(p); return; }
        PotionEffect pe = p.getPotionEffect(PotionEffectType.NIGHT_VISION);
        if (here(e.getFrom()) && pe != null && pe.isAmbient()) p.removePotionEffect(PotionEffectType.NIGHT_VISION);
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void poner(BlockPlaceEvent e) {
        if (!here(e.getBlock().getWorld()) || builder(e.getPlayer())) return;
        Block b = e.getBlockPlaced();
        if (b.getType() == Material.NOTE_BLOCK || enCampamento(b.getX(), b.getZ()) && b.getY() <= campY + 3) { e.setCancelled(true); aviso(e.getPlayer(), "eso no se puede poner aca."); }
    }

    @EventHandler(priority = EventPriority.HIGH) public void tocar(PlayerInteractEvent e) {
        Player p = e.getPlayer();
        if (e.getAction().isRightClick() && "polvo_cristal".equals(astralId(e.getItem()))) { e.setCancelled(true); usarPolvo(p, e.getItem()); return; }
        Block b = e.getClickedBlock();
        if (b == null || !here(b.getWorld()) || e.getAction() != org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK) return;
        if (b.getType() == Material.NOTE_BLOCK && !builder(p)) e.setCancelled(true);
        if (!enCampamento(b.getX(), b.getZ())) return;
        if (b.getType() == Material.LECTERN) { e.setCancelled(true); abrirComisiones(p); }
        else if (b.getType() == Material.BARREL) { e.setCancelled(true); vender(p); }
    }

    // ------------------------------------------------------------------------------- Polvo de Cristal
    void usarPolvo(Player p, ItemStack it) {
        long ahora = System.currentTimeMillis(), hasta = Math.max(ahora, p.getPersistentDataContainer().getOrDefault(polvoKey, PersistentDataType.LONG, 0L));
        hasta += polvoMin * 60_000L;
        p.getPersistentDataContainer().set(polvoKey, PersistentDataType.LONG, hasta);
        it.setAmount(it.getAmount() - 1);
        p.sendMessage(color("&d✦ Polvo de Cristal: &fgemas de mejor calidad en las Cavernas por &d" + ((hasta - ahora) / 60000) + " min&f."));
        p.playSound(p.getLocation(), Sound.BLOCK_AMETHYST_BLOCK_RESONATE, 1, 1.4f);
    }
    void polvoTick() {
        long ahora = System.currentTimeMillis();
        for (Player p : Bukkit.getOnlinePlayers()) {
            if (here(p.getWorld())) luz(p);
            long hasta = p.getPersistentDataContainer().getOrDefault(polvoKey, PersistentDataType.LONG, 0L);
            if (hasta > ahora) {
                p.addScoreboardTag("cav.polvo");
                if (here(p.getWorld())) { long s = (hasta - ahora) / 1000; p.sendActionBar(color("&d✦ Polvo de Cristal &f" + s / 60 + ":" + String.format("%02d", s % 60))); }
            } else if (p.removeScoreboardTag("cav.polvo") && hasta != 0) {
                p.getPersistentDataContainer().remove(polvoKey);
                p.sendMessage(color("&7✦ Se termino el Polvo de Cristal."));
            }
        }
    }

    // ------------------------------------------------------------------------------- comisiones
    static String hoy() { return LocalDate.now(ZoneId.of("America/Argentina/Buenos_Aires")).toString(); }
    /** [indices(3), avance(3), cobradas(3)] del dia; cambian a medianoche (hora argentina). */
    int[][] diarias(Player p) {
        String s = p.getPersistentDataContainer().get(comKey, PersistentDataType.STRING), d = hoy();
        if (s != null) {
            String[] a = s.split("\\|");
            if (a.length == 4 && a[0].equals(d)) {
                int[][] r = new int[3][3];
                for (int i = 0; i < 3; i++) { r[0][i] = Integer.parseInt(a[1].split(",")[i]); r[1][i] = Integer.parseInt(a[2].split(",")[i]); r[2][i] = a[3].charAt(i) - '0'; }
                return r;
            }
        }
        List<Integer> idx = new ArrayList<>(); for (int i = 0; i < comisiones.size(); i++) idx.add(i);
        Collections.shuffle(idx, new Random(p.getUniqueId().getMostSignificantBits() ^ d.hashCode()));
        int[][] r = {{idx.get(0), idx.get(1), idx.get(2)}, {0, 0, 0}, {0, 0, 0}};
        guardar(p, r); return r;
    }
    void guardar(Player p, int[][] r) {
        p.getPersistentDataContainer().set(comKey, PersistentDataType.STRING, hoy() + "|" + r[0][0] + "," + r[0][1] + "," + r[0][2] + "|"
            + r[1][0] + "," + r[1][1] + "," + r[1][2] + "|" + r[2][0] + r[2][1] + r[2][2]);
    }
    void avance(Player p, String tipo, String objetivo, int n) {
        if (n <= 0 || comisiones.size() < 3) return;
        int[][] r = diarias(p); boolean cambio = false;
        for (int i = 0; i < 3; i++) {
            var c = comisiones.get(r[0][i]); int meta = ((Number) c.get("cantidad")).intValue();
            if (!tipo.equals(c.get("tipo")) || r[1][i] >= meta) continue;
            Object obj = c.get("objetivo");
            if (!"any".equals(obj) && !String.valueOf(obj).equals(objetivo)) continue;
            r[1][i] = Math.min(meta, r[1][i] + n); cambio = true;
            if (r[1][i] >= meta) { p.sendMessage(color("&d✦ Comision lista: &f" + c.get("texto") + "&7. Cobrala en el atril del campamento.")); p.playSound(p.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.2f); }
        }
        if (cambio) guardar(p, r);
    }
    static final class Tablero implements InventoryHolder { Inventory inv; @Override public Inventory getInventory() { return inv; } }
    // Tablero (arte del dueno 19/11, ventanas_19_11.py): 3 tarjetas de 3 columnas. Fila 0 cartel de estado,
    // fila 1 icono, fila 3 barra de avance, fila 4 COBRAR. Clic en cualquier casilla de la tarjeta = cobrar.
    ItemStack pieza(String modelo, String nombre, List<net.kyori.adventure.text.Component> lore) {
        ItemStack it = new ItemStack(Material.PAPER); ItemMeta m = it.getItemMeta();
        m.setItemModel(NamespacedKey.fromString(modelo)); m.displayName(color(nombre)); m.lore(lore);
        it.setItemMeta(m); return it;
    }
    void abrirComisiones(Player p) {
        Tablero t = new Tablero();
        t.inv = Bukkit.createInventory(t, 54, color(getConfig().getString("titulo-comisiones", "&5&lComisiones de las Cavernas")));
        int[][] r = diarias(p);
        for (int i = 0; i < 3; i++) {
            var c = comisiones.get(r[0][i]); int meta = ((Number) c.get("cantidad")).intValue();
            boolean lista = r[1][i] >= meta, cobrada = r[2][i] == 1;
            String nombre = (cobrada ? "&8" : lista ? "&a&l" : "&e") + c.get("texto");
            var lore = List.of(color("&7Avance: &f" + r[1][i] + "/" + meta),
                color("&7Premio: &6" + fmt(((Number) c.get("plata")).longValue()) + "$ &7y &d" + c.get("polvo") + " Polvo de Cristal"),
                color(cobrada ? "&8Ya cobrada." : lista ? "&aClic para cobrar." : "&7Se reinician a medianoche."));
            String estado = cobrada ? "cobrada" : lista ? "lista" : "pendiente";
            int nivel = cobrada ? -1 : Math.min(10, r[1][i] * 10 / Math.max(1, meta));
            for (int k = 0; k < 3; k++) {
                int col = i * 3 + k;
                t.inv.setItem(col, pieza("astral:ventanas1911/badge_" + estado + "_" + k, nombre, lore));
                t.inv.setItem(27 + col, pieza("astral:ventanas1911/barra_" + (nivel < 0 ? "cobrada" : String.valueOf(nivel)) + "_" + k, nombre, lore));
                if (lista && !cobrada) t.inv.setItem(36 + col, pieza("astral:ventanas1911/cobrar_" + k, "&a&lCOBRAR", lore));
                for (int fila : new int[]{1, 2}) if (k != 1 || fila != 1) t.inv.setItem(fila * 9 + col, pieza("astral:viajes/blank", nombre, lore));
            }
            t.inv.setItem(9 + i * 3 + 1, pieza(String.valueOf(c.getOrDefault("icono", "astral:viajes/blank")), nombre, lore));
        }
        var info = List.of(color("&73 comisiones por dia (se reinician a medianoche)."), color("&7El barril de al lado compra tus Cristales y Geodas."),
            color("&7El Polvo de Cristal mejora la calidad de las gemas."));
        for (int s = 47; s <= 51; s++) t.inv.setItem(s, pieza("astral:viajes/blank", "&dCampamento", info));
        p.openInventory(t.inv);
    }
    static String fmt(long n) { return String.format(Locale.ROOT, "%,d", n).replace(',', '.'); }
    @EventHandler public void clicTablero(InventoryClickEvent e) {
        if (!(e.getInventory().getHolder() instanceof Tablero) || !(e.getWhoClicked() instanceof Player p)) return;
        e.setCancelled(true);
        if (e.getClickedInventory() != e.getInventory()) return;
        int i = e.getSlot() < 45 ? (e.getSlot() % 9) / 3 : -1;
        if (i < 0) return;
        int[][] r = diarias(p); var c = comisiones.get(r[0][i]);
        if (r[2][i] == 1 || r[1][i] < ((Number) c.get("cantidad")).intValue()) return;
        r[2][i] = 1; guardar(p, r);
        long plata = ((Number) c.get("plata")).longValue(); int polvo = ((Number) c.get("polvo")).intValue();
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "eco give " + p.getName() + " " + plata);
        for (int k = 0; k < polvo; k++) Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "loot give " + p.getName() + " loot astral:item/polvo_cristal");
        p.sendMessage(color("&a✦ Comision cobrada: &6+" + fmt(plata) + "$ &ay &d" + polvo + " Polvo de Cristal&a."));
        p.playSound(p.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 1, 1.3f);
        getLogger().info(p.getName() + " cobro la comision " + c.get("clave") + " (" + plata + ")");
        abrirComisiones(p);
    }
    @EventHandler public void dragTablero(InventoryDragEvent e) { if (e.getInventory().getHolder() instanceof Tablero) e.setCancelled(true); }

    // Taladro en area: el datapack suma cav.n<nota> (tool/mine); aca pasa a las comisiones.
    void conteoTick() {
        var sb = Bukkit.getScoreboardManager().getMainScoreboard();
        World w = Bukkit.getWorld(world); if (w == null) return;
        for (Player p : w.getPlayers()) for (var e : notaObjetivo.entrySet()) {
            Objective o = sb.getObjective("cav.n" + e.getKey()); if (o == null) continue;
            var s = o.getScore(p.getName()); int v = s.isScoreSet() ? s.getScore() : 0;
            if (v > 0) { s.setScore(0); avance(p, "veta", e.getValue(), v); }
        }
    }

    // ------------------------------------------------------------------------------- venta
    void vender(Player p) {
        double total = 0; int n = 0;
        ItemStack[] cont = p.getInventory().getStorageContents();
        for (int i = 0; i < cont.length; i++) {
            Double precio = precios.get(astralId(cont[i]));
            if (precio == null) continue;
            total += precio * cont[i].getAmount(); n += cont[i].getAmount(); cont[i] = null;
        }
        if (n == 0) { p.sendMessage(color("&7El barril compra &dCristal Astral en bruto &7y &bGeodas Estelares&7. No tenes ninguno.")); return; }
        p.getInventory().setStorageContents(cont);
        long plata = Math.round(total);
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "eco give " + p.getName() + " " + plata);
        p.sendMessage(color("&a✦ Vendiste " + n + " menas por &6" + fmt(plata) + "$&a."));
        p.playSound(p.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 1, 1);
        getLogger().info(p.getName() + " vendio " + n + " menas por " + plata);
    }

    // ------------------------------------------------------------------------------- mobs y guardianes
    Location lugar(Player p, int minD, int maxD) {
        Random r = new Random(); World w = p.getWorld();
        for (int intento = 0; intento < 8; intento++) {
            double a = r.nextDouble() * Math.PI * 2; int d = minD + r.nextInt(maxD - minD + 1);
            int x = p.getLocation().getBlockX() + (int) (Math.cos(a) * d), z = p.getLocation().getBlockZ() + (int) (Math.sin(a) * d);
            if (Math.abs(x) > radio - 4 || Math.abs(z) > radio - 4 || enCampamento(x, z) || !w.isChunkLoaded(x >> 4, z >> 4)) continue;
            int y0 = p.getLocation().getBlockY();
            for (int y = y0 + 6; y > y0 - 14; y--) {
                Block b = w.getBlockAt(x, y, z);
                if (b.getType().isSolid() && b.getRelative(0, 1, 0).isEmpty() && b.getRelative(0, 2, 0).isEmpty() && b.getRelative(0, 3, 0).isEmpty())
                    return new Location(w, x + 0.5, y + 1, z + 0.5);
            }
        }
        return null;
    }
    void aparecer(String id, Location l) {
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mm mobs spawn " + id + " 1 " + l.getWorld().getName() + "," + l.getBlockX() + "," + l.getBlockY() + "," + l.getBlockZ());
    }
    void spawnTick() {
        World w = Bukkit.getWorld(world);
        if (w == null || regenerating || !Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) return;
        long total = w.getLivingEntities().stream().filter(e -> e.getScoreboardTags().contains("cav.mob")).count();
        Random r = new Random();
        for (Player p : w.getPlayers()) {
            if (total >= mobsTope) return;
            if (p.getGameMode() == GameMode.SPECTATOR || p.getGameMode() == GameMode.CREATIVE) continue;
            if (Math.abs(p.getLocation().getX() - campX) < 30 && Math.abs(p.getLocation().getZ() - campZ) < 30) continue;
            long cerca = p.getNearbyEntities(32, 16, 32).stream().filter(e -> e.getScoreboardTags().contains("cav.mob")).count();
            if (cerca >= mobsCerca) continue;
            Location l = lugar(p, 12, 24); if (l == null) continue;
            String z = zona(l.getX(), l.getZ());
            List<String> golems = golemsPorZona.getOrDefault(z, List.of());
            String id = !golems.isEmpty() && (aranas.isEmpty() || r.nextDouble() < 0.7) ? golems.get(r.nextInt(golems.size())) : aranas.isEmpty() ? null : aranas.get(r.nextInt(aranas.size()));
            if (id != null) { aparecer(id, l); total++; }
        }
    }
    void jefeTick() {
        World w = Bukkit.getWorld(world);
        if (w == null || regenerating || !Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) return;
        Set<String> vivos = new HashSet<>();
        for (LivingEntity e : w.getLivingEntities()) if (e.getScoreboardTags().contains("cav.jefe")) vivos.add(zona(e.getLocation().getX(), e.getLocation().getZ()));
        Random r = new Random(); long ahora = System.currentTimeMillis();
        for (var e : jefePorZona.entrySet()) {
            String z = e.getKey();
            if (vivos.contains(z) || ahora - jefeMuerto.getOrDefault(z, 0L) < jefeEsperaMs || r.nextDouble() >= jefeProb) continue;
            List<Player> ps = w.getPlayers().stream().filter(p -> p.getGameMode() == GameMode.SURVIVAL && zona(p.getLocation().getX(), p.getLocation().getZ()).equals(z)
                && Math.hypot(p.getLocation().getX() - campX, p.getLocation().getZ() - campZ) > 40).toList();
            if (ps.isEmpty()) continue;
            Location l = lugar(ps.get(r.nextInt(ps.size())), 14, 22); if (l == null) continue;
            aparecer(e.getValue(), l);
            for (Player p : w.getPlayers()) p.sendMessage(color("&d✦ &f" + nombreJefe.get(e.getValue()) + " &7aparecio en " + nombreZona.getOrDefault(z, z) + "&7."));
        }
    }
    @EventHandler public void muere(EntityDeathEvent e) {
        LivingEntity m = e.getEntity();
        if (!here(m.getWorld()) || !m.getScoreboardTags().contains("cav.mob")) return;
        String z = zona(m.getLocation().getX(), m.getLocation().getZ());
        if (m.getScoreboardTags().contains("cav.jefe")) jefeMuerto.put(z, System.currentTimeMillis());
        Player k = m.getKiller(); if (k == null) return;
        if (m.getScoreboardTags().contains("cav.jefe")) avance(k, "jefe", "any", 1);
        if (m.getScoreboardTags().contains("cav.golem")) avance(k, "matar", "golem", 1);
        if (m.getScoreboardTags().contains("cav.arana")) avance(k, "matar", "arana", 1);
        if (z.equals("corazon")) avance(k, "matar", "corazon", 1);
    }

    // ------------------------------------------------------------------------------- regeneracion
    void clock() {
        if (regenerating) return;
        long left = nextRegen - System.currentTimeMillis();
        for (int m : warnMinutes) { long at = m * 60_000L; if (left <= at && left > at - 30_000L) Bukkit.broadcast(color("&dLas Cavernas de Cristal se regeneran en &f" + m + (m == 1 ? " minuto" : " minutos") + "&d.")); }
        if (left <= 0) regenerate(null);
    }
    boolean regenerate(CommandSender who) {
        World w = Bukkit.getWorld(world);
        Path template = getDataFolder().toPath().resolve("plantilla");
        if (regenerating) { if (who != null) who.sendMessage("Ya se esta regenerando."); return false; }
        if (w == null) { if (who != null) who.sendMessage("El mundo " + world + " no esta cargado."); return false; }
        regenerating = true;
        Path folder = w.getWorldFolder().toPath();
        for (Player p : w.getPlayers()) Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "spawn " + p.getName());
        Bukkit.broadcast(color("&dLas Cavernas de Cristal se estan regenerando..."));
        Bukkit.getScheduler().runTaskLater(this, () -> {
            try {
                for (Player p : w.getPlayers()) p.teleport(Bukkit.getWorlds().get(0).getSpawnLocation());
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv unload " + world);
                if (Bukkit.getWorld(world) != null) Bukkit.unloadWorld(world, false);
                if (Bukkit.getWorld(world) != null) throw new IOException("No se pudo descargar el mundo; no se borro nada");
                if (!folder.toAbsolutePath().normalize().startsWith(Bukkit.getWorldContainer().toPath().toAbsolutePath().normalize())
                    || world.equals(Bukkit.getWorlds().getFirst().getName())) throw new IOException("Ruta insegura");
                for (String sub : List.of("region", "entities", "poi")) {
                    Path target = folder.resolve(sub);
                    if (Files.isDirectory(target)) try (var s = Files.walk(target)) { s.sorted(Comparator.reverseOrder()).forEach(x -> x.toFile().delete()); }
                    Path from = template.resolve(sub);
                    if (Files.isDirectory(from)) { Files.createDirectories(target); try (var s = Files.list(from)) { for (Path f : s.toList()) Files.copy(f, target.resolve(f.getFileName()), StandardCopyOption.REPLACE_EXISTING); } }
                }
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv load " + world);
                if (Bukkit.getWorld(world) == null) Bukkit.createWorld(new WorldCreator(world).generator("AstralCavernas"));
                nextRegen = System.currentTimeMillis() + everyMs; getConfig().set("proxima-regeneracion", nextRegen); saveConfig();
                jefeMuerto.clear();
                Bukkit.broadcast(color("&aLas Cavernas de Cristal se regeneraron: vetas nuevas."));
            } catch (IOException ex) {
                getLogger().severe("No se pudo regenerar: " + ex);
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv load " + world);
            } finally { regenerating = false; }
        }, 40);
        return true;
    }

    // ------------------------------------------------------------------------------- entrada y comandos
    boolean puedeEntrar(Player p) {
        if (p.hasPermission(permTumba) || p.hasPermission("astral.cavernas.admin")) return true;
        List<ItemStack> todo = new ArrayList<>(Arrays.asList(p.getInventory().getContents()));
        for (ItemStack it : todo) { String c = comps(it); if (EQUIPO.matcher(c).find() && tier(c) >= 4) return true; }
        return false;
    }

    /** Densidad de menas en la franja que se pica (6 bloques de piso, paredes y techo) en un cuadrado de chunks. */
    void medir(CommandSender s, int chunks) {
        World w = Bukkit.getWorld(world);
        if (w == null || !(w.getGenerator() instanceof Gen g)) { s.sendMessage("Mundo no cargado."); return; }
        g.init(w.getSeed());
        long solidos = 0, cristal = 0, geoda = 0, gemas = 0;
        int cx0 = -chunks / 2, cz0 = -chunks / 2 - 10;
        for (int cx = cx0; cx < cx0 + chunks; cx++) for (int cz = cz0; cz < cz0 + chunks; cz++) {
            Chunk ch = w.getChunkAt(cx, cz);
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
                int wx = cx * 16 + x, wz = cz * 16 + z, f = g.floor(wx, wz), c = g.ceiling(wx, wz, f);
                for (int y = f - 6; y <= c + 6; y++) {
                    if (y > f && y < c) continue;
                    Block b = ch.getBlock(x, y, z);
                    if (!b.getType().isSolid() || b.getType() == Material.BEDROCK) continue;
                    solidos++;
                    int n = nota(b);
                    if (n == 14) cristal++; else if (n == 15) geoda++; else if (n >= 0) gemas++;
                }
            }
        }
        double dc = solidos == 0 ? 0 : (double) cristal / solidos, dg = solidos == 0 ? 0 : (double) geoda / solidos;
        double hora = 14_400 * (dc * precios.getOrDefault("cristal_caverna", 0d) + dg * precios.getOrDefault("geoda_estelar", 0d));
        String r = "MEDIR chunks=" + chunks * chunks + " solidos=" + solidos + " cristal=" + cristal + " geoda=" + geoda + " gemas=" + gemas
            + String.format(Locale.ROOT, " dens_cristal=%.5f dens_geoda=%.5f dens_gemas=%.5f plata_hora=%.0f", dc, dg, solidos == 0 ? 0 : (double) gemas / solidos, hora);
        s.sendMessage(r); getLogger().info(r);
    }

    /** Vistas previas desde el generador (sin generar chunks): planta 1 px = 2 bloques y dos cortes verticales. */
    void mapa(CommandSender s) throws IOException {
        Gen g = new Gen(); World w = Bukkit.getWorld(world);
        g.init(w != null ? w.getSeed() : 1L);
        int[][] col = {{163, 92, 255}, {47, 191, 106}, {224, 32, 74}, {47, 107, 255}, {90, 90, 110}};
        int n = radio;
        var planta = new java.awt.image.BufferedImage(n, n, java.awt.image.BufferedImage.TYPE_INT_RGB);
        for (int px = 0; px < n; px++) for (int pz = 0; pz < n; pz++) {
            int x = px * 2 - radio, z = pz * 2 - radio, f = g.floor(x, z);
            int[] c = col[zonaIdx(zona(x, z))];
            double k = Math.max(0.25, Math.min(1.2, 0.6 + f / 60.0));
            if (g.pilar(x, z)) k = 0.2;
            int rgb = enCampamento(x, z) ? 0xFFFFFF : zona(x, z).equals("zafiro") && f < LAGO_Y ? 0x2050C0 : ((int) Math.min(255, c[0] * k) << 16 | (int) Math.min(255, c[1] * k) << 8 | (int) Math.min(255, c[2] * k));
            planta.setRGB(px, pz, rgb);
        }
        Path dir = getDataFolder().toPath(); Files.createDirectories(dir);
        javax.imageio.ImageIO.write(planta, "png", dir.resolve("planta.png").toFile());
        for (String eje : List.of("x", "z")) {
            int alto = TECHO + 65;
            var corte = new java.awt.image.BufferedImage(radio * 2, alto, java.awt.image.BufferedImage.TYPE_INT_RGB);
            for (int i = -radio; i < radio; i++) {
                int x = eje.equals("x") ? i : campX, z = eje.equals("x") ? campZ / 2 : i;
                if (eje.equals("x")) z = 0;
                int f = g.floor(x, z), c = g.ceiling(x, z, f); boolean pil = g.pilar(x, z);
                int[] cl = col[zonaIdx(zona(x, z))];
                for (int y = -64; y <= TECHO; y++) {
                    int rgb;
                    if (y == -64 || y == TECHO) rgb = 0x111111;
                    else if (y <= f || y >= c || pil) rgb = (cl[0] / 2) << 16 | (cl[1] / 2) << 8 | cl[2] / 2;
                    else if (zona(x, z).equals("zafiro") && y <= LAGO_Y) rgb = 0x2050C0;
                    else rgb = 0xE8E8E8;
                    corte.setRGB(i + radio, TECHO - y, rgb);
                }
            }
            javax.imageio.ImageIO.write(corte, "png", dir.resolve("corte_" + eje + ".png").toFile());
        }
        s.sendMessage("MAPA listo en " + dir); getLogger().info("MAPA listo en " + dir);
    }

    @Override public boolean onCommand(CommandSender s, Command c, String label, String[] a) {
        String sub = a.length == 0 ? "estado" : a[0];
        boolean admin = s.hasPermission("astral.cavernas.admin");
        switch (sub) {
            case "entrar" -> {
                Player p = a.length > 1 && admin ? Bukkit.getPlayerExact(a[1]) : s instanceof Player q ? q : null;
                if (p == null) return true;
                World w = Bukkit.getWorld(world);
                if (w == null || regenerating) { p.sendMessage(color("&cLas Cavernas no estan disponibles ahora. Proba en un rato.")); return true; }
                if (!puedeEntrar(p)) { p.sendMessage(color("&cPara entrar tenes que haber ganado la &fTumba &co llevar equipo &ftier 4&c.")); return true; }
                p.teleport(new Location(w, campX + 0.5, campY + 1, campZ + 0.5));
                p.showTitle(net.kyori.adventure.title.Title.title(color("&d&lCavernas de Cristal"), color("&7Atril: comisiones · Barril: venta")));
                p.sendMessage(color("&dCavernas de Cristal&7: vetas de gemas con &ftaladro de Rubi&7 o mejor. Monstruos &ftier 4&7 (&ftier 5&7 en el Corazon). &f/spawn&7 para volver."));
            }
            case "comisiones" -> { if (s instanceof Player p) abrirComisiones(p); }
            case "vender" -> { if (s instanceof Player p && here(p.getWorld())) vender(p); }
            case "regenerar" -> { if (!admin) return false; s.sendMessage("Regenerando las Cavernas..."); regenerate(s); }
            case "plantilla" -> {
                if (!admin) return false;
                World w = Bukkit.getWorld(world); if (w == null) { s.sendMessage("Mundo no cargado."); return true; }
                w.save(); Path template = getDataFolder().toPath().resolve("plantilla");
                try {
                    for (String d : List.of("region", "entities", "poi")) {
                        Path from = w.getWorldFolder().toPath().resolve(d), to = template.resolve(d);
                        if (!Files.isDirectory(from)) continue; Files.createDirectories(to);
                        try (var st = Files.list(from)) { for (Path f : st.toList()) Files.copy(f, to.resolve(f.getFileName()), StandardCopyOption.REPLACE_EXISTING); }
                    }
                    s.sendMessage("Plantilla guardada en " + template);
                } catch (IOException ex) { s.sendMessage("Error: " + ex); }
            }
            case "jefe" -> {
                if (!admin || !(s instanceof Player p) || !here(p.getWorld())) return false;
                String z = a.length > 1 ? a[1] : zona(p.getLocation().getX(), p.getLocation().getZ());
                Location l = lugar(p, 6, 10); if (l != null && jefePorZona.containsKey(z)) aparecer(jefePorZona.get(z), l);
            }
            case "medir" -> { if (!admin) return false; medir(s, a.length > 1 ? Integer.parseInt(a[1]) : 6); }
            case "crear" -> {
                // Respaldo sin Multiverse (y ensayo local): crea o carga el mundo con este generador.
                if (!admin) return false;
                long t0 = System.currentTimeMillis();
                World w = Bukkit.getWorld(world) != null ? Bukkit.getWorld(world) : Bukkit.createWorld(new WorldCreator(world).generator("AstralCavernas"));
                s.sendMessage("CREAR " + (w != null) + " ms=" + (System.currentTimeMillis() - t0));
                getLogger().info("CREAR " + (w != null) + " ms=" + (System.currentTimeMillis() - t0));
            }
            case "mapa" -> { if (!admin) return false; try { mapa(s); } catch (IOException ex) { s.sendMessage("Error: " + ex); } }
            default -> {
                long left = Math.max(0, nextRegen - System.currentTimeMillis()) / 60000;
                s.sendMessage(color("&dCavernas de Cristal&7: se regeneran en " + (left / 60) + " h " + (left % 60) + " min."));
                if (s instanceof Player p && here(p.getWorld())) s.sendMessage(color("&7Estas en " + nombreZona.getOrDefault(zona(p.getLocation().getX(), p.getLocation().getZ()), "?") + "&7."));
            }
        }
        return true;
    }
}
