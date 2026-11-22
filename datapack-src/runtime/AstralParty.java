package astral;

import java.util.*;
import java.util.stream.*;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import me.clip.placeholderapi.expansion.PlaceholderExpansion;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.title.Title;

/** Party en memoria. Una caida letal se convierte en espera sin producir drops ni perder inventario. */
public final class AstralParty extends JavaPlugin implements Listener {
    final Map<UUID, UUID> leaders = new LinkedHashMap<>();
    public final Map<UUID, LinkedHashSet<UUID>> groups = new LinkedHashMap<>();
    record Invite(UUID leader, long until, UUID token) {}
    public final Map<UUID, Invite> invites = new HashMap<>();
    public static final class Fallen {
        final World world; final Location origin; final GameMode mode; final long until;
        UUID target; boolean free;
        public Fallen(Player p, long until) { world=p.getWorld(); origin=p.getLocation(); mode=p.getGameMode(); this.until=until; }
    }
    public final Map<UUID, Fallen> fallen = new HashMap<>();
    final Map<UUID,Long> immunity = new HashMap<>();
    record Wipe(World world, List<UUID> members, long until) {}
    public final List<Wipe> wipes = new ArrayList<>();
    public record Boss(String world, double x, double y, double z, boolean boss) {}
    public final List<Boss> bosses = new ArrayList<>();
    public record FightRoom(String world,double x,double y,double z,double radius,
                            double x1,double z1,double x2,double z2,String key,String controller,double floor) {
        public FightRoom(String world,double x,double y,double z,double radius,
                         double x1,double z1,double x2,double z2,String key,String controller) {
            this(world,x,y,z,radius,x1,z1,x2,z2,key,controller,Double.NEGATIVE_INFINITY);
        }
        // Piso: durante la pelea no se puede bajar a cuevas ni barrancos de la sala.
        public boolean contains(Location l) { return l.getWorld().getName().equals(world)
            &&l.getX()>x1&&l.getX()<x2&&l.getZ()>z1&&l.getZ()<z2&&l.getY()>=floor; }
        boolean enters(Location l) { return contains(l)&&Math.pow(l.getX()-x,2)+Math.pow(l.getY()-y,2)+Math.pow(l.getZ()-z,2)<=radius*radius; }
        public double side() { return Math.min(x2-x1,z2-z1); }
        static double clamp(double value,double lo,double hi) { return Math.max(lo,Math.min(hi,value)); }
        public double centerX(double playerX) {
            return Math.abs((x2-x1)-(z2-z1))<=4 || x2-x1<=z2-z1 ? (x1+x2)/2 : clamp(playerX,x1+side()/2,x2-side()/2);
        }
        public double centerZ(double playerZ) {
            return Math.abs((x2-x1)-(z2-z1))<=4 || z2-z1<=x2-x1 ? (z1+z2)/2 : clamp(playerZ,z1+side()/2,z2-side()/2);
        }
    }
    public final List<FightRoom> fightRooms = new ArrayList<>();
    final Set<FightRoom> activeRooms = new HashSet<>();
    final Map<UUID,FightRoom> borders = new HashMap<>();
    final Map<UUID,Location> borderSafe = new HashMap<>();
    Set<String> worlds;
    int waves, boss, wipeSeconds, max; public long clock;
    public NamespacedKey recovery; Expansion expansion;
    static String c(String s) { return ChatColor.translateAlternateColorCodes('&',s); }
    void msg(Player p,String s) { p.sendMessage(c("&d[Party] &f"+s)); }
    Component link(String text,NamedTextColor color,String command,String hover) {
        return Component.text(text,color).clickEvent(ClickEvent.runCommand(command)).hoverEvent(Component.text(hover));
    }
    Component openButton() { return link(" [Abrir Party]",NamedTextColor.LIGHT_PURPLE,"/party","Abrir los controles de tu party"); }
    void notice(Player p,String text) { if(p!=null)p.sendMessage(Component.text("[Party] "+text).append(openButton())); }
    void transfer(Player p,Player t) {
        if(!leader(p)||t==null||t==p||!Objects.equals(leaders.get(t.getUniqueId()),p.getUniqueId())) {notice(p,"Elegi un companero de tu party.");return;}
        var ids=groups.remove(p.getUniqueId()); groups.put(t.getUniqueId(),ids);
        ids.forEach(id->leaders.put(id,t.getUniqueId()));
        invites.values().removeIf(i->i.leader.equals(p.getUniqueId()));
        sync(); for(var m:members(t))notice(m,t.getName()+" es el nuevo lider.");
    }
    Player player(UUID id) { return id == null ? null : Bukkit.getPlayer(id); }
    public List<Player> members(Player p) {
        var ids=groups.get(leaders.get(p.getUniqueId()));
        return ids==null ? List.of(p) : ids.stream().map(this::player).filter(Objects::nonNull).toList();
    }
    public boolean inParty(Player p) { return leaders.containsKey(p.getUniqueId()); }
    public boolean leader(Player p) { return p.getUniqueId().equals(leaders.get(p.getUniqueId())); }
    void tell(Player p,String s) { for(var m:members(p)) msg(m,s); }
    void console(String cmd) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(),cmd); }
    void sync() {
        console("astralpartysync clear all");
        leaders.forEach((id,l)-> { var p=player(id); if(p!=null) console("astralpartysync add "+l+" "+p.getName()); });
    }
    @Override public void onEnable() {
        try {
            var props=new Properties(); try(var in=getResource("party.properties")){props.load(in);}
            waves=Integer.parseInt(props.getProperty("waves")); boss=Integer.parseInt(props.getProperty("boss"));
            wipeSeconds=Integer.parseInt(props.getProperty("wipe")); max=Integer.parseInt(props.getProperty("max"));
            worlds=new HashSet<>(List.of(props.getProperty("worlds").split(",")));
            try(var in=new Scanner(getResource("boss-rooms.csv"), java.nio.charset.StandardCharsets.UTF_8)) {
                while(in.hasNextLine()) { var a=in.nextLine().split(","); if(a.length==5) bosses.add(new Boss(a[0],Double.parseDouble(a[1]),Double.parseDouble(a[2]),Double.parseDouble(a[3]),Boolean.parseBoolean(a[4]))); }
            }
            try(var in=new Scanner(getResource("fight-rooms.csv"),java.nio.charset.StandardCharsets.UTF_8)) {
                while(in.hasNextLine()) {var a=in.nextLine().split(",",-1);if(a.length!=12)throw new IllegalArgumentException("Sala invalida");
                    fightRooms.add(new FightRoom(a[0],Double.parseDouble(a[1]),Double.parseDouble(a[2]),Double.parseDouble(a[3]),Double.parseDouble(a[4]),Double.parseDouble(a[5]),Double.parseDouble(a[6]),Double.parseDouble(a[7]),Double.parseDouble(a[8]),a[9],a[10],
                        a[11].isEmpty()?Double.NEGATIVE_INFINITY:Double.parseDouble(a[11])));}
            }
        } catch(Exception e) { throw new IllegalStateException("Configuracion Party invalida",e); }
        recovery=new NamespacedKey(this,"recuperar");
        getServer().getPluginManager().registerEvents(this,this);
        expansion=new Expansion(); expansion.register();
        Bukkit.getScheduler().runTaskTimer(this,()->tick(),1,1);
        Bukkit.getScheduler().runTaskLater(this,()->{ sync(); for(var p:Bukkit.getOnlinePlayers()) recover(p); },40);
    }
    @Override public void onDisable() {
        for(var p:Bukkit.getOnlinePlayers())clearBorder(p);
        for(var id:new ArrayList<>(fallen.keySet())) { var p=player(id); if(p!=null) exit(p); }
        if(expansion!=null) expansion.unregister();
    }
    // Registro temporal (20/11): por que aparece o desaparece el borde. Max 1 linea por motivo cada 2 s.
    final Map<String,Long> borderLog = new HashMap<>();
    final Map<UUID,Long> borderSent = new HashMap<>();
    void borderDebug(Player p,String what) {
        var k=p.getUniqueId()+what;var last=borderLog.get(k);
        if(last!=null&&clock-last<40)return;borderLog.put(k,clock);
        getLogger().info("[borde] "+p.getName()+" "+what+" @ "+p.getWorld().getName()+" "+p.getLocation().getBlockX()+","+p.getLocation().getBlockY()+","+p.getLocation().getBlockZ()+" "+p.getGameMode());
    }
    void clearBorder(Player p,String why) {
        if(borders.containsKey(p.getUniqueId()))borderDebug(p,"SACA "+why+" sala="+borders.get(p.getUniqueId()).controller);
        clearBorder(p);
    }
    void clearBorder(Player p) {
        borderSent.remove(p.getUniqueId());
        if(borders.remove(p.getUniqueId())!=null)p.setWorldBorder(null);
        borderSafe.remove(p.getUniqueId());
    }
    boolean fighting(FightRoom r,List<Entity> entities) {
        for(var e:entities) {
            if(e.isDead())continue;
            var tags=e.getScoreboardTags();
            if(r.key.equals("inf")&&tags.contains("inf.mob"))return true;
            if(r.key.equals("fosa")&&(tags.contains("fosa.mob")||tags.contains("fosa.jefe")))return true;
            // El controlador conserva .on durante las esperas; .fin libera enseguida.
            // El nombre identifica la sala; el soporte puede estar en la llegada y no en el centro.
            if(e instanceof ArmorStand&&r.controller.equals(ChatColor.stripColor(e.getName()))
                &&e.getX()>r.x1&&e.getX()<r.x2&&e.getZ()>r.z1&&e.getZ()<r.z2
                &&tags.contains(r.key+".on")&&!tags.contains(r.key+".fin"))return true;
        }
        return false;
    }
    void refreshFightRooms() {
        activeRooms.clear();var entities=new HashMap<String,List<Entity>>();
        for(var r:fightRooms) {
            var w=Bukkit.getWorld(r.world);if(w==null||w.getPlayers().isEmpty())continue;
            if(fighting(r,entities.computeIfAbsent(r.world,k->w.getEntities())))activeRooms.add(r);
        }
    }
    org.bukkit.WorldBorder newBorder(FightRoom r,Player p) {
        var border=Bukkit.createWorldBorder();border.setCenter(r.centerX(p.getX()),r.centerZ(p.getZ()));border.setSize(r.side());
        border.setDamageAmount(0);border.setDamageBuffer(0);border.setWarningDistance(3);border.setWarningTime(0);
        return border;
    }
    void updateBorder(Player p) {
        var id=p.getUniqueId();var r=borders.get(id);
        // Creativo tambien ve el borde: el dueno prueba las salas asi. Espectador libre queda afuera.
        if(p.isDead()||(!busy(p)&&p.getGameMode()==GameMode.SPECTATOR)) {clearBorder(p,"muerto/espectador");return;}
        if(r!=null&&(!activeRooms.contains(r)||!r.world.equals(p.getWorld().getName()))) {clearBorder(p,activeRooms.contains(r)?"otro mundo":"sala sin pelea");r=null;}
        // Si algo (otro plugin, Paper) le saco el borde visual, volver a ponerlo.
        if(r!=null&&p.getWorldBorder()==null) {borderDebug(p,"VISUAL PERDIDO sala="+r.controller);p.setWorldBorder(newBorder(r,p));}
        if(r==null) {
            // Camara del caido: misma sala que su companero, incluso en modo libre.
            var f=fallen.get(id);var target=f==null?null:player(f.target);
            if(target!=null)r=borders.get(target.getUniqueId());
            if(r==null)r=activeRooms.stream().filter(room->room.enters(p.getLocation()))
                .min(Comparator.comparingDouble(room->Math.pow(room.x-p.getX(),2)+Math.pow(room.z-p.getZ(),2))).orElse(null);
            if(r==null)return;
            p.setWorldBorder(newBorder(r,p));borders.put(id,r);borderDebug(p,"PONE sala="+r.controller+" lado="+r.side());
            if(r.contains(p.getLocation()))borderSafe.put(id,p.getLocation());
        }
        // Al llegar desde otro mundo, Minecraft le manda al cliente el borde del mundo despues del nuestro
        // y lo tapa (Bosque y Mina, primera sala). Reenviarlo cada 2 s lo mantiene visible.
        var sent=borderSent.get(id);
        if(sent==null||clock-sent>=40) {p.setWorldBorder(newBorder(r,p));borderSent.put(id,clock);}
        var visual=p.getWorldBorder();
        if(visual!=null) {
            double cx=r.centerX(p.getX()),cz=r.centerZ(p.getZ());var old=visual.getCenter();
            if(Math.abs(cx-old.getX())>=.5||Math.abs(cz-old.getZ())>=.5)visual.setCenter(cx,cz);
        }
        if(!r.contains(p.getLocation())) {
            var safe=borderSafe.get(id);
            if(safe!=null&&r.contains(safe)) {p.setFallDistance(0);p.setVelocity(new org.bukkit.util.Vector());p.teleport(safe);}
        } else borderSafe.put(id,p.getLocation());
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void borderMove(PlayerMoveEvent e) {
        var p=e.getPlayer();var r=borders.get(p.getUniqueId());if(r==null||e.getTo()==null)return;
        if(!activeRooms.contains(r)){clearBorder(p,"mover: sala sin pelea");return;}
        if(e instanceof PlayerTeleportEvent t&&t.getCause()!=PlayerTeleportEvent.TeleportCause.ENDER_PEARL
            &&t.getCause()!=PlayerTeleportEvent.TeleportCause.CHORUS_FRUIT) {
            if(!r.contains(e.getTo()))clearBorder(p,"teleport afuera "+t.getCause());return;
        }
        if(!r.contains(e.getTo())) {
            var safe=borderSafe.get(p.getUniqueId());
            e.setTo(safe==null?e.getFrom():safe);p.setFallDistance(0);p.setVelocity(new org.bukkit.util.Vector());
        } else borderSafe.put(p.getUniqueId(),e.getTo().clone());
    }
    @EventHandler public void borderWorld(PlayerChangedWorldEvent e) {clearBorder(e.getPlayer(),"cambio de mundo");}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void borderTeleport(PlayerTeleportEvent e) {borderMove(e);}
    @EventHandler(priority=EventPriority.MONITOR) public void borderDeath(PlayerDeathEvent e) {clearBorder(e.getEntity(),"muerte");}
    void create(Player p) { var id=p.getUniqueId(); leaders.put(id,id); groups.put(id,new LinkedHashSet<>(List.of(id))); }
    public boolean busy(Player p) { return fallen.containsKey(p.getUniqueId()); }
    void leave(Player p) {
        if(!inParty(p)) return;
        if(busy(p)) exit(p);
        var l=leaders.get(p.getUniqueId());
        if(leader(p)) {
            var copy=new ArrayList<>(members(p)); tell(p,p.getName()+" disolvio la party.");
            for(var m:copy) { if(busy(m)) exit(m); leaders.remove(m.getUniqueId()); }
            groups.remove(l); invites.values().removeIf(i->i.leader.equals(l));
        } else { tell(p,p.getName()+" salio de la party."); groups.get(l).remove(p.getUniqueId()); leaders.remove(p.getUniqueId()); }
        sync();
    }
    @Override public boolean onCommand(CommandSender sender,Command command,String label,String[] a) {
        if(command.getName().equals("astralpartyinternal")) {
            if(!(sender instanceof ConsoleCommandSender)) return true;
            if(a.length>0 && a[0].equals("sync")) sync();
            if(a.length==2 && a[0].equals("victory")) victory(Bukkit.getWorld(a[1]));
            if(a.length==2 && a[0].equals("fresh")) freshCopy(a[1]);
            return true;
        }
        if(!(sender instanceof Player p)) return true;
        String sub=a.length==0?"menu":a[0].toLowerCase(Locale.ROOT);
        if(sub.equals("menu")) { menu(p,false,0); return true; }
        if(sub.equals("mirar")) { spectateMenu(p); return true; }
        if(sub.equals("volver")) { rejoin(p); return true; }
        if(sub.equals("crear")) { if(!inParty(p)) { create(p); sync(); } menu(p,true,0); return true; }
        if(sub.equals("invitar")) {
            var t=a.length>1?Bukkit.getPlayerExact(a[1]):null;
            if(t==null || t==p) { notice(p,"Elegi otro jugador conectado desde el menu."); return true; }
            if(inParty(t)) { msg(p,"Ese jugador ya esta en una party."); return true; }
            if(!inParty(p)) create(p);
            if(!leader(p)) msg(p,"Solo el lider puede invitar.");
            else if(members(p).size()>=max) msg(p,"La party esta llena (maximo "+max+").");
            else {
                var invite=new Invite(p.getUniqueId(),clock+1200,UUID.randomUUID());
                var old=invites.put(t.getUniqueId(),invite);
                if(old!=null)notice(player(old.leader),"La invitacion a "+t.getName()+" fue reemplazada.");
                String token=" "+p.getUniqueId()+" "+invite.token;
                p.sendMessage(Component.text("[Party] Invitaste a "+t.getName()+" (60 segundos).")
                    .append(link(" [Cancelar]",NamedTextColor.RED,"/party cancelar "+t.getName()+token,"Retirar esta invitacion")));
                t.sendMessage(Component.text("[Party] "+p.getName()+" te invito. ")
                    .append(link("[✔ Aceptar]",NamedTextColor.GREEN,"/party aceptar"+token,"Unirte a la party de "+p.getName()))
                    .append(link(" [✘ Rechazar]",NamedTextColor.RED,"/party rechazar"+token,"Rechazar esta invitacion")).append(openButton()));
                t.showTitle(Title.title(Component.text("Invitacion de party"),Component.text("de "+p.getName())));
                t.playSound(t.getLocation(),Sound.ENTITY_EXPERIENCE_ORB_PICKUP,0.8f,1.2f);
            }
            sync(); return true;
        }
        if(sub.equals("cancelar")) {
            var t=a.length>1?Bukkit.getPlayerExact(a[1]):null; var i=t==null?null:invites.get(t.getUniqueId());
            if(i!=null&&i.leader.equals(p.getUniqueId())&&(a.length==2||(a.length==4&&a[2].equals(i.leader.toString())&&a[3].equals(i.token.toString())))) {
                invites.remove(t.getUniqueId()); notice(p,"Invitacion cancelada.");notice(t,p.getName()+" cancelo la invitacion.");
            } else notice(p,"Esa invitacion ya no esta disponible.");
            return true;
        }
        if((sub.equals("aceptar")||sub.equals("rechazar"))&&a.length>1) {
            var i=invites.get(p.getUniqueId());
            if(i==null||a.length!=3||!a[1].equals(i.leader.toString())||!a[2].equals(i.token.toString())) {notice(p,"Ese boton pertenece a una invitacion anterior.");return true;}
        }
        if(sub.equals("aceptar")) {
            var i=invites.remove(p.getUniqueId());
            if(i==null || clock>=i.until || !groups.containsKey(i.leader)) msg(p,"La invitacion vencio o la party ya no existe.");
            else if(inParty(p)) msg(p,"Sali de tu party antes de aceptar otra.");
            else if(groups.get(i.leader).size()>=max) msg(p,"La party se lleno.");
            else { leaders.put(p.getUniqueId(),i.leader); groups.get(i.leader).add(p.getUniqueId()); for(var m:members(p))notice(m,p.getName()+" se unio a la party."); sync(); }
            menu(p,false,0); return true;
        }
        if(sub.equals("rechazar")) { var i=invites.remove(p.getUniqueId()); if(i!=null)notice(player(i.leader),p.getName()+" rechazo la invitacion."); notice(p,"Invitacion rechazada."); return true; }
        if(sub.equals("lider")) { transfer(p,a.length>1?Bukkit.getPlayerExact(a[1]):null);return true; }
        if(sub.equals("salir") || sub.equals("disolver")) {
            if(sub.equals("disolver") && !leader(p)) msg(p,"Solo el lider puede disolver."); else leave(p);
            return true;
        }
        if(sub.equals("echar")) {
            var t=a.length>1?Bukkit.getPlayerExact(a[1]):null;
            if(!leader(p)) msg(p,"Solo el lider puede echar.");
            else if(t==null || t==p || !Objects.equals(leaders.get(t.getUniqueId()),p.getUniqueId())) msg(p,"Elegi un companero de tu party.");
            else { leave(t); msg(t,"Te echaron de la party."); }
            return true;
        }
        notice(p,"Invita, acepta y administra tu grupo desde el menu."); return true;
    }
    public static final class View implements InventoryHolder {
        Inventory inventory; final Map<Integer,Runnable> actions=new HashMap<>();
        public Inventory getInventory(){return inventory;}
    }
    // Ventanas ilustradas (arte de Gemini, duelos_party_ui.py): titulos = glifos del pack, botones = items.
    final Properties titles=new Properties();
    static final int[] MEMBER_SLOTS={10,11,12,14,15,16};
    static final int[] LEFT={18,19,20,21,27,28,29,30}, RIGHT={23,24,25,26,32,33,34,35};
    String title(String key,String fallback) {
        if(titles.isEmpty()) try(var in=getResource("titulos-ui.properties")){ if(in!=null)titles.load(in);}catch(Exception ignored){}
        return titles.getProperty(key,c(fallback));
    }
    View view(Player p,String key,String fallback) {
        var v=new View(); v.inventory=Bukkit.createInventory(v,54,title(key,fallback)); return v;
    }
    ItemStack item(Material m,String title,String... lore) {
        var i=new ItemStack(m); var meta=i.getItemMeta(); meta.setDisplayName(c(title));
        meta.setLore(Arrays.stream(lore).map(AstralParty::c).toList()); i.setItemMeta(meta); return i;
    }
    ItemStack head(Player p,String title,String... lore) {
        var i=item(Material.PLAYER_HEAD,title,lore); var meta=(SkullMeta)i.getItemMeta(); meta.setOwningPlayer(p); i.setItemMeta(meta); return i;
    }
    ItemStack icon(String model,Material m,String title,String... lore) {
        var i=item(m,title,lore); var meta=i.getItemMeta(); meta.setItemModel(NamespacedKey.fromString(model)); i.setItemMeta(meta); return i;
    }
    void button(View v,int slot,ItemStack item,Runnable action) { v.inventory.setItem(slot,item); if(action!=null)v.actions.put(slot,action); }
    /** Boton grande de Gemini partido en casillas: astral:duelparty/<nombre>_<i>. */
    void card(View v,int[] slots,String name,Runnable action,String title,String... lore) {
        for(int i=0;i<slots.length;i++) button(v,slots[i],icon("astral:duelparty/"+name+"_"+i,Material.PAPER,title,lore),action);
    }
    void nav(View v,Player p,Runnable back) {
        button(v,45,icon("astral:menu/icon_back",Material.ARROW,"&fVolver"),back);
        button(v,53,icon("astral:menu/icon_close",Material.BARRIER,"&cCerrar"),p::closeInventory);
    }
    boolean inDungeon(Player p) { return worlds.contains(p.getWorld().getName()); }
    void menu(Player p,boolean inviting,int page) {
        if(busy(p)) { spectateMenu(p); return; }
        if(inDungeon(p)) { msg(p,"La party se arma antes de entrar a la mazmorra."); return; }
        if(inviting) { inviteMenu(p,page); return; }
        var v=view(p,"party.menu.hasta_6_jugadores_por_party","&8Party");
        if(inParty(p)) {
            var list=members(p);
            for(int i=0;i<Math.min(list.size(),MEMBER_SLOTS.length);i++) {
                var t=list.get(i);
                button(v,MEMBER_SLOTS[i],head(t,(leader(t)?"&6♛ ":"&d")+t.getName(),"&7"+t.getWorld().getName(),leader(p)&&t!=p?"&eClic para administrar":"&7Companero de party"),
                    leader(p)&&t!=p?()->memberMenu(p,t,false):null);
            }
            if(leader(p)) {
                card(v,LEFT,"p_invitar",()->inviteMenu(p,0),"&a&lInvitar","&7Jugadores conectados, mismo mundo primero");
                card(v,RIGHT,"p_disolver",()->{leave(p);menu(p,false,0);},"&c&lDisolver","&7Termina la party para todos");
            } else {
                card(v,LEFT,"p_invitar_off",null,"&7Invitar","&7Solo el lider invita");
                card(v,RIGHT,"p_salir",()->{leave(p);menu(p,false,0);},"&c&lSalir","&7Dejas la party");
            }
        } else {
            var invite=invites.get(p.getUniqueId());
            if(invite!=null && clock<invite.until && groups.containsKey(invite.leader)) {
                var l=player(invite.leader); String from=l==null?"":l.getName();
                card(v,LEFT,"p_aceptar",()->p.performCommand("party aceptar"),"&a&lAceptar","&7Unirte a la party de "+from);
                card(v,RIGHT,"p_rechazar",()->{p.performCommand("party rechazar");menu(p,false,0);},"&c&lRechazar","&7Invitacion de "+from);
            } else {
                card(v,LEFT,"p_crear",()->{if(!inParty(p)){create(p);sync();}inviteMenu(p,0);},"&a&lCrear party","&7Crea tu grupo e invita jugadores");
                card(v,RIGHT,"p_aceptar_off",null,"&7Sin invitaciones","&7Cuando te inviten, aceptas aca");
            }
        }
        nav(v,p,()->{p.closeInventory();console("dm open principal "+p.getName());});
        p.openInventory(v.inventory);
    }
    void inviteMenu(Player p,int page) {
        if(inParty(p)&&!leader(p)) { menu(p,false,0); return; }
        var choices=Bukkit.getOnlinePlayers().stream().filter(t->t!=p&&!inParty(t))
            .sorted(Comparator.comparing((Player t)->t.getWorld()!=p.getWorld()).thenComparing(Player::getName)).collect(Collectors.toList());
        int pages=Math.max(1,(choices.size()+35)/36), current=Math.max(0,Math.min(page,pages-1));
        var v=view(p,"party.lista.invitar_jugadores","&8Invitar jugadores");
        for(int i=current*36;i<Math.min(choices.size(),(current+1)*36);i++) {
            var t=choices.get(i);
            button(v,i%36,head(t,"&d"+t.getName(),"&7"+t.getWorld().getName(),"&eClic para invitar"),()->{p.performCommand("party invitar "+t.getName());inviteMenu(p,current);});
        }
        if(choices.isEmpty()) button(v,13,item(Material.PAPER,"&7No hay jugadores libres conectados"),null);
        if(current>0) button(v,47,icon("astral:menu/icon_back",Material.ARROW,"&fAnterior"),()->inviteMenu(p,current-1));
        if(current<pages-1) button(v,51,item(Material.ARROW,"&fSiguiente"),()->inviteMenu(p,current+1));
        nav(v,p,()->menu(p,false,0)); p.openInventory(v.inventory);
    }
    void memberMenu(Player p,Player t,boolean confirm) {
        if(!leader(p)||!Objects.equals(leaders.get(t.getUniqueId()),p.getUniqueId())||p==t)return;
        var v=view(p,confirm?"party.dialogo.confirmar_expulsion":"party.dialogo.administrar_companero",confirm?"&8Confirmar expulsion":"&8Administrar companero");
        button(v,13,head(t,"&d"+t.getName(),"&7Companero de party"),null);
        if(confirm) {
            card(v,LEFT,"p_echar",()->{p.performCommand("party echar "+t.getName());menu(p,false,0);},"&c&lConfirmar: echar","&7"+t.getName()+" sale de la party");
            card(v,RIGHT,"p_rechazar",()->memberMenu(p,t,false),"&fCancelar");
        } else {
            card(v,LEFT,"p_echar",()->memberMenu(p,t,true),"&c&lEchar","&7Pide confirmacion");
            card(v,RIGHT,"p_lider",()->{transfer(p,t);menu(p,false,0);},"&6&lDar lider","&7"+t.getName()+" pasa a ser el lider");
        }
        nav(v,p,()->menu(p,false,0)); p.openInventory(v.inventory);
    }
    @EventHandler public void click(InventoryClickEvent e) {
        if(e.getView().getTopInventory().getHolder() instanceof View v) {
            e.setCancelled(true);
            if(!e.isLeftClick())return;
            if(e.getWhoClicked() instanceof Player p) { var action=v.actions.get(e.getRawSlot()); if(action!=null) { p.playSound(p.getLocation(),Sound.UI_BUTTON_CLICK,0.6f,1); Bukkit.getScheduler().runTask(this,action); } }
        }
    }
    @EventHandler public void drag(InventoryDragEvent e) { if(e.getView().getTopInventory().getHolder() instanceof View) e.setCancelled(true); }
    List<Player> living(Player p,World w) {
        return members(p).stream().filter(t->t.getWorld()==w&&!busy(t)&&!t.isDead()&&(t.getGameMode()==GameMode.SURVIVAL||t.getGameMode()==GameMode.ADVENTURE)).toList();
    }
    public int delay(Player p) {
        var l=p.getLocation();
        var room= bosses.stream().filter(b->b.world.equals(p.getWorld().getName())).min(Comparator.comparingDouble(b->l.distanceSquared(new Location(p.getWorld(),b.x,b.y,b.z))));
        return room.isPresent()&&room.get().boss?boss:waves;
    }
    void fall(Player p) {
        var f=new Fallen(p,clock+20L*delay(p)); fallen.put(p.getUniqueId(),f);
        p.addScoreboardTag("astral.party.fallen");
        countDeath(p);
        p.getPersistentDataContainer().set(recovery,PersistentDataType.STRING,f.mode.name());
        p.closeInventory(); p.setGameMode(GameMode.SPECTATOR); p.setHealth(p.getAttribute(Attribute.MAX_HEALTH).getValue());
        var alive=living(p,f.world);
        if(alive.isEmpty()) wipe(p,f.world); else { var nearest=alive.stream().min(Comparator.comparingDouble(t->t.getLocation().distanceSquared(f.origin))).orElseThrow(); watch(p,nearest,false); }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void damage(EntityDamageEvent e) {
        if(!(e.getEntity() instanceof Player p)) return;
        if(clock < immunity.getOrDefault(p.getUniqueId(),0L)) {e.setCancelled(true);return;}
        if(busy(p)) {e.setCancelled(true);return;}
        if(inParty(p)&&worlds.contains(p.getWorld().getName())&&(p.getGameMode()==GameMode.SURVIVAL||p.getGameMode()==GameMode.ADVENTURE)&&e.getFinalDamage()>=p.getHealth()) {
            e.setCancelled(true); fall(p);
        }
    }
    // /kill y danos inevitables siguen usando el evento real; se conserva todo y se fuerza respawn.
    @EventHandler(priority=EventPriority.LOWEST) public void death(PlayerDeathEvent e) {
        var p=e.getEntity(); if(!inParty(p)||!worlds.contains(p.getWorld().getName())) return;
        e.setKeepInventory(true);e.getDrops().clear();e.setKeepLevel(true);e.setDroppedExp(0);
        p.addScoreboardTag("astral.party.fallen");
        if(!busy(p)) countDeath(p);
        if(!busy(p)) { var f=new Fallen(p,clock+20L*delay(p)); fallen.put(p.getUniqueId(),f); p.getPersistentDataContainer().set(recovery,PersistentDataType.STRING,f.mode.name()); }
        Bukkit.getScheduler().runTask(this,()->p.spigot().respawn());
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void respawn(PlayerRespawnEvent e) {
        var p=e.getPlayer(); var f=fallen.get(p.getUniqueId()); if(f==null) return;
        e.setRespawnLocation(f.origin);
        Bukkit.getScheduler().runTask(this,()->{ if(!busy(p)) return; p.setGameMode(GameMode.SPECTATOR); var alive=living(p,f.world); if(alive.isEmpty())wipe(p,f.world);else watch(p,alive.getFirst(),false); });
    }
    void wipe(Player p,World w) {
        if(wipes.stream().anyMatch(x->x.world==w)) return;
        var ids=members(p).stream().filter(t->t.getWorld()==w).map(Player::getUniqueId).toList();
        wipes.add(new Wipe(w,ids,clock+20L*wipeSeconds));
        for(var id:ids) { var t=player(id); if(t==null)continue; var f=fallen.get(id); if(f==null)continue; t.setSpectatorTarget(null); t.sendTitle(c("&4La mazmorra los conquisto"),c("&cTodos cayeron"),0,60,10); t.playSound(t.getLocation(),Sound.ENTITY_WITHER_DEATH,1,0.5f); }
    }
    public void watch(Player p,Player target,boolean free) {
        var f=fallen.get(p.getUniqueId()); if(f==null||target==null||!living(p,f.world).contains(target)) return;
        p.setSpectatorTarget(null); p.teleport(target.getLocation()); f.target=target.getUniqueId(); f.free=free;
        if(!free)p.setSpectatorTarget(target);
    }
    void spectateMenu(Player p) {
        var f=fallen.get(p.getUniqueId()); if(f==null) {menu(p,false,0);return;}
        var v=view(p,"party.lista.mirar_companeros","&8Elegi a quien mirar"); int slot=0;
        for(var t:living(p,f.world)) { if(slot>=36)break; button(v,slot++,head(t,"&d"+t.getName(),"&eClic: entrar a su camara"),()->{p.closeInventory();watch(p,t,false);}); }
        button(v,49,item(Material.ENDER_EYE,"&bMirar libre","&7Hasta 16 bloques de un companero vivo"),()->{p.closeInventory();var alive=living(p,f.world); if(!alive.isEmpty())watch(p,alive.getFirst(),true);});
        button(v,53,icon("astral:menu/icon_close",Material.BARRIER,"&cCerrar"),p::closeInventory);p.openInventory(v.inventory);
    }
    @EventHandler public void sneak(PlayerToggleSneakEvent e) { if(busy(e.getPlayer())&&e.isSneaking()) Bukkit.getScheduler().runTask(this,()->spectateMenu(e.getPlayer())); }
    @EventHandler public void interact(PlayerInteractEvent e) { if(busy(e.getPlayer())) {e.setCancelled(true); spectateMenu(e.getPlayer());} }
    @EventHandler public void entityInteract(PlayerInteractEntityEvent e) { if(busy(e.getPlayer()))e.setCancelled(true); }
    @EventHandler public void open(InventoryOpenEvent e) { if(e.getPlayer() instanceof Player p&&busy(p)&&!(e.getInventory().getHolder() instanceof View))e.setCancelled(true); }
    @EventHandler public void teleport(PlayerTeleportEvent e) {
        var f=fallen.get(e.getPlayer().getUniqueId()); if(f==null||e.getTo()==null)return;
        if(e.getTo().getWorld()!=f.world) {e.setCancelled(true);return;}
        var alive=living(e.getPlayer(),f.world);
        if(!alive.isEmpty()&&alive.stream().noneMatch(t->t.getLocation().distanceSquared(e.getTo())<=256)) e.setCancelled(true);
    }
    void revive(Player p,Location at) {
        var f=fallen.remove(p.getUniqueId()); if(f==null)return;
        p.closeInventory();p.setSpectatorTarget(null);p.teleport(at);p.setGameMode(f.mode);
        p.setHealth(p.getAttribute(Attribute.MAX_HEALTH).getValue());p.setFireTicks(0);p.setFallDistance(0);p.setNoDamageTicks(40);
        immunity.put(p.getUniqueId(),clock+40);
        p.getPersistentDataContainer().remove(recovery);p.removeScoreboardTag("astral.party.fallen");p.sendTitle(c("&aReviviste"),"",0,30,10);
    }
    void exit(Player p) {
        var f=fallen.remove(p.getUniqueId()); if(f==null)return;
        p.closeInventory(); if(p.getGameMode()==GameMode.SPECTATOR)p.setSpectatorTarget(null); p.setGameMode(f.mode);
        var lobby=Bukkit.getWorld("lobby"); p.teleport((lobby==null?Bukkit.getWorlds().getFirst():lobby).getSpawnLocation());
        p.setHealth(p.getAttribute(Attribute.MAX_HEALTH).getValue());p.getPersistentDataContainer().remove(recovery);p.removeScoreboardTag("astral.party.fallen");
    }
    public void recover(Player p) {
        String mode=p.getPersistentDataContainer().get(recovery,PersistentDataType.STRING); if(mode==null)return;
        if(p.getGameMode()==GameMode.SPECTATOR)p.setSpectatorTarget(null);
        try {p.setGameMode(GameMode.valueOf(mode));}catch(Exception e){p.setGameMode(GameMode.SURVIVAL);}
        var lobby=Bukkit.getWorld("lobby");p.teleport((lobby==null?Bukkit.getWorlds().getFirst():lobby).getSpawnLocation());p.getPersistentDataContainer().remove(recovery);p.removeScoreboardTag("astral.party.fallen");
    }
    /** Muerte o caida dentro de una mazmorra: suma al puntaje de la copia (mazmorras_puntaje.py). */
    void countDeath(Player p) { if(inDungeon(p)) console("mazpuntaje muerte "+p.getName()); }
    // Desconexion en plena mazmorra (23/11): al volver va al lobby y puede volver a ayudar SIN cofre.
    record Rejoin(String world, UUID leader, long until) {}
    final Map<UUID,Rejoin> rejoins = new HashMap<>();
    static final String NO_CHEST="astral.sincofre";
    @EventHandler public void join(PlayerJoinEvent e) {
        var p=e.getPlayer();
        Bukkit.getScheduler().runTaskLater(this,()->{
            recover(p);
            if(!p.isOnline()) return;
            var r=rejoins.get(p.getUniqueId());
            if(!inDungeon(p)&&(r==null||clock>r.until)) return;
            if(inDungeon(p)) {
                // Tras un reinicio no hay registro: se arma con el mundo donde aparecio.
                if(r==null) rejoins.put(p.getUniqueId(),new Rejoin(p.getWorld().getName(),null,clock+20L*60*15));
                if(p.getGameMode()==GameMode.SPECTATOR)p.setGameMode(GameMode.SURVIVAL);
                var lobby=Bukkit.getWorld("lobby"); p.teleport((lobby==null?Bukkit.getWorlds().getFirst():lobby).getSpawnLocation());
            }
            p.sendTitle(c("&eTe sacamos de la mazmorra"),c("&7Te desconectaste en plena partida"),5,70,15);
            p.sendMessage(c("&8&m                                                  "));
            p.sendMessage(c("&e&l⚠ &eAl salirte del juego te sacamos de la mazmorra."));
            p.sendMessage(Component.text("   ").append(link("[▶ Volver a ayudar a mi party]",NamedTextColor.GREEN,"/party volver","Volves con tus companeros. Esta vez NO recibis cofre."))
                .append(Component.text("  (sin cofre)",NamedTextColor.GRAY)));
            p.sendMessage(c("&8&m                                                  "));
        },3);
    }
    @EventHandler public void quit(PlayerQuitEvent e) {
        var p=e.getPlayer();
        if(inDungeon(p)) rejoins.put(p.getUniqueId(),new Rejoin(p.getWorld().getName(),leaders.get(p.getUniqueId()),clock+20L*60*15));
        clearBorder(p);if(busy(p))exit(p);leave(p);invites.remove(p.getUniqueId());immunity.remove(p.getUniqueId());
    }
    /** /party volver: vuelve con un companero vivo de esa copia, marcado sin cofre. */
    void rejoin(Player p) {
        var r=rejoins.get(p.getUniqueId());
        if(r==null||clock>r.until) {rejoins.remove(p.getUniqueId());msg(p,"No tenes una mazmorra a la que volver.");return;}
        if(inDungeon(p)||busy(p)) {msg(p,"Ya estas en una mazmorra.");return;}
        var w=Bukkit.getWorld(r.world);
        var alive=w==null?List.<Player>of():w.getPlayers().stream().filter(t->!busy(t)&&t.getGameMode()!=GameMode.SPECTATOR&&!t.getUniqueId().equals(p.getUniqueId())).toList();
        if(alive.isEmpty()) {rejoins.remove(p.getUniqueId());msg(p,"Tu party ya no esta en esa mazmorra (termino o salieron todos).");return;}
        if(!inParty(p)&&r.leader!=null) {
            // Volver a la misma party si sigue armada (el lider puede haber cambiado: se busca por companero).
            UUID l=groups.containsKey(r.leader)?r.leader:alive.stream().map(t->leaders.get(t.getUniqueId())).filter(Objects::nonNull).findFirst().orElse(null);
            if(l!=null&&groups.get(l).size()<max) { leaders.put(p.getUniqueId(),l); groups.get(l).add(p.getUniqueId()); sync(); for(var m:members(p))notice(m,p.getName()+" volvio a ayudar (sin cofre)."); }
        }
        var target=alive.stream().filter(t->inParty(p)&&Objects.equals(leaders.get(t.getUniqueId()),leaders.get(p.getUniqueId()))).findFirst().orElse(alive.getFirst());
        rejoins.remove(p.getUniqueId());
        p.addScoreboardTag(NO_CHEST);
        p.teleport(target.getLocation());
        p.sendTitle(c("&aVolviste a ayudar"),c("&7Esta vez no recibis cofre"),5,50,10);
    }
    // La marca "sin cofre" dura hasta salir de las mazmorras; una party nueva en esa copia borra los regresos pendientes.
    @EventHandler public void noChestWorld(PlayerChangedWorldEvent e) { if(!inDungeon(e.getPlayer()))e.getPlayer().removeScoreboardTag(NO_CHEST); }
    void freshCopy(String world) { rejoins.values().removeIf(r->r.world.equals(world)); }
    public void victory(World w) {
        if(w==null||wipes.stream().anyMatch(x->x.world==w))return;
        for(var id:new ArrayList<>(fallen.keySet())) { var p=player(id);var f=fallen.get(id);if(p==null||f.world!=w)continue;var alive=living(p,w); if(!alive.isEmpty()) {revive(p,alive.getFirst().getLocation());msg(p,"Tu party gano: reviviste y podes reclamar tu recompensa normal.");} }
    }
    public void tick() {
        clock++;
        if(clock%5==0)refreshFightRooms();
        // Primero vivos para que los espectadores puedan heredar el borde en este tick.
        for(var p:Bukkit.getOnlinePlayers())if(!busy(p))updateBorder(p);
        for(var p:Bukkit.getOnlinePlayers())if(busy(p))updateBorder(p);
        for(var w:new ArrayList<>(wipes)) if(clock>=w.until) {for(var id:w.members){var p=player(id);if(p!=null&&busy(p))exit(p);}wipes.remove(w);}
        for(var id:new ArrayList<>(fallen.keySet())) {
            var p=player(id);var f=fallen.get(id);if(p==null||p.isDead())continue;
            // El respawn real y su callback pueden caer entre dos ticks del temporizador.
            if(p.getGameMode()!=GameMode.SPECTATOR)p.setGameMode(GameMode.SPECTATOR);
            if(wipes.stream().anyMatch(w->w.world==f.world)) { if(p.getWorld()!=f.world||p.getLocation().distanceSquared(f.origin)>256)p.teleport(f.origin);continue; }
            var alive=living(p,f.world);if(alive.isEmpty()){wipe(p,f.world);continue;}
            var target=player(f.target);if(target==null||!alive.contains(target)) {target=alive.getFirst();watch(p,target,f.free);}
            if(clock>=f.until){revive(p,target.getLocation());continue;}
            if(p.getWorld()!=f.world||alive.stream().noneMatch(t->t.getLocation().distanceSquared(p.getLocation())<=256))watch(p,target,f.free);
            if(!f.free&&p.getSpectatorTarget()!=target)watch(p,target,false);
            if(clock%20==0){long seconds=(f.until-clock+19)/20;p.sendTitle(c("&dRevivis en "+seconds),c("&7Shift: elegir camara"),0,25,0);p.sendActionBar(Component.text("Mirando a "+target.getName()+" · Revivis en "+seconds+" s · Shift: camaras"));}
        }
        if(clock%20==0) {
            for(var entry:new ArrayList<>(invites.entrySet()))if(clock>=entry.getValue().until){
                invites.remove(entry.getKey());var t=player(entry.getKey());
                notice(t,"La invitacion vencio.");notice(player(entry.getValue().leader),"Vencio tu invitacion"+(t==null?".":" a "+t.getName()+"."));
            }
            immunity.values().removeIf(until->clock>=until);
        }
    }
    String status(Player p,boolean compact) {
        var f=fallen.get(p.getUniqueId());if(f!=null)return "&c☠ "+Math.max(0,(f.until-clock+19)/20)+"s";
        double hp=p.getHealth(),maximum=p.getAttribute(Attribute.MAX_HEALTH).getValue();
        return (hp/maximum<=0.3?"&c":"&a")+"❤ "+(compact?Math.round(100*hp/maximum)+"%":Math.round(hp)+"/"+Math.round(maximum));
    }
    String entry(Player p,boolean compact) { String n=p.getName();if(compact&&n.length()>5)n=n.substring(0,5);return (leader(p)?"&6♛ ":"&d")+n+" "+status(p,compact); }
    public String placeholder(Player p,String key) {
        if(p==null)return "";
        var list=members(p);boolean party=inParty(p);
        if(key.equals("en"))return party?"si":"no";
        if(key.equals("cantidad"))return party?""+list.size():"0";
        if(key.equals("lider")){var l=player(leaders.get(p.getUniqueId()));return l==null?"":l.getName();}
        if(key.equals("miembros")){var s=list.stream().map(Player::getName).collect(Collectors.joining(", "));return party?(s.length()>60?s.substring(0,57)+"...":s):"";}
        if(key.equals("linea"))return c(party?"&dParty ("+list.size()+"): &f"+placeholder(p,"miembros"):"&7Sin party · /party");
        if(key.equals("titulo"))return c(party?"&d✦ Party · &6"+placeholder(p,"lider"):"&7Sin party · /party");
        boolean compact=key.startsWith("fila");String prefix=compact?"fila":"tab";
        if(key.startsWith(prefix))try {int row=Integer.parseInt(key.substring(prefix.length()))-1;if(!party||row<0||row>2)return "";return c(list.stream().skip(row*2L).limit(2).map(t->entry(t,compact)).collect(Collectors.joining(" &8· ")));}catch(NumberFormatException e){return "";}
        return "";
    }
    final class Expansion extends PlaceholderExpansion {
        public String getIdentifier(){return "astral";}
        public String getAuthor(){return "AstralRPG";}
        public String getVersion(){return "1.0.0";}
        public boolean persist(){return true;}
        public String onPlaceholderRequest(Player p,String params){return params.startsWith("party_")?placeholder(p,params.substring(6)):null;}
    }
}
