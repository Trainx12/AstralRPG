package astral;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scoreboard.*;
import org.bukkit.util.RayTraceResult;
import org.bukkit.util.Transformation;
import org.bukkit.util.Vector;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Efectos visuales con nivel por jugador (pedido del dueno 14-16/11/2026). Generado/compilado por efectos.py.
 *
 * Nivel en el score astral.fx: 0 Bajo (el juego como estaba), 1 Medio (default), 2 Alto.
 * - Particulas de golpe (damage_indicator): Bajo 3, Medio 6, Alto 12 por golpe (vanilla manda dano/2: millones).
 * - Bastones (marcador fx.rayo del datapack o /astralfx rayo): rayo laser continuo del color del baston con nucleo
 *   blanco, destellos en estrella y chispas; los de fuego tiran una bola de fuego con llamitas alrededor del mago.
 * - Impactos (fx.estallido) y golpes de jefes (/astralfx golpe): hongos de explosion en pixel art, manchas en el
 *   piso, llamitas que suben y medialunas. Medio ve una version liviana; Alto todo.
 * - Alto: rastro de armas, aura de armaduras con set completo y rastro de mascotas evolucionadas.
 * Los dibujos son item_display que solo ve quien tiene el nivel: si nadie tiene Medio/Alto cerca no se genera nada.
 */
public final class AstralEfectos extends JavaPlugin implements Listener, TabExecutor {
    static final String OBJ = "astral.fx";
    enum Categoria {
        ARMADURAS("armaduras", "armadura"), ARMAS("armas", "armas"), BASTONES("bastones", "bastones"),
        MASCOTAS("mascotas", "mascotas"), JEFES("jefes", "jefes");
        final String clave, objetivo;
        Categoria(String clave, String sufijo) { this.clave = clave; this.objetivo = "astral.fx." + sufijo; }
        static Categoria buscar(String clave) {
            for (Categoria c : values()) if (c.clave.equalsIgnoreCase(clave)) return c;
            return null;
        }
    }
    private final Map<UUID, EnumSet<Categoria>> categorias = new HashMap<>();
    static final int BAJO = 0, MEDIO = 1, ALTO = 2;
    static final int TOPE = 320, TOPE_ADORNO = 220;      // dibujos a la vez en todo el server
    static final int CRECE = 0, POP = 1, ACHICA = 2;
    static final Map<UUID, Integer> NIVEL = new ConcurrentHashMap<>();
    static final int[] GOLPE_PARTICULAS = {3, 6, 12};
    private static final Pattern ASTRAL = Pattern.compile("astral:\\{([^{}]*)\\}");
    private final Map<UUID, Location> ultimo = new HashMap<>();
    private final List<Fx> fxs = new ArrayList<>();
    private boolean prueba;
    private final Map<Integer, Color> colorTier = new HashMap<>();
    private final Map<String, Color> colorMascota = new HashMap<>();
    private final Map<String, String> auraSet = new HashMap<>();
    private final Map<String, Color> colorSet = new HashMap<>();
    private final Map<String, Integer> cuadros = new HashMap<>();

    /** Un dibujo vivo: cuadro, tamano y movimiento se calculan por tick y el cliente interpola. */
    private static final class Fx {
        ItemDisplay e; Categoria categoria; int min, max; String modelo; Color col;
        int edad, vida, cuadros = 1, cuadro = -1, curva = CRECE;
        float s0, s1, grav, largo;
        boolean ciclo, base, rayo;
        final Vector3f pos = new Vector3f(), vel = new Vector3f();
        Quaternionf rot = new Quaternionf();
    }

    @Override public void onEnable() {
        saveResource("config.yml", true);     // la config sale del generador: siempre la del jar (cuadros, colores)
        reloadConfig();
        var c = getConfig();
        ConfigurationSection s = c.getConfigurationSection("color-tier");
        if (s != null) for (String k : s.getKeys(false)) colorTier.put(Integer.parseInt(k), hex(s.getString(k)));
        s = c.getConfigurationSection("color-mascota");
        if (s != null) for (String k : s.getKeys(false)) colorMascota.put(k, hex(s.getString(k)));
        s = c.getConfigurationSection("aura-set");
        if (s != null) for (String k : s.getKeys(false)) auraSet.put(k, s.getString(k));
        s = c.getConfigurationSection("color-set");
        if (s != null) for (String k : s.getKeys(false)) colorSet.put(k, hex(s.getString(k)));
        s = c.getConfigurationSection("cuadros");
        if (s != null) for (String k : s.getKeys(false)) cuadros.put(k, s.getInt(k));
        objetivo();
        getServer().getPluginManager().registerEvents(this, this);
        Objects.requireNonNull(getCommand("efectos")).setExecutor(this);
        Objects.requireNonNull(getCommand("astralfx")).setExecutor(this);
        for (Player p : Bukkit.getOnlinePlayers()) leer(p);
        getServer().getScheduler().runTaskTimer(this, () -> { for (Player p : Bukkit.getOnlinePlayers()) leer(p); }, 40, 40);
        getServer().getScheduler().runTaskTimer(this, this::animar, 1, 1);
        getServer().getScheduler().runTaskTimer(this, this::rastros, 7, 4);
        if (getServer().getPluginManager().isPluginEnabled("packetevents")) AstralEfectosParticulas.registrar();
        else getLogger().warning("Sin PacketEvents: no se limitan las particulas de golpe (un golpe enorme puede colgar clientes)");
    }

    @Override public void onDisable() {
        for (Fx f : fxs) if (f.e.isValid()) f.e.remove();
        fxs.clear();
    }

    // ------------------------------------------------------------------ nivel por jugador
    private Objective objetivo() {
        return objetivo(OBJ);
    }
    private Objective objetivo(String nombre) {
        Scoreboard sb = Bukkit.getScoreboardManager().getMainScoreboard();
        Objective o = sb.getObjective(nombre);
        if (o == null) o = sb.registerNewObjective(nombre, Criteria.DUMMY, net.kyori.adventure.text.Component.text("Efectos"));
        return o;
    }
    private int leer(Player p) {
        Score sc = objetivo().getScore(p.getName());
        if (!sc.isScoreSet()) sc.setScore(MEDIO);   // pedido del dueno: los jugadores arrancan en Medio
        int n = Math.max(BAJO, Math.min(ALTO, sc.getScore()));
        NIVEL.put(p.getUniqueId(), n);
        EnumSet<Categoria> activas = EnumSet.noneOf(Categoria.class);
        for (Categoria c : Categoria.values()) {
            Score score = objetivo(c.objetivo).getScore(p.getName());
            if (!score.isScoreSet()) score.setScore(1);
            if (score.getScore() != 0) activas.add(c);
        }
        categorias.put(p.getUniqueId(), activas);
        actualizarVisibilidad(p);
        return n;
    }
    private boolean activada(Player p, Categoria c) {
        return categorias.getOrDefault(p.getUniqueId(), EnumSet.allOf(Categoria.class)).contains(c);
    }
    private void actualizarVisibilidad(Player p) {
        for (Fx f : fxs) {
            if (f.e.isValid() && f.e.getWorld() == p.getWorld() && nivel(p) >= f.min && nivel(p) <= f.max
                    && activada(p, f.categoria) && p.getLocation().distanceSquared(f.e.getLocation()) < 64 * 64)
                p.showEntity(this, f.e);
            else p.hideEntity(this, f.e);
        }
    }
    static int nivel(Player p) { return NIVEL.getOrDefault(p.getUniqueId(), MEDIO); }
    @EventHandler public void entra(PlayerJoinEvent e) { leer(e.getPlayer()); }
    @EventHandler public void sale(PlayerQuitEvent e) { NIVEL.remove(e.getPlayer().getUniqueId()); categorias.remove(e.getPlayer().getUniqueId()); ultimo.remove(e.getPlayer().getUniqueId()); }

    private static final String[] NOMBRE = {"Bajo", "Medio", "Alto"};
    private static final String[] DESC = {
        "el juego como siempre: sin efectos nuevos y solo 3 particulas por golpe",
        "rayos y bolas de fuego de los bastones, y explosiones chicas en impactos y jefes",
        "todo: rayos gruesos con destellos, explosiones grandes, rastros, auras y mascotas"};

    @Override public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if (cmd.getName().equals("astralfx")) return astralfx(sender, args);
        if (!(sender instanceof Player p)) return true;
        Categoria categoria = args.length > 0 ? Categoria.buscar(args[0]) : null;
        if (categoria != null) {
            if (args.length > 2 || (args.length == 2 && !List.of("on", "off").contains(args[1].toLowerCase(Locale.ROOT)))) {
                p.sendMessage("§cUsa: /efectos " + categoria.clave + " [on|off]"); return true;
            }
            leer(p);
            boolean activo = args.length == 1 ? !activada(p, categoria) : args[1].equalsIgnoreCase("on");
            objetivo(categoria.objetivo).getScore(p.getName()).setScore(activo ? 1 : 0);
            leer(p);
            p.sendMessage("§d✦ Efectos de " + categoria.clave + ": " + (activo ? "§aACTIVADO (true)" : "§cDESACTIVADO (false)"));
            return true;
        }
        if (args.length > 0) {
            int n = switch (args[0].toLowerCase(Locale.ROOT)) { case "bajo" -> 0; case "medio" -> 1; case "alto" -> 2; default -> -1; };
            if (n < 0 || args.length != 1) { p.sendMessage("§cUsa: /efectos bajo, medio o alto"); return true; }
            objetivo().getScore(p.getName()).setScore(n);
            leer(p);
            p.sendMessage("§d✦ Efectos: §f" + NOMBRE[n] + " §7(" + DESC[n] + ")");
            p.playSound(p.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.4f);
            return true;
        }
        int actual = leer(p);
        p.sendMessage("§d§l✦ Efectos visuales ✦ §7(ahora: §f" + NOMBRE[actual] + "§7)");
        for (int i = 0; i < 3; i++) {
            var linea = net.kyori.adventure.text.Component.text((i == actual ? "§a▶ " : "§7▷ ") + "§f" + NOMBRE[i] + " §8- §7" + DESC[i])
                .clickEvent(net.kyori.adventure.text.event.ClickEvent.runCommand("/efectos " + NOMBRE[i].toLowerCase(Locale.ROOT)));
            p.sendMessage(linea);
        }
        for (Categoria c : Categoria.values()) {
            p.sendMessage(net.kyori.adventure.text.Component.text("§d✦ " + c.clave + ": " +
                (activada(p, c) ? "§aACTIVADO (true)" : "§cDESACTIVADO (false)"))
                .clickEvent(net.kyori.adventure.text.event.ClickEvent.runCommand("/efectos " + c.clave)));
        }
        return true;
    }
    @Override public List<String> onTabComplete(CommandSender s, Command cmd, String label, String[] args) {
        if (cmd.getName().equals("efectos") && args.length == 1) return List.of("bajo", "medio", "alto", "armaduras", "armas", "bastones", "mascotas", "jefes");
        if (cmd.getName().equals("efectos") && args.length == 2 && Categoria.buscar(args[0]) != null) return List.of("on", "off");
        if (cmd.getName().equals("astralfx") && args.length == 1) return List.of("golpe", "estallido", "rayo", "estela");
        return List.of();
    }

    // ------------------------------------------------------------------ efectos por comando y marcadores
    private boolean astralfx(CommandSender sender, String[] a) {
        if (sender instanceof Player p && !p.hasPermission("astral.admin.efectos")) return true;
        if (a.length == 2 && a[0].equals("prueba") && !(sender instanceof Player)) {
            prueba = a[1].equals("on");                       // ensayo sin jugadores: genera igual los dibujos
            sender.sendMessage("astralfx prueba=" + prueba + " dibujos=" + fxs.size());
            return true;
        }
        if (a.length < 5) {
            sender.sendMessage("astralfx golpe|estallido <mundo> <x> <y> <z> [color] [radio] [elemento]");
            sender.sendMessage("astralfx rayo <mundo> <x> <y> <z> <x2> <y2> <z2> [color] [elemento]");
            return true;
        }
        World w = mundo(a[1]);
        if (w == null) return true;
        try {
            Location at = new Location(w, Double.parseDouble(a[2]), Double.parseDouble(a[3]), Double.parseDouble(a[4]));
            if (a[0].equals("rayo")) {
                if (a.length < 8) return true;
                Location fin = new Location(w, Double.parseDouble(a[5]), Double.parseDouble(a[6]), Double.parseDouble(a[7]));
                disparo(Categoria.BASTONES, at, fin, a.length > 8 ? hex(a[8]) : Color.fromRGB(0xD24BFF), a.length > 9 ? a[9] : "arcano", null);
                return true;
            }
            Color col = a.length > 5 ? hex(a[5]) : Color.fromRGB(0x7CFF5A);
            double radio = 4;
            if (a.length > 6) try { radio = Double.parseDouble(a[6]); } catch (NumberFormatException ignored) {}
            String elem = a.length > 7 ? a[7] : "";
            if (a[0].equals("estela")) estela(Categoria.JEFES, at, col, elem);
            else if (a[0].equals("golpe")) golpe(Categoria.JEFES, at, col, radio, elem); else estallido(Categoria.JEFES, at, col, (float) Math.max(0.6, Math.min(3, radio)), elem);
        } catch (NumberFormatException ignored) {}
        return true;
    }
    private static World mundo(String n) {
        World w = Bukkit.getWorld(n);
        if (w != null) return w;
        NamespacedKey k = NamespacedKey.fromString(n.contains(":") ? n : "minecraft:" + n);
        return k == null ? null : Bukkit.getWorld(k);
    }

    @EventHandler(ignoreCancelled = true)
    public void marcador(EntitySpawnEvent e) {
        if (!(e.getEntity() instanceof Marker m) || !m.getScoreboardTags().contains("astral.fx")) return;
        String tipo = null, elem = ""; Color col = Color.WHITE;
        for (String t : m.getScoreboardTags()) {
            if (t.startsWith("fx.")) tipo = t.substring(3);
            if (t.startsWith("fxc.")) col = hex(t.substring(4));
            if (t.startsWith("fxe.")) elem = t.substring(4);
        }
        Location at = e.getLocation();
        String tf = tipo, ef = elem; Color cf = col;
        getServer().getScheduler().runTask(this, () -> {
            m.remove();
            if ("golpe".equals(tf)) golpe(Categoria.JEFES, at, cf, 4, ef);
            else if ("estallido".equals(tf)) estallido(Categoria.BASTONES, at, cf, 1f, ef);
            else if ("rayo".equals(tf)) rayoDeBaston(at, cf, ef);
        });
    }

    // ------------------------------------------------------------------ bastones: rayo laser y bola de fuego
    /** El datapack deja el marcador frente a los ojos de quien lanza: se busca al mago y hasta donde llega. */
    private void rayoDeBaston(Location marca, Color col, String elem) {
        Player mago = null; double mejor = 9;
        for (Player p : marca.getWorld().getPlayers()) {
            double d = p.getEyeLocation().distanceSquared(marca);
            if (d < mejor) { mejor = d; mago = p; }
        }
        if (mago == null || !hayVisor(Categoria.BASTONES, marca, MEDIO)) return;
        Location ojos = mago.getEyeLocation();
        Vector dir = ojos.getDirection();
        Player yo = mago;
        RayTraceResult r = ojos.getWorld().rayTrace(ojos, dir, 25, FluidCollisionMode.NEVER, true, 0.45,
            x -> x instanceof LivingEntity && x != yo && !x.isInvulnerable() && !x.getScoreboardTags().contains("astral.pet") && !(x instanceof ArmorStand) && !(x instanceof Player pl && pl.getGameMode() == GameMode.SPECTATOR));
        Location fin = r == null ? ojos.clone().add(dir.clone().multiply(25)) : r.getHitPosition().toLocation(ojos.getWorld());
        // Sale de la punta del baston (a la derecha y abajo de la vista), no del medio de la pantalla.
        Vector der = dir.clone().crossProduct(new Vector(0, 1, 0));
        if (der.lengthSquared() < 1e-4) der = new Vector(1, 0, 0);
        Location boca = ojos.clone().add(dir.clone().multiply(0.9)).add(der.normalize().multiply(0.36)).add(0, -0.28, 0);
        disparo(Categoria.BASTONES, boca, fin, col, elem, mago);
    }

    void disparo(Categoria categoria, Location desde, Location hasta, Color col, String elem, Player mago) {
        Vector d = hasta.toVector().subtract(desde.toVector());
        double len = d.length();
        if (len < 0.3 || !hayVisor(categoria, desde, MEDIO)) return;
        d.multiply(1 / len);
        if ("fuego".equals(elem)) bolaDeFuego(categoria, desde, d, len, col, mago); else laser(categoria, desde, d, len, col, elem);
    }

    /** Rayo continuo: halo del color con nucleo blanco que se afina, destellos en estrella y chispas del color. */
    private void laser(Categoria categoria, Location desde, Vector dir, double len, Color col, String elem) {
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        for (int nv = MEDIO; nv <= ALTO; nv++) {
            if (!hayVisorExacto(categoria, desde, nv)) continue;
            float grosor = (nv == ALTO ? 0.55f : 0.3f) * ("luz".equals(elem) ? 1.35f : 1f);
            int dura = nv == ALTO ? 9 : 6;
            if ("rayo".equals(elem)) {                       // electrico: tramos quebrados en zigzag
                int tramos = (int) Math.max(3, Math.min(nv == ALTO ? 9 : 5, len / 2.5));
                Location a = desde.clone();
                for (int i = 1; i <= tramos; i++) {
                    Location b = desde.clone().add(dir.clone().multiply(len * i / tramos));
                    if (i < tramos) b.add(rnd.nextDouble(-.55, .55), rnd.nextDouble(-.45, .45), rnd.nextDouble(-.55, .55));
                    if (tramo(categoria, a, b, col, grosor * 0.8f, dura, nv) == null) return;
                    a = b;
                }
            } else {
                if (tramo(categoria, desde, desde.clone().add(dir.clone().multiply(len)), col, grosor, dura, nv) == null) return;
                if (nv == ALTO && "vacio".equals(elem))     // vacio: un segundo rayo oscuro que tarda mas en irse
                    tramo(categoria, desde, desde.clone().add(dir.clone().multiply(len)), Color.fromRGB(0x2A1048), grosor * 1.5f, dura + 5, nv);
            }
            int estrellas = nv == ALTO ? (int) Math.min(11, 4 + len / 2.2) : 2;
            for (int i = 0; i < estrellas; i++) {            // destellos blancos sobre el rayo
                double t = i == 0 ? 0.02 : rnd.nextDouble();
                Location l = desde.clone().add(dir.clone().multiply(len * t)).add(rnd.nextDouble(-.4, .4), rnd.nextDouble(-.4, .4), rnd.nextDouble(-.4, .4));
                Fx s = fx(categoria, l, "estrella", Color.WHITE, 0, (float) rnd.nextDouble(.45, i == 0 ? 1.3 : .95), rnd.nextInt(6, 12), nv, nv, true);
                if (s == null) break;
                s.curva = POP; s.cuadros = 3; s.edad = -rnd.nextInt(0, 5);
            }
            if (nv < ALTO) continue;
            int chispas = (int) Math.min(12, 5 + len / 2);     // chispas del color que se abren y caen
            for (int i = 0; i < chispas; i++) {
                Location l = desde.clone().add(dir.clone().multiply(len * rnd.nextDouble()));
                Fx s = fx(categoria, l, "estrella", col, .35f, .12f, rnd.nextInt(8, 16), nv, nv, true);
                if (s == null) break;
                s.curva = ACHICA; s.cuadros = 1; s.cuadro = 1; s.e.setItemStack(item("estrella", 1, col));
                s.vel.set((float) rnd.nextDouble(-.06, .06), (float) rnd.nextDouble(-.01, .07), (float) rnd.nextDouble(-.06, .06));
                s.grav = 0.006f;
            }
        }
        particula(categoria, desde, MEDIO, Particle.DUST, 6, 0.15, 0.15, 0.15, 0, new Particle.DustOptions(col, 1.2f));
        particula(categoria, desde, ALTO, Particle.END_ROD, 4, 0.1, 0.1, 0.1, 0.05, null);
        for (int i = 1; i <= 3; i++)                          // el elemento acompana al rayo (copos, burbujas, hojas...)
            elemento(categoria, desde.clone().add(dir.clone().multiply(len * i / 4.0)), elem, i == 2 ? MEDIO : ALTO, Math.min(1.2, len / 8), 5);
    }

    /** Un tramo recto de rayo entre dos puntos. */
    private Fx tramo(Categoria categoria, Location a, Location b, Color col, float grosor, int vida, int nv) {
        Vector d = b.toVector().subtract(a.toVector());
        double len = d.length();
        if (len < 0.05) return null;
        d.multiply(1 / len);
        Fx f = fx(categoria, a, "rayo", col, grosor, 0.04f, vida, nv, nv, false);
        if (f == null) return null;
        f.rayo = true; f.largo = (float) len;
        f.rot = new Quaternionf().rotationTo(new Vector3f(0, 0, 1), new Vector3f((float) d.getX(), (float) d.getY(), (float) d.getZ()));
        f.pos.set((float) (d.getX() * len / 2), (float) (d.getY() * len / 2), (float) (d.getZ() * len / 2));
        f.e.setBillboard(Display.Billboard.FIXED);
        aplicar(f, f.s0);
        return f;
    }

    /** Bola de fuego que vuela hasta el blanco dejando llamitas, y llamitas en el piso alrededor del mago. */
    private void bolaDeFuego(Categoria categoria, Location desde, Vector dir, double len, Color col, Player mago) {
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        int viaje = (int) Math.max(3, Math.min(10, len / 2.4));
        for (int nv = MEDIO; nv <= ALTO; nv++) {
            if (!hayVisorExacto(categoria, desde, nv)) continue;
            Fx b = fx(categoria, desde, "bola", col, nv == ALTO ? 1.5f : 0.9f, nv == ALTO ? 2.1f : 1.2f, viaje + 1, nv, nv, false);
            if (b == null) return;
            b.ciclo = true; b.cuadros = n("bola");
            b.vel.set((float) (dir.getX() * len / viaje), (float) (dir.getY() * len / viaje), (float) (dir.getZ() * len / viaje));
            Fx fogonazo = fx(categoria, desde, "estrella", Color.WHITE, 0, nv == ALTO ? 1.6f : 1f, 6, nv, nv, true);   // destello al salir
            if (fogonazo != null) { fogonazo.curva = POP; fogonazo.cuadros = 3; }
            if (nv < ALTO) continue;
            int estela = (int) Math.min(9, 2 + len / 2);
            for (int i = 1; i <= estela; i++) {             // llamitas que quedan flotando detras de la bola
                Location l = desde.clone().add(dir.clone().multiply(len * i / (estela + 1.0))).add(rnd.nextDouble(-.2, .2), rnd.nextDouble(-.2, .2), rnd.nextDouble(-.2, .2));
                Fx s = llamita(categoria, l, col, (float) rnd.nextDouble(.35, .6), rnd.nextInt(8, 14), nv);
                if (s == null) break;
                s.edad = -(viaje * i / (estela + 1));
                s.vel.set(0, 0.03f, 0);
            }
            if (mago != null) {
                Location pies = mago.getLocation();
                for (int i = 0; i < 12; i++) {              // llamitas en el piso alrededor del mago
                    double ang = Math.PI * 2 * i / 12 + rnd.nextDouble(.5), rr = rnd.nextDouble(1.0, 2.4);
                    Location l = piso(pies.clone().add(Math.cos(ang) * rr, 0.6, Math.sin(ang) * rr), 2.5);
                    if (l == null) continue;
                    Fx s = llamita(categoria, l, col, (float) rnd.nextDouble(.45, .8), rnd.nextInt(14, 24), nv);
                    if (s == null) break;
                    s.base = true; s.edad = -rnd.nextInt(0, 4);
                    s.e.setBillboard(Display.Billboard.VERTICAL);
                }
            }
        }
        if (mago != null) particula(categoria, mago.getLocation().add(0, 0.2, 0), MEDIO, Particle.FLAME, 8, 1.2, 0.1, 1.2, 0.01, null);
        Location fin = desde.clone().add(dir.clone().multiply(len));
        getServer().getScheduler().runTaskLater(this, () -> incendio(categoria, fin, col, 1f), viaje);
        for (int i = 0; i <= viaje; i++) {
            Location l = desde.clone().add(dir.clone().multiply(len * i / viaje));
            int espera = i;
            getServer().getScheduler().runTaskLater(this, () -> {
                particula(categoria, l, MEDIO, Particle.FLAME, 3, 0.12, 0.12, 0.12, 0.01, null);
                particula(categoria, l, ALTO, Particle.SMALL_FLAME, 3, 0.2, 0.2, 0.2, 0.02, null);
            }, espera);
        }
    }

    /** Donde cae el fuego: onda, corona de llamas grandes en el piso, brasas que suben y humo. */
    private void incendio(Categoria categoria, Location at, Color col, float escala) {
        if (!hayVisor(categoria, at, MEDIO)) return;
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        Location suelo = piso(at, 4);
        particula(categoria, at, MEDIO, Particle.FLAME, 20, 0.5, 0.4, 0.5, 0.06, null);
        particula(categoria, at, MEDIO, Particle.LAVA, 4, 0.4, 0.2, 0.4, 0, null);
        particula(categoria, at, ALTO, Particle.LARGE_SMOKE, 8, 0.6, 0.6, 0.6, 0.02, null);
        if (suelo == null) return;
        for (int nv = MEDIO; nv <= ALTO; nv++) {
            if (!hayVisorExacto(categoria, at, nv)) continue;
            onda(categoria, suelo, col, 1.2f * escala, (nv == ALTO ? 6.5f : 4.5f) * escala, 9, nv, 0);
            int n = nv == ALTO ? 10 : 4;
            for (int i = 0; i < n; i++) {
                double ang = Math.PI * 2 * i / n + rnd.nextDouble(.5), rr = rnd.nextDouble(.5, 2.3) * escala;
                Location l = piso(suelo.clone().add(Math.cos(ang) * rr, 0.8, Math.sin(ang) * rr), 2.5);
                if (l == null) continue;
                Fx s = llamita(categoria, l, col, (float) rnd.nextDouble(.8, 1.7) * escala, rnd.nextInt(18, 32), nv);
                if (s == null) break;
                s.base = true; s.edad = -rnd.nextInt(0, 5);
                s.e.setBillboard(Display.Billboard.VERTICAL);
            }
            if (nv < ALTO) continue;
            for (int i = 0; i < 6; i++) {                   // brasas
                Fx s = fx(categoria, at.clone().add(rnd.nextDouble(-1, 1), rnd.nextDouble(0, .8), rnd.nextDouble(-1, 1)), "estrella", col, .4f, .1f, rnd.nextInt(14, 24), nv, nv, true);
                if (s == null) break;
                s.curva = ACHICA; s.cuadros = 1; s.cuadro = 1; s.e.setItemStack(item("estrella", 1, col));
                s.vel.set((float) rnd.nextDouble(-.04, .04), (float) rnd.nextDouble(.06, .14), (float) rnd.nextDouble(-.04, .04));
            }
        }
    }

    /** Anillo plano en el piso que se abre. */
    private void onda(Categoria categoria, Location suelo, Color col, float desde, float hasta, int vida, int nv, int espera) {
        Fx f = fx(categoria, suelo.clone().add(0, 0.05, 0), "onda", col, desde, hasta, vida, nv, nv, false);
        if (f == null) return;
        f.cuadros = n("onda"); f.edad = -espera;
        f.rot = new Quaternionf().rotationX((float) (Math.PI / 2));
        f.e.setBillboard(Display.Billboard.FIXED);
        aplicar(f, espera > 0 ? 0 : desde);
    }

    private Fx llamita(Categoria categoria, Location l, Color col, float tam, int vida, int nv) {
        Fx s = fx(categoria, l, "llama", col, 0, tam, vida, nv, nv, true);
        if (s != null) { s.curva = POP; s.ciclo = true; s.cuadros = n("llama"); }
        return s;
    }

    // ------------------------------------------------------------------ impactos y golpes de jefes
    /** Golpe al piso: anillos de particulas; hongos de explosion, manchas, llamitas y medialunas segun el nivel. */
    void golpe(Categoria categoria, Location at, Color col, double radio, String elem) {
        if (!hayVisor(categoria, at, MEDIO)) return;
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        Particle.DustOptions dust = new Particle.DustOptions(col, 2.2f);
        for (int ring = 1; ring <= 3; ring++) {
            double r = radio * ring / 3.0; int pts = (int) (12 * r);
            getServer().getScheduler().runTaskLater(this, () -> {
                for (int i = 0; i < pts; i++) {
                    double ang = 2 * Math.PI * i / pts;
                    particula(categoria, at.clone().add(Math.cos(ang) * r, 0.25, Math.sin(ang) * r), MEDIO, Particle.DUST, 1, 0.05, 0.05, 0.05, 0, dust);
                }
            }, ring * 2L);
        }
        elemento(categoria, at.clone().add(0, 0.6, 0), elem, MEDIO, radio * 0.7, 18);
        Location suelo = at.clone().add(0, 0.05, 0);
        float diam = (float) (radio * 2.3);
        if (hayVisorExacto(categoria, at, MEDIO)) {                      // Medio: onda, un hongo y una mancha
            onda(categoria, suelo, col, diam * 0.25f, diam, 10, MEDIO, 0);
            hongo(categoria, suelo, col, 2.4f, 3.8f, 14, MEDIO, 0);
            mancha(categoria, suelo, col, (float) Math.min(6, radio * 1.2), 16, MEDIO);
        }
        if ("fuego".equals(elem)) getServer().getScheduler().runTaskLater(this, () -> incendio(categoria, at.clone().add(0, 0.5, 0), col, (float) Math.min(2.2, radio / 2.5)), 3);
        if (!hayVisorExacto(categoria, at, ALTO)) return;
        onda(categoria, suelo, col, diam * 0.2f, diam, 10, ALTO, 0);     // dos ondas seguidas y un destello blanco
        onda(categoria, suelo, Color.WHITE, diam * 0.15f, diam * 0.8f, 9, ALTO, 3);
        onda(categoria, suelo, col, diam * 0.2f, diam * 1.25f, 12, ALTO, 6);
        Fx flash = fx(categoria, suelo.clone().add(0, 1.2, 0), "estrella", Color.WHITE, 0, (float) Math.min(7, radio * 1.3), 7, ALTO, ALTO, false);
        if (flash != null) { flash.curva = POP; flash.cuadros = 3; }
        float grande = (float) Math.min(6.5, 3 + radio * 0.45);
        hongo(categoria, suelo, col, grande * 0.6f, grande, 18, ALTO, 0);
        mancha(categoria, suelo, col, (float) Math.min(9, radio * 1.7), 22, ALTO);
        int n = (int) Math.max(5, Math.min(9, radio * 1.4));
        for (int i = 0; i < n; i++) {                         // corona de hongos alrededor (como la referencia)
            double ang = 2 * Math.PI * i / n + rnd.nextDouble(.5), r = radio * rnd.nextDouble(.55, 1.0);
            Location l = suelo.clone().add(Math.cos(ang) * r, 0, Math.sin(ang) * r);
            float tam = (float) rnd.nextDouble(1.8, 3.1);
            hongo(categoria, l, col, tam * 0.55f, tam, rnd.nextInt(12, 17), ALTO, 2 + rnd.nextInt(7));
            if (i % 2 == 0) mancha(categoria, l, col, tam * 0.9f, 18, ALTO);
        }
        for (int i = 0; i < 14; i++) {                        // llamitas que suben por toda la zona
            double ang = rnd.nextDouble(Math.PI * 2), r = radio * Math.sqrt(rnd.nextDouble());
            Fx s = llamita(categoria, suelo.clone().add(Math.cos(ang) * r, rnd.nextDouble(.2, 1.2), Math.sin(ang) * r), col, (float) rnd.nextDouble(.3, .6), rnd.nextInt(16, 30), ALTO);
            if (s == null) break;
            s.edad = -rnd.nextInt(0, 12);
            s.vel.set(0, (float) rnd.nextDouble(.04, .1), 0);
        }
        Color oscuro = Color.fromRGB(col.getRed() * 2 / 3, col.getGreen() * 2 / 3, col.getBlue() * 2 / 3);
        for (int i = 0; i < 4; i++) {                         // medialunas que salen hacia afuera
            double ang = Math.PI / 2 * i + rnd.nextDouble(.8);
            Fx s = fx(categoria, suelo.clone().add(Math.cos(ang), 1 + rnd.nextDouble(1.5), Math.sin(ang)), "medialuna", oscuro, 1.6f, 0.5f, 12, ALTO, ALTO, true);
            if (s == null) break;
            s.curva = ACHICA; s.cuadros = 1; s.cuadro = 0; s.modelo = "medialuna";
            s.vel.set((float) (Math.cos(ang) * radio / 14), 0.02f, (float) (Math.sin(ang) * radio / 14));
        }
        // el piso queda "encendido" del elemento un par de segundos (fuego, escarcha, veneno...)
        for (int k = 1; k <= 4; k++)
            getServer().getScheduler().runTaskLater(this, () -> elemento(categoria, at.clone().add(0, 0.2, 0), elem, ALTO, radio, 14), k * 8L);
    }

    /** Impacto (bastones, disparos de jefes): hongo de explosion del color, mancha, llamitas y destellos. */
    void estallido(Categoria categoria, Location at, Color col, float escala, String elem) {
        if (!hayVisor(categoria, at, MEDIO)) return;
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        particula(categoria, at, MEDIO, Particle.DUST, 14, 0.35, 0.35, 0.35, 0, new Particle.DustOptions(col, 1.6f));
        elemento(categoria, at, elem, MEDIO, 0.5, 10);
        Location suelo = piso(at, 3);
        Location pie = suelo != null ? suelo : at.clone().add(0, -0.6, 0);
        if (hayVisorExacto(categoria, at, MEDIO)) hongo(categoria, pie, col, 0.7f * escala, 1.5f * escala, 10, MEDIO, 0);
        if (!hayVisorExacto(categoria, at, ALTO)) return;
        hongo(categoria, pie, col, 1.1f * escala, 2.5f * escala, 14, ALTO, 0);
        if (suelo != null) { mancha(categoria, suelo, col, 2.6f * escala, 16, ALTO); onda(categoria, suelo, col, 0.8f * escala, 3.6f * escala, 8, ALTO, 0); }
        if ("fuego".equals(elem)) incendio(categoria, at, col, 0.6f * escala);
        for (int i = 0; i < 5; i++) {
            Fx s = llamita(categoria, at.clone().add(rnd.nextDouble(-.7, .7) * escala, rnd.nextDouble(-.3, .5), rnd.nextDouble(-.7, .7) * escala), col, (float) rnd.nextDouble(.3, .5), rnd.nextInt(12, 22), ALTO);
            if (s == null) break;
            s.edad = -rnd.nextInt(0, 6);
            s.vel.set((float) rnd.nextDouble(-.02, .02), (float) rnd.nextDouble(.05, .1), (float) rnd.nextDouble(-.02, .02));
        }
        for (int i = 0; i < 3; i++) {
            Fx s = fx(categoria, at.clone().add(rnd.nextDouble(-.8, .8), rnd.nextDouble(-.2, .9), rnd.nextDouble(-.8, .8)), "estrella", Color.WHITE, 0, (float) rnd.nextDouble(.5, .9), rnd.nextInt(6, 10), ALTO, ALTO, true);
            if (s == null) break;
            s.curva = POP; s.cuadros = 3; s.edad = -i * 2;
        }
        particula(categoria, at, ALTO, Particle.ELECTRIC_SPARK, 8, 0.3, 0.3, 0.3, 0.2, null);
    }

    /** Rastro de un proyectil (jefes): una llamita del color y, en Alto, un destello. Muy liviano. */
    void estela(Categoria categoria, Location at, Color col, String elem) {
        if (!hayVisor(categoria, at, MEDIO)) return;
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        Fx s = fx(categoria, at, "llama", col, .7f, .15f, 9, MEDIO, ALTO, true);
        if (s != null) { s.curva = ACHICA; s.ciclo = true; s.cuadros = n("llama"); }
        if (rnd.nextInt(2) == 0 && hayVisorExacto(categoria, at, ALTO)) {
            Fx e = fx(categoria, at.clone().add(rnd.nextDouble(-.3, .3), rnd.nextDouble(-.3, .3), rnd.nextDouble(-.3, .3)), "estrella", Color.WHITE, 0, .6f, 7, ALTO, ALTO, true);
            if (e != null) { e.curva = POP; e.cuadros = 3; }
        }
        elemento(categoria, at, elem, ALTO, 0.2, 2);
    }

    private void hongo(Categoria categoria, Location pie, Color col, float desde, float hasta, int vida, int nv, int espera) {
        Fx f = fx(categoria, pie, "hongo", col, desde, hasta, vida, nv, nv, false);
        if (f == null) return;
        f.base = true; f.cuadros = n("hongo"); f.edad = -espera;
        f.e.setBillboard(Display.Billboard.VERTICAL);
        if (espera > 0) aplicar(f, 0);
    }

    private void mancha(Categoria categoria, Location suelo, Color col, float tam, int vida, int nv) {
        Fx f = fx(categoria, suelo.clone().add(0, 0.03, 0), "salpicadura", col, tam * 0.5f, tam, vida, nv, nv, true);
        if (f == null) return;
        f.cuadros = n("salpicadura");
        f.rot = new Quaternionf().rotationX((float) (Math.PI / 2)).rotateZ((float) ThreadLocalRandom.current().nextDouble(Math.PI * 2));
        f.e.setBillboard(Display.Billboard.FIXED);
        aplicar(f, f.s0);
    }

    /** Punto del piso debajo de `at` (hasta `max` bloques), o null si esta en el aire. */
    private static Location piso(Location at, double max) {
        RayTraceResult r = at.getWorld().rayTraceBlocks(at.clone().add(0, 0.3, 0), new Vector(0, -1, 0), max + 0.3, FluidCollisionMode.NEVER, true);
        return r == null ? null : r.getHitPosition().toLocation(at.getWorld()).add(0, 0.02, 0);
    }

    /** Particulas propias de cada elemento (hielo, fuego, veneno, agua, arena, naturaleza, arcano, rayo, piedra, luz, vacio). */
    void elemento(Categoria categoria, Location at, String elem, int min, double r, int cant) {
        switch (elem == null ? "" : elem) {
            case "fuego" -> { particula(categoria, at, min, Particle.FLAME, cant, r, 0.3, r, 0.02, null);
                              particula(categoria, at, min, Particle.LAVA, Math.max(1, cant / 6), r, 0.2, r, 0, null);
                              particula(categoria, at, min, Particle.LARGE_SMOKE, Math.max(1, cant / 4), r, 0.4, r, 0.01, null); }
            case "hielo" -> { particula(categoria, at, min, Particle.SNOWFLAKE, cant, r, 0.5, r, 0.02, null);
                              particula(categoria, at, min, Particle.ITEM_SNOWBALL, Math.max(1, cant / 2), r, 0.3, r, 0.05, null); }
            case "veneno" -> { particula(categoria, at, min, Particle.ITEM_SLIME, cant, r, 0.3, r, 0.05, null);
                               particula(categoria, at, min, Particle.DUST, cant, r, 0.6, r, 0, new Particle.DustOptions(Color.fromRGB(0x7CFF3A), 1.8f)); }
            case "agua" -> { particula(categoria, at, min, Particle.SPLASH, cant * 2, r, 0.3, r, 0.1, null);
                             particula(categoria, at, min, Particle.BUBBLE_POP, cant, r, 0.4, r, 0.02, null); }
            case "arena" -> { particula(categoria, at, min, Particle.CLOUD, cant / 2 + 1, r, 0.3, r, 0.02, null);
                              particula(categoria, at, min, Particle.DUST, cant, r, 0.5, r, 0, new Particle.DustOptions(Color.fromRGB(0xE8C77A), 1.6f)); }
            case "naturaleza" -> { particula(categoria, at, min, Particle.SPORE_BLOSSOM_AIR, cant, r, 0.5, r, 0, null);
                                   particula(categoria, at, min, Particle.HAPPY_VILLAGER, cant / 2 + 1, r, 0.4, r, 0, null); }
            case "arcano" -> { particula(categoria, at, min, Particle.WITCH, cant, r, 0.5, r, 0.05, null);
                               particula(categoria, at, min, Particle.END_ROD, cant / 2 + 1, r, 0.5, r, 0.03, null); }
            case "rayo" -> particula(categoria, at, min, Particle.ELECTRIC_SPARK, cant * 2, r, 0.6, r, 0.2, null);
            case "piedra" -> particula(categoria, at, min, Particle.CRIT, cant, r, 0.3, r, 0.2, null);
            case "luz" -> particula(categoria, at, min, Particle.END_ROD, cant, r, 0.6, r, 0.04, null);
            case "vacio" -> { particula(categoria, at, min, Particle.REVERSE_PORTAL, cant * 2, r, 0.6, r, 0.05, null);
                              particula(categoria, at, min, Particle.SCULK_SOUL, cant / 3 + 1, r, 0.3, r, 0.02, null); }
            case "rosa" -> particula(categoria, at, min, Particle.CHERRY_LEAVES, cant, r, 0.6, r, 0, null);
            default -> {}
        }
    }

    // ------------------------------------------------------------------ motor de dibujos
    private int n(String modelo) { return cuadros.getOrDefault(modelo, 1); }

    private ItemStack item(String modelo, int cuadro, Color col) {
        ItemStack it = new ItemStack(Material.PAPER);
        var meta = it.getItemMeta();
        meta.setItemModel(new NamespacedKey("astral", cuadro < 0 ? "fx/" + modelo : "fx/" + modelo + "_" + cuadro));
        it.setItemMeta(meta);
        it.setData(io.papermc.paper.datacomponent.DataComponentTypes.DYED_COLOR,
            io.papermc.paper.datacomponent.item.DyedItemColor.dyedItemColor(col));
        return it;
    }

    /** Crea un dibujo que solo ven los jugadores con nivel entre min y max. adorno: se descarta primero si hay muchos. */
    private Fx fx(Categoria categoria, Location at, String modelo, Color col, float s0, float s1, int vida, int min, int max, boolean adorno) {
        if (!hayVisor(categoria, at, min)) return null;
        if (fxs.size() >= (adorno ? TOPE_ADORNO : TOPE)) return null;
        // Un dibujo no debe cargar chunks: una entidad creada fuera de los
        // chunks activos puede quedar invalida al principio y aparecer mas tarde
        // cuando ya salio de fxs, sin que nadie termine su animacion.
        if (!at.getWorld().isChunkLoaded(at.getBlockX() >> 4, at.getBlockZ() >> 4)) return null;
        Fx f = new Fx();
        f.categoria = categoria; f.min = min; f.max = max;
        f.modelo = modelo; f.col = col; f.s0 = s0; f.s1 = s1; f.vida = vida;
        boolean rayo = modelo.equals("rayo");
        // Las transformaciones estan en coordenadas del mundo: no sumar yaw/pitch del emisor.
        Location origen = at.clone();
        origen.setYaw(0); origen.setPitch(0);
        f.e = at.getWorld().spawn(origen, ItemDisplay.class, x -> {
            x.setPersistent(false);
            x.setVisibleByDefault(false);
            x.setPersistent(false);
            x.setItemStack(item(modelo, rayo ? -1 : 0, col));
            x.setBillboard(Display.Billboard.CENTER);
            x.setBrightness(new Display.Brightness(15, 15));
            x.setViewRange(1.5f);
            x.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(s0, s0, s0), new Quaternionf()));
            x.addScoreboardTag("astral.fx.sprite");
        });
        f.cuadro = rayo ? -1 : 0;
        for (Player p : at.getWorld().getPlayers()) {
            int nv = nivel(p);
            if (activada(p, categoria) && nv >= min && nv <= max && p.getLocation().distanceSquared(at) < 64 * 64) p.showEntity(this, f.e);
        }
        fxs.add(f);
        return f;
    }

    private void aplicar(Fx f, float sc) {
        Vector3f t = new Vector3f(f.pos);
        if (f.base) t.y += sc / 2;
        Vector3f escala = f.rayo ? new Vector3f(sc, sc, f.largo) : new Vector3f(sc, sc, sc);
        f.e.setTransformation(new Transformation(t, f.rot, escala, new Quaternionf()));
    }

    private void animar() {
        for (Iterator<Fx> it = fxs.iterator(); it.hasNext();) {
            Fx f = it.next();
            if (!f.e.isValid()) { f.e.remove(); it.remove(); continue; }
            f.edad++;
            if (f.edad >= f.vida) { f.e.remove(); it.remove(); continue; }
            if (f.edad < 0) continue;                         // todavia esperando su turno (tamano 0)
            if (f.rayo) {                                     // un solo cambio: el cliente lo afina solo
                if (f.edad == 1) {
                    f.e.setInterpolationDelay(0); f.e.setInterpolationDuration(f.vida - 1);
                    aplicar(f, f.s1);
                }
                continue;
            }
            float t = (float) f.edad / f.vida;
            if (f.cuadros > 1) {
                int c = f.ciclo ? (f.edad / 2) % f.cuadros : Math.min(f.cuadros - 1, (int) (t * f.cuadros));
                if (f.curva == POP && !f.ciclo) c = Math.min(f.cuadros - 1, (int) (Math.sin(t * Math.PI) * f.cuadros));
                if (c != f.cuadro) { f.cuadro = c; f.e.setItemStack(item(f.modelo, c, f.col)); }
            }
            float sc = switch (f.curva) {
                case POP -> f.s0 + (f.s1 - f.s0) * (float) Math.sin(t * Math.PI);
                case ACHICA -> f.s0 + (f.s1 - f.s0) * t;
                default -> f.s0 + (f.s1 - f.s0) * (float) Math.sqrt(t);
            };
            f.pos.add(f.vel); f.vel.y -= f.grav;
            f.e.setInterpolationDelay(0); f.e.setInterpolationDuration(1);
            aplicar(f, sc);
        }
    }

    // ------------------------------------------------------------------ rastros (solo Alto)
    private void rastros() {
        boolean alguien = false;
        for (Player p : Bukkit.getOnlinePlayers()) if (nivel(p) >= ALTO) { alguien = true; break; }
        if (!alguien) { ultimo.clear(); return; }
        for (Player p : Bukkit.getOnlinePlayers()) {
            if (p.getGameMode() == GameMode.SPECTATOR || p.isInvisible() || p.isDead()) continue;
            Location loc = p.getLocation(), antes = ultimo.put(p.getUniqueId(), loc);
            boolean mueve = antes != null && antes.getWorld() == loc.getWorld() && antes.distanceSquared(loc) > 0.02;

            if (mueve) rastroArma(p, loc);
            auraArmadura(p, loc, mueve);
        }
        Categoria categoria = Categoria.MASCOTAS;
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        for (World w : Bukkit.getWorlds()) {
            if (w.getPlayers().isEmpty()) continue;
            for (Entity e : w.getEntitiesByClass(LivingEntity.class)) {
                Set<String> tags = e.getScoreboardTags();
                if (!tags.contains("astral.pet.evo")) continue;
                Color col = Color.WHITE;
                for (String t : tags) if (t.startsWith("astral.pet.") && colorMascota.containsKey(t.substring(11))) col = colorMascota.get(t.substring(11));
                Location l = e.getLocation(), antes = ultimo.put(e.getUniqueId(), l);
                if (antes == null || antes.getWorld() != l.getWorld() || antes.distanceSquared(l) < 0.01) continue;
                particula(categoria, l.clone().add(0, 0.3, 0), ALTO, Particle.DUST, 3, 0.15, 0.1, 0.15, 0, new Particle.DustOptions(col, 1.3f));
                if (rnd.nextInt(3) == 0 && hayVisor(categoria, l, ALTO)) {      // llamita del color de la mascota
                    Fx s = llamita(categoria, l.clone().add(rnd.nextDouble(-.2, .2), 0.35, rnd.nextDouble(-.2, .2)), col, .3f, 12, ALTO);
                    if (s != null) s.vel.set(0, 0.03f, 0);
                }
            }
        }
    }

    private void rastroArma(Player p, Location loc) {
        Categoria categoria = Categoria.ARMAS;
        if (!hayVisor(categoria, loc, ALTO)) return;
        Map<String, String> d = datos(p.getInventory().getItemInMainHand());
        if (d == null) return;
        String tipo = d.getOrDefault("type", ""), w = d.getOrDefault("w", "");
        int tier = entero(d.get("tier"));
        Color col = colorTier.getOrDefault(tier, Color.WHITE);
        int cant = p.isSprinting() ? 4 : 2;
        Location pies = loc.clone().add(0, 0.15, 0).subtract(loc.getDirection().setY(0).normalize().multiply(0.4));
        if (w.equals("bow") || w.equals("crossbow")) {
            particula(categoria, pies.add(0, 0.6, 0), ALTO, Particle.DUST_COLOR_TRANSITION, cant, 0.15, 0.2, 0.15, 0,
                new Particle.DustTransition(col, Color.WHITE, 0.9f));
        } else if (tipo.equals("weapon") || tipo.equals("staff")) {
            particula(categoria, pies, ALTO, Particle.DUST, cant, 0.18, 0.05, 0.18, 0, new Particle.DustOptions(col, 1.1f));
            if (!p.isSprinting()) return;
            ThreadLocalRandom rnd = ThreadLocalRandom.current();     // corriendo: destellos del color del arma
            Fx s = fx(categoria, pies.clone().add(rnd.nextDouble(-.3, .3), rnd.nextDouble(.1, .9), rnd.nextDouble(-.3, .3)), "estrella", col, 0, .4f, 8, ALTO, ALTO, true);
            if (s != null) { s.curva = POP; s.cuadros = 3; }
        }
    }

    private void auraArmadura(Player p, Location loc, boolean mueve) {
        Categoria categoria = Categoria.ARMADURAS;
        if (!hayVisor(categoria, loc, ALTO)) return;
        var inv = p.getInventory();
        Map<String, String> pecho = datos(inv.getChestplate());
        if (pecho == null || !"armor".equals(pecho.get("type"))) return;
        String set = pecho.getOrDefault("set", "");
        for (ItemStack pieza : new ItemStack[]{inv.getHelmet(), inv.getLeggings(), inv.getBoots()}) {
            Map<String, String> o = datos(pieza);
            if (o == null || !set.equals(o.get("set"))) return;   // solo con el set completo
        }
        int tier = entero(pecho.get("tier"));
        Color col = colorSet.getOrDefault(set, colorTier.getOrDefault(tier, Color.WHITE));
        Location cuerpo = loc.clone().add(0, 1.0, 0);
        String aura = auraSet.getOrDefault(set, "polvo");
        int c = mueve ? 2 : 1;
        switch (aura) {
            case "agua" -> particula(categoria, cuerpo, ALTO, Particle.DRIPPING_WATER, c, 0.3, 0.5, 0.3, 0, null);
            case "magia" -> particula(categoria, cuerpo, ALTO, Particle.ENCHANT, c * 3, 0.4, 0.6, 0.4, 0.4, null);
            case "furia" -> particula(categoria, cuerpo, ALTO, Particle.CRIT, c, 0.35, 0.5, 0.35, 0.05, null);
            case "bosque" -> particula(categoria, cuerpo, ALTO, Particle.CHERRY_LEAVES, 1, 0.4, 0.4, 0.4, 0, null);
            case "mina" -> particula(categoria, cuerpo, ALTO, Particle.WAX_ON, 1, 0.35, 0.5, 0.35, 0, null);
            case "esporas" -> particula(categoria, cuerpo, ALTO, Particle.SPORE_BLOSSOM_AIR, c, 0.4, 0.5, 0.4, 0, null);
            default -> {}
        }
        particula(categoria, cuerpo, ALTO, Particle.DUST, c, 0.35, 0.55, 0.35, 0, new Particle.DustOptions(col, 0.8f));
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        if (rnd.nextInt(5) == 0) {                                    // cada tanto, un destello del color del set
            Fx s = fx(categoria, cuerpo.clone().add(rnd.nextDouble(-.45, .45), rnd.nextDouble(-.7, .8), rnd.nextDouble(-.45, .45)), "estrella", col, 0, .35f, 10, ALTO, ALTO, true);
            if (s != null) { s.curva = POP; s.cuadros = 3; s.vel.set(0, 0.02f, 0); }
        }
    }

    // ------------------------------------------------------------------ utilidades
    static Map<String, String> datos(ItemStack it) {
        if (it == null || it.getType().isAir() || !it.hasItemMeta()) return null;
        Matcher m = ASTRAL.matcher(it.getItemMeta().getAsString());
        if (!m.find()) return null;
        Map<String, String> out = new HashMap<>();
        for (String par : m.group(1).split(",")) {
            int i = par.indexOf(':');
            if (i <= 0) continue;
            String v = par.substring(i + 1).trim();
            if (v.startsWith("\"")) v = v.replace("\"", "");
            else v = v.replaceAll("^(-?[0-9.]+)[bsLfd]$", "$1");
            out.put(par.substring(0, i).trim(), v);
        }
        return out;
    }
    static int entero(String s) { try { return s == null ? 0 : Integer.parseInt(s); } catch (NumberFormatException e) { return 0; } }
    static Color hex(String s) {
        if (s == null) return Color.WHITE;
        s = s.replace("#", "");
        try { return Color.fromRGB(Integer.parseInt(s, 16) & 0xFFFFFF); } catch (NumberFormatException e) { return Color.WHITE; }
    }
    private boolean hayVisor(Categoria categoria, Location at, int min) {
        if (prueba) return true;
        for (Player p : at.getWorld().getPlayers()) if (activada(p, categoria) && nivel(p) >= min && p.getLocation().distanceSquared(at) < 64 * 64) return true;
        return false;
    }
    private boolean hayVisorExacto(Categoria categoria, Location at, int nv) {
        if (prueba) return true;
        for (Player p : at.getWorld().getPlayers()) if (activada(p, categoria) && nivel(p) == nv && p.getLocation().distanceSquared(at) < 64 * 64) return true;
        return false;
    }
    private <T> void particula(Categoria categoria, Location at, int min, Particle part, int count, double ox, double oy, double oz, double speed, T data) {
        for (Player p : at.getWorld().getPlayers()) {
            if (!activada(p, categoria) || nivel(p) < min || p.getLocation().distanceSquared(at) > 48 * 48) continue;
            p.spawnParticle(part, at, count, ox, oy, oz, speed, data, true);
        }
    }
}

/** Limita los paquetes de damage_indicator segun el nivel de efectos de quien los recibe. */
final class AstralEfectosParticulas extends com.github.retrooper.packetevents.event.PacketListenerAbstract {
    static void registrar() {
        com.github.retrooper.packetevents.PacketEvents.getAPI().getEventManager().registerListener(new AstralEfectosParticulas());
    }
    @Override public void onPacketSend(com.github.retrooper.packetevents.event.PacketSendEvent e) {
        if (e.getPacketType() != com.github.retrooper.packetevents.protocol.packettype.PacketType.Play.Server.PARTICLE) return;
        var w = new com.github.retrooper.packetevents.wrapper.play.server.WrapperPlayServerParticle(e);
        if (w.getParticle().getType() != com.github.retrooper.packetevents.protocol.particle.type.ParticleTypes.DAMAGE_INDICATOR) return;
        UUID id = e.getUser() == null ? null : e.getUser().getUUID();
        int tope = AstralEfectos.GOLPE_PARTICULAS[id == null ? 0 : AstralEfectos.NIVEL.getOrDefault(id, AstralEfectos.MEDIO)];
        if (w.getParticleCount() > tope) { w.setParticleCount(tope); e.markForReEncode(true); }
    }
}
