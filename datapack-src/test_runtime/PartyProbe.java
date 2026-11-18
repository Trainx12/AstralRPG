package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Jugadores NMS locales, sin red remota. Prueba API Paper y Skript reales. */
public final class PartyProbe extends JavaPlugin {
    final Map<String,Player> players=new LinkedHashMap<>(); int failures,checks;
    AstralParty party;
    World world(String n) {var w=Bukkit.getWorld(n);return w!=null?w:Bukkit.createWorld(new WorldCreator(n).type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));}
    @Override public void onEnable(){party=(AstralParty)Bukkit.getPluginManager().getPlugin("AstralParty");for(var n:List.of("lobby","mina","infinita")){var w=world(n);w.setSpawnLocation(0,100,0);w.setGameRule(GameRules.ADVANCE_TIME,false);}}
    void check(boolean ok,String label){checks++;if(!ok)failures++;getLogger().info("PARTY "+(ok?"PASS ":"FAIL ")+label);}
    Player fake(String name) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();var w=((CraftWorld)world("lobby")).getHandle();
        var property=new com.mojang.authlib.properties.Property("textures",Base64.getEncoder().encodeToString(("{\"textures\":{\"SKIN\":{\"url\":\"https://textures.minecraft.net/texture/"+"0".repeat(64)+"\"}}}").getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        var profile=new GameProfile(UUID.randomUUID(),name,new com.mojang.authlib.properties.PropertyMap(com.google.common.collect.ImmutableMultimap.of("textures",property)));
        var fake=new ServerPlayer(server,w,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        fake.setPos(0.5,100,0.5);w.addNewPlayer(fake);var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")){var f=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);f.setAccessible(true);((Map)f.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);}
        var ch=(io.netty.channel.embedded.EmbeddedChannel)connection.channel;Bukkit.getScheduler().runTaskTimer(this,()->ch.releaseOutbound(),1,1);
        var p=fake.getBukkitEntity();p.setGravity(false);p.setGameMode(GameMode.SURVIVAL);return p;
    }
    Player p(String n){return players.get(n);}
    // Paper encola comandos anidados hasta terminar partyprobe; ejecutar PluginCommand
    // permite comprobar cada transicion sin que las aserciones adelanten esa cola.
    void cmd(String n,String text){var a=text.split(" ");Bukkit.getPluginCommand(a[0]).execute(p(n),a[0],Arrays.copyOfRange(a,1,a.length));}
    void move(String n,String w){p(n).teleport(new Location(world(w),0.5,100,0.5));}
    void kill(String n){
        advance(41); // la caida siguiente ocurre despues de los dos segundos de proteccion
        var p=p(n);var handle=((org.bukkit.craftbukkit.entity.CraftPlayer)p).getHandle();
        try {
            var loaded=ServerGamePacketListenerImpl.class.getDeclaredMethod("markClientLoaded");loaded.setAccessible(true);loaded.invoke(handle.connection);
            var f=ServerGamePacketListenerImpl.class.getDeclaredField("awaitingTeleport");f.setAccessible(true);
            handle.connection.handleAcceptTeleportPacket(new net.minecraft.network.protocol.game.ServerboundAcceptTeleportationPacket(f.getInt(handle.connection)));
        }catch(Exception e){throw new RuntimeException(e);}
        p.setInvulnerable(false);p.setNoDamageTicks(0);p.damage(1000);
    }
    void advance(long ticks){party.clock+=ticks-1;party.tick();}
    @Override public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command cmd,String label,String[] args){
      try {
        switch(args[0]) {
        case "setup" -> {
            for(var n:List.of("A","B","C","D","E","F","G"))players.put(n,fake("Party"+n));
            cmd("A","party");check(p("A").getOpenInventory().getTopInventory().getHolder() instanceof AstralParty.View,"/party abre inventario");p("A").closeInventory();
            cmd("A","party invitar PartyB");cmd("B","party aceptar");
            check(party.members(p("A")).size()==2,"aceptar invitacion");
            check(party.leader(p("A")),"lider correcto");
            check(party.placeholder(p("A"),"cantidad").equals("2"),"placeholder cantidad");
            check(me.clip.placeholderapi.PlaceholderAPI.setPlaceholders(p("A"),"%astral_party_cantidad%").equals("2"),"expansion PAPI registrada");
            check(party.placeholder(p("A"),"en").equals("si"),"placeholder si");
            cmd("B","party invitar PartyC");check(!party.invites.containsKey(p("C").getUniqueId()),"no lider no invita");
            cmd("A","party invitar PartyA");check(!party.invites.containsKey(p("A").getUniqueId()),"no autoinvitacion");
            for(var n:List.of("C","D","E","F")){cmd("A","party invitar Party"+n);cmd(n,"party aceptar");}
            cmd("A","party invitar PartyG");check(!party.invites.containsKey(p("G").getUniqueId()),"limite seis");
            check(party.members(p("A")).size()==6,"seis miembros");
            check(party.placeholder(p("A"),"tab3").contains("PartyF"),"TAB muestra sexto miembro");
            check(party.placeholder(p("A"),"fila3").contains("❤"),"panel contiene vida");
            cmd("B","party echar PartyC");check(party.inParty(p("C")),"solo lider puede echar");
            cmd("A","party echar PartyF");check(!party.inParty(p("F")),"lider echa");
            cmd("A","party invitar PartyF");cmd("F","party rechazar");check(!party.invites.containsKey(p("F").getUniqueId()),"rechazar");
            cmd("A","party invitar PartyF");advance(1201);cmd("F","party aceptar");check(!party.inParty(p("F")),"invitacion vence");
            cmd("E","party salir");cmd("D","party salir");cmd("C","party salir");
            check(party.members(p("A")).size()==2,"salir conserva A+B");
            move("B","infinita");check(party.placeholder(p("A"),"tab1").contains("PartyB"),"TAB entre mundos");move("B","lobby");
        }
        case "bridge" -> {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"mazentrar PartyA mina");
        }
        case "fall" -> {
            check(p("A").getWorld().getName().equals("mina")&&p("B").getWorld().getName().equals("mina"),"mazentrar usa variables sincronizadas");
            move("A","mina");move("B","mina");
            p("A").getInventory().setItem(0,new ItemStack(Material.DIAMOND,17));
            check(party.delay(p("A"))==30,"oleadas 30s");kill("A");
            check(party.busy(p("A")),"caida letal registrada");
            check(p("A").getGameMode()==GameMode.SPECTATOR,"caido espectador");
            check(p("A").getWorld().getName().equals("mina"),"no sale de copia");
            check(p("A").getSpectatorTarget()==p("B"),"camara primera persona");
            check(p("A").getInventory().getItem(0).getAmount()==17,"inventario intacto");
            check(party.placeholder(p("B"),"fila1").contains("☠"),"contador visible al companero");
            check(!p("A").teleport(new Location(world("lobby"),0,100,0)),"no escapa a otro mundo");
            check(!p("A").teleport(new Location(world("mina"),999,100,999)),"no sale de zona");
            cmd("A","party mirar");check(p("A").getOpenInventory().getTopInventory().getHolder() instanceof AstralParty.View,"selector de camaras");p("A").closeInventory();
            party.watch(p("A"),p("B"),true);check(p("A").getSpectatorTarget()==null,"mirar libre");
            party.watch(p("A"),p("B"),false);
            advance(599);check(party.busy(p("A")),"no revive antes de 30s");advance(2);
            check(!party.busy(p("A"))&&p("A").getGameMode()==GameMode.SURVIVAL,"revive a los 30s");
            check(p("A").getHealth()==p("A").getMaxHealth(),"vida llena");check(p("A").getNoDamageTicks()>=39,"2s de inmunidad");
            var room=party.bosses.stream().filter(b->b.world().equals("mina")&&b.boss()).findFirst().orElseThrow();
            p("A").teleport(new Location(world("mina"),room.x(),room.y(),room.z()));p("B").teleport(p("A"));
            check(party.delay(p("A"))==15,"jefe 15s");kill("A");advance(299);check(party.busy(p("A")),"no revive antes de 15s");advance(2);check(!party.busy(p("A")),"revive a los 15s");
            kill("A");party.victory(world("mina"));check(!party.busy(p("A")),"victoria revive para premio normal");
        }
        case "wipe" -> {
            move("A","infinita");move("B","infinita");kill("A");kill("B");
            check(party.wipes.size()==1,"todos muertos inicia derrota");
            check(p("A").getGameMode()==GameMode.SPECTATOR&&p("B").getGameMode()==GameMode.SPECTATOR,"todos espectador");
            advance(59);check(p("A").getWorld().getName().equals("infinita"),"espera 3s");advance(2);
            check(p("A").getWorld().getName().equals("lobby")&&p("B").getWorld().getName().equals("lobby"),"derrota vuelve lobby");
            check(party.fallen.isEmpty(),"sin muertos pendientes");
            check(p("A").getGameMode()==GameMode.SURVIVAL,"restaura modo");
        }
        case "actualdeath" -> {
            move("A","infinita");move("B","infinita");p("B").getInventory().setItem(0,new ItemStack(Material.DIAMOND,17));p("B").setHealth(0);
        }
        case "checkactual" -> {
            check(party.busy(p("B"))&&p("B").getGameMode()==GameMode.SPECTATOR,"muerte real tambien espera espectador");
            check(p("B").getWorld().getName().equals("infinita"),"Skript no expulsa muerte real en Infinita");
            check(p("B").getInventory().getItem(0).getAmount()==17,"muerte real conserva inventario");
            party.victory(world("infinita"));
        }
        case "cleanup" -> {
            move("A","infinita");move("B","infinita");kill("B");
            party.quit(new org.bukkit.event.player.PlayerQuitEvent(p("B"),"",org.bukkit.event.player.PlayerQuitEvent.QuitReason.DISCONNECTED));
            check(p("B").getGameMode()==GameMode.SURVIVAL&&p("B").getWorld().getName().equals("lobby"),"desconexion muerto restaura lobby");
            check(!party.inParty(p("B")),"desconexion limpia miembro");
            cmd("A","party salir");check(party.groups.isEmpty(),"lider sale disuelve");
            check(party.placeholder(p("G"),"linea").contains("Sin party"),"placeholder sin party");
            cmd("G","party invitar PartyF");cmd("F","party aceptar");
            var f=new AstralParty.Fallen(p("F"),party.clock+600);party.fallen.put(p("F").getUniqueId(),f);p("F").getPersistentDataContainer().set(party.recovery,org.bukkit.persistence.PersistentDataType.STRING,"SURVIVAL");p("F").setGameMode(GameMode.SPECTATOR);
            party.fallen.remove(p("F").getUniqueId());party.recover(p("F"));check(p("F").getGameMode()==GameMode.SURVIVAL,"recupera espectador tras reinicio");
            check(!p("F").getPersistentDataContainer().has(party.recovery),"limpia marca persistente");
            cmd("G","party");
            var e=new org.bukkit.event.inventory.InventoryClickEvent(p("G").getOpenInventory(),org.bukkit.event.inventory.InventoryType.SlotType.CONTAINER,10,org.bukkit.event.inventory.ClickType.SHIFT_LEFT,org.bukkit.event.inventory.InventoryAction.MOVE_TO_OTHER_INVENTORY);
            Bukkit.getPluginManager().callEvent(e);check(e.isCancelled(),"no permite extraer cabezas del menu");
            getLogger().info("PARTY RESULT checks="+checks+" failures="+failures);
        }
        }
      }catch(Throwable e){failures++;getLogger().warning("PARTY FAIL "+e);e.printStackTrace();}
      return true;
    }
}
