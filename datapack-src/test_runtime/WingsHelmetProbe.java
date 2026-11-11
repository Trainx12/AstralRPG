package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.player.*;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Dos jugadores simulados. Verifica estado de servidor, no renderizado de clientes. */
public final class WingsHelmetProbe extends JavaPlugin {
    Player player, observer; int failures;
    void check(boolean ok,String message) { if(!ok)failures++;getLogger().info("WINGS "+(ok?"PASS ":"FAIL ")+message); }
    void call(String method) throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");
        var m=plugin.getClass().getDeclaredMethod(method);m.setAccessible(true);m.invoke(plugin);
    }
    ItemDisplay wing() { return player.getWorld().getEntitiesByClass(ItemDisplay.class).stream().filter(e->e.getScoreboardTags().contains("astral.wings")).findFirst().orElse(null); }
    long count() { return Bukkit.getWorlds().stream().flatMap(w->w.getEntitiesByClass(ItemDisplay.class).stream()).filter(e->e.getScoreboardTags().contains("astral.wings")).count(); }
    void refresh() throws Exception { call("discoverWings");call("wings"); }
    Player fake(String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.randomUUID(),name);
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        world.getWorld().getChunkAt(0,0).setForceLoaded(true);
        fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);field.setAccessible(true);
            ((Map)field.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);p.setOp(true);return p;
    }
    ItemStack item(String id) {
        var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id));
        return table.populateLoot(new Random(),new org.bukkit.loot.LootContext.Builder(player.getLocation()).build()).iterator().next();
    }
    void equip(String key) { Bukkit.dispatchCommand(player,"astralcosmetic alas "+key); }
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
      try {
        switch(args[0]) {
        case "start" -> {
            player=fake("WingsProbe");observer=fake("WingsObserver");
            player.getInventory().setChestplate(new ItemStack(Material.DIAMOND_CHESTPLATE));
            equip("asura");refresh();
        }
        case "equipped" -> {
            check(wing()!=null && count()==1,"display unico con dos jugadores; observador sin alas");
            check(player.getPassengers().isEmpty(),"sin pasajeros que bloqueen teleports Bukkit");
            check(!wing().isPersistent() && wing().getInterpolationDuration()==2 && wing().getTeleportDuration()==2,"display transitorio interpolado");
            check(player.getInventory().getChestplate().getType()==Material.DIAMOND_CHESTPLATE,"proteccion de pecho intacta");
        }
        case "rotation" -> {
            var d=wing();var uuid=d.getUniqueId();float start=player.getBodyYaw();
            player.setRotation(start+170,80); // Solo cabeza: el body yaw permanece controlado.
            player.setBodyYaw(start);call("wings");
            var before=new org.joml.Quaternionf(d.getTransformation().getLeftRotation());
            player.setBodyYaw(start+170);call("wings");
            float angle=before.difference(d.getTransformation().getLeftRotation()).angle();
            check(Math.toDegrees(angle)<12.01,"giro brusco limitado a 12 grados por tick");
            for(int i=0;i<20;i++)call("wings");
            check(uuid.equals(wing().getUniqueId()),"rotar no recrea display");
            var m=Bukkit.getPluginManager().getPlugin("AstralDecor").getClass().getDeclaredMethod("approachYaw",float.class,float.class);m.setAccessible(true);
            check(Math.abs((float)m.invoke(null,179f,-179f)-181f)<.001,"cruce 180 por camino corto");
            player.setBodyYaw(0);for(int i=0;i<20;i++)call("wings");
            check(Math.abs(d.getTransformation().getTranslation().z+.38)<.001,"separacion espalda 0.38");
        }
        case "poses" -> {
            player.setSneaking(true);player.setPose(Pose.SNEAKING,true);call("wings");
            check(Math.abs(wing().getY()-player.getY()-1.2)<.001,"agachado baja anclaje a hombros");
            player.setSwimming(true);player.setPose(Pose.SWIMMING,true);call("wings");check(count()==0,"nadar/reptar oculta sin huerfanos");
            player.setSwimming(false);player.setSneaking(false);player.setPose(Pose.STANDING,true);refresh();check(count()==1,"volver a pie restaura un solo display");
            player.setGliding(true);call("wings");check(count()==0,"planear oculta alas");player.setGliding(false);refresh();
            player.setInvisible(true);call("wings");check(count()==0,"invisibilidad oculta alas");player.setInvisible(false);refresh();
            player.setGameMode(GameMode.SPECTATOR);call("wings");check(count()==0,"espectador oculta alas");player.setGameMode(GameMode.SURVIVAL);refresh();
        }
        case "walk" -> {
            var uuid=wing().getUniqueId();player.setSprinting(true);
            var handle=((org.bukkit.craftbukkit.entity.CraftPlayer)player).getHandle();
            for(int i=0;i<30;i++) {
                double angle=i*Math.PI/15;handle.setPos(Math.sin(angle)*4,100,Math.cos(angle)*4);
                player.setBodyYaw((float)Math.toDegrees(angle));call("wings");
                check(Math.abs(wing().getX()-player.getX())<.001 && Math.abs(wing().getY()-player.getY()-1.45)<.001,"anclaje continuo caminando/corriendo en circulo");
            }
            check(uuid.equals(wing().getUniqueId()) && count()==1,"movimiento conserva UUID y un solo par");player.setSprinting(false);
        }
        case "mount" -> {
            var horse=player.getWorld().spawn(player.getLocation(),Horse.class);horse.setAI(false);horse.setGravity(false);
            check(horse.addPassenger(player),"montar caballo");refresh();
            check(player.getVehicle()==horse && wing()!=null && count()==1,"alas conservadas al montar sin alterar montura");
            player.leaveVehicle();horse.remove();refresh();check(count()==1,"desmontar no duplica alas");
        }
        case "teleport" -> {
            var old=wing();player.teleport(player.getLocation().add(5,0,0));refresh();
            check(!old.isValid() && count()==1,"teletransporte limpia y restaura");
            var world=Bukkit.createWorld(new WorldCreator("wing_other").type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));
            // El jugador NMS no crea los tickets de chunks de una conexion real.
            world.getChunkAt(0,0).setForceLoaded(true);
            old=wing();check(player.teleport(new Location(world,0,100,0)),"cambio real de mundo");refresh();
            check(!old.isValid(),"display anterior eliminado al cambiar mundo");
        }
        case "worldcheck" -> {
            check(count()==1 && wing()!=null && wing().getWorld()==player.getWorld(),"cambio de mundo sin huerfanos");
            equip("quitar");player.getInventory().setItemInOffHand(item("carnivora_alas"));refresh();
        }
        case "offhandcheck" -> {
            check(count()==1 && wing().getItemStack().getItemMeta().getItemModel().getKey().equals("carnivora_alas"),"Carnivora segunda mano usa mismo seguimiento");
        }
        case "helmet" -> {
            var fresh=item("carnivora_helmet");var meta=fresh.getItemMeta();
            check(meta.getEquippable().getModel()==null,"casco nuevo sin asset_id");
            var eq=meta.getEquippable();eq.setModel(NamespacedKey.fromString("astral:carnivora"));meta.setEquippable(eq);
            ((org.bukkit.inventory.meta.Damageable)meta).setDamage(17);
            meta.addEnchant(org.bukkit.enchantments.Enchantment.PROTECTION,4,true);meta.setDisplayName("Casco conservado");fresh.setItemMeta(meta);
            player.getInventory().setHelmet(fresh.clone());player.getInventory().setItem(8,fresh.clone());player.getInventory().setItem(12,fresh.clone());
            // Dejar que el chequeo habitual migre tambien items v15 en automatico.
            // Las funciones de consola se ejecutan en el siguiente tick de Paper.
        }
        case "helmetcheck" -> {
            var fresh=player.getInventory().getHelmet().clone();
            check(fresh.getItemMeta().getEquippable().getModel()==null,"casco existente migrado");
            for(var repaired:List.of(player.getInventory().getHelmet(),player.getInventory().getItem(8),player.getInventory().getItem(12))) {
                var expected=fresh.clone();var em=expected.getItemMeta();var ee=em.getEquippable();ee.setModel(null);em.setEquippable(ee);expected.setItemMeta(em);
                check(repaired.equals(expected),"migracion conserva todo salvo modelo equipment (cabeza/hotbar/inventario)");
                check(((org.bukkit.inventory.meta.Damageable)repaired.getItemMeta()).getDamage()==17 && repaired.getItemMeta().getEnchantLevel(org.bukkit.enchantments.Enchantment.PROTECTION)==4 && repaired.getItemMeta().getDisplayName().equals("Casco conservado"),"dano encantamientos y nombre conservados");
            }
        }
        case "quit" -> {
            player.saveData();Bukkit.getPluginManager().callEvent(new PlayerQuitEvent(player,net.kyori.adventure.text.Component.empty(),PlayerQuitEvent.QuitReason.DISCONNECTED));
            check(count()==0,"evento desconexion retira display");
            player.loadData();refresh();
        }
        case "quitcheck" -> {
            check(count()==1,"playerdata y equipo restauran un solo par");
        }
        case "death" -> {
            player.setInvulnerable(false);player.setHealth(0);check(count()==0,"muerte limpia alas");
        }
        case "result" -> getLogger().info("WINGS RESULT failures="+failures);
        }
      } catch(Exception ex) { check(false,ex.toString());ex.printStackTrace(); }
      return true;
    }
}
