package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import astral.AstralProgression;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.CraftServer;
import org.bukkit.craftbukkit.CraftWorld;
import com.mojang.authlib.GameProfile;

/** Prueba de eventos reales; no instala este plugin en remoto. */
public final class Tanda17Probe extends JavaPlugin implements Listener {
    Player p;int failures;AstralProgression runtime;UUID text;
    void check(boolean ok,String name){if(!ok)failures++;getLogger().info("T17 "+(ok?"PASS ":"FAIL ")+name);}
    void cmd(String s){
        if(s.startsWith("oceano ")) {
            var args=s.split(" ");Bukkit.getPluginCommand("oceano").execute(Bukkit.getConsoleSender(),"oceano",Arrays.copyOfRange(args,1,args.length));
        } else Bukkit.dispatchCommand(Bukkit.getConsoleSender(),s);
    }
    public void onEnable(){Bukkit.getPluginManager().registerEvents(this,this);}
    @EventHandler(priority=EventPriority.MONITOR) public void horseDamage(EntityDamageEvent e) {
        if(e.getEntity() instanceof Horse horse)getLogger().info("T17 horse damage cancelled="+e.isCancelled()+" final="+e.getFinalDamage()+" pet="+runtime.pet(horse));
    }
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String label,String[] a){
      try {
        runtime=(AstralProgression)Bukkit.getPluginManager().getPlugin("AstralProgression");
        switch(a[0]) {
        case "player" -> {
            var server=((CraftServer)Bukkit.getServer()).getServer();
            var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
            var profile=new GameProfile(UUID.fromString("0dfec263-052c-4bf9-b35b-36af3d034112"),"ProtectProbe");
            var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
            var connection=new Connection(PacketFlow.SERVERBOUND);connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
            connection.channel.pipeline().addLast("packet_handler",connection);connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
            fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
            fake.setPos(0,-59,0);world.addNewPlayer(fake);var list=server.getPlayerList();list.players.add(fake);
            for(String name:List.of("playersByUUID","playersByName")) {
                var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(name);field.setAccessible(true);
                ((Map)field.get(list)).put(name.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
            }
            p=fake.getBukkitEntity();p.setOp(true);p.setGameMode(GameMode.SURVIVAL);p.setInvulnerable(true);
            me.ryanhamshire.GriefPrevention.GriefPrevention.instance.config_claims_worldModes.put(p.getWorld(),me.ryanhamshire.GriefPrevention.ClaimsMode.Disabled);
            me.ryanhamshire.GriefPrevention.GriefPrevention.instance.config_claims_protectHorses=false;
            me.ryanhamshire.GriefPrevention.GriefPrevention.instance.config_claims_protectCreatures=false;
            me.ryanhamshire.GriefPrevention.GriefPrevention.instance.config_pvp_protectPets=false;
            // Aislar la vulnerabilidad/XP de nuestras entidades de las protecciones de GP.
            HandlerList.unregisterAll(me.ryanhamshire.GriefPrevention.GriefPrevention.instance);
            Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(p,net.kyori.adventure.text.Component.empty()));
            AuraSkillsApi.get().getUserManager().loadUser(p.getUniqueId());
            io.lumine.mythic.bukkit.MythicBukkit.inst().getPlayerManager().loadProfile(p);
        }
        case "damage" -> {
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());check(user.isLoaded(),"AuraSkills cargado");
            for(var skill:List.of(Skills.FIGHTING,Skills.ARCHERY,Skills.SORCERY)){user.setSkillLevel(skill,25);user.setSkillXp(skill,0);}
            int kills=p.getStatistic(Statistic.MOB_KILLS);
            Pig pet=p.getWorld().spawn(p.getLocation().add(2,0,0),Pig.class);pet.setAI(false);pet.addScoreboardTag("astral.pet");
            pet.addScoreboardTag("astral.mt5");double health=pet.getHealth();
            var arrow=p.launchProjectile(Arrow.class);arrow.setGravity(false);
            for(var type:List.of(org.bukkit.damage.DamageType.PLAYER_ATTACK,org.bukkit.damage.DamageType.ARROW,org.bukkit.damage.DamageType.MAGIC,
                org.bukkit.damage.DamageType.EXPLOSION,org.bukkit.damage.DamageType.LAVA,org.bukkit.damage.DamageType.FALL,org.bukkit.damage.DamageType.DROWN)){
                pet.setInvulnerable(false); pet.setNoDamageTicks(0);
                pet.damage(1000,org.bukkit.damage.DamageSource.builder(type).withCausingEntity(p).withDirectEntity(type==org.bukkit.damage.DamageType.ARROW?arrow:p).build());
                check(!pet.isDead() && pet.getHealth()==health,"vida intacta "+type);
            }
            arrow.remove();check(pet.isInvulnerable(),"Invulnerable vanilla migrado");check(runtime.reward(pet)==0,"sin recompensa propia");
            check(p.getStatistic(Statistic.MOB_KILLS)==kills,"mascota sin bajas");
            Bukkit.getScheduler().runTaskLater(this,()->{
                for(var skill:List.of(Skills.FIGHTING,Skills.ARCHERY,Skills.SORCERY))check(user.getSkillXp(skill)==0,"mascota sin XP "+skill);
                pet.remove();
            },2);
        }
        case "mount" -> {
            Horse mount=p.getWorld().spawn(p.getLocation().add(3,0,0),Horse.class);mount.setOwner(p);mount.setAI(false);
            mount.addScoreboardTag("astral.mt5");
            int kills=p.getStatistic(Statistic.MOB_KILLS),horses=p.getStatistic(Statistic.KILL_ENTITY,EntityType.HORSE);
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());user.setSkillXp(Skills.FIGHTING,0);
            Bukkit.getScheduler().runTaskLater(this,()->{
            mount.setNoDamageTicks(0);mount.damage(2,p);check(!mount.isInvulnerable(),"montura sigue vulnerable");
            check(runtime.reward(mount)==0,"montura sin recompensa");mount.setNoDamageTicks(0);mount.damage(1000,p);check(mount.isDead(),"montura muere por dano real");
            Bukkit.getScheduler().runTaskLater(this,()->{
                check(user.getSkillXp(Skills.FIGHTING)==0,"montura sin XP por dano ni muerte");
                check(p.getStatistic(Statistic.MOB_KILLS)==kills,"montura sin MOB_KILLS");
                check(p.getStatistic(Statistic.KILL_ENTITY,EntityType.HORSE)==horses,"montura sin KILL_ENTITY");
            },2);
            },5);
        }
        case "mythic" -> {
            for(String id:List.of("fenix","ghastito","bombardero","canonero","encapuchado","llamita","hondero","saqueador","brujita","desierto","jungla","frondoso","micelio","pradera","sabana","nieve","pantano","honguito")) {
                LivingEntity mob=(LivingEntity)io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_pet_"+id,p.getLocation().add(3,0,3));
                check(mob.getScoreboardTags().contains("astral.pet") && mob.isInvulnerable(),"Mythic onSpawn "+id);
                Bukkit.getScheduler().runTaskLater(this,()->{check(mob.getScoreboardTags().contains("astral.pet") && mob.isInvulnerable(),"Mythic despues de skills "+id);mob.remove();},2);
            }
        }
        case "legacy" -> {
            for(String id:List.of("lobo","cuervo","golem","zorro","dragon")) {
                Pig mob=p.getWorld().spawn(p.getLocation().add(3,0,3),Pig.class);mob.addScoreboardTag("astral.pet."+id);mob.setNoDamageTicks(0);
                mob.damage(1000,p);check(!mob.isDead() && mob.isInvulnerable() && mob.getScoreboardTags().contains("astral.pet"),"migra retirada "+id);mob.remove();
            }
        }
        case "normal" -> {
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());user.setSkillXp(Skills.FIGHTING,0);
            Zombie mob=p.getWorld().spawn(p.getLocation().add(4,0,0),Zombie.class);mob.setAI(false);mob.addScoreboardTag("astral.mt2");
            check(runtime.reward(mob)>0,"hostil conserva recompensa");int kills=p.getStatistic(Statistic.MOB_KILLS);mob.damage(10000,p);
            Bukkit.getScheduler().runTaskLater(this,()->{
                check(user.getSkillXp(Skills.FIGHTING)>0,"hostil da XP real");
                check(p.getStatistic(Statistic.MOB_KILLS)==kills+1,"hostil suma baja");
            },2);
        }
        case "save" -> {
            World w=Bukkit.getWorld("oceano");if(w==null)w=Bukkit.createWorld(new WorldCreator("oceano").generator("AstralOceano"));
            w.getBlockAt(64,60,64).setType(Material.DIAMOND_BLOCK);w.getBlockAt(65,60,64).setType(Material.WATER);
            w.spawn(new Location(w,64.5,62,64.5),TextDisplay.class,e->{e.text(net.kyori.adventure.text.Component.text("Barco Astral"));e.setPersistent(true);});
            cmd("oceano decor guardar barco_probe 64 60 64 115 64 65");
            check(getDataFolder().toPath().getParent().resolve("AstralOceano/decor/barco_probe/estructura.nbt").toFile().exists(),"estructura mayor de 48 guardada");
            cmd("oceano decor poner barco_probe");cmd("oceano decor poner barco_probe");verifyDecor();
        }
        case "regen" -> {cmd("oceano regenerar");}
        case "verify" -> verifyDecor();
        case "restart" -> {
            // Sin Multiverse en este ensayo, cargar explicitamente el mundo secundario existente.
            if(Bukkit.getWorld("oceano")==null)Bukkit.createWorld(new WorldCreator("oceano").generator("AstralOceano"));
            cmd("oceano decor poner barco_probe");verifyDecor();
        }
        case "result" -> getLogger().info("T17 RESULT failures="+failures);
        }
      }catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"T17 FAIL exception",ex);}
      return true;
    }
    void verifyDecor(){
        World w=Bukkit.getWorld("oceano");check(w!=null,"oceano cargado");if(w==null)return;
        check(w.getBlockAt(64,60,64).getType()==Material.DIAMOND_BLOCK,"bloque restaurado");
        check(w.getBlockAt(65,60,64).getType()==Material.WATER,"agua restaurada");
        var displays=w.getEntitiesByClass(TextDisplay.class).stream().filter(e->e.getScoreboardTags().contains("astral.oceano.decor.barco_probe")).toList();
        check(displays.size()==1,"holograma una sola vez: "+displays.size());
        if(displays.size()==1){var e=displays.getFirst();check(e.getLocation().distance(new Location(w,64.5,62,64.5))<.001,"posicion exacta");
            check(net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(e.text()).equals("Barco Astral"),"texto exacto");}
    }
}
