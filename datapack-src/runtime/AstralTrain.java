package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.block.BlockFace;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.world.WorldLoadEvent;
import com.destroystokyo.paper.event.entity.EntityAddToWorldEvent;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;
import com.bergerkiller.bukkit.common.config.FileConfiguration;
import com.bergerkiller.bukkit.tc.controller.MinecartGroup;
import com.bergerkiller.bukkit.tc.controller.spawnable.SpawnableGroup;
import com.bergerkiller.bukkit.tc.properties.TrainPropertiesStore;
import com.bergerkiller.bukkit.tc.events.seat.MemberBeforeSeatEnterEvent;

/** Un solo tren, tres plazas. No modifica bloques, mundos ni NPC existentes. */
public final class AstralTrain extends JavaPlugin implements Listener {
    static final String NAME="astral_lobby_survival";
    MinecartGroup train;
    Location home, start;
    Vector forward;
    int wait=-1, travel=0, retry=0;
    boolean moving=false;
    boolean recovering=false;
    double lastDistance=0;
    final Set<Player> tracked=new HashSet<>();
    final NamespacedKey journey=new NamespacedKey(this,"journey");
    final Set<org.bukkit.Chunk> tickets=new HashSet<>();
    final Set<UUID> retired=new HashSet<>();

    @Override public void onEnable() {
        saveDefaultConfig();
        for(var id:getConfig().getStringList("cart-ids"))retired.add(UUID.fromString(id));
        if (!new java.io.File(getDataFolder(),"train.yml").exists()) saveResource("train.yml",false);
        getServer().getPluginManager().registerEvents(this,this);
        getServer().getScheduler().runTaskLater(this,()->{
            if (home==null && getConfig().getBoolean("enabled")) configure();
            getServer().getScheduler().runTaskTimer(this,this::tick,1,1);
        },40);
    }

    void recover() {
        // TC puede haber guardado el tren fuera de la estacion en un cierre abrupto.
        var properties=TrainPropertiesStore.exists(NAME)?TrainPropertiesStore.get(NAME):null;
        if (properties!=null) {
            var old=properties.getHolder();
            if(old!=null) {
                for(var cart:old)for(var e:new ArrayList<>(cart.getEntity().getEntity().getPassengers()))
                    if(e instanceof Player p) {p.leaveVehicle();p.teleport(platform());clearJourney(p);}
                old.destroy();
            }
        }
    }

    void configure() {
        var world=Bukkit.getWorld("lobby");
        if(world==null || Bukkit.getWorld("world")==null) {
            getLogger().warning("Falta lobby/world; tren desactivado.");return;
        }
        var face=BlockFace.valueOf(getConfig().getString("station.direction","NORTH"));
        if(!List.of(BlockFace.NORTH,BlockFace.SOUTH,BlockFace.EAST,BlockFace.WEST).contains(face))
            throw new IllegalArgumentException("Direccion debe ser cardinal");
        home=new Location(world,getConfig().getInt("station.x")+.5,getConfig().getInt("station.y"),getConfig().getInt("station.z")+.5);
        forward=face.getDirection();
        for(int i=-16;i<=16;i++) {
            var chunk=home.clone().add(forward.clone().multiply(i)).getChunk();
            if(tickets.add(chunk)) chunk.addPluginChunkTicket(this);
            // Paper carga terreno y entidades por separado. Esperar las entidades
            // evita que un coche viejo aparezca despues de crear el reemplazo.
            chunk.getEntities();
        }
        recover();
        for(var id:retired) {
            var entity=Bukkit.getEntity(id);
            if(entity instanceof Minecart)entity.remove();
        }
        // No crear el reemplazo hasta terminar de retirar TODOS los coches offline.
        // restore()+destroy() puede recuperar un grupo parcial y mover el reemplazo.
        var station=home;
        recovering=true;
        var tc=(com.bergerkiller.bukkit.tc.TrainCarts)Bukkit.getPluginManager().getPlugin("Train_Carts");
        tc.getOfflineGroups().destroyGroupAsync(NAME).whenComplete((removed,error)->{
            if(!isEnabled())return;
            getServer().getScheduler().runTask(this,()->{
                if(home!=station)return;
                if(error!=null) {getLogger().severe("Recuperacion pendiente: "+error);return;}
                TrainPropertiesStore.remove(NAME);
                recovering=false;
                retry=0;
                spawn();
            });
        });
    }

    void spawn() {
        if(home==null || recovering)return;
        try {
            var config=new FileConfiguration(new java.io.File(getDataFolder(),"train.yml"));config.load();
            // ItemStack del servidor: componente item_model moderno, sin CMD heredado.
            for(var cart:config.getNodeList("carts")) {
                var item=new ItemStack(Material.PAPER);var meta=item.getItemMeta();
                meta.setItemModel(NamespacedKey.fromString("astral:tren_"+cart.get("astral-model","cart")));
                item.setItemMeta(meta);
                cart.getNode("model").getNodeList("attachments").getFirst().set("item",item);
            }
            var group=SpawnableGroup.fromConfig(config);
            var locations=group.findSpawnLocations(home.clone().subtract(forward.clone().multiply(4)),forward,SpawnableGroup.SpawnMode.CENTER);
            if(locations==null || locations.isOccupied())throw new IllegalStateException("Faltan vias libres para el tren");
            train=group.spawn(locations);
            train.getProperties().setTrainName(NAME);
            train.getProperties().setKeepChunksLoaded(true);
            train.stop();
            // La espera nativa suprime la fisica de movimiento incluso antes
            // del primer tick propio, mientras terminan de cargar los mundos.
            train.getActions().addActionWaitForever();
            getConfig().set("cart-ids",train.stream().map(c->c.getEntity().getEntity().getUniqueId().toString()).toList());
            saveConfig();
            start=train.head().getEntity().getEntity().getLocation();
            wait=-1;moving=false;travel=0;
        } catch(Exception e) {
            if(train!=null && !train.isRemoved())train.destroy();
            train=null;
            getLogger().warning("No se pudo preparar tren: "+e.getMessage());retry=200;
        }
    }

    List<Player> riders() {
        var result=new ArrayList<Player>();
        if(train!=null && !train.isRemoved())for(var cart:train)
            for(var entity:cart.getEntity().getEntity().getPassengers())
                if(entity instanceof Player p && p.isOnline()) result.add(p);
        return result;
    }

    Location destination(Player p) {
        var survival=Bukkit.getWorld("world");
        var bed=p.getRespawnLocation(true);
        // Paper valida el punto de reaparicion; no enviar a lobby/otras mazmorras.
        return bed!=null && bed.getWorld().equals(survival)?bed:survival.getSpawnLocation();
    }

    void tick() {
        if(home==null || recovering)return;
        if(retry>0) {if(--retry==0)spawn();return;}
        if(train==null || train.isRemoved() || train.isEmpty()) {train=null;retry=40;return;}
        var passengers=riders();
        for(var p:new ArrayList<>(tracked))if(!passengers.contains(p))clearJourney(p);
        for(var p:passengers)if(tracked.add(p))p.getPersistentDataContainer().set(journey,PersistentDataType.BYTE,(byte)1);
        if(!moving) {
            train.stop();
            if(passengers.isEmpty()) {wait=-1;return;}
            if(wait<0)wait=100;
            if(wait%20==0)for(var p:passengers) {
                p.sendMessage("§6Tren al survival: salimos en "+wait/20+" s.");
                p.playSound(p.getLocation(),Sound.BLOCK_NOTE_BLOCK_BELL,0.8f,1.6f);
            }
            if(--wait<=0) {
                train.getActions().clear();
                moving=true;travel=0;
                start=train.head().getEntity().getEntity().getLocation();
                for(var p:passengers)p.playSound(p.getLocation(),Sound.BLOCK_NOTE_BLOCK_FLUTE,1f,0.6f);
            }
            return;
        }
        travel++;
        double distance=train.head().getEntity().getEntity().getLocation().toVector().subtract(start.toVector()).dot(forward);
        if(distance>=8) {
            lastDistance=distance;
            train.stop();
            // Se toma la lista al llegar, nunca la lista de quienes subieron al principio.
            for(var p:passengers) {
                p.leaveVehicle();
                if(!p.teleport(destination(p))) {
                    p.teleport(platform());
                    p.sendMessage("§cViaje cancelado por otro plugin. Volviste al anden.");
                }
                clearJourney(p);
            }
            reset();return;
        }
        if(travel>240 || train.size()!=4) {reset();return;}
        train.setForwardForce(.08);
    }

    Location platform() {
        var side=new Vector(-forward.getZ(),0,forward.getX()).multiply(2);
        return home.clone().add(side).add(0,.2,0);
    }

    void reset() {
        for(var p:riders()) {p.leaveVehicle();p.teleport(platform());clearJourney(p);}
        if(train!=null && !train.isRemoved())train.destroy();
        train=null;moving=false;wait=-1;retry=20;
    }

    @EventHandler(ignoreCancelled=true) public void enter(MemberBeforeSeatEnterEvent e) {
        if(train!=null && e.getMember().getGroup()==train && (moving || !(e.getEntity() instanceof Player)))e.setCancelled(true);
    }
    @EventHandler public void quit(PlayerQuitEvent e) {
        if(riders().contains(e.getPlayer())) {e.getPlayer().leaveVehicle();e.getPlayer().teleport(platform());clearJourney(e.getPlayer());}
    }
    void clearJourney(Player p) {tracked.remove(p);p.getPersistentDataContainer().remove(journey);}
    @EventHandler public void join(PlayerJoinEvent e) {
        // En un corte abrupto, los pasajeros guardados vuelven a un anden, nunca a un tren ausente.
        getServer().getScheduler().runTaskLater(this,()->{
            var p=e.getPlayer();
            if(p.isOnline() && p.getPersistentDataContainer().has(journey,PersistentDataType.BYTE)) {
                if(home!=null && p.getWorld().equals(home.getWorld()))p.teleport(platform());
                clearJourney(p);
            }
        },60);
    }
    @EventHandler public void worldLoaded(WorldLoadEvent e) {
        if(home==null && getConfig().getBoolean("enabled") && List.of("lobby","world").contains(e.getWorld().getName()))
            getServer().getScheduler().runTask(this,()->{if(home==null)configure();});
    }
    @EventHandler public void oldCartLoaded(EntityAddToWorldEvent e) {
        // Un cierre abrupto puede dejar un coche fuera del grupo guardado por TC.
        // Solo retirar los UUID propios guardados antes de ese cierre.
        if(e.getEntity() instanceof Minecart && retired.contains(e.getEntity().getUniqueId()))
            getServer().getScheduler().runTask(this,()->e.getEntity().remove());
    }
    @Override public void onDisable() {
        if(home!=null) {
            for(var p:riders()) {p.leaveVehicle();p.teleport(platform());clearJourney(p);}
            if(train!=null && !train.isRemoved())train.destroy();
        }
        for(var chunk:tickets)chunk.removePluginChunkTicket(this);
        tickets.clear();
    }
    @Override public boolean onCommand(CommandSender sender,Command command,String label,String[] args) {
        if(!sender.hasPermission("astraltren.admin"))return true;
        try {
            if(args.length==5 && args[0].equalsIgnoreCase("fijar")) {
                if(home!=null) {sender.sendMessage("Apagar el tren antes de cambiar la estacion: /astraltren apagar");return true;}
                int x=Integer.parseInt(args[1]),y=Integer.parseInt(args[2]),z=Integer.parseInt(args[3]);
                var face=BlockFace.valueOf(args[4].toUpperCase(Locale.ROOT));
                if(!List.of(BlockFace.NORTH,BlockFace.SOUTH,BlockFace.EAST,BlockFace.WEST).contains(face))throw new IllegalArgumentException();
                getConfig().set("station.x",x);getConfig().set("station.y",y);getConfig().set("station.z",z);
                getConfig().set("station.direction",face.name());getConfig().set("enabled",true);saveConfig();
                configure();sender.sendMessage("Estacion guardada. Revisar vias, anden y consola.");
            } else if(args.length==1 && args[0].equalsIgnoreCase("recrear")) {
                if(home==null && !getConfig().getBoolean("enabled")) {
                    sender.sendMessage("Estacion desactivada; usar fijar para activarla.");return true;
                }
                reset();configure();
                sender.sendMessage("Tren recreado conservando la estacion guardada.");
            } else if(args.length==1 && args[0].equalsIgnoreCase("apagar")) {
                reset();home=null;retry=0;recovering=false;getConfig().set("enabled",false);saveConfig();
                for(var chunk:tickets)chunk.removePluginChunkTicket(this);tickets.clear();
                sender.sendMessage("Tren apagado; pasajeros devueltos al anden.");
            } else sender.sendMessage("/astraltren fijar <x> <y> <z> <NORTH|SOUTH|EAST|WEST> | recrear | apagar. Estado: "+(home==null?"sin estacion":moving?"viajando":"anden"));
        } catch(Exception e) {sender.sendMessage("No se pudo configurar. Usar coordenadas enteras y direccion cardinal.");getLogger().warning(e.toString());}
        return true;
    }
}
