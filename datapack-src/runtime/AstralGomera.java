package astral;

import java.util.regex.Pattern;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.ProjectileHitEvent;
import org.bukkit.damage.DamageSource;
import org.bukkit.damage.DamageType;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import io.papermc.paper.event.player.PlayerStopUsingItemEvent;

/**
 * Gomera del Refugio, item del Modo Historia (historia_items.py).
 * Gomera: el item tiene animacion de arco (consumable sin terminar nunca). Al soltar el clic
 * se tira una piedra con fuerza segun cuanto se estiro.
 */
public final class AstralGomera implements Listener {
    private static final Pattern ID = Pattern.compile("[{,]\\s*id:\\s*\"([a-z0-9_]+)\"");
    private final JavaPlugin plugin;
    private final AstralSpell spell;
    private final NamespacedKey damageKey;
    private final double damage, speed, minimum;
    private final int chargeTicks, cooldownTicks;
    private final ItemStack pebble;

    public AstralGomera(JavaPlugin plugin, AstralSpell spell) {
        this.plugin = plugin; this.spell = spell;
        damageKey = new NamespacedKey(plugin, "gomera_dano");
        try (var in = plugin.getResource("gomera.json")) {
            var o = com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            damage = o.get("dano").getAsDouble(); speed = o.get("velocidad").getAsDouble(); minimum = o.get("minima").getAsDouble();
            chargeTicks = o.get("carga_ticks").getAsInt(); cooldownTicks = o.get("recarga_ticks").getAsInt();
        } catch (Exception ex) { throw new IllegalStateException("Gomera sin datos", ex); }
        // La piedra se ve con el dibujo de la Gomera (historia_arte.py: astral:gomera_piedra).
        pebble = new ItemStack(Material.FLINT);
        var meta = pebble.getItemMeta(); meta.setItemModel(new NamespacedKey("astral", "gomera_piedra")); pebble.setItemMeta(meta);
        Bukkit.getPluginManager().registerEvents(this, plugin);
    }

    static String astralId(ItemStack it) {
        if (it == null || !it.hasItemMeta()) return "";
        var m = ID.matcher(it.getItemMeta().getAsComponentString());
        return m.find() ? m.group(1) : "";
    }

    private static boolean lobby(World w) { return w.getName().equals("lobby") || w.getName().endsWith(":lobby"); }

    @EventHandler(priority = EventPriority.HIGH)
    public void click(PlayerInteractEvent e) {
        if (e.getAction() != Action.RIGHT_CLICK_AIR && e.getAction() != Action.RIGHT_CLICK_BLOCK) return;
        Player p = e.getPlayer(); ItemStack item = e.getItem();
        String id = astralId(item);
        if (id.equals("gomera") && !p.hasCooldown(item)) {
            if (lobby(p.getWorld())) {
                e.setCancelled(true);
                p.sendActionBar(net.kyori.adventure.text.Component.text("La Gomera no se usa en el lobby.", net.kyori.adventure.text.format.NamedTextColor.RED));
                return;
            }
            // Estirar: sonido de la goma (el cliente ya muestra la animacion de arco).
            p.playSound(p.getLocation(), Sound.ITEM_CROSSBOW_LOADING_START, .6f, 1.4f);
        }
    }

    @EventHandler
    public void release(PlayerStopUsingItemEvent e) {
        Player p = e.getPlayer(); ItemStack item = e.getItem();
        if (!astralId(item).equals("gomera") || lobby(p.getWorld()) || p.getGameMode() == GameMode.SPECTATOR) return;
        double charge = Math.min(1.0, e.getTicksHeldFor() / (double) chargeTicks);
        if (charge < minimum) return; // un clic suelto no dispara
        Snowball stone = p.launchProjectile(Snowball.class, p.getEyeLocation().getDirection().multiply(speed * (0.35 + 0.65 * charge)));
        stone.setItem(pebble);
        stone.addScoreboardTag("astral.gomera");
        stone.getPersistentDataContainer().set(damageKey, PersistentDataType.DOUBLE, damage * charge);
        Bukkit.getScheduler().runTaskLater(plugin, stone::remove, 60);
        p.setCooldown(item, cooldownTicks);
        p.playSound(p.getLocation(), Sound.ENTITY_SNOWBALL_THROW, .8f, 0.6f + 0.4f * (float) charge);
        if (charge >= 1) p.getWorld().spawnParticle(Particle.CRIT, p.getEyeLocation().add(p.getEyeLocation().getDirection()), 4, .1, .1, .1, 0);
    }

    // La bola de nieve vanilla pega 0: con el mob recien golpeado el juego la ignora. Se cancela ese
    // golpe y se aplica el dano real con la fuente "thrown" del jugador (cuenta para indicadores y XP).
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void land(ProjectileHitEvent e) {
        if (!(e.getEntity() instanceof Snowball stone) || !stone.getScoreboardTags().contains("astral.gomera")) return;
        if (!(e.getHitEntity() instanceof LivingEntity victim)) return;
        e.setCancelled(true);
        Double amount = stone.getPersistentDataContainer().get(damageKey, PersistentDataType.DOUBLE);
        stone.remove();
        if (!(stone.getShooter() instanceof Player shooter) || amount == null || !spell.eligible(victim, shooter)) return;
        var source = DamageSource.builder(DamageType.THROWN).withCausingEntity(shooter).withDirectEntity(stone)
            .withDamageLocation(stone.getLocation()).build();
        victim.damage(amount, source);
        victim.getWorld().playSound(victim.getLocation(), Sound.BLOCK_STONE_HIT, .8f, 1.2f);
    }

    // Por si otra cosa dispara el golpe vanilla de la piedra: nunca pega a quien no corresponde.
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void hit(EntityDamageByEntityEvent e) {
        if (!(e.getDamager() instanceof Snowball stone) || !stone.getScoreboardTags().contains("astral.gomera")) return;
        Double amount = stone.getPersistentDataContainer().get(damageKey, PersistentDataType.DOUBLE);
        if (!(e.getEntity() instanceof LivingEntity victim) || !(stone.getShooter() instanceof Player shooter) || amount == null
            || !spell.eligible(victim, shooter)) { e.setCancelled(true); return; }
        e.setDamage(amount);
    }
}
