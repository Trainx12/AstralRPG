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
    final NamespacedKey total=new NamespacedKey("astral","suerte_total");
    final List<String> messages=new ArrayList<>(),bars=new ArrayList<>();
    Player observed;boolean op;int sounds,particles;
    Player observe(Player real) {
        return (Player)java.lang.reflect.Proxy.newProxyInstance(getClassLoader(),new Class[]{Player.class},(proxy,m,a)->{
            if(m.getName().equals("isOp"))return op;
            if(m.getName().equals("sendMessage") || m.getName().equals("sendActionBar")) {
                Object value=a[a.length-1];
                String text=value instanceof net.kyori.adventure.text.Component c?
                    net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(c):String.valueOf(value);
                (m.getName().equals("sendMessage")?messages:bars).add(text);return null;
            }
            if(m.getName().equals("playSound")){sounds++;return null;}
            if(m.getName().equals("spawnParticle")){particles++;return null;}
            try{return m.invoke(real,a);}catch(java.lang.reflect.InvocationTargetException ex){throw ex.getCause();}
        });
    }
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
        var e=new PlayerInteractEvent(observed,Action.RIGHT_CLICK_AIR,player.getInventory().getItem(hand),null,null,hand);
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
            player=fake();player.loadData();observed=observe(player);player.getInventory().clear();player.setLevel(0);player.setExp(0);player.setTotalExperience(0);
            messages.clear();bars.clear();op=false;
            check(Bukkit.getPluginManager().isPluginEnabled("AstralDecor"),"runtime habilitado");
            for (int tier=1;tier<=10;tier++) {
                boolean existe=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/ballesta_"+tier))!=null;
                check(existe==(tier>=3 && tier<=5),"catalogo vigente de ballestas T"+tier);
            }
        }
        case "one" -> {
            player.setSneaking(false);player.getInventory().setItemInMainHand(item("frasco_xp_gigante",16));click(EquipmentSlot.HAND,false);click(EquipmentSlot.HAND,false);
            check(player.getTotalExperience()==550,"un clic da 550 XP, evento duplicado no duplica");
            check(player.getLevel()==20 || (player.getLevel()==19 && player.getExp()>.999f),
                  "550 puntos alcanzan aproximadamente nivel 20: nivel="+player.getLevel()+" barra="+player.getExp());
            check(player.getInventory().getItemInMainHand().getAmount()==15,"consume solo un frasco");
            check(messages.isEmpty(),"no OP no recibe chat de XP");
        }
        case "stack" -> {
            op=true;messages.clear();player.setSneaking(true);click(EquipmentSlot.HAND,false);
            check(player.getTotalExperience()==8800,"shift da exactamente 15 x 550 XP");
            check(player.getInventory().getItemInMainHand().getType().isAir(),"stack consumido");
            check(messages.equals(List.of("Recibiste 8250 puntos de XP.")),"OP recibe un solo total del stack");op=false;
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
        case "manzanas" -> {
            // Manzanas de Mazmorra (manzanas.py): T2 cura 250 = 125 al instante + 125 en 5 s (Paper local topa la vida en 1024).
            player.addScoreboardTag("astral.vida100");
            var max=player.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH);max.setBaseValue(1000);
            player.setHealth(100);bars.clear();
            Bukkit.getPluginManager().callEvent(new PlayerItemConsumeEvent(observed,item("manzana_t2",1),EquipmentSlot.HAND));
            check(Math.abs(player.getHealth()-225)<0.01,"manzana T2 cura 125 al instante: "+player.getHealth());
            check(!bars.isEmpty() && bars.getLast().contains("250"),"aviso de cura: "+bars);
            var it=item("manzana_t5",1);
            check(it.getItemMeta().hasUseCooldown() && it.getItemMeta().getUseCooldown().getCooldownSeconds()==20f,"enfriamiento de 20 s");
            Bukkit.getPluginManager().callEvent(new PlayerItemConsumeEvent(observed,item("manzana_esmeralda",1),EquipmentSlot.HAND));
            check(Math.abs(player.getHealth()-225)<0.01,"la Manzana de la Suerte no cura");
            player.getPersistentDataContainer().remove(until);player.getPersistentDataContainer().remove(total);
            sounds=0;particles=0;messages.clear();bars.clear();
        }
        case "manzanas2" -> {check(Math.abs(player.getHealth()-350)<1,"manzana T2 cura el resto en 5 s: "+player.getHealth());
            player.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).setBaseValue(20);player.setHealth(20);}
        case "apple" -> {
            player.getPersistentDataContainer().remove(until);player.getPersistentDataContainer().remove(total);messages.clear();
            var e=new PlayerItemConsumeEvent(observed,item("manzana_esmeralda",1),EquipmentSlot.HAND);Bukkit.getPluginManager().callEvent(e);
            long left=player.getPersistentDataContainer().getOrDefault(until,PersistentDataType.LONG,0L)-System.currentTimeMillis();
            check(left>299000 && left<=300000,"manzana activa cinco minutos");
            check(messages.getFirst().contains("Manzana de la Suerte") && messages.getFirst().contains("+5:00") && messages.getFirst().contains("15,3%") && messages.getFirst().contains("4,9%") && messages.getFirst().contains("0,7%"),"mensaje nuevo con porcentajes calculados");
            Bukkit.getPluginManager().callEvent(new PlayerItemConsumeEvent(observed,item("manzana_esmeralda",1),EquipmentSlot.HAND));
            left=player.getPersistentDataContainer().getOrDefault(until,PersistentDataType.LONG,0L)-System.currentTimeMillis();
            check(left>599000 && left<=600000,"dos manzanas acumulan diez minutos");
            check(messages.getLast().contains("Suerte renovada") && messages.getLast().contains("10:00"),"renovacion informa tiempo acumulado");
            check(player.getPersistentDataContainer().get(total,PersistentDataType.LONG)>599000,"maximo de racha persistente");
            check(sounds==2 && particles==2,"un sonido y una emision por manzana");
            player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()+150000);
            invoke("updateLuck",observed);
            check(bars.getLast().contains("▯"),"barra se vacia respecto al maximo de la racha");
            e=new PlayerItemConsumeEvent(observed,item("manzana_esmeralda",1),EquipmentSlot.HAND);e.setCancelled(true);
            long before=player.getPersistentDataContainer().get(until,PersistentDataType.LONG);Bukkit.getPluginManager().callEvent(e);
            check(before==player.getPersistentDataContainer().get(until,PersistentDataType.LONG),"comida cancelada no activa");
            player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()-1000);messages.clear();
            invoke("updateLuck",observed);invoke("updateLuck",observed);
            check(messages.size()==1 && messages.getFirst().contains("se termino"),"vencimiento avisa una sola vez");
            check(!player.getPersistentDataContainer().has(total),"racha se limpia al vencer");
            Bukkit.getPluginManager().callEvent(new PlayerItemConsumeEvent(observed,item("manzana_esmeralda",1),EquipmentSlot.HAND));
        }
        case "roll" -> {
            check(Bukkit.getPlayerExact("XPProbe")==player,"jugador resuelto por nombre");
            check(Bukkit.getConsoleSender() instanceof org.bukkit.command.ConsoleCommandSender,"consola real");
            check(Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute if entity XPProbe run astralgacha XPProbe gacha_rpg 10 true"),"comando de gacha registrado via execute");
            // Desde el 17/11 (054db88) la tirada usa la API de CrazyCrates (sin give virtual ni mass-open):
            // la cubre tools/probar_gachas_paper.py con CrazyCrates real. Aca solo vence la suerte.
            player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()-1000);
        }
        case "snapshot" -> {
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
            player.getPersistentDataContainer().set(until,PersistentDataType.LONG,System.currentTimeMillis()+300000);
            player.getPersistentDataContainer().set(total,PersistentDataType.LONG,600000L);player.saveData();
        }
        case "persist" -> {
            check(player.getPersistentDataContainer().getOrDefault(until,PersistentDataType.LONG,0L)>System.currentTimeMillis(),"suerte persistida tras reinicio");
            check(player.getPersistentDataContainer().getOrDefault(total,PersistentDataType.LONG,0L)>0,"maximo de racha persistido tras reinicio");
        }
        case "result" -> getLogger().info("XP RESULT failures="+failures);
        }
      }catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"XP FAIL exception",ex);}
      return true;
    }
}
