package astral;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.trait.Trait;
import dev.aurelium.auraskills.api.trait.TraitModifier;
import dev.aurelium.auraskills.api.trait.Traits;
import dev.aurelium.auraskills.api.user.SkillsUser;
import dev.aurelium.auraskills.api.util.AuraSkillsModifier;
import org.bukkit.Bukkit;
import org.bukkit.Particle;
import org.bukkit.attribute.Attribute;
import org.bukkit.damage.DamageSource;
import org.bukkit.damage.DamageType;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Reforja de gemas (gemas.py, 7d). Todo sale de gemas.json (generado por gemas.py).
 * - Cada segundo: mana y critico (modificadores de AuraSkills "astral_gema_<rasgo>") y plata del Topacio
 *   (etiquetas astral.gp0..gp5 en binario, que lee astral_economia.sk sin correr comandos).
 * - En cada golpe (tambien PvP): Opalo +dano a elites y jefes (barra de jefe de MythicMobs o etiquetas),
 *   Onix robo de vida (40%, % de la vida maxima, una cura cada medio segundo) y espinas de la armadura de Onix.
 * Al salir o apagar se borran los modificadores y las etiquetas.
 */
public final class AstralGemas extends JavaPlugin implements Listener {
    private static final String PREFIX = "astral_gema_";
    private static final String[] TRAITS = {"max_mana", "mana_regen", "crit_chance", "crit_damage"};
    private final Map<String, Object[][]> traits = new HashMap<>();
    private final Map<String, Map<String, Double>> efectos = new HashMap<>();
    private final Map<UUID, String> last = new HashMap<>();
    private final Map<UUID, Integer> ultimaCura = new HashMap<>();
    private final List<String> tagsJefes = new ArrayList<>();
    private double roboProb = 0.4, espinasProb = 0.1, espinasJefes = 0.5;
    private int roboEspera = 10;
    private boolean espinasActivas;

    @Override
    public void onEnable() {
        try (var in = getResource("gemas.json")) {
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            for (var e : root.getAsJsonObject("traits").entrySet()) {
                JsonArray arr = e.getValue().getAsJsonArray();
                Object[][] list = new Object[arr.size()][];
                for (int i = 0; i < arr.size(); i++) {
                    JsonArray m = arr.get(i).getAsJsonArray();
                    list[i] = new Object[]{m.get(0).getAsString(), m.get(1).getAsString(), m.get(2).getAsDouble()};
                }
                traits.put(e.getKey(), list);
            }
            for (var e : root.getAsJsonObject("efectos").entrySet()) {
                Map<String, Double> m = new HashMap<>();
                for (var x : e.getValue().getAsJsonObject().entrySet()) m.put(x.getKey(), x.getValue().getAsDouble());
                efectos.put(e.getKey(), m);
            }
            roboProb = root.get("robo_prob").getAsDouble();
            roboEspera = root.get("robo_espera").getAsInt();
            espinasProb = root.get("espinas_prob").getAsDouble();
            espinasJefes = root.get("espinas_jefes").getAsDouble();
            for (var t : root.getAsJsonArray("tags_jefes")) tagsJefes.add(t.getAsString());
        } catch (Exception ex) {
            getLogger().severe("No se pudo leer gemas.json: " + ex);
        }
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, () -> {
            for (Player p : Bukkit.getOnlinePlayers()) scan(p);
        }, 40L, 20L);
        getLogger().info("Gemas cargadas: " + traits.size() + " con AuraSkills, " + efectos.size() + " con efectos propios.");
    }

    @Override
    public void onDisable() {
        for (Player p : Bukkit.getOnlinePlayers()) clear(p);
        last.clear();
    }

    @EventHandler
    public void quit(PlayerQuitEvent e) {
        clear(e.getPlayer());
        last.remove(e.getPlayer().getUniqueId());
        ultimaCura.remove(e.getPlayer().getUniqueId());
    }

    // ------------------------------------------------------------ lectura de gemas
    private static boolean gema(String key, String variant) {
        return key.startsWith("astral:gema_") && key.contains(variant);
    }

    private Map<String, Double> efectos(ItemStack item, String variant) {
        Map<String, Double> sum = new HashMap<>();
        if (item == null || item.isEmpty() || !item.hasItemMeta()) return sum;
        for (Enchantment ench : item.getEnchantments().keySet()) {
            String key = ench.getKey().toString();
            if (!gema(key, variant)) continue;
            Map<String, Double> m = efectos.get(key);
            if (m != null) m.forEach((k, v) -> sum.merge(k, v, Double::sum));
        }
        return sum;
    }

    private void traitsDe(Map<String, Double> sum, ItemStack item, String variant) {
        if (item == null || item.isEmpty() || !item.hasItemMeta()) return;
        for (Enchantment ench : item.getEnchantments().keySet()) {
            String key = ench.getKey().toString();
            if (!gema(key, variant)) continue;
            Object[][] list = traits.get(key);
            if (list == null) continue;
            for (Object[] m : list) sum.merge(m[0] + "|" + m[1], (Double) m[2], Double::sum);
        }
    }

    // ------------------------------------------------------------ cada segundo: AuraSkills y plata
    private void scan(Player p) {
        Map<String, Double> sum = new TreeMap<>();
        var inv = p.getInventory();
        traitsDe(sum, inv.getItemInMainHand(), "_arma_");
        for (ItemStack piece : inv.getArmorContents()) traitsDe(sum, piece, "_armadura_");
        double plata = efectos(inv.getItemInMainHand(), "_arma_").getOrDefault("plata", 0d);
        for (ItemStack piece : inv.getArmorContents()) plata += efectos(piece, "_armadura_").getOrDefault("plata", 0d);
        int pl = (int) Math.min(63, Math.round(plata));
        String sig = sum + "|" + pl;
        if (sig.equals(last.get(p.getUniqueId()))) return;
        for (int i = 0; i < 6; i++) {
            if ((pl >> i & 1) == 1) p.addScoreboardTag("astral.gp" + i);
            else p.removeScoreboardTag("astral.gp" + i);
        }
        SkillsUser user = AuraSkillsApi.get().getUser(p.getUniqueId());
        if (user == null || !user.isLoaded()) return;   // se reintenta en el proximo ciclo
        clearTraits(user);
        for (var e : sum.entrySet()) {
            String[] k = e.getKey().split("\\|");
            Trait trait = trait(k[0]);
            if (trait == null || e.getValue() == 0) continue;
            user.addTraitModifier(new TraitModifier(PREFIX + k[0], trait, e.getValue(),
                    AuraSkillsModifier.Operation.valueOf(k[1])));
        }
        last.put(p.getUniqueId(), sig);
    }

    private static Trait trait(String name) {
        return switch (name) {
            case "max_mana" -> Traits.MAX_MANA;
            case "mana_regen" -> Traits.MANA_REGEN;
            case "crit_chance" -> Traits.CRIT_CHANCE;
            case "crit_damage" -> Traits.CRIT_DAMAGE;
            default -> null;
        };
    }

    private static void clearTraits(SkillsUser user) {
        for (String t : TRAITS) if (user.getTraitModifier(PREFIX + t) != null) user.removeTraitModifier(PREFIX + t);
    }

    private void clear(Player p) {
        for (int i = 0; i < 6; i++) p.removeScoreboardTag("astral.gp" + i);
        SkillsUser user = AuraSkillsApi.get().getUser(p.getUniqueId());
        if (user != null) clearTraits(user);
    }

    // ------------------------------------------------------------ en cada golpe
    private static LivingEntity causante(Entity damager) {
        if (damager instanceof Projectile pr && pr.getShooter() instanceof LivingEntity le) return le;
        return damager instanceof LivingEntity le ? le : null;
    }

    private boolean esJefe(LivingEntity e) {
        for (String t : tagsJefes) if (e.getScoreboardTags().contains(t)) return true;
        if (e instanceof Player || !Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) return false;
        try {
            return io.lumine.mythic.bukkit.MythicBukkit.inst().getMobManager().getActiveMob(e.getUniqueId())
                    .map(a -> a.getType().usesBossBar()).orElse(false);
        } catch (Throwable ex) {
            return false;
        }
    }

    private static double vidaMax(LivingEntity e) {
        var a = e.getAttribute(Attribute.MAX_HEALTH);
        return a == null ? 0 : a.getValue();
    }

    private boolean ocupado;   // el dano de las espinas no vuelve a disparar gemas

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void golpe(EntityDamageByEntityEvent e) {
        if (ocupado || !(e.getEntity() instanceof LivingEntity victima)) return;
        LivingEntity causa = causante(e.getDamager());
        if (causa == null || causa == victima) return;
        var rnd = ThreadLocalRandom.current();
        // Atacante jugador: Opalo y robo de vida (gemas del arma en la mano).
        if (causa instanceof Player atk) {
            Map<String, Double> m = efectos(atk.getInventory().getItemInMainHand(), "_arma_");
            double jefes = m.getOrDefault("dano_jefes", 0d);
            if (jefes > 0 && esJefe(victima)) e.setDamage(e.getDamage() * (1 + jefes / 100));
            double robo = m.getOrDefault("robo", 0d);
            int ahora = Bukkit.getCurrentTick();
            if (robo > 0 && rnd.nextDouble() < roboProb
                    && ahora - ultimaCura.getOrDefault(atk.getUniqueId(), -1000) >= roboEspera && !atk.isDead()) {
                ultimaCura.put(atk.getUniqueId(), ahora);
                double max = vidaMax(atk);
                atk.setHealth(Math.min(max, atk.getHealth() + max * robo / 100));
                atk.getWorld().spawnParticle(Particle.HEART, atk.getLocation().add(0, 2, 0), 1, .2, .1, .2, 0);
            }
        }
        // Victima jugador: espinas de cada pieza de Onix (tambien contra jugadores).
        if (victima instanceof Player vp) {
            double total = 0;
            for (ItemStack piece : vp.getInventory().getArmorContents()) {
                double pct = efectos(piece, "_armadura_").getOrDefault("espinas", 0d);
                if (pct > 0 && rnd.nextDouble() < espinasProb) total += pct;
            }
            if (total > 0 && !causa.isDead()) {
                if (esJefe(causa)) total *= espinasJefes;
                double dano = vidaMax(causa) * total / 100;
                if (dano > 0) {
                    ocupado = true;
                    try {
                        causa.damage(dano, DamageSource.builder(DamageType.THORNS).withCausingEntity(vp).withDirectEntity(vp).build());
                    } finally {
                        ocupado = false;
                    }
                    causa.getWorld().spawnParticle(Particle.CRIT, causa.getLocation().add(0, 1, 0), 6, .3, .4, .3, .1);
                }
            }
        }
    }
}
