package astral;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityCombustEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityPotionEffectEvent;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.potion.PotionEffectTypeCategory;

import java.util.*;

/**
 * Jefes sin estados (datapack-src/jefes_inmunes.py, 26/11/2026). Pedido del dueno: a los jefes no se los puede
 * envenenar, quemar, congelar ni ponerles ningun efecto malo.
 *
 * Jefe = MythicMob con barra de jefe, etiquetas de jefe (config) o jefe vanilla (Wither, Dragon, Warden, Guardian anciano).
 * - Efectos de pocion danosos (veneno, lentitud, debilidad, ceguera, levitacion...) se cancelan al aplicarse.
 * - No se prenden fuego; el dano de fuego, lava, veneno, wither y congelamiento se cancela.
 * - Cada segundo se apagan fuego/congelamiento y se sacan efectos malos que hayan entrado por otro lado (datapack).
 * Los efectos buenos (los que el jefe se pone con sus habilidades) no se tocan.
 * - Al recibir un golpe se apaga el congelamiento en el mismo tick y en el siguiente (Aspecto de Hielo y parecidos).
 * - Marca a los jefes con la etiqueta astral.sinestados: AstralClases no les pone el veneno del Asesino.
 * Mientras `publico` es false solo actua en jefes a menos de 96 bloques de un jugador de `probadores` (sala del dueno).
 */
public final class AstralJefesInmunes extends JavaPlugin implements Listener {
    private List<String> tags = List.of();
    private Set<String> probadores = Set.of();
    private boolean publico;
    private final Set<UUID> jefes = new HashSet<>();
    private final Map<UUID, Boolean> cacheMM = new HashMap<>();
    private int bloqueados;
    static final String TAG = "astral.sinestados";

    private static final Set<EntityDamageEvent.DamageCause> CAUSAS = EnumSet.of(
            EntityDamageEvent.DamageCause.FIRE, EntityDamageEvent.DamageCause.FIRE_TICK, EntityDamageEvent.DamageCause.LAVA,
            EntityDamageEvent.DamageCause.HOT_FLOOR, EntityDamageEvent.DamageCause.CAMPFIRE,
            EntityDamageEvent.DamageCause.POISON, EntityDamageEvent.DamageCause.WITHER, EntityDamageEvent.DamageCause.FREEZE);

    @Override public void onEnable() {
        saveDefaultConfig();
        leer();
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::limpiar, 40, 20);
    }

    private void leer() {
        reloadConfig();
        tags = getConfig().getStringList("etiquetas-jefe");
        probadores = new HashSet<>(getConfig().getStringList("probadores"));
        publico = getConfig().getBoolean("publico", false);
    }

    static boolean malo(PotionEffectType t) {
        if (t == null || t.isInstant()) return false;      // dano/cura instantanea es dano, no estado
        return t.getCategory() == PotionEffectTypeCategory.HARMFUL;
    }

    private boolean esJefe(LivingEntity e) {
        if (e instanceof Player) return false;
        if (e instanceof Wither || e instanceof EnderDragon || e instanceof Warden || e instanceof ElderGuardian) return true;
        for (String t : tags) if (e.getScoreboardTags().contains(t)) return true;
        Boolean c = cacheMM.get(e.getUniqueId());
        if (c != null) return c;
        boolean r = false;
        if (Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) {
            try {
                r = io.lumine.mythic.bukkit.MythicBukkit.inst().getMobManager().getActiveMob(e.getUniqueId())
                        .map(a -> a.getType().usesBossBar()).orElse(false);
            } catch (Throwable ex) { r = false; }
        }
        if (cacheMM.size() > 4000) cacheMM.clear();
        cacheMM.put(e.getUniqueId(), r);
        return r;
    }

    private boolean activo(LivingEntity e) {
        if (publico) return true;
        for (Player p : e.getWorld().getPlayers())
            if (probadores.contains(p.getName()) && p.getLocation().distanceSquared(e.getLocation()) <= 96 * 96) return true;
        return false;
    }

    private boolean protegido(Entity ent) {
        if (!(ent instanceof LivingEntity e) || !esJefe(e) || !activo(e)) return false;
        jefes.add(e.getUniqueId());
        e.addScoreboardTag(TAG);
        return true;
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void efecto(EntityPotionEffectEvent ev) {
        if (ev.getAction() != EntityPotionEffectEvent.Action.ADDED && ev.getAction() != EntityPotionEffectEvent.Action.CHANGED) return;
        PotionEffect n = ev.getNewEffect();
        if (n == null || !malo(n.getType()) || !protegido(ev.getEntity())) return;
        ev.setCancelled(true);
        bloqueados++;
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void fuego(EntityCombustEvent ev) {
        if (!protegido(ev.getEntity())) return;
        ev.setCancelled(true);
        bloqueados++;
    }

    @EventHandler(priority = EventPriority.LOWEST, ignoreCancelled = true)
    public void dano(EntityDamageEvent ev) {
        if (!CAUSAS.contains(ev.getCause()) || !protegido(ev.getEntity())) return;
        ev.setCancelled(true);
        LivingEntity e = (LivingEntity) ev.getEntity();
        e.setFireTicks(0); e.setFreezeTicks(0);
    }

    /** Antes que nadie: marca al jefe (para AstralClases). */
    @EventHandler(priority = EventPriority.LOWEST, ignoreCancelled = true)
    public void golpeAntes(EntityDamageByEntityEvent ev) { protegido(ev.getEntity()); }

    /** Despues de todos: el Aspecto de Hielo pone congelamiento con setFreezeTicks (sin evento); se saca ya y al tick. */
    @EventHandler(priority = EventPriority.MONITOR)
    public void golpeDespues(EntityDamageByEntityEvent ev) {
        if (!(ev.getEntity() instanceof LivingEntity e) || !jefes.contains(e.getUniqueId()) || !activo(e)) return;
        descongelar(e);
        Bukkit.getScheduler().runTask(this, () -> { if (e.isValid()) descongelar(e); });
        Bukkit.getScheduler().runTaskLater(this, () -> { if (e.isValid()) descongelar(e); }, 2);
    }

    private void descongelar(LivingEntity e) {
        if (e.getFreezeTicks() > 0) e.setFreezeTicks(0);
        for (PotionEffect p : e.getActivePotionEffects()) if (malo(p.getType())) e.removePotionEffect(p.getType());
    }

    private void limpiar() {
        for (Iterator<UUID> it = jefes.iterator(); it.hasNext(); ) {
            Entity ent = Bukkit.getEntity(it.next());
            if (!(ent instanceof LivingEntity e) || !e.isValid() || e.isDead()) { it.remove(); continue; }
            if (!activo(e)) { e.removeScoreboardTag(TAG); continue; }
            e.addScoreboardTag(TAG);
            if (e.getFireTicks() > 0) e.setFireTicks(0);
            if (e.getFreezeTicks() > 0) e.setFreezeTicks(0);
            for (PotionEffect p : e.getActivePotionEffects()) if (malo(p.getType())) e.removePotionEffect(p.getType());
        }
        cacheMM.keySet().removeIf(id -> Bukkit.getEntity(id) == null);
    }

    @Override public boolean onCommand(CommandSender s, Command c, String label, String[] a) {
        String sub = a.length > 0 ? a[0].toLowerCase(Locale.ROOT) : "";
        switch (sub) {
            case "publico" -> {
                if (a.length < 2) { s.sendMessage("Uso: /jefesinmunes publico <si|no>"); return true; }
                getConfig().set("publico", a[1].equalsIgnoreCase("si") || a[1].equalsIgnoreCase("true"));
                saveConfig(); leer();
            }
            case "recargar" -> leer();
            default -> { }
        }
        s.sendMessage(ChatColor.GOLD + "Jefes sin estados: " + ChatColor.WHITE + (publico ? "ABIERTO A TODOS" : "solo cerca de " + probadores)
                + ChatColor.GRAY + " | jefes vistos: " + jefes.size() + " | efectos/fuego bloqueados: " + bloqueados);
        return true;
    }
}
