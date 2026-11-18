package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Ensayo local de Duels + ventana /desafiar con dos jugadores NMS. Nunca va al server. */
public final class DuelosUIProbe extends JavaPlugin {
    Player a, b; int failures, checks; AstralDuelos ui;
    static final String FLAT = "{\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:the_void\"}";
    // Duels lee arenas y lobby al habilitarse: los mundos tienen que existir antes (loadbefore).
    @Override public void onEnable() { for (String w : List.of("lobby", "arena", "arenas_tft")) world(w); }
    void check(boolean ok, String s) { checks++; if (!ok) failures++; getLogger().info("DUELOSUI " + (ok ? "PASS " : "FAIL ") + s); }
    World world(String name) {
        var w = Bukkit.getWorld(name);
        return w != null ? w : Bukkit.createWorld(new WorldCreator(name).type(WorldType.FLAT).generatorSettings(FLAT).generateStructures(false));
    }
    void floor(World w, int cx, int y, int cz, int r) {
        for (int x = cx - r; x <= cx + r; x++) for (int z = cz - r; z <= cz + r; z++) w.getBlockAt(x, y, z).setType(Material.STONE);
    }
    Player fake(String name) throws Exception {
        var server = ((CraftServer) Bukkit.getServer()).getServer(); var w = ((CraftWorld) world("lobby")).getHandle();
        var property = new com.mojang.authlib.properties.Property("textures", Base64.getEncoder().encodeToString(("{\"textures\":{\"SKIN\":{\"url\":\"https://textures.minecraft.net/texture/"+"0".repeat(64)+"\"}}}").getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        var profile = new GameProfile(UUID.randomUUID(), name, new com.mojang.authlib.properties.PropertyMap(com.google.common.collect.ImmutableMultimap.of("textures", property))); var fake = new ServerPlayer(server, w, profile, ClientInformation.createDefault());
        var connection = new Connection(PacketFlow.SERVERBOUND);
        // Consumir paquetes antes del buffer de Netty: no hay cliente que los lea.
        connection.channel = new io.netty.channel.embedded.EmbeddedChannel(new io.netty.channel.ChannelOutboundHandlerAdapter() {
            @Override public void write(io.netty.channel.ChannelHandlerContext ctx, Object msg, io.netty.channel.ChannelPromise promise) {
                io.netty.util.ReferenceCountUtil.release(msg); promise.setSuccess();
            }
        });
        connection.channel.pipeline().addLast("packet_handler", connection); connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        fake.connection = new ServerGamePacketListenerImpl(server, connection, fake, CommonListenerCookie.createInitial(profile, false));
        fake.setPos(180.5, 98, 190.5); w.addNewPlayer(fake); var list = server.getPlayerList(); list.players.add(fake);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var f = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); f.setAccessible(true);
            ((Map) f.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fake);
        }
        // Sin cliente, nadie lee los paquetes: vaciar cada tick para que no se trabe el server.
        var ch = (io.netty.channel.embedded.EmbeddedChannel) connection.channel;
        Bukkit.getScheduler().runTaskTimer(this, () -> ch.releaseOutbound(), 1, 1);
        var p = fake.getBukkitEntity(); p.setGravity(false); p.setGameMode(GameMode.SURVIVAL);
        // Duels carga los datos del jugador al entrar.
        Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(p, net.kyori.adventure.text.Component.empty()));
        return p;
    }
    void click(Player p, int slot) {
        var event = new InventoryClickEvent(p.getOpenInventory(), InventoryType.SlotType.CONTAINER, slot, ClickType.LEFT, InventoryAction.PICKUP_ALL);
        Bukkit.getPluginManager().callEvent(event); check(event.isCancelled(), "clic protegido " + slot);
    }
    void cmd(Player p, String... args) { ui.onCommand(p, ui.getCommand("duelos"), "duelos", args); }
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command command, String label, String[] args) {
      try {
        switch (args[0]) {
        case "setup" -> {
            ui = (AstralDuelos) Bukkit.getPluginManager().getPlugin("AstralDuelos");
            floor(world("lobby"),180,97,190,6); floor(world("arena"),-206,72,-2371,14);
            for (int z : new int[]{-551,-283,-15}) floor(world("arenas_tft"),-287,z == -551 ? 142 : 138,z,14);
            a=fake("RetadorA"); b=fake("RivalB");
            a.getInventory().addItem(new ItemStack(Material.DIAMOND,5)); b.getInventory().addItem(new ItemStack(Material.EMERALD,7));
            check(ui.isEnabled(), "runtime habilitado");
        }
        case "menus" -> {
            cmd(a); check(a.getOpenInventory().getTitle().contains("Duelos"), "menu principal propio");
            click(a,20);
        }
        case "players" -> {
            check(a.getOpenInventory().getTitle().contains("Desafiar"),"selector propio");
            check(a.getOpenInventory().getTopInventory().getItem(10).getType()==Material.PLAYER_HEAD,"cabeza del rival sin incluirse");
            click(a,10);
        }
        case "arenas" -> {
            check(a.getOpenInventory().getTitle().contains("Elegi"),"selector de arenas propio"); click(a,19);
        }
        case "confirm" -> {
            check(a.getOpenInventory().getTitle().contains("Confirmar"),"confirmacion propia");click(a,30);
        }
        case "requests" -> {
            check(ui.recibidos(b).size()==1,"pedido enviado sin GUI generica");
            check(ui.recibidos(a).isEmpty(),"pedido solo al destinatario");
            var r=ui.recibidos(b).getFirst(); cmd(a,"aceptar",r.id().toString());check(ui.pedidos.size()==1,"no acepta un tercero/remitente");
            cmd(b,"rechazar",r.id().toString());check(ui.pedidos.isEmpty(),"rechazo elimina pedido");
            ui.enviados.clear(); ui.enviar(a,b,"TFT2");r=ui.recibidos(b).getFirst();
            ui.pedidos.put(r.id(),new AstralDuelos.Pedido(r.id(),r.de(),r.para(),r.arena(),0));ui.vencer();
            check(ui.pedidos.isEmpty(),"vencimiento real elimina pedido");
            cmd(b,"aceptar",r.id().toString());check(!ui.duels.getArenaManager().isInMatch(b),"aceptacion vencida no inicia");
            b.setGameMode(GameMode.CREATIVE);ui.enviados.clear();ui.enviar(a,b,"Astral");check(ui.pedidos.isEmpty(),"no desafiar creativo"); b.setGameMode(GameMode.SURVIVAL);
            ui.duels.getUserManager().get(b).setRequests(false);ui.enviar(a,b,"Astral");check(ui.pedidos.isEmpty(),"respeta pedidos desactivados");ui.duels.getUserManager().get(b).setRequests(true);
            ui.duels.getConfig().set("request.use-own-inventory.drop-inventory-items",true);
            ui.enviar(a,b,"Astral");check(ui.pedidos.isEmpty(),"bloquea configuracion con perdida de items");
            ui.duels.getConfig().set("request.use-own-inventory.drop-inventory-items",false);
            var arena=ui.duels.getArenaManager().get("Astral"); arena.setDisabled(true);
            ui.enviar(a,b,"Astral");check(ui.pedidos.isEmpty(),"arena desactivada no recibe pedido");
            check(ui.elegir("Cualquiera").getName().equals("TFT1"),"cualquiera primera libre");arena.setDisabled(false);
            ui.enviados.clear();ui.enviar(a,b,"Astral");ui.enviar(a,b,"Astral");check(ui.pedidos.size()==1,"anti duplicado y spam");
            r=ui.recibidos(b).getFirst();arena.setDisabled(true);cmd(b,"aceptar",r.id().toString());check(ui.pedidos.size()==1,"revalida arena al aceptar");arena.setDisabled(false);
            cmd(b,"aceptar",r.id().toString());
        }
        case "combat" -> {
            check(a.getWorld().getName().equals("arena")&&b.getWorld().getName().equals("arena"),"aceptar inicia Duels en arena exacta");
            check(ui.duels.getArenaManager().isInMatch(a),"Duels controla combate");
            check(ui.pedidos.isEmpty(),"inicio limpia pedidos");
            cmd(a);check(a.getOpenInventory().getType()!=InventoryType.CHEST,"en duelo no abre GUI ni evade bloqueo");
            ui.enviados.clear();ui.enviar(a,b,"TFT1");check(ui.pedidos.isEmpty(),"ocupados no reciben pedidos");
            b.setHealth(0);
        }
        case "after" -> {
            check(a.getWorld().getName().equals("lobby"),"ganador vuelve al lobby");
            if(b.isDead())b.spigot().respawn();
            check(a.getInventory().contains(Material.DIAMOND,5),"ganador conserva items");
            check(ui.duels.getUserManager().get(a).getWins()==1,"victoria Duels registrada");
            check(ui.getConfig().getInt("racha."+a.getUniqueId())==1,"racha persistente");
            check(ui.getConfig().getInt("semanas."+ui.semana()+"."+a.getUniqueId())==1,"ranking semanal persistente");
            cmd(a,"resultado");check(a.getOpenInventory().getTitle().contains("Resultado"),"ventana resultado propia");
            click(a,30);
        }
        case "rematch" -> {
            check(b.getInventory().contains(Material.EMERALD,7),"perdedor conserva items");
            check(b.getWorld().getName().equals("lobby"),"perdedor vuelve al lobby");
            check(a.getOpenInventory().getTitle().contains("Confirmar"),"revancha pide nuevo consentimiento");
            ui.estadisticas(a);check(a.getOpenInventory().getTopInventory().getItem(22).getItemMeta().getLore().toString().contains("Victorias: 1"),"stats leen API Duels");
            ui.ranking(a,true);check(a.getOpenInventory().getTopInventory().getItem(10)!=null,"ranking semanal muestra ganador");
            ui.ranking(a,false);check(a.getOpenInventory().getTitle().contains("total"),"ranking total propio");
            a.closeInventory();
            ui.enviados.clear();ui.enviar(a,b,"TFT2");
            ui.salir(new org.bukkit.event.player.PlayerQuitEvent(b, net.kyori.adventure.text.Component.empty()));
            check(ui.pedidos.isEmpty(),"desconexion elimina pedidos");
            ui.enviados.clear();ui.enviar(a,b,"TFT2");
            cmd(b,"aceptar",ui.recibidos(b).getFirst().id().toString());
        }
        case "surrender" -> {check(a.getWorld().getName().equals("arenas_tft"),"segunda arena TFT2");cmd(b,"salir");}
        case "final" -> {
            check(a.getWorld().getName().equals("lobby"),"rendicion vuelve al lobby");
            check(a.getInventory().contains(Material.DIAMOND,5),"rendicion conserva ganador");
            if(b.isDead())b.spigot().respawn();
            check(ui.getConfig().getInt("racha."+a.getUniqueId())==2,"dos victorias en racha");
            check(ui.getConfig().getInt("racha."+b.getUniqueId())==0,"racha perdedor a cero");
            for(int i=0;i<29;i++) fake(String.format("Extra%02d",i));
            ui.jugadores(a,0);click(a,50);
        }
        case "pages" -> {
            check(a.getOpenInventory().getTitle().contains("2"),"segunda pagina de jugadores");
            check(a.getOpenInventory().getTopInventory().getItem(10).getType()==Material.PLAYER_HEAD,"jugadores mas alla del limite original");
            check(a.getOpenInventory().getTopInventory().getItem(48).getType()==Material.ARROW,"volver de pagina");
            ui.getConfig().set("prueba.persistente",7);ui.saveConfig();ui.reloadConfig();
            check(ui.getConfig().getInt("prueba.persistente")==7,"persistencia YAML comprobada");
            getLogger().info("DUELOSUI RESULT checks="+checks+" failures="+failures);
        }
        }
      }catch(Throwable ex){failures++;getLogger().warning("DUELOSUI FAIL "+ex);ex.printStackTrace();}
      return true;
    }
}
