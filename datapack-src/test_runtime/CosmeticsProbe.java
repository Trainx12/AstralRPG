package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.player.PlayerQuitEvent;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.*;
import com.mojang.authlib.GameProfile;

/** Solo para Paper local. No instalar este plugin en remoto. */
public final class CosmeticsProbe extends JavaPlugin {
    Player player; int failures;
    void check(boolean ok,String label) { if(!ok)failures++;getLogger().info("COSMETICS "+(ok?"PASS ":"FAIL ")+label); }
    long displays(String tag) { return player.getWorld().getEntitiesByClass(ItemDisplay.class).stream().filter(e->e.getScoreboardTags().contains(tag)).count(); }
    void command(String args) { Bukkit.dispatchCommand(player,"astralcosmetic "+args); }
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String l,String[] a) {
      try {
        if(a[0].equals("start")) {
            var server=((CraftServer)Bukkit.getServer()).getServer();
            var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
            var profile=new GameProfile(UUID.randomUUID(),"CosmeticProbe");
            var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
            var connection=new Connection(PacketFlow.SERVERBOUND);
            connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
            connection.channel.pipeline().addLast("packet_handler",connection);
            connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
            fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
            world.getWorld().getChunkAt(0,0).setForceLoaded(true);
            fake.setPos(0,100,0);world.addNewPlayer(fake);
            var list=server.getPlayerList();list.players.add(fake);
            for(String name:List.of("playersByUUID","playersByName")) {
                var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(name);field.setAccessible(true);
                ((Map)field.get(list)).put(name.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
            }
            player=fake.getBukkitEntity();player.setOp(false);player.setInvulnerable(true);player.setGravity(false);
            command("sombrero bruja");
            check(!player.getPersistentDataContainer().has(new NamespacedKey("astraldecor","cosmetic_sombrero")),"sin permiso no equipa");
            player.addAttachment(this,"astral.cosmetico.sombrero.bruja",true);
            player.addAttachment(this,"astral.cosmetico.alas.asura",true);
            command("sombrero bruja");command("alas asura");
        } else if(a[0].equals("equipped")) {
            check(displays("astral.hat")==1,"un sombrero visual");
            check(displays("astral.wings")==1,"un par de alas visual");
            check(player.getInventory().getItemInOffHand().getType().isAir(),"segunda mano libre");
            check(player.getInventory().getHelmet()==null || player.getInventory().getHelmet().getType().isAir(),"no ocupa casco");
            var key=new NamespacedKey("astraldecor","cosmetic_sombrero");
            player.saveData();player.getPersistentDataContainer().remove(key);player.loadData();
            check("bruja".equals(player.getPersistentDataContainer().get(key,PersistentDataType.STRING)),"seleccion persiste en playerdata");
            player.getInventory().setHelmet(new ItemStack(Material.DIAMOND_HELMET));
        } else if(a[0].equals("helmet")) {
            check(displays("astral.hat")==0,"casco oculta sombrero");
            check(player.getInventory().getHelmet().getType()==Material.DIAMOND_HELMET,"casco conservado");
            player.getInventory().setHelmet(null);command("sombrero quitar");command("alas quitar");
        } else if(a[0].equals("clear")) {
            check(displays("astral.hat")==0 && displays("astral.wings")==0,"quitar limpia displays");
            check(player.hasPermission("astral.cosmetico.sombrero.bruja"),"quitar conserva desbloqueo");
            command("sombrero bruja");command("alas asura");
        } else if(a[0].equals("death")) {
            player.setInvulnerable(false);player.setHealth(0);
            check(displays("astral.hat")==0 && displays("astral.wings")==0,"muerte elimina displays");
            check(player.getWorld().getEntitiesByClass(Item.class).isEmpty(),"sin drops cosmeticos");
            check(player.getPersistentDataContainer().has(new NamespacedKey("astraldecor","cosmetic_sombrero")),"muerte conserva seleccion");
            Bukkit.getPluginManager().callEvent(new PlayerQuitEvent(player,net.kyori.adventure.text.Component.empty(),PlayerQuitEvent.QuitReason.DISCONNECTED));
        } else if(a[0].equals("result")) getLogger().info("COSMETICS RESULT failures="+failures);
      } catch(Exception ex) { check(false,ex.toString());ex.printStackTrace(); }
      return true;
    }
}
