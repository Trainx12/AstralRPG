package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.command.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.*;
import net.minecraft.network.protocol.game.*;
import com.mojang.authlib.GameProfile;
import net.milkbowl.vault.economy.*;

/** Solo Paper local: jugadores NMS y economia simulada, MythicMobs real. */
public final class MerchantProbe extends JavaPlugin {
    int failures, checks, opens, charges; Object merchant; Player first, second;
    final List<String> messages=new ArrayList<>();
    void check(boolean ok,String label){checks++;if(!ok)failures++;getLogger().info("MERCHANT "+(ok?"PASS ":"FAIL ")+label);}
    Player fake(World w,String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();var world=((CraftWorld)w).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),name);
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false)) {
            @Override public void send(Packet<?> packet){if(packet instanceof ClientboundSystemChatPacket chat)messages.add(chat.content().getString());}
            @Override public void send(Packet<?> packet,io.netty.channel.ChannelFutureListener listener){send(packet);}
        };
        fake.setPos(0,65,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }
    Object get(String name) throws Exception {var f=merchant.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(merchant);}
    void set(String name,Object value) throws Exception {var f=merchant.getClass().getDeclaredField(name);f.setAccessible(true);f.set(merchant,value);}
    Object call(String name,Class<?>[] types,Object...args) throws Exception {var m=merchant.getClass().getDeclaredMethod(name,types);m.setAccessible(true);return m.invoke(merchant,args);}
    // Paper puede diferir dispatchCommand al siguiente tick; ejecutar su PluginCommand
    // permite verificar cada transaccion antes de iniciar la siguiente.
    void command(CommandSender sender,String args){Bukkit.getPluginCommand("astralmercader").execute(sender,"astralmercader",args.split(" "));}
    void cmd(String args){command(Bukkit.getConsoleSender(),args);}
    LivingEntity active() throws Exception {return (LivingEntity)get("merchant");}
    void floor(World w,Material type){for(int x=-20;x<=20;x++)for(int z=-20;z<=20;z++){w.getBlockAt(x,64,z).setType(type);w.getBlockAt(x,65,z).setType(Material.AIR);w.getBlockAt(x,66,z).setType(Material.AIR);}}
    public boolean onCommand(CommandSender sender,Command command,String label,String[] args) {
        if(command.getName().equals("dm")){opens++;return true;}
        try {run();}catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"MERCHANT FAIL",ex);}
        Bukkit.getScheduler().runTaskLater(this,()->{
            check(opens==1,"comando de menu diferido se ejecuta una vez");
            getLogger().info("MERCHANT RESULT checks="+checks+" failures="+failures);
        },5);return true;
    }
    void run() throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");
        var field=plugin.getClass().getDeclaredField("merchant");field.setAccessible(true);merchant=field.get(plugin);
        var world=Bukkit.getWorld("world");floor(world,Material.STONE);
        first=fake(world,"MerchantOne");second=fake(world,"MerchantTwo");first.setOp(true);first.setGameMode(GameMode.CREATIVE);second.setOp(false);
        Economy economy=(Economy)java.lang.reflect.Proxy.newProxyInstance(Economy.class.getClassLoader(),new Class[]{Economy.class},(proxy,m,a)->{
            if(m.getName().equals("withdrawPlayer")){charges++;return new EconomyResponse(0,999999,EconomyResponse.ResponseType.SUCCESS,"");}
            if(m.getName().equals("depositPlayer"))return new EconomyResponse(0,999999,EconomyResponse.ResponseType.SUCCESS,"");
            if(m.getName().equals("getName"))return "MerchantProbe";
            if(m.getReturnType()==boolean.class)return true;if(m.getReturnType()==double.class)return 999999d;if(m.getReturnType()==int.class)return 2;return null;
        });
        Bukkit.getServicesManager().register(Economy.class,economy,this,org.bukkit.plugin.ServicePriority.Highest);
        command(second,"visita");check(active()==null,"sin OP no crea visita");
        command(first,"visita");var entity=active();
        check(entity!=null && entity.isValid(),"OP creativo fuerza visita en world");
        check(entity.isSilent(),"mercader real Silent true");check((int)get("expires")==Bukkit.getCurrentTick()+6000,"visita cinco minutos");
        cmd("visita MerchantTwo");check(active().getUniqueId().equals(entity.getUniqueId()),"no duplica UUID activo");
        second.teleport(entity.getLocation());first.teleport(entity.getLocation());
        var click=new PlayerInteractEntityEvent(second,entity,EquipmentSlot.HAND);Bukkit.getPluginManager().callEvent(click);
        check(click.isCancelled(),"visita acepta clic derecho para comerciar");
        for(int i=0;i<5;i++)cmd("MerchantTwo frasco_xp_pequeno");
        check(charges==4,"limite de cuatro compras sin cobrar quinta");
        var stocks=(Map<UUID,Map<String,Integer>>)get("bought");check(stocks.get(second.getUniqueId()).get("frasco_xp_pequeno")==4,"stock real por UUID");
        cmd("MerchantOne frasco_xp_pequeno");check(charges==5 && stocks.get(first.getUniqueId()).get("frasco_xp_pequeno")==1,"stock independiente entre jugadores");
        check(second.getInventory().contains(Material.PAPER),"loot entregado al inventario");
        int before=charges;second.teleport(new Location(world,80,65,80));cmd("MerchantTwo frasco_xp_grande");check(charges==before,"lejos no cobra");
        command(second,"irse");check(active()!=null,"sin OP no despide");
        cmd("irse");check(active()==null && !entity.isValid() && ((Map)get("bought")).isEmpty(),"irse elimina visita y stock");
        int next=(int)get("next")-Bukkit.getCurrentTick();check(next>=40*60*20 && next<=60*60*20,"siguiente visita 40-60 min");
        cmd("visita");check(active()==null,"consola requiere jugador");
        first.teleport(new Location(world,0,65,0));cmd("visita MerchantOne");check(active()!=null,"consola con jugador conectado");
        set("expires",Bukkit.getCurrentTick());call("tick",new Class[]{});check(active()==null,"expiracion retira visita");
        var manual=io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_goblin_vendedor",first.getLocation());
        int messageCount=messages.size();Bukkit.getPluginManager().callEvent(new PlayerInteractEntityEvent(first,manual,EquipmentSlot.HAND));
        check(messages.subList(messageCount,messages.size()).stream().anyMatch(s->s.contains("no esta de visita")),"spawn manual informa comando al OP");
        messageCount=messages.size();call("cleanupOld",new Class[]{Entity.class},manual);
        check(!manual.isValid() && messages.subList(messageCount,messages.size()).stream().anyMatch(s->s.contains("Se retiro")),"limpieza anuncia retiro a OP cercano");
        floor(world,Material.MAGMA_BLOCK);cmd("visita MerchantOne");check(active()==null,"rechaza suelo peligroso");
        floor(world,Material.STONE);first.setGameMode(GameMode.SURVIVAL);second.setGameMode(GameMode.CREATIVE);set("next",Bukkit.getCurrentTick());call("tick",new Class[]{});
        check(active()!=null,"temporizador natural sigue creando visita survival");cmd("irse");
    }
}
