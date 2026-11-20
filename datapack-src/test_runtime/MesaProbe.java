package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

/** Ensayo local de AstralMesa: que encantamientos ofrece para cada objeto. Nunca va al server. */
public final class MesaProbe extends JavaPlugin {
    @Override public void onEnable() {
        Bukkit.getScheduler().runTaskLater(this, () -> {
            try {
                var mesa = Bukkit.getPluginManager().getPlugin("AstralMesa");
                var m = mesa.getClass().getMethod("opciones", ItemStack.class);
                for (String id : List.of("minecraft:diamond_sword", "minecraft:netherite_chestplate", "minecraft:bow",
                                         "minecraft:diamond_pickaxe", "minecraft:stick")) {
                    var item = Bukkit.getItemFactory().createItemStack(id);
                    var ops = (List<?>) m.invoke(mesa, item);
                    var porNs = new TreeMap<String, Integer>();
                    var nombres = new LinkedHashSet<String>();
                    for (Object o : ops) {
                        var e = (org.bukkit.enchantments.Enchantment) o.getClass().getMethod("ench").invoke(o);
                        porNs.merge(e.getKey().getNamespace(), 1, Integer::sum);
                        nombres.add(e.getKey().toString());
                    }
                    getLogger().info("MESA " + id + " libros=" + ops.size() + " " + porNs + " encantamientos=" + nombres.size());
                    getLogger().info("MESA " + id + " lista " + nombres);
                }
                // Espada con Filo IV: no debe ofrecer Filo 1-4 ni Castigo (choca).
                var s = new ItemStack(Material.DIAMOND_SWORD);
                s.addEnchantment(Registry.ENCHANTMENT.get(NamespacedKey.minecraft("sharpness")), 4);
                var ops = (List<?>) m.invoke(mesa, s);
                var filo = new ArrayList<String>();
                for (Object o : ops) {
                    var e = (org.bukkit.enchantments.Enchantment) o.getClass().getMethod("ench").invoke(o);
                    if (List.of("sharpness", "smite", "bane_of_arthropods").contains(e.getKey().getKey()))
                        filo.add(e.getKey().getKey() + " " + o.getClass().getMethod("nivel").invoke(o) + " $" + o.getClass().getMethod("puntos").invoke(o));
                }
                getLogger().info("MESA filo4 -> " + filo);
                var sinDesc = new TreeSet<String>();
                var dm = mesa.getClass().getMethod("descripcion", String.class);
                for (var e : Registry.ENCHANTMENT) {
                    String k = e.getKey().toString();
                    if (k.startsWith("astral:")) continue;
                    if (dm.invoke(mesa, k) == null) sinDesc.add(k);
                }
                getLogger().info("MESA sin descripcion: " + sinDesc);
                getLogger().info("MESA ejemplo vampire: " + dm.invoke(mesa, "excellentenchants:vampire") + " / partir " +
                    mesa.getClass().getMethod("partir", String.class, int.class).invoke(null, dm.invoke(mesa, "minecraft:smite"), 34));
                var baston = Bukkit.getItemFactory().createItemStack("minecraft:carrot_on_a_stick[custom_data={astral:{w:\"staff\",tier:1}}]");
                var bops = (List<?>) m.invoke(mesa, baston);
                var bn = new LinkedHashSet<String>();
                for (Object o : bops) bn.add(((org.bukkit.enchantments.Enchantment) o.getClass().getMethod("ench").invoke(o)).getKey().toString());
                getLogger().info("MESA baston -> " + bn);
                var gancho = Bukkit.getItemFactory().createItemStack("minecraft:carrot_on_a_stick");
                getLogger().info("MESA cana zanahoria comun -> " + ((List<?>) m.invoke(mesa, gancho)).size() + " libros");
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "astralmesa faltan");
                var en = (java.util.function.Function<String, org.bukkit.enchantments.Enchantment>) k -> Registry.ENCHANTMENT.get(NamespacedKey.fromString(k));
                var bt = mesa.getClass().getMethod("bloqueTexto", ItemStack.class);
                var pocas = new ItemStack(Material.DIAMOND_SWORD);
                pocas.addUnsafeEnchantment(en.apply("minecraft:sharpness"), 5);
                pocas.addUnsafeEnchantment(en.apply("excellentenchants:vampire"), 2);
                pocas.addUnsafeEnchantment(en.apply("nova_structures:illagers_bane"), 3);
                getLogger().info("MESA tooltip pocas: " + bt.invoke(mesa, pocas));
                var muchas = pocas.clone();
                for (String k : List.of("minecraft:looting", "minecraft:unbreaking", "minecraft:mending", "excellentenchants:thunder", "stellarity:critical_strike", "minecraft:vanishing_curse"))
                    muchas.addUnsafeEnchantment(en.apply(k), 2);
                getLogger().info("MESA tooltip muchas: " + bt.invoke(mesa, muchas));
                var dec = (ItemStack) mesa.getClass().getMethod("decorar", ItemStack.class).invoke(mesa, muchas);
                var lim = (ItemStack) mesa.getClass().getMethod("limpiar", ItemStack.class).invoke(mesa, dec);
                getLogger().info("MESA limpiar vuelve igual: " + lim.equals(muchas) + " ocultaAntes=" + muchas.getItemMeta().hasItemFlag(org.bukkit.inventory.ItemFlag.HIDE_ENCHANTS) + " ocultaDespues=" + lim.getItemMeta().hasItemFlag(org.bukkit.inventory.ItemFlag.HIDE_ENCHANTS));
                var cn = mesa.getClass().getMethod("costoNiveles", org.bukkit.enchantments.Enchantment.class);
                getLogger().info("MESA costos mending=" + cn.invoke(mesa, en.apply("minecraft:mending")) + " sharpness=" + cn.invoke(mesa, en.apply("minecraft:sharpness")) + " knockback=" + cn.invoke(mesa, en.apply("minecraft:knockback")) + " curse=" + cn.invoke(mesa, en.apply("minecraft:vanishing_curse")));
                var todos = new TreeSet<String>();
                for (Object o : (List<?>) m.invoke(mesa, new ItemStack(Material.DIAMOND_SWORD)))
                    todos.add(((org.bukkit.enchantments.Enchantment) o.getClass().getMethod("ench").invoke(o)).getKey().getNamespace());
                getLogger().info("MESA espada namespaces " + todos);
                var tecnicos = new TreeSet<String>();
                for (Object o : (List<?>) m.invoke(mesa, new ItemStack(Material.STICK)))
                    tecnicos.add(((org.bukkit.enchantments.Enchantment) o.getClass().getMethod("ench").invoke(o)).getKey().toString());
                getLogger().info("MESA palo (tecnicos?) " + tecnicos);
                getLogger().info("MESA xp30 " + mesa.getClass().getMethod("xpHastaNivel", int.class).invoke(null, 30));
            } catch (Throwable t) { getLogger().warning("MESA FAIL " + t); t.printStackTrace(); }
            getLogger().info("MESA DONE");
            Bukkit.shutdown();
        }, 60);
    }
}
