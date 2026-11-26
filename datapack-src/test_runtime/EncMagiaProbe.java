package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
import dev.aurelium.auraskills.api.AuraSkillsApi;

/** Prueba local: APIs reales y jugadores NMS. No se instala en producción. */
public final class EncMagiaProbe extends JavaPlugin implements Listener {
    Player owner, other; AstralMesa mesa; int failures;
    LivingEntity echoTarget; double echoDamage; int echoHits;
    void check(boolean ok,String message) { if(!ok) failures++; getLogger().info("MAGIA "+(ok?"PASS ":"FAIL ")+message); }
    void near(double actual,double wanted,String message) {check(Math.abs(actual-wanted)<.001,message+" actual="+actual+" esperado="+wanted);}
    Player fake(String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes(("EncMagia"+name).getBytes()),name);
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        world.getWorld().getChunkAt(0,0).setForceLoaded(true); fake.setPos(0,100,0); world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);field.setAccessible(true);
            ((Map)field.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        Player p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(p,net.kyori.adventure.text.Component.empty()));
        return p;
    }
    @Override public void onEnable() {Bukkit.getPluginManager().registerEvents(this,this);}
    @EventHandler public void regen(dev.aurelium.auraskills.api.event.mana.ManaRegenerateEvent e) {e.setCancelled(true);}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void echoHit(EntityDamageByEntityEvent e) {if(e.getEntity()==echoTarget) {echoDamage+=e.getFinalDamage();echoHits++;}}
    ItemStack item(String id) {
        return Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id)).populateLoot(new Random(),new org.bukkit.loot.LootContext.Builder(owner.getLocation()).build()).iterator().next();
    }
    org.bukkit.enchantments.Enchantment ench(String id) {return Registry.ENCHANTMENT.get(NamespacedKey.fromString("astral:"+id));}
    Set<String> options(Player p,ItemStack item) {
        var set=new HashSet<String>();for(var o:mesa.opciones(p,item)) if(o.ench().getKey().getNamespace().equals("astral"))set.add(o.ench().getKey().getKey());return set;
    }
    void cmd(String c) {Bukkit.dispatchCommand(Bukkit.getConsoleSender(),c);}
    int score(String key) {return Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp").getScore(key).getScore();}
    void call(String name,Class<?>[] types,Object... args) throws Exception {
        var m=mesa.magia.getClass().getDeclaredMethod(name,types);m.setAccessible(true);m.invoke(mesa.magia,args);
    }
    EntityDamageByEntityEvent spell(Player p,LivingEntity mob,double amount) {
        p.addScoreboardTag("astral.caster");mob.addScoreboardTag("astral.spell.hit");
        var source=org.bukkit.damage.DamageSource.builder(org.bukkit.damage.DamageType.MAGIC).withCausingEntity(p).withDirectEntity(p).build();
        var e=new EntityDamageByEntityEvent(p,mob,EntityDamageEvent.DamageCause.MAGIC,source,amount);
        Bukkit.getPluginManager().callEvent(e);
        p.removeScoreboardTag("astral.caster");mob.removeScoreboardTag("astral.spell.hit");return e;
    }
    public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String label,String[] a) {
        try {
            if(a[0].equals("start")) { mesa=(AstralMesa)Bukkit.getPluginManager().getPlugin("AstralMesa"); owner=fake("ByTrainx");other=fake("MagiaOther");return true; }
            // Paper encola dispatchCommand anidado dentro de otro comando. Fuera de ese contexto,
            // los comandos se ejecutan antes de comprobar sus resultados.
            if(a[0].equals("run")) { Bukkit.getScheduler().runTask(this,()->onCommand(s,c,label,new String[]{"checks"}));return true; }
            cmd("encmagia privado");
            var staff=item("baston_1");
            check(options(owner,staff).equals(Set.of("poder_arcano","fluidez","sifon_mana","marca_arcana","sabio_arcano","eco_arcano","escudo_mana")),"mesa bastón: 7 y sin Bendición");
            check(options(other,staff).isEmpty(),"mesa oculta para otro jugador incluso con objeto Astral");
            check(options(owner,new ItemStack(Material.CARROT_ON_A_STICK)).isEmpty(),"material vanilla no acepta magia");
            check(options(owner,item("varita_curacion")).equals(Set.of("bendicion","sabio_arcano","escudo_mana")),"varita cura: 3 exactos");
            check(options(owner,item("varita_estallido")).equals(Set.of("sifon_mana","sabio_arcano","escudo_mana")),"varita estallido: 3 exactos");
            var definitive=staff.clone();definitive.addUnsafeEnchantment(ench("sabio_arcano"),1);
            check(!options(owner,definitive).contains("eco_arcano")&&!options(owner,definitive).contains("escudo_mana"),"definitivos excluyentes");
            check(ench("sabio_arcano").conflictsWith(ench("eco_arcano")),"exclusive_set cargado por Minecraft");
            owner.getInventory().setItemInMainHand(staff);
            cmd("scoreboard players set ByTrainx astral.cd 0");
            cmd("execute as ByTrainx at @s run function astral:spell/cast");
            int base=score("#base"),pct=score("#pct"),cd=score("#cd");
            staff.addUnsafeEnchantment(ench("poder_arcano"),5);staff.addUnsafeEnchantment(ench("fluidez"),4);staff.addUnsafeEnchantment(ench("sabio_arcano"),5);
            owner.getInventory().setItemInMainHand(staff);var u=AuraSkillsApi.get().getUser(owner.getUniqueId());u.setMana(100);
            cmd("encmagiapago ByTrainx");near(u.getMana(),60,"Sabio V cobra 40 de 50 mediante asw_pay real");
            cmd("scoreboard players set ByTrainx astral.cd 0");cmd("execute as ByTrainx at @s run function astral:spell/cast");
            check(score("#pct")==pct+20,"Poder V suma 20% al cast real");check(score("#base")>base,"cast real aumenta daño");check(score("#cd")<cd,"Fluidez IV reduce recarga");
            other.getInventory().setItemInMainHand(staff);var v=AuraSkillsApi.get().getUser(other.getUniqueId());v.setMana(100);
            cmd("encmagiapago MagiaOther");near(v.getMana(),50,"Sabio no beneficia otro jugador en privado");
            cmd("scoreboard players set MagiaOther astral.cd 0");cmd("execute as MagiaOther at @s run function astral:spell/cast");
            check(score("#pct")==pct,"Poder inerte para otro jugador");check(score("#cd")==cd,"Fluidez inerte para otro jugador");
            staff=item("baston_1");staff.addUnsafeEnchantment(ench("sifon_mana"),3);staff.addUnsafeEnchantment(ench("marca_arcana"),3);
            owner.getInventory().setItemInMainHand(staff);other.getInventory().setItemInMainHand(staff);
            var mob=owner.getWorld().spawn(owner.getLocation().add(3,0,0),Zombie.class);mob.setAI(false);
            u.setMana(0);call("begin",new Class<?>[]{Player.class},owner);
            near(spell(owner,mob,100).getDamage(),100,"primer hechizo aplica marca después del daño");
            near(u.getMana(),u.getMaxMana()*.03,"Sifón III restaura 3% máximo");
            near(spell(owner,mob,100).getDamage(),112,"marca III potencia siguiente hechizo 12%");
            near(u.getMana(),u.getMaxMana()*.03,"Sifón una vez por lanzamiento");
            near(spell(other,mob,100).getDamage(),100,"marca no beneficia otro jugador en privado");
            cmd("encmagia publico");
            check(!options(other,item("baston_1")).isEmpty(),"publico habilita mesa inmediatamente");
            near(spell(other,mob,100).getDamage(),112,"marca beneficia hechizo de cualquiera en público");
            cmd("encmagia privado");
            check(!other.getScoreboardTags().contains("astral.encmagia"),"privado retira tag inmediatamente");
            staff=item("baston_1");staff.addUnsafeEnchantment(ench("escudo_mana"),3);owner.getInventory().setItemInMainHand(staff);u.setMana(2);
            var source=org.bukkit.damage.DamageSource.builder(org.bukkit.damage.DamageType.GENERIC).build();
            var hit=new EntityDamageEvent(owner,EntityDamageEvent.DamageCause.CUSTOM,source,10);
            Bukkit.getPluginManager().callEvent(hit);near(hit.getFinalDamage(),8,"Escudo limitado a maná disponible");near(u.getMana(),0,"1 maná = 1 vida, sin saldo negativo");
            var wand=item("varita_curacion");wand.addUnsafeEnchantment(ench("bendicion"),3);owner.getInventory().setItemInMainHand(wand);
            owner.setHealth(1);call("heal",new Class<?>[]{Player.class,double.class,int.class,double.class},owner,7.0,5,5.0);call("healTick",new Class<?>[]{});
            near(owner.getHealth(),1+owner.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue()*.065,"Bendición III cura 30% más");
            other.teleport(owner.getLocation().add(8,0,0));other.setHealth(1);
            var party=Bukkit.getPluginManager().getPlugin("AstralParty");
            var groups=(Map)party.getClass().getField("groups").get(party);
            var leadersField=party.getClass().getDeclaredField("leaders");leadersField.setAccessible(true);
            var leaders=(Map)leadersField.get(party);
            groups.put(owner.getUniqueId(),new LinkedHashSet<>(List.of(owner.getUniqueId(),other.getUniqueId())));
            leaders.put(owner.getUniqueId(),owner.getUniqueId());leaders.put(other.getUniqueId(),owner.getUniqueId());
            call("heal",new Class<?>[]{Player.class,double.class,int.class,double.class},owner,7.0,5,5.0);call("healTick",new Class<?>[]{});
            check(other.getHealth()>1,"Bendición alcanza party a 8 bloques con radio 7");
            other.teleport(owner.getLocation().add(10,0,0));other.setHealth(1);
            var healingField=mesa.magia.getClass().getDeclaredField("healing");healingField.setAccessible(true);((Map)healingField.get(mesa.magia)).clear();
            call("heal",new Class<?>[]{Player.class,double.class,int.class,double.class},owner,7.0,5,5.0);call("healTick",new Class<?>[]{});
            near(other.getHealth(),1,"Bendición no excede radio +2");
            mob.remove();
            var marksField=mesa.magia.getClass().getDeclaredField("marks");marksField.setAccessible(true);((Map)marksField.get(mesa.magia)).clear();
            staff=item("baston_1");staff.addUnsafeEnchantment(ench("eco_arcano"),3);staff.addUnsafeEnchantment(ench("sifon_mana"),3);
            owner.getInventory().setItemInMainHand(staff);owner.teleport(new Location(owner.getWorld(),0,100,0,0,0));u.setMana(0);
            echoTarget=owner.getWorld().spawn(new Location(owner.getWorld(),0,100,4),Zombie.class);
            echoTarget.setAI(false);echoTarget.setGravity(false);echoTarget.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).setBaseValue(1000);echoTarget.setHealth(1000);
            // Reproduce la inmunidad real del golpe original: el eco menor a los 4 ticks debe pegar igual.
            var original=echoTarget;echoTarget=null;original.damage(100,owner);echoTarget=original;
            var randomField=mesa.magia.getClass().getDeclaredField("random");randomField.setAccessible(true);randomField.set(mesa.magia,(java.util.function.DoubleSupplier)()->0.0);
            var tmp=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp");tmp.getScore("#base").setScore(100);tmp.getScore("#sk").setScore(1);
            call("echo",new Class<?>[]{Player.class},owner);
            near(echoDamage,0,"Eco no sale inmediatamente");
            Bukkit.getScheduler().runTaskLater(this,()->near(echoDamage,0,"Eco espera los primeros 3 ticks"),3);
            Bukkit.getScheduler().runTaskLater(this,()->{
                near(echoDamage,50,"Eco real pega la mitad a los 4 ticks");
                near(u.getMana(),0,"Eco no da Sifón ni cobra maná");
            },7);
            Bukkit.getScheduler().runTaskLater(this,()->{
                check(echoHits==1,"Eco no genera otro eco");echoTarget.remove();
                getLogger().info("MAGIA RESULT failures="+failures);
            },12);
        } catch(Throwable ex) {failures++;getLogger().log(java.util.logging.Level.SEVERE,"MAGIA FAIL exception",ex);}
        return true;
    }
}
