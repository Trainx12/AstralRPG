package astraltest;

import org.bukkit.Bukkit;
import org.bukkit.command.*;
import org.bukkit.entity.Display;
import org.bukkit.plugin.java.JavaPlugin;
import kr.toxicity.model.api.tracker.EntityTrackerRegistry;

/** Prueba local: observa los displays reales del tracker; no es una captura visual. */
public final class ArreglosProbe extends JavaPlugin {
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        int tested=0;
        for(var registry:EntityTrackerRegistry.registries()) {
            var entity=Bukkit.getEntity(registry.uuid());
            String run=args.length>0?args[0]:"arreglos.probe";
            if(entity==null || !entity.getScoreboardTags().contains(run))continue;
            int total=0, glowing=0, white=0;
            for(var display:registry.displays().toList()) {
                try {
                    Object nms=display.getClass().getMethod("getDisplay").invoke(display);
                    var bukkit=(Display)nms.getClass().getMethod("getBukkitEntity").invoke(nms);
                    total++;
                    if(bukkit.isGlowing())glowing++;
                    if(bukkit.getGlowColorOverride()!=null && bukkit.getGlowColorOverride().asRGB()==0xffffff)white++;
                } catch(ReflectiveOperationException ex) {throw new IllegalStateException(ex);}
            }
            boolean expected=entity.getScoreboardTags().contains("arreglos.expected_glow");
            boolean ok=total>0 && (expected ? glowing==total && white==total : glowing==0);
            getLogger().info("ARREGLOS_PROBE "+(ok?"PASS":"FAIL")+" "+registry.first().name()+" displays="+total+" glow="+glowing+" white="+white+" expected="+expected);
            tested++;
        }
        getLogger().info("ARREGLOS_PROBE tested="+tested);
        return true;
    }
}
