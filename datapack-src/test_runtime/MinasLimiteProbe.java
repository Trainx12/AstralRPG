package astraltest;

import java.util.*;
import java.lang.reflect.Method;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.event.entity.EntityPickupItemEvent;
import org.bukkit.event.entity.ItemSpawnEvent;
import org.bukkit.event.Listener;
import org.bukkit.event.EventHandler;
import org.bukkit.plugin.java.JavaPlugin;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.*;
import com.mojang.authlib.GameProfile;

/** Local only. Real Paper inventories and Skript functions, simulated NMS players. */
public final class MinasLimiteProbe extends JavaPlugin implements Listener {
    Object limit; Class<?> type; int failures, checks;
    List<ItemStack> spawned = new ArrayList<>();
    @EventHandler public void spawn(ItemSpawnEvent e) { spawned.add(e.getEntity().getItemStack().clone()); }
    void check(boolean ok, String label) { checks++; if (!ok) failures++; getLogger().info("MLTEST " + (ok ? "PASS " : "FAIL ") + label); }
    Object call(String name, Class<?>[] types, Object... args) throws Exception {
        Method m = type.getDeclaredMethod(name, types); m.setAccessible(true); return m.invoke(limit, args);
    }
    boolean marked(ItemStack i) throws Exception { return (boolean)call("marked", new Class[]{ItemStack.class}, i); }
    ItemStack mark(ItemStack i) throws Exception { return (ItemStack)call("mark", new Class[]{ItemStack.class}, i); }
    void clean(Player p) throws Exception { call("cleanOutside", new Class[]{Player.class}, p); }
    World world(String name) {
        World w = Bukkit.getWorld(name);
        return w != null ? w : Bukkit.createWorld(new WorldCreator(name).type(WorldType.FLAT)
            .generatorSettings("{\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:the_void\"}").generateStructures(false));
    }
    Player fake(String name) throws Exception {
        var server = ((CraftServer)Bukkit.getServer()).getServer();
        var w = ((CraftWorld)world("astral_minas")).getHandle();
        var profile = new GameProfile(UUID.randomUUID(), name);
        var f = new ServerPlayer(server, w, profile, ClientInformation.createDefault());
        var c = new Connection(PacketFlow.SERVERBOUND);
        c.channel = new io.netty.channel.embedded.EmbeddedChannel(); c.channel.pipeline().addLast("packet_handler", c);
        c.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        f.connection = new ServerGamePacketListenerImpl(server, c, f, CommonListenerCookie.createInitial(profile, false));
        f.setPos(83, 74, 80); w.addNewPlayer(f);
        var list = server.getPlayerList(); list.players.add(f);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var field = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); field.setAccessible(true);
            ((Map)field.get(list)).put(key.equals("playersByUUID") ? profile.id() : name.toLowerCase(Locale.ROOT), f);
        }
        Player p = f.getBukkitEntity(); p.setInvulnerable(true); p.setGravity(false); p.setGameMode(GameMode.SURVIVAL);
        Bukkit.getScheduler().runTaskTimer(this, () -> ((io.netty.channel.embedded.EmbeddedChannel)c.channel).releaseOutbound(), 1, 1);
        return p;
    }
    void script(Player p, String op) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mlscript " + p.getName() + " " + op); }
    @Override public void onEnable() {
        Bukkit.getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            try { run(); } catch (Throwable t) { failures++; t.printStackTrace(); }
            getLogger().info("MLTEST RESULT checks=" + checks + " failures=" + failures);
            Bukkit.shutdown();
        }, 100L);
    }
    void run() throws Exception {
        limit = Bukkit.getPluginManager().getPlugin("AstralMinasLimite"); type = limit.getClass();
        Player p = fake("ByTrainx"), other = fake("MinasOtro");
        check(!(boolean)call("active", new Class[]{Player.class}, other), "privado por defecto");
        script(p, "give"); script(p, "give");
        ItemStack first = p.getInventory().getItem(0);
        check(first != null && first.getAmount() == 32 && marked(first), "am_give marca y apila dos lotes");
        check(!first.getItemMeta().hasDisplayName() && !first.getItemMeta().hasLore() && !first.getItemMeta().hasCustomModelData(), "marca invisible sin nombre lore ni modelo");
        check(marked(ItemStack.deserializeBytes(first.serializeAsBytes())), "marca persiste serializada");
        p.getInventory().addItem(new ItemStack(Material.DIAMOND, 3));
        script(p, "sale");
        check(!p.getInventory().contains(Material.DIAMOND), "Venta rapida acepta marcados y no marcados");
        script(other, "give");
        check(!marked(other.getInventory().getItem(0)), "otro jugador privado recibe mineral sin marca");
        other.teleport(new Location(world("lobby"), 0, 80, 0));
        check(other.getInventory().contains(Material.DIAMOND), "privado conserva sus minerales al salir");
        // Exercise real mining handler, including normal Bukkit drop calculation.
        p.getInventory().setItemInMainHand(new ItemStack(Material.DIAMOND_PICKAXE));
        var block = p.getWorld().getBlockAt(82, 73, 78); block.setType(Material.STONE);
        var breakEvent = new BlockBreakEvent(block, p); Bukkit.getPluginManager().callEvent(breakEvent);
        ItemStack cobble = Arrays.stream(p.getInventory().getContents()).filter(i -> i != null && i.getType() == Material.COBBLESTONE).findFirst().orElse(null);
        check(!breakEvent.isCancelled() && marked(cobble), "picar piedra usa am_give marcado");
        p.getInventory().clear();
        ItemStack goods = mark(new ItemStack(Material.DIAMOND, 8));
        p.getInventory().setItem(0, goods); p.getInventory().setItem(1, new ItemStack(Material.DIAMOND, 7));
        p.getEnderChest().setItem(0, goods); p.getInventory().setItemInOffHand(goods);
        p.getInventory().setHelmet(goods); p.setItemOnCursor(goods);
        p.getOpenInventory().getTopInventory().setItem(1, goods);
        p.teleport(new Location(world("lobby"), 0, 80, 0));
        check(p.getInventory().getItem(0) == null && p.getInventory().getItem(1).getAmount() == 7, "salida borra solo procedencia minas");
        check(!marked(p.getInventory().getItemInOffHand()) && !marked(p.getInventory().getHelmet()), "salida limpia secundaria y armadura");
        check(!marked(p.getItemOnCursor()) && !marked(p.getOpenInventory().getTopInventory().getItem(1)), "salida limpia cursor y grilla");
        check(p.getEnderChest().isEmpty(), "salida limpia Ender");
        p.getInventory().setItem(2, goods); clean(p);
        check(p.getInventory().getItem(2) == null, "red de seguridad fuera");
        p.teleport(new Location(world("astral_minas"), 83, 74, 80));
        p.getInventory().clear(); p.getInventory().setItem(0, goods);
        var chest = Bukkit.createInventory(null, 27); p.openInventory(chest);
        // Chest raw slots: 27..53 are main inventory 9..35; hotbar 0 starts at 54.
        var click = new InventoryClickEvent(p.getOpenInventory(), InventoryType.SlotType.CONTAINER, 54, ClickType.SHIFT_LEFT, InventoryAction.MOVE_TO_OTHER_INVENTORY);
        Bukkit.getPluginManager().callEvent(click); check(click.isCancelled(), "shift click contenedor bloqueado");
        p.setItemOnCursor(goods);
        click = new InventoryClickEvent(p.getOpenInventory(), InventoryType.SlotType.CONTAINER, 0, ClickType.LEFT, InventoryAction.PLACE_ALL);
        Bukkit.getPluginManager().callEvent(click); check(click.isCancelled(), "cursor contenedor bloqueado");
        click = new InventoryClickEvent(p.getOpenInventory(), InventoryType.SlotType.CONTAINER, 0, ClickType.NUMBER_KEY, InventoryAction.HOTBAR_SWAP, 0);
        Bukkit.getPluginManager().callEvent(click); check(click.isCancelled(), "tecla numero bloqueada");
        var drag = new InventoryDragEvent(p.getOpenInventory(), goods, goods, false, Map.of(0, goods));
        Bukkit.getPluginManager().callEvent(drag); check(drag.isCancelled(), "arrastre bloqueado");
        for (String cmd : List.of("trade MinasOtro", "axtrade:trade MinasOtro", "ah sell 1", "bazar", "sell hand")) {
            var e = new PlayerCommandPreprocessEvent(p, "/" + cmd); Bukkit.getPluginManager().callEvent(e);
            check(e.isCancelled(), "comercio bloqueado " + cmd);
        }
        var e = new PlayerCommandPreprocessEvent(p, "/minas"); Bukkit.getPluginManager().callEvent(e);
        check(!e.isCancelled(), "viajes no bloqueados");
        p.closeInventory(); p.setItemOnCursor(null);
        click = new InventoryClickEvent(p.getOpenInventory(), InventoryType.SlotType.QUICKBAR, 36, ClickType.SHIFT_LEFT, InventoryAction.MOVE_TO_OTHER_INVENTORY);
        Bukkit.getPluginManager().callEvent(click); check(!click.isCancelled(), "shift personal entre barra e inventario permitido");
        // A marked stack cannot be transformed in the personal crafting grid.
        p.setItemOnCursor(goods);
        click = new InventoryClickEvent(p.getOpenInventory(), InventoryType.SlotType.CRAFTING, 1, ClickType.LEFT, InventoryAction.PLACE_ALL);
        Bukkit.getPluginManager().callEvent(click); check(click.isCancelled(), "crafteo bloqueado");
        p.setItemOnCursor(null);
        Item dropped = p.getWorld().dropItem(p.getLocation(), goods);
        var pickup = new EntityPickupItemEvent(other, dropped, 0); Bukkit.getPluginManager().callEvent(pickup);
        check(pickup.isCancelled() && !dropped.isDead(), "privado impide transferir marca a otro jugador");
        var hopper = new InventoryPickupItemEvent(Bukkit.createInventory(null, InventoryType.HOPPER), dropped);
        Bukkit.getPluginManager().callEvent(hopper); check(hopper.isCancelled(), "tolva no recoge marcados");
        p.teleport(new Location(world("lobby"), 0, 80, 0));
        Item outside = p.getWorld().dropItem(p.getLocation(), goods);
        pickup = new EntityPickupItemEvent(p, outside, 0); Bukkit.getPluginManager().callEvent(pickup);
        check(pickup.isCancelled() && outside.isDead(), "recogida fuera borra marcados");
        p.teleport(new Location(world("astral_minas"), 83, 74, 80));
        for (int s = 0; s < 36; s++) p.getInventory().setItem(s, new ItemStack(Material.STONE, 64));
        spawned.clear();
        script(p, "give");
        check(spawned.stream().anyMatch(i -> {
            try { return marked(i) && i.getAmount() == 16; } catch (Exception ex) { throw new RuntimeException(ex); }
        }), "inventario lleno deja sobrantes marcados");
        ItemStack almost = goods.clone(); almost.setAmount(60); p.getInventory().setItem(0, almost);
        spawned.clear(); script(p, "give");
        check(p.getInventory().getItem(0).getAmount() == 60 && spawned.stream().anyMatch(i -> i.getAmount() == 16),
            "poco espacio conserva entrega completa al piso anterior");
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "minaslimite publico");
        check((boolean)call("active", new Class[]{Player.class}, other), "publico activa otros jugadores");
        check(org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.File(((JavaPlugin)limit).getDataFolder(), "config.yml")).getBoolean("publico"), "interruptor persistente en disco");
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "minaslimite privado");
        p.getInventory().clear(); other.getInventory().clear();
    }
}
