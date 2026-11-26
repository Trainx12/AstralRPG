package astral;

import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeModifier;
import org.bukkit.block.Biome;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.data.type.NoteBlock;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.player.*;
import org.bukkit.generator.BiomeProvider;
import org.bukkit.generator.ChunkGenerator;
import org.bukkit.generator.WorldInfo;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Vacio Estelar (plan E6 / 7f, datapack-src/vacio.py, 23/11/2026). Dimension de late game: islas flotantes en el
 * espacio, de noche siempre y con gravedad baja. Mismas gemas que las Cavernas pero en calidad Impecable, Perfecta
 * y Estelar. Lluvia de meteoritos cada 20-30 min (nucleo con gemas mejores y el Nucleo de Meteorito que invoca al
 * jefe en el altar de la isla central). Mobs tier 6 a 8 segun la distancia al centro.
 *
 * Vetas = bloque de nota en campanilla (chime 0-15): no usar ese estado para otra cosa.
 * Todo numero sale de config.yml (lo arma vacio.py).
 */
public final class AstralVacio extends JavaPlugin implements Listener {
    String world; int radio, celda, centroR, centroY, drillTier, mobsCerca, mobsTope, mobsTanda, guardianes, campamentoR, meteoroMin, meteoroMax, meteoroDura;
    long everyMs, nextRegen, proximoMeteoro; List<Integer> warnMinutes; boolean regenerating;
    double gravedad, salto, caidaSegura;
    final Map<String, Double> precios = new HashMap<>();
    final List<String> mobs = new ArrayList<>(); String voladorId;
    String jefe, permSantuario;
    final List<int[]> meteoro = new ArrayList<>();
    NamespacedKey kGrav, kSalto, kCaida;

    // ------------------------------------------------------------------------------- arranque
    @Override public void onEnable() {
        saveDefaultConfig();
        var c = getConfig();
        world = c.getString("mundo", "vacio_estelar");
        radio = c.getInt("radio", 600); celda = c.getInt("celda", 72); centroR = c.getInt("centro-radio", 34); centroY = c.getInt("centro-y", 92);
        drillTier = c.getInt("taladro-tier", 6);
        mobsCerca = c.getInt("mobs-cerca", 7); mobsTope = c.getInt("mobs-tope", 90); mobsTanda = c.getInt("mobs-tanda", 2);
        guardianes = c.getInt("meteoro-guardianes", 3); campamentoR = c.getInt("campamento-radio", 16); voladorId = c.getString("volador", "");
        meteoroMin = c.getInt("meteoro-min", 20); meteoroMax = c.getInt("meteoro-max", 30); meteoroDura = c.getInt("meteoro-dura-seg", 360);
        everyMs = c.getLong("regenerar-cada-horas", 72) * 3600_000L;
        warnMinutes = c.getIntegerList("avisos-minutos");
        nextRegen = c.getLong("proxima-regeneracion", 0);
        if (nextRegen == 0) { nextRegen = System.currentTimeMillis() + everyMs; c.set("proxima-regeneracion", nextRegen); saveConfig(); }
        gravedad = c.getDouble("gravedad-pct", -35) / 100; salto = c.getDouble("salto-pct", 20) / 100; caidaSegura = c.getDouble("caida-segura", 8);
        jefe = c.getString("jefe", "astral_vac_coloso"); permSantuario = c.getString("permiso-santuario", "astral.fragmento.corazon");
        mobs.addAll(c.getStringList("mobs"));
        ConfigurationSection pr = c.getConfigurationSection("precios");
        if (pr != null) for (String k : pr.getKeys(false)) precios.put(k, pr.getDouble(k));
        kGrav = new NamespacedKey(this, "gravedad"); kSalto = new NamespacedKey(this, "salto"); kCaida = new NamespacedKey(this, "caida");
        proximoMeteoro = System.currentTimeMillis() + minutosMeteoro();
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::clock, 20 * 30, 20 * 30);
        Bukkit.getScheduler().runTaskTimer(this, this::jugadoresTick, 20, 10);
        Bukkit.getScheduler().runTaskTimer(this, this::spawnTick, 60, 60);
        getLogger().info("Vacio Estelar: mundo " + world + ", " + mobs.size() + " mobs, jefe " + jefe);
    }

    @Override public ChunkGenerator getDefaultWorldGenerator(String worldName, String id) { return new Gen(this); }
    boolean here(World w) { return w != null && w.getName().equals(world); }
    long minutosMeteoro() { return (meteoroMin + new Random().nextInt(Math.max(1, meteoroMax - meteoroMin + 1))) * 60_000L; }
    static net.kyori.adventure.text.Component color(String s) { return net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer.legacyAmpersand().deserialize(s); }
    void aviso(Player p, String s) { p.sendActionBar(color("&5Vacio Estelar: &f" + s)); }
    boolean enCampamento(int x, int z) { return x * x + z * z <= 14 * 14; }
    /** Zona sin monstruos alrededor del campamento (bloques del centro). */
    boolean zonaSegura(Location l) { int x = l.getBlockX(), z = l.getBlockZ(); return x * x + z * z <= campamentoR * campamentoR; }

    // ------------------------------------------------------------------------------- generador
    /** Islas en una grilla: cada celda tiene (o no) una isla con centro, alto y radio al azar por semilla. */
    static final class Gen extends ChunkGenerator {
        final int celda, centroR, centroY, radio;
        Gen(AstralVacio p) { celda = p.celda; centroR = p.centroR; centroY = p.centroY; radio = p.radio; }

        record Isla(int x, int y, int z, int r, int gemaA, int gemaB, long semilla) { }

        Isla isla(long seed, int i, int j) {
            if (i == 0 && j == 0) return new Isla(0, centroY, 0, centroR, -1, -1, seed);
            Random r = new Random(seed * 341873128712L + i * 132897987541L + j * 9876543211L);
            if (r.nextDouble() > 0.72) return null;
            int x = i * celda + 12 + r.nextInt(celda - 24), z = j * celda + 12 + r.nextInt(celda - 24);
            if (Math.abs(x) > radio - 30 || Math.abs(z) > radio - 30 || x * x + z * z < (centroR + 30) * (centroR + 30)) return null;
            return new Isla(x, 66 + r.nextInt(56), z, 9 + r.nextInt(15), r.nextInt(7), r.nextInt(7), r.nextLong());
        }

        static double ruido(long s, int x, int z) {
            long h = s ^ (x * 73856093L) ^ (z * 19349663L);
            h = (h ^ (h >>> 13)) * 0x5bd1e995L;
            return ((h ^ (h >>> 15)) & 0xffff) / 65535.0;
        }

        static BlockData nota(int n) {
            return Bukkit.createBlockData(Material.NOTE_BLOCK, d -> { ((NoteBlock) d).setInstrument(Instrument.CHIME); ((NoteBlock) d).setNote(new Note(n)); });
        }

        @Override public void generateNoise(WorldInfo info, Random random, int cx, int cz, ChunkData data) {
            long seed = info.getSeed();
            int x0 = cx << 4, z0 = cz << 4;
            int i0 = Math.floorDiv(x0, celda), j0 = Math.floorDiv(z0, celda);
            BlockData[] notas = new BlockData[16];
            for (int n = 0; n < 16; n++) notas[n] = nota(n);
            for (int i = i0 - 1; i <= i0 + 1; i++) for (int j = j0 - 1; j <= j0 + 1; j++) {
                Isla is = isla(seed, i, j);
                if (is == null) continue;
                Random vr = new Random(is.semilla() ^ (cx * 31L + cz));
                for (int dx = 0; dx < 16; dx++) for (int dz = 0; dz < 16; dz++) {
                    int x = x0 + dx, z = z0 + dz;
                    double d = Math.hypot(x - is.x(), z - is.z());
                    double borde = is.r() * (0.85 + 0.3 * ruido(is.semilla(), x >> 2, z >> 2));
                    if (d > borde) continue;
                    double f = 1 - d / borde;
                    boolean central = is.gemaA() < 0;
                    int top = central ? is.y() : is.y() + (int) Math.round(2.5 * f);
                    int bottom = is.y() - (int) Math.round(is.r() * 1.3 * Math.pow(f, 0.7) * (0.75 + 0.5 * ruido(is.semilla() + 7, x, z)));
                    for (int y = bottom; y <= top; y++) {
                        Material m;
                        double q = vr.nextDouble();
                        if (y == top) m = central ? (d < 6 ? Material.PURPUR_BLOCK : Material.END_STONE_BRICKS) : (q < 0.15 ? Material.PURPUR_BLOCK : Material.END_STONE);
                        else if (central) m = Material.END_STONE;
                        else if (q < 0.010) { data.setBlock(dx, y, dz, notas[vr.nextBoolean() ? is.gemaA() : is.gemaB()]); continue; }
                        else if (q < 0.028) { data.setBlock(dx, y, dz, notas[14]); continue; }
                        else if (q < 0.045) m = Material.OBSIDIAN;
                        else if (q < 0.050) m = Material.CRYING_OBSIDIAN;
                        else if (q < 0.120) m = Material.PURPUR_BLOCK;
                        else m = Material.END_STONE;
                        data.setBlock(dx, y, dz, m);
                    }
                }
            }
            // Campamento (isla central): altar del jefe, barril de venta y faroles.
            if (cx == 0 && cz == 0 || cx == -1 && cz == 0 || cx == 0 && cz == -1 || cx == -1 && cz == -1) {
                int y = centroY;
                for (int x = -2; x <= 2; x++) for (int z = 8; z <= 12; z++) put(data, x0, z0, x, y, z, Material.CRYING_OBSIDIAN);
                put(data, x0, z0, 0, y + 1, 10, Material.LODESTONE);
                put(data, x0, z0, 3, y + 1, -3, Material.BARREL);
                for (int[] l : new int[][]{{6, 6}, {-6, 6}, {6, -6}, {-6, -6}}) {
                    put(data, x0, z0, l[0], y + 1, l[1], Material.END_ROD);
                    put(data, x0, z0, l[0], y, l[1], Material.SEA_LANTERN);
                }
            }
        }

        static void put(ChunkData data, int x0, int z0, int x, int y, int z, Material m) {
            int dx = x - x0, dz = z - z0;
            if (dx >= 0 && dx < 16 && dz >= 0 && dz < 16) data.setBlock(dx, y, dz, m);
        }

        @Override public BiomeProvider getDefaultBiomeProvider(WorldInfo info) {
            return new BiomeProvider() {
                @Override public Biome getBiome(WorldInfo i, int x, int y, int z) { return Biome.THE_END; }
                @Override public List<Biome> getBiomes(WorldInfo i) { return List.of(Biome.THE_END); }
            };
        }
        @Override public boolean shouldGenerateDecorations() { return false; }
        @Override public boolean shouldGenerateStructures() { return false; }
        @Override public boolean shouldGenerateMobs() { return false; }
        @Override public boolean shouldGenerateCaves() { return false; }
        @Override public boolean shouldGenerateSurface() { return false; }
        @Override public Location getFixedSpawnLocation(World w, Random random) { return new Location(w, 0.5, centroY + 1, 0.5); }
    }

    // ------------------------------------------------------------------------------- vetas
    static int nota(Block b) {
        if (b.getType() != Material.NOTE_BLOCK || !(b.getBlockData() instanceof NoteBlock n)) return -1;
        return n.getInstrument() == Instrument.CHIME && n.getNote().getId() <= 15 ? n.getNote().getId() : -1;
    }
    static final Pattern ID = Pattern.compile("[{,]\\s*id:\\s*\"([a-z0-9_]+)\""), TIER = Pattern.compile("tier:\\s*([0-9]+)"),
        DRILL = Pattern.compile("tool:\\s*\"drill\""), EQUIPO = Pattern.compile("type:\\s*\"(weapon|armor|staff)\""),
        AREA = Pattern.compile("area:\\s*([0-9]+)");
    static String comps(ItemStack it) { return it == null || !it.hasItemMeta() ? "" : it.getItemMeta().getAsComponentString(); }
    static String astralId(ItemStack it) { Matcher m = ID.matcher(comps(it)); return m.find() ? m.group(1) : ""; }
    static int tier(String c) { Matcher m = TIER.matcher(c); return m.find() ? Integer.parseInt(m.group(1)) : 0; }
    static int drillTier(ItemStack it) { String c = comps(it); return DRILL.matcher(c).find() ? tier(c) : 0; }
    boolean builder(Player p) { return p.getGameMode() == GameMode.CREATIVE && p.hasPermission("astral.vacio.editar"); }

    @EventHandler(ignoreCancelled = true) public void fisica(BlockPhysicsEvent e) { if (nota(e.getBlock()) >= 0 && here(e.getBlock().getWorld())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void explota(EntityExplodeEvent e) { if (here(e.getLocation().getWorld())) e.blockList().clear(); }

    // Fuera del Vacio un bloque de nota afinado como veta solo devuelve el bloque de nota.
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void falsa(BlockBreakEvent e) {
        if (here(e.getBlock().getWorld()) || nota(e.getBlock()) < 0) return;
        e.setDropItems(false);
        if (e.getPlayer().getGameMode() != GameMode.CREATIVE) e.getBlock().getWorld().dropItemNaturally(e.getBlock().getLocation().add(.5, .5, .5), new ItemStack(Material.NOTE_BLOCK));
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void picar(BlockBreakEvent e) {
        if (!here(e.getBlock().getWorld()) || builder(e.getPlayer())) return;
        Block b = e.getBlock();
        if (enCampamento(b.getX(), b.getZ()) && b.getY() >= centroY - 1) { e.setCancelled(true); aviso(e.getPlayer(), "el campamento no se rompe."); return; }
        if (nota(b) < 0) return;
        if (drillTier(e.getPlayer().getInventory().getItemInMainHand()) < drillTier) {
            e.setCancelled(true); aviso(e.getPlayer(), "las vetas estelares se pican con taladro tier " + drillTier + " o mejor.");
        }
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void poner(BlockPlaceEvent e) {
        if (!here(e.getBlock().getWorld()) || builder(e.getPlayer())) return;
        Block b = e.getBlock();
        if (b.getType() == Material.NOTE_BLOCK || enCampamento(b.getX(), b.getZ()) && b.getY() >= centroY - 1) { e.setCancelled(true); aviso(e.getPlayer(), "eso no se puede poner aca."); }
    }

    // Taladro en area: lo hace el plugin (el datapack no pica en el Vacio), como en las Cavernas.
    boolean rompiendo;
    static int[] rango(int n, boolean mas) {
        int lo = n % 2 == 1 ? -(n / 2) : mas ? -(n / 2 - 1) : -(n / 2);
        int[] r = new int[n]; for (int i = 0; i < n; i++) r[i] = lo + i; return r;
    }
    static org.bukkit.block.BlockFace cardinal(float yaw) {
        float y = ((yaw % 360) + 360) % 360;
        return y >= 45 && y < 135 ? org.bukkit.block.BlockFace.WEST : y >= 135 && y < 225 ? org.bukkit.block.BlockFace.NORTH
            : y >= 225 && y < 315 ? org.bukkit.block.BlockFace.EAST : org.bukkit.block.BlockFace.SOUTH;
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
        var f = cardinal(eye.getYaw());
        int fx = f.getModX(), fz = f.getModZ(), rx = -fz, rz = fx;
        List<int[]> offs = new ArrayList<>();
        if (Math.abs(eye.getPitch()) >= 50) {
            for (int u : rango(d[0], true)) for (int v : rango(d[1], true)) offs.add(new int[]{u * rx + v * fx, 0, u * rz + v * fz});
        } else {
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

    // ------------------------------------------------------------------------------- jugadores
    /** Gravedad baja, salto mas alto y caida segura mientras estan en el Vacio; caer al vacio vuelve al campamento. */
    void jugadoresTick() {
        World w = Bukkit.getWorld(world);
        for (Player p : Bukkit.getOnlinePlayers()) {
            boolean adentro = here(p.getWorld());
            modificar(p, Attribute.GRAVITY, kGrav, adentro ? gravedad : 0, AttributeModifier.Operation.ADD_SCALAR);
            modificar(p, Attribute.JUMP_STRENGTH, kSalto, adentro ? salto : 0, AttributeModifier.Operation.ADD_SCALAR);
            modificar(p, Attribute.SAFE_FALL_DISTANCE, kCaida, adentro ? caidaSegura : 0, AttributeModifier.Operation.ADD_NUMBER);
            if (adentro && w != null && p.getLocation().getY() < 0 && p.getGameMode() != GameMode.SPECTATOR) {
                p.setFallDistance(0);
                p.teleport(new Location(w, 0.5, centroY + 1, 0.5));
                p.showTitle(net.kyori.adventure.title.Title.title(color("&5Caiste al vacio"), color("&7Las estrellas te devolvieron al campamento")));
            }
        }
    }
    void modificar(Player p, Attribute at, NamespacedKey k, double v, AttributeModifier.Operation op) {
        var a = p.getAttribute(at);
        if (a == null) return;
        var old = a.getModifier(k);
        if (v == 0) { if (old != null) a.removeModifier(k); return; }
        if (old != null && old.getAmount() == v) return;
        if (old != null) a.removeModifier(k);
        a.addModifier(new AttributeModifier(k, v, op));
    }
    @EventHandler public void sale(PlayerQuitEvent e) {
        Player p = e.getPlayer();
        modificar(p, Attribute.GRAVITY, kGrav, 0, null); modificar(p, Attribute.JUMP_STRENGTH, kSalto, 0, null); modificar(p, Attribute.SAFE_FALL_DISTANCE, kCaida, 0, null);
    }

    // ------------------------------------------------------------------------------- venta (barril) y altar
    @EventHandler(priority = EventPriority.HIGH) public void tocar(PlayerInteractEvent e) {
        if (e.getHand() != EquipmentSlot.HAND || e.getAction() != Action.RIGHT_CLICK_BLOCK || e.getClickedBlock() == null || !here(e.getClickedBlock().getWorld())) return;
        Block b = e.getClickedBlock();
        if (!enCampamento(b.getX(), b.getZ())) return;
        if (b.getType() == Material.BARREL) { e.setCancelled(true); vender(e.getPlayer()); }
        else if (b.getType() == Material.LODESTONE) { e.setCancelled(true); altar(e.getPlayer(), b); }
    }

    void vender(Player p) {
        double total = 0; int n = 0;
        ItemStack[] cont = p.getInventory().getStorageContents();
        for (int i = 0; i < cont.length; i++) {
            Double precio = precios.get(astralId(cont[i]));
            if (precio == null) continue;
            total += precio * cont[i].getAmount(); n += cont[i].getAmount(); cont[i] = null;
        }
        if (n == 0) { p.sendMessage(color("&7El barril compra &dFragmentos Estelares &7y &bNucleos de Meteorito&7. No tenes ninguno.")); return; }
        p.getInventory().setStorageContents(cont);
        long plata = Math.round(total);
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "eco give " + p.getName() + " " + plata);
        p.sendMessage(color("&a✦ Vendiste " + n + " por &6" + String.format(Locale.ROOT, "%,d", plata).replace(',', '.') + "$&a."));
        p.playSound(p.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 1, 1);
        getLogger().info(p.getName() + " vendio " + n + " cosas del Vacio por " + plata);
    }

    void altar(Player p, Block b) {
        World w = b.getWorld();
        boolean vivo = w.getLivingEntities().stream().anyMatch(x -> x.getScoreboardTags().contains("vac.jefe"));
        if (vivo) { aviso(p, "el Coloso Estelar ya esta despierto."); return; }
        ItemStack mano = p.getInventory().getItemInMainHand();
        if (!"nucleo_meteorito".equals(astralId(mano))) { aviso(p, "el altar pide un Nucleo de Meteorito."); return; }
        mano.setAmount(mano.getAmount() - 1);
        Location l = b.getLocation().add(0.5, 2, 0.5);
        w.strikeLightningEffect(l);
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mm mobs spawn " + jefe + " 1 " + w.getName() + "," + l.getBlockX() + "," + l.getBlockY() + "," + l.getBlockZ());
        Bukkit.broadcast(color("&5✦ " + p.getName() + " desperto al &d&lColoso Estelar &5en el Vacio Estelar."));
        vidaJefe(w, 10); vidaJefe(w, 40);
    }

    /** La vida real del Coloso (30 x vida de referencia del tier 8). MythicMobs puede pisar la de vacio/jefe. */
    void vidaJefe(World w, long ticks) {
        double vida = getConfig().getDouble("jefe-vida", 0);
        if (vida <= 0) return;
        Bukkit.getScheduler().runTaskLater(this, () -> {
            for (LivingEntity j : w.getLivingEntities()) {
                if (!j.getScoreboardTags().contains("vac.jefe") || j.getScoreboardTags().contains("vac.vida")) continue;
                var mh = j.getAttribute(Attribute.MAX_HEALTH);
                if (mh == null) continue;
                mh.setBaseValue(vida); j.setHealth(vida); j.addScoreboardTag("vac.vida");
            }
        }, ticks);
    }

    // ------------------------------------------------------------------------------- mobs
    Location lugar(Player p, int minD, int maxD) {
        Random r = new Random(); World w = p.getWorld();
        for (int intento = 0; intento < 18; intento++) {
            double a = r.nextDouble() * Math.PI * 2; int d = minD + r.nextInt(maxD - minD + 1);
            int x = p.getLocation().getBlockX() + (int) (Math.cos(a) * d), z = p.getLocation().getBlockZ() + (int) (Math.sin(a) * d);
            if (Math.abs(x) > radio - 4 || Math.abs(z) > radio - 4 || x * x + z * z < campamentoR * campamentoR || !w.isChunkLoaded(x >> 4, z >> 4)) continue;
            int y0 = p.getLocation().getBlockY();
            for (int y = y0 + 12; y > y0 - 24; y--) {
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
    /** Lugar en el aire para el Ojo del Vacio (vuela): 8-16 bloques del jugador y 3-6 arriba. */
    Location aire(Player p) {
        Random r = new Random(); World w = p.getWorld();
        for (int i = 0; i < 8; i++) {
            double a = r.nextDouble() * Math.PI * 2; int d = 8 + r.nextInt(9);
            Location l = p.getLocation().clone().add(Math.cos(a) * d, 3 + r.nextInt(4), Math.sin(a) * d);
            if (Math.abs(l.getBlockX()) > radio - 4 || Math.abs(l.getBlockZ()) > radio - 4 || zonaSegura(l)) continue;
            if (!w.isChunkLoaded(l.getBlockX() >> 4, l.getBlockZ() >> 4)) continue;
            if (l.getBlock().isEmpty() && l.getBlock().getRelative(0, 1, 0).isEmpty()) return l;
        }
        return null;
    }
    /** Cada 3 s: hasta mobs-tanda monstruos por jugador (en el suelo de su isla o, el Ojo, en el aire), fuera del campamento. */
    void spawnTick() {
        World w = Bukkit.getWorld(world);
        if (w == null || regenerating || mobs.isEmpty() || !Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) return;
        long total = w.getLivingEntities().stream().filter(e -> e.getScoreboardTags().contains("vac.mob")).count();
        Random r = new Random();
        for (Player p : w.getPlayers()) {
            if (p.getGameMode() == GameMode.SPECTATOR || zonaSegura(p.getLocation())) continue;
            long cerca = p.getNearbyEntities(40, 24, 40).stream().filter(e -> e.getScoreboardTags().contains("vac.mob")).count();
            for (int k = 0; k < mobsTanda && cerca < mobsCerca && total < mobsTope; k++) {
                String id = mobs.get(r.nextInt(mobs.size()));
                Location l = id.equals(voladorId) ? aire(p) : lugar(p, 6, 24);
                if (l == null && !voladorId.isEmpty()) { id = voladorId; l = aire(p); }   // isla chica: viene volando
                if (l == null) break;
                aparecer(id, l); total++; cerca++;
            }
        }
    }

    // ------------------------------------------------------------------------------- meteoritos
    void clock() {
        if (regenerating) return;
        long ahora = System.currentTimeMillis();
        long left = nextRegen - ahora;
        for (int m : warnMinutes) { long at = m * 60_000L; if (left <= at && left > at - 30_000L) Bukkit.broadcast(color("&5El Vacio Estelar se regenera en &f" + m + (m == 1 ? " minuto" : " minutos") + "&5.")); }
        if (left <= 0) { regenerate(null); return; }
        World w = Bukkit.getWorld(world);
        if (!meteoro.isEmpty() && ahora > meteoroFin) limpiarMeteoro(w);
        if (ahora >= proximoMeteoro) {
            proximoMeteoro = ahora + minutosMeteoro();
            if (w != null && !w.getPlayers().isEmpty()) caerMeteoro(w, null);
        }
    }
    long meteoroFin;

    /** Elige una isla al azar (cerca de algun jugador) y deja caer un meteorito con su nucleo de vetas mejores. */
    void caerMeteoro(World w, Location donde) {
        Random r = new Random();
        Location l = donde;
        List<Player> ps = w.getPlayers();
        // Una isla al azar a 25-80 bloques de algun jugador (la superficie mas alta de esa columna).
        for (int i = 0; l == null && i < 60 && !ps.isEmpty(); i++) {
            Location pl = ps.get(r.nextInt(ps.size())).getLocation();
            double a = r.nextDouble() * Math.PI * 2; int d = 25 + r.nextInt(56);
            int x = pl.getBlockX() + (int) (Math.cos(a) * d), z = pl.getBlockZ() + (int) (Math.sin(a) * d);
            if (Math.abs(x) > radio - 10 || Math.abs(z) > radio - 10 || x * x + z * z < 20 * 20) continue;
            Block top = w.getHighestBlockAt(x, z);
            if (top.getY() > 20 && top.getType().isSolid()) l = top.getLocation().add(0.5, 1, 0.5);
        }
        if (l == null) return;
        limpiarMeteoro(w);
        final Location impacto = l.clone();
        Bukkit.broadcast(color("&5☄ &dUn meteorito cae en el Vacio Estelar &7(x " + impacto.getBlockX() + ", z " + impacto.getBlockZ() + ")&d. ¡El primero que llegue se lleva el nucleo!"));
        for (Player p : ps) p.playSound(p.getLocation(), Sound.ENTITY_WITHER_SPAWN, 0.6f, 1.6f);
        BlockDisplay roca = w.spawn(impacto.clone().add(0, 60, 0), BlockDisplay.class, d -> {
            d.setBlock(Material.MAGMA_BLOCK.createBlockData()); d.setPersistent(false);
            d.setTransformation(new org.bukkit.util.Transformation(new org.joml.Vector3f(-1.5f, -1.5f, -1.5f), new org.joml.AxisAngle4f(),
                new org.joml.Vector3f(3, 3, 3), new org.joml.AxisAngle4f()));
        });
        int[] paso = {0};
        Bukkit.getScheduler().runTaskTimer(this, t -> {
            paso[0]++;
            Location at = impacto.clone().add(0, 60 - paso[0] * 1.5, 0);
            roca.teleport(at);
            w.spawnParticle(Particle.FLAME, at, 30, 1, 1, 1, 0.05);
            w.spawnParticle(Particle.LARGE_SMOKE, at, 10, 1, 1, 1, 0.02);
            if (paso[0] >= 40) {
                t.cancel(); roca.remove();
                w.playSound(impacto, Sound.ENTITY_GENERIC_EXPLODE, 3f, 0.6f);
                w.spawnParticle(Particle.EXPLOSION_EMITTER, impacto, 3, 1, 1, 1, 0);
                crater(w, impacto, r);
                guardianes(impacto, r);
            }
        }, 1, 1);
    }

    void crater(World w, Location c, Random r) {
        int cx = c.getBlockX(), cy = c.getBlockY(), cz = c.getBlockZ();
        BlockData nucleo = Gen.nota(15);
        for (int x = -3; x <= 3; x++) for (int y = -2; y <= 3; y++) for (int z = -3; z <= 3; z++) {
            double d = Math.sqrt(x * x + y * y * 1.4 + z * z);
            if (d > 3.2) continue;
            Block b = w.getBlockAt(cx + x, cy + y, cz + z);
            if (!b.getType().isAir() && b.getType() != Material.END_STONE && b.getType() != Material.PURPUR_BLOCK && b.getType() != Material.OBSIDIAN) continue;
            BlockData m;
            if (d < 1.2) m = r.nextDouble() < 0.4 ? nucleo : Gen.nota(7 + r.nextInt(7));
            else if (d < 2.2) m = r.nextDouble() < 0.35 ? Gen.nota(7 + r.nextInt(7)) : Material.MAGMA_BLOCK.createBlockData();
            else m = (r.nextDouble() < 0.5 ? Material.OBSIDIAN : Material.BLACKSTONE).createBlockData();
            b.setBlockData(m, false);
            meteoro.add(new int[]{cx + x, cy + y, cz + z});
        }
        meteoroFin = System.currentTimeMillis() + meteoroDura * 1000L;
    }

    /** Monstruos que custodian el crater (aparecen al caer, alrededor del nucleo). */
    void guardianes(Location c, Random r) {
        if (mobs.isEmpty() || !Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) return;
        for (int i = 0; i < guardianes; i++) {
            double a = Math.PI * 2 * i / Math.max(1, guardianes);
            Location l = c.clone().add(Math.cos(a) * 5, 1, Math.sin(a) * 5);
            Block top = c.getWorld().getHighestBlockAt(l.getBlockX(), l.getBlockZ());
            if (top.getY() > 20 && Math.abs(top.getY() - c.getBlockY()) < 8) l = top.getLocation().add(0.5, 1, 0.5);
            String id = mobs.get(r.nextInt(mobs.size()));
            if (id.equals(voladorId)) l.add(0, 3, 0);
            aparecer(id, l);
        }
        c.getWorld().getPlayers().forEach(p -> { if (p.getLocation().distanceSquared(c) < 80 * 80) aviso(p, "monstruos custodian el meteorito."); });
    }

    void limpiarMeteoro(World w) {
        if (w != null) for (int[] p : meteoro) {
            Block b = w.getBlockAt(p[0], p[1], p[2]);
            if (b.getType() == Material.MAGMA_BLOCK || b.getType() == Material.BLACKSTONE || b.getType() == Material.OBSIDIAN || nota(b) >= 7) b.setType(Material.AIR, false);
        }
        meteoro.clear();
    }

    // ------------------------------------------------------------------------------- regeneracion
    boolean regenerate(CommandSender who) {
        World w = Bukkit.getWorld(world);
        if (regenerating) { if (who != null) who.sendMessage("Ya se esta regenerando."); return false; }
        if (w == null) { if (who != null) who.sendMessage("El mundo " + world + " no esta cargado."); return false; }
        regenerating = true;
        meteoro.clear();
        Path folder = w.getWorldFolder().toPath();
        for (Player p : w.getPlayers()) Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "spawn " + p.getName());
        Bukkit.broadcast(color("&5El Vacio Estelar se esta regenerando..."));
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
                }
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv load " + world);
                if (Bukkit.getWorld(world) == null) Bukkit.createWorld(new WorldCreator(world).generator("AstralVacio"));
                nextRegen = System.currentTimeMillis() + everyMs; getConfig().set("proxima-regeneracion", nextRegen); saveConfig();
                Bukkit.broadcast(color("&aEl Vacio Estelar se regenero: islas y vetas nuevas."));
            } catch (IOException ex) {
                getLogger().severe("No se pudo regenerar: " + ex);
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mv load " + world);
            } finally { regenerating = false; }
        }, 40);
        return true;
    }

    // ------------------------------------------------------------------------------- entrada y comandos
    boolean puedeEntrar(Player p) {
        if (p.hasPermission(permSantuario) || p.hasPermission("astral.vacio.admin")) return true;
        for (ItemStack it : p.getInventory().getContents()) { String c = comps(it); if (EQUIPO.matcher(c).find() && tier(c) >= 6) return true; }
        return false;
    }

    @EventHandler public void muere(EntityDeathEvent e) {
        if (!here(e.getEntity().getWorld()) || !e.getEntity().getScoreboardTags().contains("vac.jefe")) return;
        Player k = e.getEntity().getKiller();
        Bukkit.broadcast(color("&d✦ El Coloso Estelar cayo" + (k != null ? " ante &f" + k.getName() : "") + "&d."));
    }

    @Override public boolean onCommand(CommandSender s, Command c, String label, String[] a) {
        String sub = a.length == 0 ? "entrar" : a[0];
        boolean admin = s.hasPermission("astral.vacio.admin");
        switch (sub) {
            case "entrar" -> {
                Player p = a.length > 1 && admin ? Bukkit.getPlayerExact(a[1]) : s instanceof Player q ? q : null;
                if (p == null) return true;
                World w = Bukkit.getWorld(world);
                if (w == null || regenerating) { p.sendMessage(color("&cEl Vacio Estelar no esta disponible ahora. Proba en un rato.")); return true; }
                if (!puedeEntrar(p)) { p.sendMessage(color("&cPara entrar tenes que haber ganado el &fSantuario &co llevar equipo &ftier 6&c.")); return true; }
                p.teleport(new Location(w, 0.5, centroY + 1, 0.5));
                p.showTitle(net.kyori.adventure.title.Title.title(color("&5&lVacio Estelar"), color("&7Barril: venta · Altar: Coloso Estelar")));
                p.sendMessage(color("&5Vacio Estelar&7: vetas de gemas &fImpecables&7, &dPerfectas &7y &bEstelares &7con &ftaladro tier " + drillTier
                    + "&7. Monstruos &ftier 6 a 8&7 (mas lejos, mas fuertes). Meteoritos cada " + meteoroMin + "-" + meteoroMax + " min. &f/spawn&7 para volver."));
            }
            case "vender" -> { if (s instanceof Player p && here(p.getWorld())) vender(p); }
            case "meteorito" -> {
                if (!admin) return false;
                World w = Bukkit.getWorld(world); if (w == null) return true;
                caerMeteoro(w, null);
            }
            case "jefe" -> {
                if (!admin || !(s instanceof Player p) || !here(p.getWorld())) return false;
                Location l = lugar(p, 6, 10); if (l != null) { aparecer(jefe, l); vidaJefe(p.getWorld(), 10); }
            }
            case "regenerar" -> { if (!admin) return false; s.sendMessage("Regenerando el Vacio Estelar..."); regenerate(s); }
            case "crear" -> {
                if (!admin) return false;
                World w = Bukkit.getWorld(world) != null ? Bukkit.getWorld(world) : Bukkit.createWorld(new WorldCreator(world).generator("AstralVacio"));
                if (w != null) { w.setGameRule(GameRules.ADVANCE_TIME, false); w.setGameRule(GameRules.ADVANCE_WEATHER, false);
                    w.setGameRule(GameRules.SPAWN_MOBS, false); w.setTime(18000); w.getWorldBorder().setCenter(0, 0); w.getWorldBorder().setSize(radio * 2); }
                s.sendMessage("CREAR " + (w != null));
                getLogger().info("CREAR " + (w != null));
            }
            default -> {
                long left = Math.max(0, nextRegen - System.currentTimeMillis()) / 60000, met = Math.max(0, proximoMeteoro - System.currentTimeMillis()) / 60000;
                s.sendMessage(color("&5Vacio Estelar&7: se regenera en " + (left / 60) + " h " + (left % 60) + " min; proximo meteorito en ~" + met + " min."));
            }
        }
        return true;
    }

    @Override public List<String> onTabComplete(CommandSender s, Command c, String label, String[] a) {
        if (a.length != 1) return List.of();
        return s.hasPermission("astral.vacio.admin") ? List.of("entrar", "vender", "estado", "meteorito", "jefe", "regenerar", "crear") : List.of("entrar", "estado");
    }
}
