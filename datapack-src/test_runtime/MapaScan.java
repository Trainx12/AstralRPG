package astraltest;

import java.io.File;
import java.util.*;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.plugin.java.JavaPlugin;

/** Solo Paper local: dibuja desde arriba el mundo principal (mapa de terceros) y lista lo que tiene. */
public final class MapaScan extends JavaPlugin {
    @Override public void onEnable() { Bukkit.getScheduler().runTaskLater(this, this::scan, 40); }

    void scan() {
        World w = Bukkit.getWorlds().get(0);
        int x0 = -56, x1 = 62, z0 = -26, z1 = 158;
        int[] ys = {88, 92, 96, 100, 104, 108, 112, 116, 120, 126, 132, 138};
        List<int[]> todo = new ArrayList<>();
        for (int cx = x0 >> 4; cx <= x1 >> 4; cx++) for (int cz = z0 >> 4; cz <= z1 >> 4; cz++) todo.add(new int[]{cx, cz});
        int W = x1 - x0 + 1, H = z1 - z0 + 1;
        var img = new java.awt.image.BufferedImage(W * ys.length + ys.length, H, java.awt.image.BufferedImage.TYPE_INT_RGB);
        Map<Integer, int[]> perY = new TreeMap<>();
        int[] done = {0};
        for (int[] cc : todo) w.getChunkAtAsync(cc[0], cc[1], false).thenAccept(c -> {
            done[0]++;
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
                int wx = c.getX() * 16 + x, wz = c.getZ() * 16 + z;
                if (wx < x0 || wx > x1 || wz < z0 || wz > z1) continue;
                for (int y = 84; y < 142; y++) {
                    Material m = c.getBlock(x, y, z).getType();
                    int[] cnt = perY.computeIfAbsent(y, k -> new int[3]);
                    if (m == Material.WATER) cnt[0]++; else if (m.isAir()) cnt[1]++; else cnt[2]++;
                }
                for (int i = 0; i < ys.length; i++) {
                    Material m = c.getBlock(x, ys[i], z).getType();
                    int rgb = m == Material.WATER ? 0x1a4a9a : m.isAir() ? 0xffffff : m == Material.BARRIER ? 0xff0000 : m.name().contains("COMMAND") ? 0xffff00 : 0x777766;
                    img.setRGB(i * (W + 1) + wx - x0, wz - z0, rgb);
                }
            }
            if (done[0] == todo.size()) {
                perY.forEach((y, v) -> getLogger().info("MAPA y=" + y + " agua=" + v[0] + " aire=" + v[1] + " solido=" + v[2]));
                try { javax.imageio.ImageIO.write(img, "png", new File("mapa-cortes.png")); } catch (Exception e) { getLogger().warning("" + e); }
                getLogger().info("MAPA FIN"); Bukkit.shutdown();
            }
        });
    }
}
