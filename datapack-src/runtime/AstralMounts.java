package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
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
    private Player eggUser;
    private final Map<Item,UUID> thrownEggs=new HashMap<>();
    @EventHandler(priority=EventPriority.LOWEST)
    public void eggStart(org.bukkit.event.player.PlayerInteractEvent e) {
        eggUser=(e.getAction()==org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK || e.getAction()==org.bukkit.event.block.Action.RIGHT_CLICK_AIR) &&
            e.getItem()!=null &&
            e.getItem().getType()==Material.PIG_SPAWN_EGG ? e.getPlayer() : null;
    }
    @EventHandler(priority=EventPriority.MONITOR)
    public void eggEnd(org.bukkit.event.player.PlayerInteractEvent e) {eggUser=null;}
    @EventHandler(ignoreCancelled=true)
    public void thrown(org.bukkit.event.entity.ItemSpawnEvent e) {
        if(eggUser==null || e.getEntity().getItemStack().getType()!=Material.PIG_SPAWN_EGG)return;
        Item item=e.getEntity();thrownEggs.put(item,eggUser.getUniqueId());
        Bukkit.getScheduler().runTaskLater(plugin,()->thrownEggs.remove(item),40);
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void thrownHatch(io.lumine.mythic.bukkit.events.MythicMobEggEvent e) {
        Location loc=io.lumine.mythic.bukkit.BukkitAdapter.adapt(e.getLocation());
        for(var entry:thrownEggs.entrySet()) {
            Location item=entry.getKey().getLocation();
            if(item.getWorld()==loc.getWorld() && item.distanceSquared(loc)<.000001) {
                eggUser=Bukkit.getPlayer(entry.getValue());thrownEggs.remove(entry.getKey());
                Bukkit.getScheduler().runTask(plugin,()->eggUser=null);break;
            }
        }
    }
    @EventHandler(ignoreCancelled=true)
    public void spawn(io.lumine.mythic.bukkit.events.MythicMobSpawnEvent e) {
        if(!(e.getEntity() instanceof AbstractHorse horse) ||
            !Set.of("astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto").contains(e.getMobType().getInternalName()))return;
        horse.setTamed(true);horse.setAI(true);
        horse.addScoreboardTag(e.getMobType().getInternalName());
        if(eggUser!=null) {horse.setOwner(eggUser);eggUser=null;}
    }
    AstralMounts(JavaPlugin plugin) {
        this.plugin=plugin;
        Bukkit.getPluginManager().registerEvents(this,plugin);
        Bukkit.getScheduler().runTaskTimer(plugin,this::tick,1,1);
    }
    static boolean isMount(Entity e) {
        if(!(e instanceof AbstractHorse))return false;
        return e.getScoreboardTags().stream().anyMatch(Set.of("astral_grillo","astral_chocobo",
            "astral_escarabajo","astral_lagarto")::contains);
    }
    void interact(UUID entityId,UUID playerId) {
        Entity entity=Bukkit.getEntity(entityId);Player p=Bukkit.getPlayer(playerId);
        if(!isMount(entity) || p==null || p.getWorld()!=entity.getWorld() ||
            p.getLocation().distanceSquared(entity.getLocation())>36)return;
        int tick=Bukkit.getCurrentTick();
        if(clicks.getOrDefault(playerId,-10)==tick)return; // mano secundaria / hitboxes
        clicks.put(playerId,tick);
        AbstractHorse horse=(AbstractHorse)entity;
        horse.setTamed(true);horse.setAI(true);
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
            held.setAmount(held.getAmount()-1);
            horse.addScoreboardTag("astral.ensillado");
            MythicBukkit.inst().getAPIHelper().castSkill(horse,"AST_SILLA_VER");
            p.playSound(p.getLocation(),Sound.ENTITY_HORSE_SADDLE,1,1);
            return;
        }
        if(held.getType()!=Material.SADDLE && horse.getPassengers().isEmpty() && !p.isInsideVehicle())horse.addPassenger(p);
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
