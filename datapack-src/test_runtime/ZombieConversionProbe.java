package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.plugin.java.JavaPlugin;

/** Solo en Paper local: conversion real en agua y controles de otras transformaciones. */
public final class ZombieConversionProbe extends JavaPlugin implements Listener {
    private int failures, checks;
    private final List<Entity> cleanup = new ArrayList<>();
    private final Set<UUID> blocked = new HashSet<>();
    private int expected;
    private boolean huskConverted;
    private Zombie husk;

    public void onEnable() {
        getServer().getPluginManager().registerEvents(this, this);
        getCommand("zombieprobe").setExecutor((s,c,l,a)->{start(); return true;});
    }
    private void check(boolean ok, String message) {
        checks++; if (!ok) failures++;
        getLogger().info("ZOMBIE " + (ok ? "PASS " : "FAIL ") + message);
    }
    @EventHandler(priority=EventPriority.MONITOR)
    public void transform(EntityTransformEvent event) {
        if (event.getTransformReason()!=EntityTransformEvent.TransformReason.DROWNED) return;
        if (event.getEntity().getType()==EntityType.ZOMBIE) {
            check(event.isCancelled(), "zombie drowning cancelled");
            blocked.add(event.getEntity().getUniqueId());
        } else if (husk!=null && event.getEntity().getUniqueId().equals(husk.getUniqueId())) {
            huskConverted=!event.isCancelled();
            cleanup.addAll(event.getTransformedEntities());
        }
    }
    private <T extends Entity> T track(T entity) { cleanup.add(entity); return entity; }
    private void start() {
        World w=Bukkit.getWorlds().getFirst(); w.setDifficulty(Difficulty.NORMAL);
        Location at=new Location(w, 0, 20, 0); w.getChunkAt(at).setForceLoaded(true);
        List<Zombie> zombies=new ArrayList<>();
        for (int i=0;i<3;i++) {
            Location p=at.clone().add(i*3,0,0);
            p.getBlock().setType(Material.WATER); p.clone().add(0,1,0).getBlock().setType(Material.WATER);
            Zombie z=track((Zombie)w.spawnEntity(p,EntityType.ZOMBIE));
            z.setGravity(false); z.setAI(true); z.setSilent(true);
            if(i>0) z.addScoreboardTag("astral.mt"+(i==1?3:10));
            if(i==2) z.addScoreboardTag("astral.elite");
            z.getAttribute(Attribute.MAX_HEALTH).setBaseValue(i==0?20:10000*i);
            z.setHealth(z.getAttribute(Attribute.MAX_HEALTH).getValue());
            z.setConversionTime(1); zombies.add(z);
        }
        expected=zombies.size();
        Location h=at.clone().add(10,0,0);
        h.getBlock().setType(Material.WATER); h.clone().add(0,1,0).getBlock().setType(Material.WATER);
        husk=track((Zombie)w.spawnEntity(h,EntityType.HUSK)); husk.setGravity(false); husk.setConversionTime(1);
        Drowned natural=track((Drowned)w.spawnEntity(at.clone().add(14,0,0),EntityType.DROWNED));
        ZombieVillager villager=track((ZombieVillager)w.spawnEntity(at.clone().add(17,0,0),EntityType.ZOMBIE_VILLAGER));
        Villager cured=track((Villager)w.spawnEntity(at.clone().add(20,0,0),EntityType.VILLAGER));
        EntityTransformEvent cure=new EntityTransformEvent(villager,List.of(cured),EntityTransformEvent.TransformReason.CURED);
        Bukkit.getPluginManager().callEvent(cure);
        check(!cure.isCancelled(),"villager curing allowed");
        Skeleton skeleton=track((Skeleton)w.spawnEntity(at.clone().add(23,0,0),EntityType.SKELETON));
        Stray stray=track((Stray)w.spawnEntity(at.clone().add(26,0,0),EntityType.STRAY));
        EntityTransformEvent freeze=new EntityTransformEvent(skeleton,List.of(stray),EntityTransformEvent.TransformReason.FROZEN);
        Bukkit.getPluginManager().callEvent(freeze);
        check(!freeze.isCancelled(),"skeleton freezing allowed");
        Bukkit.getScheduler().runTaskLater(this,()->{
            check(blocked.size()==expected,"all three real zombie conversions intercepted");
            for(int i=0;i<zombies.size();i++) {
                Zombie z=zombies.get(i);
                check(z.isValid() && z.getType()==EntityType.ZOMBIE,"original zombie survives "+i);
                check(z.getAttribute(Attribute.MAX_HEALTH).getValue()==(i==0?20:10000*i),"maximum health retained "+i);
                if(i>0) check(z.getScoreboardTags().contains("astral.mt"+(i==1?3:10)),"tier retained "+i);
            }
            check(huskConverted,"real husk to zombie conversion allowed");
            check(natural.isValid() && natural.getType()==EntityType.DROWNED,"natural drowned allowed");
            cleanup.forEach(Entity::remove);
            getLogger().info("ZOMBIE RESULT checks="+checks+" failures="+failures);
        }, 12);
    }
}
