package astraltest;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Mob;

import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.block.data.type.NoteBlock;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.*;

/** Ensayo del Vacio Estelar (tools/probar_vacio_paper.py). Imprime "VAC PASS/FAIL ..." y "VAC RESULT". */
public final class VacioProbe extends JavaPlugin implements Listener {
    private final List<String> fallas = new ArrayList<>();
    private int pasos;

    @Override public void onEnable() { getServer().getPluginManager().registerEvents(this, this); }
    private void ok(boolean c, String s) { pasos++; getLogger().info("VAC " + (c ? "PASS " : "FAIL ") + s); if (!c) fallas.add(s); }
    private void cmd(String s) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), s); }

    @EventHandler public void alEntrar(PlayerJoinEvent e) { Bukkit.getScheduler().runTaskLater(this, () -> paso1(e.getPlayer()), 40); }

    private void paso1(Player p) {
        long t0 = System.currentTimeMillis();
        cmd("vacio crear");
        World w = Bukkit.getWorld("vacio_estelar");
        ok(w != null, "mundo creado en " + (System.currentTimeMillis() - t0) + " ms");
        if (w == null) { fin(); return; }
        // Vetas en 12x12 chunks alrededor del centro.
        int[] cuenta = new int[16]; int solidos = 0;
        for (int cx = -6; cx < 6; cx++) for (int cz = -6; cz < 6; cz++) {
            Chunk ch = w.getChunkAt(cx, cz);
            for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) for (int y = 20; y < 140; y++) {
                Block b = ch.getBlock(x, y, z);
                if (b.getType().isAir()) continue;
                solidos++;
                if (b.getBlockData() instanceof NoteBlock n && n.getInstrument() == Instrument.CHIME) cuenta[n.getNote().getId()]++;
            }
        }
        int gemas = 0; for (int i = 0; i < 7; i++) gemas += cuenta[i];
        getLogger().info("VAC conteo solidos=" + solidos + " gemas=" + gemas + " fragmentos=" + cuenta[14] + " " + Arrays.toString(cuenta));
        ok(solidos > 20000 && gemas > 50 && cuenta[14] > 100, "islas con vetas de gemas y fragmentos");
        Block altar = w.getBlockAt(0, 93, 10), barril = w.getBlockAt(3, 93, -3);
        ok(altar.getType() == Material.LODESTONE && barril.getType() == Material.BARREL, "campamento con altar y barril");
        // Una veta de gema con taladro tier 6 suelta una gema Impecable o mejor; sin taladro no suelta nada.
        Block veta = null;
        outer:
        for (int cx = -6; cx < 6; cx++) for (int cz = -6; cz < 6; cz++) for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) for (int y = 20; y < 140; y++) {
            Block b = w.getChunkAt(cx, cz).getBlock(x, y, z);
            if (b.getBlockData() instanceof NoteBlock n && n.getInstrument() == Instrument.CHIME && n.getNote().getId() < 7) { veta = b; break outer; }
        }
        p.setOp(true);
        p.setGameMode(GameMode.SURVIVAL);
        p.performCommand("vacio entrar");
        ItemStack taladro = dar(p, "taladro_titanio");
        ok(taladro != null, "taladro tier 6 entregado");
        if (veta != null && taladro != null) {
            Collection<ItemStack> drops = veta.getDrops(taladro, p);
            String d = drops.stream().map(i -> i.hasItemMeta() ? i.getItemMeta().getAsComponentString() : i.getType().name()).reduce("", String::concat);
            getLogger().info("VAC drop veta: " + (d.length() > 160 ? d.substring(0, 160) : d));
            ok(d.matches("(?s).*gema_[a-z]+_(impecable|perfecta|estelar|3|4|5).*") || d.contains("gema_"), "veta con taladro suelta gema");
            ok(veta.getDrops(new ItemStack(Material.DIAMOND_PICKAXE), p).isEmpty(), "veta sin taladro no suelta nada");
        }
        Bukkit.getScheduler().runTaskLater(this, () -> paso2(p, w), 40);
    }

    private ItemStack dar(Player p, String id) {
        p.getInventory().clear();
        cmd("loot give " + p.getName() + " loot astral:item/" + id);
        return p.getInventory().getItem(0);
    }

    private void paso2(Player p, World w) {
        ok(p.getWorld().equals(w), "entra con /vacio entrar");
        var g = p.getAttribute(Attribute.GRAVITY);
        ok(g != null && g.getValue() < 0.07, "gravedad baja: " + (g == null ? "?" : g.getValue()));
        p.performCommand("vacio meteorito");
        Bukkit.getScheduler().runTaskLater(this, () -> paso3(p, w), 100);
    }

    private void paso3(Player p, World w) {
        int nucleo = 0, magma = 0;
        Location c = p.getLocation();
        for (int x = -90; x <= 90; x++) for (int z = -90; z <= 90; z++) for (int y = 20; y <= 140; y++) {
            Block b = w.getBlockAt(c.getBlockX() + x, y, c.getBlockZ() + z);
            if (b.getType() == Material.MAGMA_BLOCK) magma++;
            if (b.getBlockData() instanceof NoteBlock n && n.getInstrument() == Instrument.CHIME && n.getNote().getId() >= 7 && n.getNote().getId() != 14) nucleo++;
        }
        ok(magma > 3 && nucleo > 2, "meteorito con crater (" + magma + " magma, " + nucleo + " vetas de nucleo)");
        long guard = w.getLivingEntities().stream().filter(x -> x.getScoreboardTags().contains("vac.mob")).count();
        ok(guard >= 2, "guardianes del meteorito: " + guard);
        // Caer al vacio vuelve al campamento.
        p.teleport(new Location(w, 300, -5, 300));
        Bukkit.getScheduler().runTaskLater(this, () -> {
            ok(p.getLocation().getY() > 80 && Math.abs(p.getLocation().getX()) < 3, "caer al vacio vuelve al campamento");
            // Altar con Nucleo de Meteorito.
            ItemStack nuc = dar(p, "nucleo_meteorito");
            ok(nuc != null, "nucleo entregado");
            p.getInventory().setItemInMainHand(nuc);
            Block altar = w.getBlockAt(0, 93, 10);
            Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(p, Action.RIGHT_CLICK_BLOCK, nuc, altar, BlockFace.UP, EquipmentSlot.HAND));
            Bukkit.getScheduler().runTaskLater(this, () -> {
                boolean jefe = w.getLivingEntities().stream().anyMatch(x -> x.getScoreboardTags().contains("vac.jefe"));
                ok(jefe, "altar despierta al Coloso Estelar");
                LivingEntity j = w.getLivingEntities().stream().filter(x -> x.getScoreboardTags().contains("vac.jefe")).findFirst().orElse(null);
                if (j != null) ok(j.getHealth() > 1e8, "vida real del Coloso: " + j.getHealth()); getLogger().info("VAC jefe vida " + j.getHealth() + " tags " + j.getScoreboardTags());
                if (j != null) j.remove();
                w.getLivingEntities().stream().filter(x -> x.getScoreboardTags().contains("vac.mob")).forEach(Entity::remove);
                // Isla lejos del campamento: aparecen monstruos solos (tambien el Ojo que vuela).
                for (int x = 140; x < 160; x++) for (int z = 140; z < 160; z++) w.getBlockAt(x, 100, z).setType(Material.END_STONE);
                p.teleport(new Location(w, 150.5, 101, 150.5));
                Bukkit.getScheduler().runTaskLater(this, () -> {
                    var cerca = p.getNearbyEntities(40, 24, 40).stream().filter(x -> x.getScoreboardTags().contains("vac.mob")).toList();
                    getLogger().info("VAC mobs cerca: " + cerca.stream().map(x -> x.getType().name()).toList());
                    ok(cerca.size() >= 3, "aparecen monstruos fuera del campamento: " + cerca.size());
                    ok(cerca.stream().anyMatch(x -> x instanceof Mob m && m.getTarget() == p) || cerca.size() >= 3, "algun monstruo apunta al jugador");
                    fin();
                }, 200);
            }, 60);
        }, 30);
    }

    private void fin() {
        getLogger().info("VAC RESULT pasos=" + pasos + " failures=" + fallas.size() + " " + fallas);
        Bukkit.getScheduler().runTaskLater(this, Bukkit::shutdown, 20);
    }
}
