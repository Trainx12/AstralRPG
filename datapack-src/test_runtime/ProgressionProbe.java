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

public final class ProgressionProbe extends JavaPlugin {
    Player p; int failures;
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
        } else if(args[0].equals("xp")) {
            check(runtime.weaponSkill(item("baston_1")).equals("sorcery"),"PDC baston sorcery");
            check(runtime.weaponSkill(item("espada_1")).equals("fighting"),"PDC espada fighting");
            var user=AuraSkillsApi.get().getUser(p.getUniqueId());
            check(user.isLoaded(),"usuario AuraSkills cargado");
            for(var skill:List.of(Skills.SORCERY,Skills.FIGHTING,Skills.ARCHERY)) {user.setSkillLevel(skill,25);user.setSkillXp(skill,0);}
            p.getInventory().setItemInMainHand(item("baston_1"));
            Zombie mob=p.getWorld().spawn(p.getLocation().add(2,0,0),Zombie.class);mob.setAI(false);mob.addScoreboardTag("astral.mt5");
            mob.damage(100000,p);
            Bukkit.getScheduler().runTaskLater(this,()->{
                check(Math.abs(user.getSkillXp(Skills.SORCERY)-550.8)<.1,"baston T5 + jefe T2: 230.8+320 sorcery real="+user.getSkillXp(Skills.SORCERY));
                check(Math.abs(user.getSkillXp(Skills.FIGHTING)-90)<.1,"sin fighting duplicado (60 x Fighter 1.5) real="+user.getSkillXp(Skills.FIGHTING));
            },2);
            p.getInventory().setItemInMainHand(item("arco_1"));
            Arrow arrow=p.launchProjectile(Arrow.class);arrow.setGravity(false);
            runtime.shoot(new EntityShootBowEvent(p,p.getInventory().getItemInMainHand(),null,arrow,EquipmentSlot.HAND,1,false));
            p.getInventory().setItemInMainHand(item("baston_1"));
            Zombie target=p.getWorld().spawn(p.getLocation().add(4,0,0),Zombie.class);target.setAI(false);target.addScoreboardTag("astral.mt3");
            target.damage(100000,org.bukkit.damage.DamageSource.builder(org.bukkit.damage.DamageType.ARROW).withCausingEntity(p).withDirectEntity(arrow).build());arrow.remove();
            Bukkit.getScheduler().runTaskLater(this,()->check(Math.abs(user.getSkillXp(Skills.ARCHERY)-120)<.1,"arco conserva skill (80 x Archer 1.5): "+user.getSkillXp(Skills.ARCHERY)),2);
            p.getInventory().setItemInMainHand(item("espada_1"));
            Zombie elite=p.getWorld().spawn(p.getLocation().add(6,0,0),Zombie.class);elite.setAI(false);elite.addScoreboardTag("astral.mt2");elite.addScoreboardTag("astral.elite3");
            check(runtime.reward(elite)==60,"elite T2 60 XP");elite.damage(100000,p);
            Bukkit.getScheduler().runTaskLater(this,()->check(Math.abs(user.getSkillXp(Skills.FIGHTING)-90)<.1,"espada una recompensa 60 x Fighter 1.5, real="+user.getSkillXp(Skills.FIGHTING)),2);
            var boss=io.lumine.mythic.bukkit.MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_mina_guardian",p.getLocation().add(8,0,0));
            p.getInventory().setItemInMainHand(item("baston_1"));
            ((LivingEntity)boss).damage(100000,p);
            Bukkit.getScheduler().runTaskLater(this,()->check(Math.abs(user.getSkillXp(Skills.SORCERY)-550.8)<.1,"jefe Mythic T2 suma 320 una vez: "+user.getSkillXp(Skills.SORCERY)),3);
        } else if(args[0].equals("claims")) {
            var gp=GriefPrevention.instance;
            var pd=gp.dataStore.getPlayerData(p.getUniqueId());
            pd.setAccruedClaimBlocks(36);pd.setBonusClaimBlocks(0);
            check(gp.config_claims_initialBlocks==36,"saldo inicial configurado 36");
            check(gp.config_claims_blocksAccruedPerHour_default==0,"cero bloques por hora");
            var w=p.getWorld();
            var old=gp.dataStore.getClaimAt(new Location(w,22,-60,22),false,null);if(old!=null)gp.dataStore.deleteClaim(old);
            var result=gp.dataStore.createClaim(w,20,25,w.getMinHeight(),w.getMaxHeight()-1,20,25,p.getUniqueId(),null,null,p);
            check(result.succeeded,"claim 6x6 creado");
            if(result.succeeded) {
                check(result.claim.getArea()==36,"area X*Z 36");
                check(gp.dataStore.getClaimAt(new Location(w,22,w.getMinHeight(),22),false,null)!=null,"protege fondo");
                check(gp.dataStore.getClaimAt(new Location(w,22,w.getMaxHeight()-1,22),false,null)!=null,"protege techo");
            }
            cmd("adjustbonusclaimblocks "+p.getName()+" 25");
            Bukkit.getScheduler().runTaskLater(this,()->check(pd.getBonusClaimBlocks()==25 && pd.getAccruedClaimBlocks()==36,"paquete suma 36+25=61"),2);
            var other=Bukkit.createWorld(new WorldCreator("lobby").type(WorldType.FLAT).generateStructures(false));
            check(gp.config_claims_worldModes.get(other)==ClaimsMode.Disabled,"claims desactivados mundo nuevo");
            var structure=org.bukkit.Registry.STRUCTURE.get(NamespacedKey.fromString("structory:abandoned_camp"));
            check(structure!=null,"estructura real de Structory cargada");
            if(structure!=null) {
                var event=new AsyncStructureSpawnEvent(other,structure,new org.bukkit.util.BoundingBox(0,0,0,10,10,10),0,0);
                runtime.structures(event);check(event.isCancelled(),"estructura excluida de lobby");
                var allowed=new AsyncStructureSpawnEvent(w,structure,new org.bukkit.util.BoundingBox(0,0,0,10,10,10),0,0);
                runtime.structures(allowed);check(!allowed.isCancelled(),"estructura permitida en survival");
            }
        } else if(args[0].equals("loot")) {
            // Probabilidad 1 SOLO en memoria del servidor de prueba, nunca config de entrega.
            var cat=runtime.getConfig().getConfigurationSection("loot");
            for(String id:cat.getKeys(false)) cat.set(id+".chance",0);
            cat.set("fragmento_cristal.chance",1);
            for(String table:List.of("minecraft:chests/simple_dungeon","nova_structures:chests/catacomb/catacomb_generic","explorify:chest/supply_cache","structory:outcast/low","structory_towers:basic/wizard_basic")) {
                var vanilla=Bukkit.getLootTable(NamespacedKey.fromString(table));
                if(vanilla==null) {check(false,"tabla ausente "+table);continue;}
                var b=p.getWorld().getBlockAt(35+Math.abs(table.hashCode()%100),-59,5);b.setType(Material.CHEST);
                Chest chest=(Chest)b.getState();chest.getPersistentDataContainer().remove(new NamespacedKey("astralprogression","generated"));chest.update();chest.getInventory().clear();
                var list=new ArrayList<ItemStack>();list.add(new ItemStack(Material.DIAMOND,3));
                var event=new LootGenerateEvent(p.getWorld(),p,chest,vanilla,new LootContext.Builder(b.getLocation()).build(),list,false);
                Bukkit.getPluginManager().callEvent(event);
                check(event.getLoot().equals(list),"loot vanilla intacto "+table);
                Bukkit.getScheduler().runTaskLater(this,()->{
                    check(chest.getInventory().contains(item("fragmento_cristal").getType()),"item Astral agregado "+table);
                    int before=Arrays.stream(chest.getInventory().getContents()).filter(Objects::nonNull).mapToInt(ItemStack::getAmount).sum();
                    Bukkit.getPluginManager().callEvent(event);
                    Bukkit.getScheduler().runTaskLater(this,()->check(Arrays.stream(chest.getInventory().getContents()).filter(Objects::nonNull).mapToInt(ItemStack::getAmount).sum()==before,"no repite cofre "+table),2);
                },2);
            }
        } else if(args[0].equals("backpack")) {
            // Mismo comando que ejecuta la tienda de AstralProgression al cobrar.
            p.setOp(false);p.getInventory().clear();
            check(Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"backpack give "+p.getName()+" leather"),"tienda: backpack give");
            Bukkit.getScheduler().runTaskLater(this,()->{openBackpack();Bukkit.getScheduler().runTaskLater(this,()->backpackCheck(),3);},2);
        } else if(args[0].equals("restart")) {
            // El jugador simulado vuelve sin inventario: se le devuelve la MISMA mochila guardada.
            var saved=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.File(getDataFolder(),"mochila.yml")).getItemStack("item");
            check(saved!=null,"mochila guardada antes del reinicio");
            p.setOp(false);p.getInventory().clear();p.getInventory().setItem(0,saved);openBackpack();
            Bukkit.getScheduler().runTaskLater(this,()->{
                var stack=p.getOpenInventory().getTopInventory().getItem(0);
                check(stack!=null && stack.getType()==Material.EMERALD && stack.getAmount()==7,"mochila conserva 7 esmeraldas tras reinicio");
                p.closeInventory();
            },3);
        } else if(args[0].equals("result")) getLogger().info("T5A RESULT failures="+failures);
      } catch(Throwable ex) { failures++;getLogger().warning("T5A FAIL "+ex);ex.printStackTrace(); }
      return true;
    }
    void openBackpack() {
        int slot=-1;
        for(int i=0;i<36;i++) { var it=p.getInventory().getItem(i); if(it!=null && it.getType()==Material.PLAYER_HEAD) { slot=i;break; } }
        check(slot>=0,"mochila entregada como item");
        if(slot<0) return;
        var it=p.getInventory().getItem(slot);p.getInventory().setItem(slot,null);p.getInventory().setItem(0,it);p.getInventory().setHeldItemSlot(0);
        var ev=new org.bukkit.event.player.PlayerInteractEvent(p,org.bukkit.event.block.Action.RIGHT_CLICK_AIR,it,null,org.bukkit.block.BlockFace.SELF,org.bukkit.inventory.EquipmentSlot.HAND);
        Bukkit.getPluginManager().callEvent(ev);
    }
    void backpackCheck() {
      try {
            var inv=p.getOpenInventory().getTopInventory();
            check(inv.getSize()==9 && inv.getType()!=org.bukkit.event.inventory.InventoryType.CRAFTING,"mochila de cuero abre con 9 espacios");
            inv.setItem(0,new ItemStack(Material.EMERALD,7));p.closeInventory();
            Bukkit.getScheduler().runTaskLater(this,()->{
            openBackpack();
            Bukkit.getScheduler().runTaskLater(this,()->{
            var stack=p.getOpenInventory().getTopInventory().getItem(0);
            check(stack!=null && stack.getAmount()==7,"guardar y reabrir sin duplicar");
            p.closeInventory();
            try {
                var y=new org.bukkit.configuration.file.YamlConfiguration();y.set("item",p.getInventory().getItem(0));
                getDataFolder().mkdirs();y.save(new java.io.File(getDataFolder(),"mochila.yml"));
            } catch(java.io.IOException ex) { check(false,"guardar mochila de prueba"); }
            },3);
            },2);
      } catch(Throwable ex) { failures++;getLogger().warning("T5A FAIL "+ex);ex.printStackTrace(); }
    }
}
