package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.world.*;
import org.bukkit.inventory.*;
import org.bukkit.loot.LootContext;
import org.bukkit.plugin.java.JavaPlugin;
import astral.AstralProgression;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;
import me.ryanhamshire.GriefPrevention.GriefPrevention;
import me.ryanhamshire.GriefPrevention.ClaimsMode;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import org.bukkit.craftbukkit.CraftServer;
import org.bukkit.craftbukkit.CraftWorld;
import com.mojang.authlib.GameProfile;

public final class SupportTierProbe extends JavaPlugin {
    Player p; int failures; double before,baseline=-1; LivingEntity target; String held;
    AstralProgression runtime;
    void check(boolean ok,String msg) { if(!ok) failures++; getLogger().info("T5A "+(ok?"PASS ":"FAIL ")+msg); }
    ItemStack item(String id) {
        var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id));
        return table.populateLoot(new Random(0),new LootContext.Builder(p.getLocation()).build()).iterator().next();
    }
    void cmd(String command) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(),command); }
    public boolean onCommand(CommandSender sender,Command c,String label,String[] args) {
      try {
        runtime=(AstralProgression)Bukkit.getPluginManager().getPlugin("AstralProgression");
        if(args[0].equals("player")) {
            var server=((CraftServer)Bukkit.getServer()).getServer();
            var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
            var profile=new GameProfile(UUID.fromString("173b8ccf-b657-4093-bc4c-7c8527d0a502"),"TandaProbe");
            var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
            var connection=new Connection(PacketFlow.SERVERBOUND);
            connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
            connection.channel.pipeline().addLast("packet_handler",connection);
            connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
            fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
            fake.setPos(0,-59,0);world.addNewPlayer(fake);
            var list=server.getPlayerList();list.players.add(fake);
            for(String name:List.of("playersByUUID","playersByName")) {
                var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(name);field.setAccessible(true);
                ((Map)field.get(list)).put(name.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
            }
            p=fake.getBukkitEntity();p.setOp(true);p.setGameMode(GameMode.SURVIVAL);p.setInvulnerable(true);
            Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(p,net.kyori.adventure.text.Component.empty()));
            AuraSkillsApi.get().getUserManager().loadUser(p.getUniqueId());
            var permission=p.addAttachment(this);permission.setPermission("auraskills.skill.sorcery",true);
            io.lumine.mythic.bukkit.MythicBukkit.inst().getPlayerManager().loadProfile(p);
        } else if(args[0].equals("support")) {
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());
            user.setSkillLevel(Skills.FIGHTING,16);user.setSkillLevel(Skills.SORCERY,42);
            p.getInventory().clear();p.getInventory().setItemInMainHand(item("espada_2"));
            p.getInventory().setItem(9,item(args[1]));p.getInventory().setItemInOffHand(item(args[1]));
            cmd("execute as "+p.getName()+" run function astral:player/lvl");
            check(runtime.weaponSkill(item(args[1])).isEmpty(),args[1]+" sin skill");
        } else if(args[0].equals("scores")) {
            for(String score:List.of("astral.wt","astral.lvl")) check(Bukkit.getScoreboardManager().getMainScoreboard().getObjective(score).getScore(p.getName()).getScore()==2,args[1]+" "+score+"=2");
        } else if(args[0].equals("kill")) {
            held=args[1];p.getInventory().clear();
            p.getInventory().setItemInMainHand(held.equals("varita_curacion")?item(held):new ItemStack(Material.IRON_SWORD));
            if(held.equals("varita_inventario")) p.getInventory().setItem(9,item("varita_curacion"));
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());before=user.getSkillXp(Skills.FIGHTING);
            Zombie mob=p.getWorld().spawn(p.getLocation().add(2,0,0),Zombie.class);target=mob;mob.setAI(false);mob.addScoreboardTag("astral.mt2");
            check(runtime.tierXpFactor(p,"fighting",2)==1,held+" factor XP T2 completo");
            mob.damage(100000,p);
        } else if(args[0].equals("xpcheck")) {
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());
            check(runtime.creditedSkill(target,p).equals("fighting"),held+" acredita Combate");
            double gain=user.getSkillXp(Skills.FIGHTING)-before;
            check(gain>0,held+" otorga XP real: "+gain);
            if(baseline<0) baseline=gain;
            else check(Math.abs(gain-baseline)<0.01,"varita misma XP que sin varita: "+gain+" = "+baseline);
        } else if(args[0].equals("tiers")) {
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());
            String[] names={"fighting","sorcery","archery"};
            Skills[] skills={Skills.FIGHTING,Skills.SORCERY,Skills.ARCHERY};
            int[][] requirements={{4,16,20,25,30,35,40,45,50,55},
                {0,14,20,26,32,37,42,47,52,57},{8,14,20,25,30,35,40,45,50,55}};
            var attachment=p.addAttachment(this);
            attachment.setPermission("astral.xp.tierbonus",true);
            for(int s=0;s<names.length;s++) for(int t=1;t<10;t++) {
                int level=requirements[s][t];
                user.setSkillLevel(skills[s],level-1);
                check(runtime.playerTier(p,names[s])==t,names[s]+" antes T"+(t+1));
                check(runtime.tierXpFactor(p,names[s],t)==1,names[s]+" sin penalizacion prematura T"+t);
                user.setSkillLevel(skills[s],level);
                check(runtime.playerTier(p,names[s])==t+1,names[s]+" alcanza T"+(t+1));
                check(Math.abs(runtime.tierXpFactor(p,names[s],t)-0.15)<1e-9,names[s]+" penalizacion legitima");
            }
            user.setSkillLevel(Skills.FIGHTING,19);user.setSkillLevel(Skills.SORCERY,14);
            check(runtime.playerTier(p,"fighting")==2,"Combate 19 sigue T2");
            check(runtime.playerTier(p,"sorcery")==2,"Magia 14 es T2 independiente de Combate");
            double base=runtime.getConfig().getDouble("xp.2");
            double mob=runtime.getConfig().getDouble("xp.3");
            check(Math.abs(mob*runtime.tierXpFactor(p,"fighting",3)-base*5)<1e-7,"T3 con Combate 19 paga T2 x5");
            user.setSkillLevel(Skills.FIGHTING,20);
            check(runtime.tierXpFactor(p,"fighting",3)==1,"Combate 20 XP T3 completa");
            user.setSkillLevel(Skills.SORCERY,20);
            check(runtime.tierXpFactor(p,"sorcery",3)==1,"Magia 20 XP T3 completa");
            p.removeAttachment(attachment);
        } else if(args[0].equals("result")) {
            getLogger().info("T5A RESULT failures="+failures);
        }
      } catch(Throwable ex) {failures++;ex.printStackTrace();}
      return true;
    }
}
