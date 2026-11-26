package astral;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.NamespacedKey;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.ConsoleCommandSender;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.*;

/**
 * Estadisticas de mazmorra (datapack-src/estadisticas_mazmorra.py, 26/11/2026). Pedido del dueno: al terminar la
 * mazmorra mostrar quien pego mas al jefe, quien mato mas mobs, quien cayo menos y quien curo mas.
 *
 * Liviano: solo suma numeros en un mapa cuando ya pasa un evento (golpe, muerte de mob) y solo en las copias que
 * estan en curso (entre `astralstats inicio <mundo>` y `astralstats fin <mundo>`, que manda astral_puntaje.sk).
 * No hay tareas repetidas. Las caidas las cuenta astral_puntaje.sk (`astralstats muerte <jugador>`), la curacion la
 * avisa la Varita de Curacion (AstralMesaMagia -> curacion(UUID, Player, double)).
 *
 * Danio de invocaciones (AstralClases, astral:invocacion_dueno) y mascotas domadas cuenta para el dueno.
 * Mientras `publico` es false el resumen solo lo ve `probadores` (regla del dueno: nada al publico sin su prueba).
 */
public final class AstralEstadisticas extends JavaPlugin implements Listener {
    static final class Num { double jefe, dano, cura; int mobs, caidas; }
    static final class Copia {
        final Map<UUID, Num> jugadores = new LinkedHashMap<>();
        final Map<UUID, UUID> ultimoGolpe = new HashMap<>();   // mob -> jugador (kills de invocaciones/flechas tardias)
        Num de(UUID id) { return jugadores.computeIfAbsent(id, k -> new Num()); }
    }
    private final Map<String, Copia> copias = new HashMap<>();
    private final Map<UUID, Boolean> cacheJefe = new HashMap<>();
    private final NamespacedKey kDueno = new NamespacedKey("astral", "invocacion_dueno");
    private List<String> tags = List.of();
    private Set<String> probadores = Set.of();
    private boolean publico;
    private int demora;

    @Override public void onEnable() {
        saveDefaultConfig();
        leer();
        getServer().getPluginManager().registerEvents(this, this);
    }

    private void leer() {
        reloadConfig();
        publico = getConfig().getBoolean("publico", false);
        probadores = new HashSet<>(getConfig().getStringList("probadores"));
        tags = getConfig().getStringList("etiquetas-jefe");
        demora = getConfig().getInt("demora-ticks", 100);
    }

    // ---------------- conteo ----------------

    private boolean jefe(LivingEntity e) {
        if (e instanceof Wither || e instanceof EnderDragon || e instanceof Warden || e instanceof ElderGuardian) return true;
        for (String t : tags) if (e.getScoreboardTags().contains(t)) return true;
        Boolean c = cacheJefe.get(e.getUniqueId());
        if (c != null) return c;
        boolean r = false;
        if (Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) {
            try { r = MM.barraDeJefe(e); } catch (Throwable ex) { r = false; }
        }
        if (cacheJefe.size() > 2000) cacheJefe.clear();
        cacheJefe.put(e.getUniqueId(), r);
        return r;
    }

    /** Jugador responsable del golpe: el mismo, el que tiro el proyectil, el dueno de la invocacion o de la mascota. */
    private UUID autor(Entity d) {
        if (d instanceof Player p) return p.getUniqueId();
        if (d instanceof Projectile pr && pr.getShooter() instanceof Entity s) d = s;
        else if (d instanceof AreaEffectCloud n && n.getSource() instanceof Entity s) d = s;
        else if (d instanceof TNTPrimed t && t.getSource() != null) d = t.getSource();
        if (d instanceof Player p) return p.getUniqueId();
        String s = d.getPersistentDataContainer().get(kDueno, PersistentDataType.STRING);
        if (s != null) try { return UUID.fromString(s); } catch (IllegalArgumentException ignored) { }
        if (d instanceof Tameable t && t.getOwner() != null) return t.getOwner().getUniqueId();
        return null;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void golpe(EntityDamageByEntityEvent ev) {
        if (!(ev.getEntity() instanceof LivingEntity e) || e instanceof Player || e instanceof ArmorStand) return;
        Copia c = copias.get(e.getWorld().getName());
        if (c == null) return;
        UUID id = autor(ev.getDamager());
        if (id == null) return;
        double real = Math.min(ev.getFinalDamage(), e.getHealth() + e.getAbsorptionAmount());
        if (real <= 0) return;
        Num n = c.de(id);
        n.dano += real;
        if (jefe(e)) n.jefe += real;
        c.ultimoGolpe.put(e.getUniqueId(), id);
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void muerte(EntityDeathEvent ev) {
        LivingEntity e = ev.getEntity();
        if (e instanceof Player) return;
        Copia c = copias.get(e.getWorld().getName());
        if (c == null) return;
        UUID id = c.ultimoGolpe.remove(e.getUniqueId());
        if (e.getKiller() != null) id = e.getKiller().getUniqueId();
        if (id != null) c.de(id).mobs++;
        cacheJefe.remove(e.getUniqueId());
    }

    /** Lo llama AstralMesaMagia (Varita de Curacion) con la vida que de verdad recupero el objetivo. */
    public void curacion(UUID fuente, Player objetivo, double cantidad) {
        if (fuente == null || objetivo == null || cantidad <= 0) return;
        Copia c = copias.get(objetivo.getWorld().getName());
        if (c != null) c.de(fuente).cura += cantidad;
    }

    // ---------------- resumen ----------------

    static String corto(double v) {
        if (v >= 1e9) return String.format(Locale.ROOT, "%.1fB", v / 1e9);
        if (v >= 1e6) return String.format(Locale.ROOT, "%.1fM", v / 1e6);
        if (v >= 1e4) return String.format(Locale.ROOT, "%.1fk", v / 1e3);
        return String.valueOf(Math.round(v));
    }
    static String c(String s) { return ChatColor.translateAlternateColorCodes('&', s); }

    private String nombre(UUID id) {
        var p = Bukkit.getOfflinePlayer(id);
        return p.getName() == null ? "?" : p.getName();
    }

    private void fin(String mundo) {
        Copia c = copias.remove(mundo);
        World w = Bukkit.getWorld(mundo);
        if (c == null || w == null) return;
        // Entran todos los que siguen en la copia (aunque no hayan pegado) y los que pegaron y siguen conectados en ella.
        for (Player p : w.getPlayers()) if (p.getGameMode() != org.bukkit.GameMode.CREATIVE || c.jugadores.containsKey(p.getUniqueId())) c.de(p.getUniqueId());
        c.jugadores.keySet().removeIf(id -> { Player p = Bukkit.getPlayer(id); return p == null || p.getWorld() != w; });
        if (c.jugadores.isEmpty()) return;
        List<String> lineas = resumen(c);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            World ww = Bukkit.getWorld(mundo);
            if (ww == null) return;
            for (Player p : ww.getPlayers()) {
                if (!publico && !probadores.contains(p.getName())) continue;
                for (String l : lineas) p.sendMessage(l);
            }
            getLogger().info("Resumen " + mundo + ": " + c.jugadores.entrySet().stream().map(en -> nombre(en.getKey()) + " jefe="
                    + corto(en.getValue().jefe) + " total=" + corto(en.getValue().dano) + " mobs=" + en.getValue().mobs + " caidas="
                    + en.getValue().caidas + " cura=" + corto(en.getValue().cura)).collect(java.util.stream.Collectors.joining(" | ")));
        }, demora);
    }

    private List<String> resumen(Copia c) {
        var lista = new ArrayList<>(c.jugadores.entrySet());
        lista.sort((a, b) -> Double.compare(b.getValue().jefe + b.getValue().dano * 1e-9, a.getValue().jefe + a.getValue().dano * 1e-9));
        List<String> out = new ArrayList<>();
        out.add(c("&8&m                                        "));
        out.add(c("&6&l  ✦ Estadisticas de la mazmorra"));
        for (var en : lista) {
            Num n = en.getValue();
            out.add(c("&f " + nombre(en.getKey()) + " &8» &c⚔ &f" + corto(n.jefe) + " &7jefe &8· &e🗡 &f" + corto(n.dano)
                    + " &7total &8· &a☠ &f" + n.mobs + " &7mobs &8· &4✖ &f" + n.caidas + " &7caidas"
                    + (n.cura > 0 ? " &8· &d❤ &f" + corto(n.cura) + " &7curado" : "")));
        }
        if (lista.size() >= 2) {
            out.add(c("&6  Premios:"));
            premio(out, lista, "&c⚔ Mas dano al jefe", n -> n.jefe, true, "");
            premio(out, lista, "&a☠ Mas mobs", n -> n.mobs, true, " mobs");
            premio(out, lista, "&4✖ Menos caidas", n -> n.caidas, false, " caidas");
            premio(out, lista, "&d❤ Mas curacion", n -> n.cura, true, "");
        }
        out.add(c("&8&m                                        "));
        return out;
    }

    private void premio(List<String> out, List<Map.Entry<UUID, Num>> lista, String titulo,
                        java.util.function.ToDoubleFunction<Num> f, boolean mayor, String unidad) {
        double mejor = mayor ? lista.stream().mapToDouble(e -> f.applyAsDouble(e.getValue())).max().orElse(0)
                             : lista.stream().mapToDouble(e -> f.applyAsDouble(e.getValue())).min().orElse(0);
        if (mayor && mejor <= 0) return;     // nadie curo: no se muestra
        var ganadores = lista.stream().filter(e -> f.applyAsDouble(e.getValue()) == mejor).map(e -> nombre(e.getKey())).toList();
        if (!mayor && ganadores.size() == lista.size()) {
            if (mejor == 0) out.add(c("   " + titulo + "&8: &fnadie cayo"));
            return;                          // empate de todos: no es premio
        }
        out.add(c("   " + titulo + "&8: &f" + String.join(", ", ganadores) + " &7(" + corto(mejor) + unidad + ")"));
    }

    // ---------------- comandos ----------------

    @Override public boolean onCommand(CommandSender s, Command cmd, String label, String[] a) {
        String sub = a.length > 0 ? a[0].toLowerCase(Locale.ROOT) : "";
        if (sub.equals("inicio") || sub.equals("fin") || sub.equals("muerte")) {
            if (!(s instanceof ConsoleCommandSender) || a.length < 2) return true;
            switch (sub) {
                case "inicio" -> copias.put(a[1], new Copia());
                case "fin" -> fin(a[1]);
                default -> {
                    Player p = Bukkit.getPlayerExact(a[1]);
                    if (p == null) return true;
                    Copia c = copias.get(p.getWorld().getName());
                    if (c != null) c.de(p.getUniqueId()).caidas++;
                }
            }
            return true;
        }
        if (!s.hasPermission("astral.estadisticas.admin")) return true;
        if (sub.equals("publico")) {
            if (a.length < 2) { s.sendMessage("Uso: /mazstats publico <si|no>"); return true; }
            getConfig().set("publico", a[1].equalsIgnoreCase("si") || a[1].equalsIgnoreCase("true"));
            saveConfig(); leer();
        } else if (sub.equals("recargar")) leer();
        else if (sub.equals("ver") && s instanceof Player p) {
            Copia c = copias.get(p.getWorld().getName());
            if (c == null) s.sendMessage("Esta copia no tiene una partida en curso.");
            else for (String l : resumen(c)) s.sendMessage(l);
            return true;
        }
        s.sendMessage(ChatColor.GOLD + "Estadisticas de mazmorra: " + ChatColor.WHITE + (publico ? "ABIERTO A TODOS" : "solo " + probadores)
                + ChatColor.GRAY + " | copias en curso: " + copias.size() + " | /mazstats ver | publico si|no");
        return true;
    }

    /** Aparte: si MythicMobs no esta, la clase principal igual registra sus eventos. */
    static final class MM {
        static boolean barraDeJefe(LivingEntity e) {
            return io.lumine.mythic.bukkit.MythicBukkit.inst().getMobManager().getActiveMob(e.getUniqueId())
                    .map(a -> a.getType().usesBossBar()).orElse(false);
        }
    }
}
