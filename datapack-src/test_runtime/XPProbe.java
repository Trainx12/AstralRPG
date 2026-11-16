package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.event.player.*;
import org.bukkit.event.block.Action;
import org.bukkit.persistence.PersistentDataType;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Solo ensayo local: XP real y eventos con un jugador NMS, sin cliente visual. */
public final class XPProbe extends JavaPlugin {
    Player player;int failures;final List<String> crateCalls=new ArrayList<>();
    final NamespacedKey until=new NamespacedKey("astral","suerte_hasta");
    void check(boolean ok,String text){if(!ok)failures++;getLogger().info("XP "+(ok?"PASS ":"FAIL ")+text);}
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("AstralXPProbe".getBytes()),"XPProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        world.getWorld().getChunkAt(0,0).setForceLoaded(true);fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }
    ItemStack item(String id,int n) {
        var it=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id)).populateLoot(new Random(),new org.bukkit.loot.LootContext.Builder(player.getLocation()).build()).iterator().next();
        it.setAmount(n);return it;
    }
    void click(EquipmentSlot hand,boolean deny) {
        var e=new PlayerInteractEvent(player,Action.RIGHT_CLICK_AIR,player.getInventory().getItem(hand),null,null,hand);
        if(deny)e.setUseItemInHand(org.bukkit.event.Event.Result.DENY);
        Bukkit.getPluginManager().callEvent(e);
    }
    void invoke(String name,Player p) throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");var m=plugin.getClass().getDeclaredMethod(name,Player.class);m.setAccessible(true);m.invoke(plugin,p);
    }
    public void onEnable() {
        // Dobles de consola: se comprueba el routing sin instalar otra ruleta ni cobrar dinero.
        for(String name:List.of("crates","sudo")) {
            Bukkit.getCommandMap().register("xpprobe",new org.bukkit.command.Command(name){
                public boolean execute(org.bukkit.command.CommandSender s,String label,String[] args){crateCalls.add(label+" "+String.join(" ",args));return true;}
            });
        }
    }
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
      try {
        switch(args[0]) {
        case "start" -> {
            player=fake();player.loadData();player.getInventory().clear();player.setLevel(0);player.setExp(0);player.setTotalExperience(0);
            check(Bukkit.getPluginManager().isPluginEnabled("AstralDecor"),"runtime habilitado");
            check(Bukkit.getLootTable(NamespacedKey.fromString("astral:item/ballesta_10"))!=null,"datapack 10 ballestas carga");
        }
        case "one" -> {
            player.setSneaking(false);player.getInventory().setItemInMainHand(item("frasco_xp_gigante",16));click(EquipmentSlot.HAND,false);click(EquipmentSlot.HAND,false);
            check(player.getTotalExperience()==550,"un clic da 550 XP, evento duplicado no duplica");
            check(player.getLevel()==20 || (player.getLevel()==19 && player.getExp()>.999f),
                  "550 puntos alcanzan aproximadamente nivel 20: nivel="+player.getLevel()+" barra="+player.getExp());
            check(player.getInventory().getItemInMainHand().getAmount()==15,"consume solo un frasco");
        }
        case "stack" -> {
            player.setSneaking(true);click(EquipmentSlot.HAND,false);
            check(player.getTotalExperience()==8800,"shift da exactamente 15 x 550 XP");
            check(player.getInventory().getItemInMainHand().getType().isAir(),"stack consumido");
        }
        case "offhand" -> {
            player.setSneaking(false);player.getInventory().setItemInOffHand(item("barril_xp",2));click(EquipmentSlot.OFF_HAND,false);
            check(player.getTotalExperience()==14300,"mano secundaria da 5500 XP");
            check(player.getInventory().getItemInOffHand().getAmount()==1,"consume un barril de mano secundaria");
        }
        case "denied" -> {
            player.getInventory().setItemInMainHand(item("frasco_xp_gigante",1));click(EquipmentSlot.HAND,true);
            check(player.getTotalExperience()==14300 && player.getInventory().getItemInMainHand().getAmount()==1,"evento denegado no consume ni da XP");
        }
        case "apple" -> {
            var e=new PlayerItemConsumeEvent(player,item("manzana_esmeralda",1),EquipmentSlot.HAND);Bukkit.getPluginManager().callEvent(e);
            long left=player.getPersistentDataContainer().getOrDefault(until,PersistentDataType.LONG,0L)-System.currentTimeMillis();
            check(left>299000 && left<=300000,"manzana activa cinco minutos");
            player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()+1000);
            Bukkit.getPluginManager().callEvent(new PlayerItemConsumeEvent(player,item("manzana_esmeralda",1),EquipmentSlot.HAND));
            left=player.getPersistentDataContainer().getOrDefault(until,PersistentDataType.LONG,0L)-System.currentTimeMillis();
            check(left>299000 && left<=300000,"renueva, no acumula");
            e=new PlayerItemConsumeEvent(player,item("manzana_esmeralda",1),EquipmentSlot.HAND);e.setCancelled(true);
            long before=player.getPersistentDataContainer().get(until,PersistentDataType.LONG);Bukkit.getPluginManager().callEvent(e);
            check(before==player.getPersistentDataContainer().get(until,PersistentDataType.LONG),"comida cancelada no activa");
        }
        case "roll" -> {
            check(Bukkit.getPlayerExact("XPProbe")==player,"jugador resuelto por nombre");
            check(Bukkit.getConsoleSender() instanceof org.bukkit.command.ConsoleCommandSender,"consola real");
            check(Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute if entity XPProbe run astralgacha XPProbe gacha_rpg 10 true"),"comando de gacha registrado via execute");
            Bukkit.getScheduler().runTaskLater(this,()->{
                check(crateCalls.contains("crates forceopen gacha_rpg_garantia_suerte XPProbe"),"garantia usa tabla con suerte");
                player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()-1000);
            },20);
        }
        case "snapshot" -> {
            check(crateCalls.contains("crates give virtual gacha_rpg_suerte 9 XPProbe -s"),"resto del lote conserva suerte vencida");
            check(crateCalls.stream().anyMatch(s->s.contains("mass-open gacha_rpg_suerte virtual 9")),"lote abre mismas llaves");
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astralgacha XPProbe gacha_rpg 1 false");
            Bukkit.getScheduler().runTaskLater(this,()->check(crateCalls.contains("crates forceopen gacha_rpg XPProbe"),"siguiente compra sin suerte"),20);
            invoke("updateLuck",player);check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.suerte").getScore("XPProbe").getScore()==0,"suerte vencida en scoreboard");
        }
        case "backpacks" -> {
            for(int t=1;t<=6;t++) {
                var it=new ItemStack(Material.PLAYER_HEAD);var meta=it.getItemMeta();
                meta.getPersistentDataContainer().set(NamespacedKey.fromString("expendablebackpacks:backpack_uuid"),PersistentDataType.STRING,"preservar-"+t);
                meta.getPersistentDataContainer().set(NamespacedKey.fromString("expendablebackpacks:backpack_tier"),PersistentDataType.INTEGER,t);it.setItemMeta(meta);player.getInventory().setItem(t,it);
            }
            invoke("backpackModels",player);
            for(int t=1;t<=6;t++) {
                var meta=player.getInventory().getItem(t).getItemMeta();
                check(meta.getItemModel()!=null && meta.getItemModel().getKey().startsWith("mochila_"),"modelo mochila T"+t);
                check(meta.getPersistentDataContainer().get(NamespacedKey.fromString("expendablebackpacks:backpack_uuid"),PersistentDataType.STRING).equals("preservar-"+t),"UUID conservado T"+t);
            }
            player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()+300000);player.saveData();
        }
        case "persist" -> {
            check(player.getPersistentDataContainer().getOrDefault(until,PersistentDataType.LONG,0L)>System.currentTimeMillis(),"suerte persistida tras reinicio");
        }
        case "result" -> getLogger().info("XP RESULT failures="+failures);
        }
      }catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"XP FAIL exception",ex);}
      return true;
    }
}
