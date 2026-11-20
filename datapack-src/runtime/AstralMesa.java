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
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import net.kyori.adventure.text.minimessage.MiniMessage;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;
import java.lang.reflect.Method;
import java.util.regex.Pattern;

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
    List<String> excluirContiene = List.of();
    final Map<String, Integer> costos = new HashMap<>();
    final Map<String, String> nombres = new HashMap<>();
    boolean tooltipActivo = true;
    int conDescHasta = 4, porLinea = 3;
    NamespacedKey MARCA, ICONO;
    Object paquetes;  // AstralMesaPaquetes si hay packetevents

    @Override public void onEnable() {
        MARCA = new NamespacedKey(this, "tt");
        ICONO = new NamespacedKey(this, "icono");
        saveDefaultConfig();
        cargar();
        getServer().getPluginManager().registerEvents(this, this);
        if (tooltipActivo && getServer().getPluginManager().getPlugin("packetevents") != null) {
            try { paquetes = AstralMesaPaquetes.registrar(this); getLogger().info("Lista de encantamientos estilo Hypixel activa."); }
            catch (Throwable t) { getLogger().warning("No pude activar la lista de encantamientos: " + t); }
        }
    }

    @Override public void onDisable() {
        if (paquetes != null) try { AstralMesaPaquetes.quitar(paquetes); } catch (Throwable ignored) {}
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
        excluirContiene = c.getStringList("excluir-contiene");
        tooltipActivo = c.getBoolean("tooltip.activo", true);
        conDescHasta = c.getInt("tooltip.con-descripcion-hasta", 4);
        porLinea = Math.max(1, c.getInt("tooltip.por-linea", 3));
        costos.clear();
        seccion(c, "costos").forEach((k, v) -> { try { costos.put(k, Integer.parseInt(v)); } catch (NumberFormatException ignored) {} });
        nombres.clear();
        nombres.putAll(seccion(c, "nombres"));
        descripciones.clear();
        descripciones.putAll(seccion(c, "descripciones"));
        conducto.clear();
        seccion(c, "conducto").forEach((k, v) -> {
            Material m = Material.matchMaterial(k);
            if (m != null) try { conducto.put(m, Integer.parseInt(v)); } catch (NumberFormatException ignored) {}
        });
    }

    /** Lo que trae el jar (textos al dia) y encima lo que el server haya cambiado en su config.yml.
     *  getConfigurationSection no usa los valores por defecto: con un config.yml viejo quedaba vacio. */
    static Map<String, String> seccion(org.bukkit.configuration.file.FileConfiguration c, String path) {
        var out = new LinkedHashMap<String, String>();
        var def = c.getDefaults() == null ? null : c.getDefaults().getConfigurationSection(path);
        if (def != null) for (String k : def.getKeys(false)) out.put(k, String.valueOf(def.get(k)));
        Object propio = c.get(path, null);
        if (propio instanceof org.bukkit.configuration.ConfigurationSection s)
            for (String k : s.getKeys(false)) out.put(k, String.valueOf(s.get(k)));
        return out;
    }

    @Override public boolean onCommand(CommandSender s, Command cmd, String label, String[] args) {
        if (args.length == 1 && args[0].equalsIgnoreCase("reload")) {
            cargar();
            s.sendMessage(Component.text("AstralMesa recargada.", NamedTextColor.GREEN));
            return true;
        }
        if (args.length == 1 && args[0].equalsIgnoreCase("faltan")) {
            var sin = new TreeSet<String>();
            for (Enchantment e : Registry.ENCHANTMENT)
                if (!excluida(e) && !descripciones.containsKey(clave(e)) && descEE(e, 1) == null) sin.add(clave(e));
            s.sendMessage(Component.text("Sin descripcion (" + sin.size() + "): " + sin, NamedTextColor.YELLOW));
            getLogger().info("Sin descripcion: " + sin);
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
            if (excluida(e)) continue;
            if (!e.canEnchantItem(it) && !(baston && bastones.contains(clave(e)))) continue;
            int actual = tiene.getOrDefault(e, 0), max = e.getMaxLevel();
            if (actual >= max) continue;
            boolean choca = false;
            for (Enchantment o : tiene.keySet())
                if (!o.equals(e) && (o.conflictsWith(e) || e.conflictsWith(o))) { choca = true; break; }
            if (choca) continue;
            for (int n = Math.max(actual + 1, e.getStartLevel()); n <= max; n++) {
                int niveles = Math.max(1, (int) Math.ceil(n / (double) max * costoNiveles(e)));
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

    public boolean excluida(Enchantment e) {
        String k = clave(e);
        if (excluirNs.contains(e.getKey().getNamespace()) || excluir.contains(k)) return true;
        return excluidaTecnica(e);
    }

    boolean excluidaTecnica(Enchantment e) {
        String k = clave(e);
        for (String s : excluirContiene) if (k.contains(s)) return true;
        return false;
    }

    public int costoNiveles(Enchantment e) { return costos.getOrDefault(clave(e), nivelesMax); }

    Component calidad(Enchantment e) {
        int c = costoNiveles(e);
        if (e.isCursed() || c < nivelesMax) return Component.text("Maldición", NamedTextColor.RED);
        if (c >= 50) return Component.text("Calidad: ★★★ Muy bueno", NamedTextColor.LIGHT_PURPLE);
        if (c >= 40) return Component.text("Calidad: ★★ Bueno", NamedTextColor.AQUA);
        return Component.text("Calidad: ★ Normal", NamedTextColor.GRAY);
    }

    // ---------- Nombres y descripciones ----------
    static final String[] ROMANOS = {"", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"};
    static String romano(int n) { return n >= 0 && n < ROMANOS.length ? ROMANOS[n] : String.valueOf(n); }

    public Component nombre(Enchantment e, int lvl) {
        String n = nombres.get(clave(e));
        Component c;
        if (n != null && !n.isBlank()) c = Component.text(e.getMaxLevel() > 1 || lvl > 1 ? n + " " + romano(lvl) : n);
        else c = e.displayName(lvl);
        if (!e.getKey().getNamespace().equals("astral"))
            c = Component.text().append(c).color(e.isCursed() ? NamedTextColor.RED : NamedTextColor.BLUE).build();
        return c.decoration(TextDecoration.ITALIC, false);
    }

    Method eeGet, eeDesc; boolean eeBuscado;
    /** Descripcion de ExcellentEnchants con los numeros del nivel (en espanol por ee_descripciones.py), o null. */
    public String descEE(Enchantment e, int lvl) {
        if (!"excellentenchants".equals(e.getKey().getNamespace())) return null;
        try {
            if (!eeBuscado) {
                eeBuscado = true;
                var ee = getServer().getPluginManager().getPlugin("ExcellentEnchants");
                if (ee != null) {
                    var cl = ee.getClass().getClassLoader();
                    eeGet = Class.forName("su.nightexpress.excellentenchants.enchantment.EnchantRegistry", true, cl)
                        .getMethod("getByBukkit", Enchantment.class);
                    eeDesc = Class.forName("su.nightexpress.excellentenchants.api.enchantment.CustomEnchantment", true, cl)
                        .getMethod("getDescription", int.class);
                }
            }
            if (eeGet == null) return null;
            Object ce = eeGet.invoke(null, e);
            if (ce == null) return null;
            @SuppressWarnings("unchecked") List<String> lineas = (List<String>) eeDesc.invoke(ce, lvl);
            var sb = new StringBuilder();
            for (String l : lineas) {
                String plano = PlainTextComponentSerializer.plainText().serialize(MiniMessage.miniMessage().deserialize(l));
                if (sb.length() > 0) sb.append(' ');
                sb.append(plano.trim());
            }
            String r = sb.toString().trim();
            return r.isEmpty() || r.matches(".*%[a-z_]+%.*") ? null : r;
        } catch (Throwable t) { return null; }
    }

    public String textoDe(Enchantment e, int lvl) {
        String ee = descEE(e, lvl);
        return ee != null ? ee : descripciones.get(clave(e));
    }

    static final Pattern NUMERO = Pattern.compile("\\S*\\d\\S*");
    /** Lineas de descripcion: gris con los numeros en verde, como Hypixel. */
    static List<Component> lineasDesc(String texto, int ancho) {
        var out = new ArrayList<Component>();
        if (texto == null || texto.isBlank()) return out;
        for (String l : partir(texto, ancho)) {
            var b = Component.text();
            String[] ws = l.split(" ");
            for (int i = 0; i < ws.length; i++) {
                String w = (i > 0 ? " " : "") + ws[i];
                b.append(Component.text(w, NUMERO.matcher(ws[i]).matches() ? NamedTextColor.GREEN : NamedTextColor.GRAY));
            }
            out.add(b.build().decoration(TextDecoration.ITALIC, false));
        }
        return out;
    }

    // ---------- Lista de encantamientos estilo Hypixel ----------
    int orden(Enchantment e) {
        String ns = e.getKey().getNamespace();
        return ns.equals("astral") ? 0 : e.isCursed() ? 3 : ns.equals("minecraft") ? 1 : 2;
    }

    /** Lineas que van arriba del lore. Vacio si no hay nada que mostrar. */
    public List<Component> bloque(Map<Enchantment, Integer> ench) {
        var lista = new ArrayList<>(ench.entrySet());
        lista.removeIf(en -> excluidaTecnica(en.getKey()));
        if (lista.isEmpty()) return List.of();
        lista.sort(Comparator.<Map.Entry<Enchantment, Integer>>comparingInt(en -> orden(en.getKey()))
            .thenComparing(en -> en.getKey().getKey().toString()));
        var out = new ArrayList<Component>();
        if (lista.size() <= conDescHasta) {
            for (var en : lista) {
                out.add(nombre(en.getKey(), en.getValue()));
                out.addAll(lineasDesc(textoDe(en.getKey(), en.getValue()), 38));
            }
        } else {
            for (int i = 0; i < lista.size(); i += porLinea) {
                var b = Component.text();
                for (int j = i; j < Math.min(i + porLinea, lista.size()); j++) {
                    if (j > i) b.append(Component.text(", ", NamedTextColor.BLUE));
                    b.append(nombre(lista.get(j).getKey(), lista.get(j).getValue()));
                }
                out.add(b.build().decoration(TextDecoration.ITALIC, false));
            }
        }
        out.add(Component.empty());
        return out;
    }

    /** Copia del objeto con la lista arriba del lore y los encantamientos vanilla ocultos; null si no cambia. */
    public ItemStack decorar(ItemStack it) {
        if (it == null || it.getType().isAir() || !it.hasItemMeta()) return null;
        ItemMeta meta = it.getItemMeta();
        var pdc = meta.getPersistentDataContainer();
        if (pdc.has(MARCA) || pdc.has(ICONO)) return null;
        boolean libro = meta instanceof EnchantmentStorageMeta;
        Map<Enchantment, Integer> ench = libro ? ((EnchantmentStorageMeta) meta).getStoredEnchants() : meta.getEnchants();
        if (ench.isEmpty()) return null;
        ItemFlag flag = libro ? ItemFlag.HIDE_STORED_ENCHANTS : ItemFlag.HIDE_ENCHANTS;
        boolean oculto = meta.hasItemFlag(flag);
        var visibles = new LinkedHashMap<Enchantment, Integer>();
        // Si el objeto ya ocultaba sus encantamientos (efectos Astral, gancho), solo se muestran los agregados.
        ench.forEach((e, l) -> { if (!(oculto && e.getKey().getNamespace().equals("astral"))) visibles.put(e, l); });
        var lineas = bloque(visibles);
        if (lineas.isEmpty()) return null;
        var lore = new ArrayList<Component>(lineas);
        if (meta.lore() != null) lore.addAll(meta.lore());
        meta.lore(lore);
        meta.addItemFlags(flag);
        pdc.set(MARCA, PersistentDataType.STRING, lineas.size() + ":" + (oculto ? 1 : 0));
        var copia = it.clone();
        copia.setItemMeta(meta);
        return copia;
    }

    /** Deshace decorar (lo que vuelve del cliente en creativo); null si no estaba decorado. */
    public ItemStack limpiar(ItemStack it) {
        if (it == null || it.getType().isAir() || !it.hasItemMeta()) return null;
        ItemMeta meta = it.getItemMeta();
        var pdc = meta.getPersistentDataContainer();
        String m = pdc.get(MARCA, PersistentDataType.STRING);
        if (m == null) return null;
        String[] p = m.split(":");
        int n = Integer.parseInt(p[0]);
        boolean oculto = p.length > 1 && p[1].equals("1");
        var lore = meta.lore() == null ? new ArrayList<Component>() : new ArrayList<>(meta.lore());
        for (int i = 0; i < n && !lore.isEmpty(); i++) lore.remove(0);
        meta.lore(lore.isEmpty() ? null : lore);
        if (!oculto) meta.removeItemFlags(meta instanceof EnchantmentStorageMeta ? ItemFlag.HIDE_STORED_ENCHANTS : ItemFlag.HIDE_ENCHANTS);
        pdc.remove(MARCA);
        var copia = it.clone();
        copia.setItemMeta(meta);
        return copia;
    }

    /** Lore decorado en texto plano (pruebas). */
    public List<String> bloqueTexto(ItemStack it) {
        var d = decorar(it);
        if (d == null) return List.of();
        var out = new ArrayList<String>();
        for (Component c : d.getItemMeta().lore()) out.add(PlainTextComponentSerializer.plainText().serialize(c));
        return out;
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
            meta.displayName(nombre(o.ench(), o.nivel()));
            meta.getPersistentDataContainer().set(ICONO, PersistentDataType.BYTE, (byte) 1);
            boolean alcanza = tengo >= o.puntos();
            var lore = new ArrayList<Component>();
            lore.add(Component.text(o.ench().getKey().getNamespace().equals("minecraft") ? "Encantamiento normal" : "Encantamiento especial", NamedTextColor.DARK_GRAY));
            lore.add(calidad(o.ench()));
            lore.addAll(lineasDesc(textoDe(o.ench(), o.nivel()), 34));
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
            p.sendMessage(Component.text("Encantaste con ", NamedTextColor.GREEN).append(nombre(o.ench(), o.nivel()))
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

/** Paquetes (PacketEvents): agrega la lista al mostrar objetos y la saca de lo que vuelve en creativo.
 *  Clase aparte para que AstralMesa cargue igual sin packetevents. */
final class AstralMesaPaquetes implements com.github.retrooper.packetevents.event.PacketListener {
    final AstralMesa mesa;
    AstralMesaPaquetes(AstralMesa mesa) { this.mesa = mesa; }

    static Object registrar(AstralMesa m) {
        return com.github.retrooper.packetevents.PacketEvents.getAPI().getEventManager().registerListener(
            new AstralMesaPaquetes(m), com.github.retrooper.packetevents.event.PacketListenerPriority.NORMAL);
    }
    static void quitar(Object l) {
        com.github.retrooper.packetevents.PacketEvents.getAPI().getEventManager().unregisterListener((com.github.retrooper.packetevents.event.PacketListenerCommon) l);
    }

    com.github.retrooper.packetevents.protocol.item.ItemStack pasar(com.github.retrooper.packetevents.protocol.item.ItemStack pe, boolean decorar) {
        if (pe == null || pe.isEmpty()) return null;
        try {
            var b = io.github.retrooper.packetevents.util.SpigotConversionUtil.toBukkitItemStack(pe);
            var r = decorar ? mesa.decorar(b) : mesa.limpiar(b);
            return r == null ? null : io.github.retrooper.packetevents.util.SpigotConversionUtil.fromBukkitItemStack(r);
        } catch (Throwable t) { return null; }
    }

    @Override public void onPacketSend(com.github.retrooper.packetevents.event.PacketSendEvent e) {
        var t = e.getPacketType();
        if (t == com.github.retrooper.packetevents.protocol.packettype.PacketType.Play.Server.SET_SLOT) {
            var w = new com.github.retrooper.packetevents.wrapper.play.server.WrapperPlayServerSetSlot(e);
            var n = pasar(w.getItem(), true);
            if (n != null) { w.setItem(n); e.markForReEncode(true); }
        } else if (t == com.github.retrooper.packetevents.protocol.packettype.PacketType.Play.Server.WINDOW_ITEMS) {
            var w = new com.github.retrooper.packetevents.wrapper.play.server.WrapperPlayServerWindowItems(e);
            var items = new ArrayList<>(w.getItems());
            boolean cambio = false;
            for (int i = 0; i < items.size(); i++) {
                var n = pasar(items.get(i), true);
                if (n != null) { items.set(i, n); cambio = true; }
            }
            var carried = w.getCarriedItem();
            if (carried.isPresent()) {
                var n = pasar(carried.get(), true);
                if (n != null) { w.setCarriedItem(n); cambio = true; }
            }
            if (cambio) { w.setItems(items); e.markForReEncode(true); }
        } else if (t == com.github.retrooper.packetevents.protocol.packettype.PacketType.Play.Server.SET_CURSOR_ITEM) {
            var w = new com.github.retrooper.packetevents.wrapper.play.server.WrapperPlayServerSetCursorItem(e);
            var n = pasar(w.getStack(), true);
            if (n != null) { w.setStack(n); e.markForReEncode(true); }
        } else if (t == com.github.retrooper.packetevents.protocol.packettype.PacketType.Play.Server.SET_PLAYER_INVENTORY) {
            var w = new com.github.retrooper.packetevents.wrapper.play.server.WrapperPlayServerSetPlayerInventory(e);
            var n = pasar(w.getStack(), true);
            if (n != null) { w.setStack(n); e.markForReEncode(true); }
        }
    }

    @Override public void onPacketReceive(com.github.retrooper.packetevents.event.PacketReceiveEvent e) {
        if (e.getPacketType() == com.github.retrooper.packetevents.protocol.packettype.PacketType.Play.Client.CREATIVE_INVENTORY_ACTION) {
            var w = new com.github.retrooper.packetevents.wrapper.play.client.WrapperPlayClientCreativeInventoryAction(e);
            var n = pasar(w.getItemStack(), false);
            if (n != null) { w.setItemStack(n); e.markForReEncode(true); }
        }
    }
}
