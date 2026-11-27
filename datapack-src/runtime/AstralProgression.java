package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.block.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.world.*;
import org.bukkit.inventory.*;
import org.bukkit.loot.LootContext;
import org.bukkit.persistence.*;
import org.bukkit.plugin.java.JavaPlugin;
import dev.aurelium.auraskills.api.event.skill.*;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import io.lumine.mythic.bukkit.MythicBukkit;
import me.ryanhamshire.GriefPrevention.GriefPrevention;
import me.ryanhamshire.GriefPrevention.ClaimsMode;

/** XP por muerte y loot adicional, sin comandos accesibles al jugador. */
public final class AstralProgression extends JavaPlugin implements Listener {
    private NamespacedKey skillKey, playerKey, timeKey, placedKey, generatedKey, mythicKey;
    private String survival;
    private final Random random = new Random();
    private final Set<UUID> buying = new HashSet<>();
    private final Map<UUID,Map<Statistic,EntityType>> friendlyDeaths = new HashMap<>();
    private static final Set<String> SKILLS = Set.of("fighting", "archery", "sorcery");
    private final Set<UUID> tinySplits = new HashSet<>();
    private final Set<String> splitExcludedWorlds = new HashSet<>();
    private final Properties worldBossHealth = new Properties();
    private record SplitAttribute(Attribute type, double base,
            List<org.bukkit.attribute.AttributeModifier> modifiers) {}
    private final Map<UUID,List<SplitAttribute>> pendingSplits = new HashMap<>();
    private final Map<UUID,List<SplitAttribute>> dyingSplits = new HashMap<>();
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void worldBossSpawn(io.lumine.mythic.bukkit.events.MythicMobSpawnEvent e) {
        LivingEntity mob=e.getLivingEntity();
        // Mythic restores its configured base health after onSpawn commands finish (e.g. 1000 x5).
        // Run once after insertion, using the tier saved on spawn, never on chunk load or a timer.
        Bukkit.getScheduler().runTaskLater(this,()->{
            if(!mob.isValid() || mob.isDead() || !mob.getScoreboardTags().contains("ad.boss.scaled") ||
                mob.getScoreboardTags().stream().noneMatch(t->t.matches("astral\\.jm(?:[1-9]|10)"))) return;
            for(int t=10;t>=1;t--) if(mob.getScoreboardTags().contains("astral.jm"+t)) {
                var health=mob.getAttribute(Attribute.MAX_HEALTH);
                double base=Double.parseDouble(worldBossHealth.getProperty(Integer.toString(t)));
                // Mythic's stat registry reapplies HEALTH after spawn; update its source of truth too.
                e.getMob().getStatRegistry().putBaseValue(io.lumine.mythic.core.skills.stats.Stats.HEALTH,base);
                e.getMob().getStatRegistry().updateDirtyStats();
                health.setBaseValue(base);
                mob.setHealth(health.getValue());
                getLogger().info("Jefe de mundo T"+t+" vida="+health.getValue()+" base="+health.getBaseValue());
                break;
            }
        },2);
    }
    @EventHandler(priority=EventPriority.LOWEST,ignoreCancelled=true)
    public void splitDeath(EntityDeathEvent e) {
        if(!(e.getEntity() instanceof Slime parent) || parent.getSize()<=1 || !scaledSplit(parent)) return;
        UUID id=parent.getUniqueId();
        var snapshot=splitAttributes(parent);
        dyingSplits.put(id,snapshot);
        // Cancelled deaths, cancelled transforms and plugins removing a corpse must not leak entries.
        Bukkit.getScheduler().runTaskLater(this,()->dyingSplits.remove(id,snapshot),100);
    }
    private List<SplitAttribute> splitAttributes(Slime parent) {
        List<SplitAttribute> result=new ArrayList<>();
        for(Attribute type:List.of(Attribute.MAX_HEALTH,Attribute.ATTACK_DAMAGE,Attribute.MOVEMENT_SPEED,
                Attribute.ARMOR,Attribute.ARMOR_TOUGHNESS,Attribute.KNOCKBACK_RESISTANCE,Attribute.FOLLOW_RANGE)) {
            var from=parent.getAttribute(type);
            if(from!=null) result.add(new SplitAttribute(type,from.getBaseValue(),List.copyOf(from.getModifiers())));
        }
        return List.copyOf(result);
    }
    private void applySplitAttributes(Slime child,List<SplitAttribute> snapshot) {
        for(var saved:snapshot) {
            var to=child.getAttribute(saved.type());
            if(to==null) continue;
            for(var modifier:List.copyOf(to.getModifiers())) to.removeModifier(modifier);
            to.setBaseValue(saved.base());
            for(var modifier:saved.modifiers()) to.addModifier(modifier);
        }
        child.setHealth(child.getAttribute(Attribute.MAX_HEALTH).getValue());
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void splitSpawn(CreatureSpawnEvent e) {
        if(e.getSpawnReason()!=CreatureSpawnEvent.SpawnReason.SLIME_SPLIT ||
                !(e.getEntity() instanceof Slime child)) return;
        var snapshot=pendingSplits.get(child.getUniqueId());
        if(snapshot!=null) applySplitAttributes(child,snapshot);
    }
    public void onEnable() {
        saveDefaultConfig();
        try(var reader=getTextResource("world-boss-health.txt")) {
            if(reader==null) throw new IllegalStateException("Falta world-boss-health.txt");
            worldBossHealth.load(reader);
        } catch(java.io.IOException ex) {throw new IllegalStateException(ex);}
        try(var reader=getTextResource("split-excluded-worlds.txt")) {
            if(reader==null) throw new IllegalStateException("Falta split-excluded-worlds.txt");
            new java.io.BufferedReader(reader).lines().forEach(splitExcludedWorlds::add);
        } catch(java.io.IOException ex) {throw new IllegalStateException(ex);}
        splitExcludedWorlds.addAll(getConfig().getStringList("split-excluded-worlds"));
        survival = getConfig().getString("survival-world", "world");
        skillKey=new NamespacedKey(this,"skill"); playerKey=new NamespacedKey(this,"player");
        timeKey=new NamespacedKey(this,"time"); placedKey=new NamespacedKey(this,"placed");
        generatedKey=new NamespacedKey(this,"generated");
        mythicKey=new NamespacedKey(this,"mythic");
        getServer().getPluginManager().registerEvents(this,this);
        Bukkit.getWorlds().forEach(this::claims);
        Bukkit.getWorlds().forEach(w -> w.getLivingEntities().forEach(this::protectPet));
        Bukkit.getScheduler().runTaskTimer(this, () -> Bukkit.getWorlds().forEach(w ->
            w.getLivingEntities().forEach(this::protectPet)), 1, 20);
        Bukkit.getWorlds().forEach(w -> w.getLivingEntities().forEach(this::trackSplit));
        Bukkit.getScheduler().runTaskTimer(this, this::tinySplitAttacks, 1, 10);
        getLogger().info("XP por tier, proteccion 2D y loot aditivo activos; survival="+survival);
    }
    private boolean scaledSplit(Slime mob) {
        return mob.getScoreboardTags().contains("astral.seen") &&
            mob.getScoreboardTags().stream().anyMatch(t -> t.matches("astral\\.mt(?:[1-9]|10)")) &&
            !mob.isInvulnerable() && !pet(mob) &&
            !mob.getScoreboardTags().contains("astral.pet") &&
            !splitExcludedWorlds.contains(mob.getWorld().getName());
    }
    // Paper copies entity tags during conversion, then setSize resets health/damage to the small size.
    // Insertion/spawn listeners can reset bases after SPLIT. Keep values, not the dying parent,
    // and restore once more next tick, after insertion and synchronous spawn listeners finish.
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void slimeSplit(EntityTransformEvent e) {
        if(e.getTransformReason()!=EntityTransformEvent.TransformReason.SPLIT ||
            !(e.getEntity() instanceof Slime parent) || !scaledSplit(parent)) return;
        var captured=dyingSplits.remove(parent.getUniqueId());
        var original=captured!=null?captured:splitAttributes(parent);
        // Each generation has half the previous maximum, including elite modifiers.
        var snapshot=original.stream().map(a -> a.type()==Attribute.MAX_HEALTH
            ? new SplitAttribute(a.type(),a.base()/2,a.modifiers()) : a).toList();
        for(Entity entity:e.getTransformedEntities()) {
            if(!(entity instanceof Slime child) || child.getType()!=parent.getType() ||
                child.isInvulnerable() || pet(child)) continue;
            pendingSplits.put(child.getUniqueId(),snapshot);
            applySplitAttributes(child,snapshot);
            for(String tag:parent.getScoreboardTags()) child.addScoreboardTag(tag);
            child.addScoreboardTag("astral.split");
            var objective=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.mt");
            if(objective!=null) {
                var score=objective.getScore(parent.getUniqueId().toString());
                if(score.isScoreSet()) objective.getScore(child.getUniqueId().toString()).setScore(score.getScore());
            }
            child.addPotionEffects(parent.getActivePotionEffects());
            child.customName(parent.customName());
            child.setCustomNameVisible(parent.isCustomNameVisible());
            // Refresh the health text after insertion (the parent's death label may contain zero).
            Bukkit.getScheduler().runTask(this, () -> {
                var saved=pendingSplits.remove(child.getUniqueId());
                if(saved==null || !child.isValid() || child.isDead()) return;
                applySplitAttributes(child,saved);
                trackSplit(child);
                if(child.getScoreboardTags().contains("astral.hpname"))
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute as "+child.getUniqueId()+" run function astral:mob/vida");
            });
        }
    }
    private void trackSplit(LivingEntity entity) {
        if(entity instanceof Slime slime && !(slime instanceof MagmaCube) && slime.getSize()==1 &&
            slime.getScoreboardTags().contains("astral.split")) tinySplits.add(slime.getUniqueId());
    }
    private void tinySplitAttacks() {
        // Vanilla tiny slimes never call dealDamage, even with ATTACK_DAMAGE set. Restore contact
        // attacks only for inherited Astral children; damage events/protections/iframes still apply.
        tinySplits.removeIf(id -> {
            Entity entity=Bukkit.getEntity(id);
            if(!(entity instanceof Slime slime) || !slime.isValid() || slime.isDead()) return true;
            if(!scaledSplit(slime) || !slime.hasAI() || slime.getSize()!=1) return false;
            LivingEntity target=slime.getTarget();
            if(target!=null && !target.isDead() && target.getWorld().equals(slime.getWorld()) &&
                slime.getBoundingBox().expand(0.1).overlaps(target.getBoundingBox()))
                target.damage(slime.getAttribute(Attribute.ATTACK_DAMAGE).getValue(),slime);
            return false;
        });
    }
    public boolean pet(LivingEntity mob) {
        // 26/11: las invocaciones del Invocador (AstralClases) llevan astral.pet para que hechizos y datapack no las
        // toquen, pero tienen que poder recibir golpes de los mobs: no son mascotas invulnerables.
        if(mob.getScoreboardTags().contains("astral.invocacion")) return false;
        return mob.getScoreboardTags().stream().anyMatch(t -> t.equals("astral.pet") || t.startsWith("astral.pet."))
            || mythic(mob).startsWith("astral_pet_");
    }
    public boolean friendly(LivingEntity mob) {
        if(mob.getScoreboardTags().contains("astral.no_combat_xp")) return true;
        if(pet(mob)) return true;
        if(mob instanceof Tameable tame && tame.getOwner()!=null) {mob.addScoreboardTag("astral.no_combat_xp");return true;}
        var active=MythicBukkit.inst().getMobManager().getActiveMob(mob.getUniqueId());
        boolean owned=active.map(m -> m.getOwner().isPresent() && Set.of("astral_grillo","astral_chocobo",
            "astral_escarabajo","astral_lagarto","astral_ave","astral_pterodactilo").contains(m.getType().getInternalName())).orElse(false);
        if(owned) mob.addScoreboardTag("astral.no_combat_xp");
        return owned;
    }
    private void protectPet(LivingEntity mob) {
        if(!pet(mob)) return;
        mob.addScoreboardTag("astral.pet"); mob.setInvulnerable(true);
        mob.setFireTicks(0); mob.setFallDistance(0);
    }
    @EventHandler(priority=EventPriority.LOWEST) public void petDamage(EntityDamageEvent e) {
        if(e.getEntity() instanceof LivingEntity mob && pet(mob)) {protectPet(mob); e.setCancelled(true);}
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void petDamageFinal(EntityDamageEvent e) {
        petDamage(e);
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void petKnockback(io.papermc.paper.event.entity.EntityKnockbackEvent e) {
        if(e.getEntity() instanceof LivingEntity mob && pet(mob)) e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void petPush(io.papermc.paper.event.entity.EntityPushedByEntityAttackEvent e) {
        if(e.getEntity() instanceof LivingEntity mob && pet(mob)) e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.LOWEST) public void petAttack(io.papermc.paper.event.player.PrePlayerAttackEntityEvent e) {
        if(e.getAttacked() instanceof LivingEntity mob && pet(mob)) {protectPet(mob);e.setCancelled(true);}
    }
    @EventHandler public void petLoad(EntitiesLoadEvent e) { e.getEntities().forEach(entity -> {
        if(entity instanceof LivingEntity mob) {protectPet(mob);trackSplit(mob);}
    }); }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void petSpawn(CreatureSpawnEvent e) {
        Bukkit.getScheduler().runTask(this, () -> { if(e.getEntity().isValid()) protectPet(e.getEntity()); });
    }
    @EventHandler(priority=EventPriority.LOWEST) public void mythicPetSpawn(io.lumine.mythic.bukkit.events.MythicMobSpawnEvent e) {
        if(e.getMobType().getInternalName().startsWith("astral_pet_") && e.getEntity() instanceof LivingEntity mob) {
            mob.addScoreboardTag("astral.pet");protectPet(mob);
        }
    }
    private void claims(World w) {
        GriefPrevention.instance.config_claims_worldModes.put(w,
            w.getName().equals(survival) ? ClaimsMode.Survival : ClaimsMode.Disabled);
    }
    @EventHandler(priority=EventPriority.MONITOR) public void world(WorldLoadEvent e) { claims(e.getWorld()); }
    @EventHandler(ignoreCancelled=true) public void structures(AsyncStructureSpawnEvent e) {
        // Evento asincrono: solo datos inmutables, nunca comandos ni escrituras de mundo.
        if(!e.getWorld().getName().equals(survival) &&
            getConfig().getStringList("structure-namespaces").contains(e.getStructure().getKey().getNamespace()))
            e.setCancelled(true);
    }
    public String weaponSkill(ItemStack item) {
        if(item==null || !item.hasItemMeta()) return "";
        var meta=item.getItemMeta();
        var model=meta.getItemModel();
        if(model==null || !model.getNamespace().equals("astral")) return "";
        // Soporte: ignorar incluso requisitos heredados de versiones anteriores.
        if(model.getKey().equals("varita_curacion") || model.getKey().startsWith("talisman_")) return "";
        var req=meta.getPersistentDataContainer().get(NamespacedKey.fromString("auraskills:item_requirements"),PersistentDataType.TAG_CONTAINER);
        if(req==null) return "";
        for(String s:List.of("sorcery","archery","fighting"))
            if(req.has(NamespacedKey.fromString("auraskills:"+s),PersistentDataType.INTEGER)) return s;
        return "";
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void shoot(EntityShootBowEvent e) {
        if(!(e.getEntity() instanceof Player p)) return;
        String skill=weaponSkill(e.getBow());
        // Vanilla archery tambien usa XP por tier del mob, sin tocar fuentes tier 0.
        if(skill.isEmpty()) skill="archery";
        e.getProjectile().getPersistentDataContainer().set(skillKey,PersistentDataType.STRING,skill);
        e.getProjectile().getPersistentDataContainer().set(playerKey,PersistentDataType.STRING,p.getUniqueId().toString());
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void hit(EntityDamageEvent e) {
        if(!(e.getEntity() instanceof LivingEntity mob) || mob instanceof Player || e.getFinalDamage()<=0) return;
        Entity cause=e.getDamageSource().getCausingEntity();
        Entity direct=e.getDamageSource().getDirectEntity();
        if(friendly(mob)) {
            Player player=cause instanceof Player source ? source : mob.getKiller();
            if(player!=null && e.getFinalDamage()>=mob.getHealth()) suppressKill(player,mob);
            return;
        }
        if(!(cause instanceof Player p)) return;
        String skill;
        if(direct instanceof Projectile projectile) {
            skill=projectile.getPersistentDataContainer().get(skillKey,PersistentDataType.STRING);
            // Proyectiles sin captura (tridente, plugins) se atribuyen a la skill disponible.
            if(skill==null) skill=weaponSkill(p.getInventory().getItemInMainHand());
            if(skill.isEmpty()) skill="archery";
        } else {
            skill=weaponSkill(p.getInventory().getItemInMainHand());
            if(p.getScoreboardTags().contains("astral.caster")) skill="sorcery";
            if(skill.isEmpty()) skill="fighting";
        }
        lastSkill.put(p.getUniqueId(),skill);
        var data=mob.getPersistentDataContainer();
        String mm=mythic(mob);
        if(!mm.isEmpty()) data.set(mythicKey,PersistentDataType.STRING,mm);
        data.set(skillKey,PersistentDataType.STRING,skill);
        data.set(playerKey,PersistentDataType.STRING,p.getUniqueId().toString());
        data.set(timeKey,PersistentDataType.LONG,System.currentTimeMillis());
    }
    private String mythic(LivingEntity mob) {
        return MythicBukkit.inst().getMobManager().getActiveMob(mob.getUniqueId())
            .map(m->m.getType().getInternalName()).orElse(mob.getPersistentDataContainer().getOrDefault(mythicKey,PersistentDataType.STRING,""));
    }
    public int tier(LivingEntity mob) {
        if(mob instanceof Player || mob.getType()==EntityType.ARMOR_STAND || friendly(mob)) return 0;
        for(int t=10;t>=1;t--) if(mob.getScoreboardTags().contains("astral.mt"+t)) return t;
        for(int t=10;t>=1;t--) if(mob.getScoreboardTags().contains("astral.jm"+t)) return t;
        String mm=mythic(mob);
        if(!mm.isEmpty()) return getConfig().getInt("mythic."+mm+".tier",0);
        if(!(mob instanceof Monster)) return 0;
        return getConfig().getInt("dungeon-tiers."+mob.getWorld().getName(),0);
    }
    public String creditedSkill(LivingEntity mob, Player p) {
        return p==null?"":creditedSkill(mob,p.getUniqueId());
    }
    private String creditedSkill(LivingEntity mob, UUID player) {
        var data=mob.getPersistentDataContainer();
        Long time=data.get(timeKey,PersistentDataType.LONG);
        if(time==null || System.currentTimeMillis()-time>15000 ||
            !player.toString().equals(data.get(playerKey,PersistentDataType.STRING))) return "";
        String skill=data.get(skillKey,PersistentDataType.STRING);
        return SKILLS.contains(skill==null?"":skill) ? skill : "";
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void vanillaXp(XpGainEvent e) {
        if(e instanceof EntityXpGainEvent entity && friendly(entity.getAttacked())) {e.setCancelled(true);return;}
        if(e instanceof EntityXpGainEvent entity && SKILLS.contains(e.getSkill().getId().getKey()) &&
            tier(entity.getAttacked())>0 && !creditedSkill(entity.getAttacked(),e.getUser().getUuid()).isEmpty())
            e.setCancelled(true);
    }
    public double reward(LivingEntity mob) {
        int tier=tier(mob);
        if(tier==0) return 0;
        String mm=mythic(mob);
        boolean boss=getConfig().getBoolean("mythic."+mm+".boss",false);
        boolean elite=getConfig().getBoolean("mythic."+mm+".elite",false) ||
            mob.getScoreboardTags().stream().anyMatch(t->t.startsWith("astral.elite"));
        double sizeFactor=mob instanceof Slime slime ? (slime.getSize()==1?0.20:slime.getSize()==2?0.45:1) : 1;
        return getConfig().getDouble("xp."+tier) * getConfig().getDouble(boss?"boss-bonus":elite?"elite-bonus":"normal-bonus",1) * sizeFactor;
    }
    // 27/11 (dueno): XP del tier del jugador x4 con +1 tier, x10 con +2 o mas; tope +2.
    // Tier del jugador = requisitos reales del equipo de la skill acreditada.
    // BEGIN GENERATED SKILL TIERS
    // Generado por skill_tiers.py desde items.py/items_t6_10.py.
    private static final Map<String,int[]> SKILL_TIER_LEVELS = Map.of(
        "fighting", new int[]{4, 16, 20, 25, 30, 35, 40, 45, 50, 55},
        "sorcery", new int[]{0, 14, 20, 26, 32, 37, 42, 47, 52, 57},
        "archery", new int[]{8, 14, 20, 25, 30, 35, 40, 45, 50, 55}
    );
    // END GENERATED SKILL TIERS
    public int playerTier(Player p, String skill) {
        int level;
        try {level=AuraSkillsApi.get().getUser(p.getUniqueId()).getSkillLevel(Skills.valueOf(skill.toUpperCase(Locale.ROOT)));}
        catch(RuntimeException ex) {return 0;}
        int[] levels=SKILL_TIER_LEVELS.get(skill);
        if(levels==null) return 0;
        int tier=1;
        for(int t=levels.length;t>=1;t--) if(level>=levels[t-1]) {tier=t;break;}
        return tier;
    }
    public double tierXpFactor(Player p, String skill, int mobTier) {
        int own=playerTier(p,skill);
        if(own<=0 || mobTier<=0) return 1;
        // 26/11 (dueno): penalizacion publica, incluso sin las claves nuevas en el config del servidor.
        if(mobTier<own) {
            if(!getConfig().getBoolean("tier-penalty-enabled",true)) return 1;
            int below=Math.min(own-mobTier,2);
            return getConfig().getDouble("tier-penalty."+below,below==1?0.15:0.03);
        }
        if(mobTier==own || !p.hasPermission(getConfig().getString("tier-bonus-permission","astral.xp.tierbonus"))) return 1;
        int diff=Math.min(mobTier-own, getConfig().getInt("tier-bonus-max",2));
        double base=getConfig().getDouble("xp."+own), mob=getConfig().getDouble("xp."+mobTier);
        if(base<=0 || mob<=0) return 1;
        // Clave nueva: el antiguo tier-bonus: 5 del servidor no debe restaurar x5/x25.
        double multiplier=getConfig().getDouble("tier-bonus-multipliers."+diff,diff<=0?1:diff==1?4:10);
        return Math.max(1, base*multiplier/mob);
    }
    @EventHandler(priority=EventPriority.MONITOR) public void death(EntityDeathEvent e) {
        LivingEntity mob=e.getEntity(); Player p=mob.getKiller();
        if(friendly(mob)) {
            e.setDroppedExp(0);
            return;
        }
        if(p==null) {
            String uuid=mob.getPersistentDataContainer().get(playerKey,PersistentDataType.STRING);
            if(uuid!=null) p=Bukkit.getPlayer(UUID.fromString(uuid));
        }
        if(p==null || p.getWorld().getName().equals("lobby") || p.getGameMode()!=GameMode.SURVIVAL) return;
        String skill=creditedSkill(mob,p); double xp=reward(mob);
        if(skill.isEmpty() || xp<=0) return;
        int mobTier=tier(mob);
        // 24/11 (dueno): en mazmorras de party la XP se reparte en partes iguales entre los companeros
        // del mismo mundo; cada uno la recibe en su skill de combate y con su propio factor de tier.
        List<Player> share=partyShare(p);
        double each=xp/share.size();
        for(Player m:share) {
            String s=m.equals(p)?skill:lastSkill.getOrDefault(m.getUniqueId(),skill);
            giveXp(m,s,each*tierXpFactor(m,s,mobTier));
        }
    }
    private final Map<UUID,String> lastSkill = new HashMap<>();
    private void giveXp(Player p,String skill,double xp) {
        // Command XP no genera EntityXpGainEvent: el filtro anterior no cancela nuestro premio.
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"skills xp add "+p.getName()+" "+skill+" "+String.format(Locale.ROOT,"%.2f",xp));
    }
    @SuppressWarnings("unchecked")
    public List<Player> partyShare(Player p) {
        if(!p.hasPermission(getConfig().getString("party-split-permission","astral.xp.partysplit")) ||
            !getConfig().getStringList("party-split-worlds").contains(p.getWorld().getName())) return List.of(p);
        var party=Bukkit.getPluginManager().getPlugin("AstralParty");
        if(party==null || !party.isEnabled()) return List.of(p);
        List<Player> members;
        try {members=(List<Player>)party.getClass().getMethod("members",Player.class).invoke(party,p);}
        catch(ReflectiveOperationException|ClassCastException ex) {return List.of(p);}
        List<Player> share=new ArrayList<>();
        share.add(p);
        for(Player m:members) if(!m.equals(p) && m.isOnline() && m.getWorld().equals(p.getWorld()) &&
            m.getGameMode()==GameMode.SURVIVAL && !m.isDead()) share.add(m);
        return share;
    }
    private void suppressKill(Player player,LivingEntity mob) {
        // Las estadisticas se adjudican ANTES de EntityDeathEvent en vanilla.
        UUID id=player.getUniqueId();Map<Statistic,EntityType> pending=new EnumMap<>(Statistic.class);
        pending.put(Statistic.MOB_KILLS,mob.getType());pending.put(Statistic.KILL_ENTITY,mob.getType());
        friendlyDeaths.put(id,pending);
        Bukkit.getScheduler().runTask(this,()->friendlyDeaths.remove(id,pending));
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void friendlyStatistic(org.bukkit.event.player.PlayerStatisticIncrementEvent e) {
        var pending=friendlyDeaths.get(e.getPlayer().getUniqueId());if(pending==null)return;
        EntityType type=pending.get(e.getStatistic());
        if(type!=null && (e.getEntityType()==null || type==e.getEntityType())) {
            pending.remove(e.getStatistic());e.setCancelled(true);
        }
    }
    private PersistentDataContainer container(InventoryHolder h) {
        return h instanceof PersistentDataHolder p ? p.getPersistentDataContainer() : null;
    }
    private void update(InventoryHolder h) { if(h instanceof TileState tile) tile.update(); }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void placed(BlockPlaceEvent e) {
        if(e.getBlockPlaced().getState() instanceof TileState tile) {
            tile.getPersistentDataContainer().set(placedKey,PersistentDataType.BYTE,(byte)1); tile.update();
        }
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void placedEntity(EntityPlaceEvent e) {
        if(e.getEntity() instanceof org.bukkit.entity.minecart.StorageMinecart cart)
            cart.getPersistentDataContainer().set(placedKey,PersistentDataType.BYTE,(byte)1);
    }
    public int lootTier(String key) {
        for(String s:List.of("stronghold","bastion","ancient_city","end_city","catacomb","toxic_lair","illager_mansion","wizard","keep","structory_towers:"))
            if(key.contains(s)) return 5;
        if(key.startsWith("structory:")) return 2;
        for(String s:List.of("village","shipwreck","tavern","cabin","ruin","camp","supply_cache")) if(key.contains(s)) return 2;
        return 3;
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void loot(LootGenerateEvent e) {
        String key=e.getLootTable().getKey().toString();
        if(!e.getWorld().getName().equals(survival) || key.startsWith("astral:") || e.isPlugin()) return;
        InventoryHolder holder=e.getInventoryHolder();
        // Entidades: solo vagonetas de cofre naturales. Bloques: cofres/barriles con loot table.
        if(!(holder instanceof Chest || holder instanceof Barrel || holder instanceof org.bukkit.entity.minecart.StorageMinecart)) return;
        var data=container(holder);
        if(data==null || data.has(placedKey) || data.has(generatedKey)) return;
        int max=lootTier(key);
        List<ItemStack> additions=new ArrayList<>();
        var catalog=getConfig().getConfigurationSection("loot");
        for(String id:catalog.getKeys(false)) {
            if(catalog.getInt(id+".tier")>max || random.nextDouble()>=catalog.getDouble(id+".chance")) continue;
            var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id));
            if(table==null) { getLogger().warning("Falta item loot "+id); continue; }
            additions.addAll(table.populateLoot(random,new LootContext.Builder(e.getLootContext().getLocation()).build()));
        }
        data.set(generatedKey,PersistentDataType.BYTE,(byte)1); update(holder);
        Location location=e.getLootContext().getLocation().clone();
        // Agregar despues de llenar vanilla conserva hasta cofres llenos; excedentes caen al lado.
        getServer().getScheduler().runTask(this,()->{
            Inventory inv=holder.getInventory();
            for(ItemStack item:additions) inv.addItem(item).values().forEach(left->location.getWorld().dropItemNaturally(location,left));
        });
    }
    private static final class Shop implements InventoryHolder {
        Inventory inventory; final boolean claims;
        Shop(boolean claims) { this.claims=claims; }
        public Inventory getInventory() { return inventory; }
    }
    @EventHandler(ignoreCancelled=true) public void open(InventoryOpenEvent e) {
        String title=e.getView().getTitle();
        if(!(e.getPlayer() instanceof Player p) || (!title.equals("Astral - Proteccion") && !title.equals("Astral - Mochilas"))) return;
        boolean claims=title.equals("Astral - Proteccion");
        getServer().getScheduler().runTask(this,()->{
            if(!p.isOnline() || p.getOpenInventory().getTopInventory()!=e.getInventory()) return;
            Shop shop=new Shop(claims);
            shop.inventory=Bukkit.createInventory(shop,9,claims?"Proteccion - comprar area":"Mochilas Astrales");
            var packages=getConfig().getMapList(claims?"claim-packages":"backpack-packages");
            for(int i=0;i<packages.size();i++) {
                var row=packages.get(i);
                ItemStack item=new ItemStack(claims?Material.GOLDEN_SHOVEL:Material.CHEST);
                var meta=item.getItemMeta();
                meta.setDisplayName((claims?row.get("blocks")+" bloques":"Mochila de "+row.get("name")+" ("+row.get("slots")+" espacios)")+" - $"+row.get("price"));
                meta.setLore(List.of(claims?"Suma area; no define un lado del terreno.":"Se entrega como item. Clic derecho para abrirla.","Click izquierdo para comprar."));
                item.setItemMeta(meta); shop.inventory.setItem(i,item);
            }
            p.openInventory(shop.inventory);
        });
    }
    @EventHandler public void drag(InventoryDragEvent e) { if(e.getInventory().getHolder() instanceof Shop) e.setCancelled(true); }
    @SuppressWarnings({"rawtypes","unchecked"})
    @EventHandler public void buy(InventoryClickEvent e) {
        if(!(e.getView().getTopInventory().getHolder() instanceof Shop shop)) return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p) || !e.isLeftClick() || e.getRawSlot()<0) return;
        var packages=getConfig().getMapList(shop.claims?"claim-packages":"backpack-packages");
        if(e.getRawSlot()>=packages.size() || !buying.add(p.getUniqueId())) return;
        try {
            var row=packages.get(e.getRawSlot());
            if(!shop.claims && Bukkit.getPluginManager().getPlugin("ExpendableBackpacks")==null) {
                p.sendMessage("Las mochilas no estan disponibles; avisa al administrador."); return;
            }
            // La mochila es un item: sin lugar libre se perderia. Revisar antes de cobrar.
            if(!shop.claims && p.getInventory().firstEmpty()==-1) {
                p.sendMessage("Libera un espacio del inventario para recibir la mochila."); return;
            }
            var vault=Bukkit.getPluginManager().getPlugin("Vault");
            if(vault==null) throw new IllegalStateException("Falta Vault");
            Class economy=Class.forName("net.milkbowl.vault.economy.Economy",true,vault.getClass().getClassLoader());
            var registration=Bukkit.getServicesManager().getRegistration(economy);
            if(registration==null) throw new IllegalStateException("Falta proveedor de economia");
            Object provider=registration.getProvider();
            double price=((Number)row.get("price")).doubleValue();
            String command=shop.claims?"griefprevention:adjustbonusclaimblocks "+p.getName()+" "+row.get("blocks"):
                "backpack give "+p.getName()+" "+row.get("tier");
            Object result=economy.getMethod("withdrawPlayer",OfflinePlayer.class,double.class).invoke(provider,p,price);
            if(!(boolean)result.getClass().getMethod("transactionSuccess").invoke(result)) { p.sendMessage("No tenes saldo suficiente."); return; }
            if(!Bukkit.dispatchCommand(Bukkit.getConsoleSender(),command)) {
                economy.getMethod("depositPlayer",OfflinePlayer.class,double.class).invoke(provider,p,price);
                p.sendMessage("No se completo la compra; saldo devuelto."); return;
            }
            p.sendMessage(shop.claims?"Bloques sumados a tu saldo de proteccion.":"Mochila comprada. Clic derecho con ella en la mano para abrirla.");
            p.closeInventory();
        } catch(ReflectiveOperationException | IllegalStateException ex) {
            getLogger().warning("Compra no disponible: "+ex); p.sendMessage("La tienda no esta disponible; avisa al administrador.");
        } finally { buying.remove(p.getUniqueId()); }
    }
}
