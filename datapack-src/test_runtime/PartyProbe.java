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
    final List<ArmorStand> borderControls=new ArrayList<>();
    World world(String n) {var w=Bukkit.getWorld(n);return w!=null?w:Bukkit.createWorld(new WorldCreator(n).type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").generateStructures(false));}
    @Override public void onEnable(){party=(AstralParty)Bukkit.getPluginManager().getPlugin("AstralParty");for(var n:List.of("lobby","mina","infinita","fosa")){var w=world(n);w.setSpawnLocation(0,100,0);w.setGameRule(GameRules.ADVANCE_TIME,false);}}
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
    // Los plugins tienen classloaders distintos: usar reflexion solo en el ensayo.
    void invoke(String name,Class<?>[] types,Object... args) {
        try {var m=AstralParty.class.getDeclaredMethod(name,types);m.setAccessible(true);m.invoke(party,args);}
        catch(Exception e){throw new RuntimeException(e);}
    }
    void memberMenu(Player p,Player t,boolean confirm){invoke("memberMenu",new Class<?>[]{Player.class,Player.class,boolean.class},p,t,confirm);}
    void refreshBorders(){invoke("refreshFightRooms",new Class<?>[]{});}
    void updateBorder(Player p){invoke("updateBorder",new Class<?>[]{Player.class},p);}
    void action(AstralParty.View v,int slot) {
        try {var f=AstralParty.View.class.getDeclaredField("actions");f.setAccessible(true);((Runnable)((Map)f.get(v)).get(slot)).run();}
        catch(Exception e){throw new RuntimeException(e);}
    }
    String inviteToken(Player p) {
        try {Object i=party.invites.get(p.getUniqueId());var m=i.getClass().getDeclaredMethod("token");m.setAccessible(true);return m.invoke(i).toString();}
        catch(Exception e){throw new RuntimeException(e);}
    }
    boolean inside(AstralParty.FightRoom r,Location at){return r.contains(at);}
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
        case "controls" -> {
            cmd("A","party invitar PartyF");var oldToken=inviteToken(p("F"));
            cmd("B","party cancelar PartyF");check(party.invites.containsKey(p("F").getUniqueId()),"otro miembro no cancela invitacion");
            cmd("A","party cancelar PartyF");check(!party.invites.containsKey(p("F").getUniqueId()),"cancelar invitacion");
            cmd("A","party invitar PartyF");
            cmd("F","party aceptar "+p("A").getUniqueId()+" "+oldToken);
            check(!party.inParty(p("F"))&&party.invites.containsKey(p("F").getUniqueId()),"boton viejo no acepta invitacion nueva");
            cmd("A","party cancelar PartyF "+p("A").getUniqueId()+" "+oldToken);
            check(party.invites.containsKey(p("F").getUniqueId()),"cancelar viejo no retira invitacion nueva");
            cmd("F","party aceptar "+p("A").getUniqueId()+" "+inviteToken(p("F")));
            check(party.inParty(p("F")),"aceptar con token del boton");cmd("F","party salir");
            cmd("A","party invitar PartyF");cmd("F","party rechazar "+p("A").getUniqueId()+" "+inviteToken(p("F")));
            check(!party.invites.containsKey(p("F").getUniqueId()),"rechazar con token del boton");
            cmd("A","party invitar PartyF");cmd("A","party cancelar PartyF "+p("A").getUniqueId()+" "+inviteToken(p("F")));
            check(!party.invites.containsKey(p("F").getUniqueId()),"cancelar con token del boton");
            memberMenu(p("A"),p("B"),false);
            var v=(AstralParty.View)p("A").getOpenInventory().getTopInventory().getHolder();
            check(v.getInventory().getSize()==27,"submenu compacto");action(v,10);
            check(party.inParty(p("B")),"echar requiere confirmar");
            check(p("A").getOpenInventory().getTitle().contains("Confirmar"),"ventana de confirmacion");
            memberMenu(p("A"),p("B"),false);
            action((AstralParty.View)p("A").getOpenInventory().getTopInventory().getHolder(),16);
            check(party.leader(p("B"))&&!party.leader(p("A")),"boton pasa liderazgo");
            check(party.members(p("A")).size()==2,"traspaso conserva miembros");
            cmd("A","party lider PartyA");check(party.leader(p("B")),"miembro no puede robar liderazgo");
            cmd("B","party lider PartyA");check(party.leader(p("A")),"comando de liderazgo conserva API");
            p("A").closeInventory();p("B").closeInventory();
        }
        case "prepareborders" -> {
            var rooms=party.fightRooms.stream().filter(r->r.world().equals("mina")).toList();
            var a=rooms.get(0);var b=rooms.get(2);var w=world("mina");
            for(var r:List.of(a,b))w.getChunkAt(new Location(w,r.x(),r.y(),r.z())).load();
            for(var e:w.getEntities())if(e instanceof ArmorStand&&e.getName().startsWith("Control "))e.remove();
            for(var r:List.of(a,b)) {
                var at=new Location(w,r.x(),r.y(),r.z());w.getChunkAt(at).load();
                var stand=w.spawn(at,ArmorStand.class,e->e.setInvulnerable(true));
                stand.setCustomName(r.controller());stand.setGravity(false);stand.setMarker(true);stand.addScoreboardTag("mina.on");borderControls.add(stand);
            }
            p("A").teleport(new Location(w,a.x(),a.y(),a.z()));p("B").teleport(new Location(w,b.x(),b.y(),b.z()));
        }
        case "borders" -> {
            var rooms=party.fightRooms.stream().filter(r->r.world().equals("mina")).toList();
            var a=rooms.get(0);var b=rooms.get(2);var w=world("mina");var controls=borderControls;
            refreshBorders();updateBorder(p("A"));updateBorder(p("B"));
            check(p("A").getWorldBorder()!=null&&p("A").getWorldBorder().getSize()==a.side(),"borde personal Paper");
            check(Math.abs(p("B").getWorldBorder().getCenter().getX()-b.centerX(p("B").getX()))<1e-6,"dos salas independientes en mismo mundo");
            check(p("A").getWorldBorder().getDamageAmount()==0&&p("A").getWorldBorder().getDamageBuffer()==0,"borde sin dano ni buffer");
            check(p("A").getWorldBorder().getWarningDistance()==3,"aviso tres bloques");
            var from=p("A").getLocation();var out=from.clone().add(a.side(),0,0);
            var move=new org.bukkit.event.player.PlayerMoveEvent(p("A"),from,out);
            Bukkit.getPluginManager().callEvent(move);check(inside(a,move.getTo()),"movimiento y knockback no cruzan borde");
            var pearl=new org.bukkit.event.player.PlayerTeleportEvent(p("A"),from,out,org.bukkit.event.player.PlayerTeleportEvent.TeleportCause.ENDER_PEARL);
            Bukkit.getPluginManager().callEvent(pearl);check(inside(a,pearl.getTo()),"perla no cruza borde");
            // Simular desincronizacion sin lanzar un evento de teletransporte.
            ((org.bukkit.craftbukkit.entity.CraftPlayer)p("A")).getHandle().setPos(out.getX(),out.getY(),out.getZ());
            updateBorder(p("A"));check(inside(a,p("A").getLocation()),"tick recupera posicion exterior");
            // 26/11: mobs adentro del borde y lugar seguro solo pisando firme.
            var p1=new Location(w,a.x()+2,a.y(),a.z()+2);
            var zom=w.spawn(p1,Zombie.class,z->{z.setAI(false);z.setGravity(false);});
            invoke("keepMobs",new Class<?>[]{});
            zom.setGravity(true);zom.teleport(p1.clone().add(0,20,0));invoke("keepMobs",new Class<?>[]{});
            zom.teleport(new Location(w,a.x2()+1.5,p1.getY(),p1.getZ()));invoke("keepMobs",new Class<?>[]{});
            check(inside(a,zom.getLocation()),"mob no cruza borde");
            check(Math.abs(zom.getLocation().getY()-p1.getY())<.01,"mob vuelve al ultimo lugar firme, no al aire");
            zom.remove();
            p("B").teleport(new Location(w,a.x()+1,a.y(),a.z()));updateBorder(p("B"));
            invoke("fall",new Class<?>[]{Player.class},p("A"));updateBorder(p("A"));
            check(p("A").getWorldBorder()!=null&&party.busy(p("A")),"caido conserva borde de companero");
            invoke("revive",new Class<?>[]{Player.class,Location.class},p("A"),p("B").getLocation());
            controls.getFirst().addScoreboardTag("mina.fin");refreshBorders();updateBorder(p("A"));
            check(p("A").getWorldBorder()==null,"limpiar sala quita borde");
            p("B").teleport(new Location(w,b.x(),b.y(),b.z()));updateBorder(p("B"));check(p("B").getWorldBorder()!=null,"limpiar una sala conserva la otra");
            controls.forEach(Entity::remove);refreshBorders();
            move("A","infinita");move("B","infinita");
            p("A").teleport(new Location(world("infinita"),0.5,63,0.5));
            var infAt=new Location(world("infinita"),1,63,1);world("infinita").getChunkAt(infAt).load();
            var mob=world("infinita").spawn(infAt,Zombie.class);mob.setAI(false);mob.addScoreboardTag("inf.mob");
            refreshBorders();updateBorder(p("A"));check(p("A").getWorldBorder()!=null,"Infinita detecta inf.mob");
            mob.remove();refreshBorders();updateBorder(p("A"));check(p("A").getWorldBorder()==null,"Infinita limpia sin enemigos");
            move("A","fosa");p("A").teleport(new Location(world("fosa"),2,112,94));
            var fosaAt=p("A").getLocation();world("fosa").getChunkAt(fosaAt).load();
            var fosaMob=world("fosa").spawn(fosaAt,Zombie.class);fosaMob.setAI(false);fosaMob.addScoreboardTag("fosa.jefe");
            refreshBorders();updateBorder(p("A"));check(p("A").getWorldBorder()!=null,"Fosa detecta jefe vivo");
            fosaMob.removeScoreboardTag("fosa.jefe");fosaMob.addScoreboardTag("fosa.mob");
            refreshBorders();updateBorder(p("A"));check(p("A").getWorldBorder()!=null,"Fosa conserva borde con ayudantes vivos");
            fosaMob.remove();refreshBorders();updateBorder(p("A"));check(p("A").getWorldBorder()==null,"Fosa oculta borde entre oleadas");
            move("A","lobby");move("B","lobby");
        }
        case "rectangles" -> {
            var w=world("mina");var p=p("A");
            var r=new AstralParty.FightRoom("mina",500,100,500,150,400,480,600,520,"mina","Control Rectangulo");
            var rz=new AstralParty.FightRoom("mina",800,100,800,150,780,700,820,900,"mina","Control Rectangulo Z");
            var square=new AstralParty.FightRoom("mina",900,100,900,50,880,880,922,920,"mina","Control Cuadrado");
            check(r.side()==40&&r.centerX(0)==420&&r.centerX(900)==580&&r.centerX(500)==500&&r.centerZ(0)==500,"clamp X en ambos extremos y eje corto fijo");
            check(rz.side()==40&&rz.centerZ(0)==720&&rz.centerZ(999)==880&&rz.centerX(0)==800,"clamp Z en ambos extremos y eje corto fijo");
            check(square.centerX(999)==901&&square.centerZ(0)==900&&square.side()==40,"casi cuadrado fijo dentro de rectangulo");
            party.fightRooms.add(r);party.fightRooms.add(rz);
            var controls=new ArrayList<ArmorStand>();
            for(var room:List.of(r,rz)) {
                var at=new Location(w,room.x(),room.y(),room.z());w.getChunkAt(at).load();
                controls.add(w.spawn(at,ArmorStand.class,e->{e.setCustomName(room.controller());e.setGravity(false);e.setMarker(true);e.addScoreboardTag("mina.on");}));
            }
            p.teleport(new Location(w,500,100,500));refreshBorders();updateBorder(p);
            var border=p.getWorldBorder();check(border!=null&&border.getSize()==40,"rectangulo crea borde de lado corto");
            var handle=((org.bukkit.craftbukkit.entity.CraftPlayer)p).getHandle();
            handle.setPos(500.3,100,500);updateBorder(p);
            check(border.getCenter().getX()==500,"centro estable para cambio menor de medio bloque");
            handle.setPos(501,100,500);updateBorder(p);
            check(p.getWorldBorder()==border&&border.getCenter().getX()==501,"mismo borde actualiza centro sin recrear");
            var from=p.getLocation();var far=new Location(w,595,100,500);
            var ev=new org.bukkit.event.player.PlayerMoveEvent(p,from,far);Bukkit.getPluginManager().callEvent(ev);
            check(ev.getTo().getX()==595,"recuperacion acepta eje largo fuera del cuadrado anterior");
            handle.setPos(595,100,500);updateBorder(p);
            check(border.getCenter().getX()==580&&p.getX()==595,"extremo largo acotado no devuelve jugador interior");
            var pearl=new org.bukkit.event.player.PlayerTeleportEvent(p,p.getLocation(),new Location(w,595,100,521),org.bukkit.event.player.PlayerTeleportEvent.TeleportCause.ENDER_PEARL);
            Bukkit.getPluginManager().callEvent(pearl);check(r.contains(pearl.getTo()),"perla usa rectangulo exacto en eje corto");
            handle.setPos(601,100,500);updateBorder(p);check(r.contains(p.getLocation())&&p.getX()==595,"lag exterior recupera ultimo punto rectangular");
            p.teleport(new Location(w,800,100,800));refreshBorders();updateBorder(p);
            handle.setPos(800,100,895);updateBorder(p);
            check(p.getWorldBorder().getCenter().getZ()==880&&p.getZ()==895,"rectangulo Z se desplaza hasta extremo");
            controls.forEach(Entity::remove);party.fightRooms.remove(r);party.fightRooms.remove(rz);refreshBorders();updateBorder(p);
            check(p.getWorldBorder()==null,"rectangulos limpian borde al terminar");
            move("A","lobby");
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
