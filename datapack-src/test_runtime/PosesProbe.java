package astraltest;

import java.util.ArrayList;
import java.util.List;

import org.bukkit.Bukkit;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;

import kr.toxicity.model.api.BetterModel;
import kr.toxicity.model.api.animation.AnimationIterator;
import kr.toxicity.model.api.animation.AnimationModifier;
import kr.toxicity.model.api.util.function.FloatSupplier;

/** Ensayo local (tools/probar_modelos_22_11.py): modelos nuevos de BetterModel y animaciones de jugador. */
public final class PosesProbe extends JavaPlugin implements Listener {
    private int fallas = 0;
    private int pasos = 0;
    private boolean jugadorProbado = false;

    private void ok(boolean cond, String what) {
        pasos++;
        if (!cond) fallas++;
        getLogger().info((cond ? "POSES PASS " : "POSES FAIL ") + what);
    }

    @Override
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        esperar(0);
    }

    private void esperar(int intentos) {
        Bukkit.getScheduler().runTaskLater(this, () -> {
            if (BetterModel.limbOrNull("astral_poses") == null && BetterModel.model("astral_capitan_vacio").isEmpty() && intentos < 60) {
                esperar(intentos + 1);
                return;
            }
            modelos();
        }, 20);
    }

    private void modelos() {
        var limb = BetterModel.limbOrNull("astral_poses");
        ok(limb != null, "limb astral_poses cargado");
        if (limb != null) ok(limb.animation("guadana_giro").isPresent(), "limb anim guadana_giro");
        var fx = BetterModel.model("astral_fx_clases").orElse(null);
        ok(fx != null, "modelo astral_fx_clases cargado");
        if (fx != null) for (String a : new String[]{"tajo", "invocar"}) ok(fx.animation(a).isPresent(), "fx anim " + a);
        var cap = BetterModel.model("astral_capitan_vacio").orElse(null);
        ok(cap != null, "modelo astral_capitan_vacio cargado");
        String[] anims = {"idle", "walk", "attack", "barrido", "throw", "salto", "furia", "pulso", "aparece", "death"};
        if (cap != null) for (String a : anims) ok(cap.animation(a).isPresent(), "capitan anim " + a);
        ok(BetterModel.model("astral_ojo_vigia").isPresent(), "modelo astral_ojo_vigia cargado");
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mm mobs spawn astral_nave_capitan 1 world,0,-55,0");
        Bukkit.getScheduler().runTaskLater(this, () -> {
            Entity jefe = null;
            for (Entity e : Bukkit.getWorlds().get(0).getEntities()) if (e.getScoreboardTags().contains("nave.jefe")) jefe = e;
            ok(jefe != null, "Capitan aparece por MythicMobs");
            if (jefe != null) {
                var reg = BetterModel.registryOrNull(jefe.getUniqueId());
                ok(reg != null, "Capitan tiene modelo BetterModel");
                if (reg != null) {
                    var tracker = reg.tracker("astral_capitan_vacio");
                    ok(tracker != null, "tracker del Capitan");
                    if (tracker != null) for (String a : anims) if (!a.equals("death") && !a.equals("salto"))
                        ok(tracker.animate(a), "Capitan reproduce " + a);
                }
            }
            Bukkit.getScheduler().runTaskLater(this, () -> {
                if (!jugadorProbado) ok(false, "no entro el bot a tiempo");
                terminar();
            }, 20 * 90);
        }, 60);
    }

    @EventHandler
    public void entra(PlayerJoinEvent e) {
        Player p = e.getPlayer();
        List<String> lista = new ArrayList<>(List.of("guadana_giro", "fx:tajo", "fx:invocar"));
        Bukkit.getScheduler().runTaskLater(this, () -> probarJugador(p, lista), 60);
    }

    private void probarJugador(Player p, List<String> lista) {
        if (lista.isEmpty()) {
            jugadorProbado = true;
            Bukkit.getScheduler().runTaskLater(this, this::terminar, 60);
            return;
        }
        String a = lista.remove(0);
        try {
            var mod = new AnimationModifier(0, 0, AnimationIterator.Type.PLAY_ONCE, FloatSupplier.of(1f));
            if (a.startsWith("fx:")) {
                String n = a.substring(3);
                var r = BetterModel.model("astral_fx_clases").orElseThrow();
                var t = r.create(kr.toxicity.model.bukkit.util.BukkitWrappersKt.wrap(p.getLocation()));
                t.spawn(kr.toxicity.model.bukkit.util.BukkitWrappersKt.wrap(p));
                boolean ok = t.animate(n, mod, t::close);
                ok(ok, "efecto " + n + " junto al jugador");
                if (!ok) t.close();
            } else {
                var r = BetterModel.limbOrNull("astral_poses");
                var t = r.getOrCreate(kr.toxicity.model.bukkit.util.BukkitWrappersKt.wrap(p));
                boolean ok = t.animate(a, mod, t::close);
                ok(ok, "jugador " + a);
                if (!ok) t.close();
            }
        } catch (Throwable ex) {
            ok(false, "jugador " + a + ": " + ex);
        }
        Bukkit.getScheduler().runTaskLater(this, () -> probarJugador(p, lista), 40);
    }

    private boolean terminado = false;

    private void terminar() {
        if (terminado) return;
        terminado = true;
        getLogger().info("POSES RESULT pasos=" + pasos + " failures=" + fallas);
        Bukkit.shutdown();
    }
}
