package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

/** Ensayo local de LynExp: que libros ofrece la Mesa para un objeto. Nunca va al server. */
public final class LynProbe extends JavaPlugin {
    @Override public void onEnable() {
        Bukkit.getScheduler().runTaskLater(this, () -> {
            try {
                var lyn = Bukkit.getPluginManager().getPlugin("LynExp");
                var util = Class.forName("dev.foksha.lynExp.gui.EnchantmentUtil", true, lyn.getClass().getClassLoader());
                var inst = util.getField("INSTANCE").get(null);
                var m = util.getMethod("getEnchantmentBooksFor", ItemStack.class);
                for (String id : List.of("minecraft:diamond_sword", "minecraft:netherite_chestplate", "minecraft:bow", "minecraft:stick")) {
                    var item = Bukkit.getItemFactory().createItemStack(id);
                    var books = (List<?>) m.invoke(inst, item);
                    var names = new ArrayList<String>();
                    for (Object b : books) {
                        var meta = (org.bukkit.inventory.meta.EnchantmentStorageMeta) ((ItemStack) b).getItemMeta();
                        meta.getStoredEnchants().forEach((e, l) -> names.add(e.getKey() + " " + l));
                    }
                    getLogger().info("LYN " + id + " (" + names.size() + "): " + names);
                    getLogger().info("LYN " + id + " astral: " + names.stream().filter(n -> n.startsWith("astral:")).toList());
                }
            } catch (Throwable t) { getLogger().warning("LYN FAIL " + t); t.printStackTrace(); }
            try {
                // Efecto de Mejora +10 (x1.4) con un golpe real de un zombie.
                var w = Bukkit.getWorlds().get(0);
                w.setChunkForceLoaded(0, 0, true); w.getChunkAt(0, 0).load();
                var at = new Location(w, 0.5, -60, 0.5);
                double[] hit = new double[3];
                for (int i = 0; i < 3; i++) {
                    var z = (org.bukkit.entity.Zombie) w.spawnEntity(at, org.bukkit.entity.EntityType.ZOMBIE);
                    var v = (org.bukkit.entity.Husk) w.spawnEntity(at.clone().add(1, 0, 0), org.bukkit.entity.EntityType.HUSK);
                    z.setAI(false); v.setAI(false);
                    var sword = new ItemStack(Material.DIAMOND_SWORD);
                    if (i == 2) sword.addUnsafeEnchantment(Registry.ENCHANTMENT.get(new NamespacedKey("astral", "mejora_arma")), 10);
                    z.getEquipment().setItemInMainHand(sword);
                    var fb = Bukkit.createCommandSender(c -> getLogger().info("LYN cmd: " + net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(c)));
                    if (i == 1) Bukkit.dispatchCommand(fb,
                        "item modify entity " + z.getUniqueId() + " weapon.mainhand {function:\"minecraft:set_enchantments\",enchantments:{\"astral:mejora_arma\":10}}");
                    v.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).setBaseValue(1000); v.setHealth(1000);
                    z.attack(v);
                    hit[i] = 1000 - v.getHealth();
                    getLogger().info("LYN golpe " + i + " " + hit[i] + " " + z.getEquipment().getItemInMainHand().getEnchantments());
                    z.remove(); v.remove();
                }
                getLogger().info("LYN MEJORA ratio comando " + (hit[1] / hit[0]) + " api " + (hit[2] / hit[0]));
            } catch (Throwable t) { getLogger().warning("LYN FAIL golpe " + t); t.printStackTrace(); }
            getLogger().info("LYN DONE");
            Bukkit.shutdown();
        }, 40);
    }
}
