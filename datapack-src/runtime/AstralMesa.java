package astral;

import java.util.*;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.*;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.EnchantmentStorageMeta;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Mesa de encantamientos de AstralRPG (reemplaza a LynExp).
 * Ofrece TODOS los encantamientos que acepta el objeto (vanilla, ExcellentEnchants y otros),
 * menos las mejoras del Herrero (namespace astral). Con paginas: LynExp cortaba la lista en 48 libros
 * y los vanilla quedaban afuera. Generado por datapack-src/mesa_encantamientos.py.
 */
public final class AstralMesa extends JavaPlugin implements Listener {
    static final int POR_PAGINA = 45, ANTERIOR = 45, INFO = 48, OBJETO = 49, SIGUIENTE = 53;

    public record Opcion(Enchantment ench, int nivel, int puntos, int niveles) {}

    static final class Mesa implements InventoryHolder {
        final UUID dueno;
        ItemStack objeto;
        int pagina;
        List<Opcion> opciones = List.of();
        Inventory inv;
        Mesa(UUID dueno) { this.dueno = dueno; }
        @Override public Inventory getInventory() { return inv; }
    }

    int nivelesMax = 30, botellaCosto = 5;
    boolean particulas = true;
    Set<String> excluirNs = Set.of("astral");
    Set<String> excluir = Set.of();
    final Map<Material, Integer> conducto = new EnumMap<>(Material.class);
    final Map<String, String> descripciones = new HashMap<>();
    Set<String> bastones = Set.of();

    @Override public void onEnable() {
        saveDefaultConfig();
        cargar();
        getServer().getPluginManager().registerEvents(this, this);
    }

    @Override public void onDisable() {
        for (Player p : Bukkit.getOnlinePlayers())
            if (p.getOpenInventory().getTopInventory().getHolder() instanceof Mesa m) { devolver(p, m); p.closeInventory(); }
    }

    void cargar() {
        reloadConfig();
        var c = getConfig();
        nivelesMax = Math.max(1, c.getInt("niveles-maximo", 30));
        botellaCosto = Math.max(1, c.getInt("botella.costo-xp", 5));
        particulas = c.getBoolean("particulas", true);
        excluirNs = new HashSet<>(c.getStringList("excluir-namespaces"));
        excluir = new HashSet<>(c.getStringList("excluir"));
        bastones = new HashSet<>(c.getStringList("bastones"));
        descripciones.clear();
        var des = c.getConfigurationSection("descripciones");
        if (des != null) for (String k : des.getKeys(false)) descripciones.put(k, des.getString(k, ""));
        conducto.clear();
        var sec = c.getConfigurationSection("conducto");
        if (sec != null) for (String k : sec.getKeys(false)) {
            Material m = Material.matchMaterial(k);
            if (m != null) conducto.put(m, sec.getInt(k));
        }
    }

    @Override public boolean onCommand(CommandSender s, Command cmd, String label, String[] args) {
        if (args.length == 1 && args[0].equalsIgnoreCase("reload")) {
            cargar();
            s.sendMessage(Component.text("AstralMesa recargada.", NamedTextColor.GREEN));
            return true;
        }
        return false;
    }

    // ---------- XP (mismas cuentas que vanilla y LynExp) ----------
    public static int xpHastaNivel(int n) {
        if (n <= 16) return n * n + 6 * n;
        if (n <= 31) return (int) (2.5 * n * n - 40.5 * n + 360);
        return (int) (4.5 * n * n - 162.5 * n + 2220);
    }
    static int xpParaSubir(int n) { return n <= 15 ? 2 * n + 7 : n <= 30 ? 5 * n - 38 : 9 * n - 158; }
    public static int xpTotal(Player p) {
        return xpHastaNivel(p.getLevel()) + Math.round(p.getExp() * xpParaSubir(p.getLevel()));
    }
    public static void ponerXp(Player p, int total) {
        total = Math.max(0, total);
        int lvl = 0;
        while (xpHastaNivel(lvl + 1) <= total) lvl++;
        p.setLevel(lvl);
        p.setExp(Math.min(0.9999f, (total - xpHastaNivel(lvl)) / (float) xpParaSubir(lvl)));
        p.setTotalExperience(total);
    }

    // ---------- Opciones ----------
    public static String clave(Enchantment e) { return e.getKey().toString(); }

    public List<Opcion> opciones(ItemStack it) {
        if (it == null || it.getType().isAir() || it.getType() == Material.ENCHANTED_BOOK) return List.of();
        var lista = new ArrayList<Opcion>();
        var tiene = it.getEnchantments();
        boolean baston = esBaston(it);
        for (Enchantment e : Registry.ENCHANTMENT) {
            if (excluirNs.contains(e.getKey().getNamespace()) || excluir.contains(clave(e))) continue;
            if (!e.canEnchantItem(it) && !(baston && bastones.contains(clave(e)))) continue;
            int actual = tiene.getOrDefault(e, 0), max = e.getMaxLevel();
            if (actual >= max) continue;
            boolean choca = false;
            for (Enchantment o : tiene.keySet())
                if (!o.equals(e) && (o.conflictsWith(e) || e.conflictsWith(o))) { choca = true; break; }
            if (choca) continue;
            for (int n = Math.max(actual + 1, e.getStartLevel()); n <= max; n++) {
                int niveles = (int) Math.ceil(n / (double) max * nivelesMax);
                lista.add(new Opcion(e, n, xpHastaNivel(niveles), niveles));
            }
        }
        // Vanilla primero, despues los demas plugins; maldiciones al final; por nombre y nivel.
        lista.sort(Comparator.<Opcion>comparingInt(o -> o.ench().isCursed() ? 2 : o.ench().getKey().getNamespace().equals("minecraft") ? 0 : 1)
            .thenComparing(o -> o.ench().getKey().getNamespace())
            .thenComparing(o -> o.ench().getKey().getKey())
            .thenComparingInt(Opcion::nivel));
        return lista;
    }

    /** Bastones de mago: carrot_on_a_stick con custom_data astral w:"staff" (build.py). */
    public static boolean esBaston(ItemStack it) {
        if (it == null || it.getType() != Material.CARROT_ON_A_STICK || !it.hasItemMeta()) return false;
        String s = it.getItemMeta().getAsComponentString().replace(" ", "");
        return s.contains("w:\"staff\"") || s.contains("\"w\":\"staff\"");
    }

    // ---------- Ventana ----------
    static ItemStack boton(Material mat, Component nombre, List<Component> lore) {
        var it = new ItemStack(mat);
        ItemMeta m = it.getItemMeta();
        m.displayName(nombre.decoration(TextDecoration.ITALIC, false));
        m.lore(lore.stream().map(l -> l.decoration(TextDecoration.ITALIC, false)).toList());
        m.addItemFlags(ItemFlag.values());
        it.setItemMeta(m);
        return it;
    }

    void abrir(Player p) {
        var mesa = new Mesa(p.getUniqueId());
        mesa.inv = Bukkit.createInventory(mesa, 54, Component.text("Mesa de encantamientos"));
        dibujar(p, mesa);
        p.openInventory(mesa.inv);
    }

    void dibujar(Player p, Mesa mesa) {
        var inv = mesa.inv;
        inv.clear();
        mesa.opciones = opciones(mesa.objeto);
        int paginas = Math.max(1, (mesa.opciones.size() + POR_PAGINA - 1) / POR_PAGINA);
        mesa.pagina = Math.min(mesa.pagina, paginas - 1);
        int tengo = xpTotal(p);
        for (int i = 0; i < POR_PAGINA; i++) {
            int idx = mesa.pagina * POR_PAGINA + i;
            if (idx >= mesa.opciones.size()) break;
            Opcion o = mesa.opciones.get(idx);
            var libro = new ItemStack(Material.ENCHANTED_BOOK);
            var meta = (EnchantmentStorageMeta) libro.getItemMeta();
            meta.addStoredEnchant(o.ench(), o.nivel(), true);
            meta.displayName(o.ench().displayName(o.nivel()).decoration(TextDecoration.ITALIC, false));
            boolean alcanza = tengo >= o.puntos();
            var lore = new ArrayList<Component>();
            lore.add(Component.text(o.ench().getKey().getNamespace().equals("minecraft") ? "Encantamiento normal" : "Encantamiento especial", NamedTextColor.DARK_GRAY));
            String desc = descripciones.get(clave(o.ench()));
            if (desc != null && !desc.isBlank()) {
                for (String linea : partir(desc, 34)) lore.add(Component.text(linea, NamedTextColor.GRAY));
            }
            if (o.ench().getMaxLevel() > 1)
                lore.add(Component.text("Nivel " + o.nivel() + " de " + o.ench().getMaxLevel() + " (más nivel, más fuerte)", NamedTextColor.DARK_GRAY));
            lore.add(Component.empty());
            lore.add(Component.text("Cuesta " + o.puntos() + " puntos de XP (" + o.niveles() + " niveles)", alcanza ? NamedTextColor.GOLD : NamedTextColor.RED));
            lore.add(Component.text(alcanza ? "Clic para encantar" : "No te alcanza la XP", alcanza ? NamedTextColor.GREEN : NamedTextColor.RED));
            meta.lore(lore.stream().map(l -> l.decoration(TextDecoration.ITALIC, false)).toList());
            meta.addItemFlags(ItemFlag.HIDE_STORED_ENCHANTS);
            libro.setItemMeta(meta);
            inv.setItem(i, libro);
        }
        var vidrio = boton(Material.BLACK_STAINED_GLASS_PANE, Component.text(" "), List.of());
        for (int s = 45; s < 54; s++) inv.setItem(s, vidrio);
        if (mesa.objeto == null) {
            inv.setItem(OBJETO, boton(Material.LIME_STAINED_GLASS_PANE, Component.text("Poné un objeto", NamedTextColor.GREEN),
                List.of(Component.text("Hacé clic en un arma, herramienta o", NamedTextColor.GRAY),
                        Component.text("armadura de tu inventario.", NamedTextColor.GRAY))));
        } else {
            var muestra = mesa.objeto.clone();
            inv.setItem(OBJETO, muestra);
            if (mesa.opciones.isEmpty())
                inv.setItem(22, boton(Material.BARRIER, Component.text("No hay encantamientos para agregar", NamedTextColor.RED),
                    List.of(Component.text("Ya tiene todo al máximo o no se puede encantar.", NamedTextColor.GRAY))));
        }
        inv.setItem(INFO, boton(Material.EXPERIENCE_BOTTLE, Component.text("Tu XP: " + tengo + " puntos", NamedTextColor.YELLOW),
            List.of(Component.text("Nivel " + p.getLevel(), NamedTextColor.GRAY),
                    Component.text("Página " + (mesa.pagina + 1) + " de " + paginas, NamedTextColor.GRAY),
                    Component.text("Clic en el objeto de abajo para sacarlo.", NamedTextColor.DARK_GRAY))));
        if (mesa.pagina > 0)
            inv.setItem(ANTERIOR, boton(Material.ARROW, Component.text("Página anterior", NamedTextColor.AQUA), List.of()));
        if (mesa.pagina < paginas - 1)
            inv.setItem(SIGUIENTE, boton(Material.ARROW, Component.text("Página siguiente", NamedTextColor.AQUA), List.of()));
    }

    /** Corta el texto en lineas de hasta 'ancho' letras sin partir palabras. */
    public static List<String> partir(String texto, int ancho) {
        var out = new ArrayList<String>();
        var linea = new StringBuilder();
        for (String w : texto.trim().split("\\s+")) {
            if (linea.length() > 0 && linea.length() + 1 + w.length() > ancho) { out.add(linea.toString()); linea.setLength(0); }
            if (linea.length() > 0) linea.append(' ');
            linea.append(w);
        }
        if (linea.length() > 0) out.add(linea.toString());
        return out;
    }

    /** Descripcion de un encantamiento por su clave (para pruebas). */
    public String descripcion(String clave) { return descripciones.get(clave); }

    void devolver(Player p, Mesa m) {
        if (m.objeto == null) return;
        var sobra = p.getInventory().addItem(m.objeto);
        sobra.values().forEach(it -> p.getWorld().dropItemNaturally(p.getLocation(), it));
        m.objeto = null;
    }

    /** Aplica una opcion: cobra la XP y encanta. Devuelve un mensaje de error o null si salio bien. */
    public String encantar(Player p, ItemStack objeto, Opcion o) {
        int tengo = xpTotal(p);
        if (tengo < o.puntos()) return "No te alcanza la XP: necesitás " + o.puntos() + " puntos y tenés " + tengo + ".";
        ponerXp(p, tengo - o.puntos());
        objeto.addUnsafeEnchantment(o.ench(), o.nivel());
        return null;
    }

    // ---------- Eventos ----------
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void alAbrir(InventoryOpenEvent e) {
        if (e.getInventory().getType() != InventoryType.ENCHANTING || !(e.getPlayer() instanceof Player p)) return;
        e.setCancelled(true);
        Bukkit.getScheduler().runTask(this, () -> { if (p.isOnline()) abrir(p); });
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void alTocar(PlayerInteractEvent e) {
        if (e.getAction() != Action.RIGHT_CLICK_BLOCK || e.getClickedBlock() == null || e.getHand() != EquipmentSlot.HAND) return;
        Player p = e.getPlayer();
        ItemStack mano = p.getInventory().getItemInMainHand();
        Material bloque = e.getClickedBlock().getType();
        if (bloque == Material.ENCHANTING_TABLE && mano.getType() == Material.GLASS_BOTTLE) {
            e.setCancelled(true);
            int tengo = xpTotal(p);
            if (tengo < botellaCosto) { p.sendMessage(Component.text("No tenés XP suficiente para embotellar.", NamedTextColor.RED)); return; }
            ponerXp(p, tengo - botellaCosto);
            mano.setAmount(mano.getAmount() - 1);
            p.getInventory().addItem(new ItemStack(Material.EXPERIENCE_BOTTLE))
                .values().forEach(it -> p.getWorld().dropItemNaturally(p.getLocation(), it));
            p.sendMessage(Component.text("Embotellaste tu experiencia.", NamedTextColor.GREEN));
        } else if (bloque == Material.CONDUIT && conducto.containsKey(mano.getType())) {
            e.setCancelled(true);
            int xp = conducto.get(mano.getType());
            mano.setAmount(mano.getAmount() - 1);
            p.giveExp(xp, false);
            p.playSound(p.getLocation(), Sound.BLOCK_CONDUIT_AMBIENT, 1f, 1.4f);
            p.sendMessage(Component.text("+" + xp + " XP", NamedTextColor.GREEN));
        }
    }

    @EventHandler
    public void alClic(InventoryClickEvent e) {
        if (!(e.getView().getTopInventory().getHolder() instanceof Mesa mesa) || !(e.getWhoClicked() instanceof Player p)) return;
        e.setCancelled(true);
        Inventory clic = e.getClickedInventory();
        if (clic == null) return;
        if (clic != mesa.inv) {
            // Poner un objeto desde el inventario del jugador.
            ItemStack it = clic.getItem(e.getSlot());
            if (it == null || it.getType().isAir()) return;
            var uno = it.clone(); uno.setAmount(1);
            if (opciones(uno).isEmpty() && uno.getEnchantments().isEmpty()) {
                p.sendMessage(Component.text("Ese objeto no se puede encantar acá.", NamedTextColor.RED));
                return;
            }
            it.setAmount(it.getAmount() - 1);
            clic.setItem(e.getSlot(), it.getAmount() > 0 ? it : null);
            devolver(p, mesa);
            mesa.objeto = uno;
            mesa.pagina = 0;
            p.playSound(p.getLocation(), Sound.ITEM_ARMOR_EQUIP_GENERIC, 0.7f, 1.2f);
            dibujar(p, mesa);
            return;
        }
        int s = e.getSlot();
        if (s == ANTERIOR && mesa.pagina > 0) { mesa.pagina--; dibujar(p, mesa); }
        else if (s == SIGUIENTE) { mesa.pagina++; dibujar(p, mesa); }
        else if (s == OBJETO && mesa.objeto != null) { devolver(p, mesa); mesa.pagina = 0; dibujar(p, mesa); }
        else if (s < POR_PAGINA && mesa.objeto != null) {
            int idx = mesa.pagina * POR_PAGINA + s;
            if (idx >= mesa.opciones.size()) return;
            Opcion o = mesa.opciones.get(idx);
            String error = encantar(p, mesa.objeto, o);
            if (error != null) {
                p.sendMessage(Component.text(error, NamedTextColor.RED));
                p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1f, 0.6f);
                return;
            }
            p.playSound(p.getLocation(), Sound.BLOCK_ENCHANTMENT_TABLE_USE, 1f, 1f);
            if (particulas) p.spawnParticle(Particle.ENCHANT, p.getLocation().add(0, 1, 0), 60, 0.5, 0.5, 0.5);
            p.sendMessage(Component.text("Encantaste con ", NamedTextColor.GREEN).append(o.ench().displayName(o.nivel()))
                .append(Component.text(" (-" + o.puntos() + " XP).", NamedTextColor.GREEN)));
            dibujar(p, mesa);
        }
    }

    @EventHandler
    public void alArrastrar(InventoryDragEvent e) {
        if (e.getView().getTopInventory().getHolder() instanceof Mesa) e.setCancelled(true);
    }

    @EventHandler
    public void alCerrar(InventoryCloseEvent e) {
        if (e.getInventory().getHolder() instanceof Mesa m && e.getPlayer() instanceof Player p) devolver(p, m);
    }

    @EventHandler
    public void alSalir(PlayerQuitEvent e) {
        if (e.getPlayer().getOpenInventory().getTopInventory().getHolder() instanceof Mesa m) devolver(e.getPlayer(), m);
    }
}
