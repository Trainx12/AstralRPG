package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.persistence.PersistentDataType;
import kr.toxicity.model.api.BetterModel;
import kr.toxicity.model.api.event.hitbox.HitBoxInteractAtEvent;
import kr.toxicity.model.api.nms.ModelInteractionHand;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.potion.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;
import io.lumine.mythic.bukkit.MythicBukkit;

/** Monta nativa: un solo asiento, silla y propietario persistentes en el caballo. */
final class AstralMounts implements Listener {
    private final JavaPlugin plugin;
    private final Map<UUID,Integer> chillUntil=new HashMap<>();
    private final Map<UUID,Integer> clicks=new HashMap<>();
    private static final Set<String> GROUND=Set.of("astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto");
    private static final Set<String> FLYING=Set.of("astral_ave","astral_pterodactilo");
    private final Set<UUID> horses=new HashSet<>();
    private final NamespacedKey ownerKey=new NamespacedKey("astral","mount_owner");
    private final NamespacedKey modeKey=new NamespacedKey("astral","mount_follow");
    private final NamespacedKey nameKey=new NamespacedKey("astral","mount_name");
    private final Set<UUID> mounts=new HashSet<>();
    private final Map<UUID,TextDisplay> labels=new HashMap<>();
    private final Set<UUID> controlledFlying=new HashSet<>();
    // Circuito privado: no se concede a otros OP ni a grupos con wildcard.
    private boolean enabled(Player p) {return p!=null && p.getName().equalsIgnoreCase("ByTrainx");}
    private Player owner(Entity e) {
        String value=e.getPersistentDataContainer().get(ownerKey,PersistentDataType.STRING);
        if(value==null && e instanceof Tameable t && t.getOwner()!=null)return Bukkit.getPlayer(t.getOwner().getUniqueId());
        try{return value==null?null:Bukkit.getPlayer(UUID.fromString(value));}catch(IllegalArgumentException ex){return null;}
    }
    private boolean following(Entity e) {return e.getPersistentDataContainer().getOrDefault(modeKey,PersistentDataType.BYTE,(byte)1)==1;}
    private boolean riding(Entity e) {
        if(!e.getPassengers().isEmpty())return true;
        var r=BetterModel.registryOrNull(e.getUniqueId());return r!=null && r.hasPassenger();
    }
    private boolean allowed(World w) {
        // Lista positiva: nunca lobby, minas, mazmorras, arenas ni otros mundos.
        return Set.of("world","world_nether","world_the_end","sala_dueno").contains(w.getName());
    }
    private void stop(Mob m) {m.getPathfinder().stopPathfinding();m.setAI(false);m.setVelocity(new Vector());}
    private Location safeNear(Player p) {
        Location at=p.getLocation();World w=p.getWorld();
        for(int radius=2;radius<=4;radius++)for(int dx=-radius;dx<=radius;dx++)for(int dz=-radius;dz<=radius;dz++) {
            if(Math.max(Math.abs(dx),Math.abs(dz))!=radius)continue;
            int x=at.getBlockX()+dx,z=at.getBlockZ()+dz;
            if(!w.isChunkLoaded(x>>4,z>>4))continue;
            for(int dy=1;dy>=-2;dy--) {
                Location target=new Location(w,x+.5,at.getBlockY()+dy,z+.5);
                if(!w.getWorldBorder().isInside(target))continue;
                boolean clear=true;
                for(int ox=-1;ox<=1;ox++)for(int oz=-1;oz<=1;oz++) {
                    var floor=w.getBlockAt(x+ox,target.getBlockY()-1,z+oz);
                    if(!floor.getType().isSolid() || Set.of(Material.MAGMA_BLOCK,Material.CACTUS,Material.CAMPFIRE,Material.SOUL_CAMPFIRE).contains(floor.getType()))clear=false;
                    for(int y=0;y<4;y++) {var b=w.getBlockAt(x+ox,target.getBlockY()+y,z+oz);if(!b.isPassable() || b.isLiquid() || b.getType()==Material.FIRE)clear=false;}
                }
                if(clear)return target;
            }
        }
        return null;
    }
    private void follow() {
        mounts.removeIf(id->{
            Entity e=Bukkit.getEntity(id);
            if(e==null || !e.isValid()) {controlledFlying.remove(id);TextDisplay text=labels.remove(id);if(text!=null)text.remove();return true;}
            Player p=owner(e);
            if(!(e instanceof Mob m) || riding(e))return false;
            if(!enabled(p) && !e.getPersistentDataContainer().has(modeKey))return false;
            if(e.getScoreboardTags().stream().anyMatch(FLYING::contains)) {
                e.setGravity(false);
                if(controlledFlying.add(id)) {Bukkit.getMobGoals().removeAllGoals(m);m.setTarget(null);}
            }
            if(!enabled(p) || !following(e) || !allowed(e.getWorld()) || p.getWorld()!=e.getWorld() || p.isDead() || p.getGameMode()==GameMode.SPECTATOR) {stop(m);return false;}
            double distance=e.getLocation().distanceSquared(p.getLocation());
            if(distance>400) {stop(m);Location target=safeNear(p);if(target!=null)e.teleport(target);}
            else if(distance>16) {
                m.setAI(true);
                if(e.getScoreboardTags().stream().anyMatch(FLYING::contains)) {
                    Vector direction=p.getLocation().add(0,1,0).toVector().subtract(e.getLocation().toVector());
                    e.setVelocity(direction.normalize().multiply(.25));
                } else m.getPathfinder().moveTo(p.getLocation(),1.1);
            } else stop(m);
            return false;
        });
    }
    private void label(Entity e) {
        String name=e.getPersistentDataContainer().get(nameKey,PersistentDataType.STRING);if(name==null)return;
        // Separado del nombre que MythicMobs/BetterModel reemplaza u oculta.
        TextDisplay text=labels.get(e.getUniqueId());
        Location at=e.getLocation().add(0,Math.max(3.5,e.getHeight()+1),0);
        if(text==null || !text.isValid()) {
            text=e.getWorld().spawn(at,TextDisplay.class,d->{d.setPersistent(false);d.setGravity(false);d.setBillboard(Display.Billboard.CENTER);d.setSeeThrough(true);d.setShadowed(true);d.setViewRange(1);});
            labels.put(e.getUniqueId(),text);
        }
        text.setText(name);text.teleport(at);
    }
    @EventHandler public void unload(org.bukkit.event.world.EntitiesUnloadEvent event) {
        for(Entity e:event.getEntities()) {mounts.remove(e.getUniqueId());controlledFlying.remove(e.getUniqueId());TextDisplay text=labels.remove(e.getUniqueId());if(text!=null)text.remove();}
    }
    @EventHandler public void disable(org.bukkit.event.server.PluginDisableEvent event) {
        if(event.getPlugin()==plugin) {labels.values().forEach(Entity::remove);labels.clear();}
    }
    private UUID eggUser;
    private record EggUse(UUID owner,boolean refund) {}
    private final Map<Item,EggUse> thrownEggs=new HashMap<>();
    private boolean thrownRefund;
    @EventHandler(priority=EventPriority.LOWEST)
    public void eggStart(org.bukkit.event.player.PlayerInteractEvent e) {
        thrownHatchUser=false;
        eggUser=(e.getAction()==org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK || e.getAction()==org.bukkit.event.block.Action.RIGHT_CLICK_AIR) &&
            e.getItem()!=null &&
            e.getHand()==EquipmentSlot.HAND && e.getItem().getType().name().endsWith("_SPAWN_EGG") ? e.getPlayer().getUniqueId() : null;
    }
    @EventHandler(priority=EventPriority.MONITOR)
    public void eggEnd(org.bukkit.event.player.PlayerInteractEvent e) {eggUser=null;}
    @EventHandler(ignoreCancelled=true)
    public void thrown(org.bukkit.event.entity.ItemSpawnEvent e) {
        if(eggUser==null || !e.getEntity().getItemStack().getType().name().endsWith("_SPAWN_EGG"))return;
        Item item=e.getEntity();thrownEggs.put(item,new EggUse(eggUser,e.getEntity().getWorld().getPlayers().stream().anyMatch(p->p.getUniqueId().equals(eggUser) && p.getGameMode()!=GameMode.CREATIVE)));
        Bukkit.getScheduler().runTaskLater(plugin,()->thrownEggs.remove(item),40);
    }
    @EventHandler(priority=EventPriority.HIGH,ignoreCancelled=true)
    public void thrownHatch(io.lumine.mythic.bukkit.events.MythicMobEggEvent e) {
        Location loc=io.lumine.mythic.bukkit.BukkitAdapter.adapt(e.getLocation());
        for(var entry:thrownEggs.entrySet()) {
            Location item=entry.getKey().getLocation();
            if(item.getWorld()==loc.getWorld() && item.distanceSquared(loc)<.000001) {
                eggUser=entry.getValue().owner();thrownHatchUser=true;thrownRefund=entry.getValue().refund();thrownEggs.remove(entry.getKey());
                Bukkit.getScheduler().runTask(plugin,()->{eggUser=null;thrownHatchUser=false;});break;
            }
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void lobbyEgg(io.lumine.mythic.bukkit.events.MythicMobEggEvent e) {
        String id=e.getMobType().getInternalName();
        Location at=io.lumine.mythic.bukkit.BukkitAdapter.adapt(e.getLocation());
        if(eggUser==null || !at.getWorld().getName().equals("lobby") ||
            !(GROUND.contains(id) || FLYING.contains(id)))return;
        // Mythic cancela antes de consumir el huevo de bloque; el lanzado ya se consumio.
        boolean refund=thrownHatchUser && thrownRefund;
        Player user=Bukkit.getPlayer(eggUser);e.setCancelled(true);
        if(user==null)return;
        if(refund)Bukkit.getScheduler().runTask(plugin,()->Bukkit.dispatchCommand(Bukkit.getConsoleSender(),
            "mm egg give "+user.getName()+" "+id+" 1"));
        user.sendMessage("§eLos huevos de monturas se usan en el mundo, no en el lobby. Conservas tu huevo.");
    }
    private boolean thrownHatchUser;
    @EventHandler(ignoreCancelled=true)
    public void spawn(io.lumine.mythic.bukkit.events.MythicMobSpawnEvent e) {
        Entity entity=e.getEntity();String id=e.getMobType().getInternalName();
        if(!GROUND.contains(id) && !FLYING.contains(id))return;
        entity.addScoreboardTag(id);
        if(eggUser!=null) {
            entity.getPersistentDataContainer().set(ownerKey,PersistentDataType.STRING,eggUser.toString());
            if(entity instanceof Tameable tame)tame.setOwner(Bukkit.getOfflinePlayer(eggUser));
        }
        prepare(entity);
        Bukkit.getScheduler().runTask(plugin,()->prepare(entity));
    }
    private void prepare(Entity e) {
        if(!isMount(e) || !e.isValid())return;
        mounts.add(e.getUniqueId());
        Player p=owner(e);
        if(enabled(p) && !e.getPersistentDataContainer().has(modeKey))e.getPersistentDataContainer().set(modeKey,PersistentDataType.BYTE,(byte)1);
        if(e.getPersistentDataContainer().has(modeKey))e.addScoreboardTag("astral.mount_mode");
        label(e);
        if(e instanceof AbstractHorse horse) {
            horse.setTamed(true);horse.setAI(!horse.getPassengers().isEmpty());horses.add(horse.getUniqueId());
        }
    }
    AstralMounts(JavaPlugin plugin) {
        this.plugin=plugin;
        Bukkit.getPluginManager().registerEvents(this,plugin);
        if(Bukkit.getPluginManager().isPluginEnabled("BetterModel"))modelClicks();
        for(World w:Bukkit.getWorlds())for(Entity e:w.getEntities())prepare(e);
        Bukkit.getScheduler().runTaskTimer(plugin,this::tick,1,1);
    }
    @EventHandler public void loaded(org.bukkit.event.world.EntitiesLoadEvent e) {
        e.getEntities().forEach(this::prepare);
        Bukkit.getScheduler().runTask(plugin,()->e.getEntities().forEach(this::prepare));
    }
    static boolean isMount(Entity e) {
        return e!=null && e.getScoreboardTags().stream().anyMatch(t->GROUND.contains(t)||FLYING.contains(t));
    }
    private Entity source(Entity clicked) {
        if(isMount(clicked))return clicked;
        if(Bukkit.getPluginManager().isPluginEnabled("BetterModel"))
            for(var registry:kr.toxicity.model.api.tracker.EntityTrackerRegistry.registries())
                for(var box:registry.hitBoxes())if(box.uuid().equals(clicked.getUniqueId()))return Bukkit.getEntity(registry.uuid());
        return null;
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void click(PlayerInteractEntityEvent e) {
        if(e.getHand()!=EquipmentSlot.HAND)return;
        Entity entity=source(e.getRightClicked());if(!isMount(entity))return;
        e.setCancelled(true);interact(entity.getUniqueId(),e.getPlayer().getUniqueId());
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void clickAt(PlayerInteractAtEntityEvent e) {click(e);}
    private void modelClicks() {
        BetterModel.eventBus().subscribe(plugin::isEnabled,HitBoxInteractAtEvent.class,e->{
            if(e.getHand()!=ModelInteractionHand.RIGHT)return;
            UUID id=e.getHitBox().source().uuid(),user=e.getWho().uuid();
            // El evento del modelo precede al reenvio al mob base.
            Runnable action=()->{Entity entity=Bukkit.getEntity(id);if(isMount(entity))interact(id,user);};
            if(Bukkit.isPrimaryThread())action.run();else Bukkit.getScheduler().runTask(plugin,action);
        });
    }
    void interact(UUID entityId,UUID playerId) {
        Entity entity=Bukkit.getEntity(entityId);Player p=Bukkit.getPlayer(playerId);
        if(!isMount(entity) || p==null || p.getWorld()!=entity.getWorld() ||
            p.getLocation().distanceSquared(entity.getLocation())>36)return;
        int tick=Bukkit.getCurrentTick();
        if(clicks.getOrDefault(playerId,-10)==tick)return; // mano secundaria / hitboxes
        clicks.put(playerId,tick);
        if(entity.getWorld().getName().equals("lobby")) {p.sendMessage("§eUsa tu montura fuera del lobby.");return;}
        String owner=entity.getPersistentDataContainer().get(ownerKey,PersistentDataType.STRING);
        if(owner==null && entity instanceof Tameable tame && tame.getOwner()!=null)owner=tame.getOwner().getUniqueId().toString();
        if(owner!=null && !owner.equals(playerId.toString())) {p.sendMessage("§eEsta montura tiene otro dueno.");return;}
        entity.getPersistentDataContainer().set(ownerKey,PersistentDataType.STRING,playerId.toString());
        ItemStack hand=p.getInventory().getItemInMainHand();
        if(enabled(p)) {
            entity.addScoreboardTag("astral.mount_mode");
            if(!entity.getPersistentDataContainer().has(modeKey))entity.getPersistentDataContainer().set(modeKey,PersistentDataType.BYTE,(byte)1);
            if(hand.getType()==Material.NAME_TAG) {
                if(hand.hasItemMeta() && hand.getItemMeta().hasDisplayName()) {
                    String name=hand.getItemMeta().getDisplayName();
                    entity.getPersistentDataContainer().set(nameKey,PersistentDataType.STRING,name);
                    entity.setCustomName(name);entity.setCustomNameVisible(false);label(entity);
                    if(p.getGameMode()!=GameMode.CREATIVE)hand.setAmount(hand.getAmount()-1);
                }
                return;
            }
            if(p.isSneaking() && hand.getType()!=Material.SADDLE) {
                boolean next=!following(entity);entity.getPersistentDataContainer().set(modeKey,PersistentDataType.BYTE,(byte)(next?1:0));
                String name=entity.getPersistentDataContainer().get(nameKey,PersistentDataType.STRING);
                if(name==null)name=entity.getName();
                p.sendMessage((next?"§a":"§e")+name+(next?" ahora te sigue.":" se queda quieta."));
                if(!next && entity instanceof Mob m && !riding(entity))stop(m);
                return;
            }
        }
        if(!(entity instanceof AbstractHorse)) {flyInteract(entity,p);return;}
        AbstractHorse horse=(AbstractHorse)entity;
        horse.setTamed(true);horse.setAI(true);horses.add(horse.getUniqueId());
        if(horse.getOwner()==null)horse.setOwner(p); // UUID exacto, tambien en creativo
        if(!horse.getOwner().getUniqueId().equals(playerId)) {
            p.sendMessage("§eEsta montura tiene otro dueno.");return;
        }
        ItemStack held=p.getInventory().getItemInMainHand();
        ItemStack saddle=horse.getInventory().getSaddle();
        // Migracion de la silla virtual antigua, sin regalar otra ni perderla.
        if((saddle==null || saddle.getType().isAir()) && horse.getScoreboardTags().contains("astral.ensillado")) {
            horse.getInventory().setSaddle(new ItemStack(Material.SADDLE));saddle=horse.getInventory().getSaddle();
        }
        if(saddle==null || saddle.getType().isAir()) {
            if(held.getType()!=Material.SADDLE) {p.sendMessage("§ePonele una silla con clic derecho.");return;}
            horse.getInventory().setSaddle(new ItemStack(Material.SADDLE));
            if(p.getGameMode()!=GameMode.CREATIVE)held.setAmount(held.getAmount()-1);
            horse.addScoreboardTag("astral.ensillado");
            MythicBukkit.inst().getAPIHelper().castSkill(horse,"AST_SILLA_VER");
            p.playSound(p.getLocation(),Sound.ENTITY_HORSE_SADDLE,1,1);
            return;
        }
        if(held.getType()!=Material.SADDLE && horse.getPassengers().isEmpty() && !p.isInsideVehicle())horse.addPassenger(p);
    }
    private void flyInteract(Entity entity,Player p) {
        ItemStack held=p.getInventory().getItemInMainHand();
        if(!entity.getScoreboardTags().contains("astral.ensillado")) {
            if(held.getType()!=Material.SADDLE) {p.sendMessage("§ePonele una silla con clic derecho.");return;}
            entity.addScoreboardTag("astral.ensillado");
            if(p.getGameMode()!=GameMode.CREATIVE)held.setAmount(held.getAmount()-1);
            MythicBukkit.inst().getAPIHelper().castSkill(entity,"AST_SILLA_VER");return;
        }
        if(held.getType()==Material.SADDLE || p.isInsideVehicle())return;
        var registry=BetterModel.registryOrNull(entity.getUniqueId());
        if(registry==null || registry.hasPassenger())return;
        var tracker=registry.first();if(tracker==null)return;
        var box=tracker.hitbox(kr.toxicity.model.api.nms.HitBoxListener.EMPTY,b->true);
        if(box==null)return;
        box.mountController(kr.toxicity.model.api.mount.MountControllers.FLY);
        box.mount(BetterModel.platform().adapter().player(p.getUniqueId()));
    }
    void chill(UUID id) {
        Player p=Bukkit.getPlayer(id);if(p==null)return;
        p.addPotionEffect(new PotionEffect(PotionEffectType.SLOWNESS,50,0));
        p.getWorld().spawnParticle(Particle.SNOWFLAKE,p.getLocation().add(0,1,0),18,.4,.6,.4,.01);
        // Por debajo del umbral de dano (140); repetidos golpes nunca lo acumulan.
        p.setFreezeTicks(Math.max(p.getFreezeTicks(),100));
        chillUntil.put(id,Bukkit.getCurrentTick()+20);
    }
    @EventHandler(ignoreCancelled=true)
    public void noExtraFreezeDamage(EntityDamageEvent e) {
        if(e.getCause()==EntityDamageEvent.DamageCause.FREEZE && chillUntil.containsKey(e.getEntity().getUniqueId()))e.setCancelled(true);
    }
    static Vector swimVector(org.bukkit.Input input,Location look) {
        double forward=(input.isForward()?1:0)-(input.isBackward()?1:0);
        double side=(input.isRight()?1:0)-(input.isLeft()?1:0);
        Vector dir=look.getDirection();
        double yaw=Math.toRadians(look.getYaw());
        Vector v=dir.multiply(forward).add(new Vector(-Math.cos(yaw),0,-Math.sin(yaw)).multiply(side));
        if(input.isJump())v.setY(v.getY()+1);
        if(v.lengthSquared()>1)v.normalize();
        return v.multiply(.65); // 13 bloques/s frente a ~2 nadando a pie sin efectos
    }
    private void tick() {
        int now=Bukkit.getCurrentTick();
        if(now%10==0)follow();
        for(UUID id:List.copyOf(labels.keySet())) {Entity e=Bukkit.getEntity(id);if(e!=null && e.isValid())label(e);else {TextDisplay text=labels.remove(id);if(text!=null)text.remove();}}
        horses.removeIf(id->{
            Entity e=Bukkit.getEntity(id);if(!(e instanceof AbstractHorse h) || !h.isValid())return true;
            h.setTamed(true);
            if(!enabled(owner(h)) && !h.getPersistentDataContainer().has(modeKey))h.setAI(!h.getPassengers().isEmpty());
            else if(!h.getPassengers().isEmpty())h.setAI(true);
            return false;
        });
        chillUntil.entrySet().removeIf(e->{
            if(e.getValue()>now)return false;
            Player p=Bukkit.getPlayer(e.getKey());
            if(p!=null && p.getFreezeTicks()<=100)p.setFreezeTicks(0);
            return true;
        });
        if(now%200==0)clicks.clear();
        for(Player p:Bukkit.getOnlinePlayers()) {
            Entity e=p.getVehicle();
            if(!isMount(e) || !e.getScoreboardTags().contains("astral_lagarto"))continue;
            if(!e.isInWater())continue;
            e.setVelocity(swimVector(p.getCurrentInput(),p.getLocation()));
            p.addPotionEffect(new PotionEffect(PotionEffectType.WATER_BREATHING,40,0,true,false,false));
        }
    }
}
