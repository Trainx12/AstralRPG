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
    Player a,b,c; int failures; Location initialHead;
    @Override public void onEnable() {
        // En remoto lo carga Multiverse. El ensayo solo carga su lobby sintetico.
        if(Bukkit.getWorld("lobby")==null)Bukkit.createWorld(new WorldCreator("lobby").type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));
        if(((JavaPlugin)plugin()).getConfig().getBoolean("enabled"))awaitReady();
    }
    void awaitReady() {
        new org.bukkit.scheduler.BukkitRunnable() {
            int ticks;
            public void run() {
                try {
                    if(train()!=null && train().size()==3 && !(boolean)field("recovering")) {
                        getLogger().info("TRAIN READY");cancel();
                    } else if(++ticks>1200) {check(false,"tiempo de creacion agotado");cancel();}
                } catch(Exception e) {check(false,"esperando creacion: "+e);cancel();}
            }
        }.runTaskTimer(this,1,1);
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
        p.teleport(new Location(Bukkit.getWorld("lobby"),118.5,99,193.5));
        check(train().get(seat).addPassengerForced(p),"subir "+p.getName()+" asiento "+seat);
    }
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command cmd,String label,String[] args){
      try {
        switch(args[0]) {
        case "setup" -> {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astraltren apagar");
            var w=Bukkit.getWorld("lobby");if(w==null)w=Bukkit.createWorld(new WorldCreator("lobby").type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));
            for(int x=117;x<=123;x++)for(int z=175;z<=211;z++) {
                w.getBlockAt(x,98,z).setType(Material.STONE_BRICKS);
                for(int y=99;y<=104;y++)w.getBlockAt(x,y,z).setType(Material.AIR);
            }
            for(int z=178;z<=208;z++) {
                var block=w.getBlockAt(120,99,z);block.setType(Material.RAIL);
                var rail=(Rail)block.getBlockData();rail.setShape(Rail.Shape.NORTH_SOUTH);block.setBlockData(rail);
            }
            for(int x=117;x<=123;x++)for(int y=99;y<=104;y++)for(int z:List.of(175,211))w.getBlockAt(x,y,z).setType(Material.BLACK_CONCRETE);
            Bukkit.getWorld("world").setSpawnLocation(0,65,0);
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astraltren fijar 120 99 193 SOUTH");
            a=fake("TrainA");b=fake("TrainB");c=fake("TrainC");
            awaitReady();
        }
        case "ready" -> {
            var source=new com.bergerkiller.bukkit.common.config.FileConfiguration(new java.io.File(((JavaPlugin)plugin()).getDataFolder(),"train.yml"));source.load();
            var spawnable=com.bergerkiller.bukkit.tc.controller.spawnable.SpawnableGroup.fromConfig(source);
            for(int i=0;i<=12000;i++) {
                double offset=-11.175613+i*.001;
                var locations=spawnable.findSpawnLocations(new Location(Bukkit.getWorld("lobby"),120.5,99,193.5+offset),new org.bukkit.util.Vector(0,0,1),com.bergerkiller.bukkit.tc.controller.spawnable.SpawnableGroup.SpawnMode.CENTER);
                if(locations!=null) {getLogger().info("TRAIN SPAWN nearestOffset="+offset+" geometricTail="+(193.5+offset-(4.89375+2*3.6275125)/2));break;}
            }
            if(train()==null) {check(false,"spawn completo requerido");return true;}
            check(train()!=null && train().size()==3,"locomotora y dos vagones");
            initialHead=train().head().getEntity().getEntity().getLocation();
            double tail=train().tail().getEntity().getEntity().getLocation().getZ()-3.6275125/2;
            getLogger().info("TRAIN GEOMETRY tail="+tail+" gap="+(tail-176)+" head="+train().head().getEntity().getEntity().getLocation().getZ());
            check(tail>=177.99 && tail<=178.51,"cola en spawn valido mas cercano al muro norte");
            check(train().tail().getEntity().getEntity().getLocation().getZ()>=178,"ultimo coche sobre primer riel");
            check(!(boolean)field("moving") && (int)field("state")==0 && train().getAverageForce()<.001,"tren completo quieto al aparecer");
            var cfg=plugin().getClass().getDeclaredMethod("cfg",String.class,double.class);cfg.setAccessible(true);
            var config=((JavaPlugin)plugin()).getConfig();
            config.set("viaje.velocidad",.01);config.set("viaje.espera",99);config.set("viaje.teleport",2);config.set("viaje.salida",0);
            check((double)cfg.invoke(plugin(),"velocidad",0d)==.16 && (double)cfg.invoke(plugin(),"espera",0d)==3,"JAR prevalece sobre config vieja");
            config.set("viaje.manual",true);
            check((double)cfg.invoke(plugin(),"velocidad",0d)==.01 && (double)cfg.invoke(plugin(),"espera",0d)==99,"manual true habilita valores del administrador");
            config.set("viaje.manual",false);
            check(!a.hasPermission("astraltren.admin"),"administracion denegada a jugador normal");
            var model=train().get(1).getProperties().getConfig().getNode("model");
            var item=model.getNodeList("attachments").getFirst().get("item",org.bukkit.inventory.ItemStack.class);
            check(item.getItemMeta().getItemModel().toString().equals("astral:tren_head"),"componente item_model moderno (vagon bajo)");
            var loco=train().get(0).getProperties().getConfig().getNode("model").getNodeList("attachments").getFirst().get("item",org.bukkit.inventory.ItemStack.class);
            check(loco.getItemMeta().getItemModel().toString().equals("astral:tren_cart"),"locomotora con chimenea adelante");
            check(train().head().getEntity().getEntity().getLocation().getZ()>train().tail().getEntity().getEntity().getLocation().getZ(),"locomotora al sur");
        }
        case "recreate" -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astraltren recrear");
        case "one" -> {a.setRespawnLocation(null,true);board(a,1);}
        case "countdown" -> {check(!(boolean)field("moving") && (int)field("wait")>0,"cuenta regresiva espera al grupo");}
        case "arrived" -> {
            check(a.getWorld().getName().equals("world") && a.getLocation().distance(Bukkit.getWorld("world").getSpawnLocation())<2,"sin cama llega al spawn survival");
            check(train()!=null && !train().hasPassenger(),"tren repuesto vacio");
            double d=(double)field("lastDistance");
            check(Math.abs(d-15.053125)<.001,"frente llega al muro sur: z="+(193.5+d+4.89375/2));
            check((int)field("state")==0 && !(boolean)field("moving"),"reaparece quieto en espera sin regreso vacio");
        }
        case "three" -> {
            var w=Bukkit.getWorld("world");
            for(int x=8;x<=13;x++)for(int z=8;z<=13;z++)w.getBlockAt(x,64,z).setType(Material.STONE);
            var foot=w.getBlockAt(10,65,10);foot.setType(Material.RED_BED,false);
            var f=(org.bukkit.block.data.type.Bed)foot.getBlockData();f.setFacing(org.bukkit.block.BlockFace.NORTH);f.setPart(org.bukkit.block.data.type.Bed.Part.FOOT);foot.setBlockData(f,false);
            var head=w.getBlockAt(10,65,9);head.setType(Material.RED_BED,false);var h=(org.bukkit.block.data.type.Bed)head.getBlockData();h.setFacing(org.bukkit.block.BlockFace.NORTH);h.setPart(org.bukkit.block.data.type.Bed.Part.HEAD);head.setBlockData(h,false);
            a.setRespawnLocation(head.getLocation(),false);b.setRespawnLocation(null,true);c.setRespawnLocation(null,true);
            board(a,1);board(b,1);board(c,2);
            check(train().hasPlayerPassenger(),"tres jugadores abordados");
        }
        case "exit" -> {c.leaveVehicle();c.teleport(new Location(Bukkit.getWorld("lobby"),118.5,99,193.5));}
        case "twoarrived" -> {
            check(a.getWorld().getName().equals("world") && a.getLocation().distance(new Location(Bukkit.getWorld("world"),10,65,9))<4,"cama survival respetada");
            check(b.getWorld().getName().equals("world"),"segundo pasajero transferido");
            check(c.getWorld().getName().equals("lobby") && !c.isInsideVehicle(),"quien baja queda en lobby");
        }
        case "back" -> {
            check((int)field("state")==0 && !(boolean)field("moving"),"frena en el anden y espera");
            check(train().head().getEntity().getEntity().getLocation().distance(initialHead)<.01,"queda junto al muro como al principio: "+train().head().getEntity().getEntity().getLocation());
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
            check(train()!=null && train().size()==3 && !train().hasPassenger(),"reinicio recupera unico tren vacio");
            getLogger().info("TRAIN POSITION actual="+train().head().getEntity().getEntity().getLocation()+" initial="+field("start"));
            check(Bukkit.getWorld("lobby").getEntitiesByClass(Minecart.class).size()==3,"sin vagones duplicados tras recuperar");
            check(train().head().getEntity().getEntity().getLocation().distance((Location)field("start"))<.1,"reinicio en estacion");
        }
        case "result" -> getLogger().info("TRAIN RESULT failures="+failures);
        }
      }catch(Throwable e){failures++;getLogger().severe("TRAIN FAIL "+e);e.printStackTrace();}
      return true;
    }
}
