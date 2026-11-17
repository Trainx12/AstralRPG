package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.BoundingBox;
import kr.toxicity.model.api.BetterModel;
import io.lumine.mythic.bukkit.MythicBukkit;

/** Ordena una sola interseccion por enemigo; el datapack conserva /damage magic y su XP. */
public final class AstralSpell implements Listener {
    private final Set<String> arenas;
    public AstralSpell(JavaPlugin plugin) {
        try (var stream = plugin.getResource("spell-arenas.txt")) {
            arenas = stream == null ? Set.of() : Set.copyOf(new String(stream.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).lines().toList());
        } catch (java.io.IOException e) { throw new IllegalStateException(e); }
        Bukkit.getPluginManager().registerEvents(this, plugin);
    }
    private boolean eligible(LivingEntity e, Player caster) {
        if(e == caster || e.isDead() || e.isInvulnerable() || e instanceof ArmorStand ||
           e instanceof Villager || e instanceof WanderingTrader) return false;
        var tags=e.getScoreboardTags();
        if(tags.stream().anyMatch(t -> t.equals("astral.pet") || t.startsWith("astral.pet.") ||
            t.equals("astral.no_combat_xp") || t.equals("astral.mercader"))) return false;
        if(e instanceof Player p) return arenas.contains(p.getWorld().getName()) &&
            p.getGameMode()!=GameMode.CREATIVE && p.getGameMode()!=GameMode.SPECTATOR;
        if(!e.hasAI() || (e instanceof Tameable tame && tame.getOwner()!=null)) return false;
        if(Bukkit.getPluginManager().isPluginEnabled("MythicMobs")) {
            var active=MythicBukkit.inst().getMobManager().getActiveMob(e.getUniqueId());
            if(active.isPresent()) {
                var mob=active.get(); String id=mob.getType().getInternalName();
                if(id.startsWith("astral_pet_") || id.startsWith("astral_npc_") || id.startsWith("astral_estatua_") ||
                   id.equals("astral_goblin_vendedor") || (mob.getOwner().isPresent() &&
                   Set.of("astral_grillo","astral_chocobo","astral_escarabajo","astral_lagarto","astral_ave","astral_pterodactilo").contains(id))) return false;
            }
        }
        return true;
    }
    private record Hit(LivingEntity entity, double distance) {}
    @EventHandler(ignoreCancelled=true)
    public void trace(EntitySpawnEvent event) {
        if(!(event.getEntity() instanceof Marker marker) || !marker.getScoreboardTags().contains("astral.spell.perfora")) return;
        Player caster=marker.getWorld().getPlayers().stream().filter(p -> p.getScoreboardTags().contains("astral.caster"))
            .min(Comparator.comparingDouble(p -> p.getEyeLocation().distanceSquared(marker.getLocation()))).orElse(null);
        if(caster==null) return;
        var origin=marker.getLocation().toVector(); var direction=caster.getEyeLocation().getDirection();
        double end=25;
        var wall=marker.getWorld().rayTraceBlocks(marker.getLocation(),direction,end,FluidCollisionMode.NEVER,true);
        if(wall!=null) end=wall.getHitPosition().distance(origin);
        var hits=new ArrayList<Hit>();
        for(var e:marker.getWorld().getLivingEntities()) {
            for(int n=1;n<=3;n++) e.removeScoreboardTag("astral.spell.hit"+n);
            if(!eligible(e,caster)) continue;
            var boxes=new ArrayList<BoundingBox>(); boxes.add(e.getBoundingBox());
            if(Bukkit.getPluginManager().isPluginEnabled("BetterModel")) {
                var registry=BetterModel.registryOrNull(e.getUniqueId());
                if(registry!=null) for(var tracker:registry.trackers()) {
                    var bone=tracker.bone("b_astral_hitbox");
                    if(bone!=null && bone.getHitBox()!=null) {
                        var physical=Bukkit.getEntity(bone.getHitBox().uuid());
                        if(physical!=null) boxes.add(physical.getBoundingBox());
                    }
                }
            }
            double nearest=Double.POSITIVE_INFINITY;
            for(var box:boxes) {
                var expanded=box.clone().expand(.45);
                if(expanded.contains(origin)) nearest=0;
                var hit=expanded.rayTrace(origin,direction,25);
                if(hit!=null) nearest=Math.min(nearest,hit.getHitPosition().distance(origin));
            }
            if(nearest<end) hits.add(new Hit(e,nearest));
        }
        hits.sort(Comparator.comparingDouble(Hit::distance).thenComparing(h -> h.entity().getUniqueId()));
        int count=Math.min(3,hits.size());
        for(int n=0;n<count;n++) hits.get(n).entity().addScoreboardTag("astral.spell.hit"+(n+1));
        // Con menos de tres enemigos, sigue hasta pared/alcance; el tercero corta.
        if(count==3) end=hits.get(2).distance();
        var objective=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp");
        if(objective!=null) {
            objective.getScore("#spell.end").setScore(Math.min(50,(int)Math.floor(end/.5)));
            objective.getScore("#spell.mm").setScore((int)Math.round(end*1000));
            objective.getScore("#spell.wall").setScore(wall!=null && count<3 ? 1 : 0);
            objective.getScore("#spell.ready").setScore(1);
        }
    }
}
