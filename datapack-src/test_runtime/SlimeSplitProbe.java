package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.attribute.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.plugin.java.JavaPlugin;

/** Real deaths and two generations, not a fabricated transform event. Local only. */
public final class SlimeSplitProbe extends JavaPlugin implements Listener {
    private int failures, checks, splits;
    private final Map<UUID,Slime> parents=new HashMap<>();
    private final List<Slime> children=new ArrayList<>();
    private final List<Entity> cleanup=new ArrayList<>();
    private void check(boolean ok,String message) {
        checks++; if(!ok) failures++;
        getLogger().info("SLIME "+(ok?"PASS ":"FAIL ")+message);
    }
    public void onEnable() {
        getServer().getPluginManager().registerEvents(this,this);
        getCommand("slimeprobe").setExecutor((s,c,l,a)->{start();return true;});
    }
    private void start() {
        World w=Bukkit.getWorlds().getFirst();
        w.setDifficulty(Difficulty.NORMAL);
        for(int x=-1;x<=9;x++) for(int z=-1;z<=1;z++) w.getChunkAt(x,z).setForceLoaded(true);
        var board=Bukkit.getScoreboardManager().getMainScoreboard();
        if(board.getObjective("astral.mt")==null)
            board.registerNewObjective("astral.mt",org.bukkit.scoreboard.Criteria.DUMMY,
                net.kyori.adventure.text.Component.text("tier"));
        int i=0;
        for(EntityType type:List.of(EntityType.SLIME,EntityType.MAGMA_CUBE)) {
            for(boolean elite:List.of(false,true)) {
                Slime parent=(Slime)w.spawnEntity(new Location(w, i++*12, 10, 0),type);
                cleanup.add(parent);parent.setSize(4);parent.setGravity(false);parent.setAI(false);
                parent.addScoreboardTag("astral.seen");parent.addScoreboardTag("astral.mt3");
                parent.addScoreboardTag("astral.vpaga");
                if(elite) {parent.addScoreboardTag("astral.elite");parent.addScoreboardTag("astral.elite3");}
                parent.getAttribute(Attribute.MAX_HEALTH).addModifier(new AttributeModifier(
                    new NamespacedKey("astral","tier"),99,AttributeModifier.Operation.ADD_SCALAR));
                if(elite) parent.getAttribute(Attribute.MAX_HEALTH).addModifier(new AttributeModifier(
                    new NamespacedKey("astral","elite"),2,AttributeModifier.Operation.MULTIPLY_SCALAR_1));
                parent.getAttribute(Attribute.ATTACK_DAMAGE).setBaseValue(7);
                parent.setHealth(parent.getAttribute(Attribute.MAX_HEALTH).getValue());
                parent.customName(net.kyori.adventure.text.Component.text("[T3] "+(elite?"Elite ":"")+type));
                parent.setCustomNameVisible(true);
                Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.mt")
                    .getScore(parent.getUniqueId().toString()).setScore(3);
                parents.put(parent.getUniqueId(),parent);parent.setHealth(0);
            }
        }
        Bukkit.getScheduler().runTaskLater(this,()->{
            check(splits==4,"four parent splits, got "+splits);
            for(Slime child:List.copyOf(children)) {
                check(child.isValid(),"child inserted");
                check(Math.abs(child.getHealth()-child.getAttribute(Attribute.MAX_HEALTH).getValue())<0.01,"full after insertion");
                parents.put(child.getUniqueId(),child);child.setHealth(0);
            }
        },45);
        Bukkit.getScheduler().runTaskLater(this,()->{
            check(splits>4,"second generation split");
            exclusions(w);
            contact(w);
        },90);
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void split(EntityTransformEvent e) {
        Slime parent=parents.get(e.getEntity().getUniqueId());
        if(parent==null || e.getTransformReason()!=EntityTransformEvent.TransformReason.SPLIT)return;
        splits++;
        getLogger().info("SLIME RAW parent="+parent.getType()+" size="+parent.getSize()+" max="+parent.getAttribute(Attribute.MAX_HEALTH).getValue());
        for(Entity entity:e.getTransformedEntities()) {
            Slime child=(Slime)entity;cleanup.add(child);
            double expected=parent.getAttribute(Attribute.MAX_HEALTH).getValue();
            getLogger().info("SLIME RAW child size="+child.getSize()+" max="+child.getAttribute(Attribute.MAX_HEALTH).getValue()+" health="+child.getHealth()+" seen="+child.getScoreboardTags().contains("astral.seen"));
            check(Math.abs(child.getAttribute(Attribute.MAX_HEALTH).getValue()-expected)<0.01,"max inherited "+expected);
            check(Math.abs(child.getHealth()-expected)<0.01,"full health");
            check(child.getAttribute(Attribute.ATTACK_DAMAGE).getValue()==parent.getAttribute(Attribute.ATTACK_DAMAGE).getValue(),"damage inherited");
            check(Objects.equals(child.customName(),parent.customName()),"name inherited");
            check(child.getScoreboardTags().containsAll(parent.getScoreboardTags()),"tags including elite inherited");
            check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.mt").getScore(child.getUniqueId().toString()).getScore()==3,"score tier inherited");
            var progression=Bukkit.getPluginManager().getPlugin("AstralProgression");
            try {
                double reward=(double)progression.getClass().getMethod("reward",LivingEntity.class).invoke(progression,child);
                double normal=progression.getConfig().getDouble("xp.3")*progression.getConfig().getDouble("normal-bonus",1);
                check(reward==normal,"normal tier XP, elite included");
            } catch(ReflectiveOperationException ex) {throw new RuntimeException(ex);}
            if(parent.getSize()==4)children.add(child);
        }
    }
    private void exclusions(World w) {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralProgression");
        for(String kind:List.of("unscaled","invulnerable","pet","minigame","cancelled")) {
            Slime p=w.spawn(new Location(w,100,10,0),Slime.class);p.setSize(2);cleanup.add(p);
            Slime c=w.spawn(new Location(w,100,10,0),Slime.class);c.setSize(1);cleanup.add(c);
            if(!kind.equals("unscaled")) {p.addScoreboardTag("astral.seen");p.addScoreboardTag("astral.mt3");}
            if(kind.equals("invulnerable"))p.setInvulnerable(true);
            if(kind.equals("pet"))p.addScoreboardTag("astral.pet");
            if(kind.equals("minigame")) {
                World mini=Bukkit.createWorld(new WorldCreator("magmarun").type(WorldType.FLAT).generateStructures(false)
                    .generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}"));
                p.teleport(new Location(mini,0,10,0));c.teleport(new Location(mini,0,10,0));
            }
            EntityTransformEvent e=new EntityTransformEvent(p,List.of(c),EntityTransformEvent.TransformReason.SPLIT);
            if(kind.equals("cancelled")) e.setCancelled(true);
            Bukkit.getPluginManager().callEvent(e);
            check(c.getAttribute(Attribute.MAX_HEALTH).getValue()==1 && !c.getScoreboardTags().contains("astral.split"),"excluded "+kind);
        }
    }
    private void contact(World w) {
        Slime s=w.spawn(new Location(w,120,15,0),Slime.class);s.setSize(1);s.setGravity(false);cleanup.add(s);
        for(String tag:List.of("astral.seen","astral.mt3","astral.split"))s.addScoreboardTag(tag);
        s.getAttribute(Attribute.ATTACK_DAMAGE).setBaseValue(7);
        IronGolem target=w.spawn(s.getLocation(),IronGolem.class);target.setAI(false);target.setGravity(false);cleanup.add(target);
        s.setTarget(target);
        new org.bukkit.scheduler.BukkitRunnable() {
            int ticks;
            public void run() {
                if(++ticks>14 || !s.isValid()) {cancel();return;}
                s.teleport(target.getLocation());s.setVelocity(new org.bukkit.util.Vector());s.setTarget(target);
            }
        }.runTaskTimer(this,1,1);
        try {
            var plugin=Bukkit.getPluginManager().getPlugin("AstralProgression");
            var track=plugin.getClass().getDeclaredMethod("trackSplit",LivingEntity.class);track.setAccessible(true);track.invoke(plugin,s);
        } catch(ReflectiveOperationException ex) {check(false,"tiny contact tracker unavailable");}
        Bukkit.getScheduler().runTaskLater(this,()->{
            getLogger().info("SLIME CONTACT target="+s.getTarget()+" ai="+s.hasAI()+" overlap="+s.getBoundingBox().expand(0.1).overlaps(target.getBoundingBox())+" health="+target.getHealth());
            check(target.getHealth()<100,"tiny slime actually deals contact damage");
            cleanup.forEach(Entity::remove);
            getLogger().info("SLIME RESULT checks="+checks+" splits="+splits+" failures="+failures);
        },15);
    }
}
