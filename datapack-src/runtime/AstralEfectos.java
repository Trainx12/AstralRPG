package astral;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
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
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Efectos visuales con nivel por jugador (pedido del dueno 14-15/11/2026). Generado/compilado por efectos.py.
 *
 * Nivel en el score astral.fx: 0 Bajo (el juego como estaba), 1 Medio (default), 2 Alto.
 * - Particulas de golpe (damage_indicator): Bajo 3, Medio 6, Alto 12 por golpe (vanilla manda dano/2: millones).
 * - /astralfx golpe|estallido <mundo> <x> <y> <z> <#color>: jefes (MythicMobs) y Skript. Medio: anillos de particulas.
 *   Alto: ademas dibujos planos animados (item_display solo visible para quien tiene Alto).
 * - Marcadores del datapack con tags astral.fx + fx.<tipo> + fxc.<rrggbb> (el datapack no puede llamar comandos
 *   de plugins): el plugin hace el efecto y borra el marcador.
 * - Alto: rastro de armas (espadas, hachas, guadanas, lanzas, arcos) al caminar/correr, aura de armaduras con set
 *   completo y rastro de mascotas evolucionadas (tag astral.pet.evo + astral.pet.<id>).
 * Cada efecto se manda solo a quien lo puede ver y tiene el nivel: si nadie tiene Medio/Alto no se genera nada.
 */
public final class AstralEfectos extends JavaPlugin implements Listener, TabExecutor {
    static final String OBJ = "astral.fx";
    static final int BAJO = 0, MEDIO = 1, ALTO = 2;
    static final Map<UUID, Integer> NIVEL = new ConcurrentHashMap<>();
    static final int[] GOLPE_PARTICULAS = {3, 6, 12};
    private static final Pattern ASTRAL = Pattern.compile("astral:\\{([^{}]*)\\}");
    private final Map<UUID, Location> ultimo = new HashMap<>();
    private final List<Sprite> sprites = new ArrayList<>();
    private final Map<Integer, Color> colorTier = new HashMap<>();
    private final Map<String, Color> colorMascota = new HashMap<>();
    private final Map<String, String> auraSet = new HashMap<>();
    private final Map<String, Color> colorSet = new HashMap<>();
    private int frames = 8;

    private static final class Sprite {
        ItemDisplay e; int edad, vida; float desde, hasta; String modelo;
    }

    @Override public void onEnable() {
        saveDefaultConfig();
        var c = getConfig();
        frames = c.getInt("frames", 8);
        ConfigurationSection s = c.getConfigurationSection("color-tier");
        if (s != null) for (String k : s.getKeys(false)) colorTier.put(Integer.parseInt(k), hex(s.getString(k)));
        s = c.getConfigurationSection("color-mascota");
        if (s != null) for (String k : s.getKeys(false)) colorMascota.put(k, hex(s.getString(k)));
        s = c.getConfigurationSection("aura-set");
        if (s != null) for (String k : s.getKeys(false)) auraSet.put(k, s.getString(k));
        s = c.getConfigurationSection("color-set");
        if (s != null) for (String k : s.getKeys(false)) colorSet.put(k, hex(s.getString(k)));
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
        for (Sprite s : sprites) if (s.e.isValid()) s.e.remove();
        sprites.clear();
    }

    // ------------------------------------------------------------------ nivel por jugador
    private Objective objetivo() {
        Scoreboard sb = Bukkit.getScoreboardManager().getMainScoreboard();
        Objective o = sb.getObjective(OBJ);
        if (o == null) o = sb.registerNewObjective(OBJ, Criteria.DUMMY, net.kyori.adventure.text.Component.text("Efectos"));
        return o;
    }
    private int leer(Player p) {
        Score sc = objetivo().getScore(p.getName());
        if (!sc.isScoreSet()) sc.setScore(MEDIO);   // pedido del dueno: los jugadores arrancan en Medio
        int n = Math.max(BAJO, Math.min(ALTO, sc.getScore()));
        NIVEL.put(p.getUniqueId(), n);
        return n;
    }
    static int nivel(Player p) { return NIVEL.getOrDefault(p.getUniqueId(), MEDIO); }
    @EventHandler public void entra(PlayerJoinEvent e) { leer(e.getPlayer()); }
    @EventHandler public void sale(PlayerQuitEvent e) { NIVEL.remove(e.getPlayer().getUniqueId()); ultimo.remove(e.getPlayer().getUniqueId()); }

    private static final String[] NOMBRE = {"Bajo", "Medio", "Alto"};
    private static final String[] DESC = {
        "el juego como siempre: sin efectos nuevos y solo 3 particulas por golpe",
        "disparos de bastones mas lindos y anillos en los golpes de los jefes",
        "todo: explosiones de los jefes, rastros de armas, auras de armaduras y mascotas"};

    @Override public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if (cmd.getName().equals("astralfx")) return astralfx(sender, args);
        if (!(sender instanceof Player p)) return true;
        if (args.length == 1) {
            int n = switch (args[0].toLowerCase(Locale.ROOT)) { case "bajo" -> 0; case "medio" -> 1; case "alto" -> 2; default -> -1; };
            if (n < 0) { p.sendMessage("§cUsa: /efectos bajo, medio o alto"); return true; }
            objetivo().getScore(p.getName()).setScore(n);
            NIVEL.put(p.getUniqueId(), n);
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
        return true;
    }
    @Override public List<String> onTabComplete(CommandSender s, Command cmd, String label, String[] args) {
        if (cmd.getName().equals("efectos") && args.length == 1) return List.of("bajo", "medio", "alto");
        if (cmd.getName().equals("astralfx") && args.length == 1) return List.of("golpe", "estallido");
        return List.of();
    }

    // ------------------------------------------------------------------ efectos por comando y marcadores
    private boolean astralfx(CommandSender sender, String[] a) {
        if (sender instanceof Player p && !p.hasPermission("astral.admin.efectos")) return true;
        if (a.length < 5) { sender.sendMessage("astralfx golpe|estallido <mundo> <x> <y> <z> [color] [radio] [elemento]"); return true; }
        World w = mundo(a[1]);
        if (w == null) return true;
        Location at;
        try { at = new Location(w, Double.parseDouble(a[2]), Double.parseDouble(a[3]), Double.parseDouble(a[4])); }
        catch (NumberFormatException ex) { return true; }
        Color col = a.length > 5 ? hex(a[5]) : Color.fromRGB(0x7CFF5A);
        double radio = 4;
        if (a.length > 6) try { radio = Double.parseDouble(a[6]); } catch (NumberFormatException ignored) {}
        String elem = a.length > 7 ? a[7] : "";
        if (a[0].equals("golpe")) golpe(at, col, radio, elem); else estallido(at, col, 1f, elem);
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
            if ("golpe".equals(tf)) golpe(at, cf, 4, ef); else if ("estallido".equals(tf)) estallido(at, cf, 0.8f, ef);
        });
    }

    /** Golpe al piso: Medio anillos de particulas; Alto, ademas, dibujos de explosion alrededor. */
    void golpe(Location at, Color col, double radio, String elem) {
        Particle.DustOptions dust = new Particle.DustOptions(col, 2.2f);
        for (int ring = 1; ring <= 3; ring++) {
            double r = radio * ring / 3.0; int pts = (int) (12 * r);
            int delay = ring * 2;
            getServer().getScheduler().runTaskLater(this, () -> {
                for (int i = 0; i < pts; i++) {
                    double ang = 2 * Math.PI * i / pts;
                    Location l = at.clone().add(Math.cos(ang) * r, 0.25, Math.sin(ang) * r);
                    particula(l, MEDIO, Particle.DUST, 1, 0.05, 0.05, 0.05, 0, dust);
                }
            }, delay);
        }
        elemento(at.clone().add(0, 0.6, 0), elem, MEDIO, radio * 0.7, 18);
        if (!hayVisor(at, ALTO)) return;
        Random rnd = new Random();
        sprite(at.clone().add(0, 0.1, 0), col, 3.2f, 5.0f, 16);
        // el piso queda "encendido" del elemento un par de segundos (fuego, escarcha, veneno...)
        for (int k = 1; k <= 4; k++) {
            int d = k * 8;
            getServer().getScheduler().runTaskLater(this, () -> elemento(at.clone().add(0, 0.2, 0), elem, ALTO, radio, 14), d);
        }
        int n = 5;
        for (int i = 0; i < n; i++) {
            double ang = 2 * Math.PI * i / n + rnd.nextDouble() * 0.6;
            double r = radio * (0.6 + rnd.nextDouble() * 0.5);
            Location l = at.clone().add(Math.cos(ang) * r, 0.1, Math.sin(ang) * r);
            int d = 2 + rnd.nextInt(5);
            getServer().getScheduler().runTaskLater(this, () -> sprite(l, col, 1.6f, 3.0f, 13), d);
        }
        particula(at.clone().add(0, 1.5, 0), ALTO, Particle.END_ROD, 25, radio * 0.6, 1.2, radio * 0.6, 0.04, null);
    }

    /** Impacto (bastones, disparos de jefes): Medio chispas de color; Alto un dibujo de explosion chico. */
    void estallido(Location at, Color col, float escala, String elem) {
        particula(at, MEDIO, Particle.DUST, 14, 0.35, 0.35, 0.35, 0, new Particle.DustOptions(col, 1.6f));
        elemento(at, elem, MEDIO, 0.5, 10);
        if (!hayVisor(at, ALTO)) return;
        sprite(at.clone().add(0, -0.4, 0), col, 0.9f * escala, 1.8f * escala, 10);
        particula(at, ALTO, Particle.ELECTRIC_SPARK, 10, 0.3, 0.3, 0.3, 0.2, null);
    }

    /** Particulas propias de cada elemento (hielo, fuego, veneno, agua, arena, naturaleza, arcano, rayo, piedra, luz, vacio). */
    void elemento(Location at, String elem, int min, double r, int cant) {
        switch (elem == null ? "" : elem) {
            case "fuego" -> { particula(at, min, Particle.FLAME, cant, r, 0.3, r, 0.02, null);
                              particula(at, min, Particle.LAVA, Math.max(1, cant / 6), r, 0.2, r, 0, null);
                              particula(at, min, Particle.LARGE_SMOKE, Math.max(1, cant / 4), r, 0.4, r, 0.01, null); }
            case "hielo" -> { particula(at, min, Particle.SNOWFLAKE, cant, r, 0.5, r, 0.02, null);
                              particula(at, min, Particle.ITEM_SNOWBALL, Math.max(1, cant / 2), r, 0.3, r, 0.05, null); }
            case "veneno" -> { particula(at, min, Particle.ITEM_SLIME, cant, r, 0.3, r, 0.05, null);
                               particula(at, min, Particle.DUST, cant, r, 0.6, r, 0, new Particle.DustOptions(Color.fromRGB(0x7CFF3A), 1.8f)); }
            case "agua" -> { particula(at, min, Particle.SPLASH, cant * 2, r, 0.3, r, 0.1, null);
                             particula(at, min, Particle.BUBBLE_POP, cant, r, 0.4, r, 0.02, null); }
            case "arena" -> { particula(at, min, Particle.CLOUD, cant / 2 + 1, r, 0.3, r, 0.02, null);
                              particula(at, min, Particle.DUST, cant, r, 0.5, r, 0, new Particle.DustOptions(Color.fromRGB(0xE8C77A), 1.6f)); }
            case "naturaleza" -> { particula(at, min, Particle.SPORE_BLOSSOM_AIR, cant, r, 0.5, r, 0, null);
                                   particula(at, min, Particle.HAPPY_VILLAGER, cant / 2 + 1, r, 0.4, r, 0, null); }
            case "arcano" -> { particula(at, min, Particle.WITCH, cant, r, 0.5, r, 0.05, null);
                               particula(at, min, Particle.END_ROD, cant / 2 + 1, r, 0.5, r, 0.03, null); }
            case "rayo" -> particula(at, min, Particle.ELECTRIC_SPARK, cant * 2, r, 0.6, r, 0.2, null);
            case "piedra" -> particula(at, min, Particle.CRIT, cant, r, 0.3, r, 0.2, null);
            case "luz" -> particula(at, min, Particle.END_ROD, cant, r, 0.6, r, 0.04, null);
            case "vacio" -> { particula(at, min, Particle.REVERSE_PORTAL, cant * 2, r, 0.6, r, 0.05, null);
                              particula(at, min, Particle.SCULK_SOUL, cant / 3 + 1, r, 0.3, r, 0.02, null); }
            case "rosa" -> particula(at, min, Particle.CHERRY_LEAVES, cant, r, 0.6, r, 0, null);
            default -> {}
        }
    }

    private void sprite(Location at, Color col, float desde, float hasta, int vida) {
        if (sprites.size() > 120) return;   // tope de dibujos a la vez en todo el server
        ItemStack it = new ItemStack(Material.PAPER);
        var meta = it.getItemMeta();
        meta.setItemModel(new NamespacedKey("astral", "fx/hongo_0"));
        it.setItemMeta(meta);
        it.setData(io.papermc.paper.datacomponent.DataComponentTypes.DYED_COLOR,
            io.papermc.paper.datacomponent.item.DyedItemColor.dyedItemColor(col));
        ItemDisplay d = at.getWorld().spawn(at, ItemDisplay.class, x -> {
            x.setVisibleByDefault(false);
            x.setPersistent(false);
            x.setItemStack(it);
            x.setBillboard(Display.Billboard.VERTICAL);
            x.setBrightness(new Display.Brightness(15, 15));
            x.setTransformation(new Transformation(new Vector3f(0, desde / 2, 0), new Quaternionf(), new Vector3f(desde, desde, desde), new Quaternionf()));
            x.setViewRange(1.5f);
            x.addScoreboardTag("astral.fx.sprite");
        });
        for (Player p : at.getWorld().getPlayers())
            if (nivel(p) >= ALTO && p.getLocation().distanceSquared(at) < 64 * 64) p.showEntity(this, d);
        Sprite s = new Sprite(); s.e = d; s.vida = vida; s.desde = desde; s.hasta = hasta;
        sprites.add(s);
    }

    private void animar() {
        for (Iterator<Sprite> it = sprites.iterator(); it.hasNext();) {
            Sprite s = it.next();
            if (!s.e.isValid()) { it.remove(); continue; }
            s.edad++;
            if (s.edad >= s.vida) { s.e.remove(); it.remove(); continue; }
            float f = (float) s.edad / s.vida;
            int frame = Math.min(frames - 1, (int) (f * frames));
            ItemStack item = s.e.getItemStack();
            var meta = item.getItemMeta();
            meta.setItemModel(new NamespacedKey("astral", "fx/hongo_" + frame));
            item.setItemMeta(meta);
            s.e.setItemStack(item);
            float sc = s.desde + (s.hasta - s.desde) * (float) Math.sqrt(f);
            s.e.setInterpolationDelay(0); s.e.setInterpolationDuration(1);
            s.e.setTransformation(new Transformation(new Vector3f(0, sc / 2, 0), new Quaternionf(), new Vector3f(sc, sc, sc), new Quaternionf()));
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
            if (!hayVisor(loc, ALTO)) continue;
            if (mueve) rastroArma(p, loc);
            auraArmadura(p, loc, mueve);
        }
        for (World w : Bukkit.getWorlds()) {
            if (w.getPlayers().isEmpty()) continue;
            for (Entity e : w.getEntitiesByClass(LivingEntity.class)) {
                Set<String> tags = e.getScoreboardTags();
                if (!tags.contains("astral.pet.evo")) continue;
                Color col = Color.WHITE;
                for (String t : tags) if (t.startsWith("astral.pet.") && colorMascota.containsKey(t.substring(11))) col = colorMascota.get(t.substring(11));
                Location l = e.getLocation(), antes = ultimo.put(e.getUniqueId(), l);
                if (antes == null || antes.getWorld() != l.getWorld() || antes.distanceSquared(l) < 0.01) continue;
                particula(l.clone().add(0, 0.3, 0), ALTO, Particle.DUST, 3, 0.15, 0.1, 0.15, 0, new Particle.DustOptions(col, 1.3f));
                particula(l.clone().add(0, 0.5, 0), ALTO, Particle.END_ROD, 1, 0.2, 0.2, 0.2, 0.005, null);
            }
        }
    }

    private void rastroArma(Player p, Location loc) {
        Map<String, String> d = datos(p.getInventory().getItemInMainHand());
        if (d == null) return;
        String tipo = d.getOrDefault("type", ""), w = d.getOrDefault("w", "");
        int tier = entero(d.get("tier"));
        Color col = colorTier.getOrDefault(tier, Color.WHITE);
        int cant = p.isSprinting() ? 4 : 2;
        Location pies = loc.clone().add(0, 0.15, 0).subtract(loc.getDirection().setY(0).normalize().multiply(0.4));
        if (w.equals("bow") || w.equals("crossbow")) {
            particula(pies.add(0, 0.6, 0), ALTO, Particle.DUST_COLOR_TRANSITION, cant, 0.15, 0.2, 0.15, 0,
                new Particle.DustTransition(col, Color.WHITE, 0.9f));
        } else if (tipo.equals("weapon") || tipo.equals("staff")) {
            particula(pies, ALTO, Particle.DUST, cant, 0.18, 0.05, 0.18, 0, new Particle.DustOptions(col, 1.1f));
            if (p.isSprinting()) particula(pies, ALTO, Particle.ELECTRIC_SPARK, 1, 0.2, 0.05, 0.2, 0.02, null);
        }
    }

    private void auraArmadura(Player p, Location loc, boolean mueve) {
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
            case "agua" -> particula(cuerpo, ALTO, Particle.DRIPPING_WATER, c, 0.3, 0.5, 0.3, 0, null);
            case "magia" -> particula(cuerpo, ALTO, Particle.ENCHANT, c * 3, 0.4, 0.6, 0.4, 0.4, null);
            case "furia" -> particula(cuerpo, ALTO, Particle.CRIT, c, 0.35, 0.5, 0.35, 0.05, null);
            case "bosque" -> particula(cuerpo, ALTO, Particle.CHERRY_LEAVES, 1, 0.4, 0.4, 0.4, 0, null);
            case "mina" -> particula(cuerpo, ALTO, Particle.WAX_ON, 1, 0.35, 0.5, 0.35, 0, null);
            case "esporas" -> particula(cuerpo, ALTO, Particle.SPORE_BLOSSOM_AIR, c, 0.4, 0.5, 0.4, 0, null);
            default -> {}
        }
        particula(cuerpo, ALTO, Particle.DUST, c, 0.35, 0.55, 0.35, 0, new Particle.DustOptions(col, 0.8f));
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
    private boolean hayVisor(Location at, int min) {
        for (Player p : at.getWorld().getPlayers()) if (nivel(p) >= min && p.getLocation().distanceSquared(at) < 64 * 64) return true;
        return false;
    }
    private <T> void particula(Location at, int min, Particle part, int count, double ox, double oy, double oz, double speed, T data) {
        for (Player p : at.getWorld().getPlayers()) {
            if (nivel(p) < min || p.getLocation().distanceSquared(at) > 48 * 48) continue;
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
