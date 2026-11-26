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
    Player fake(World w) throws Exception {return fake(w,"Mount"+UUID.randomUUID().toString().substring(0,8));}
    Player fake(World w,String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)w).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),name);
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
    void interact(org.bukkit.entity.Entity e){
        Bukkit.getPluginManager().callEvent(new PlayerInteractEntityEvent(player,e,org.bukkit.inventory.EquipmentSlot.HAND));
    }
    void modelClick(org.bukkit.entity.Entity e) {
        var registry=kr.toxicity.model.api.BetterModel.registryOrNull(e.getUniqueId());
        check(registry!=null && !registry.hitBoxes().isEmpty(),"modelo tiene hitbox real: "+e.getScoreboardTags());
        var box=registry.hitBoxes().iterator().next();
        new kr.toxicity.model.api.event.hitbox.HitBoxInteractAtEvent(
            kr.toxicity.model.api.BetterModel.platform().adapter().player(player.getUniqueId()),box,
            kr.toxicity.model.api.nms.ModelInteractionHand.RIGHT,new org.joml.Vector3f()).call();
    }
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
        } else if(args[0].equals("clicks")) {
          int index=0;
          for(String id:List.of("astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto")) {
            later(1+index++*18,()->{
              var h=(org.bukkit.entity.AbstractHorse)spawn(id,player.getLocation().clone().add(1,0,0));
              later(5,()->{
                player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE,2));
                // Incluso si Mythic/otra proteccion cancelo previamente el evento.
                var event=new PlayerInteractAtEntityEvent(player,h,new org.bukkit.util.Vector(),org.bukkit.inventory.EquipmentSlot.HAND);
                event.setCancelled(true);Bukkit.getPluginManager().callEvent(event);
                modelClick(h);
                check(player.getInventory().getItemInMainHand().getAmount()==1,id+" clic duplicado consume una sola silla");
                check(h.isTamed() && h.getOwner().equals(player),id+" clic AtEntity reclama/domestica");
                double speed=h.getAttribute(org.bukkit.attribute.Attribute.MOVEMENT_SPEED).getBaseValue();
                double jump=h.getAttribute(org.bukkit.attribute.Attribute.JUMP_STRENGTH).getBaseValue();
                double expectedSpeed=switch(id){case "astral_grillo"->.24;case "astral_chocobo"->.38;case "astral_escarabajo"->.14;default->.22;};
                double expectedJump=switch(id){case "astral_grillo"->1.25;case "astral_chocobo"->.7;case "astral_escarabajo"->.45;default->.6;};
                check(Math.abs(speed-expectedSpeed)<.001 && Math.abs(jump-expectedJump)<.001,id+" velocidad/salto segun MOBS");
                later(1,()->{
                  player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));modelClick(h);
                  check(player.getVehicle()==h,id+" clic hitbox monta caballo nativo");
                  check(((org.bukkit.craftbukkit.entity.CraftAbstractHorse)h).getHandle().getControllingPassenger()==((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle(),id+" control nativo desde modelo");
                  player.leaveVehicle();
                  later(2,()->{check(!h.hasAI(),id+" quieta sin jinete");h.remove();});
                });
              });
            });
          }
        } else if(args[0].equals("legacy")) {
          var h=(org.bukkit.entity.AbstractHorse)spawn("astral_grillo",player.getLocation().clone().add(1,0,0));
          later(5,()->{
            h.setOwner(player);h.setTamed(false);h.addScoreboardTag("astral.ensillado");
            Bukkit.getPluginManager().callEvent(new org.bukkit.event.world.EntitiesLoadEvent(h.getChunk(),List.of(h)));
            check(h.isTamed() && h.getOwner().equals(player),"carga de entidad vieja restaura doma sin cambiar dueno");
            player.setGameMode(GameMode.CREATIVE);player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));
            interact(h);check(player.getVehicle()==h,"silla virtual vieja migra y permite montar en creativo");
            player.leaveVehicle();h.remove();
            later(1,()->{
              var fresh=(org.bukkit.entity.AbstractHorse)spawn("astral_grillo",player.getLocation().clone().add(1,0,0));
              later(5,()->{
                player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE));
                Bukkit.getPluginManager().callEvent(new PlayerInteractEntityEvent(player,fresh,org.bukkit.inventory.EquipmentSlot.OFF_HAND));
                check(fresh.getInventory().getSaddle()==null,"mano secundaria no ensilla");
                interact(fresh);check(player.getInventory().getItemInMainHand().getType()==Material.SADDLE,"creativo conserva silla al ensillar");
                fresh.remove();player.setGameMode(GameMode.SURVIVAL);
              });
            });
          });
        } else if(args[0].equals("flying")) {
          int index=0;
          for(String id:List.of("astral_ave","astral_pterodactilo")) {
            later(1+index++*30,()->{
              var e=spawn(id,player.getLocation().clone().add(1,0,0));
              later(6,()->{
                player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE,2));modelClick(e);
                check(e.getScoreboardTags().contains("astral.ensillado"),id+" ensilla por modelo");
                later(1,()->{
                  player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));modelClick(e);
                  later(2,()->{
                    var r=kr.toxicity.model.api.BetterModel.registryOrNull(e.getUniqueId());
                    check(player.isInsideVehicle() && r.hasControllingPassenger(),id+" asiento volador con conductor");
                    check(r.hitBoxes().stream().anyMatch(b->b.hasMountDriver() && b.mountController()==kr.toxicity.model.api.mount.MountControllers.FLY),id+" conserva controlador FLY");
                    player.leaveVehicle();e.remove();
                  });
                });
              });
            });
          }
        } else if(args[0].equals("lobby")) {
          World original=player.getWorld();Location before=player.getLocation();
          World lobby=Bukkit.getWorld("lobby");if(lobby==null)lobby=Bukkit.createWorld(new WorldCreator("lobby").generateStructures(false));
          player.teleport(new Location(lobby,0,100,0));player.setGameMode(GameMode.SURVIVAL);
          player.getInventory().clear();cmd("mm egg give "+player.getName()+" astral_grillo 2");
          later(2,()->{
            var item=player.getInventory().getItemInMainHand();int amount=item.getAmount();
            var block=player.getLocation().clone().add(0,-1,0).getBlock();block.setType(Material.STONE);
            Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(player,org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK,item,block,org.bukkit.block.BlockFace.UP,org.bukkit.inventory.EquipmentSlot.HAND));
            check(item.getAmount()==amount,"lobby conserva huevo sin consumirlo");
            check(player.getWorld().getEntitiesByClass(org.bukkit.entity.AbstractHorse.class).isEmpty(),"lobby no deja montura");
            Bukkit.getPluginManager().callEvent(new PlayerInteractEvent(player,org.bukkit.event.block.Action.RIGHT_CLICK_AIR,item,null,null,org.bukkit.inventory.EquipmentSlot.HAND));
            later(36,()->{
              int count=Arrays.stream(player.getInventory().getContents()).filter(it->it!=null && it.getType()==Material.PIG_SPAWN_EGG).mapToInt(org.bukkit.inventory.ItemStack::getAmount).sum();
              check(count==amount,"lobby devuelve un unico huevo lanzado al usuario exacto");
              player.teleport(before);
            });
          });
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
              check(horses.size()==1 && player.equals(horses.getFirst().getOwner()) && horses.getFirst().isTamed(),"huevo en creativo asigna UUID exacto sin buscar jugador cercano");
              try {
                Player other=fake(player.getWorld());other.teleport(player.getLocation());
                other.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE));
                Bukkit.getPluginManager().callEvent(new PlayerInteractEntityEvent(other,horses.getFirst(),org.bukkit.inventory.EquipmentSlot.HAND));
                check(horses.getFirst().getOwner().equals(player) && other.getInventory().getItemInMainHand().getType()==Material.SADDLE,"otro jugador no roba ni ensilla");
                ((org.bukkit.craftbukkit.entity.CraftPlayer)other).getHandle().connection.disconnect(net.minecraft.network.chat.Component.literal("fin"));
              } catch(Exception ex){throw new RuntimeException(ex);}
              horses.forEach(org.bukkit.entity.Entity::remove);
              player.setGameMode(GameMode.SURVIVAL);
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
          // El mundo de ensayo puede tener drops de una ejecucion anterior.
          at.getWorld().getNearbyEntities(at,5,5,5).stream().filter(e->e instanceof org.bukkit.entity.Item).forEach(org.bukkit.entity.Entity::remove);
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
        } else if(args[0].equals("modes")) {
          World room=Bukkit.getWorld("sala_dueno");if(room==null)room=Bukkit.createWorld(new WorldCreator("sala_dueno").type(WorldType.FLAT).generateStructures(false));
          player=fake(room,"ByTrainx");player.setGameMode(GameMode.SURVIVAL);
          World w=player.getWorld();
          for(int x=-12;x<=38;x++)for(int z=-12;z<=12;z++)w.getBlockAt(x,99,z).setType(Material.STONE);
          player.teleport(new Location(w,0,100,0));player.setSneaking(false);
          int index=0;
          for(String id:List.of("astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto","astral_ave","astral_pterodactilo")) {
            later(1+index++*30,()->{
              var e=spawn(id,player.getLocation().clone().add(1,0,0));e.setGravity(false);
              later(5,()->{
                var tag=new org.bukkit.inventory.ItemStack(Material.NAME_TAG,2);var meta=tag.getItemMeta();meta.setDisplayName("Amiga "+id);tag.setItemMeta(meta);
                player.getInventory().setItemInMainHand(tag);modelClick(e);
                var key=new NamespacedKey("astral","mount_name");var mode=new NamespacedKey("astral","mount_follow");
                check(player.getInventory().getItemInMainHand().getAmount()==1 && ("Amiga "+id).equals(e.getPersistentDataContainer().get(key,org.bukkit.persistence.PersistentDataType.STRING)),id+" etiqueta gasta una y guarda nombre");
                check(e.getPersistentDataContainer().get(mode,org.bukkit.persistence.PersistentDataType.BYTE)==1,id+" modo inicial seguir");
                check(w.getEntitiesByClass(org.bukkit.entity.TextDisplay.class).stream().anyMatch(t->("Amiga "+id).equals(t.getText())),id+" texto independiente del modelo");
                try {
                  Player other=fake(w);other.teleport(player.getLocation());other.setSneaking(true);other.getInventory().setItemInMainHand(tag.clone());
                  Bukkit.getPluginManager().callEvent(new PlayerInteractEntityEvent(other,e,org.bukkit.inventory.EquipmentSlot.HAND));
                  check(e.getPersistentDataContainer().get(mode,org.bukkit.persistence.PersistentDataType.BYTE)==1 && other.getInventory().getItemInMainHand().getAmount()==2,id+" tercero no nombra ni cambia modo");
                  ((org.bukkit.craftbukkit.entity.CraftPlayer)other).getHandle().connection.disconnect(net.minecraft.network.chat.Component.literal("fin"));
                }catch(Exception ex){throw new RuntimeException(ex);}
                later(1,()->{
                  player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));player.setSneaking(true);interact(e);player.setSneaking(false);
                  check(e.getPersistentDataContainer().get(mode,org.bukkit.persistence.PersistentDataType.BYTE)==0,id+" Shift cambia a quieta");
                  Location before=e.getLocation();
                  later(201,()->{
                    check(e.getLocation().distanceSquared(before)<.0001,id+" quieta 200 ticks");
                    var bytes=Bukkit.getUnsafe().serializeEntity(e);e.remove();
                    var restored=Bukkit.getUnsafe().deserializeEntity(bytes,w,true);
                    Bukkit.getPluginManager().callEvent(new org.bukkit.event.world.EntitiesLoadEvent(restored.getChunk(),List.of(restored)));
                    check(restored.getPersistentDataContainer().get(mode,org.bukkit.persistence.PersistentDataType.BYTE)==0 && ("Amiga "+id).equals(restored.getPersistentDataContainer().get(key,org.bukkit.persistence.PersistentDataType.STRING)),id+" nombre/modo conservados en NBT al restaurar");
                    restored.remove();
                  });
                });
              });
            });
          }
          later(380,()->{
            packets.stream().filter(p->p instanceof ClientboundSystemChatPacket).map(p->((ClientboundSystemChatPacket)p).content().getString()).filter(t->t.contains("se queda quieta.")).findAny().ifPresentOrElse(t->check(true,"aviso chat quieta"),()->check(false,"aviso chat quieta"));
          });
        } else if(args[0].equals("follow")) {
          player.teleport(new Location(player.getWorld(),0,100,0));player.setSneaking(false);
          var e=spawn("astral_chocobo",player.getLocation().clone().add(1,0,0));
          later(5,()->{
            player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE));interact(e);
            later(1,()->{
              e.teleport(new Location(player.getWorld(),10,100,0));double before=e.getLocation().distanceSquared(player.getLocation());
              later(80,()->{
                check(e.getLocation().distanceSquared(player.getLocation())<before,"seguir reduce distancia caminando");
                e.teleport(new Location(player.getWorld(),30,100,0));
                later(15,()->{
                  check(e.getLocation().distanceSquared(player.getLocation())<36,"seguir tp seguro a mas de 20 bloques");
                  player.setSneaking(true);player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.AIR));interact(e);
                  later(1,()->{
                    interact(e);player.setSneaking(false);
                    check(e.getPersistentDataContainer().get(new NamespacedKey("astral","mount_follow"),org.bukkit.persistence.PersistentDataType.BYTE)==1,"Shift vuelve a seguir");
                    packets.stream().filter(p->p instanceof ClientboundSystemChatPacket).map(p->((ClientboundSystemChatPacket)p).content().getString()).filter(t->t.contains("ahora te sigue.")).findAny().ifPresentOrElse(t->check(true,"aviso chat seguir"),()->check(false,"aviso chat seguir"));
                    later(1,()->{interact(e);check(player.getVehicle()==e,"clic normal aun monta en modo seguir");player.leaveVehicle();e.remove();});
                  });
                });
              });
            });
          });
        } else if(args[0].equals("followall")) {
          player.teleport(new Location(player.getWorld(),0,100,0));int index=0;
          for(String id:List.of("astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto","astral_ave","astral_pterodactilo")) {
            later(1+index++*35,()->{
              var e=spawn(id,player.getLocation().clone().add(1,0,0));
              later(5,()->{
                player.getInventory().setItemInMainHand(new org.bukkit.inventory.ItemStack(Material.SADDLE));interact(e);
                e.teleport(player.getLocation().clone().add(9,0,0));
                later(25,()->{
                  check(e.getLocation().distanceSquared(player.getLocation())<81,id+" se acerca al dueno");
                  e.teleport(player.getLocation().clone().add(30,0,0));
                  later(12,()->{check(e.getLocation().distanceSquared(player.getLocation())<36,id+" tp seguro sin cruzar mundo");e.remove();});
                });
              });
            });
          }
        } else if(args[0].equals("persist")) {
          World w=player.getWorld();Location at=new Location(w,328,100,328);w.getChunkAt(at);
          w.getBlockAt(328,99,328).setType(Material.STONE);
          var e=spawn("astral_grillo",at);UUID uuid=e.getUniqueId();
          var mode=new NamespacedKey("astral","mount_follow");var name=new NamespacedKey("astral","mount_name");
          later(5,()->{
            e.getPersistentDataContainer().set(mode,org.bukkit.persistence.PersistentDataType.BYTE,(byte)0);
            e.getPersistentDataContainer().set(name,org.bukkit.persistence.PersistentDataType.STRING,"Persistente");
            e.getPersistentDataContainer().set(new NamespacedKey("astral","mount_owner"),org.bukkit.persistence.PersistentDataType.STRING,player.getUniqueId().toString());
            w.save();w.unloadChunk(20,20,true);
            later(30,()->{
              check(!w.isChunkLoaded(20,20),"chunk realmente descargado");w.getChunkAt(20,20).setForceLoaded(true);
              later(20,()->{
                var restored=Bukkit.getEntity(uuid);check(restored!=null,"montura recuperada del chunk");
                if(restored!=null){check(restored.getPersistentDataContainer().get(mode,org.bukkit.persistence.PersistentDataType.BYTE)==0 && "Persistente".equals(restored.getPersistentDataContainer().get(name,org.bukkit.persistence.PersistentDataType.STRING)),"nombre/modo sobreviven descarga real");restored.remove();}w.getChunkAt(20,20).setForceLoaded(false);
              });
            });
          });
        } else if(args[0].equals("result"))getLogger().info("MOUNT RESULT failures="+failures);
      }catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"MOUNT FAIL",ex);}
      if(!args[0].equals("result")) {
        String step=args[0];int ticks=switch(step){case "modes"->400;case "follow"->140;case "followall"->240;case "persist"->80;default->100;};
        later(ticks,()->getLogger().info("MOUNT STEP "+step+" DONE"));
      }
      return true;
    }
}
