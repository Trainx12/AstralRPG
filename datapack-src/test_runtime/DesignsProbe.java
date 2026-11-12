package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.persistence.PersistentDataType;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import net.minecraft.network.protocol.game.ClientboundSetEquipmentPacket;
import com.mojang.authlib.GameProfile;
import io.netty.channel.*;

/** Comprueba paquetes y estado real de Paper; no simula el render del cliente. */
public final class DesignsProbe extends JavaPlugin {
    Player player,observer;int failures;
    Map<UUID,List<ClientboundSetEquipmentPacket>> packets=new HashMap<>();
    void check(boolean ok,String label) {if(!ok)failures++;getLogger().info("DESIGNS "+(ok?"PASS ":"FAIL ")+label);}
    Player fake(String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),name);
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        var seen=new ArrayList<ClientboundSetEquipmentPacket>();packets.put(profile.id(),seen);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel(new ChannelOutboundHandlerAdapter(){
            @Override public void write(ChannelHandlerContext ctx,Object msg,ChannelPromise promise) {
                if(msg instanceof ClientboundSetEquipmentPacket p)seen.add(p);
                promise.setSuccess();
            }
        });
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        world.getWorld().getChunkAt(0,0).setForceLoaded(true);fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);field.setAccessible(true);
            ((Map)field.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        Player p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);p.setOp(false);return p;
    }
    void refresh() throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");
        var method=plugin.getClass().getDeclaredMethod("hats");method.setAccessible(true);method.invoke(plugin);
    }
    void equip(String name) {getLogger().info("DESIGNS command "+name+" result="+Bukkit.dispatchCommand(player,"astralcosmetic sombrero "+name));}
    boolean sent(Player viewer,Material material) {
        return packets.get(viewer.getUniqueId()).stream().anyMatch(p->p.getEntity()==player.getEntityId()
            && p.getSlots().stream().anyMatch(pair->pair.getFirst()==net.minecraft.world.entity.EquipmentSlot.HEAD
            && org.bukkit.craftbukkit.inventory.CraftItemStack.asBukkitCopy(pair.getSecond()).getType()==material));
    }
    void clear() {packets.values().forEach(List::clear);}
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String l,String[] a) {
      try {
        switch(a[0]) {
        case "start" -> {
            player=fake("DesignOwner");observer=fake("DesignObserver");
            equip("bruja");
            check(!player.getPersistentDataContainer().has(new NamespacedKey("astraldecor","cosmetic_sombrero")),"sin permiso no equipa");
            player.addAttachment(this,"astral.cosmetico.sombrero.bruja",true);
            clear();equip("bruja");refresh();
        }
        case "equipped" -> {
            check(sent(player,Material.PAPER),"paquete HEAD al portador (tercera persona)");
            check(sent(observer,Material.PAPER),"paquete HEAD al observador");
            check(player.getInventory().getHelmet()==null || player.getInventory().getHelmet().getType().isAir(),"inventario casco vacio");
            check(player.getPassengers().isEmpty(),"sin pasajeros ni bloqueo de teleport");
            check(player.getWorld().getEntitiesByClass(ItemDisplay.class).stream().noneMatch(e->e.getScoreboardTags().contains("astral.hat") || e.getScoreboardTags().contains("astral.wings")),"sin displays de gorros ni alas");
            clear();player.getInventory().setHelmet(new ItemStack(Material.DIAMOND_HELMET));refresh();
        }
        case "helmet" -> {
            check(sent(player,Material.DIAMOND_HELMET) && sent(observer,Material.DIAMOND_HELMET),"casco real restaurado para ambos");
            check(player.getInventory().getHelmet().getType()==Material.DIAMOND_HELMET,"casco real intacto");
            clear();player.getInventory().setHelmet(null);refresh();
        }
        case "restore" -> {
            check(sent(player,Material.PAPER) && sent(observer,Material.PAPER),"al sacar casco reaparece gorro");
            clear();equip("quitar");refresh();
        }
        case "clear" -> {
            check(sent(player,Material.AIR) && sent(observer,Material.AIR),"quitar restaura cabeza vacia");
            player.addAttachment(this,"astral.cosmetico.alas.asura",true);equip("diablo");refresh();
        }
        case "legacy" -> {
            check("diablo".equals(player.getPersistentDataContainer().get(new NamespacedKey("astraldecor","cosmetic_sombrero"),PersistentDataType.STRING)),"permiso de alas Asura habilita Diablo");
            Bukkit.dispatchCommand(player,"astralcosmetic alas asura");
            check(!player.getPersistentDataContainer().has(new NamespacedKey("astraldecor","cosmetic_alas")),"no se pueden reequipar alas retiradas");
            player.saveData();player.getPersistentDataContainer().remove(new NamespacedKey("astraldecor","cosmetic_sombrero"));player.loadData();
            check("diablo".equals(player.getPersistentDataContainer().get(new NamespacedKey("astraldecor","cosmetic_sombrero"),PersistentDataType.STRING)),"seleccion persiste al cargar playerdata");
        }
        case "result" -> getLogger().info("DESIGNS RESULT failures="+failures);
        }
      } catch(Exception ex) {check(false,ex.toString());ex.printStackTrace();}
      return true;
    }
}
