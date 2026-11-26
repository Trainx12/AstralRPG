package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import com.shweit.expendablebackpacks.items.*;
import com.shweit.expendablebackpacks.ExpendableBackpacks;

/** Solo Paper local. Eventos Bukkit reales, persistencia real del plugin, jugador NMS simulado. */
public final class EnderProbe extends JavaPlugin {
    int failures;
    Player owner,other;
    final UUID outerId=UUID.fromString("8ed7cf4b-73ef-41c0-9723-a5e45d161601");
    final UUID innerId=UUID.fromString("8ed7cf4b-73ef-41c0-9723-a5e45d161602");
    void check(boolean ok,String msg){if(!ok)failures++;getLogger().info("ENDER "+(ok?"PASS ":"FAIL ")+msg);}
    Player fake(String name) throws Exception {
        var server=((org.bukkit.craftbukkit.CraftServer)Bukkit.getServer()).getServer();
        var world=((org.bukkit.craftbukkit.CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new com.mojang.authlib.GameProfile(UUID.randomUUID(),name);
        var n=new net.minecraft.server.level.ServerPlayer(server,world,profile,net.minecraft.server.level.ClientInformation.createDefault());
        var connection=new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        n.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(server,connection,n,
            net.minecraft.server.network.CommonListenerCookie.createInitial(profile,false)) {
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet){}
            @Override public void send(net.minecraft.network.protocol.Packet<?> packet,io.netty.channel.ChannelFutureListener l){}
        };
        n.setPos(0,100,0);world.addNewPlayer(n);
        var list=server.getPlayerList();list.players.add(n);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),n);
        }
        var p=n.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }
    void cmd(String c){
        // Paper encola dispatchCommand de consola; el ensayo necesita ejecutar y observar en este tick.
        var server=((org.bukkit.craftbukkit.CraftServer)Bukkit.getServer()).getServer();
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack(),c);
    }
    void as(Player p,String c){cmd("execute as "+p.getName()+" at @s run "+c);}
    int score(Player p,String o){return Bukkit.getScoreboardManager().getMainScoreboard().getObjective(o).getScore(p.getName()).getScore();}
    int level(Player p){return p.getInventory().getItemInMainHand().getEnchantmentLevel(
        org.bukkit.Registry.ENCHANTMENT.get(NamespacedKey.fromString("astral:mejora_taladro")));}
    void fresh(Player p){p.getInventory().clear();p.getInventory().setHeldItemSlot(0);as(p,"loot give @s loot astral:item/taladro_diamante");}
    void smith() {
        cmd("scoreboard players set #pub astral.mejtal 0");
        for(Player p:List.of(owner,other)) {
            fresh(p);as(p,"function astral:mejora/ver");check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp").getScore("#k").getScore()== (p==owner?3:0),"Herrero privado "+p.getName());
            as(p,"function astral:mejora/gui/inspect");check(p.getScoreboardTags().contains("asgui.valid")== (p==owner),"GUI privada "+p.getName());
        }
        cmd("scoreboard players set #pub astral.mejtal 1");
        as(other,"function astral:mejora/ver");check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp").getScore("#k").getScore()==3,"Herrero publico");
        as(other,"function astral:mejora/gui/inspect");check(other.getScoreboardTags().contains("asgui.valid"),"GUI publica");
        fresh(owner);as(owner,"function astral:mejora/ver");as(owner,"loot give @s loot astral:item/fragmento_astral");
        as(owner,"loot give @s loot astral:item/esencia_elite");as(owner,"function astral:mejora/ver");as(owner,"function astral:mejora/hacer");
        check(level(owner)==1 && score(owner,"astralmejok")==1,"hacer +1 probabilidad 100%");
        double[] bonus={.05,.10,.15,.20,.25,.30,.36,.42,.50,.60};
        for(int l=1;l<=10;l++) {
            fresh(owner);as(owner,"function astral:mejora/ver");cmd("scoreboard players set #k astral.tmp 3");
            as(owner,"function astral:mejora/ok/"+l);check(level(owner)==l,"taladro +"+l);
            as(owner,"function astral:forge/ip/taladro_mitril/taladro_diamante");
            check(level(owner)==l && owner.getInventory().getItemInMainHand().getItemMeta().getAsComponentString().contains("taladro_mitril"),"Forja conserva +"+l);
            as(owner,"item modify entity @s weapon.mainhand {function:\"minecraft:set_custom_data\",tag:{astral:{v:1}}}");
            as(owner,"function astral:upgrade/slot/container_0");check(level(owner)==l,"migracion conserva +"+l);
        }
        fresh(owner);as(owner,"function astral:mejora/ver");cmd("scoreboard players set #k astral.tmp 3");
        as(owner,"function astral:mejora/ok/10");
        Bukkit.getScheduler().runTaskLater(this,()->{
            ((org.bukkit.craftbukkit.entity.CraftPlayer)owner).getHandle().detectEquipmentUpdates();
            getLogger().info("ENDER DEBUG speed="+owner.getAttribute(org.bukkit.attribute.Attribute.BLOCK_BREAK_SPEED).getValue()+" modifiers="+owner.getAttribute(org.bukkit.attribute.Attribute.BLOCK_BREAK_SPEED).getModifiers()+" held="+level(owner));
            check(Math.abs(owner.getAttribute(org.bukkit.attribute.Attribute.BLOCK_BREAK_SPEED).getValue()-1.6)<.00001,"atributo real velocidad +60%");
            as(owner,"function astral:mejora/ver");check(score(owner,"astralmejn")==0,"tope +10");
            getLogger().info("ENDER STEP smith DONE");},5);
    }
    boolean click(Player p,InventoryView v,ItemStack item,String mode) {
        p.getInventory().clear();v.setCursor(null);
        InventoryClickEvent e;
        if(mode.equals("shift")) {p.getInventory().setItem(9,item);e=new InventoryClickEvent(v,InventoryType.SlotType.CONTAINER,v.getTopInventory().getSize(),ClickType.SHIFT_LEFT,InventoryAction.MOVE_TO_OTHER_INVENTORY);}
        else if(mode.equals("number")) {p.getInventory().setItem(1,item);e=new InventoryClickEvent(v,InventoryType.SlotType.CONTAINER,0,ClickType.NUMBER_KEY,InventoryAction.HOTBAR_SWAP,1);}
        else if(mode.equals("offhand")) {p.getInventory().setItemInOffHand(item);e=new InventoryClickEvent(v,InventoryType.SlotType.CONTAINER,0,ClickType.SWAP_OFFHAND,InventoryAction.HOTBAR_SWAP);}
        else {v.setCursor(item);e=new InventoryClickEvent(v,InventoryType.SlotType.CONTAINER,0,ClickType.LEFT,InventoryAction.PLACE_ALL);}
        Bukkit.getPluginManager().callEvent(e);v.setCursor(null);return e.isCancelled();
    }
    void bags() {
        var mgr=((ExpendableBackpacks)Bukkit.getPluginManager().getPlugin("ExpendableBackpacks")).getBackpackManager();
        for(int pub=0;pub<=1;pub++) {
            cmd("scoreboard players set #pub astral.mochender "+pub);
            getLogger().info("ENDER DEBUG pub API="+Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.mochender").getScore("#pub").getScore());
            for(Player p:List.of(owner,other)) for(BackpackTier outer:List.of(BackpackTier.LEATHER,BackpackTier.ENDERPACK)) {
                var inv=mgr.getInventory(UUID.randomUUID(),outer.getDisplayName(),outer.getSlots());
                var v=p.openInventory(inv);
                for(BackpackTier tier:BackpackTier.values()) {
                    var item=BackpackItem.createBackpack(tier);
                    boolean blocked=outer!=BackpackTier.ENDERPACK || tier==BackpackTier.ENDERPACK || pub==0 && p!=owner;
                    for(String mode:List.of("click","shift","number","offhand"))
                        check(click(p,v,item,mode)==blocked,"entrada "+mode+" "+p.getName()+" pub="+pub+" "+outer+" <- "+tier);
                    var drag=new InventoryDragEvent(v,null,item,false,Map.of(0,item));
                    Bukkit.getPluginManager().callEvent(drag);check(drag.isCancelled()==blocked,"arrastre "+outer+" <- "+tier);
                }
                // Shift de salida siempre permitido, aun si se cierra la prueba privada.
                inv.setItem(0,BackpackItem.createBackpack(BackpackTier.LEATHER));
                var take=new InventoryClickEvent(v,InventoryType.SlotType.CONTAINER,0,ClickType.SHIFT_LEFT,InventoryAction.MOVE_TO_OTHER_INVENTORY);
                Bukkit.getPluginManager().callEvent(take);check(!take.isCancelled(),"shift sacar mochila");p.closeInventory();
            }
        }
        var normal=BackpackItem.createBackpack(BackpackTier.LEATHER,innerId);
        var inner=mgr.getInventory(innerId,BackpackTier.LEATHER.getDisplayName(),9);
        inner.setItem(0,new ItemStack(Material.DIAMOND,17));
        var outer=mgr.getInventory(outerId,BackpackTier.ENDERPACK.getDisplayName(),27);
        var v=owner.openInventory(outer);
        check(!click(owner,v,normal,"shift"),"normal con contenido admitida en Ender");
        // Aplicar el movimiento aprobado: callEvent no ejecuta el protocolo de inventario NMS.
        outer.setItem(0,normal);owner.getInventory().clear();owner.closeInventory();
        mgr.saveInventory(innerId,inner);mgr.saveInventory(outerId,outer);mgr.saveAllInventories();
        var reopened=mgr.getInventory(outerId,BackpackTier.ENDERPACK.getDisplayName(),27);
        check(BackpackItem.getBackpackUUID(reopened.getItem(0)).equals(innerId),"UUID normal se conserva al reabrir Ender");
        check(mgr.getInventory(innerId,BackpackTier.LEATHER.getDisplayName(),9).getItem(0).getAmount()==17,"contenido tras sacar/reabrir");
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerQuitEvent(owner,net.kyori.adventure.text.Component.empty()));
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(owner,net.kyori.adventure.text.Component.empty()));
        check(inner.getItem(0).getAmount()==17,"contenido tras eventos reconexion");
        getLogger().info("ENDER STEP bags DONE");
    }
    void persisted() {
        var mgr=((ExpendableBackpacks)Bukkit.getPluginManager().getPlugin("ExpendableBackpacks")).getBackpackManager();
        var outer=mgr.getInventory(outerId,BackpackTier.ENDERPACK.getDisplayName(),27);
        check(outer.getItem(0)!=null && innerId.equals(BackpackItem.getBackpackUUID(outer.getItem(0))),"mochila normal tras reinicio real");
        var inner=mgr.getInventory(innerId,BackpackTier.LEATHER.getDisplayName(),9);
        check(inner.getItem(0)!=null && inner.getItem(0).getType()==Material.DIAMOND && inner.getItem(0).getAmount()==17,"17 diamantes tras reinicio real");
        getLogger().info("ENDER STEP persisted DONE");
    }
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String l,String[] a) {
        Bukkit.getScheduler().runTask(this,()->step(a));
        return true;
    }
    private void step(String[] a) {
        try {
            if(a[0].equals("persisted")){persisted();return;}
            if(a[0].equals("result")){getLogger().info("ENDER RESULT failures="+failures);return;}
            if(owner==null){owner=fake("ByTrainx");other=fake("EnderTester");}
            if(a[0].equals("smith"))smith();else bags();
        } catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"ENDER FAIL",ex);getLogger().info("ENDER STEP "+a[0]+" DONE");}
    }
}
