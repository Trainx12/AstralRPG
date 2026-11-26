package astral;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import dev.aurelium.auraskills.api.user.SkillsUser;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.attribute.Attribute;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Enemy;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityTargetEvent;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.PlayerChangedWorldEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.util.Vector;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Clases Segador, Invocador y Asesino (datapack-src/clases.py, 22/11/2026). Todos los numeros salen de clases.json.
 *
 * Segador (guadana): tajo en area (semicirculo) a varios mobs y cura al matar. La Cosecha se saco el 23/11.
 * Asesino (cuchillo): golpe por la espalda, veneno y invisibilidad (agachado + clic derecho; nunca en arenas PvP).
 * Invocador (libro): esqueletos que pelean y atraen a los mobs; cuestan mana y tienen recarga con barra.
 *
 * Las areas y el veneno solo pegan a mobs (nunca a jugadores, mascotas, NPCs ni invocaciones).
 * Recargas se ven en una barra arriba (BossBar violeta, como al picar vetas). Nunca YELLOW (BetterHud).
 */
public final class AstralClases extends JavaPlugin implements Listener {
    private final NamespacedKey kArma = new NamespacedKey("astral", "clase_arma");
    private final NamespacedKey kTier = new NamespacedKey("astral", "clase_tier");
    private final NamespacedKey kSet = new NamespacedKey("astral", "clase_set");
    private final NamespacedKey kDueno = new NamespacedKey("astral", "invocacion_dueno");
    private final NamespacedKey kInvTier = new NamespacedKey("astral", "invocacion_tier");
    static final String TAG_INV = "astral.invocacion";

    private JsonObject cfg, seg, ase, inv;
    private final Set<String> arenas = new HashSet<>();
    private final Map<String, Integer> mazmorras = new HashMap<>();
    private final Set<String> agresivos = new HashSet<>();
    private JsonObject agr;
    private final NamespacedKey kRapido = new NamespacedKey("astral", "mazmorra_rapido");
    private final NamespacedKey kAgua = new NamespacedKey("astral", "mazmorra_agua");
    private final Random rng = new Random();

    // Equipo puesto (se recalcula cada segundo)
    static final class Equipo {
        final Map<String, Integer> piezas = new HashMap<>();
        final Map<String, Double> stat = new HashMap<>();
        double get(String k) { return stat.getOrDefault(k, 0.0); }
        int piezas(String set) { return piezas.getOrDefault(set, 0); }
    }
    private final Map<UUID, Equipo> equipos = new HashMap<>();

    // Segador
    private final Map<UUID, Long> ultimoBarrido = new HashMap<>();
    // Asesino
    private final Map<UUID, Long> invisHasta = new HashMap<>();
    private final Map<UUID, Long> invisCdHasta = new HashMap<>();
    private final Map<UUID, Long> asesinoKill = new HashMap<>();
    static final class Veneno { UUID atacante; double porSegundo; int restante; }
    private final Map<UUID, Veneno> venenos = new HashMap<>();
    // Invocador
    private final Map<UUID, List<UUID>> invocaciones = new HashMap<>();
    private final Map<UUID, Long> invocacionFin = new HashMap<>();
    private final Map<UUID, Long> invCdHasta = new HashMap<>();
    private final Map<UUID, Double> invCdTotal = new HashMap<>();
    // Barras
    private final Map<UUID, BossBar> barrasRecarga = new HashMap<>();
    private boolean interno = false;   // dano que genera este plugin (no se vuelve a procesar)

    @Override
    public void onEnable() {
        try (var r = new InputStreamReader(Objects.requireNonNull(getResource("clases.json")), StandardCharsets.UTF_8)) {
            cfg = JsonParser.parseReader(r).getAsJsonObject();
        } catch (Exception e) {
            throw new IllegalStateException("No se pudo leer clases.json", e);
        }
        seg = cfg.getAsJsonObject("segador");
        ase = cfg.getAsJsonObject("asesino");
        inv = cfg.getAsJsonObject("invocador");
        cfg.getAsJsonArray("arenas").forEach(x -> arenas.add(x.getAsString()));
        cfg.getAsJsonObject("mazmorras").entrySet().forEach(x -> mazmorras.put(x.getKey(), x.getValue().getAsInt()));
        if (cfg.has("agresivos")) cfg.getAsJsonArray("agresivos").forEach(x -> agresivos.add(x.getAsString()));
        agr = cfg.has("agresivos_cfg") ? cfg.getAsJsonObject("agresivos_cfg") : null;
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::cadaSegundo, 20, 20);
        Bukkit.getScheduler().runTaskTimer(this, this::cadaMedioSegundo, 10, 10);
        // Invocaciones que quedaron de un reinicio: afuera.
        for (World w : Bukkit.getWorlds())
            for (Entity e : w.getEntities())
                if (e.getScoreboardTags().contains(TAG_INV) || e.getScoreboardTags().contains(TAG_INV + ".cartel")) e.remove();
    }

    @Override
    public void onDisable() {
        for (UUID dueno : new ArrayList<>(invocaciones.keySet())) quitarInvocaciones(dueno);
        barrasRecarga.values().forEach(BossBar::removeAll);
    }

    // ------------------------------------------------------------------------------------------ util
    private double d(JsonObject o, String k) { return o.get(k).getAsDouble(); }

    private String arma(ItemStack it) {
        if (it == null || !it.hasItemMeta()) return null;
        return it.getItemMeta().getPersistentDataContainer().get(kArma, PersistentDataType.STRING);
    }

    private int tierArma(ItemStack it) {
        Integer t = it.getItemMeta().getPersistentDataContainer().get(kTier, PersistentDataType.INTEGER);
        return t == null ? 1 : t;
    }

    private boolean esArena(World w) { return arenas.contains(w.getName()); }

    private boolean esInvocacion(Entity e) { return e != null && e.getScoreboardTags().contains(TAG_INV); }

    /** Tier del mob (etiqueta astral.mt# del datapack) o 0. */
    private int tierMob(Entity e) {
        for (int t = 10; t >= 1; t--) if (e.getScoreboardTags().contains("astral.mt" + t)) return t;
        return 0;
    }

    /** Jefe: mob sin tier dentro de una mazmorra (misma regla que astral_gameplay.sk). */
    private boolean esJefe(Entity e) {
        return tierMob(e) == 0 && tierMazmorra(e.getWorld()) > 0;
    }

    private int tierMazmorra(World w) {
        String n = w.getName();
        for (String pre : new String[]{"", "minecraft:", "world_minecraft_"})
            for (var x : mazmorras.entrySet()) if (n.equals(pre + x.getKey())) return x.getValue();
        return 0;
    }

    /** Objetivo valido para areas, veneno e invocaciones: un enemigo vivo (nunca jugador, mascota, NPC o invocacion). */
    private boolean enemigo(Entity e) {
        if (!(e instanceof LivingEntity le) || le.isDead() || e instanceof Player || e instanceof ArmorStand) return false;
        if (e.isInvulnerable() || !le.hasAI()) return false;
        Set<String> tags = e.getScoreboardTags();
        if (tags.contains("astral.pet") || tags.contains(TAG_INV)) return false;
        return e instanceof Enemy || tierMob(e) > 0;
    }

    private Equipo equipo(Player p) {
        return equipos.computeIfAbsent(p.getUniqueId(), u -> calcularEquipo(p));
    }

    private Equipo calcularEquipo(Player p) {
        Equipo q = new Equipo();
        JsonObject sets = cfg.getAsJsonObject("sets");
        for (ItemStack it : p.getInventory().getArmorContents()) {
            if (it == null || !it.hasItemMeta()) continue;
            PersistentDataContainer pdc = it.getItemMeta().getPersistentDataContainer();
            String set = pdc.get(kSet, PersistentDataType.STRING);
            Integer t = pdc.get(kTier, PersistentDataType.INTEGER);
            if (set == null || t == null || !sets.has(set)) continue;
            q.piezas.merge(set, 1, Integer::sum);
            JsonObject st = sets.getAsJsonObject(set).getAsJsonObject(String.valueOf(t));
            if (st == null) continue;
            for (var x : st.entrySet()) q.stat.merge(x.getKey(), x.getValue().getAsDouble() / 4, Double::sum);
        }
        return q;
    }

    private void danoInterno(LivingEntity victima, double dano, Player atacante) {
        interno = true;
        try { victima.damage(dano, atacante); } finally { interno = false; }
    }

    private void curar(Player p, double pct) {
        var max = p.getAttribute(Attribute.MAX_HEALTH);
        if (max == null || p.isDead()) return;
        p.setHealth(Math.min(max.getValue(), p.getHealth() + max.getValue() * pct / 100));
    }

    private void aviso(Player p, String s) { p.sendActionBar(net.kyori.adventure.text.Component.text(s)); }

    // ------------------------------------------------------------------------------------------ barras
    private BossBar barra(Map<UUID, BossBar> m, Player p, BarColor c) {
        return m.computeIfAbsent(p.getUniqueId(), u -> {
            BossBar b = Bukkit.createBossBar("", c, BarStyle.SEGMENTED_12);
            b.addPlayer(p);
            return b;
        });
    }

    private void sinBarra(Map<UUID, BossBar> m, Player p) {
        BossBar b = m.remove(p.getUniqueId());
        if (b != null) b.removeAll();
    }

    /** Recarga visible: la habilidad del arma que tiene en la mano (Invocador o Asesino). */
    private void actualizarRecarga(Player p, long ahora) {
        String a = arma(p.getInventory().getItemInMainHand());
        Long hasta = null; double total = 0; String nombre = null;
        if ("libro".equals(a)) {
            hasta = invCdHasta.get(p.getUniqueId()); total = invCdTotal.getOrDefault(p.getUniqueId(), 30.0);
            nombre = "☠ Invocacion";
        } else if ("cuchillo".equals(a) && !esArena(p.getWorld())) {
            hasta = invisCdHasta.get(p.getUniqueId()); total = d(ase, "invis_cd");
            nombre = "☾ Invisibilidad";
        }
        if (hasta == null || hasta <= ahora) { sinBarra(barrasRecarga, p); return; }
        double falta = (hasta - ahora) / 1000.0;
        BossBar b = barra(barrasRecarga, p, BarColor.PURPLE);
        b.setTitle(nombre + " lista en " + (int) Math.ceil(falta) + " s");
        b.setProgress(Math.max(0, Math.min(1, 1 - falta / total)));
    }

    // ------------------------------------------------------------------------------------------ tareas
    private void cadaSegundo() {
        long ahora = System.currentTimeMillis();
        for (Player p : Bukkit.getOnlinePlayers()) {
            equipos.put(p.getUniqueId(), calcularEquipo(p));
        }
        // Veneno del Asesino
        // 23/11: sobre una copia. El veneno puede matar al mob y alMorir lo saca del mapa (antes: ConcurrentModification).
        for (var x : new ArrayList<>(venenos.entrySet())) {
            Entity e = Bukkit.getEntity(x.getKey());
            Veneno v = x.getValue();
            Player a = Bukkit.getPlayer(v.atacante);
            if (!(e instanceof LivingEntity le) || le.isDead() || a == null || v.restante <= 0
                    || le.getScoreboardTags().contains("astral.sinestados")) { venenos.remove(x.getKey()); continue; }
            danoInterno(le, v.porSegundo, a);
            le.getWorld().spawnParticle(Particle.ITEM_SLIME, le.getLocation().add(0, le.getHeight() / 2, 0), 6, .3, .4, .3, 0);
            v.restante--;
        }
        // Invocaciones: tiempo, dueno y provocacion
        for (UUID dueno : new ArrayList<>(invocaciones.keySet())) {
            Player p = Bukkit.getPlayer(dueno);
            Long fin = invocacionFin.get(dueno);
            if (p == null || p.isDead() || fin == null || fin <= ahora) { quitarInvocaciones(dueno); continue; }
            List<UUID> lista = invocaciones.get(dueno);
            lista.removeIf(id -> { Entity e = Bukkit.getEntity(id); return e == null || e.isDead(); });
            if (lista.isEmpty()) { quitarInvocaciones(dueno); continue; }
            provocar(p, lista);
        }
    }

    private void cadaMedioSegundo() {
        long ahora = System.currentTimeMillis();
        for (Player p : Bukkit.getOnlinePlayers()) actualizarRecarga(p, ahora);
        mobsMazmorra();
        for (UUID dueno : new ArrayList<>(invocaciones.keySet())) {
            Player p = Bukkit.getPlayer(dueno);
            if (p == null) continue;
            for (UUID id : invocaciones.get(dueno)) {
                if (!(Bukkit.getEntity(id) instanceof Mob m) || m.isDead()) continue;
                guiar(p, m);
                golpear(p, m);
                cartel(m, p.getName());
            }
        }
        // Fin de la invisibilidad por tiempo
        for (var it = invisHasta.entrySet().iterator(); it.hasNext(); ) {
            var x = it.next();
            if (x.getValue() > ahora) continue;
            it.remove();
            Player p = Bukkit.getPlayer(x.getKey());
            if (p != null) mostrarEquipo(p);
        }
    }

    // ------------------------------------------------------------------------------------------ Mobs de mazmorra (23/11)
    private boolean esMundoAgresivo(World w) {
        String n = w.getName();
        for (String pre : new String[]{"", "minecraft:", "world_minecraft_"})
            if (n.startsWith(pre) && agresivos.contains(n.substring(pre.length()))) return true;
        return false;
    }

    /** Cada medio segundo: los mobs de mazmorra van un poco mas rapido, no se frenan en el agua y siempre buscan
     *  al jugador mas cercano. Nunca toca invocaciones, mascotas, NPCs ni mobs sin IA. */
    private void mobsMazmorra() {
        if (agr == null || agresivos.isEmpty()) return;
        double radio = d(agr, "busca_radio");
        for (World w : Bukkit.getWorlds()) {
            if (!esMundoAgresivo(w) || w.getPlayers().isEmpty()) continue;
            for (Mob m : w.getEntitiesByClass(Mob.class)) {
                if (m.isDead() || !m.hasAI() || m.isInvulnerable()) continue;
                Set<String> tags = m.getScoreboardTags();
                if (tags.contains(TAG_INV) || tags.contains("astral.pet") || tags.contains("astral.npc")) continue;
                if (!(m instanceof Enemy) && tierMob(m) == 0 && m.getAttribute(Attribute.ATTACK_DAMAGE) == null) continue;
                boolean jefe = esJefe(m);
                var vel = m.getAttribute(Attribute.MOVEMENT_SPEED);
                if (vel != null && !jefe) {
                    if (vel.getModifier(kRapido) == null)
                        vel.addModifier(new org.bukkit.attribute.AttributeModifier(kRapido, d(agr, "velocidad_pct") / 100,
                                org.bukkit.attribute.AttributeModifier.Operation.ADD_SCALAR));
                    boolean agua = m.isInWater();
                    if (agua && vel.getModifier(kAgua) == null)
                        vel.addModifier(new org.bukkit.attribute.AttributeModifier(kAgua, d(agr, "agua_pct") / 100,
                                org.bukkit.attribute.AttributeModifier.Operation.ADD_SCALAR));
                    else if (!agua && vel.getModifier(kAgua) != null) vel.removeModifier(kAgua);
                }
                var ef = m.getAttribute(Attribute.WATER_MOVEMENT_EFFICIENCY);
                if (ef != null && ef.getBaseValue() < d(agr, "eficiencia_agua")) ef.setBaseValue(d(agr, "eficiencia_agua"));
                var fr = m.getAttribute(Attribute.FOLLOW_RANGE);
                if (fr != null && fr.getBaseValue() < d(agr, "rango_min")) fr.setBaseValue(d(agr, "rango_min"));
                LivingEntity t = m.getTarget();
                if (t != null && t.isValid() && !t.isDead()) continue;
                Player mejor = null; double dist = radio * radio;
                for (Player p : w.getPlayers()) {
                    if (p.getGameMode() != org.bukkit.GameMode.SURVIVAL && p.getGameMode() != org.bukkit.GameMode.ADVENTURE) continue;
                    if (p.isDead() || invisible(p)) continue;
                    double d2 = p.getLocation().distanceSquared(m.getLocation());
                    if (d2 < dist && m.hasLineOfSight(p)) { dist = d2; mejor = p; }
                }
                if (mejor != null) m.setTarget(mejor);
            }
        }
    }

    // ------------------------------------------------------------------------------------------ Segador
    private List<LivingEntity> enArea(Player p, double radio, boolean soloAdelante, Entity excluir, int max) {
        Location c = p.getLocation();
        Vector mira = c.getDirection().setY(0);
        if (mira.lengthSquared() < 1e-6) mira = new Vector(0, 0, 1);
        mira.normalize();
        double cos = Math.cos(Math.toRadians(d(seg, "angulo")));
        List<LivingEntity> out = new ArrayList<>();
        for (Entity e : p.getNearbyEntities(radio, radio / 2 + 1, radio)) {
            if (e == excluir || !enemigo(e)) continue;
            Vector hacia = e.getLocation().toVector().subtract(c.toVector()).setY(0);
            if (hacia.length() > radio) continue;
            if (soloAdelante && hacia.lengthSquared() > 1e-6 && hacia.normalize().dot(mira) < cos - 1e-9) continue;
            if (!p.hasLineOfSight(e)) continue;
            out.add((LivingEntity) e);
        }
        out.sort(Comparator.comparingDouble(e -> e.getLocation().distanceSquared(c)));
        return out.size() > max ? out.subList(0, max) : out;
    }

    private void barrido(Player p, LivingEntity victima, double golpe) {
        long ahora = System.currentTimeMillis();
        if (ahora - ultimoBarrido.getOrDefault(p.getUniqueId(), 0L) < 600) return;  // ~golpe cargado de guadana
        ultimoBarrido.put(p.getUniqueId(), ahora);
        Equipo q = equipo(p);
        double radio = d(seg, "radio") + q.get("radio");
        double pct = q.piezas("segador") >= 4 ? d(seg, "barrido_pct_set") : d(seg, "barrido_pct");
        double dano = golpe * pct / 100 * (1 + q.get("tajo") / 100);
        for (LivingEntity e : enArea(p, radio, true, victima, (int) d(seg, "barrido_max"))) danoInterno(e, dano, p);
        Location c = p.getLocation().add(0, 1, 0);
        Vector mira = c.getDirection().setY(0).normalize();
        for (int i = -4; i <= 4; i++) {
            Vector v = mira.clone().rotateAroundY(Math.toRadians(i * 20)).multiply(radio * .7);
            p.getWorld().spawnParticle(Particle.SWEEP_ATTACK, c.clone().add(v), 1, 0, 0, 0, 0);
        }
        efecto(p, "tajo", p.getLocation());
    }

    // ------------------------------------------------------------------------------------------ Asesino
    private boolean porLaEspalda(Player p, LivingEntity v) {
        Vector frente = v.getLocation().getDirection().setY(0);
        Vector hacia = p.getLocation().toVector().subtract(v.getLocation().toVector()).setY(0);
        if (frente.lengthSquared() < 1e-6 || hacia.lengthSquared() < 1e-6) return false;
        double ang = Math.toDegrees(frente.normalize().angle(hacia.normalize()));
        return ang >= 180 - d(ase, "espalda_angulo");
    }

    private void invisibilidad(Player p) {
        if (esArena(p.getWorld())) { aviso(p, "☾ La invisibilidad no funciona en PvP"); return; }
        long ahora = System.currentTimeMillis();
        Long cd = invisCdHasta.get(p.getUniqueId());
        if (cd != null && cd > ahora) { aviso(p, "☾ Invisibilidad en recarga: " + (int) Math.ceil((cd - ahora) / 1000.0) + " s"); return; }
        int seg = (int) d(ase, "invis_seg");
        invisHasta.put(p.getUniqueId(), ahora + seg * 1000L);
        invisCdHasta.put(p.getUniqueId(), ahora + (long) (d(ase, "invis_cd") * 1000));
        p.addPotionEffect(new PotionEffect(PotionEffectType.INVISIBILITY, seg * 20, 0, false, false, false));
        // Los demas no ven la armadura ni el arma flotando.
        Map<EquipmentSlot, ItemStack> vacio = new EnumMap<>(EquipmentSlot.class);
        for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS,
                EquipmentSlot.FEET, EquipmentSlot.HAND, EquipmentSlot.OFF_HAND}) vacio.put(s, new ItemStack(org.bukkit.Material.AIR));
        for (Player o : p.getWorld().getPlayers()) if (o != p) o.sendEquipmentChange(p, vacio);
        // Los mobs comunes lo pierden de vista (los jefes no).
        for (Entity e : p.getNearbyEntities(32, 16, 32))
            if (e instanceof Mob m && p.equals(m.getTarget()) && !esJefe(m)) m.setTarget(null);
        p.getWorld().spawnParticle(Particle.LARGE_SMOKE, p.getLocation().add(0, 1, 0), 20, .4, .6, .4, .02);
        p.getWorld().playSound(p.getLocation(), Sound.ENTITY_ILLUSIONER_MIRROR_MOVE, 1f, 1.3f);
    }

    private boolean invisible(Player p) {
        Long h = invisHasta.get(p.getUniqueId());
        return h != null && h > System.currentTimeMillis();
    }

    private void terminarInvisibilidad(Player p) {
        if (invisHasta.remove(p.getUniqueId()) == null) return;
        p.removePotionEffect(PotionEffectType.INVISIBILITY);
        mostrarEquipo(p);
    }

    private void mostrarEquipo(Player p) {
        Map<EquipmentSlot, ItemStack> real = new EnumMap<>(EquipmentSlot.class);
        var inv = p.getInventory();
        real.put(EquipmentSlot.HEAD, inv.getHelmet()); real.put(EquipmentSlot.CHEST, inv.getChestplate());
        real.put(EquipmentSlot.LEGS, inv.getLeggings()); real.put(EquipmentSlot.FEET, inv.getBoots());
        real.put(EquipmentSlot.HAND, inv.getItemInMainHand()); real.put(EquipmentSlot.OFF_HAND, inv.getItemInOffHand());
        real.replaceAll((k, v) -> v == null ? new ItemStack(org.bukkit.Material.AIR) : v);
        for (Player o : p.getWorld().getPlayers()) if (o != p) o.sendEquipmentChange(p, real);
    }

    // ------------------------------------------------------------------------------------------ Invocador
    private void invocar(Player p, int t) {
        long ahora = System.currentTimeMillis();
        Long cd = invCdHasta.get(p.getUniqueId());
        if (cd != null && cd > ahora) { aviso(p, "☠ Invocacion en recarga: " + (int) Math.ceil((cd - ahora) / 1000.0) + " s"); return; }
        JsonObject req = cfg.getAsJsonObject("libro_nivel");
        int nivel = req.get(String.valueOf(t)).getAsInt();
        SkillsUser user = AuraSkillsApi.get().getUser(p.getUniqueId());
        if (user == null) return;
        if (user.getSkillLevel(Skills.SORCERY) < nivel) { aviso(p, "Necesitas Hechiceria " + nivel + " para este libro"); return; }
        double costo = inv.getAsJsonObject("mana").get(String.valueOf(t)).getAsDouble();
        if (user.getMana() < costo) { aviso(p, "Te falta mana: " + (int) costo + " (tenes " + (int) user.getMana() + ")"); return; }
        user.setMana(user.getMana() - costo);
        quitarInvocaciones(p.getUniqueId());
        Equipo q = equipo(p);
        JsonObject st = inv.getAsJsonObject("stats").getAsJsonObject(String.valueOf(t));
        double vida = st.get("vida").getAsDouble() * (1 + q.get("ivida") / 100);
        double dano = st.get("dano").getAsDouble() * (1 + q.get("idano") / 100);
        int n = inv.getAsJsonObject("cantidad").get(String.valueOf(t)).getAsInt();
        List<UUID> lista = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            double a = 2 * Math.PI * i / n;
            Location l = p.getLocation().add(Math.cos(a) * 1.5, 0, Math.sin(a) * 1.5);
            LivingEntity e = aparecer(l);
            if (e == null) continue;
            e.addScoreboardTag(TAG_INV);
            e.addScoreboardTag("astral.pet");     // los hechizos y el datapack no las tocan
            e.addScoreboardTag("astral.seen");    // sin tier ni elite del datapack
            e.addScoreboardTag("clearlag_exclude");
            e.getPersistentDataContainer().set(kDueno, PersistentDataType.STRING, p.getUniqueId().toString());
            e.getPersistentDataContainer().set(kInvTier, PersistentDataType.STRING, String.valueOf(t));
            e.setPersistent(false);
            e.setRemoveWhenFarAway(false);
            e.setCanPickupItems(false);
            var mh = e.getAttribute(Attribute.MAX_HEALTH);
            if (mh != null) { mh.setBaseValue(vida); e.setHealth(vida); }
            var ad = e.getAttribute(Attribute.ATTACK_DAMAGE);
            if (ad != null) ad.setBaseValue(dano);
            e.setCustomNameVisible(true);
            cartel(e, p.getName());
            if (e.getEquipment() != null) e.getEquipment().clear();
            lista.add(e.getUniqueId());
            e.getWorld().spawnParticle(Particle.SOUL, l.clone().add(0, 1, 0), 15, .3, .6, .3, .02);
        }
        if (lista.isEmpty()) return;
        invocaciones.put(p.getUniqueId(), lista);
        invocacionFin.put(p.getUniqueId(), ahora + (long) (d(inv, "duracion") * 1000));
        double recarga = d(inv, "recarga") * (1 - q.get("cdr") / 100);
        invCdHasta.put(p.getUniqueId(), ahora + (long) (recarga * 1000));
        invCdTotal.put(p.getUniqueId(), recarga);
        p.getWorld().playSound(p.getLocation(), Sound.ENTITY_EVOKER_PREPARE_SUMMON, 1f, 1f);
        efecto(p, "invocar", p.getLocation());
    }

    // ------------------------------------------------------------------------------------------ Efectos (22/11)
    // 23/11: sin pose del cuerpo (BetterModel limb): saco al dueno del juego y escondia su armadura.
    /** Efecto suelto (models/astral_fx_clases): el tajo del barrido o el circulo de invocar, en los pies del jugador
     *  mirando adonde mira. No reemplaza al jugador, asi que la armadura se sigue viendo. */
    private void efecto(Player p, String anim, Location donde) {
        if (invisible(p) || !Bukkit.getPluginManager().isPluginEnabled("BetterModel")) return;
        try {
            Location l = donde.clone();
            l.setPitch(0);
            Poses.efecto(l, anim);
        } catch (Throwable ex) {
            getLogger().warning("No se pudo mostrar " + anim + ": " + ex);
        }
    }

    /** Aparte para que la clase no cargue BetterModel si no esta instalado. */
    static final class Poses {
        static void efecto(Location l, String anim) {
            var r = kr.toxicity.model.api.BetterModel.model("astral_fx_clases").orElse(null);
            if (r == null || r.animation(anim).isEmpty()) return;
            var t = r.create(kr.toxicity.model.bukkit.util.BukkitWrappersKt.wrap(l));
            for (Player o : l.getWorld().getPlayers())
                if (o.getLocation().distanceSquared(l) < 48 * 48) t.spawn(kr.toxicity.model.bukkit.util.BukkitWrappersKt.wrap(o));
            var mod = new kr.toxicity.model.api.animation.AnimationModifier(0, 0,
                    kr.toxicity.model.api.animation.AnimationIterator.Type.PLAY_ONCE,
                    kr.toxicity.model.api.util.function.FloatSupplier.of(1f));
            if (!t.animate(anim, mod, t::close)) t.close();
        }

    }

    /** Cartel arriba de la invocacion: "Invocacion de <jugador> · Tier N" y abajo "❤ vida / maxima".
     *  23/11: el modelo de BetterModel esconde el nombre del mob, asi que va en un TextDisplay montado encima. */
    private final Map<UUID, UUID> carteles = new HashMap<>();
    private void cartel(LivingEntity e, String dueno) {
        var mh = e.getAttribute(Attribute.MAX_HEALTH);
        double max = mh == null ? e.getHealth() : mh.getValue();
        var fmt = java.text.NumberFormat.getIntegerInstance(Locale.GERMANY);
        String tier = e.getPersistentDataContainer().getOrDefault(kInvTier, PersistentDataType.STRING, "?");
        var texto = net.kyori.adventure.text.Component.text("Invocacion de " + dueno + " · Tier " + tier,
                        net.kyori.adventure.text.format.TextColor.color(0xB98BFF))
                .append(net.kyori.adventure.text.Component.newline())
                .append(net.kyori.adventure.text.Component.text("❤ " + fmt.format(Math.ceil(Math.max(0, e.getHealth()))) + " / " + fmt.format(Math.round(max)),
                        net.kyori.adventure.text.format.NamedTextColor.RED));
        e.customName(texto);
        Entity d = carteles.containsKey(e.getUniqueId()) ? Bukkit.getEntity(carteles.get(e.getUniqueId())) : null;
        org.bukkit.entity.TextDisplay td = d instanceof org.bukkit.entity.TextDisplay x && x.isValid() ? x : null;
        if (td == null) {
            td = e.getWorld().spawn(e.getLocation().add(0, e.getHeight() + .35, 0), org.bukkit.entity.TextDisplay.class, x -> {
                x.setPersistent(false);
                x.setBillboard(org.bukkit.entity.Display.Billboard.CENTER);
                x.addScoreboardTag(TAG_INV + ".cartel");
                x.setBackgroundColor(org.bukkit.Color.fromARGB(90, 0, 0, 0));
                x.setTransformation(new org.bukkit.util.Transformation(new org.joml.Vector3f(0, .45f, 0),
                        new org.joml.AxisAngle4f(), new org.joml.Vector3f(.8f, .8f, .8f), new org.joml.AxisAngle4f()));
            });
            e.addPassenger(td);
            carteles.put(e.getUniqueId(), td.getUniqueId());
        }
        td.text(texto);
    }

    /** La invocacion pega sola al enemigo que tiene cerca (no depende de la IA del mob, que con el modelo no
     *  siempre ataca). El golpe pasa por alPegar: credito del dueno y la mitad a jefes. */
    private final Map<UUID, Long> ultimoGolpe = new HashMap<>();
    private void golpear(Player p, Mob m) {
        LivingEntity t = m.getTarget();
        if (t == null || !enemigo(t) || !t.getWorld().equals(m.getWorld())) return;
        if (t.getLocation().distanceSquared(m.getLocation()) > 3.2 * 3.2) { m.getPathfinder().moveTo(t, 1.25); return; }
        long ahora = System.currentTimeMillis();
        if (ahora - ultimoGolpe.getOrDefault(m.getUniqueId(), 0L) < 900) return;
        ultimoGolpe.put(m.getUniqueId(), ahora);
        var ad = m.getAttribute(Attribute.ATTACK_DAMAGE);
        m.swingMainHand();
        t.damage(ad == null ? 1 : ad.getValue(), m);
        // El mob golpeado se da vuelta contra la invocacion (los jefes no): asi tambien la lastiman.
        if (t instanceof Mob tm && !esJefe(tm)) tm.setTarget(m);
    }

    private void actualizarCartel(Entity e) {
        if (!(e instanceof LivingEntity le) || le.isDead()) return;
        String s = e.getPersistentDataContainer().get(kDueno, PersistentDataType.STRING);
        if (s == null) return;
        var dueno = Bukkit.getOfflinePlayer(UUID.fromString(s));
        cartel(le, dueno.getName() == null ? "?" : dueno.getName());
    }

    /** Despues de cualquier golpe o curacion (ya con la escala aplicada), el cartel muestra la vida nueva. */
    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void cartelAlRecibir(EntityDamageEvent e) {
        if (esInvocacion(e.getEntity())) Bukkit.getScheduler().runTask(this, () -> actualizarCartel(e.getEntity()));
    }

    private LivingEntity aparecer(Location l) {
        if (Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) {
            try {
                var am = io.lumine.mythic.bukkit.MythicBukkit.inst().getMobManager().spawnMob(cfg.get("modelo").getAsString(), l);
                if (am != null && am.getEntity().getBukkitEntity() instanceof LivingEntity le) return le;
            } catch (Throwable ignored) {
            }
        }
        return l.getWorld().spawn(l, org.bukkit.entity.Zombie.class, z -> {
            z.setShouldBurnInDay(false);
            z.setAdult();
        });
    }

    private void quitarInvocaciones(UUID dueno) {
        List<UUID> lista = invocaciones.remove(dueno);
        invocacionFin.remove(dueno);
        if (lista == null) return;
        for (UUID id : lista) {
            UUID c = carteles.remove(id);
            Entity cart = c == null ? null : Bukkit.getEntity(c);
            if (cart != null) cart.remove();
            ultimoGolpe.remove(id);
            Entity e = Bukkit.getEntity(id);
            if (e == null) continue;
            e.getWorld().spawnParticle(Particle.SOUL, e.getLocation().add(0, 1, 0), 10, .3, .5, .3, .02);
            e.remove();
        }
    }

    private Player duenoDe(Entity e) {
        String s = e.getPersistentDataContainer().get(kDueno, PersistentDataType.STRING);
        return s == null ? null : Bukkit.getPlayer(UUID.fromString(s));
    }

    /** Atacar al enemigo mas cercano del dueno; si no hay, seguirlo. Muy lejos: vuelve a su lado. */
    private void guiar(Player p, Mob m) {
        if (!m.getWorld().equals(p.getWorld()) || m.getLocation().distance(p.getLocation()) > d(inv, "distancia_max")) {
            m.teleport(p.getLocation());
            m.setTarget(null);
            return;
        }
        LivingEntity t = m.getTarget();
        if (t != null && (!enemigo(t) || t.getLocation().distance(p.getLocation()) > 16)) { m.setTarget(null); t = null; }
        if (t == null) {
            LivingEntity mejor = null; double dist = 144;
            for (Entity e : p.getNearbyEntities(12, 6, 12)) {
                if (!enemigo(e)) continue;
                double d2 = e.getLocation().distanceSquared(m.getLocation());
                if (d2 < dist) { dist = d2; mejor = (LivingEntity) e; }
            }
            if (mejor != null) m.setTarget(mejor);
            else if (m.getLocation().distance(p.getLocation()) > 4) m.getPathfinder().moveTo(p.getLocation(), 1.2);
        }
    }

    /** Mini tanques: los mobs comunes que persiguen al dueno cerca de una invocacion pasan a atacarla. */
    private void provocar(Player p, List<UUID> lista) {
        double r = d(inv, "provoca_radio"), prob = d(inv, "provoca_prob");
        for (UUID id : lista) {
            if (!(Bukkit.getEntity(id) instanceof LivingEntity yo)) continue;
            for (Entity e : yo.getNearbyEntities(r, r / 2, r)) {
                if (!(e instanceof Mob m) || !enemigo(m) || esJefe(m)) continue;
                if (m.getTarget() instanceof Player && rng.nextDouble() < prob) m.setTarget(yo);
            }
        }
    }

    // ------------------------------------------------------------------------------------------ eventos
    // 23/11: sin ignoreCancelled. Bukkit manda el clic en el AIRE ya "cancelado" (no hay bloque), asi que el libro
    // solo invocaba mirando un bloque. Se respeta solo si otro plugin nego usar el item.
    @EventHandler
    public void alUsar(PlayerInteractEvent e) {
        if (e.getHand() != EquipmentSlot.HAND) return;
        if (e.useItemInHand() == org.bukkit.event.Event.Result.DENY) return;
        if (e.getAction() != Action.RIGHT_CLICK_AIR && e.getAction() != Action.RIGHT_CLICK_BLOCK) return;
        Player p = e.getPlayer();
        ItemStack it = p.getInventory().getItemInMainHand();
        String a = arma(it);
        if (a == null) return;
        switch (a) {
            // 23/11: Cosecha retirada (pedido del dueno). La guadana solo pega en area con el tajo.
            case "cuchillo" -> { if (p.isSneaking()) { e.setCancelled(true); invisibilidad(p); } }
            case "libro" -> { e.setCancelled(true); invocar(p, tierArma(it)); }
            default -> { }
        }
    }

    @EventHandler(priority = EventPriority.LOWEST, ignoreCancelled = true)
    public void protegerInvocaciones(EntityDamageByEntityEvent e) {
        Entity atacante = e.getDamager();
        if (atacante instanceof Projectile pr && pr.getShooter() instanceof Entity s) atacante = s;
        // Nadie del lado de los jugadores lastima a una invocacion; las invocaciones no lastiman jugadores ni mascotas.
        if (esInvocacion(e.getEntity()) && (atacante instanceof Player || esInvocacion(atacante))) { e.setCancelled(true); return; }
        if (esInvocacion(atacante) && (e.getEntity() instanceof Player || e.getEntity().getScoreboardTags().contains("astral.pet")))
            e.setCancelled(true);
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void alPegar(EntityDamageByEntityEvent e) {
        if (interno) return;
        Entity atacante = e.getDamager();
        // Invocacion pegando: credito del dueno (botin, XP y almas) y la mitad a jefes.
        if (esInvocacion(atacante) && e.getEntity() instanceof LivingEntity v) {
            if (esJefe(v)) e.setDamage(e.getDamage() * d(inv, "jefe_dano"));
            Player dueno = duenoDe(atacante);
            if (dueno != null) v.setKiller(dueno);
            return;
        }
        // Un mob pegandole a una invocacion: como a un jugador del tier (dano del mob x defensa).
        if (esInvocacion(e.getEntity()) && !(atacante instanceof Player)) {
            Entity fuente = atacante instanceof Projectile pr && pr.getShooter() instanceof Entity s ? s : atacante;
            int t = tierMob(fuente);
            double k = 1;
            JsonObject dm = cfg.getAsJsonObject("dano_mob");
            if (t > 0) k = dm.get(String.valueOf(t)).getAsDouble();
            else {
                int tz = tierMazmorra(fuente.getWorld());
                JsonObject dj = cfg.has("dano_jefe") ? cfg.getAsJsonObject("dano_jefe") : dm;
                if (tz > 0) k = dj.get(String.valueOf(tz)).getAsDouble() * d(inv, "jefe_recibe");
            }
            double def = 0;
            JsonObject sts = inv.getAsJsonObject("stats");
            String tierInv = e.getEntity().getPersistentDataContainer().getOrDefault(kInvTier, PersistentDataType.STRING, "");
            if (sts.has(tierInv)) def = sts.getAsJsonObject(tierInv).get("defensa").getAsDouble();
            e.setDamage(e.getDamage() * k * 100 / (def + 100));
            return;
        }
        if (!(atacante instanceof Player p) || !(e.getEntity() instanceof LivingEntity v)) return;
        ItemStack it = p.getInventory().getItemInMainHand();
        String a = arma(it);
        if (a == null) return;
        if (e.getCause() != EntityDamageEvent.DamageCause.ENTITY_ATTACK && e.getCause() != EntityDamageEvent.DamageCause.ENTITY_SWEEP_ATTACK) return;
        Equipo q = equipo(p);
        if (a.equals("guadana")) {
            if (v instanceof Player) return;
            e.setDamage(e.getDamage() * (1 + q.get("guadana") / 100));
            barrido(p, v, e.getDamage());
        } else if (a.equals("cuchillo")) {
            boolean espalda = invisible(p) || porLaEspalda(p, v);
            terminarInvisibilidad(p);
            if (v instanceof Player) {
                // PvP: lo suma astral_pvp (gameplay.py) con esta etiqueta, despues de su formula.
                if (espalda && esArena(p.getWorld())) {
                    p.addScoreboardTag("astral.espalda");
                    Bukkit.getScheduler().runTask(this, () -> p.removeScoreboardTag("astral.espalda"));
                }
                return;
            }
            double dano = e.getDamage();
            if (espalda) {
                dano *= 1 + d(ase, "espalda_pct") / 100;
                v.getWorld().spawnParticle(Particle.CRIT, v.getLocation().add(0, v.getHeight() * .7, 0), 12, .3, .3, .3, .2);
            }
            Long k = asesinoKill.remove(p.getUniqueId());
            if (k != null && k > System.currentTimeMillis())
                dano *= esJefe(v) ? d(ase, "set_kill_mult_jefe") : d(ase, "set_kill_mult");
            e.setDamage(dano);
            // 26/11: a los jefes no se los envenena (AstralJefesInmunes les pone esta etiqueta).
            if (v.getScoreboardTags().contains("astral.sinestados")) { venenos.remove(v.getUniqueId()); return; }
            Veneno ve = new Veneno();
            ve.atacante = p.getUniqueId();
            ve.porSegundo = dano * d(ase, "veneno_pct") / 100;
            ve.restante = (int) d(ase, "veneno_seg");
            venenos.put(v.getUniqueId(), ve);
        }
    }

    /** Set completo de Invocador: menos dano mientras tenga invocaciones (corre despues de la escala de Skript). */
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void alRecibir(EntityDamageEvent e) {
        if (!(e.getEntity() instanceof Player p)) return;
        if (invocaciones.containsKey(p.getUniqueId()) && equipo(p).piezas("invocador") >= 4)
            e.setDamage(e.getDamage() * (1 - d(inv, "set_menos_dano") / 100));
    }

    @EventHandler
    public void alMorir(EntityDeathEvent e) {
        LivingEntity v = e.getEntity();
        if (esInvocacion(v)) {
            e.getDrops().clear(); e.setDroppedExp(0);
            UUID c = carteles.remove(v.getUniqueId());
            if (c != null && Bukkit.getEntity(c) != null) Bukkit.getEntity(c).remove();
            return;
        }
        venenos.remove(v.getUniqueId());
        Player p = v.getKiller();
        if (p == null || v instanceof Player) return;
        String a = arma(p.getInventory().getItemInMainHand());
        if ("guadana".equals(a)) {
            curar(p, d(seg, "cura_alma") * (1 + equipo(p).get("cura") / 100));
            v.getWorld().spawnParticle(Particle.SOUL, v.getLocation().add(0, 1, 0), 6, .2, .4, .2, .03);
        } else if ("cuchillo".equals(a) && equipo(p).piezas("asesino") >= 4) {
            asesinoKill.put(p.getUniqueId(), System.currentTimeMillis() + (long) (d(ase, "set_kill_seg") * 1000));
        }
    }

    @EventHandler(ignoreCancelled = true)
    public void alApuntar(EntityTargetEvent e) {
        Entity t = e.getTarget();
        // Invocaciones: nunca contra jugadores, mascotas u otras invocaciones.
        if (esInvocacion(e.getEntity()) && t != null && (t instanceof Player || t.getScoreboardTags().contains("astral.pet"))) {
            e.setCancelled(true);
            return;
        }
        // Asesino invisible: los mobs comunes no lo eligen.
        if (t instanceof Player p && invisible(p) && !esJefe(e.getEntity())) e.setCancelled(true);
    }

    @EventHandler
    public void alSalir(PlayerQuitEvent e) { limpiar(e.getPlayer()); equipos.remove(e.getPlayer().getUniqueId()); }

    @EventHandler
    public void alMorirJugador(PlayerDeathEvent e) {
        limpiar(e.getPlayer());
    }

    @EventHandler
    public void alCambiarMundo(PlayerChangedWorldEvent e) { limpiar(e.getPlayer()); }

    private void limpiar(Player p) {
        quitarInvocaciones(p.getUniqueId());
        terminarInvisibilidad(p);
        sinBarra(barrasRecarga, p);
    }
}
