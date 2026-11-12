package astraltest;

import java.io.File;
import java.io.FileInputStream;
import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.java.JavaPlugin;
import com.sk89q.worldedit.WorldEdit;
import com.sk89q.worldedit.bukkit.BukkitAdapter;
import com.sk89q.worldedit.extent.clipboard.Clipboard;
import com.sk89q.worldedit.extent.clipboard.io.ClipboardFormats;
import com.sk89q.worldedit.function.operation.Operations;
import com.sk89q.worldedit.math.BlockVector3;
import com.sk89q.worldedit.session.ClipboardHolder;

/** Solo para armar regiones en Paper local: pega una schematic entera en un mundo. Nunca va al server. */
public final class SchemPaste extends JavaPlugin {
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        try {
            var world = Bukkit.getWorld(args[0]);
            if (world == null) { getLogger().info("PASTE FAIL mundo " + args[0] + " no existe: " + Bukkit.getWorlds()); return true; }
            var file = new File(args[1]);
            Clipboard clip;
            try (var reader = ClipboardFormats.findByFile(file).getReader(new FileInputStream(file))) { clip = reader.read(); }
            var to = BlockVector3.at(Integer.parseInt(args[2]), Integer.parseInt(args[3]), Integer.parseInt(args[4]));
            try (var session = WorldEdit.getInstance().newEditSession(BukkitAdapter.adapt(world))) {
                Operations.complete(new ClipboardHolder(clip).createPaste(session).to(to).ignoreAirBlocks(false).build());
            }
            var min = to.add(clip.getRegion().getMinimumPoint().subtract(clip.getOrigin()));
            var max = to.add(clip.getRegion().getMaximumPoint().subtract(clip.getOrigin()));
            getLogger().info("PASTE OK min=" + min + " max=" + max + " world=" + world.getName());
            // Primer bloque solido bajando desde arriba en el centro: punto provisorio con piso.
            int cx = (min.x() + max.x()) / 2, cz = (min.z() + max.z()) / 2;
            for (int y = max.y(); y >= min.y(); y--) {
                if (world.getBlockAt(cx, y, cz).getType().isSolid()) { getLogger().info("PASTE TOP " + cx + " " + y + " " + cz + " " + world.getBlockAt(cx, y, cz).getType()); break; }
            }
            world.save();
        } catch (Exception e) { getLogger().info("PASTE FAIL " + e); e.printStackTrace(); }
        return true;
    }
}
