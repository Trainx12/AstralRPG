package astraltest;

import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.java.JavaPlugin;

/** Solo Paper local: busca dos puntos enfrentados con piso y 2 de aire alrededor de una llegada. */
public final class ArenaScan extends JavaPlugin {
    int floor(World w, int x, int y0, int z) {
        for (int y = y0 + 3; y >= y0 - 4; y--) {
            if (w.getBlockAt(x, y - 1, z).getType().isSolid() && w.getBlockAt(x, y, z).isPassable()
                    && w.getBlockAt(x, y + 1, z).isPassable() && !w.getBlockAt(x, y, z).isLiquid()) return y;
        }
        return Integer.MIN_VALUE;
    }
    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        World w = Bukkit.getWorld(a[0]);
        int x = (int) Math.floor(Double.parseDouble(a[1])), y = Integer.parseInt(a[2]), z = (int) Math.floor(Double.parseDouble(a[3]));
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) w.getChunkAt((x >> 4) + dx * 2, (z >> 4) + dz * 2).load(true);
        for (int d = 12; d >= 5; d--) {
            for (int[] dir : new int[][]{{1, 0}, {0, 1}}) {
                int ya = floor(w, x + dir[0] * d, y, z + dir[1] * d), yb = floor(w, x - dir[0] * d, y, z - dir[1] * d);
                if (ya != Integer.MIN_VALUE && yb != Integer.MIN_VALUE && Math.abs(ya - yb) <= 1) {
                    getLogger().info("ARENA " + a[4] + " A=" + (x + dir[0] * d) + "," + ya + "," + (z + dir[1] * d)
                            + " B=" + (x - dir[0] * d) + "," + yb + "," + (z - dir[1] * d) + " eje=" + (dir[0] == 1 ? "x" : "z")
                            + " pisoA=" + w.getBlockAt(x + dir[0] * d, ya - 1, z + dir[1] * d).getType()
                            + " pisoB=" + w.getBlockAt(x - dir[0] * d, yb - 1, z - dir[1] * d).getType());
                    return true;
                }
            }
        }
        getLogger().info("ARENA " + a[4] + " SIN PAR");
        return true;
    }
}
