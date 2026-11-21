package astraltest;

import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.plugin.java.JavaPlugin;

/** Ensayo local del Bosque Astral: tala arboles como la motosierra (sin eventos) y espera que vuelvan. */
public final class BosqueProbe extends JavaPlugin {
    private final List<int[]> boxes = new ArrayList<>();
    private int moldDy;

    @Override public void onEnable() {
        Bukkit.getScheduler().runTaskLater(this, this::start, 20 * 20);
    }

    private boolean wood(Material m) {
        String n = m.name();
        return n.endsWith("_LOG") || n.endsWith("_WOOD") || n.endsWith("LEAVES") || n.endsWith("BEE_NEST");
    }

    private void start() {
        try {
            World w = Bukkit.getWorld("astral_bosque");
            if (w == null) w = Bukkit.createWorld(new org.bukkit.WorldCreator("astral_bosque"));
            List<String> lines = Files.readAllLines(getDataFolder().toPath().resolve("boxes.txt"));
            moldDy = Integer.parseInt(lines.get(0).trim());
            for (String l : lines.subList(1, lines.size())) {
                String[] p = l.trim().split(" ");
                int[] b = new int[6];
                for (int i = 0; i < 6; i++) b[i] = Integer.parseInt(p[i]);
                boxes.add(b);
            }
            int cut = 0;
            for (int[] b : boxes) {
                for (int cx = b[0] >> 4; cx <= b[3] >> 4; cx++)
                    for (int cz = b[2] >> 4; cz <= b[5] >> 4; cz++) w.setChunkForceLoaded(cx, cz, true);
                // Como la motosierra a mitad de tronco: la base (5 bloques de abajo) queda entera.
                for (int x = b[0]; x <= b[3]; x++)
                    for (int y = b[1] + 5; y <= b[4]; y++)
                        for (int z = b[2]; z <= b[5]; z++) {
                            var bl = w.getBlockAt(x, y, z);
                            if (wood(bl.getType())) { bl.setType(Material.AIR, false); cut++; }
                        }
            }
            // Hoja suelta: el ensayo la anota a mano como haria un jugador (no hay jugadores).
            getLogger().info("PROBE talados " + boxes.size() + " arboles, " + cut + " bloques");
            World ww = w;
            Bukkit.getScheduler().runTaskLater(this, () -> check(ww), 20 * 30);
        } catch (Exception e) { getLogger().info("PROBE FAIL " + e); e.printStackTrace(); }
    }

    private void check(World w) {
        int missing = 0, total = 0;
        for (int[] b : boxes)
            for (int x = b[0]; x <= b[3]; x++)
                for (int y = b[1]; y <= b[4]; y++)
                    for (int z = b[2]; z <= b[5]; z++) {
                        Material m = w.getBlockAt(x, y + moldDy, z).getType();
                        if (!wood(m)) continue;
                        total++;
                        if (w.getBlockAt(x, y, z).getType() != m) missing++;
                    }
        getLogger().info((missing == 0 && total > 0 ? "PROBE OK" : "PROBE FAIL") + " madera del molde " + total + ", faltan " + missing);
        Bukkit.getScheduler().runTaskLater(this, () -> Bukkit.shutdown(), 40);
    }
}
