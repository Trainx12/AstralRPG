package astral;

import java.util.*;
import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.plugin.java.JavaPlugin;
import org.popcraft.chunky.api.ChunkyAPI;
import org.popcraft.chunky.api.event.task.GenerationCompleteEvent;

/** Cola de Chunky (23/11): pregenera un mundo por vez, en orden. Pausa si hay jugadores conectados
 *  (come todo el procesador aunque los TPS sigan en 20) o si el servidor anda lento. */
public final class AstralChunky extends JavaPlugin {
    record Paso(String mundo, double radio) {}
    final List<Paso> cola = new ArrayList<>();
    Set<String> hechos;
    ChunkyAPI chunky;
    String actual;           // mundo en curso (lo arranco esta cola o lo retomo Chunky al prender)
    boolean pausadoPorLag, pausadoPorGente;
    double tpsPausa, tpsSeguir;
    int jugadoresPausa;

    @Override public void onEnable() {
        saveDefaultConfig();
        for (var m : getConfig().getMapList("cola"))
            cola.add(new Paso(String.valueOf(m.get("mundo")), Double.parseDouble(String.valueOf(m.get("radio")))));
        hechos = new HashSet<>(getConfig().getStringList("hechos"));
        tpsPausa = getConfig().getDouble("tps-pausa", 17); tpsSeguir = getConfig().getDouble("tps-seguir", 19.5);
        jugadoresPausa = getConfig().getInt("jugadores-pausa", 1);
        chunky = Bukkit.getServicesManager().load(ChunkyAPI.class);
        if (chunky == null) { getLogger().warning("Chunky no esta: cola apagada"); return; }
        chunky.onGenerationComplete(this::termino);
        // Dar tiempo a que Chunky retome solo lo que quedo a medias (continue-on-restart).
        Bukkit.getScheduler().runTaskTimer(this, this::revisar, 20L * 90, 20L * 10);
    }

    static String nombre(String w) { // "minecraft:the_end" -> world_the_end
        if (w == null) return "";
        World x = Bukkit.getWorld(w);
        if (x != null) return x.getName();
        for (World y : Bukkit.getWorlds()) if (y.getKey().toString().equals(w)) return y.getName();
        return w;
    }

    void termino(GenerationCompleteEvent e) {
        String w = nombre(e.world());
        Bukkit.getScheduler().runTask(this, () -> {
            if (e.reason() == GenerationCompleteEvent.Reason.COMPLETED) {
                hechos.add(w); getConfig().set("hechos", new ArrayList<>(hechos)); saveConfig();
                getLogger().info("Pregenerado completo: " + w + " (" + e.chunks() + " chunks)");
                if (w.equals(actual)) actual = null;
            }
        });
    }

    double tps() { return Bukkit.getTPS()[0]; }

    boolean hayGente() { return jugadoresPausa > 0 && Bukkit.getOnlinePlayers().size() >= jugadoresPausa; }

    /** Pausa lo que este corriendo (lo haya arrancado esta cola o Chunky al prender). */
    void pausarTodo() {
        for (Paso p : cola) if (Bukkit.getWorld(p.mundo()) != null && chunky.isRunning(p.mundo())) {
            chunky.pauseTask(p.mundo()); actual = p.mundo(); }
    }

    void revisar() {
        // Con gente conectada no se pregenera: los jugadores necesitan el procesador.
        if (hayGente()) {
            if (!pausadoPorGente) { pausadoPorGente = true; getLogger().info("Pausado: hay jugadores conectados"); }
            pausarTodo();
            return;
        }
        if (pausadoPorGente) {
            pausadoPorGente = false; getLogger().info("Servidor vacio: sigue la pregeneracion");
            if (actual != null && !pausadoPorLag && chunky.continueTask(actual)) return;
        }
        // Lag: pausar el que corre; seguir cuando el servidor se recupera.
        if (actual != null && !pausadoPorLag && tps() < tpsPausa && chunky.isRunning(actual)) {
            chunky.pauseTask(actual); pausadoPorLag = true;
            getLogger().info("Pausado por lag (" + String.format("%.1f", tps()) + " TPS): " + actual);
            return;
        }
        if (pausadoPorLag) {
            if (tps() >= tpsSeguir && actual != null) { chunky.continueTask(actual); pausadoPorLag = false;
                getLogger().info("Sigue: " + actual); }
            return;
        }
        // Un solo mundo a la vez, en el orden de la cola.
        for (Paso p : cola) {
            if (hechos.contains(p.mundo())) continue;
            if (Bukkit.getWorld(p.mundo()) == null) { getLogger().warning("No existe el mundo " + p.mundo()); continue; }
            if (chunky.isRunning(p.mundo())) { actual = p.mundo(); return; }
            for (Paso q : cola) if (!q.equals(p) && Bukkit.getWorld(q.mundo()) != null && chunky.isRunning(q.mundo())) {
                actual = q.mundo(); return; } // hay otro corriendo: esperar a que termine
            if (chunky.continueTask(p.mundo())) { actual = p.mundo(); getLogger().info("Retoma: " + p.mundo()); return; }
            if (chunky.startTask(p.mundo(), "square", 0, 0, p.radio(), p.radio(), "ring")) {
                actual = p.mundo(); getLogger().info("Empieza: " + p.mundo() + " radio " + (int) p.radio());
            }
            return;
        }
    }
}
