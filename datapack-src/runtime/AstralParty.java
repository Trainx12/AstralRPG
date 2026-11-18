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

/** Party en memoria. Una caida letal se convierte en espera sin producir drops ni perder inventario. */
public final class AstralParty extends JavaPlugin implements Listener {
    final Map<UUID, UUID> leaders = new LinkedHashMap<>();
    public final Map<UUID, LinkedHashSet<UUID>> groups = new LinkedHashMap<>();
    record Invite(UUID leader, long until) {}
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
    Set<String> worlds;
    int waves, boss, wipeSeconds, max; public long clock;
    public NamespacedKey recovery; Expansion expansion;
    static String c(String s) { return ChatColor.translateAlternateColorCodes('&',s); }
    void msg(Player p,String s) { p.sendMessage(c("&d[Party] &f"+s)); }
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
        } catch(Exception e) { throw new IllegalStateException("Configuracion Party invalida",e); }
        recovery=new NamespacedKey(this,"recuperar");
        getServer().getPluginManager().registerEvents(this,this);
        expansion=new Expansion(); expansion.register();
        Bukkit.getScheduler().runTaskTimer(this,()->tick(),1,1);
        Bukkit.getScheduler().runTaskLater(this,()->{ sync(); for(var p:Bukkit.getOnlinePlayers()) recover(p); },40);
    }
    @Override public void onDisable() {
        for(var id:new ArrayList<>(fallen.keySet())) { var p=player(id); if(p!=null) exit(p); }
        if(expansion!=null) expansion.unregister();
    }
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
            return true;
        }
        if(!(sender instanceof Player p)) return true;
        String sub=a.length==0?"menu":a[0].toLowerCase(Locale.ROOT);
        if(sub.equals("menu")) { menu(p,false,0); return true; }
        if(sub.equals("mirar")) { spectateMenu(p); return true; }
        if(sub.equals("crear")) { if(!inParty(p)) { create(p); sync(); } menu(p,true,0); return true; }
        if(sub.equals("invitar")) {
            var t=a.length>1?Bukkit.getPlayerExact(a[1]):null;
            if(t==null || t==p) { msg(p,"Elegi otro jugador conectado: /party invitar <jugador>"); return true; }
            if(inParty(t)) { msg(p,"Ese jugador ya esta en una party."); return true; }
            if(!inParty(p)) create(p);
            if(!leader(p)) msg(p,"Solo el lider puede invitar.");
            else if(members(p).size()>=max) msg(p,"La party esta llena (maximo "+max+").");
            else { invites.put(t.getUniqueId(),new Invite(p.getUniqueId(),clock+1200)); msg(p,"Invitaste a "+t.getName()+" (60 segundos)."); msg(t,p.getName()+" te invito. /party para aceptar o rechazar."); }
            sync(); return true;
        }
        if(sub.equals("aceptar")) {
            var i=invites.remove(p.getUniqueId());
            if(i==null || clock>=i.until || !groups.containsKey(i.leader)) msg(p,"La invitacion vencio o la party ya no existe.");
            else if(inParty(p)) msg(p,"Sali de tu party antes de aceptar otra.");
            else if(groups.get(i.leader).size()>=max) msg(p,"La party se lleno.");
            else { leaders.put(p.getUniqueId(),i.leader); groups.get(i.leader).add(p.getUniqueId()); tell(p,p.getName()+" se unio a la party."); sync(); }
            menu(p,false,0); return true;
        }
        if(sub.equals("rechazar")) { invites.remove(p.getUniqueId()); msg(p,"Invitacion rechazada."); return true; }
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
        msg(p,"/party invitar <jugador>, aceptar, rechazar, salir, echar <jugador>, disolver, mirar"); return true;
    }
    public static final class View implements InventoryHolder {
        Inventory inventory; final Map<Integer,Runnable> actions=new HashMap<>();
        public Inventory getInventory(){return inventory;}
    }
    View view(Player p,String title) {
        var v=new View(); v.inventory=Bukkit.createInventory(v,54,c(title));
        var filler=item(Material.GRAY_STAINED_GLASS_PANE," ");
        for(int i=0;i<54;i++) v.inventory.setItem(i,filler);
        return v;
    }
    ItemStack item(Material m,String title,String... lore) {
        var i=new ItemStack(m); var meta=i.getItemMeta(); meta.setDisplayName(c(title));
        meta.setLore(Arrays.stream(lore).map(AstralParty::c).toList()); i.setItemMeta(meta); return i;
    }
    ItemStack head(Player p,String title,String... lore) {
        var i=item(Material.PLAYER_HEAD,title,lore); var meta=(SkullMeta)i.getItemMeta(); meta.setOwningPlayer(p); i.setItemMeta(meta); return i;
    }
    void button(View v,int slot,ItemStack item,Runnable action) { v.inventory.setItem(slot,item); v.actions.put(slot,action); }
    void menu(Player p,boolean inviting,int page) {
        if(busy(p)) { spectateMenu(p); return; }
        var v=view(p,"&8✦ Party Astral");
        if(inviting) {
            var choices=Bukkit.getOnlinePlayers().stream().filter(t->t!=p&&!inParty(t))
                .sorted(Comparator.comparing((Player t)->t.getWorld()!=p.getWorld()).thenComparing(Player::getName)).toList();
            int pages=Math.max(1,(choices.size()+27)/28), current=Math.max(0,Math.min(page,pages-1));
            for(int i=current*28;i<Math.min(choices.size(),(current+1)*28);i++) {
                var t=choices.get(i); int n=i%28,slot=10+(n/7)*9+n%7;
                button(v,slot,head(t,"&d"+t.getName(),"&7"+t.getWorld().getName(),"&eClic para invitar"),()->{p.performCommand("party invitar "+t.getName());menu(p,true,current);});
            }
            button(v,45,item(Material.ARROW,"&fAnterior"),()->menu(p,true,current-1));
            button(v,53,item(Material.ARROW,"&fSiguiente"),()->menu(p,true,current+1));
        } else {
            int slot=10;
            if(inParty(p)) for(var t:members(p)) {
                button(v,slot++,head(t,(leader(t)?"&6♛ ":"&d")+t.getName(),"&f"+status(t,false),"&7"+t.getWorld().getName(),leader(p)&&t!=p?"&eClic para echar":"&7Companero de party"),()->{if(leader(p)&&t!=p) p.performCommand("party echar "+t.getName());menu(p,false,0);});
            }
            if(!inParty(p)||leader(p)) button(v,30,item(Material.EMERALD,"&dCrear / Invitar","&7Jugadores conectados, mismo mundo primero"),()->{if(!inParty(p)){create(p);sync();}menu(p,true,0);});
            if(inParty(p)) button(v,32,item(Material.RED_BED,leader(p)?"&cDisolver":"&cSalir"),()->{leave(p);menu(p,false,0);});
            var invite=invites.get(p.getUniqueId());
            if(invite!=null && clock<invite.until && groups.containsKey(invite.leader)) {
                var l=player(invite.leader);
                button(v,39,item(Material.LIME_WOOL,"&aAceptar invitacion",l==null?"":l.getName()),()->p.performCommand("party aceptar"));
                button(v,41,item(Material.RED_WOOL,"&cRechazar"),()->{p.performCommand("party rechazar");menu(p,false,0);});
            }
        }
        button(v,49,item(Material.BARRIER,"&cCerrar"),p::closeInventory); p.openInventory(v.inventory);
    }
    @EventHandler public void click(InventoryClickEvent e) {
        if(e.getView().getTopInventory().getHolder() instanceof View v) {
            e.setCancelled(true);
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
        var v=view(p,"&8✦ Elegi a quien mirar"); int slot=10;
        for(var t:living(p,f.world)) button(v,slot++,head(t,"&d"+t.getName(),"&eClic: entrar a su camara"),()->{p.closeInventory();watch(p,t,false);});
        button(v,31,item(Material.ENDER_EYE,"&bMirar libre","&7Hasta 16 bloques de un companero vivo"),()->{p.closeInventory();var alive=living(p,f.world); if(!alive.isEmpty())watch(p,alive.getFirst(),true);});
        button(v,49,item(Material.BARRIER,"&cCerrar"),p::closeInventory);p.openInventory(v.inventory);
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
    @EventHandler public void join(PlayerJoinEvent e) { Bukkit.getScheduler().runTaskLater(this,()->recover(e.getPlayer()),2); }
    @EventHandler public void quit(PlayerQuitEvent e) { var p=e.getPlayer();if(busy(p))exit(p);leave(p);invites.remove(p.getUniqueId());immunity.remove(p.getUniqueId()); }
    public void victory(World w) {
        if(w==null||wipes.stream().anyMatch(x->x.world==w))return;
        for(var id:new ArrayList<>(fallen.keySet())) { var p=player(id);var f=fallen.get(id);if(p==null||f.world!=w)continue;var alive=living(p,w); if(!alive.isEmpty()) {revive(p,alive.getFirst().getLocation());msg(p,"Tu party gano: reviviste y podes reclamar tu recompensa normal.");} }
    }
    public void tick() {
        clock++;
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
            if(clock%20==0){long seconds=(f.until-clock+19)/20;p.sendTitle(c("&dRevivis en "+seconds),c("&7Shift o /party mirar: elegir camara"),0,25,0);p.sendActionBar(Component.text("Mirando a "+target.getName()+" · Revivis en "+seconds+" s · Shift: camaras")); for(var t:alive)t.sendActionBar(Component.text(p.getName()+" revive en "+seconds+" s"));}
        }
        if(clock%20==0) {invites.values().removeIf(i->clock>=i.until);immunity.values().removeIf(until->clock>=until);}
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
