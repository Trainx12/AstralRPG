package astraltest;

import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.block.BlockFace;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.ArrayList;
import java.util.List;

/** Ensayo de la revision del 23/11 (tools/probar_revision_23_11.py): invocaciones, guadana sin Cosecha,
 *  mobs de mazmorra rapidos/agresivos y AstralDueno (/modo, /sala). Imprime "R23 PASS/FAIL ..." y "R23 RESULT". */
public final class Revision23Probe extends JavaPlugin implements Listener {
    private final List<String> fallas = new ArrayList<>();
    private int pasos;

    @Override public void onEnable() { getServer().getPluginManager().registerEvents(this, this); }

    private void ok(boolean c, String s) {
        pasos++;
        getLogger().info("R23 " + (c ? "PASS " : "FAIL ") + s);
        if (!c) fallas.add(s);
    }

    private void cmd(String s) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), s); }

    private ItemStack item(Player p, String id) {
        p.getInventory().clear();
        cmd("loot give " + p.getName() + " loot astral:item/" + id);
        for (ItemStack it : p.getInventory().getContents())
            if (it != null && it.hasItemMeta() && it.getItemMeta().getPersistentDataContainer().getKeys().stream()
                    .anyMatch(k -> k.getKey().equals("clase_arma"))) return it;
        return null;
    }

    private void usar(Player p, ItemStack it) {
        p.getInventory().setItemInMainHand(it);
        Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(p, Action.RIGHT_CLICK_AIR, it, null, BlockFace.SELF, EquipmentSlot.HAND));
    }

    @EventHandler
    public void alEntrar(PlayerJoinEvent e) {
        Player p = e.getPlayer();
        Bukkit.getScheduler().runTaskLater(this, () -> paso1(p), 60);
    }

    private void paso1(Player p) {
        World w = new WorldCreator("bosque").type(WorldType.FLAT).generateStructures(false).createWorld();
        w.setSpawnFlags(false, false);
        w.setTime(6000);
        p.teleport(new Location(w, 0.5, -60, 0.5));
        p.setGameMode(GameMode.SURVIVAL);
        var max = p.getAttribute(Attribute.MAX_HEALTH);
        max.setBaseValue(2000); p.setHealth(2000);
        var u = AuraSkillsApi.get().getUser(p.getUniqueId());
        u.setSkillLevel(Skills.SORCERY, 60);
        u.setSkillLevel(Skills.FIGHTING, 60);
        Bukkit.getScheduler().runTaskLater(this, () -> paso2(p, w), 40);
    }

    private void paso2(Player p, World w) {
        AuraSkillsApi.get().getUser(p.getUniqueId()).setMana(100000);
        // 1) Mob de mazmorra: agresivo y mas rapido; en agua, eficiencia 1.
        Zombie z = w.spawn(new Location(w, 8, -60, 0), Zombie.class, x -> { x.setShouldBurnInDay(false); x.addScoreboardTag("astral.mt1"); });
        double base = z.getAttribute(Attribute.MOVEMENT_SPEED).getValue();
        // 2) Invocar con el libro I.
        ItemStack libro = item(p, "libro_invocador_1");
        ok(libro != null, "libro de invocador entregado");
        if (libro != null) usar(p, libro);
        Bukkit.getScheduler().runTaskLater(this, () -> paso3(p, w, z, base), 30);
    }

    private void paso3(Player p, World w, Zombie z, double base) {
        double ahora = z.getAttribute(Attribute.MOVEMENT_SPEED).getValue();
        ok(ahora > base * 1.09, "mob de mazmorra mas rapido " + base + " -> " + ahora);
        ok(z.getAttribute(Attribute.WATER_MOVEMENT_EFFICIENCY).getBaseValue() >= 1.0, "mob de mazmorra no se frena en el agua");
        ok(p.equals(z.getTarget()) || z.getTarget() != null, "mob de mazmorra con objetivo: " + z.getTarget());
        z.remove();
        List<LivingEntity> inv = new ArrayList<>();
        for (Entity e : w.getEntities()) if (e.getScoreboardTags().contains("astral.invocacion") && e instanceof LivingEntity le) inv.add(le);
        ok(!inv.isEmpty(), "aparecio la invocacion (" + inv.size() + ")");
        boolean cartel = false;
        for (TextDisplay td : w.getEntitiesByClass(TextDisplay.class))
            if (td.getScoreboardTags().contains("astral.invocacion.cartel")) {
                String s = net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(td.text());
                cartel = s.contains("Invocacion de " + p.getName()) && s.contains("Tier 1") && s.contains("❤");
                getLogger().info("R23 cartel: " + s.replace('\n', '|'));
            }
        ok(cartel, "cartel con duenio, tier y vida");
        if (inv.isEmpty()) { fin(p); return; }
        LivingEntity yo = inv.get(0);
        Husk h = w.spawn(yo.getLocation().add(2, 0, 0), Husk.class, x -> {
            x.addScoreboardTag("astral.mt1");
            x.getAttribute(Attribute.MAX_HEALTH).setBaseValue(5000); x.setHealth(5000);
        });
        yo.getAttribute(Attribute.MAX_HEALTH).setBaseValue(100000); yo.setHealth(100000);   // que aguante la prueba
        double vidaInv = yo.getHealth();
        double[] vidaMob = new double[1];
        Bukkit.getScheduler().runTaskLater(this, () -> vidaMob[0] = h.getHealth(), 10);
        Bukkit.getScheduler().runTaskLater(this, () -> {
            ok(h.isDead() || h.getHealth() < h.getAttribute(Attribute.MAX_HEALTH).getValue(), "la invocacion le pega al mob: " + h.getAttribute(Attribute.MAX_HEALTH).getValue() + " -> " + h.getHealth());
            ok(yo.isDead() || yo.getHealth() < vidaInv, "el mob le pega a la invocacion: " + vidaInv + " -> " + yo.getHealth());
            h.remove();
            paso4(p, w);
        }, 160);
    }

    private void paso4(Player p, World w) {
        // 3) Guadana: clic derecho ya no hace la Cosecha (ni la pose del cuerpo).
        ItemStack g = item(p, "guadana_1");
        ok(g != null, "guadana entregada");
        boolean sinError = true;
        try { if (g != null) usar(p, g); } catch (Throwable t) { sinError = false; }
        ok(sinError, "clic derecho con guadana sin error");
        Bukkit.getScheduler().runTaskLater(this, () -> paso5(p), 20);
    }

    private void paso5(Player p) {
        // 4) AstralDueno: /modo y /sala (el ensayo pone la UUID del bot como duenia en la config).
        p.getInventory().clear();
        p.getInventory().addItem(new ItemStack(Material.DIAMOND, 7));
        p.setOp(true);
        p.performCommand("modo jugador");
        ok(!p.isOp() && p.getGameMode() == GameMode.SURVIVAL, "modo jugador: sin OP y en supervivencia");
        ok(!p.getInventory().contains(Material.DIAMOND), "modo jugador: inventario aparte");
        p.getInventory().addItem(new ItemStack(Material.EMERALD, 3));
        p.performCommand("modo admin");
        ok(p.isOp(), "modo admin: OP otra vez");
        ok(p.getInventory().contains(Material.DIAMOND, 7) && !p.getInventory().contains(Material.EMERALD), "modo admin: vuelve su inventario");
        p.performCommand("modo jugador");
        ok(p.getInventory().contains(Material.EMERALD, 3), "modo jugador: conserva lo suyo");
        p.performCommand("modo admin");
        p.performCommand("sala");
        Bukkit.getScheduler().runTaskLater(this, () -> {
            World s = Bukkit.getWorld("sala_dueno");
            ok(s != null && p.getWorld().equals(s), "sala: el duenio entra");
            int cajas = 0, items = 0;
            if (s != null)
                for (int x = -12; x <= 12; x++) for (int z = -12; z <= 12; z++) for (int y = 64; y <= 67; y++)
                    if (s.getBlockAt(x, y, z).getState() instanceof org.bukkit.block.ShulkerBox b) {
                        cajas++;
                        for (ItemStack it : b.getInventory().getContents()) if (it != null) items++;
                    }
            ok(cajas > 5 && items > 100, "sala: shulkers con items (" + cajas + " cajas, " + items + " items)");
            fin(p);
        }, 40);
    }

    private void fin(Player p) {
        getLogger().info("R23 RESULT pasos=" + pasos + " failures=" + fallas.size() + " " + fallas);
        Bukkit.getScheduler().runTaskLater(this, Bukkit::shutdown, 20);
    }
}
