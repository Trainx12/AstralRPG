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
public final class BalanceProbe extends JavaPlugin implements org.bukkit.event.Listener {
    org.bukkit.entity.Snowball lastShot;
    public void onEnable(){Bukkit.getPluginManager().registerEvents(this,this);}
    @org.bukkit.event.EventHandler public void launch(org.bukkit.event.entity.ProjectileLaunchEvent e){if(e.getEntity() instanceof org.bukkit.entity.Snowball s)lastShot=s;}
    Player player;int failures;final List<String> crateCalls=new ArrayList<>();
    final NamespacedKey until=new NamespacedKey("astral","suerte_hasta");
    void check(boolean ok,String text){if(!ok)failures++;getLogger().info("BAL "+(ok?"PASS ":"FAIL ")+text);}
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("AstralBalanceProbe".getBytes()),"BalanceProbe");
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

    Object ocean(String method,Class<?>[] types,Object...args) throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralOceano");
        var m=plugin.getClass().getDeclaredMethod(method,types);m.setAccessible(true);return m.invoke(plugin,args);
    }
    double swim(boolean equipped,boolean sprint) throws Exception {
        var p=player;var n=((org.bukkit.craftbukkit.entity.CraftPlayer)p).getHandle();p.setSprinting(sprint);n.setOnGround(false);
        p.getInventory().setArmorContents(equipped?new ItemStack[]{item("agua_boots",1),item("agua_leggings",1),item("agua_chestplate",1),item("agua_helmet",1)}:new ItemStack[4]);
        var eq=net.minecraft.world.entity.LivingEntity.class.getDeclaredMethod("detectEquipmentUpdates");eq.setAccessible(true);eq.invoke(n);
        ocean("swimSpeed",new Class[]{Player.class,boolean.class},p,equipped);
        n.setSpeed((float)p.getAttribute(org.bukkit.attribute.Attribute.MOVEMENT_SPEED).getValue());
        n.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);n.setYRot(0);
        var travel=net.minecraft.world.entity.LivingEntity.class.getDeclaredMethod("travelInWater",net.minecraft.world.phys.Vec3.class,double.class,boolean.class,double.class);travel.setAccessible(true);
        for(int i=0;i<200;i++) {n.setPos(0,100,0);n.setOnGround(false);travel.invoke(n,new net.minecraft.world.phys.Vec3(0,0,1),0.,false,100.);}
        return p.getLocation().toVector().setY(0).length();
    }
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
      try {
        switch(args[0]) {
        case "start" -> {
            for(var mat:List.of(Material.IRON_SPEAR,Material.DIAMOND_SPEAR,Material.NETHERITE_SPEAR)) {
                var nativeItem=org.bukkit.craftbukkit.inventory.CraftItemStack.asNMSCopy(new ItemStack(mat));
                getLogger().info("BAL vanilla spear "+mat+" "+nativeItem.get(net.minecraft.core.component.DataComponents.ATTRIBUTE_MODIFIERS));
            }
            player=fake();player.getInventory().clear();player.setGameMode(GameMode.SURVIVAL);
            check(Bukkit.getPluginManager().isPluginEnabled("AstralDecor"),"runtime habilitado");
            check(Bukkit.getPluginManager().isPluginEnabled("AstralOceano"),"oceano habilitado");
        }
        case "swim" -> {
            for(boolean sprint:List.of(false,true)) {
                double normal=swim(false,sprint),boost=swim(true,sprint),ratio=boost/normal;
                check(Math.abs(ratio-1.5)<.005,"nado horizontal sprint="+sprint+" normal="+normal+" set="+boost+" ratio="+ratio);
            }
            player.setSprinting(false);player.teleport(new Location(player.getWorld(),0,100,0));
        }
        case "waterstart" -> {
            for(int x=-2;x<=2;x++)for(int y=99;y<=104;y++)for(int z=-2;z<=2;z++)player.getWorld().getBlockAt(x,y,z).setType(Material.WATER);
            ((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle().setPos(0,100,0);
            player.setVelocity(new org.bukkit.util.Vector());
            var fluid=net.minecraft.world.entity.Entity.class.getDeclaredMethod("updateFluidInteraction");fluid.setAccessible(true);fluid.invoke(((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle());
            getLogger().info("BAL waterstart pos="+player.getLocation()+" eyes="+player.getEyeLocation().getBlock().getType()+" under="+player.isUnderWater());
            player.getInventory().setArmorContents(new ItemStack[]{item("agua_boots",1),item("agua_leggings",1),item("agua_chestplate",1),item("agua_helmet",1)});
        }
        case "vision" -> {
            var handle=((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle();handle.baseTick();
            check(player.isUnderWater(),"jugador sumergido");
            ocean("waterSet",new Class[]{});
            check(player.hasPotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION),"vision bajo agua");
            handle.setPos(10,110,10);
            var fluid=net.minecraft.world.entity.Entity.class.getDeclaredMethod("updateFluidInteraction");fluid.setAccessible(true);fluid.invoke(handle);handle.baseTick();fluid.invoke(handle);handle.baseTick();
            ocean("waterSet",new Class[]{});
            check(!player.hasPotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION),"vision retirada al salir del agua");
            player.getInventory().setHelmet(null);ocean("waterSet",new Class[]{});
            check(!player.hasPotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION),"vision retirada al quitar pieza");
            player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION,1200,1,false,false,true));
            player.getInventory().setHelmet(item("agua_helmet",1));ocean("waterSet",new Class[]{});
            player.getInventory().setHelmet(null);ocean("waterSet",new Class[]{});
            check(player.getPotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION).getAmplifier()==1,"vision ajena conservada");
        }
        case "durability" -> {
            var it=item("berserker_5_chestplate",1);int sum=0;
            for(int i=0;i<200;i++) {
                var e=new org.bukkit.event.player.PlayerItemDamageEvent(player,it,250);Bukkit.getPluginManager().callEvent(e);
                if(!e.isCancelled())sum+=e.getDamage();
            }
            check(sum==200,"200 eventos de desgaste alto -> 200 puntos: "+sum);
            player.getInventory().setArmorContents(new ItemStack[]{item("berserker_5_boots",1),item("berserker_5_leggings",1),it,item("berserker_5_helmet",1)});
            var handle=((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle();handle.detectEquipmentUpdates();
            var mob=player.getWorld().spawn(player.getLocation().add(5,0,0),org.bukkit.entity.Zombie.class);mob.setAI(false);mob.addScoreboardTag("astral.mt5");
            player.setInvulnerable(false);
            double max=player.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue();
            for(int i=0;i<200;i++){player.setHealth(max);player.setNoDamageTicks(0);player.damage(1000,mob);}
            int wear=((org.bukkit.inventory.meta.Damageable)player.getInventory().getChestplate().getItemMeta()).getDamage();
            check(wear==200,"200 golpes reales T5 con set T5 -> desgaste "+wear);
            mob.remove();player.setInvulnerable(true);
            check(((org.bukkit.inventory.meta.Damageable)item("minero_helmet",1).getItemMeta()).getMaxDamage()>=2401,"oficios max_damage migrable");
        }
        case "asura" -> {
            player.getInventory().setItemInMainHand(item("asura_espada",1));
            var victim=player.getWorld().spawn(player.getLocation().add(5,0,0),org.bukkit.entity.Zombie.class);victim.setAI(false);
            for(int i=1;i<=4;i++) {
                var e=new org.bukkit.event.entity.EntityDamageByEntityEvent(player,victim,org.bukkit.event.entity.EntityDamageEvent.DamageCause.ENTITY_ATTACK,100);
                Bukkit.getPluginManager().callEvent(e);
                check(Math.abs(e.getDamage()-(i==4?150:100))<.01,"Asura golpe "+i+" dano="+e.getDamage());
            }
            victim.remove();
        }
        case "shot" -> {
            player.getInventory().setItemInMainHand(item("agua_espada",1));
            getLogger().info("BAL waterid="+ocean("astralId",new Class[]{ItemStack.class},player.getInventory().getItemInMainHand()));
            getLogger().info("BAL shot online="+player.isOnline()+" lookup="+(Bukkit.getPlayer(player.getUniqueId())!=null));
            check(Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"astralagua "+player.getUniqueId()),"comando de proyectil registrado");
        }
        case "shothit" -> {
            var shots=lastShot!=null && lastShot.getScoreboardTags().contains("astral.water_sword")?List.of(lastShot):List.<org.bukkit.entity.Snowball>of();
            check(shots.size()==1,"proyectil de agua creado");
            if(!shots.isEmpty()) {
                var victim=player.getWorld().spawn(player.getLocation().add(5,0,0),org.bukkit.entity.Zombie.class);
                var e=new org.bukkit.event.entity.EntityDamageByEntityEvent(shots.getFirst(),victim,org.bukkit.event.entity.EntityDamageEvent.DamageCause.PROJECTILE,0);
                Bukkit.getPluginManager().callEvent(e);check(e.getDamage()==3186,"proyectil dano real T3 -10%: "+e.getDamage());victim.remove();shots.getFirst().remove();
            }
        }
        case "arrows" -> {
            var world=player.getWorld();
            for(int x=-1;x<=12;x++)for(int y=99;y<=103;y++)for(int z=-1;z<=1;z++)world.getBlockAt(x,y,z).setType(Material.WATER);
            var a=world.spawnArrow(new Location(world,0,101,0),new org.bukkit.util.Vector(1,0,0),1,0);
            var air=world.spawnArrow(new Location(world,0,101,20),new org.bukkit.util.Vector(1,0,0),1,0);
            world.getChunkAt(0,1).setForceLoaded(true);
            a.setGravity(false);air.setGravity(false);
            a.setVelocity(new org.bukkit.util.Vector(1,0,0));air.setVelocity(new org.bukkit.util.Vector(1,0,0));
            var bow=item("agua_arco",1);
            Bukkit.getPluginManager().callEvent(new org.bukkit.event.entity.EntityShootBowEvent(player,bow,new ItemStack(Material.ARROW),a,EquipmentSlot.HAND,1,true));
            check(a.getScoreboardTags().contains("astral.water_arrow"),"flecha acuatica identificada");
            var nativeWater=((org.bukkit.craftbukkit.entity.CraftArrow)a).getHandle();
            var nativeAir=((org.bukkit.craftbukkit.entity.CraftArrow)air).getHandle();
            for(int i=0;i<6;i++) {
                ocean("waterArrowStart",new Class[]{com.destroystokyo.paper.event.server.ServerTickStartEvent.class},new Object[]{null});
                nativeWater.tick();nativeAir.tick();
                ocean("waterArrowTick",new Class[]{com.destroystokyo.paper.event.server.ServerTickEndEvent.class},new Object[]{null});
                getLogger().info("BAL arrow tick="+i+" water="+a.getVelocity()+" air="+air.getVelocity()+" positions="+a.getLocation().getX()+"/"+air.getLocation().getX());
            }
            double ratio=a.getVelocity().length()/air.getVelocity().length();
            check(Math.abs(ratio-1)<.001,"flecha agua/aire velocidad="+ratio);
            double distance=a.getLocation().getX()/air.getLocation().getX();check(Math.abs(distance-1)<.001,"flecha agua/aire distancia="+distance);
            check(a.getDamage()==air.getDamage(),"flecha agua/aire mismo dano base");a.remove();air.remove();
        }
        case "cleanup" -> {
            var copy=Bukkit.getWorld(NamespacedKey.fromString("minecraft:santuario_azeroth_2"));
            var at=new Location(copy,0,100,0);copy.getChunkAt(at).setForceLoaded(true);
            var drop=copy.dropItem(at,new ItemStack(Material.DIAMOND));
            var arrow=copy.spawn(at,org.bukkit.entity.Arrow.class);
            var display=copy.spawn(at,org.bukkit.entity.TextDisplay.class);
            var reward=copy.spawn(at,org.bukkit.entity.ArmorStand.class);
            var other=player.getWorld().dropItem(player.getLocation(),new ItemStack(Material.EMERALD));
            for(String type:List.of("item","arrow","spectral_arrow","trident","experience_orb"))Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute in minecraft:santuario_azeroth_2 run minecraft:kill @e[type=minecraft:"+type+",distance=0..]");
            Bukkit.getScheduler().runTaskLater(this,()->check(drop.isDead() && arrow.isDead(),"limpieza elimina items/flechas de copia"),2);
            check(display.isValid() && reward.isValid() && other.isValid(),"limpieza conserva display/recompensa y otro mundo");
            display.remove();reward.remove();other.remove();
            var a=player.getWorld().spawn(player.getLocation(),org.bukkit.entity.TextDisplay.class);a.addScoreboardTag("astral_rank_trainx");
            var b=copy.spawn(at,org.bukkit.entity.TextDisplay.class);b.addScoreboardTag("astral_rank_trainx");
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute as "+player.getUniqueId()+" at @s run minecraft:kill @e[type=text_display,tag=astral_rank_trainx,distance=0..]");
            Bukkit.getScheduler().runTaskLater(this,()->{check(a.isDead() && b.isValid(),"cartel local no borra el de Santuario");b.remove();},2);
        }
        case "result" -> getLogger().info("BAL RESULT failures="+failures);
        }
      }catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"BAL FAIL exception",ex);}
      return true;
    }
}
