package astral;

import org.bukkit.NamespacedKey;
import org.bukkit.entity.Entity;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityTransformEvent;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;

/** Solo suprime los orbes vanilla; no interviene en las recompensas de habilidades. */
public final class AstralSpawnerXp extends JavaPlugin implements Listener {
    private NamespacedKey origin;

    @Override public void onEnable() {
        origin = new NamespacedKey(this, "spawner_origin");
        getServer().getPluginManager().registerEvents(this, this);
    }

    private boolean fromSpawner(Entity entity) {
        return switch (entity.getEntitySpawnReason()) {
            case SPAWNER, TRIAL_SPAWNER -> true;
            default -> entity.getPersistentDataContainer().has(origin, PersistentDataType.BYTE);
        };
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void transform(EntityTransformEvent event) {
        if (!fromSpawner(event.getEntity())) return;
        for (Entity child : event.getTransformedEntities()) {
            child.getPersistentDataContainer().set(origin, PersistentDataType.BYTE, (byte) 1);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void death(EntityDeathEvent event) {
        if (fromSpawner(event.getEntity())) event.setDroppedExp(0);
    }
}
