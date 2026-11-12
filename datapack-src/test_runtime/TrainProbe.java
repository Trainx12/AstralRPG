package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.block.data.Rail;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
import com.bergerkiller.bukkit.tc.controller.MinecartGroup;

/** Ensayo NMS de estado servidor: no simula render ni clientes conectados. */
public final class TrainProbe extends JavaPlugin {
    Player a,b,c; int failures;
    @Override public void onEnable() {
        // En remoto lo carga Multiverse. El ensayo solo carga su lobby sintetico.
        if(Bukkit.getWorld("lobby")==null)Bukkit.createWorld(new WorldCreator("lobby").type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));
    }
    Object plugin() {return Bukkit.getPluginManager().getPlugin("AstralTrain");}
    Object field(String key)throws Exception {var f=plugin().getClass().getDeclaredField(key);f.setAccessible(true);return f.get(plugin());}
    MinecartGroup train()throws Exception {return (MinecartGroup)field("train");}
    void check(boolean ok,String s){if(!ok)failures++;getLogger().info("TRAIN "+(ok?"PASS ":"FAIL ")+s);}
    Player fake(String name)throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();var w=((CraftWorld)Bukkit.getWorld("lobby")).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),name);var fake=new ServerPlayer(server,w,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        fake.setPos(2.5,81,0.5);w.addNewPlayer(fake);var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }
    void board(Player p,int seat)throws Exception {
        p.teleport(new Location(Bukkit.getWorld("lobby"),2.5,81,.5));
        check(train().get(seat).addPassengerForced(p),"subir "+p.getName()+" asiento "+seat);
    }
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command cmd,String label,String[] args){
      try {
        switch(args[0]) {
        case "setup" -> {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astraltren apagar");
            var w=Bukkit.getWorld("lobby");if(w==null)w=Bukkit.createWorld(new WorldCreator("lobby").type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));
            for(int x=-3;x<=3;x++)for(int z=-16;z<=16;z++) {
                w.getBlockAt(x,80,z).setType(Material.STONE_BRICKS);
                for(int y=81;y<=86;y++)w.getBlockAt(x,y,z).setType(Material.AIR);
            }
            for(int z=-14;z<=14;z++) {
                var block=w.getBlockAt(0,81,z);block.setType(Material.RAIL);
                var rail=(Rail)block.getBlockData();rail.setShape(Rail.Shape.NORTH_SOUTH);block.setBlockData(rail);
            }
            Bukkit.getWorld("world").setSpawnLocation(0,65,0);
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astraltren fijar 0 81 0 NORTH");
            a=fake("TrainA");b=fake("TrainB");c=fake("TrainC");
        }
        case "ready" -> {
            check(train()!=null && train().size()==4,"locomotora y tres vagones");
            check(!a.hasPermission("astraltren.admin"),"administracion denegada a jugador normal");
            var model=train().get(1).getProperties().getConfig().getNode("model");
            var item=model.getNodeList("attachments").getFirst().get("item",org.bukkit.inventory.ItemStack.class);
            check(item.getItemMeta().getItemModel().toString().equals("astral:tren_cart"),"componente item_model moderno");
            check(train().head().getEntity().getEntity().getLocation().getZ()<train().tail().getEntity().getEntity().getLocation().getZ(),"locomotora al norte");
        }
        case "one" -> {a.setRespawnLocation(null,true);board(a,1);}
        case "countdown" -> {check(!(boolean)field("moving") && (int)field("wait")>0,"cuenta regresiva espera al grupo");}
        case "arrived" -> {
            check(a.getWorld().getName().equals("world") && a.getLocation().distance(Bukkit.getWorld("world").getSpawnLocation())<2,"sin cama llega al spawn survival");
            check(train()!=null && !train().hasPassenger() && !(boolean)field("moving"),"tren repuesto vacio");
            check((double)field("lastDistance")>=8 && (double)field("lastDistance")<8.4,"recorrido de ocho bloques");
        }
        case "three" -> {
            var w=Bukkit.getWorld("world");
            for(int x=8;x<=13;x++)for(int z=8;z<=13;z++)w.getBlockAt(x,64,z).setType(Material.STONE);
            var foot=w.getBlockAt(10,65,10);foot.setType(Material.RED_BED,false);
            var f=(org.bukkit.block.data.type.Bed)foot.getBlockData();f.setFacing(org.bukkit.block.BlockFace.NORTH);f.setPart(org.bukkit.block.data.type.Bed.Part.FOOT);foot.setBlockData(f,false);
            var head=w.getBlockAt(10,65,9);head.setType(Material.RED_BED,false);var h=(org.bukkit.block.data.type.Bed)head.getBlockData();h.setFacing(org.bukkit.block.BlockFace.NORTH);h.setPart(org.bukkit.block.data.type.Bed.Part.HEAD);head.setBlockData(h,false);
            a.setRespawnLocation(head.getLocation(),false);b.setRespawnLocation(null,true);c.setRespawnLocation(null,true);
            board(a,1);board(b,2);board(c,3);
            check(train().hasPlayerPassenger(),"tres jugadores abordados");
        }
        case "exit" -> {c.leaveVehicle();c.teleport(new Location(Bukkit.getWorld("lobby"),2.5,81,.5));}
        case "twoarrived" -> {
            check(a.getWorld().getName().equals("world") && a.getLocation().distance(new Location(Bukkit.getWorld("world"),10,65,9))<4,"cama survival respetada");
            check(b.getWorld().getName().equals("world"),"segundo pasajero transferido");
            check(c.getWorld().getName().equals("lobby") && !c.isInsideVehicle(),"quien baja queda en lobby");
        }
        case "allarrived" -> {check(List.of(a,b,c).stream().allMatch(p->p.getWorld().getName().equals("world")),"tres pasajeros transferidos juntos");}
        case "invalidbed" -> {
            Bukkit.getWorld("world").getBlockAt(10,65,9).setType(Material.AIR);
            Bukkit.getWorld("world").getBlockAt(10,65,10).setType(Material.AIR);
            var m=plugin().getClass().getDeclaredMethod("destination",Player.class);m.setAccessible(true);
            var destination=(Location)m.invoke(plugin(),a);
            check(destination.distance(Bukkit.getWorld("world").getSpawnLocation())<2,"cama rota vuelve al spawn");
        }
        case "outside" -> {check((boolean)field("moving"),"reinicio con tren en movimiento");}
        case "persist" -> {
            check((boolean)field("moving"),"corte abrupto con tren afuera");
            ((com.bergerkiller.bukkit.tc.TrainCarts)Bukkit.getPluginManager().getPlugin("Train_Carts")).save(com.bergerkiller.bukkit.tc.TrainCarts.SaveMode.COMMAND);
            Bukkit.savePlayers();Bukkit.getWorld("lobby").save();
        }
        case "recovered" -> {
            check(train()!=null && train().size()==4 && !train().hasPassenger(),"reinicio recupera unico tren vacio");
            getLogger().info("TRAIN POSITION actual="+train().head().getEntity().getEntity().getLocation()+" initial="+field("start"));
            check(Bukkit.getWorld("lobby").getEntitiesByClass(Minecart.class).size()==4,"sin vagones duplicados tras recuperar");
            check(train().head().getEntity().getEntity().getLocation().distance((Location)field("start"))<.1,"reinicio en estacion");
        }
        case "result" -> getLogger().info("TRAIN RESULT failures="+failures);
        }
      }catch(Throwable e){failures++;getLogger().severe("TRAIN FAIL "+e);e.printStackTrace();}
      return true;
    }
}
