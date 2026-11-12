import java.nio.file.*;
import net.minecraft.SharedConstants;
import net.minecraft.nbt.*;
import net.minecraft.util.datafix.*;

/** Converts inert private chunks with the same DataFixer shipped by Paper. */
class ConvertLegacyChunks {
    public static void main(String[] args) throws Exception {
        SharedConstants.tryDetectVersion();
        var fixer = DataFixers.getDataFixer();
        var input = Path.of(args[0]);
        var output = Path.of(args[1]);
        Files.createDirectories(output);
        int count = 0;
        try (var files = Files.list(input)) {
            for (var path : files.filter(p -> p.toString().endsWith(".nbt")).sorted().toList()) {
                var old = NbtIo.readCompressed(path, NbtAccounter.unlimitedHeap());
                int sourceVersion = args.length > 2 ? Integer.parseInt(args[2]) : 1343;
                var converted = DataFixTypes.CHUNK.updateToCurrentVersion(fixer, old, sourceVersion);
                converted.putInt("DataVersion", SharedConstants.getCurrentVersion().dataVersion().version());
                NbtIo.writeCompressed(converted, output.resolve(path.getFileName()));
                count++;
            }
        }
        System.out.println("Converted " + count + " chunks");
        System.exit(0); // DataFixer workers must not keep the preparation process alive.
    }
}
