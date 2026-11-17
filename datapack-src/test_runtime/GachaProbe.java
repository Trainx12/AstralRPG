package astraltest;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.persistence.PersistentDataType;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
import com.badbones69.crazycrates.paper.CrazyCrates;
public final class GachaProbe extends JavaPlugin {
 Player player;int failures,total,expected,model,initial,limit;boolean pityMode,lucky;String mode,gid;Map<String,Integer> counts=new TreeMap<>();
 ArrayDeque<String[]> cases=new ArrayDeque<>();
 void cmd(String s){Bukkit.dispatchCommand(Bukkit.getConsoleSender(),s);}
 void check(boolean ok,String text){if(!ok)failures++;getLogger().info("GACHA "+(ok?"PASS ":"FAIL ")+text);}
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("AstralGachaProbe".getBytes()),"GachaProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        var embedded=(io.netty.channel.embedded.EmbeddedChannel)connection.channel;
        Bukkit.getScheduler().runTaskTimer(this,()->{
            Object packet;
            while((packet=embedded.readOutbound())!=null)io.netty.util.ReferenceCountUtil.release(packet);
        },1,1);
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

 public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
  try {
   if(args[0].equals("start")) {
    player=fake();player.setOp(true);player.setGameMode(GameMode.ADVENTURE);
    if(args.length<2)for(String name:List.of("gacha_rpg","gacha_monturas","gacha_cosmeticos"))for(String luck:List.of("","_suerte"))for(String m:List.of("force","mass"))cases.add(new String[]{name+luck,m,"1000","0"});
    for(String name:List.of("gacha_rpg","gacha_monturas","gacha_cosmeticos")) {
     int n=name.equals("gacha_rpg")?50:name.equals("gacha_monturas")?40:20;
     for(String lucky:List.of("false","true"))for(int t:List.of(10,25,50))for(int start:List.of(0,n-1,n))cases.add(new String[]{name,"pity",String.valueOf(t),String.valueOf(start),lucky});
    }
    cases.add(new String[]{"gacha_rpg","recovery","10","0","false"});
    preview(0);return true;
   }
   if(args[0].equals("reward")) {
    total++;String rarity=args[2];counts.merge(rarity,1,Integer::sum);
    if(pityMode) {
     boolean guarantee=model+1>=limit;
     check(args.length>3 && args[3].equals(gid+(guarantee?"_garantia":"")+(lucky?"_suerte":"")),"caja exacta y snapshot en premio "+total);
     if(guarantee)check(rarity.equals("epic")||rarity.equals("legendary"),"garantia en premio "+total);
     model=(rarity.equals("epic")||rarity.equals("legendary"))?0:model+1;
     Bukkit.getScheduler().runTask(this,()->{
      int real=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("pity_"+gid.substring(6)).getScore(player.getName()).getScore();
      check(real==model,"pity premio "+total+" = "+real+" esperado "+model);
     });
    }
    if(total==expected)Bukkit.getScheduler().runTaskLater(this,()->{
     getLogger().info("GACHA COUNTS "+gid+" "+mode+" n="+total+" initial="+initial+" final="+model+" "+counts);
     next();
    },4);
    else if(mode.equals("force"))Bukkit.getScheduler().runTaskLater(this,this::force,2);
    return true;
   }
  }catch(Exception ex){failures++;ex.printStackTrace();getLogger().info("GACHA RESULT failures="+failures);}
  return true;
 }
 void preview(int index) {
  var names=List.of("gacha_rpg","gacha_monturas","gacha_cosmeticos");
  if(index==names.size()) {
   player.setOp(false);player.addAttachment(this,"crazycrates.massopen",true);
   player.performCommand("crates");
   Bukkit.getScheduler().runTaskLater(this,()->{
    check(player.getOpenInventory().getTopInventory().getSize()==5,"/crates no abre menu a jugador");next();
   },5);return;
  }
  String name=names.get(index);
  var board=Bukkit.getScoreboardManager().getMainScoreboard();
  if(board.getObjective("pity_"+name.substring(6))==null)cmd("scoreboard objectives add pity_"+name.substring(6)+" dummy");
  CrazyCrates.getPlugin().getPlatform().getCrateManager().getCrateFromName(name).getPreview(player).open();
  Bukkit.getScheduler().runTaskLater(this,()->{
   var inv=player.getOpenInventory().getTopInventory();
   check(inv.getSize()>=27 && Arrays.stream(inv.getContents()).anyMatch(Objects::nonNull),"vitrina real con premios: "+name);
   check(Arrays.stream(inv.getContents()).filter(Objects::nonNull).noneMatch(i->i.getType()==Material.COMPASS),"preview sin Menu: "+name);
   player.closeInventory();preview(index+1);
  },5);
 }
 void force(){cmd("crates forceopen "+gid+" GachaProbe");}
 void next() {
  if(cases.isEmpty()){getLogger().info("GACHA RESULT failures="+failures);cmd("tick rate 20");return;}
  var c=cases.remove();gid=c[0];mode=c[1];expected=Integer.parseInt(c[2]);initial=Integer.parseInt(c[3]);model=initial;total=0;counts.clear();pityMode=mode.equals("pity")||mode.equals("recovery");
  player.getInventory().clear();
  getLogger().info("GACHA CASE "+Arrays.toString(c));
  if(pityMode){
   limit=gid.equals("gacha_rpg")?50:gid.equals("gacha_monturas")?40:20;
   cmd("scoreboard players set GachaProbe pity_"+gid.substring(6)+" "+initial);
   lucky=Boolean.parseBoolean(c[4]);
   player.getPersistentDataContainer().set(new NamespacedKey("astral","suerte_hasta"),PersistentDataType.LONG,lucky?System.currentTimeMillis()+36000000:0L);
   if(mode.equals("recovery")) {
    player.getPersistentDataContainer().set(new NamespacedKey("astral","gacha_pending"),PersistentDataType.STRING,gid+",10,false,false");
    player.getPersistentDataContainer().set(new NamespacedKey("astral","gacha_flight"),PersistentDataType.STRING,gid+",0");
    cmd("scoreboard players set GachaProbe pity_rpg 1");
   }else cmd("astralgacha GachaProbe "+gid+" "+expected+" false");
   player.getPersistentDataContainer().set(new NamespacedKey("astral","suerte_hasta"),PersistentDataType.LONG,0L);
  }else if(mode.equals("force"))force();
  else {
   cmd("crates give virtual "+gid+" 1000 GachaProbe -s");
   for(int i=0;i<20;i++)player.performCommand("crates mass-open "+gid+" virtual 50");
  }
 }
}
