package astraltest;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.command.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.*;
import com.mojang.authlib.GameProfile;
public final class SpellProbe extends JavaPlugin implements Listener {
    Player player; int checks,failures,impacts,rays; double rayLength; final List<LivingEntity> mobs=new ArrayList<>();
    final Map<UUID,Double> damage=new HashMap<>(); final Map<UUID,Integer> counts=new HashMap<>();
    void check(boolean ok,String s){checks++;if(!ok)failures++;getLogger().info("SPELL "+(ok?"PASS ":"FAIL ")+s);}
    void cmd(String s){Bukkit.dispatchCommand(Bukkit.getConsoleSender(),s);}
    public void onEnable(){Bukkit.getPluginManager().registerEvents(this,this);}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void damage(EntityDamageByEntityEvent e){
        if(e.getDamager()==player) {damage.put(e.getEntity().getUniqueId(),e.getDamage());counts.merge(e.getEntity().getUniqueId(),1,Integer::sum);}
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void marker(EntitySpawnEvent e){
        var tags=e.getEntity().getScoreboardTags();
        if(tags.contains("fx.estallido"))impacts++;
        if(tags.contains("fx.rayo")) {
            rays++;
            for(String t:tags)if(t.startsWith("fxlen."))rayLength=Double.parseDouble(t.substring(6));
        }
        if(e.getEntity().getScoreboardTags().contains("astral.spell.perfora"))
            for(var target:e.getEntity().getWorld().getLivingEntities())
                if(target.getScoreboardTags().stream().anyMatch(t->t.startsWith("astral.spell.hit")))
                    getLogger().info("SPELL TARGET "+target.getType()+" "+target.getLocation()+" "+target.getScoreboardTags());
    }
    Player fake(World w) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();var world=((CraftWorld)w).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),"SpellProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);
        var ch=(io.netty.channel.embedded.EmbeddedChannel)connection.channel;
        Bukkit.getScheduler().runTaskTimer(this,()->ch.releaseOutbound(),1,1);
        return p;
    }

    public boolean onCommand(CommandSender sender,Command command,String label,String[] args) {
      try {
        if(args[0].equals("setup")) {
          World w=Bukkit.getWorlds().getFirst();player=fake(w);player.setGameMode(GameMode.ADVENTURE);
          w.getChunkAt(0,0).setForceLoaded(true);w.getChunkAt(0,1).setForceLoaded(true);
          for(int x=-2;x<=2;x++)for(int z=-2;z<=28;z++)w.getBlockAt(x,99,z).setType(Material.STONE);
        } else if(args[0].equals("case")) trial(args[1],Integer.parseInt(args[2]));
        else if(args[0].equals("result")) getLogger().info("SPELL RESULT checks="+checks+" failures="+failures);
      } catch(Throwable e){check(false,e.toString());e.printStackTrace();}
      return true;
    }
    void trial(String mode,int tier) {
      for(var e:mobs)e.remove();mobs.clear();damage.clear();counts.clear();impacts=0;rays=0;rayLength=-1;
      World w=player.getWorld();player.teleport(new Location(w,0,100,0,0,0));
      // Cada repeticion usa exclusivamente sus cuatro objetivos; el mundo del probe persiste.
      for(var e:w.getLivingEntities())if(!(e instanceof Player))e.remove();
      for(int y=100;y<=103;y++)w.getBlockAt(0,y,5).setType(mode.equals("wall")?Material.STONE:Material.AIR);
      for(int n=0;n<4;n++) {
        var mob=w.spawn(new Location(w,0,100,3+n*3),Zombie.class,e->{
          e.setAdult();
          e.setGravity(false);e.getAttribute(org.bukkit.attribute.Attribute.MOVEMENT_SPEED).setBaseValue(0);
          e.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).setBaseValue(100000000);e.setHealth(100000000);
          e.setRemoveWhenFarAway(false);e.setSilent(true);
        });mobs.add(mob);
      }
      if(mode.equals("pet"))mobs.getFirst().addScoreboardTag("astral.pet");
      if(mode.equals("noai"))mobs.getFirst().setAI(false);
      if(mode.equals("invulnerable"))mobs.getFirst().setInvulnerable(true);
      if(mode.equals("owned")) {
        mobs.getFirst().remove();var wolf=w.spawn(new Location(w,0,100,3),Wolf.class);wolf.setOwner(player);mobs.set(0,wolf);
      }
      cmd("loot replace entity SpellProbe weapon.mainhand loot astral:item/baston_"+tier);
      cmd("scoreboard players set SpellProbe astral.cd 0");
      cmd("scoreboard players set SpellProbe astral.fx "+(mode.equals("low")?0:1));
      cmd("scoreboard players set SpellProbe astral.fx.bastones "+(mode.equals("off")?0:1));
      cmd("execute as SpellProbe at @s run function astral:spell/cast");
      Bukkit.getScheduler().runTaskLater(this,()->{
      var objective=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp");
      double base=objective.getScore("#base").getScore()*objective.getScore("#sk").getScore();
      boolean protectedFirst=Set.of("pet","invulnerable","owned").contains(mode);
      for(int n=0;n<4;n++) {
        int index=protectedFirst?n-1:n; double expected=(index<0||index>2||mode.equals("wall")&&n>0)?0:base*(index==0?1:.7);
        double actual=damage.getOrDefault(mobs.get(n).getUniqueId(),0.0);
        check(Math.abs(actual-expected)<Math.max(.01,expected*.0001),mode+" T"+tier+" mob"+n+" actual="+actual+" expected="+expected);
        check(counts.getOrDefault(mobs.get(n).getUniqueId(),0)==(expected>0?1:0),"unico evento "+n);
      }
      check(base>0,"hechizo emitido T"+tier);
      if(mode.equals("off")||mode.equals("low")) {
        check(rays==0 && impacts==0,"interruptor/nivel sin efectos nuevos");
      } else {
        check(rays==1 && rayLength>=0,"rayo con longitud explicita");
        check(impacts==(mode.equals("wall")?2:3),"un estallido por impacto y pared");
        double endpoint=mode.equals("wall")?4.2:protectedFirst?10.45:7.45;
        check(Math.abs(rayLength-endpoint)<.01,"extremo visual real "+rayLength+" expected="+endpoint);
      }
      check(w.getEntities().stream().noneMatch(e->e.getScoreboardTags().stream().anyMatch(t->t.startsWith("astral.spell.hit")||t.equals("astral.caster")||t.equals("astral.spell.perfora"))),"limpieza tags "+mode);
      },2);
    }
}
