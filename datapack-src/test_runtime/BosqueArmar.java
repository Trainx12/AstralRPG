package astraltest;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.WorldCreator;
import org.bukkit.WorldType;
import org.bukkit.block.data.BlockData;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Solo para Paper local: arma el mundo astral_bosque con el recorte de tools/bosque_mapa.py.
 * Pone el molde (abajo), planta los arboles extra en el molde, copia el molde arriba y cierra con barreras.
 * Uso: bosquearmar <carpeta datos> <mold_dy> <alto_barrera>. Nunca va al server.
 */
public final class BosqueArmar extends JavaPlugin {
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        try {
            Path dir = Path.of(args[0]);
            int moldDy = Integer.parseInt(args[1]);
            int wallTop = Integer.parseInt(args[2]);
            String info = Files.readString(dir.resolve("info.json"));
            int size = num(info, "\"size\":"), y0 = num(info, "\"y0\":");
            List<String> pal = Files.readAllLines(dir.resolve("paleta.txt"));
            BlockData[] data = new BlockData[pal.size()];
            int bad = 0;
            for (int i = 0; i < pal.size(); i++) {
                try { data[i] = Bukkit.createBlockData(pal.get(i)); }
                catch (Exception e) { data[i] = Material.AIR.createBlockData(); bad++; getLogger().info("ARMAR paleta mala: " + pal.get(i)); }
            }
            ByteBuffer buf = ByteBuffer.wrap(Files.readAllBytes(dir.resolve("bloques.u16"))).order(ByteOrder.LITTLE_ENDIAN);
            int H = buf.capacity() / 2 / size / size;
            World w = Bukkit.getWorld("astral_bosque");
            if (w == null) {
                w = Bukkit.createWorld(new WorldCreator("astral_bosque").type(WorldType.FLAT).generateStructures(false)
                    .generatorSettings("{\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:forest\"}"));
            }
            for (int cx = -2; cx <= (size >> 4) + 1; cx++)
                for (int cz = -2; cz <= (size >> 4) + 1; cz++) w.setChunkForceLoaded(cx, cz, true);
            long t = System.currentTimeMillis();
            if (args.length > 3 && args[3].equals("copiar")) { copy(w, size, y0, H, moldDy, wallTop, dir); return true; }
            for (int y = 0; y < H; y++)
                for (int z = 0; z < size; z++)
                    for (int x = 0; x < size; x++) {
                        BlockData d = data[buf.getShort(2 * ((y * size + z) * size + x)) & 0xFFFF];
                        if (d.getMaterial() != Material.AIR) w.getBlockAt(x, y0 + y + moldDy, z).setBlockData(d, false);
                    }
            getLogger().info("ARMAR molde listo en " + (System.currentTimeMillis() - t) + " ms, paleta mala " + bad);
            var rnd = new java.util.Random(20112026L);
            int ok = 0, fail = 0;
            int[][] offs = {{0,0},{1,0},{0,1},{-1,0},{0,-1},{1,1},{-1,-1},{2,0},{0,2},{-2,0},{0,-2},{2,2},{-2,-2},{2,-2},{-2,2},{3,0},{0,3},{-3,0},{0,-3}};
            for (String line : Files.readAllLines(dir.resolve("extra.txt"))) {
                String[] p = line.trim().split(" ");
                if (p.length < 4) continue;
                org.bukkit.TreeType type = switch (p[0]) {
                    case "mega_spruce" -> org.bukkit.TreeType.MEGA_REDWOOD;
                    case "mega_pine" -> org.bukkit.TreeType.MEGA_PINE;
                    case "cherry" -> org.bukkit.TreeType.CHERRY;
                    case "mega_jungle_tree" -> org.bukkit.TreeType.JUNGLE;
                    case "jungle_tree" -> org.bukkit.TreeType.SMALL_JUNGLE;
                    case "pale_oak" -> org.bukkit.TreeType.PALE_OAK;
                    case "super_birch_bees_0002" -> org.bukkit.TreeType.TALL_BIRCH;
                    case "fancy_oak" -> org.bukkit.TreeType.BIG_TREE;
                    default -> org.bukkit.TreeType.TREE;
                };
                int x0 = Integer.parseInt(p[1]), y0t = Integer.parseInt(p[2]) + moldDy, z0 = Integer.parseInt(p[3]);
                boolean done = false;
                for (int[] o : offs) {
                    int x = x0 + o[0], z = z0 + o[1];
                    int gy = Integer.MIN_VALUE;
                    for (int y = y0t + 4; y >= y0t - 5; y--) {
                        var b = w.getBlockAt(x, y, z);
                        if (b.getType().isSolid() && !b.getType().name().endsWith("LEAVES")) { gy = y; break; }
                    }
                    if (gy == Integer.MIN_VALUE) continue;
                    String g = w.getBlockAt(x, gy, z).getType().name();
                    if (!(g.contains("DIRT") || g.contains("GRASS_BLOCK") || g.contains("PODZOL") || g.contains("MOSS_BLOCK"))) continue;
                    for (int dy = 1; dy <= 2; dy++) {
                        var b = w.getBlockAt(x, gy + dy, z);
                        if (!b.getType().isSolid() && b.getType() != Material.AIR && b.getType() != Material.WATER) b.setType(Material.AIR, false);
                    }
                    if (w.generateTree(new org.bukkit.Location(w, x, gy + 1, z), rnd, type)) { done = true; break; }
                }
                if (done) ok++; else { fail++; getLogger().info("ARMAR arbol no crecio: " + line); }
            }
            getLogger().info("ARMAR arboles extra ok=" + ok + " fallaron=" + fail);
            getLogger().info("ARMAR FASE1 OK");
        } catch (Exception e) { getLogger().info("ARMAR FAIL " + e); e.printStackTrace(); }
        return true;
    }

    private void copy(World w, int size, int y0, int H, int moldDy, int wallTop, Path dir) throws Exception {
            long t = System.currentTimeMillis();
            // Molde -> bosque (bloque por bloque, sin fisica).
            for (int y = 0; y < H; y++)
                for (int z = 0; z < size; z++)
                    for (int x = 0; x < size; x++) {
                        BlockData d = w.getBlockAt(x, y0 + y + moldDy, z).getBlockData();
                        if (d.getMaterial() != Material.AIR) w.getBlockAt(x, y0 + y, z).setBlockData(d, false);
                    }
            // Borde de barreras alrededor del bosque (como en las mazmorras).
            BlockData barrier = Material.BARRIER.createBlockData();
            for (int y = y0; y <= wallTop; y++)
                for (int i = -1; i <= size; i++) {
                    w.getBlockAt(i, y, -1).setBlockData(barrier, false);
                    w.getBlockAt(i, y, size).setBlockData(barrier, false);
                    w.getBlockAt(-1, y, i).setBlockData(barrier, false);
                    w.getBlockAt(size, y, i).setBlockData(barrier, false);
                }
            w.save();
            getLogger().info("ARMAR OK en " + (System.currentTimeMillis() - t) + " ms");
    }

    private static int num(String json, String key) {
        int i = json.indexOf(key) + key.length();
        while (!Character.isDigit(json.charAt(i)) && json.charAt(i) != '-') i++;
        int j = i + 1;
        while (Character.isDigit(json.charAt(j))) j++;
        return Integer.parseInt(json.substring(i, j));
    }
}
