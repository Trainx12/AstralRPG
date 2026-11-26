package astral;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import kr.toxicity.model.api.BetterModel;
import kr.toxicity.model.api.tracker.EntityTracker;
import kr.toxicity.model.api.tracker.EntityTrackerRegistry;
import kr.toxicity.model.api.tracker.ModelScaler;
import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Enemy;
import org.bukkit.entity.IronGolem;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

/**
 * Cajas de golpe iguales al modelo 3D (datapack-src/tamanos_runtime.py, 23/11/2026).
 *
 * BetterModel dibuja el modelo a (alto del .bbmodel) x (s de model{}) x (escala de la entidad), pero la caja de golpe es
 * solo (alto vanilla) x (escala de la entidad): casi todos los mobs se veian mas grandes que donde se les pega.
 * Cada 2 s, a cada mob hostil con modelo: escala de la entidad = factor x alto visible / alto vanilla, y el modelo se
 * compensa para que se siga viendo igual. Lee los altos de plugins/BetterModel/models (mismos archivos que dibuja).
 */
public final class AstralTamanos extends JavaPlugin {
    final Map<String, Double> altos = new HashMap<>();
    double factor; List<String> excluir; List<String> mundosExcluidos;
    int ajustados;
    org.bukkit.NamespacedKey kVisible;

    @Override public void onEnable() {
        saveDefaultConfig();
        kVisible = new org.bukkit.NamespacedKey(this, "visible");
        factor = getConfig().getDouble("factor", 0.9);
        excluir = getConfig().getStringList("excluir-modelos");
        mundosExcluidos = getConfig().getStringList("mundos-excluidos");
        Bukkit.getScheduler().runTaskLater(this, this::leerModelos, 40);
        Bukkit.getScheduler().runTaskTimer(this, this::ajustar, 100, 40);
    }

    void leerModelos() {
        altos.clear();
        File dir = new File(getDataFolder().getParentFile(), "BetterModel/models");
        Deque<File> pila = new ArrayDeque<>(List.of(dir));
        while (!pila.isEmpty()) {
            File[] fs = pila.pop().listFiles();
            if (fs == null) continue;
            for (File f : fs) {
                if (f.isDirectory()) { pila.push(f); continue; }
                if (!f.getName().endsWith(".bbmodel")) continue;
                try {
                    double h = alto(JsonParser.parseString(Files.readString(f.toPath(), StandardCharsets.UTF_8)).getAsJsonObject());
                    if (h > 0.05) altos.put(f.getName().substring(0, f.getName().length() - 8), h);
                } catch (Exception ex) { getLogger().warning("No pude leer " + f.getName() + ": " + ex.getMessage()); }
            }
        }
        getLogger().info("Altos de " + altos.size() + " modelos leidos.");
    }

    // ------------------------------------------------------------------ alto del modelo (igual que mobs/tamanos.py)
    static double[] rot(double[] p, double[] o, double[] a) {
        double x = p[0] - o[0], y = p[1] - o[1], z = p[2] - o[2];
        for (int axis = 0; axis < 3; axis++) {
            double s = Math.sin(Math.toRadians(a[axis])), c = Math.cos(Math.toRadians(a[axis]));
            if (axis == 0) { double ny = y * c - z * s, nz = y * s + z * c; y = ny; z = nz; }
            else if (axis == 1) { double nx = x * c + z * s, nz = -x * s + z * c; x = nx; z = nz; }
            else { double nx = x * c - y * s, ny = x * s + y * c; x = nx; y = ny; }
        }
        return new double[]{x + o[0], y + o[1], z + o[2]};
    }
    static double[] vec(JsonObject o, String k) {
        JsonArray a = o.has(k) ? o.getAsJsonArray(k) : null;
        return a == null ? new double[3] : new double[]{a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble()};
    }
    static double alto(JsonObject d) {
        Map<String, JsonObject> el = new HashMap<>(), gr = new HashMap<>();
        for (JsonElement e : d.getAsJsonArray("elements")) {
            JsonObject o = e.getAsJsonObject();
            if (!o.has("type") || o.get("type").getAsString().equals("cube")) el.put(o.get("uuid").getAsString(), o);
        }
        if (d.has("groups")) for (JsonElement g : d.getAsJsonArray("groups")) gr.put(g.getAsJsonObject().get("uuid").getAsString(), g.getAsJsonObject());
        double[] mm = {Double.MAX_VALUE, -Double.MAX_VALUE};
        for (JsonElement n : d.getAsJsonArray("outliner")) visitar(n, new ArrayList<>(), el, gr, mm);
        return mm[1] < mm[0] ? 0 : (mm[1] - mm[0]) / 16;
    }
    static void visitar(JsonElement n, List<JsonObject> padres, Map<String, JsonObject> el, Map<String, JsonObject> gr, double[] mm) {
        if (n.isJsonPrimitive()) {
            JsonObject e = el.get(n.getAsString());
            if (e == null) return;
            double inf = e.has("inflate") ? e.get("inflate").getAsDouble() : 0;
            double[] from = vec(e, "from"), to = vec(e, "to"), o = vec(e, "origin"), r = vec(e, "rotation");
            for (int i = 0; i < 8; i++) {
                double[] p = {(i & 1) == 0 ? from[0] - inf : to[0] + inf, (i & 2) == 0 ? from[1] - inf : to[1] + inf, (i & 4) == 0 ? from[2] - inf : to[2] + inf};
                p = rot(p, o, r);
                for (int k = padres.size() - 1; k >= 0; k--) p = rot(p, vec(padres.get(k), "origin"), vec(padres.get(k), "rotation"));
                mm[0] = Math.min(mm[0], p[1]); mm[1] = Math.max(mm[1], p[1]);
            }
            return;
        }
        JsonObject node = n.getAsJsonObject();
        JsonObject g = gr.getOrDefault(node.has("uuid") ? node.get("uuid").getAsString() : "", node);
        List<JsonObject> np = new ArrayList<>(padres); np.add(g);
        if (node.has("children")) for (JsonElement c : node.getAsJsonArray("children")) visitar(c, np, el, gr, mm);
    }

    // ------------------------------------------------------------------ ajuste
    boolean excluido(String modelo) { for (String p : excluir) if (modelo.startsWith(p)) return true; return false; }

    void ajustar() {
        if (altos.isEmpty()) return;
        for (World w : Bukkit.getWorlds()) {
            boolean fuera = false;
            for (String m : mundosExcluidos) if (w.getName().startsWith(m)) fuera = true;
            if (fuera) continue;
            for (LivingEntity e : w.getLivingEntities()) {
                if (e instanceof Player || !(e instanceof Enemy || e instanceof IronGolem) || e.isDead() || e.getTicksLived() < 60) continue;
                EntityTrackerRegistry reg = BetterModel.registryOrNull(e.getUniqueId());
                if (reg == null) continue;
                for (EntityTracker t : reg.trackers()) { if (ajustar(e, t)) ajustados++; break; }
            }
        }
    }

    boolean ajustar(LivingEntity e, EntityTracker t) {
        String nombre = t.name();
        Double h = altos.get(nombre);
        if (h == null || excluido(nombre)) return false;
        AttributeInstance sc = e.getAttribute(Attribute.SCALE);
        if (sc == null) return false;
        double a = sc.getValue(), total = t.scaler().scale(t);
        if (a <= 0 || total <= 0) return false;
        // El alto visible se guarda la primera vez: si MythicMobs vuelve a poner el modelo (al cargar el chunk) sin
        // volver a poner la escala, no se agranda de nuevo.
        var pdc = e.getPersistentDataContainer();
        Double guardado = pdc.get(kVisible, PersistentDataType.DOUBLE);
        double visible = guardado != null ? guardado : h * total, base = e.getHeight() / a;
        if (guardado == null) pdc.set(kVisible, PersistentDataType.DOUBLE, visible);
        double nueva = Math.max(0.0625, Math.min(16, factor * visible / base));
        if (Math.abs(nueva - a) / a < 0.02 && Math.abs(h * total - visible) / visible < 0.02) return false;
        sc.setBaseValue(sc.getBaseValue() * nueva / a);
        AttributeInstance step = e.getAttribute(Attribute.STEP_HEIGHT);
        if (step != null) step.setBaseValue(Math.max(0.6, Math.min(8, nueva * 0.6)));
        t.scaler(ModelScaler.entity().multiply((float) (visible / (h * nueva))));
        return true;
    }

    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        if (a.length > 0 && a[0].equals("recargar")) { reloadConfig(); factor = getConfig().getDouble("factor", 0.9);
            excluir = getConfig().getStringList("excluir-modelos"); mundosExcluidos = getConfig().getStringList("mundos-excluidos"); leerModelos(); }
        s.sendMessage("AstralTamanos: " + altos.size() + " modelos, factor " + factor + ", ajustados " + ajustados);
        return true;
    }
}
