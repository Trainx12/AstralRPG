package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import io.lumine.mythic.bukkit.MythicBukkit;

/** Mercader de visita: estado efimero, stock por UUID y defensa solo del agresor. */
final class AstralMerchant implements Listener {
    private final AstralDecor plugin;
    private final Random rng=new Random();
    private LivingEntity merchant;
    private UUID aggressor;
    private int expires, next;
    private final Map<UUID,Map<String,Integer>> bought=new HashMap<>();
    private final Map<String,int[]> offers=new LinkedHashMap<>();
    private final Map<String,String> commands=new HashMap<>(), requiredPlugins=new HashMap<>(), permissions=new HashMap<>();
    private final Map<UUID,ItemDisplay> backs=new HashMap<>();
    AstralMerchant(AstralDecor plugin) {
        this.plugin=plugin;
        try(var in=plugin.getResource("mercader.json")) {
            var obj=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();
            obj.entrySet().forEach(e->{var o=e.getValue().getAsJsonObject();offers.put(e.getKey(),new int[]{o.get("price").getAsInt(),o.get("stock").getAsInt()});});
            obj.entrySet().forEach(e->{var o=e.getValue().getAsJsonObject();
                if(o.has("command")){commands.put(e.getKey(),o.get("command").getAsString());requiredPlugins.put(e.getKey(),o.get("plugin").getAsString());}
                if(o.has("permission"))permissions.put(e.getKey(),o.get("permission").getAsString());});
        } catch(Exception ex) {throw new IllegalStateException(ex);}
        Bukkit.getPluginManager().registerEvents(this,plugin);
        next=Bukkit.getCurrentTick()+interval();
        // Una visita previa no sobrevive reinicios ni carga de chunks.
        for(World w:Bukkit.getWorlds())for(Entity e:w.getEntities())cleanupOld(e);
        Bukkit.getScheduler().runTaskTimer(plugin,this::tick,20,20);
    }
    private int interval(){return (40*60+rng.nextInt(20*60+1))*20;}
    private void cleanupOld(Entity e){
        if(e.getScoreboardTags().contains("astral.mercader")) {
            // Un spawn manual no es una visita; avisar antes de retirar un duplicado.
            for(Player p:e.getWorld().getPlayers())if(p.isOp() && p.getLocation().distanceSquared(e.getLocation())<=32*32)
                p.sendMessage("§eSe retiro un Goblin Mercader sin visita activa. Usa /astralmercader visita [jugador].");
            e.remove();
        } else if(e.getScoreboardTags().contains("astral.espalda"))e.remove();
    }
    @EventHandler public void load(org.bukkit.event.world.ChunkLoadEvent e){for(Entity x:e.getChunk().getEntities())if(x!=merchant && !backs.containsValue(x))cleanupOld(x);}
    private void leave(){if(merchant!=null)merchant.remove();merchant=null;aggressor=null;bought.clear();next=Bukkit.getCurrentTick()+interval();}
    private boolean isMerchant(Entity entity){return merchant!=null && merchant.getUniqueId().equals(entity.getUniqueId());}
    private void tick() {
        int now=Bukkit.getCurrentTick();
        if(merchant!=null && (!merchant.isValid() || now>=expires))leave();
        if(merchant==null && now>=next) {
            List<Player> players=Bukkit.getOnlinePlayers().stream().filter(p->p.getWorld().getName().equals("world") &&
                p.getGameMode()==GameMode.SURVIVAL && !p.isDead()).map(p->(Player)p).toList();
            if(players.isEmpty()){next=now+1200;return;}
            visit(players.get(rng.nextInt(players.size())));
        }
        updateBacks();
    }
    private String visit(Player p) {
        if(merchant!=null && merchant.isValid() && Bukkit.getCurrentTick()<expires)return "§eYa hay un mercader de visita. Usa /astralmercader irse para despedirlo.";
        if(merchant!=null)leave();
        if(!p.getWorld().getName().equals("world") || p.isDead())return "§cEl jugador debe estar vivo en world.";
        int now=Bukkit.getCurrentTick();
        Location loc=null;
        for(int attempt=0;attempt<16;attempt++) {
            Location candidate=p.getLocation().clone().add((rng.nextBoolean()?1:-1)*(6+rng.nextInt(7)),0,(rng.nextBoolean()?1:-1)*(6+rng.nextInt(7)));
            if(!candidate.getWorld().getWorldBorder().isInside(candidate))continue;
            candidate.setY(candidate.getWorld().getHighestBlockYAt(candidate)+1);
            if(candidate.getY()<p.getY()-8 || candidate.getY()>p.getY()+8 ||
                !candidate.clone().subtract(0,1,0).getBlock().getType().isSolid() ||
                !candidate.getBlock().isPassable() || candidate.getBlock().isLiquid() ||
                !candidate.clone().add(0,1,0).getBlock().isPassable() || candidate.clone().add(0,1,0).getBlock().isLiquid())continue;
            Material floor=candidate.clone().subtract(0,1,0).getBlock().getType();
            if(floor==Material.MAGMA_BLOCK || floor==Material.CAMPFIRE || floor==Material.SOUL_CAMPFIRE || floor==Material.CACTUS)continue;
            loc=candidate;break;
        }
        if(loc==null){next=now+1200;return "§cNo se encontro un lugar seguro cerca del jugador. Acercate a terreno abierto.";}
            try {merchant=(LivingEntity)MythicBukkit.inst().getAPIHelper().spawnMythicMob("astral_goblin_vendedor",loc);}
            catch(Exception ex){plugin.getLogger().warning("No se pudo invocar mercader: "+ex);next=now+1200;return "§cNo se pudo invocar el mercader; revisa la consola.";}
            if(merchant==null){next=now+1200;return "§cMythicMobs no pudo crear el mercader.";}
            bought.clear();aggressor=null;
            expires=now+6000;
            for(Player near:loc.getWorld().getPlayers())if(near.getLocation().distanceSquared(loc)<=64*64)
                near.sendMessage("§2Goblin Mercader §aesta cerca de "+p.getName()+". Se va en cinco minutos. Clic derecho para comerciar.");
        return "§aVisita iniciada cerca de "+p.getName()+" por cinco minutos.";
    }
    private boolean visitor(Player p){return plugin.authenticated(p) && merchant!=null && merchant.isValid() && aggressor==null &&
        Bukkit.getCurrentTick()<expires && p.getWorld()==merchant.getWorld() && p.getLocation().distanceSquared(merchant.getLocation())<=64 && !p.isDead();}
    @EventHandler(priority=EventPriority.MONITOR) public void manualInteract(PlayerInteractEntityEvent e) {
        // El aviso tambien debe llegar si Mythic u otra proteccion cancelo el clic.
        if(!isMerchant(e.getRightClicked()) && e.getHand()==EquipmentSlot.HAND && e.getPlayer().isOp() &&
            e.getRightClicked().getScoreboardTags().contains("astral.mercader"))
            e.getPlayer().sendMessage("§eEste Goblin Mercader no esta de visita: usa /astralmercader visita [jugador].");
    }
    @EventHandler(ignoreCancelled=true) public void interact(PlayerInteractEntityEvent e) {
        if(!isMerchant(e.getRightClicked()))return;
        e.setCancelled(true);
        if(e.getHand()==EquipmentSlot.HAND && visitor(e.getPlayer()))
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"dm open goblin_mercader "+e.getPlayer().getName());
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void target(EntityTargetLivingEntityEvent e) {
        if(e.getEntity().getScoreboardTags().contains("astral.mercader") &&
            (aggressor==null || e.getTarget()==null || !aggressor.equals(e.getTarget().getUniqueId())))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void hit(EntityDamageByEntityEvent e) {
        if(!isMerchant(e.getEntity()) || aggressor!=null)return;
        Entity damager=e.getDamager();
        if(damager instanceof Projectile projectile && projectile.getShooter() instanceof Entity shooter)damager=shooter;
        if(damager instanceof Player p) {
            aggressor=p.getUniqueId();expires=Math.min(expires,Bukkit.getCurrentTick()+600);
            if(merchant instanceof Mob mob)mob.setTarget(p);
        }
    }
    @EventHandler(priority=EventPriority.HIGH,ignoreCancelled=true) public void defend(EntityDamageByEntityEvent e) {
        if(isMerchant(e.getDamager()) && (aggressor==null || !e.getEntity().getUniqueId().equals(aggressor)))e.setCancelled(true);
        if(e.getDamager() instanceof Player p && e.getCause()==EntityDamageEvent.DamageCause.ENTITY_ATTACK &&
            id(p.getInventory().getItemInMainHand()).equals("espada_heroe_errante") && p.getHealth()>=p.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue()-.001)
            e.setDamage(e.getDamage()*1.10);
    }
    private String id(ItemStack item) {
        if(item==null || !item.hasItemMeta())return "";
        var m=java.util.regex.Pattern.compile("[{,]\\s*id:\\s*\"([a-z0-9_]+)\"").matcher(item.getItemMeta().getAsComponentString());
        return m.find()?m.group(1):"";
    }
    @SuppressWarnings({"unchecked","rawtypes"})
    boolean command(org.bukkit.command.CommandSender sender,String[] args) {
        while(sender instanceof org.bukkit.command.ProxiedCommandSender proxy)sender=proxy.getCaller();
        if(args.length>0 && (args[0].equalsIgnoreCase("visita") || args[0].equalsIgnoreCase("irse"))) {
            if(!sender.isOp()){sender.sendMessage("§cSolo un administrador OP puede gestionar visitas.");return true;}
            if(args[0].equalsIgnoreCase("irse")) {
                if(args.length!=1){sender.sendMessage("§eUso: /astralmercader irse");return true;}
                if(merchant==null){sender.sendMessage("§eNo hay un mercader de visita.");return true;}
                leave();sender.sendMessage("§aEl Goblin Mercader se retiro.");return true;
            }
            Player target=args.length==1 && sender instanceof Player player?player:args.length==2?Bukkit.getPlayerExact(args[1]):null;
            if(target==null){sender.sendMessage("§eUso: /astralmercader visita [jugador conectado]");return true;}
            sender.sendMessage(visit(target));return true;
        }
        if(!(sender instanceof org.bukkit.command.ConsoleCommandSender) || args.length!=2)return true;
        Player p=Bukkit.getPlayerExact(args[0]);int[] offer=offers.get(args[1]);
        if(p==null || offer==null)return true;
        if(!visitor(p)){p.sendMessage("§cEl mercader ya no esta disponible cerca tuyo.");return true;}
        Map<String,Integer> stock=bought.computeIfAbsent(p.getUniqueId(),k->new HashMap<>());
        if(stock.getOrDefault(args[1],0)>=offer[1]){p.sendMessage("§cAgotaste tu stock de esta visita.");return true;}
        String rewardCommand=commands.get(args[1]), permission=permissions.get(args[1]);
        if(permission!=null && p.hasPermission(permission)){p.sendMessage("§eYa tenes este cosmetico.");return true;}
        if(rewardCommand!=null && !Bukkit.getPluginManager().isPluginEnabled(requiredPlugins.get(args[1]))){p.sendMessage("§cLa tienda no esta disponible.");return true;}
        if(rewardCommand==null && p.getInventory().firstEmpty()<0){p.sendMessage("§cNecesitas un espacio libre.");return true;}
        try {
            Collection<ItemStack> items=List.of();
            if(rewardCommand==null) {
                var loot=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+args[1]));
                if(loot==null)throw new IllegalStateException("Falta loot "+args[1]);
                items=loot.populateLoot(rng,new org.bukkit.loot.LootContext.Builder(p.getLocation()).build());
                if(items.size()!=1)throw new IllegalStateException("Oferta no unitaria");
            }
            var vault=Bukkit.getPluginManager().getPlugin("Vault");if(vault==null)throw new IllegalStateException("Falta Vault");
            Class economy=Class.forName("net.milkbowl.vault.economy.Economy",true,vault.getClass().getClassLoader());
            var reg=Bukkit.getServicesManager().getRegistration(economy);if(reg==null)throw new IllegalStateException("Falta economia");
            Object provider=reg.getProvider();
            Object response=economy.getMethod("withdrawPlayer",OfflinePlayer.class,double.class).invoke(provider,p,(double)offer[0]);
            if(!(boolean)response.getClass().getMethod("transactionSuccess").invoke(response)){p.sendMessage("§cNo tenes dinero suficiente.");return true;}
            boolean delivered=false;
            try {
                if(rewardCommand==null)p.getInventory().addItem(items.iterator().next());
                else if(!Bukkit.dispatchCommand(Bukkit.getConsoleSender(),rewardCommand.replace("%player%",p.getName())))throw new IllegalStateException("Comando de premio rechazado");
                delivered=true;
            } finally {
                if(!delivered)economy.getMethod("depositPlayer",OfflinePlayer.class,double.class).invoke(provider,p,(double)offer[0]);
            }
            stock.merge(args[1],1,Integer::sum);
            p.sendMessage("§aCompra completada. Stock restante: "+(offer[1]-stock.get(args[1])));
        } catch(Exception ex){p.sendMessage("§cLa tienda no esta disponible.");plugin.getLogger().warning(ex.toString());}
        return true;
    }
    private void updateBacks() {
        Set<UUID> active=new HashSet<>();
        for(Player p:Bukkit.getOnlinePlayers()) {
            String key=p.getPersistentDataContainer().get(new NamespacedKey(plugin,"cosmetic_espalda"),PersistentDataType.STRING);
            String model=key==null?null:plugin.getConfig().getString("cosmetics.espalda."+key);
            if(!plugin.authenticated(p) || model==null || !p.hasPermission("astral.cosmetico.espalda."+key) || p.isDead() || p.isInvisible() || p.getGameMode()==GameMode.SPECTATOR)continue;
            active.add(p.getUniqueId());
            Location loc=p.getLocation().clone();loc.setPitch(0);loc.subtract(loc.getDirection().multiply(.32)).add(0,1.1,0);
            ItemDisplay display=backs.get(p.getUniqueId());
            if(display!=null && display.getWorld()!=p.getWorld()){display.remove();display=null;}
            if(display==null || !display.isValid()) {
                display=p.getWorld().spawn(loc,ItemDisplay.class,d->{d.setPersistent(false);d.addScoreboardTag("astral.espalda");d.setTeleportDuration(20);d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);});
                backs.put(p.getUniqueId(),display);
            }
            ItemStack item=new ItemStack(Material.PAPER);var meta=item.getItemMeta();meta.setItemModel(NamespacedKey.fromString("astral:"+model));item.setItemMeta(meta);
            display.setItemStack(item);display.teleport(loc);
        }
        for(UUID id:new HashSet<>(backs.keySet()))if(!active.contains(id))backs.remove(id).remove();
    }
    void close(){leave();backs.values().forEach(Entity::remove);backs.clear();}
}
