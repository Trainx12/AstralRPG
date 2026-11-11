package astral;

import java.util.*;
import java.lang.reflect.Array;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.block.data.type.NoteBlock;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.event.world.ChunkLoadEvent;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.joml.Vector3f;
import org.bukkit.util.Transformation;
import io.papermc.paper.event.player.PrePlayerAttackEntityEvent;

/** Runtime propio de la tanda 4b. Datos persistentes en entidades/chunks. */
public final class AstralDecor extends JavaPlugin implements Listener {
    private static final class PlushShop implements InventoryHolder {
        private Inventory inventory;
        public Inventory getInventory() { return inventory; }
    }
    private static final String SHOP_TITLE = "Astral - Peluches";
    private static final List<String> PLUSH_ORDER = List.of("alex","creaking","ocelot","steve","tropical_fish","zombie_horse");
    private boolean isShop(Inventory inventory) { return inventory.getHolder() instanceof PlushShop; }
    private ItemStack plush(String id, World world) {
        var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/peluche_"+id));
        if(table==null) throw new IllegalStateException("Falta datapack AstralRPG");
        return table.populateLoot(random,new org.bukkit.loot.LootContext.Builder(world.getSpawnLocation()).build()).iterator().next();
    }
    private void shop(Player p) {
        PlushShop holder=new PlushShop(); holder.inventory=Bukkit.createInventory(holder,9,"Peluches - $2.500 c/u");
        for(int i=0;i<PLUSH_ORDER.size();i++) holder.inventory.setItem(i,plush(PLUSH_ORDER.get(i),p.getWorld()));
        p.openInventory(holder.inventory);
    }
    @EventHandler(ignoreCancelled=true) public void openShop(InventoryOpenEvent e) {
        // Titulo reservado en la seccion gratuita de EconomyShopGUI. No se mueve ningun item suyo.
        if(e.getView().getTitle().equals(SHOP_TITLE) && e.getPlayer() instanceof Player p)
            getServer().getScheduler().runTask(this,()->{if(p.isOnline() && p.getOpenInventory().getTopInventory()==e.getInventory()) shop(p);});
    }
    @EventHandler public void shopDrag(InventoryDragEvent e) { if(isShop(e.getInventory())) e.setCancelled(true); }
    @EventHandler public void buy(InventoryClickEvent e) {
        if(!isShop(e.getView().getTopInventory())) return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p) || e.getRawSlot()<0 || e.getRawSlot()>=PLUSH_ORDER.size() || !e.isLeftClick()) return;
        if(p.getInventory().firstEmpty()<0) { p.sendMessage("Deja un espacio libre para el peluche."); return; }
        ItemStack item=plush(PLUSH_ORDER.get(e.getRawSlot()),p.getWorld());
        try {
            var vault=getServer().getPluginManager().getPlugin("Vault");
            if(vault==null) throw new IllegalStateException("Falta Vault");
            Class economy=Class.forName("net.milkbowl.vault.economy.Economy",true,vault.getClass().getClassLoader());
            Object registration=getServer().getServicesManager().getRegistration(economy);
            if(registration==null) throw new IllegalStateException("Falta proveedor de economia");
            Object provider=registration.getClass().getMethod("getProvider").invoke(registration);
            Object result=economy.getMethod("withdrawPlayer",OfflinePlayer.class,double.class).invoke(provider,p,2500d);
            if(!(boolean)result.getClass().getMethod("transactionSuccess").invoke(result)) { p.sendMessage("No tenes $2.500 disponibles."); return; }
            p.getInventory().addItem(item); p.sendMessage("Compraste un peluche por $2.500.");
        } catch(ReflectiveOperationException | IllegalStateException ex) { p.sendMessage("La tienda de peluches no esta disponible."); getLogger().warning(ex.toString()); }
    }
    private NamespacedKey saved, display;
    private final Map<UUID, ItemDisplay> wings = new HashMap<>();
    private final Random random = new Random();
    private static final Set<String> PLUSH = Set.of("alex","creaking","ocelot","steve","tropical_fish","zombie_horse");
    private static final Map<String,Integer> PLANTS = Map.of("swamp",65,"mangrove_swamp",65,"jungle",70,"sparse_jungle",50,"bamboo_jungle",65,"dark_forest",35,"forest",8,"flower_forest",8,"birch_forest",8);
    public void onEnable() {
        saved = new NamespacedKey(this,"item"); display = new NamespacedKey(this,"display");
        getServer().getPluginManager().registerEvents(this,this);
        getServer().getScheduler().runTaskTimer(this,this::wings,1,2);
        getServer().getScheduler().runTaskTimer(this,this::plants,400,400);
        getLogger().info("Tanda 4b: peluches, alas, plantas y mena exterior. WorldGuard obligatorio para construir.");
    }
    public void onDisable() { wings.values().forEach(Entity::remove); wings.clear(); }
    private String id(ItemStack item) {
        if(item == null || !item.hasItemMeta()) return "";
        NamespacedKey key = item.getItemMeta().getItemModel();
        return key != null && key.getNamespace().equals("astral") ? key.getKey() : "";
    }
    // API oficial WorldGuard; reflexion mantiene el jar independiente de sus binarios.
    // Si falta WG o cambia su API, construir/recoger queda bloqueado, sin bypass.
    private boolean build(Player p, Location loc) {
        try {
            Object wgPlugin = getServer().getPluginManager().getPlugin("WorldGuard");
            if(wgPlugin == null) return false;
            ClassLoader loader = wgPlugin.getClass().getClassLoader();
            Class<?> wg = Class.forName("com.sk89q.worldguard.WorldGuard",true,loader);
            Object instance = wg.getMethod("getInstance").invoke(null);
            Object platform = wg.getMethod("getPlatform").invoke(instance);
            Object container = platform.getClass().getMethod("getRegionContainer").invoke(platform);
            Object query = container.getClass().getMethod("createQuery").invoke(container);
            Class<?> adapter = Class.forName("com.sk89q.worldedit.bukkit.BukkitAdapter",true,loader);
            Object location = adapter.getMethod("adapt",Location.class).invoke(null,loc);
            Object player = wgPlugin.getClass().getMethod("wrapPlayer",Player.class).invoke(wgPlugin,p);
            Class<?> flag = Class.forName("com.sk89q.worldguard.protection.flags.StateFlag",true,loader);
            Object flags = Array.newInstance(flag,0);
            for(var m:query.getClass().getMethods()) if(m.getName().equals("testBuild") && m.getParameterCount()==3 && m.getParameterTypes()[2].isArray())
                return (boolean)m.invoke(query,location,player,flags);
        } catch(ReflectiveOperationException ex) { getLogger().warning("WorldGuard: no se pudo consultar build: " + ex.getClass().getSimpleName()); }
        return false;
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void place(PlayerInteractEvent e) {
        if(e.getAction()!=Action.RIGHT_CLICK_BLOCK || e.getHand()!=EquipmentSlot.HAND || e.useInteractedBlock()==Event.Result.DENY || e.useItemInHand()==Event.Result.DENY) return;
        String id = id(e.getItem());
        if(!id.startsWith("peluche_") || !PLUSH.contains(id.substring(8))) return;
        e.setCancelled(true);
        Player p = e.getPlayer(); Block target = e.getClickedBlock().getRelative(e.getBlockFace());
        if(!target.getType().isAir() || !target.getRelative(BlockFace.UP).getType().isAir() || !target.getRelative(BlockFace.DOWN).getType().isSolid() || !build(p,target.getLocation())) return;
        Location loc = target.getLocation().add(.5,0,.5); loc.setYaw(p.getLocation().getYaw()+180);
        if(!loc.getWorld().getNearbyEntities(loc,.45,.7,.45,x->x instanceof Interaction).isEmpty()) return;
        ItemStack item = e.getItem().clone(); item.setAmount(1);
        ItemDisplay visual = null; Interaction hitbox = null;
        try {
            visual = loc.getWorld().spawn(loc,ItemDisplay.class); visual.setItemStack(item); visual.setInvulnerable(true);
            visual.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
            hitbox = loc.getWorld().spawn(loc,Interaction.class); hitbox.setInteractionWidth(.85f); hitbox.setInteractionHeight(.9f); hitbox.setResponsive(true);
            hitbox.getPersistentDataContainer().set(saved,PersistentDataType.BYTE_ARRAY,item.serializeAsBytes());
            hitbox.getPersistentDataContainer().set(display,PersistentDataType.STRING,visual.getUniqueId().toString());
            // Siempre consumir, incluso creativo: recoger devuelve exactamente esa unidad.
            p.getInventory().getItemInMainHand().subtract(1);
        } catch(RuntimeException ex) {
            if(visual!=null) visual.remove(); if(hitbox!=null) hitbox.remove(); throw ex;
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void collect(PrePlayerAttackEntityEvent e) {
        // Interaction puede llegar cancelada por defecto (willAttack=false).
        // Con ataques normales respetar cancelaciones de otros plugins.
        if(e.willAttack() && e.isCancelled()) return;
        Entity entity = e.getAttacked();
        byte[] bytes = entity.getPersistentDataContainer().get(saved,PersistentDataType.BYTE_ARRAY);
        if(bytes==null) return;
        e.setCancelled(true);
        Player p = e.getPlayer();
        if(entity.getLocation().distanceSquared(p.getLocation())>36 || !build(p,entity.getLocation())) return;
        ItemStack item = ItemStack.deserializeBytes(bytes);
        String uuid = entity.getPersistentDataContainer().get(display,PersistentDataType.STRING);
        // Retirar el derecho a devolver antes de emitir items: dos clics nunca cobran dos veces.
        entity.getPersistentDataContainer().remove(saved);
        entity.remove();
        if(uuid!=null) { Entity visual=Bukkit.getEntity(UUID.fromString(uuid)); if(visual!=null) visual.remove(); }
        for(ItemStack overflow:p.getInventory().addItem(item).values()) p.getWorld().dropItemNaturally(p.getLocation(),overflow);
    }
    private void wings() {
        Set<UUID> active = new HashSet<>();
        for(Player p:Bukkit.getOnlinePlayers()) {
            String id=id(p.getInventory().getChestplate());
            if(!Set.of("carnivora_alas","asura_alas").contains(id) || p.isDead() || p.isInvisible() || p.getGameMode()==GameMode.SPECTATOR) continue;
            active.add(p.getUniqueId());
            Location loc=p.getLocation().add(0,1.1,0); loc.setPitch(0);
            ItemDisplay v=wings.get(p.getUniqueId());
            if(v==null || !v.isValid()) { v=p.getWorld().spawn(loc,ItemDisplay.class); v.setPersistent(false); v.addScoreboardTag("astral.wings"); wings.put(p.getUniqueId(),v); }
            v.setItemStack(p.getInventory().getChestplate()); v.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED); v.teleport(loc);
        }
        wings.entrySet().removeIf(e->{if(active.contains(e.getKey())) return false; e.getValue().remove(); return true;});
    }
    private void plants() {
        Set<String> visited=new HashSet<>();
        for(Player p:Bukkit.getOnlinePlayers()) {
            World world=p.getWorld(); if(!world.getName().equals("world") || p.getGameMode()==GameMode.SPECTATOR) continue;
            int x=p.getLocation().getBlockX()+random.nextInt(65)-32, z=p.getLocation().getBlockZ()+random.nextInt(65)-32;
            if(!world.isChunkLoaded(x>>4,z>>4) || !visited.add((x>>4)+","+(z>>4))) continue;
            Block floor=world.getHighestBlockAt(x,z); Location loc=floor.getLocation().add(.5,1,.5);
            int chance=PLANTS.getOrDefault(floor.getBiome().getKey().getKey(),0);
            if(random.nextInt(100)>=chance || !floor.getType().isSolid() || !floor.getRelative(BlockFace.UP).getType().isAir() || loc.distanceSquared(p.getLocation())<256) continue;
            long chunkCount=Arrays.stream(floor.getChunk().getEntities()).filter(e->e.getScoreboardTags().contains("astral.wildplant")).count();
            long zoneCount=world.getNearbyEntities(loc,48,32,48,e->e.getScoreboardTags().contains("astral.wildplant")).size();
            if(chunkCount>=2 || zoneCount>=6 || !build(p,loc)) continue;
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"mm mobs spawn astral_planta_salvaje 1 world,"+loc.getX()+","+loc.getY()+","+loc.getZ());
        }
    }
    private boolean ore(Block b) { return b.getBlockData() instanceof NoteBlock n && n.getNote().getId()==24 && n.getInstrument()==Instrument.BANJO; }
    @EventHandler public void generate(ChunkLoadEvent e) {
        if(!e.isNewChunk() || e.getWorld().getEnvironment()!=World.Environment.THE_END) return;
        Chunk c=e.getChunk(); int x=c.getX()*16+8,z=c.getZ()*16+8;
        if((long)x*x+(long)z*z<1024L*1024 || random.nextInt(8)!=0) return;
        getServer().getScheduler().runTask(this,()->{
            if(!c.isLoaded()) return;
            int y=30+random.nextInt(46);
            // Feature definida por datapack; no modifica biomas ni archivos de Stellarity.
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute in "+e.getWorld().getKey()+" run place feature astral:asura_ore "+x+" "+y+" "+z);
        });
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void tune(PlayerInteractEvent e) {
        Block b=e.getClickedBlock(); if(b==null) return;
        if(ore(b)) { if(e.getAction()==Action.RIGHT_CLICK_BLOCK || e.getAction()==Action.LEFT_CLICK_BLOCK) e.setUseInteractedBlock(Event.Result.DENY); return; }
        // Reservar nota 24: instrumentos normales conservan notas 0..23.
        if(e.getAction()==Action.RIGHT_CLICK_BLOCK && b.getBlockData() instanceof NoteBlock n && n.getInstrument()==Instrument.BANJO && n.getNote().getId()==23) { n.setNote(new Note(0)); b.setBlockData(n,false); e.setCancelled(true); }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void physics(BlockPhysicsEvent e) {
        Block b=e.getBlock(); if(ore(b)) { e.setCancelled(true); return; }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void play(NotePlayEvent e) { if(ore(e.getBlock())) e.setCancelled(true); }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void breakOre(BlockBreakEvent e) {
        if(!ore(e.getBlock())) return;
        if(!e.getPlayer().getInventory().getItemInMainHand().getType().name().endsWith("_PICKAXE")) e.setDropItems(false);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void piston(BlockPistonExtendEvent e) { if(e.getBlocks().stream().anyMatch(this::ore)) e.setCancelled(true); }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void piston(BlockPistonRetractEvent e) { if(e.getBlocks().stream().anyMatch(this::ore)) e.setCancelled(true); }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void blast(EntityExplodeEvent e) { e.blockList().removeIf(this::ore); }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void blast(BlockExplodeEvent e) { e.blockList().removeIf(this::ore); }
}
