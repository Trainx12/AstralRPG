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
public final class CorreccionesProbe extends JavaPlugin {
    Player player;int failures;final List<String> crateCalls=new ArrayList<>();
    final NamespacedKey until=new NamespacedKey("astral","suerte_hasta");
    void check(boolean ok,String text){if(!ok)failures++;getLogger().info("CORR "+(ok?"PASS ":"FAIL ")+text);}
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("AstralXPProbe".getBytes()),"XPProbe");
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
    void click(EquipmentSlot hand,boolean deny) {
        var e=new PlayerInteractEvent(player,Action.RIGHT_CLICK_AIR,player.getInventory().getItem(hand),null,null,hand);
        if(deny)e.setUseItemInHand(org.bukkit.event.Event.Result.DENY);
        Bukkit.getPluginManager().callEvent(e);
    }
    void invoke(String name,Player p) throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");var m=plugin.getClass().getDeclaredMethod(name,Player.class);m.setAccessible(true);m.invoke(plugin,p);
    }
    void later(long ticks,Runnable task){Bukkit.getScheduler().runTaskLater(this,()->{try{task.run();}catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"CORR FAIL delayed",ex);}},ticks);}
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
        try {
            if(player==null)player=fake();
            var runtime=Bukkit.getPluginManager().getPlugin("AstralDecor");
            switch(args[0]) {
            case "xp" -> {
                String[] ids={"frasco_xp_pequeno","frasco_xp_grande","frasco_xp_gigante","barril_xp"};
                int[] values={60,200,550,5500};
                for(int j=0;j<ids.length;j++) {
                    final int i=j;
                    later(1+i*6,()->{
                    player.setTotalExperience(0);player.setLevel(0);player.setExp(0);player.setSneaking(false);
                    player.getInventory().setItemInMainHand(item(ids[i],3));click(EquipmentSlot.HAND,false);
                    check(player.getTotalExperience()==values[i],ids[i]+" XP unitaria real");
                    check(player.getInventory().getItemInMainHand().getAmount()==2,"consume uno");
                    later(3,()->{player.setSneaking(true);click(EquipmentSlot.HAND,false);
                        check(player.getTotalExperience()==values[i]*3,"Shift usa resto del stack");player.setSneaking(false);});
                    });
                }
                player.setSneaking(false);
            }
            case "neutral" -> {
                player.setGameMode(GameMode.SURVIVAL);player.setInvulnerable(false);
                var gob=(org.bukkit.entity.Mob)io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_goblin_vendedor",player.getLocation().clone().add(3,0,0));
                check(gob.getTarget()==null,"mercader sin objetivo inicial");
                var field=runtime.getClass().getDeclaredField("merchant");field.setAccessible(true);var merchant=field.get(runtime);
                var entity=merchant.getClass().getDeclaredField("merchant");entity.setAccessible(true);entity.set(merchant,gob);
                var expires=merchant.getClass().getDeclaredField("expires");expires.setAccessible(true);expires.set(merchant,Bukkit.getCurrentTick()+6000);
                later(2,()->{
                check(gob.getScoreboardTags().contains("astral.mercader"),"identificado tras onSpawn");
                var target=new org.bukkit.event.entity.EntityTargetLivingEntityEvent(gob,player,org.bukkit.event.entity.EntityTargetEvent.TargetReason.CLOSEST_PLAYER);
                Bukkit.getPluginManager().callEvent(target);check(target.isCancelled(),"rechaza jugador que no ataco");
                gob.damage(1,player);
                try {var a=merchant.getClass().getDeclaredField("aggressor");a.setAccessible(true);
                    check(player.getUniqueId().equals(a.get(merchant)),"registra primer agresor");}
                catch(Exception ex){throw new RuntimeException(ex);}
                later(1,()->check(player.equals(gob.getTarget()),"persigue al agresor"));
                var stranger=player.getWorld().spawn(player.getLocation(),org.bukkit.entity.Zombie.class);
                var other=new org.bukkit.event.entity.EntityTargetLivingEntityEvent(gob,stranger,org.bukkit.event.entity.EntityTargetEvent.TargetReason.CLOSEST_ENTITY);
                Bukkit.getPluginManager().callEvent(other);check(other.isCancelled(),"no cambia a otro objetivo");stranger.remove();
                later(2,()->{gob.remove();player.setInvulnerable(true);});
                });
            }
            case "tiers" -> {
                for(String kind:List.of("bosque","hielo","cristal")) {
                    var mob=(org.bukkit.entity.LivingEntity)io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_golem_"+kind+"_infinita",player.getLocation().clone().add(8,0,0));
                    later(2,()->{
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute as "+mob.getUniqueId()+" at @s run function astral:inf/apply/t4");
                    later(2,()->{
                    check(mob.getScoreboardTags().contains("astral.mt4"),kind+" tier IV real");
                    check(mob.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue()>1000,kind+" vida escalada");
                    check(mob.getScoreboardTags().contains("astral.hpname"),kind+" nombre con vida");
                    check(mob.getScoreboardTags().contains("inf.mob"),kind+" pertenece al limite Infinita");
                    mob.remove();
                    });});
                }
            }
            case "result" -> getLogger().info("CORR RESULT failures="+failures);
            }
        } catch(Throwable ex){failures++;getLogger().log(java.util.logging.Level.SEVERE,"CORR FAIL exception",ex);}
        return true;
    }
}
