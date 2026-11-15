package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.command.*;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Portales del Nether (pedido del dueno 15/11/2026). Generado/compilado por portales.py.
 *
 * - Portal del Nether de portales_astrales -> llegada del Nether Hub (the_nether).
 * - Portal del Nether Hub -> llegada de portales_astrales (frente al portal grande).
 * - Portales fuera del Hub: como siempre (Nether <-> mundo survival). Si un portal del survival cayera dentro
 *   del Hub, la llegada se corre afuera para que no se creen portales ahi.
 * - Hub y zona del portal en portales_astrales: sin romper/poner bloques (salvo astral.admin.build),
 *   sin explosiones y sin mobs que aparezcan solos.
 * /astralportal hub|astral (OP): guarda la llegada donde esta parado.
 */
public final class AstralPortales extends JavaPlugin implements Listener, CommandExecutor {
    private record Caja(String mundo, int x1, int y1, int z1, int x2, int y2, int z2) {
        boolean dentro(Location l, int margen) {
            if (l.getWorld() == null || !nombre(l.getWorld()).equals(mundo)) return false;
            return l.getX() >= x1 - margen && l.getX() <= x2 + 1 + margen && l.getY() >= y1 - margen && l.getY() <= y2 + 1 + margen
                && l.getZ() >= z1 - margen && l.getZ() <= z2 + 1 + margen;
        }
    }
    private final List<Caja> protegidas = new ArrayList<>();
    private Caja hub, astral;

    @Override public void onEnable() {
        getConfig().options().copyDefaults(true);
        saveConfig();
        hub = caja(getConfig().getConfigurationSection("hub"));
        astral = caja(getConfig().getConfigurationSection("astral"));
        protegidas.add(hub); protegidas.add(astral);
        getServer().getPluginManager().registerEvents(this, this);
        Objects.requireNonNull(getCommand("astralportal")).setExecutor(this);
    }

    static String nombre(World w) { return w.getKey().toString(); }
    private static Caja caja(ConfigurationSection s) {
        List<Integer> a = s.getIntegerList("desde"), b = s.getIntegerList("hasta");
        return new Caja(s.getString("mundo"), Math.min(a.get(0), b.get(0)), Math.min(a.get(1), b.get(1)), Math.min(a.get(2), b.get(2)),
            Math.max(a.get(0), b.get(0)), Math.max(a.get(1), b.get(1)), Math.max(a.get(2), b.get(2)));
    }
    private Location llegada(String clave) {
        ConfigurationSection s = getConfig().getConfigurationSection(clave);
        NamespacedKey k = NamespacedKey.fromString(s.getString("mundo"));
        World w = k == null ? null : Bukkit.getWorld(k);
        if (w == null) return null;
        List<Double> p = s.getDoubleList("llegada");
        return new Location(w, p.get(0), p.get(1), p.get(2), p.get(3).floatValue(), p.get(4).floatValue());
    }

    @Override public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if (!(sender instanceof Player p) || !p.hasPermission("astral.admin.portales")) return true;
        if (args.length != 1 || !Set.of("hub", "astral").contains(args[0])) { p.sendMessage("§eUsa: /astralportal hub|astral (parado donde se aparece)"); return true; }
        Location l = p.getLocation();
        getConfig().set(args[0] + ".mundo", nombre(l.getWorld()));
        getConfig().set(args[0] + ".llegada", List.of(round(l.getX()), round(l.getY()), round(l.getZ()), round(l.getYaw()), round(l.getPitch())));
        saveConfig();
        p.sendMessage("§aLlegada de §f" + args[0] + " §aguardada aca.");
        return true;
    }
    private static double round(double v) { return Math.round(v * 100) / 100.0; }

    // ------------------------------------------------------------------ portales
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void portal(PlayerPortalEvent e) {
        if (e.getCause() != PlayerTeleportEvent.TeleportCause.NETHER_PORTAL) return;
        Location from = e.getFrom();
        String w = nombre(from.getWorld());
        Location destino = null;
        if (w.equals(astral.mundo())) destino = llegada("hub");
        else if (hub.dentro(from, 4)) destino = llegada("astral");
        if (destino != null) {
            e.setCancelled(true);
            Player p = e.getPlayer();
            Location d = destino;
            getServer().getScheduler().runTask(this, () -> { p.teleport(d); p.playSound(d, Sound.BLOCK_PORTAL_TRAVEL, 0.25f, 1.2f); });
            return;
        }
        // Del survival al Nether: nunca crear ni buscar portales dentro del Hub.
        Location to = e.getTo();
        if (to != null && hub.dentro(to, 24)) {
            to.setX(hub.x1() - 40);
            e.setTo(to);
        }
    }

    @EventHandler(ignoreCancelled = true)
    public void portalEntidad(EntityPortalEvent e) {
        if (nombre(e.getFrom().getWorld()).equals(astral.mundo()) || hub.dentro(e.getFrom(), 4)) e.setCancelled(true);
    }

    // ------------------------------------------------------------------ proteccion
    private boolean protegido(Location l) {
        for (Caja c : protegidas) if (c.dentro(l, 0)) return true;
        return false;
    }
    private boolean libre(Player p) { return p.hasPermission("astral.admin.build"); }
    @EventHandler(ignoreCancelled = true) public void romper(BlockBreakEvent e) { if (protegido(e.getBlock().getLocation()) && !libre(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void poner(BlockPlaceEvent e) { if (protegido(e.getBlock().getLocation()) && !libre(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void balde(PlayerBucketEmptyEvent e) { if (protegido(e.getBlock().getLocation()) && !libre(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void baldeLlenar(PlayerBucketFillEvent e) { if (protegido(e.getBlock().getLocation()) && !libre(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void fuego(BlockIgniteEvent e) {
        if (protegido(e.getBlock().getLocation()) && (e.getPlayer() == null || !libre(e.getPlayer()))
            && e.getCause() != BlockIgniteEvent.IgniteCause.FLINT_AND_STEEL) e.setCancelled(true);
        // Prender el portal con encendedor si se deja (lo usa el dueno); el fuego en el piso se apaga solo.
    }
    @EventHandler(ignoreCancelled = true) public void quema(BlockBurnEvent e) { if (protegido(e.getBlock().getLocation())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void explosion(EntityExplodeEvent e) { e.blockList().removeIf(b -> protegido(b.getLocation())); }
    @EventHandler(ignoreCancelled = true) public void explosionBloque(BlockExplodeEvent e) { e.blockList().removeIf(b -> protegido(b.getLocation())); }
    @EventHandler(ignoreCancelled = true) public void cambio(EntityChangeBlockEvent e) {
        if (!(e.getEntity() instanceof Player) && !(e.getEntity() instanceof FallingBlock) && protegido(e.getBlock().getLocation())) e.setCancelled(true);
    }
    @EventHandler(ignoreCancelled = true)
    public void mobs(CreatureSpawnEvent e) {
        switch (e.getSpawnReason()) {
            case CUSTOM, COMMAND, SPAWNER_EGG, SHOULDER_ENTITY, MOUNT -> { return; }   // NPC de MythicMobs, mascotas, admins
            default -> { if (protegido(e.getLocation())) e.setCancelled(true); }
        }
    }
    @EventHandler(ignoreCancelled = true)
    public void piston(BlockPistonExtendEvent e) { for (Block b : e.getBlocks()) if (protegido(b.getLocation())) { e.setCancelled(true); return; } }
}
