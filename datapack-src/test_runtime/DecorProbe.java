package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.event.block.Action;
import org.bukkit.block.BlockFace;
import kr.toxicity.model.api.BetterModel;
import io.lumine.mythic.bukkit.MythicBukkit;
import io.lumine.mythic.api.skills.placeholders.PlaceholderString;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.CraftServer;
import org.bukkit.craftbukkit.CraftWorld;
import com.mojang.authlib.GameProfile;

public final class DecorProbe extends JavaPlugin {
    Player player; int failures;
    void check(boolean ok,String detail) { if(!ok) failures++; getLogger().info("DECOR "+(ok?"PASS ":"FAIL ")+detail); }
    void cmd(String s) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(),s); }
    void buildFlag(boolean allow) {
        var platform=com.sk89q.worldguard.WorldGuard.getInstance().getPlatform();
        var manager=platform.getRegionContainer().get(com.sk89q.worldedit.bukkit.BukkitAdapter.adapt(player.getWorld()));
        var region=manager.getRegion("__global__");
        if(region==null) {region=new com.sk89q.worldguard.protection.regions.GlobalProtectedRegion("__global__");manager.addRegion(region);}
        region.setFlag(com.sk89q.worldguard.protection.flags.Flags.BUILD,allow?com.sk89q.worldguard.protection.flags.StateFlag.State.ALLOW:com.sk89q.worldguard.protection.flags.StateFlag.State.DENY);
        platform.getSessionManager().resetState(com.sk89q.worldguard.bukkit.WorldGuardPlugin.inst().wrapPlayer(player));
        // Solo la prueba alterna OP dos veces en el mismo tick; invalidar su cache de permisos.
        try {
            var f=com.sk89q.worldguard.session.AbstractSessionManager.class.getDeclaredField("bypassCache");f.setAccessible(true);
            ((com.google.common.cache.Cache<?,?>)f.get(platform.getSessionManager())).invalidateAll();
        } catch(Exception ex) {throw new RuntimeException(ex);}
    }
    ItemStack item(String model) { var i=new ItemStack(Material.PAPER);var m=i.getItemMeta();m.setItemModel(NamespacedKey.fromString("astral:"+model));i.setItemMeta(m);return i; }
    List<Interaction> plush() { return player.getWorld().getEntitiesByClass(Interaction.class).stream().filter(e->e.getPersistentDataContainer().has(new NamespacedKey("astraldecor","item"))).toList(); }
    void click(org.bukkit.block.Block floor) { var e=new PlayerInteractEvent(player,Action.RIGHT_CLICK_BLOCK,player.getInventory().getItemInMainHand(),floor,BlockFace.UP,EquipmentSlot.HAND); Bukkit.getPluginManager().callEvent(e); }
    public boolean onCommand(CommandSender sender,Command command,String label,String[] args) {
      try {
        if(args[0].equals("player")) {
                var server=((CraftServer)Bukkit.getServer()).getServer();
                var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
                var other=Bukkit.createWorld(new WorldCreator("urgente_mascotas").type(WorldType.FLAT).generateStructures(false));
                for(var bw:List.of(world.getWorld(),other)) {
                    bw.getChunkAt(0,0).setForceLoaded(true);bw.getChunkAt(1,0).setForceLoaded(true);
                    for(int x=-32;x<=64;x++)for(int z=-32;z<=32;z++) {
                        bw.getBlockAt(x,-61,z).setType(Material.STONE);
                        for(int y=-60;y<=-56;y++)bw.getBlockAt(x,y,z).setType(Material.AIR);
                    }
                }
                var profile=new GameProfile(UUID.randomUUID(),"AstralProbe");
                var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
                var connection=new Connection(PacketFlow.SERVERBOUND);
                connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
                connection.channel.pipeline().addLast("packet_handler",connection);
                connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
                fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
                fake.setPos(0,-60,0);
                world.addNewPlayer(fake);
                var list=server.getPlayerList();
                list.players.add(fake);
                for(String name:List.of("playersByUUID","playersByName")) {
                    var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(name);field.setAccessible(true);
                    ((Map)field.get(list)).put(name.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
                }
                player=fake.getBukkitEntity();player.setOp(true);
                for(Entity old:player.getWorld().getEntities())if(old.getScoreboardTags().contains("decor.migrate")) {
                    String uuid=old.getPersistentDataContainer().get(new NamespacedKey("astraldecor","display"),org.bukkit.persistence.PersistentDataType.STRING);
                    if(uuid!=null) {Entity d=Bukkit.getEntity(UUID.fromString(uuid));if(d!=null)d.remove();}old.remove();
                }
                player.setInvulnerable(true);
                MythicBukkit.inst().getPlayerManager().loadProfile(player);
                kr.toxicity.model.api.BetterModel.platform().playerManager().player(
                    kr.toxicity.model.api.bukkit.platform.BukkitAdapter.adapt(player));
                player.teleport(new Location(Bukkit.getWorlds().getFirst(),0,-60,0));

        } else if(args[0].equals("npc")) {
            var api=MythicBukkit.inst().getAPIHelper();
            var e=api.spawnMythicMob("astral_npc_expediciones",new Location(player.getWorld(),5,-60,5));
            e.addScoreboardTag("decor.restart");
            var registry=BetterModel.registryOrNull(e.getUniqueId()); if(registry!=null) registry.close();
            Bukkit.getScheduler().runTaskLater(this,()-> {
              var reg=BetterModel.registryOrNull(e.getUniqueId()); check(reg!=null && reg.trackers().size()==1,"modelo recuperado sin duplicados");
              if(reg!=null) for(var t:reg.trackers())for(var b:t.bones())if(b.getNametag()!=null) try {
                var f=b.getNametag().getClass().getDeclaredField("alwaysVisible"); f.setAccessible(true);check(f.getBoolean(b.getNametag()),"nombre siempre visible en BetterModel");
              } catch(Exception ex) { check(false,"inspeccion nombre "+ex.getClass().getSimpleName()); }
              if(reg!=null) reg.spawn(kr.toxicity.model.api.bukkit.platform.BukkitAdapter.adapt(player));
              e.teleport(new Location(player.getWorld(),8,-60,8));
              Bukkit.getScheduler().runTaskLater(this,()-> {
                var registryMoved=BetterModel.registryOrNull(e.getUniqueId());
                if(registryMoved!=null)for(var t:registryMoved.trackers())for(var b:t.bones())if(b.getNametag()!=null)try {
                    var f=b.getNametag().getClass().getDeclaredField("location");f.setAccessible(true);
                    var pos=(kr.toxicity.model.api.platform.PlatformLocation)f.get(b.getNametag());
                    check(Math.abs(t.location().x()-8)<.1 && Math.abs(t.location().z()-8)<.1,"tracker sigue tp sin duplicar modelo");
                    getLogger().info("DECOR nametag location="+pos+" tracker="+t.location());
                } catch(Exception ex) {check(false,"inspeccion nombre movido");}
              },10);
            },65);
            int index=0;
            for(String mid:List.of("astral_npc_tienda","astral_maquina_arcade","astral_maquina_capsulas","astral_npc_venta","astral_npc_mina","astral_mina_guia")) {
                var npc=api.spawnMythicMob(mid,new Location(player.getWorld(),10+index++,-60,10));npc.addScoreboardTag("decor.restart");
                var existing=BetterModel.registryOrNull(npc.getUniqueId());if(existing!=null)existing.close();
                Bukkit.getScheduler().runTaskLater(this,()-> {
                    var reg=BetterModel.registryOrNull(npc.getUniqueId());check(reg!=null && reg.trackers().size()==1,"modelo recuperado "+mid);
                    if(reg!=null)for(var t:reg.trackers())for(var b:t.bones())if(b.getNametag()!=null) try {
                        var f=b.getNametag().getClass().getDeclaredField("alwaysVisible");f.setAccessible(true);
                        check(f.getBoolean(b.getNametag())!=mid.equals("astral_npc_mina"),"visibilidad nombre "+mid);
                    } catch(Exception ex) { check(false,"inspeccion nombre "+mid); }
                },65);
            }
        } else if(args[0].equals("combat")) {
            Location back=player.getLocation();
            World arena=Bukkit.getWorld("yeti_combat");
            if(arena==null)arena=Bukkit.createWorld(new WorldCreator("yeti_combat").type(WorldType.FLAT).generateStructures(false));
            cmd("execute in minecraft:yeti_combat run gamerule minecraft:spawn_mobs false");
            player.teleport(new Location(arena,0,-60,0));
            player.addScoreboardTag("astral.caster");
            cmd("data modify storage astral:tmp spell set value {dmg:1}");
            for(int cx=1;cx<=4;cx++)for(int cz=-6;cz<=3;cz++)player.getWorld().getChunkAt(cx,cz).setForceLoaded(true);
            for(int x=25;x<=55;x++)for(int z=-90;z<=40;z++)player.getWorld().getBlockAt(x,-61,z).setType(Material.STONE);
            List<LivingEntity> targets=new ArrayList<>();
            targets.add(player.getWorld().spawn(new Location(player.getWorld(),40,-60,0),Zombie.class));
            targets.add((LivingEntity)MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_esq_arquero",new Location(player.getWorld(),40,-60,10)));
            targets.add((LivingEntity)MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_cumbre_yeti",new Location(player.getWorld(),40,-60,20)));
            targets.add(player.getWorld().spawn(new Location(player.getWorld(),40,-60,30),TropicalFish.class));
            targets.add(player.getWorld().spawn(new Location(player.getWorld(),40,-60,-10),CaveSpider.class));
            int bossIndex=0;
            for(String mid:List.of("astral_momia","astral_golem_forja","astral_mina_guardian","astral_yeti_ancestral"))
                targets.add((LivingEntity)MythicBukkit.inst().getAPIHelper().spawnMythicMob(mid,new Location(player.getWorld(),40,-60,-20-20*bossIndex++)));
            Bukkit.getScheduler().runTaskLater(this,()-> {
                try {
                    int targetIndex=0;
                    for(LivingEntity target:targets) {
                        var box=target.getBoundingBox();
                        // Apuntar al cuerpo visible, no al espacio sobrante por el escalado uniforme.
                        double visibleHeight=getConfig().getDoubleList("probe-heights").get(targetIndex++);
                        getLogger().info("DECOR BOX "+target.getType()+" "+box);
                        if(target.getType()==EntityType.RAVAGER)check(box.getWidthX()>8 && box.getHeight()>7,"caja real del Yeti cubre modelo completo");
                        for(double distance:new double[]{1.5,18})for(double fraction:new double[]{.02,.5,.98}) {
                            target.setHealth(target.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue());
                            double before=target.getHealth();target.setNoDamageTicks(0);
                            double y=box.getMinY()+visibleHeight*fraction;
                            cmd("scoreboard players set #steps astral.tmp 0");
                            cmd("execute in "+target.getWorld().getKey()+" positioned "+(box.getMaxX()+distance)+" "+y+" "+target.getZ()+" rotated 90 0 run function astral:spell/ray");
                            check(target.getHealth()<before,"baston caja "+target.getType()+" altura="+fraction+" distancia="+distance);
                        }
                        // Ray tracing de Paper usa la misma caja para melee y proyectiles.
                        for(double fraction:new double[]{.02,.5,.98}) {
                            var start=new Location(target.getWorld(),box.getMinX()-2,box.getMinY()+visibleHeight*fraction,target.getZ());
                            var hit=target.getWorld().rayTraceEntities(start,new org.bukkit.util.Vector(1,0,0),box.getWidthX()+4,e->e==target);
                            check(hit!=null && hit.getHitEntity()==target,"rayo melee/flecha "+target.getType()+" altura="+fraction);
                        }
                        target.remove();
                    }
                } catch(Exception ex) {check(false,"combat exception "+ex);}
                finally {targets.forEach(Entity::remove);player.removeScoreboardTag("astral.caster");player.teleport(back);}
            },20);
        } else if(args[0].equals("restart")) {
            var mobs=MythicBukkit.inst().getMobManager().getActiveMobs().stream().filter(m->m.getEntity().getBukkitEntity().getScoreboardTags().contains("decor.restart")).toList();
            check(!mobs.isEmpty(),"NPC persistio al reiniciar");
            for(var m:mobs) { var reg=BetterModel.registryOrNull(m.getUniqueId());check(reg!=null && reg.trackers().size()==1,"NPC modelado tras reinicio"); }
            int migrated=0;
            for(World w:Bukkit.getWorlds())for(Interaction h:w.getEntitiesByClass(Interaction.class)) {
                if(!h.getScoreboardTags().contains("decor.migrate"))continue;
                migrated++;
                var uuid=h.getPersistentDataContainer().get(new NamespacedKey("astraldecor","display"),org.bukkit.persistence.PersistentDataType.STRING);
                var d=(ItemDisplay)Bukkit.getEntity(UUID.fromString(uuid));
                check(d!=null && d.getItemDisplayTransform()==ItemDisplay.ItemDisplayTransform.NONE,"peluche antiguo reparado al cargar");
                check(h.getScoreboardTags().contains("astral.plush.upright.v2"),"migracion persistida sin perder item");
            }
            check(migrated==6,"seis peluches conservados al reiniciar");
        } else if(args[0].equals("wings")) {
            player.getInventory().setChestplate(new ItemStack(Material.DIAMOND_CHESTPLATE));
            player.getInventory().setItemInOffHand(item("asura_alas"));
            Bukkit.getScheduler().runTaskLater(this,()-> {
              var v=player.getPassengers().stream().filter(e->e.getScoreboardTags().contains("astral.wings")).toList();
              check(v.size()==1,"alas pasajero unico");check(player.getInventory().getChestplate().getType()==Material.DIAMOND_CHESTPLATE,"alas con pechera");
              if(!v.isEmpty()) { var d=(ItemDisplay)v.getFirst();check(d.getTransformation().getTranslation().z<0,"offset detras del cuerpo yaw cero");
                check(Math.abs(d.getY()+d.getTransformation().getTranslation().y-player.getY()-1.45)<.05,"alas a altura real de hombros"); }
              player.setBodyYaw(90);player.setSneaking(true);
              Bukkit.getScheduler().runTaskLater(this,()-> {
                var ds=player.getPassengers().stream().filter(e->e.getScoreboardTags().contains("astral.wings")).toList();
                if(!ds.isEmpty()) {var d=(ItemDisplay)ds.getFirst();check(d.getTransformation().getTranslation().x>0.3,"alas siguen body yaw 90");
                    check(Math.abs(d.getY()+d.getTransformation().getTranslation().y-player.getY()-1.2)<.05,"alas bajan al agacharse sin duplicar offset");}
                player.getInventory().setItemInOffHand(null);
                Bukkit.getScheduler().runTaskLater(this,()->check(player.getPassengers().stream().noneMatch(e->e.getScoreboardTags().contains("astral.wings")),"alas retiradas sin objeto duplicado"),5);
              },5);
            },5);
        } else if(args[0].equals("plush")) {
            check(Bukkit.getPluginManager().isPluginEnabled("WorldGuard"),"WorldGuard instalado y activo");
            player.setOp(false);player.setSneaking(false); player.getInventory().setItemInMainHand(item("peluche_alex"));
            var floor=player.getWorld().getBlockAt(0,-61,0);floor.setType(Material.STONE);
            buildFlag(false);
            click(floor);check(plush().isEmpty() && player.getInventory().getItemInMainHand().getAmount()==1,"WG deniega sin consumir");
            buildFlag(true);
            // Recorrer tambien el camino vanilla, no solo eventos sinteticos.
            var handle=((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle();
            handle.gameMode.useItemOn(handle,handle.level(),handle.getMainHandItem(),net.minecraft.world.InteractionHand.MAIN_HAND,
                new net.minecraft.world.phys.BlockHitResult(new net.minecraft.world.phys.Vec3(.5,-60,.5),net.minecraft.core.Direction.UP,new net.minecraft.core.BlockPos(0,-61,0),false));
            check(plush().size()==1,"clic nativo Paper con objeto paper sin uso vanilla");
            for(var h:plush()) Bukkit.getPluginManager().callEvent(new io.papermc.paper.event.player.PrePlayerAttackEntityEvent(player,h,false));
            for(var mode:List.of(GameMode.SURVIVAL,GameMode.CREATIVE)) for(var mat:List.of(Material.STONE,Material.STONE_SLAB,Material.WHITE_CARPET)) {
              player.setGameMode(mode);
              floor.setType(mat);player.getInventory().setItemInMainHand(item("peluche_alex"));
              click(floor);check(plush().size()==1,"colocar sobre "+mat+" "+mode);
              if(!plush().isEmpty()) {var h=plush().getFirst();check(h.getLocation().getY()<-59.9,"altura superficie "+h.getLocation().getY());
                Bukkit.getPluginManager().callEvent(new io.papermc.paper.event.player.PrePlayerAttackEntityEvent(player,h,false));
                check(plush().isEmpty(),"recoger una vez "+mat);
                Bukkit.getPluginManager().callEvent(new io.papermc.paper.event.player.PrePlayerAttackEntityEvent(player,h,false));
                check(player.getInventory().getItemInMainHand().getAmount()==1,"devolucion unica "+mode);
              }
            }
            floor.setType(Material.STONE);player.setOp(true);buildFlag(false);
            player.getInventory().setItemInMainHand(item("peluche_alex"));click(floor);check(plush().size()==1,"OP respeta bypass WG para decorar");
            for(var h:plush()) Bukkit.getPluginManager().callEvent(new io.papermc.paper.event.player.PrePlayerAttackEntityEvent(player,h,false));
            buildFlag(true);
            floor.setType(Material.STONE);
            int idx=0;
            for(String id:List.of("alex","creaking","ocelot","steve","tropical_fish","zombie_horse")) {
                var f=player.getWorld().getBlockAt(3+idx++*2,-61,0);f.setType(Material.STONE);
                player.getInventory().setItemInMainHand(item("peluche_"+id));click(f);
                Interaction h=plush().stream().filter(v->Math.abs(v.getX()-f.getX()-.5)<.01).findFirst().orElseThrow();
                String uuid=h.getPersistentDataContainer().get(new NamespacedKey("astraldecor","display"),org.bukkit.persistence.PersistentDataType.STRING);
                var d=(ItemDisplay)Bukkit.getEntity(UUID.fromString(uuid));
                check(d.getItemDisplayTransform()==ItemDisplay.ItemDisplayTransform.NONE,"transformacion neutra "+id);
                check(h.getInteractionHeight()>0 && h.getInteractionHeight()<=.801,"altura caja "+id);
                check(d.getLocation().getDirection().dot(player.getLocation().subtract(d.getLocation()).toVector().normalize())<0,"frente -Z mira al jugador "+id);
                // Persistir el formato anterior para probar la migracion en el segundo arranque.
                d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
                h.removeScoreboardTag("astral.plush.upright.v2");h.addScoreboardTag("decor.migrate");
            }
            World lobby=Bukkit.getWorld("lobby");if(lobby==null)lobby=Bukkit.createWorld(new WorldCreator("lobby").type(WorldType.FLAT).generateStructures(false));
            Location back=player.getLocation();player.teleport(new Location(lobby,0,-60,0));player.setOp(true);
            var lobbyFloor=lobby.getBlockAt(0,-61,0);lobbyFloor.setType(Material.STONE);
            player.getInventory().setItemInMainHand(item("peluche_alex"));click(lobbyFloor);
            check(plush().isEmpty() && player.getInventory().getItemInMainHand().getAmount()==1,"lobby bloqueado incluso OP sin consumir");
            player.teleport(back);
        } else if(args[0].equals("result")) { getLogger().info("DECOR RESULT failures="+failures); }
      } catch(Exception ex) {failures++;getLogger().log(java.util.logging.Level.SEVERE,"DECOR FAIL exception",ex);}
      return true;
    }
}
