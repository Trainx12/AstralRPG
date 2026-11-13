package astraltest;

import java.io.*;
import java.util.*;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.data.Waterlogged;
import org.bukkit.generator.ChunkGenerator;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Solo Paper local: copia la arena del mapa de terceros (mundo principal) a un mundo vacio "fosa",
 * sin los bloques de comando y con el aire de adentro convertido en agua. Lista puntos de agua
 * libres (aparicion de mobs) para oceano_fosa.py. Nunca va al server; las regiones quedan en .local.
 */
public final class FosaBuild extends JavaPlugin {
    static final int X0 = -50, X1 = 54, Z0 = 35, Z1 = 153, Y0 = 86, Y1 = 141;

    static final class Vacio extends ChunkGenerator { }

    static long key(int x, int y, int z) { return ((long) (x + 1000) << 32) | ((long) (y + 200) << 20) | (z + 1000); }

    @Override public void onEnable() { Bukkit.getScheduler().runTaskLater(this, this::build, 40); }

    void build() {
        World src = Bukkit.getWorlds().get(0);
        World dst = Bukkit.createWorld(new WorldCreator("fosa").generator(new Vacio()));
        for (int cx = X0 >> 4; cx <= X1 >> 4; cx++) for (int cz = Z0 >> 4; cz <= Z1 >> 4; cz++) {
            src.getChunkAt(cx, cz).load(); dst.getChunkAt(cx, cz).load(true);
            dst.setChunkForceLoaded(cx, cz, true);
        }
        int copied = 0, removed = 0, flooded = 0;
        BlockData water = Bukkit.createBlockData(Material.WATER);
        for (int x = X0; x <= X1; x++) for (int z = Z0; z <= Z1; z++) for (int y = Y0; y <= Y1; y++) {
            Block a = src.getBlockAt(x, y, z), b = dst.getBlockAt(x, y, z);
            Material m = a.getType();
            if (m.name().contains("COMMAND_BLOCK") || m == Material.STRUCTURE_BLOCK || m == Material.MOVING_PISTON
                    || m == Material.REDSTONE_WIRE || m == Material.REPEATER || m == Material.COMPARATOR || m == Material.LEVER) {
                b.setBlockData(m == Material.MOVING_PISTON ? water : Bukkit.createBlockData(Material.STONE), false); removed++; continue;
            }
            if (m.isAir()) { b.setBlockData(water, false); flooded++; continue; }
            BlockData d = a.getBlockData().clone();
            if (d instanceof Waterlogged wl) wl.setWaterlogged(true);
            b.setBlockData(d, false); copied++;
        }
        getLogger().info("FOSA copiados=" + copied + " quitados=" + removed + " aire->agua=" + flooded);
        // Zona jugable: relleno por agua desde el centro de la cueva (4,112,93).
        int sx = 4, sy = 112, sz = 93;
        getLogger().info("FOSA inicio " + dst.getBlockAt(sx, sy, sz).getType());
        Set<Long> seen = new HashSet<>(); ArrayDeque<int[]> q = new ArrayDeque<>();
        q.add(new int[]{sx, sy, sz}); seen.add(key(sx, sy, sz));
        while (!q.isEmpty()) {
            int[] c = q.poll();
            for (int[] d : new int[][]{{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}}) {
                int x = c[0] + d[0], y = c[1] + d[1], z = c[2] + d[2];
                if (x < X0 || x > X1 || z < Z0 || z > Z1 || y < Y0 || y > Y1) continue;
                long k = key(x, y, z);
                if (seen.contains(k)) continue;
                Material m = dst.getBlockAt(x, y, z).getType();
                if (m != Material.WATER && m != Material.SEAGRASS && m != Material.TALL_SEAGRASS && m != Material.KELP && m != Material.KELP_PLANT && m != Material.BUBBLE_COLUMN) continue;
                seen.add(k); q.add(new int[]{x, y, z});
            }
        }
        int ymin = 999, ymax = -999;
        for (long k : seen) { int y = (int) ((k >> 20) & 0x3ff) - 200; ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); }
        getLogger().info("FOSA zona jugable=" + seen.size() + " bloques, y " + ymin + ".." + ymax);
        List<String> pts = new ArrayList<>();
        for (int x = X0 + 2; x <= X1 - 2; x += 3) for (int z = Z0 + 2; z <= Z1 - 2; z += 3) for (int y = 98; y <= 126; y += 3) {
            boolean ok = true;
            for (int dx = -1; dx <= 1 && ok; dx++) for (int dz = -1; dz <= 1 && ok; dz++) for (int dy = 0; dy <= 1 && ok; dy++)
                if (!seen.contains(key(x + dx, y + dy, z + dz))) ok = false;
            if (ok) pts.add(x + "," + y + "," + z);
        }
        getLogger().info("FOSA puntos=" + pts.size());
        try (var out = new PrintWriter(new FileWriter("fosa-puntos.txt"))) { pts.forEach(out::println); } catch (IOException e) { getLogger().warning("" + e); }
        dst.save();
        getLogger().info("FOSA FIN " + dst.getWorldFolder());
        Bukkit.getScheduler().runTaskLater(this, Bukkit::shutdown, 40);
    }
}
