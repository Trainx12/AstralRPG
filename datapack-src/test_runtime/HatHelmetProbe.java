package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.Damageable;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.player.PlayerQuitEvent;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.*;
import com.mojang.authlib.GameProfile;

/** Sombrero sobre el casco. Solo para Paper local; no instalar en remoto. */
public final class HatHelmetProbe extends JavaPlugin {
    Player player; int failures; ItemStack original, keep;
    ItemStack restoreForProbe(ItemStack i) { return i==null?original.clone():i; }
    void check(boolean ok,String label) { if(!ok)failures++;getLogger().info("HATHELM "+(ok?"PASS ":"FAIL ")+label); }
    void command(String args) { Bukkit.dispatchCommand(player,"astralcosmetic "+args); }
    ItemStack helmet() {
        ItemStack item=new ItemStack(Material.DIAMOND_HELMET);var meta=item.getItemMeta();
        meta.setItemModel(NamespacedKey.fromString("astral:berserker_4_helmet"));
        var eq=meta.getEquippable();eq.setModel(NamespacedKey.fromString("astral:berserker_4"));meta.setEquippable(eq);
        meta.addAttributeModifier(org.bukkit.attribute.Attribute.ARMOR,new org.bukkit.attribute.AttributeModifier(
            NamespacedKey.fromString("astral:berserker_4_helmet.barra"),3,org.bukkit.attribute.AttributeModifier.Operation.ADD_NUMBER,EquipmentSlotGroup.HEAD));
        meta.getPersistentDataContainer().set(NamespacedKey.fromString("astral:probe"),org.bukkit.persistence.PersistentDataType.STRING,"berserker");
        item.setItemMeta(meta);return item;
    }
    boolean worn(ItemStack item,String hat) {
        if(item==null||!item.hasItemMeta())return false;var meta=item.getItemMeta();
        return ("astral:cosmeticos/casco_"+hat).equals(String.valueOf(meta.getItemModel()))
            && meta.getCustomModelDataComponent().getStrings().equals(List.of("astral:berserker_4_helmet"))
            && meta.getEquippable().getModel()==null;
    }
    boolean same(ItemStack a,ItemStack b) { return a!=null && b!=null && a.isSimilar(b); }
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String l,String[] a) {
      try {
        if(a[0].equals("start")) {
            var server=((CraftServer)Bukkit.getServer()).getServer();
            var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
            var profile=new GameProfile(UUID.randomUUID(),"HatProbe");
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
            player.addAttachment(this,"astral.cosmetico.sombrero.bruja",true);
            player.addAttachment(this,"astral.cosmetico.sombrero.cleric",true);
            original=helmet();player.getInventory().setHelmet(original.clone());
            command("sombrero bruja");
        } else if(a[0].equals("worn")) {
            ItemStack h=player.getInventory().getHelmet();
            check(worn(h,"bruja"),"casco puesto dibuja el sombrero y sin armadura");
            check(h.getType()==Material.DIAMOND_HELMET,"sigue siendo el mismo casco");
            check(h.getItemMeta().getAttributeModifiers(org.bukkit.attribute.Attribute.ARMOR).stream().anyMatch(m->m.getAmount()==3),"conserva la armadura (modificador del casco)");
            check(h.getItemMeta().getPersistentDataContainer().has(NamespacedKey.fromString("astral:probe")),"conserva sus datos");
            var meta=h.getItemMeta();((Damageable)meta).setDamage(7);h.setItemMeta(meta);player.getInventory().setHelmet(h);
            command("sombrero cleric");
        } else if(a[0].equals("change")) {
            check(worn(player.getInventory().getHelmet(),"cleric"),"cambiar de sombrero cambia el dibujo");
            // Sacar el casco a la mochila: debe volver a ser el original.
            ItemStack h=player.getInventory().getHelmet();player.getInventory().setHelmet(null);player.getInventory().setItem(5,h);
        } else if(a[0].equals("moved")) {
            ItemStack back=player.getInventory().getItem(5);
            check(back!=null && back.getItemMeta().getItemModel().toString().equals("astral:berserker_4_helmet"),"fuera de la cabeza vuelve el modelo");
            check(back.getItemMeta().getEquippable().getModel()!=null,"fuera de la cabeza vuelve la armadura");
            check(((Damageable)back.getItemMeta()).getDamage()==7,"conserva el desgaste");
            var copy=original.clone();var m=copy.getItemMeta();((Damageable)m).setDamage(7);copy.setItemMeta(m);
            check(same(back,copy),"identico al original");
            player.getInventory().setItem(5,null);player.getInventory().setHelmet(back);
        } else if(a[0].equals("again")) {
            check(worn(player.getInventory().getHelmet(),"cleric"),"al volver a la cabeza se viste de nuevo");
            command("sombrero quitar");
        } else if(a[0].equals("off")) {
            ItemStack h=player.getInventory().getHelmet();
            check(h!=null && !h.getItemMeta().getPersistentDataContainer().has(new NamespacedKey("astraldecor","hat_original")),"quitar devuelve el casco original");
            command("sombrero bruja");
        } else if(a[0].equals("bare")) {
            keep=player.getInventory().getHelmet();player.getInventory().setHelmet(null);
        } else if(a[0].equals("bare2")) {
            ItemStack h=player.getInventory().getHelmet();
            check(h!=null && "astral:cosmeticos/solo_bruja".equals(String.valueOf(h.getItemMeta().getItemModel())),"sin casco el sombrero sigue en la cabeza");
            check(h!=null && h.getItemMeta().isHideTooltip(),"sin texto al pasar el mouse");
            check(Arrays.stream(player.getInventory().getStorageContents()).noneMatch(i->i!=null && i.getType()==Material.PAPER),"no aparece en la mochila");
            // Al ponerse un casco, el sombrero solo se va y el casco se viste.
            player.getInventory().setHelmet(restoreForProbe(keep));
        } else if(a[0].equals("bare3")) {
            check(worn(player.getInventory().getHelmet(),"bruja"),"al ponerse el casco vuelve a dibujar el sombrero");
        } else if(a[0].equals("death")) {
            check(worn(player.getInventory().getHelmet(),"bruja"),"vestido antes de morir");
            player.setInvulnerable(false);player.setHealth(0);
        } else if(a[0].equals("drops")) {
            var items=player.getWorld().getEntitiesByClass(Item.class);
            check(items.stream().anyMatch(i->i.getItemStack().getType()==Material.DIAMOND_HELMET
                && "astral:berserker_4_helmet".equals(String.valueOf(i.getItemStack().getItemMeta().getItemModel()))),"al morir cae el casco original");
            check(items.stream().noneMatch(i->i.getItemStack().hasItemMeta() && i.getItemStack().getItemMeta().getPersistentDataContainer()
                .has(new NamespacedKey("astraldecor","hat_original"))),"ningun casco cambiado en el suelo");
            Bukkit.getPluginManager().callEvent(new PlayerQuitEvent(player,net.kyori.adventure.text.Component.empty(),PlayerQuitEvent.QuitReason.DISCONNECTED));
        } else if(a[0].equals("result")) getLogger().info("HATHELM RESULT failures="+failures);
      } catch(Exception ex) { check(false,ex.toString());ex.printStackTrace(); }
      return true;
    }
}
