package astral;

import ch.njol.skript.Skript;
import ch.njol.skript.lang.*;
import ch.njol.util.Kleenean;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import java.util.*;

/** Only am_give creates provenance. Never infer it from material or world drops. */
public final class AstralMinasLimite extends JavaPlugin implements Listener {
    static AstralMinasLimite instance;
    static final NamespacedKey KEY = new NamespacedKey("astral", "minas_origen");
    static final String WARNING = "§cNingún mineral de las Minas Astrales puede usarse en otros mundos. Lo que no vendiste desapareció.";
    static final String BLOCKED = "§cVendé o tirá los minerales de las minas antes de guardarlos o intercambiarlos.";
    boolean publico;

    @SuppressWarnings("removal")
    @Override public void onEnable() {
        instance = this;
        getConfig().addDefault("publico", false);
        getConfig().options().copyDefaults(true);
        saveConfig();
        publico = getConfig().getBoolean("publico", false);
        Skript.registerEffect(Give.class, "astral mine give %itemstack% to %player%");
        getServer().getPluginManager().registerEvents(this, this);
        getServer().getScheduler().runTaskTimer(this, () -> {
            for (Player p : Bukkit.getOnlinePlayers()) cleanOutside(p);
        }, 100L, 100L);
    }
    boolean active(Player p) { return publico || p.getName().equalsIgnoreCase("ByTrainx"); }
    static boolean mines(Player p) { return p.getWorld().getName().equals("astral_minas"); }
    static boolean marked(ItemStack i) {
        return i != null && i.hasItemMeta() && i.getItemMeta().getPersistentDataContainer().has(KEY, PersistentDataType.BYTE);
    }
    static ItemStack mark(ItemStack original) {
        ItemStack i = original.clone();
        i.editMeta(m -> m.getPersistentDataContainer().set(KEY, PersistentDataType.BYTE, (byte)1));
        return i;
    }
    static boolean fits(PlayerInventory inventory, ItemStack item) {
        int remaining = item.getAmount();
        int max = Math.min(inventory.getMaxStackSize(), item.getMaxStackSize());
        for (ItemStack slot : inventory.getStorageContents()) {
            if (slot == null || slot.getType().isAir()) remaining -= max;
            else if (slot.isSimilar(item)) remaining -= Math.max(0, max - slot.getAmount());
            if (remaining <= 0) return true;
        }
        return false;
    }
    public static class Give extends ch.njol.skript.lang.Effect {
        Expression<ItemStack> item;
        Expression<Player> player;
        @SuppressWarnings("unchecked") public boolean init(Expression<?>[] e, int m, Kleenean d, SkriptParser.ParseResult r) {
            item = (Expression<ItemStack>) e[0]; player = (Expression<Player>) e[1]; return true;
        }
        protected void execute(Event e) {
            Player p = player.getSingle(e); ItemStack i = item.getSingle(e);
            if (p == null || i == null) return;
            ItemStack drop = instance.active(p) && mines(p) ? mark(i) : i.clone();
            // Keep Skript's previous all-or-drop behavior for every player.
            if (!fits(p.getInventory(), drop)) {
                p.getWorld().dropItem(p.getLocation(), drop);
                return;
            }
            for (ItemStack rest : p.getInventory().addItem(drop).values())
                p.getWorld().dropItem(p.getLocation(), rest);
        }
        public String toString(Event e, boolean debug) { return "astral mine give"; }
    }
    boolean carries(Player p) {
        for (ItemStack i : p.getInventory().getContents()) if (marked(i)) return true;
        return marked(p.getItemOnCursor());
    }
    int clear(Inventory inv) {
        int n = 0;
        for (int s = 0; s < inv.getSize(); s++) {
            ItemStack i = inv.getItem(s);
            if (marked(i)) { n += i.getAmount(); inv.setItem(s, null); }
        }
        return n;
    }
    void cleanOutside(Player p) {
        if (!active(p) || mines(p)) return;
        int n = clear(p.getInventory()) + clear(p.getEnderChest());
        if (marked(p.getItemOnCursor())) { n += p.getItemOnCursor().getAmount(); p.setItemOnCursor(null); }
        Inventory top = p.getOpenInventory().getTopInventory();
        if (top.getType() == InventoryType.CRAFTING || top.getType() == InventoryType.WORKBENCH) n += clear(top);
        if (n > 0) p.sendMessage(WARNING + " §7(" + n + " objetos)");
    }
    void later(Player p) { Bukkit.getScheduler().runTask(this, () -> { if (p.isOnline()) cleanOutside(p); }); }
    void entry(Player p) {
        if (active(p) && mines(p)) p.sendMessage("§eVendé tus minerales antes de irte: no salen de las Minas Astrales.");
        else cleanOutside(p);
    }
    @EventHandler public void world(PlayerChangedWorldEvent e) { entry(e.getPlayer()); }
    @EventHandler public void join(PlayerJoinEvent e) { later(e.getPlayer()); entry(e.getPlayer()); }
    @EventHandler public void respawn(PlayerRespawnEvent e) { later(e.getPlayer()); }
    @EventHandler public void quit(PlayerQuitEvent e) { cleanOutside(e.getPlayer()); }
    @EventHandler public void open(InventoryOpenEvent e) { if (e.getPlayer() instanceof Player p) later(p); }
    @EventHandler public void close(InventoryCloseEvent e) { if (e.getPlayer() instanceof Player p) later(p); }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void pickup(EntityPickupItemEvent e) {
        if (!(e.getEntity() instanceof Player p) || !marked(e.getItem().getItemStack())) return;
        // A private tester cannot pass marked drops to an unaffected player.
        if (!active(p)) { e.setCancelled(true); return; }
        if (!mines(p)) { e.setCancelled(true); e.getItem().remove(); p.sendMessage(WARNING); cleanOutside(p); }
    }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void hopper(InventoryPickupItemEvent e) { if (marked(e.getItem().getItemStack())) e.setCancelled(true); }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void move(InventoryMoveItemEvent e) { if (marked(e.getItem())) e.setCancelled(true); }
    boolean forbidden(InventoryClickEvent e) {
        Inventory top = e.getView().getTopInventory();
        boolean playerGrid = top.getType() == InventoryType.CRAFTING;
        ItemStack number = e.getHotbarButton() >= 0 ? e.getWhoClicked().getInventory().getItem(e.getHotbarButton()) : null;
        ItemStack off = e.getWhoClicked().getInventory().getItemInOffHand();
        boolean source = marked(e.getCurrentItem()) || marked(e.getCursor()) || marked(number)
            || (e.getClick() == ClickType.SWAP_OFFHAND && marked(off));
        if (!source) return false;
        // Marked goods may move within personal storage and be dropped, but never
        // enter any external GUI (including previously opened trades) or craft grid.
        if (playerGrid) return e.getRawSlot() >= 0 && e.getRawSlot() < top.getSize();
        return true;
    }
    // Cancel before trading/backpack plugins can implement their own transfer.
    @EventHandler(priority=EventPriority.LOWEST, ignoreCancelled=true)
    public void clickBeforePlugins(InventoryClickEvent e) {
        if (forbidden(e)) { e.setCancelled(true); e.getWhoClicked().sendMessage(BLOCKED); }
    }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void click(InventoryClickEvent e) {
        if (!(e.getWhoClicked() instanceof Player p)) return;
        if (forbidden(e)) { e.setCancelled(true); p.sendMessage(BLOCKED); }
        later(p);
    }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void drag(InventoryDragEvent e) {
        if (!marked(e.getOldCursor())) return;
        int top = e.getView().getTopInventory().getSize();
        if (e.getRawSlots().stream().anyMatch(s -> s < top)) { e.setCancelled(true); e.getWhoClicked().sendMessage(BLOCKED); }
    }
    @EventHandler(priority=EventPriority.LOWEST, ignoreCancelled=true)
    public void dragBeforePlugins(InventoryDragEvent e) { drag(e); }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void death(PlayerDeathEvent e) {
        // Graves plugins must never capture marked drops. keepInventory stays intact
        // and is cleaned on respawn/world change if the player leaves the mines.
        e.getDrops().removeIf(AstralMinasLimite::marked);
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void deathBeforeGrave(PlayerDeathEvent e) { e.getDrops().removeIf(AstralMinasLimite::marked); }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void interact(PlayerInteractEvent e) { if (marked(e.getItem())) e.setCancelled(true); }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void entity(PlayerInteractEntityEvent e) {
        if (marked(e.getPlayer().getInventory().getItem(e.getHand()))) e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void command(PlayerCommandPreprocessEvent e) {
        Player p = e.getPlayer();
        if (!carries(p)) return;
        String root = e.getMessage().substring(1).split("\\s+", 2)[0].toLowerCase(Locale.ROOT);
        root = root.substring(root.lastIndexOf(':') + 1);
        Set<String> blocked = Set.of("trade", "axtrade", "ah", "auction", "auctions", "crazyauctions", "ca", "subastas", "bazar", "bazaar", "sell", "sellall", "sellgui", "shop", "market", "royalbazaar", "ezauction");
        Command resolved = Bukkit.getCommandMap().getCommand(root);
        if (blocked.contains(root) || resolved != null && blocked.contains(resolved.getName().toLowerCase(Locale.ROOT))) {
            e.setCancelled(true); p.sendMessage(BLOCKED);
        }
    }
    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("astral.minas.admin")) return true;
        if (args.length != 1 || !Set.of("publico", "privado").contains(args[0].toLowerCase(Locale.ROOT))) {
            sender.sendMessage("§e/minaslimite publico | privado. Actual: " + (publico ? "publico" : "privado")); return true;
        }
        publico = args[0].equalsIgnoreCase("publico");
        getConfig().set("publico", publico); saveConfig();
        sender.sendMessage("§aLímite de minerales: " + (publico ? "público" : "privado (ByTrainx)"));
        return true;
    }
}
