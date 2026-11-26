package astraltest;

import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.block.BlockFace;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.ArrayList;
import java.util.List;

/** Ensayo de la invocacion del 26/11 (tools/probar_invocacion_paper.py), con AstralProgression cargado:
 *  no es invulnerable, vida 220 / golpe 167 en T1, aguanta 3 golpes, pega sin doble golpe, va al enemigo
 *  mas cercano, dura 30 s y el libro muestra los numeros nuevos. Imprime "INV PASS/FAIL ..." e "INV RESULT". */
public final class InvocacionProbe extends JavaPlugin implements Listener {
    private final List<String> fallas = new ArrayList<>();
    private int pasos;
    private final List<Double> recibidos = new ArrayList<>();
    private final List<Long> golpesDados = new ArrayList<>();
    private final List<Double> danosDados = new ArrayList<>();

    @Override public void onEnable() { getServer().getPluginManager().registerEvents(this, this); }

    private void ok(boolean c, String s) {
        pasos++;
        getLogger().info("INV " + (c ? "PASS " : "FAIL ") + s);
        if (!c) fallas.add(s);
    }

    private void cmd(String s) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), s); }

    private LivingEntity invocacion(World w) {
        for (Entity e : w.getEntities())
            if (e.getScoreboardTags().contains("astral.invocacion") && e instanceof LivingEntity le && !le.isDead()) return le;
        return null;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void golpes(EntityDamageByEntityEvent e) {
        if (e.getEntity().getScoreboardTags().contains("astral.invocacion")) recibidos.add(e.getFinalDamage());
        if (e.getDamager().getScoreboardTags().contains("astral.invocacion")) {
            golpesDados.add(System.currentTimeMillis());
            danosDados.add(e.getFinalDamage());
        }
    }

    @EventHandler
    public void alEntrar(PlayerJoinEvent e) {
        Player p = e.getPlayer();
        Bukkit.getScheduler().runTaskLater(this, () -> paso1(p), 60);
    }

    private Husk husk(World w, Location l, double ataque) {
        return w.spawn(l, Husk.class, x -> {
            x.addScoreboardTag("astral.mt1");
            x.getAttribute(Attribute.MAX_HEALTH).setBaseValue(50000); x.setHealth(50000);
            x.getAttribute(Attribute.MOVEMENT_SPEED).setBaseValue(0);
            x.getAttribute(Attribute.ATTACK_DAMAGE).setBaseValue(ataque);
        });
    }

    private void paso1(Player p) {
        World w = new WorldCreator("bosque").type(WorldType.FLAT).generateStructures(false).createWorld();
        w.setSpawnFlags(false, false);
        w.setTime(6000);
        w.setDifficulty(Difficulty.EASY);
        p.teleport(new Location(w, 0.5, -60, 0.5));
        p.setGameMode(GameMode.SURVIVAL);
        var max = p.getAttribute(Attribute.MAX_HEALTH);
        max.setBaseValue(1000000); p.setHealth(1000000);
        var u = AuraSkillsApi.get().getUser(p.getUniqueId());
        u.setSkillLevel(Skills.SORCERY, 60);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            AuraSkillsApi.get().getUser(p.getUniqueId()).setMana(100000);
            p.getInventory().clear();
            cmd("loot give " + p.getName() + " loot astral:item/libro_invocador_1");
            ItemStack libro = null;
            for (ItemStack it : p.getInventory().getContents())
                if (it != null && it.hasItemMeta() && it.getItemMeta().getPersistentDataContainer().getKeys().stream()
                        .anyMatch(k -> k.getKey().equals("clase_arma"))) libro = it;
            ok(libro != null, "libro de invocador entregado");
            if (libro == null) { fin(); return; }
            p.getInventory().setItemInMainHand(libro);
            Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(p, Action.RIGHT_CLICK_AIR, libro, null, BlockFace.SELF, EquipmentSlot.HAND));
            Bukkit.getScheduler().runTaskLater(this, () -> paso2(p, w), 30);
        }, 40);
    }

    private void paso2(Player p, World w) {
        LivingEntity yo = invocacion(w);
        ok(yo != null, "aparecio la invocacion");
        if (yo == null) { fin(); return; }
        ok(!yo.isInvulnerable(), "no es invulnerable (AstralProgression ya no la toma por mascota)");
        double vida = yo.getAttribute(Attribute.MAX_HEALTH).getValue();
        double ataque = yo.getAttribute(Attribute.ATTACK_DAMAGE).getValue();
        ok(Math.abs(vida - 220) < 1, "vida T1 = 220: " + vida);
        ok(Math.abs(ataque - 167) < 1, "golpe T1 = 167: " + ataque);
        var plano = net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText();
        String lore = String.join(" | ", p.getInventory().getItemInMainHand().lore().stream().map(plano::serialize).toList());
        getLogger().info("INV lore: " + lore);
        ok(lore.contains("por 30 s") && lore.contains("220 de vida") && lore.contains("167 de dano"), "libro con numeros nuevos");
        long t0 = System.currentTimeMillis();
        // A los 20 s sigue (antes duraba 20). Sin mobs cerca.
        Bukkit.getScheduler().runTaskLater(this, () -> {
            LivingEntity y = invocacion(w);
            ok(y != null, "sigue viva a los ~21 s");
            if (y == null) { fin(); return; }
            Location c = y.getLocation();
            limpiar(w);
            // Enemigo lejos primero; despues uno pegado: tiene que cambiar al mas cercano.
            // Los dos a la vez: el lejano como objetivo actual y uno pegado; tiene que pasarse al pegado.
            Husk lejos = husk(w, c.clone().add(7, 0, 0), 3);
            Husk cerca = husk(w, c.clone().add(0, 0, 1.4), 20);   // pega fuerte: el tope de 1/3,5 la protege
            lejos.customName(net.kyori.adventure.text.Component.text("lejos"));
            cerca.customName(net.kyori.adventure.text.Component.text("cerca"));
            ((Mob) y).setTarget(lejos);
            cerca.setTarget((Mob) y);
            Bukkit.getScheduler().runTaskLater(this, () -> {
                var t = ((Mob) y).getTarget();
                ok(cerca.equals(t), "cambio al enemigo mas cercano: " + (t == null ? "nada" : t.getName()));
            }, 15);
            Bukkit.getScheduler().runTaskLater(this, () -> paso3(w, y, cerca, lejos, t0), 120);
        }, 400);
    }

    private void paso3(World w, LivingEntity y, Husk cerca, Husk lejos, long t0) {
        getLogger().info("INV recibidos: " + recibidos + " dados: " + danosDados);
        ok(!recibidos.isEmpty(), "los mobs le pegan (" + recibidos.size() + " golpes)");
        double tope = 220 / 3.5 + 0.5;
        ok(recibidos.stream().allMatch(x -> x <= tope), "ningun golpe de su tier pasa 1/3,5 de la vida");
        ok(!danosDados.isEmpty() && danosDados.stream().anyMatch(x -> x > 150), "pega con ~167 (159 por la armadura natural del husk) (" + danosDados.size() + " golpes)");
        boolean sinDoble = true;
        for (int i = 1; i < golpesDados.size(); i++) if (golpesDados.get(i) - golpesDados.get(i - 1) < 800) sinDoble = false;
        ok(sinDoble, "sin doble golpe");
        cerca.remove(); lejos.remove();
        long falta = 31000 - (System.currentTimeMillis() - t0);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            ok(invocacion(w) == null, "se va al terminar los 30 s");
            fin();
        }, Math.max(20, falta / 50));
    }

    /** Saca mobs que aparecieron solos (slimes del mundo plano); deja jugadores, la invocacion y los husks de prueba. */
    private void limpiar(World w) {
        for (LivingEntity e : w.getLivingEntities())
            if (!(e instanceof Player) && !(e instanceof Husk) && !e.getScoreboardTags().contains("astral.invocacion")) e.remove();
    }

    private void fin() {
        getLogger().info("INV RESULT pasos=" + pasos + " failures=" + fallas.size() + " " + fallas);
        Bukkit.getScheduler().runTaskLater(this, Bukkit::shutdown, 20);
    }
}
