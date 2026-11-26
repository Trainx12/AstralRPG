package astral;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.block.ShulkerBox;
import org.bukkit.block.data.Directional;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerChangedWorldEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerTeleportEvent;
import org.bukkit.generator.ChunkGenerator;
import org.bukkit.inventory.ItemStack;
import org.bukkit.loot.LootContext;
import org.bukkit.loot.LootTable;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Herramientas del dueno (23/11/2026, datapack-src/dueno.py). Solo para las UUID de config.yml (duenos).
 *
 * /modo [admin|jugador]: la misma cuenta con dos perfiles separados. Cada perfil guarda inventario, armadura,
 *   mano izquierda, cofre de ender, experiencia, vida, comida, modo de juego y lugar. Admin = OP + creativo;
 *   jugador = sin OP + supervivencia (para probar como cualquiera). Los niveles de AuraSkills y la plata son de
 *   la cuenta: no se separan.
 * /sala: mundo privado "sala_dueno" (vacio, sin mobs) con una habitacion y shulkers con todos los items del
 *   datapack (astral:item/*). /sala rellenar vuelve a llenarlos. Nadie mas puede entrar: si alguien aparece ahi,
 *   vuelve al spawn del lobby.
 */
public final class AstralDueno extends JavaPlugin implements Listener {
    static final String MUNDO = "sala_dueno";
    private final Set<UUID> duenos = new HashSet<>();
    private final List<String> items = new ArrayList<>();

    @Override
    public void onEnable() {
        saveDefaultConfig();
        for (String s : getConfig().getStringList("duenos")) duenos.add(UUID.fromString(s));
        try (var r = new InputStreamReader(Objects.requireNonNull(getResource("items.txt")), StandardCharsets.UTF_8)) {
            new java.io.BufferedReader(r).lines().map(String::trim).filter(x -> !x.isEmpty()).forEach(items::add);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
        getServer().getPluginManager().registerEvents(this, this);
        // El mundo se carga solo si ya existe (lo crea el primer /sala).
        if (new File(Bukkit.getWorldContainer(), MUNDO).isDirectory()) Bukkit.getScheduler().runTask(this, this::mundo);
    }

    private boolean dueno(CommandSender s) {
        return s instanceof Player p && duenos.contains(p.getUniqueId());
    }

    // ------------------------------------------------------------------------------------------ /modo
    private File perfil(Player p, String modo) {
        File dir = new File(getDataFolder(), "perfiles");
        dir.mkdirs();
        return new File(dir, p.getUniqueId() + "-" + modo + ".yml");
    }

    private String modoActual(Player p) {
        return getConfig().getString("modo." + p.getUniqueId(), "admin");
    }

    private void guardar(Player p, String modo) throws IOException {
        YamlConfiguration y = new YamlConfiguration();
        y.set("inventario", Arrays.asList(p.getInventory().getContents()));
        y.set("ender", Arrays.asList(p.getEnderChest().getContents()));
        y.set("nivel", p.getLevel());
        y.set("exp", (double) p.getExp());
        y.set("vida", p.getHealth());
        y.set("comida", p.getFoodLevel());
        y.set("modo_juego", p.getGameMode().name());
        y.set("lugar", p.getLocation());
        y.save(perfil(p, modo));
    }

    @SuppressWarnings("unchecked")
    private void cargar(Player p, String modo) {
        File f = perfil(p, modo);
        p.getInventory().clear();
        p.getEnderChest().clear();
        if (!f.isFile()) {
            // Perfil nuevo: vacio, en el spawn del lobby.
            p.setLevel(0); p.setExp(0);
            p.setGameMode(modo.equals("admin") ? GameMode.CREATIVE : GameMode.SURVIVAL);
            World lobby = Bukkit.getWorld(getConfig().getString("mundo_inicio", "lobby"));
            if (lobby != null) p.teleport(lobby.getSpawnLocation());
            return;
        }
        YamlConfiguration y = YamlConfiguration.loadConfiguration(f);
        List<ItemStack> inv = (List<ItemStack>) y.getList("inventario", List.of());
        p.getInventory().setContents(inv.toArray(new ItemStack[0]));
        List<ItemStack> ender = (List<ItemStack>) y.getList("ender", List.of());
        p.getEnderChest().setContents(ender.toArray(new ItemStack[0]));
        p.setLevel(y.getInt("nivel"));
        p.setExp((float) y.getDouble("exp"));
        p.setGameMode(GameMode.valueOf(y.getString("modo_juego", "SURVIVAL")));
        var max = p.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH);
        p.setHealth(Math.max(1, Math.min(max == null ? 20 : max.getValue(), y.getDouble("vida", 20))));
        p.setFoodLevel(y.getInt("comida", 20));
        Location l = y.getLocation("lugar");
        if (l != null && l.getWorld() != null) p.teleport(l);
    }

    private void aplicarPermisos(Player p, String modo) {
        p.setOp(modo.equals("admin"));
        if (modo.equals("jugador") && p.getGameMode() == GameMode.CREATIVE) p.setGameMode(GameMode.SURVIVAL);
    }

    private void cambiar(Player p, String modo) {
        String antes = modoActual(p);
        if (antes.equals(modo)) { p.sendMessage("§eYa estas en modo " + modo + "."); return; }
        try {
            guardar(p, antes);
        } catch (IOException e) {
            p.sendMessage("§cNo pude guardar tu perfil " + antes + ": no cambio nada.");
            getLogger().warning(e.toString());
            return;
        }
        getConfig().set("modo." + p.getUniqueId(), modo);
        saveConfig();
        cargar(p, modo);
        aplicarPermisos(p, modo);
        p.sendMessage(modo.equals("admin")
                ? "§6Modo ADMIN: OP y tu inventario de admin. §7(/modo jugador para volver a jugar)"
                : "§aModo JUGADOR: sin OP, tu inventario de jugador. §7(/modo admin para volver)");
        p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_CHIME, 1f, modo.equals("admin") ? .8f : 1.4f);
    }

    @EventHandler
    public void alEntrar(PlayerJoinEvent e) {
        Player p = e.getPlayer();
        if (duenos.contains(p.getUniqueId())) aplicarPermisos(p, modoActual(p));
        else if (p.getWorld().getName().equals(MUNDO)) echar(p);
    }

    // ------------------------------------------------------------------------------------------ /sala
    private World mundo() {
        World w = Bukkit.getWorld(MUNDO);
        if (w != null) return w;
        w = new WorldCreator(MUNDO).generator(new Vacio()).environment(World.Environment.NORMAL)
                .generateStructures(false).createWorld();
        if (w == null) return null;
        w.setSpawnFlags(false, false);
        w.setGameRule(GameRules.ADVANCE_TIME, false);
        w.setGameRule(GameRules.ADVANCE_WEATHER, false);
        w.setGameRule(GameRules.SPAWN_MOBS, false);
        w.setTime(6000);
        w.setSpawnLocation(0, 65, -6);
        return w;
    }

    static final class Vacio extends ChunkGenerator { }

    /** Habitacion 25x9x25 de cuarzo con luz, y shulkers en las paredes con todos los items. */
    private void armar(World w) {
        int r = 12, piso = 63, alto = 9;
        for (int x = -r; x <= r; x++)
            for (int z = -r; z <= r; z++)
                for (int y = piso; y <= piso + alto; y++) {
                    boolean borde = Math.abs(x) == r || Math.abs(z) == r || y == piso || y == piso + alto;
                    Block b = w.getBlockAt(x, y, z);
                    if (borde) b.setType((y == piso + alto && (x + z) % 4 == 0) ? Material.SEA_LANTERN
                            : y == piso ? Material.POLISHED_DEEPSLATE : Material.QUARTZ_BLOCK, false);
                    else if (b.getType() != Material.AIR && !(b.getState() instanceof ShulkerBox)) b.setType(Material.AIR, false);
                }
        rellenar(w);
    }

    /** Los items en grupos por familia (espada_, mago_, baston_...): 27 por shulker, en las paredes. */
    private int rellenar(World w) {
        List<Block> lugares = new ArrayList<>();
        int r = 12, piso = 63;
        for (int y = piso + 1; y <= piso + 4; y++)
            for (int i = -r + 1; i <= r - 1; i++) {
                lugares.add(w.getBlockAt(i, y, -r + 1));
                lugares.add(w.getBlockAt(i, y, r - 1));
                lugares.add(w.getBlockAt(-r + 1, y, i));
                lugares.add(w.getBlockAt(r - 1, y, i));
            }
        for (Block b : lugares) b.setType(Material.AIR, false);
        Map<String, List<ItemStack>> grupos = new TreeMap<>();
        LootContext ctx = new LootContext.Builder(w.getSpawnLocation()).build();
        Random rnd = new Random(1);
        for (String id : items) {
            LootTable lt = Bukkit.getLootTable(new NamespacedKey("astral", "item/" + id));
            if (lt == null) continue;
            Collection<ItemStack> out;
            try { out = lt.populateLoot(rnd, ctx); } catch (Exception ex) { continue; }
            String g = id.contains("_") ? id.substring(0, id.indexOf('_')) : id;
            grupos.computeIfAbsent(g, k -> new ArrayList<>()).addAll(out);
        }
        Material[] colores = {Material.PURPLE_SHULKER_BOX, Material.LIGHT_BLUE_SHULKER_BOX, Material.ORANGE_SHULKER_BOX,
                Material.LIME_SHULKER_BOX, Material.PINK_SHULKER_BOX, Material.YELLOW_SHULKER_BOX, Material.CYAN_SHULKER_BOX,
                Material.RED_SHULKER_BOX};
        int n = 0, c = 0;
        Iterator<Block> it = lugares.iterator();
        for (var g : grupos.entrySet()) {
            List<ItemStack> lista = g.getValue();
            for (int i = 0; i < lista.size(); i += 27) {
                if (!it.hasNext()) { getLogger().warning("No entran todos los shulkers en la sala"); return n; }
                Block b = it.next();
                b.setType(colores[c % colores.length], false);
                if (b.getBlockData() instanceof Directional d) { d.setFacing(BlockFace.UP); b.setBlockData(d, false); }
                ShulkerBox box = (ShulkerBox) b.getState();
                box.customName(net.kyori.adventure.text.Component.text(g.getKey() + (i > 0 ? " " + (i / 27 + 1) : "")));
                box.update(true, false);
                box = (ShulkerBox) b.getState();
                box.getInventory().setContents(lista.subList(i, Math.min(lista.size(), i + 27)).toArray(new ItemStack[0]));
                n++;
            }
            c++;
        }
        return n;
    }

    private void echar(Player p) {
        World lobby = Bukkit.getWorld(getConfig().getString("mundo_inicio", "lobby"));
        Location l = lobby != null ? lobby.getSpawnLocation() : Bukkit.getWorlds().get(0).getSpawnLocation();
        Bukkit.getScheduler().runTask(this, () -> p.teleport(l));
        p.sendMessage("§cEsa sala es privada.");
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void alTeleportar(PlayerTeleportEvent e) {
        if (e.getTo().getWorld() != null && e.getTo().getWorld().getName().equals(MUNDO)
                && !duenos.contains(e.getPlayer().getUniqueId())) {
            e.setCancelled(true);
            e.getPlayer().sendMessage("§cEsa sala es privada.");
        }
    }

    @EventHandler
    public void alCambiarMundo(PlayerChangedWorldEvent e) {
        if (e.getPlayer().getWorld().getName().equals(MUNDO) && !duenos.contains(e.getPlayer().getUniqueId())) echar(e.getPlayer());
    }

    // ------------------------------------------------------------------------------------------ comandos
    @Override
    public boolean onCommand(CommandSender s, Command cmd, String label, String[] a) {
        if (!dueno(s)) { s.sendMessage("§cEse comando es solo del dueno."); return true; }
        Player p = (Player) s;
        if (cmd.getName().equals("modo")) {
            String modo = a.length > 0 ? a[0].toLowerCase(Locale.ROOT) : (modoActual(p).equals("admin") ? "jugador" : "admin");
            if (!modo.equals("admin") && !modo.equals("jugador")) { p.sendMessage("§e/modo admin  o  /modo jugador"); return true; }
            cambiar(p, modo);
            return true;
        }
        World w = mundo();
        if (w == null) { p.sendMessage("§cNo se pudo crear la sala."); return true; }
        boolean nueva = w.getBlockAt(0, 63, 0).getType() == Material.AIR;
        if (nueva) armar(w);
        if (a.length > 0 && a[0].equalsIgnoreCase("rellenar")) {
            p.sendMessage("§aShulkers rellenados: " + rellenar(w));
            return true;
        }
        p.teleport(new Location(w, 0.5, 64, 0.5));
        p.sendMessage("§dTu sala privada." + (nueva ? " §7(recien armada; /sala rellenar vuelve a llenar los shulkers)" : ""));
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender s, Command cmd, String label, String[] a) {
        if (!dueno(s) || a.length != 1) return List.of();
        return cmd.getName().equals("modo") ? List.of("admin", "jugador") : List.of("rellenar");
    }
}
