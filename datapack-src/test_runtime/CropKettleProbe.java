package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.craftbukkit.*;
import org.bukkit.plugin.java.JavaPlugin;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Solo ensayo local; no se instala en el servidor remoto. */
public final class CropKettleProbe extends JavaPlugin {
    Player player; int failures;
    void cmd(String c) {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(),c);
    }
    void check(boolean ok, String text) { if(!ok) failures++; getLogger().info("CNK "+(ok?"PASS ":"FAIL ")+text); }
    void player() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("CNKProbe".getBytes()),"CNKProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        fake.setPos(0,65,0); world.addNewPlayer(fake);
        var list=server.getPlayerList(); list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        player=fake.getBukkitEntity();player.setInvulnerable(true);player.setGravity(false);
        player.getWorld().getChunkAt(0,0).setForceLoaded(true);
    }
    public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command command, String label, String[] args) {
        Bukkit.getScheduler().runTask(this, () -> step(args[0]));
        return true;
    }
    void step(String step) {
        try { switch(step) {
        case "player" -> player();
        case "setup" -> {
            var w=player.getWorld();
            w.setTime(1000);
            cmd("gamerule random_tick_speed 4096");
            cmd("data modify storage cnk:temp response set value 1b");
            cmd("setblock 4 63 0 farmland[moisture=7]");
            cmd("setblock 5 63 0 water");
            cmd("execute positioned 4 64 0 run function cnk:seeds/corn/place");
            cmd("data modify storage cnk:temp item_name set value {text:'Olla de prueba'}");
            cmd("execute positioned 0 64 0 run function cnk:cooking_pot/place");
            cmd("data modify block 0 64 0 Items set value [{Slot:0b,id:'minecraft:poisonous_potato',count:1,components:{'minecraft:custom_data':{cnk:{ingredient:{type:'dough'}}}}}]");
            check(w.getBlockAt(0,64,0).getType()==Material.HOPPER,"olla colocada por funcion real");
        }
        case "check" -> {
            var w=player.getWorld();
            check(w.getEntitiesByClass(Item.class).stream().anyMatch(e->e.getItemStack().getType()==Material.BREAD),"olla convierte masa en pan via ticks y consume ingrediente");
            check(((org.bukkit.block.Hopper)w.getBlockAt(0,64,0).getState()).getInventory().isEmpty(),"olla sin masa remanente");
            var crop=w.getEntitiesByClass(ItemDisplay.class).stream().filter(e->e.getScoreboardTags().contains("cnk.corn_crop")).findFirst();
            check(crop.isPresent(),"cultivo nuevo presente");
            var objective=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("cnk.age");
            int age=crop.isPresent()?objective.getScore(crop.get().getUniqueId().toString()).getScore():-1;
            check(age>0,"maiz crece con random ticks reales, edad="+age);
            check(Bukkit.getPluginManager().isPluginEnabled("Skript"),"Skript activo");
            check(Bukkit.getPluginManager().isPluginEnabled("MythicMobs"),"MythicMobs activo");
            check(Bukkit.getAdvancement(NamespacedKey.fromString("astral:join"))!=null,"Astral cargado");
            check(Bukkit.getAdvancement(NamespacedKey.fromString("cnk:block"))!=null,"CNK cargado con overlay 101.1");
            cmd("execute as CNKProbe if predicate astral_cnk:survival run say CNK PASS survival predicate");
            cmd("execute in minecraft:the_nether run forceload add 0 0");
            cmd("execute in minecraft:the_nether run summon marker 0 80 0 {Tags:['cnkprobe']}");
            cmd("execute in minecraft:the_nether as @e[type=marker,tag=cnkprobe] if predicate astral_cnk:survival run say CNK FAIL predicate nether");
            cmd("execute in minecraft:the_nether as @e[type=marker,tag=cnkprobe] unless predicate astral_cnk:survival run say CNK PASS nether excluido");
            cmd("gamerule random_tick_speed 3");
            getLogger().info("CNK RESULT failures="+failures);
        }
        case "cost" -> {
            // Microbenchmark del conjunto de entradas, con 1 jugador, 1 olla y 1 cultivo.
            // Incluye dispatch de comandos: cota local, no una medicion spark remota.
            String[] functions={"tick","tick_2","tick_5","tick_20","tick_50","tick_100","tick_1200"};
            int[] periods={1,2,5,20,50,100,1200}; double weighted=0;
            for(int j=0;j<functions.length;j++) {
                long start=System.nanoTime();
                for(int i=0;i<200;i++)cmd("function cnk:"+functions[j]);
                double ms=(System.nanoTime()-start)/1e6/200;
                weighted+=ms/periods[j];
                getLogger().info("CNK cost "+functions[j]+" ms/call="+ms);
            }
            getLogger().info("CNK cost weighted-ms/tick="+weighted+" entities="+player.getWorld().getEntityCount());
        }
        }} catch(Throwable ex) { failures++;getLogger().severe("CNK FAIL "+ex);ex.printStackTrace(); }
    }
}
