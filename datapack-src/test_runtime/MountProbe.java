package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.event.*;
import org.bukkit.event.player.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.*;
import net.minecraft.network.protocol.game.*;
import com.mojang.authlib.GameProfile;

/** Solo ensayo local: captura en el listener NMS, sin cliente visual. */
public final class MountProbe extends JavaPlugin implements Listener {
    Player player; World expectedWorld; Location origin; int failures; boolean cancel; int charges,refunds;
    final List<Packet<?>> packets=new ArrayList<>();
    void check(boolean ok,String msg){if(!ok)failures++;getLogger().info("MOUNT "+(ok?"PASS ":"FAIL ")+msg);}
    Player fake(World w) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)w).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),"MountProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false)) {
            @Override public void send(Packet<?> packet){packets.add(packet);}
            @Override public void send(Packet<?> packet,io.netty.channel.ChannelFutureListener listener){packets.add(packet);}
        };
        w.getChunkAt(0,0).setForceLoaded(true);fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);
            ((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }

    void cmd(String s){Bukkit.dispatchCommand(Bukkit.getConsoleSender(),s);}
    org.bukkit.entity.Entity spawn(String id,Location at) {
        try{return io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob(id,at);}
        catch(Exception ex){throw new RuntimeException(ex);}
    }
    void later(long ticks,Runnable r){Bukkit.getScheduler().runTaskLater(this,()->{try{r.run();}catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"MOUNT FAIL",ex);}},ticks);}
    void interact(org.bukkit.entity.Entity e){cmd("astralmount "+e.getUniqueId()+" "+player.getUniqueId());}
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
      try {
        if(player==null){player=fake(Bukkit.getWorlds().getFirst());player.setGameMode(GameMode.SURVIVAL);}
        if(args[0].equals("mounts")) {
          String[] ids={"astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto"};
          for(int i=0;i<ids.length;i++) {final String id=ids[i];
            later(1+i*15,()->{
              var horse=(org.bukkit.entity.AbstractHorse)spawn(id,player.getLocation().clone().add(1,0,0));
              later(4,()->{
                check(horse.isTamed(),id+" domado al aparecer");
                player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE,2));interact(horse);
                check(horse.getOwner().getUniqueId().equals(player.getUniqueId()),id+" dueno UUID exacto");
                check(player.getInventory().getItemInMainHand().getAmount()==1,id+" consume una silla");
                check(horse.getInventory().getSaddle().getType()==Material.SADDLE,id+" silla real");
                later(1,()->{
                  player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));interact(horse);
                  check(player.getVehicle()==horse,id+" asiento nativo");
                  var nativeHorse=((org.bukkit.craftbukkit.entity.CraftAbstractHorse)horse).getHandle();
                  check(nativeHorse.getControllingPassenger()==((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle(),id+" jinete tiene control");
                  player.leaveVehicle();horse.remove();
                });
              });
            });
          }
        } else if(args[0].equals("eggs")) {
          player.setGameMode(GameMode.CREATIVE);
          player.getInventory().clear();cmd("mm egg give "+player.getName()+" astral_grillo 2");
          later(3,()->{
            var item=Arrays.stream(player.getInventory().getContents()).filter(it->it!=null && it.getType()==Material.PIG_SPAWN_EGG).findFirst().orElseThrow();
            player.getInventory().setItemInMainHand(item);
            var block=player.getLocation().clone().add(0,-1,0).getBlock();block.setType(Material.STONE);
            Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(player,org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK,item,block,org.bukkit.block.BlockFace.UP,org.bukkit.inventory.EquipmentSlot.HAND));
            later(5,()->{
              var horses=player.getWorld().getEntitiesByClass(org.bukkit.entity.AbstractHorse.class).stream().filter(h->h.getScoreboardTags().contains("astral_grillo")).toList();
              check(horses.size()==1 && player.equals(horses.getFirst().getOwner()),"huevo en creativo asigna UUID exacto sin buscar jugador cercano");
              horses.forEach(org.bukkit.entity.Entity::remove);
              Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(player,org.bukkit.event.block.Action.RIGHT_CLICK_AIR,item,null,null,org.bukkit.inventory.EquipmentSlot.HAND));
              later(32,()->{
                var air=player.getWorld().getEntitiesByClass(org.bukkit.entity.AbstractHorse.class).stream().filter(h->h.getScoreboardTags().contains("astral_grillo")).toList();
                check(air.size()==1 && player.equals(air.getFirst().getOwner()),"huevo lanzado conserva UUID exacto");
                air.forEach(org.bukkit.entity.Entity::remove);player.setGameMode(GameMode.SURVIVAL);
              });
            });
          });
        } else if(args[0].equals("saddle")) {
          Location at=player.getLocation().clone().add(3,0,0);
          var horse=(org.bukkit.entity.AbstractHorse)spawn("astral_grillo",at);
          horse.setGravity(false);
          later(4,()->{
            horse.getInventory().setSaddle(new org.bukkit.inventory.ItemStack(Material.SADDLE));
            horse.addScoreboardTag("astral.ensillado");horse.setHealth(0);
            later(2,()->{
              int saddles=at.getWorld().getNearbyEntities(at,4,4,4).stream()
                .filter(e->e instanceof org.bukkit.entity.Item i && i.getItemStack().getType()==Material.SADDLE)
                .mapToInt(e->((org.bukkit.entity.Item)e).getItemStack().getAmount()).sum();
              check(saddles==1,"muerte devuelve exactamente una silla: "+saddles);
            });
          });
        } else if(args[0].equals("hostiles")) {
          player.setInvulnerable(false);player.setHealth(player.getMaxHealth());
          cmd("scoreboard players set "+player.getName()+" astral.wt 3");
          World w=player.getWorld();Location at=player.getLocation();
          for(int x=-6;x<=6;x++)for(int z=-6;z<=6;z++)w.getBlockAt(x,99,z).setType(Material.STONE);
          player.teleport(new Location(w,0,100,0));
          for(String id:List.of("astral_mapache","astral_pinguino")) {
            var mob=(org.bukkit.entity.Mob)io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob(id,player.getLocation().clone().add(id.equals("astral_mapache")?3:0,0,id.equals("astral_pinguino")?3:0));
            later(70,()->{
              check(mob.getScoreboardTags().stream().anyMatch(t->t.startsWith("astral.mt")),id+" tier aplicado");
              check(player.equals(mob.getTarget()),id+" persigue jugador sin provocacion");
              mob.remove();
            });
          }
        } else if(args[0].equals("swim")) {
          World w=player.getWorld();
          var vectorMethod=Class.forName("astral.AstralMounts").getDeclaredMethod("swimVector",org.bukkit.Input.class,Location.class);
          vectorMethod.setAccessible(true);
          var inputPlayer=((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle();
          inputPlayer.setLastClientInput(new net.minecraft.world.entity.player.Input(false,false,false,true,false,false,false));
          var right=(org.bukkit.util.Vector)vectorMethod.invoke(null,player.getCurrentInput(),new Location(w,0,100,0,0,0));
          check(right.getX()<-.64 && Math.abs(right.getZ())<.001,"D desplaza a la derecha de la mirada");
          inputPlayer.setLastClientInput(new net.minecraft.world.entity.player.Input(false,false,true,false,false,false,false));
          var left=(org.bukkit.util.Vector)vectorMethod.invoke(null,player.getCurrentInput(),new Location(w,0,100,0,0,0));
          check(left.getX()>.64 && Math.abs(left.getZ())<.001,"A desplaza a la izquierda de la mirada");
          inputPlayer.setLastClientInput(net.minecraft.world.entity.player.Input.EMPTY);
          for(int x=-4;x<=35;x++)for(int z=-4;z<=4;z++)for(int y=95;y<=105;y++)w.getBlockAt(x,y,z).setType(Material.WATER);
          player.teleport(new Location(w,0,100,0,-90,0));
          var horse=(org.bukkit.entity.AbstractHorse)io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_lagarto",player.getLocation());
          later(4,()->{
            player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE));interact(horse);
            later(1,()->{
              player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));interact(horse);
              var fake=((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle();
              fake.setLastClientInput(new net.minecraft.world.entity.player.Input(true,false,false,false,false,false,false));
              Location start=horse.getLocation();
              later(30,()->{
                double distance=horse.getLocation().getX()-start.getX();
                check(player.getVehicle()==horse,"agua profunda conserva jinete");
                check(player.hasPotionEffect(org.bukkit.potion.PotionEffectType.WATER_BREATHING),"respiracion acuatica");
                getLogger().info("MOUNT DEBUG swim distance="+distance+" vel="+horse.getVelocity()+" input="+player.getCurrentInput()+" loc="+horse.getLocation()+" online="+player.isOnline());
                check(horse.getVelocity().length()>.6,"nado solicita mas de 0,6 bloques/tick");
                player.setRotation(-90,45);
                double initialY=horse.getLocation().getY();
                later(8,()->{
                  check(horse.getVelocity().getY()<-.2,"mirada abajo solicita descenso");
                  player.setRotation(-90,-45);double bottom=horse.getLocation().getY();
                  later(8,()->{
                    check(horse.getVelocity().getY()>.2,"mirada arriba solicita ascenso");
                    fake.setLastClientInput(net.minecraft.world.entity.player.Input.EMPTY);
                    player.leaveVehicle();horse.remove();
                  });
                });
              });
            });
          });
        } else if(args[0].equals("ice")) {
          getLogger().info("MOUNT DEBUG ice player="+Bukkit.getPlayer(player.getUniqueId())+" health="+player.getHealth()+" valid="+player.isValid());
          player.setFreezeTicks(0);cmd("astralchill "+player.getUniqueId());
          getLogger().info("MOUNT DEBUG chill command="+Bukkit.getPluginCommand("astralchill")+" ticks="+player.getFreezeTicks()+" effects="+player.getActivePotionEffects());
          later(1,()->{
            check(player.getFreezeTicks()>0 && player.getFreezeTicks()<=100,"congelado visual bajo umbral de dano");
            check(player.hasPotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS),"lentitud");
          });
          later(25,()->check(player.getFreezeTicks()==0,"congelado termina sin dano extra"));
        } else if(args[0].equals("statues")) {
          World w=player.getWorld();w.setDifficulty(Difficulty.PEACEFUL);
          var statues=new ArrayList<org.bukkit.entity.Entity>();
          for(String name:List.of("coloso_musgoso","chaman","momia","yeti","golem_forja")) {
            var e=spawn("astral_estatua_"+name,player.getLocation().clone().add(4,5,0));statues.add(e);
            check(e.getType()==org.bukkit.entity.EntityType.IRON_GOLEM,"estatua "+name+" base no hostil");
          }
          later(60,()->{
            for(var e:statues)check(e.isValid() && !e.isDead() && !((org.bukkit.entity.Mob)e).hasAI() && e.isInvulnerable() && !e.hasGravity(),"estatua persiste en pacifico sin IA/gravedad: "+e.getUniqueId());
            statues.forEach(org.bukkit.entity.Entity::remove);w.setDifficulty(Difficulty.NORMAL);
          });
        } else if(args[0].equals("result"))getLogger().info("MOUNT RESULT failures="+failures);
      }catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"MOUNT FAIL",ex);}
      return true;
    }
}
