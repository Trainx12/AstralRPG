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
import org.joml.Quaternionf;
import io.lumine.mythic.bukkit.MythicBukkit;
import kr.toxicity.model.api.BetterModel;
import org.bukkit.util.Transformation;
import io.papermc.paper.event.player.PrePlayerAttackEntityEvent;

/** Runtime propio de la tanda 4b. Datos persistentes en entidades/chunks. */
public final class AstralDecor extends JavaPlugin implements Listener {
    private static final class TableRecipe {
        NamespacedKey key;
        final List<ItemStack> ingredients = new ArrayList<>();
        final Map<String,Integer> requirements = new HashMap<>();
        final List<Integer> questTiers = new ArrayList<>();
    }
    private final Map<NamespacedKey,TableRecipe> tableRecipes = new LinkedHashMap<>();
    private final Map<UUID,Long> craftWarnings = new HashMap<>();
    private final List<ItemStack> tableItems = new ArrayList<>();
    private ItemStack recipeItem(String id) {
        var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id));
        if(table==null)throw new IllegalStateException("Falta loot astral:item/"+id);
        return table.populateLoot(random,new org.bukkit.loot.LootContext.Builder(Bukkit.getWorlds().getFirst().getSpawnLocation()).build()).iterator().next();
    }
    private void loadTableRecipes() {
        tableRecipes.keySet().forEach(Bukkit::removeRecipe); tableRecipes.clear();tableItems.clear();
        try(var in=getResource("mesa.json")) {
            var rows=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonArray();
            for(var element:rows) {
                var row=element.getAsJsonObject();if(!row.get("table").getAsBoolean())continue;
                String output=row.get("output").getAsString();
                TableRecipe data=new TableRecipe();data.key=new NamespacedKey("astral","mesa/"+output);
                var result=recipeItem(output);result.setAmount(row.get("count").getAsInt());
                var recipe=new ShapelessRecipe(data.key,result);
                // Un grupo por resultado: compartir grupo ocultaria alternativas tras una sola tarjeta.
                recipe.setGroup("astral_"+output);recipe.setCategory(org.bukkit.inventory.recipe.CraftingBookCategory.MISC);
                for(var ingredient:row.getAsJsonArray("ingredients")) {
                    var a=ingredient.getAsJsonArray();String kind=a.get(0).getAsString(),id=a.get(1).getAsString();
                    ItemStack item;
                    if(kind.equals("c"))item=recipeItem(id);
                    else if(id.equals("water_bottle")) {
                        item=new ItemStack(Material.POTION);var meta=(org.bukkit.inventory.meta.PotionMeta)item.getItemMeta();
                        meta.setBasePotionType(org.bukkit.potion.PotionType.WATER);item.setItemMeta(meta);
                    } else item=new ItemStack(Objects.requireNonNull(Material.matchMaterial(id)));
                    item.setAmount(1);
                    for(int i=0;i<a.get(2).getAsInt();i++) {recipe.addIngredient(new RecipeChoice.ExactChoice(item));data.ingredients.add(item);}
                }
                row.getAsJsonObject("requirements").entrySet().forEach(e->data.requirements.put(e.getKey(),e.getValue().getAsInt()));
                String custom=result.getItemMeta().getAsString();
                for(int tier:List.of(1,5))if(custom.matches("(?s).*\\btier:"+tier+"[,}].*") || output.equals("baston_"+tier))data.questTiers.add(tier);
                rememberTableItem(result.asOne());
                for(var ingredient:data.ingredients)if(astralIngredient(ingredient))rememberTableItem(ingredient);
                if(!Bukkit.addRecipe(recipe))throw new IllegalStateException("Receta duplicada "+data.key);
                tableRecipes.put(data.key,data);
            }
            discoverTableRecipes();
            getLogger().info("Mesa Astral: "+tableRecipes.size()+" recetas exactas registradas");
        } catch(Exception ex) {
            tableRecipes.keySet().forEach(Bukkit::removeRecipe);tableRecipes.clear();tableItems.clear();
            getLogger().log(java.util.logging.Level.SEVERE,"No se pudieron registrar las recetas Astral",ex);
        }
    }
    private void rememberTableItem(ItemStack item) {
        if(tableItems.stream().noneMatch(item::isSimilar))tableItems.add(item);
    }
    private void discoverTableRecipes() {
        for(Player p:Bukkit.getOnlinePlayers()) {
          // Migrar solo lore de items canonicos previos; conservar cantidades y otros componentes.
          for(var item:p.getInventory().getContents())if(astralIngredient(item)) {
            for(var canonical:tableItems) {
                if(item.getType()!=canonical.getType())continue;
                if(item.isSimilar(canonical))break;
                var candidate=item.clone();var meta=candidate.getItemMeta();
                meta.lore(canonical.getItemMeta().lore());candidate.setItemMeta(meta);
                if(candidate.isSimilar(canonical)) {item.setItemMeta(meta);break;}
            }
          }
          for(var recipe:tableRecipes.values()) {
            if(p.hasDiscoveredRecipe(recipe.key))continue;
            boolean found=false;
            for(var item:p.getInventory().getContents()) {
                if(item!=null && recipe.ingredients.stream().anyMatch(ingredient->ingredient.isSimilar(item))) {found=true;break;}
            }
            if(found)p.discoverRecipe(recipe.key);
          }
        }
    }
    @EventHandler public void tableReload(org.bukkit.event.server.ServerLoadEvent e) {
        if(e.getType()==org.bukkit.event.server.ServerLoadEvent.LoadType.RELOAD)loadTableRecipes();
    }
    @EventHandler public void tableQuit(PlayerQuitEvent e) {craftWarnings.remove(e.getPlayer().getUniqueId());}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void protectFuel(FurnaceBurnEvent e) {
        if(astralIngredient(e.getFuel()))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void protectSmelting(FurnaceSmeltEvent e) {
        if(astralIngredient(e.getSource()))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void protectCampfire(BlockCookEvent e) {
        if(astralIngredient(e.getSource()))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void protectBrewing(BrewEvent e) {
        for(var item:e.getContents().getContents())if(astralIngredient(item)) {e.setCancelled(true);return;}
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void protectBrewingFuel(BrewingStandFuelEvent e) {
        if(astralIngredient(e.getFuel()))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void protectSmithing(PrepareSmithingEvent e) {
        for(var item:e.getInventory().getContents())if(astralIngredient(item)) {e.setResult(null);return;}
    }
    private boolean astralIngredient(ItemStack item) {
        // Incluye materiales sin item_model y objetos Astral de versiones anteriores.
        return item!=null && item.hasItemMeta() && item.getItemMeta().getAsString().contains("astral:");
    }
    private TableRecipe tableRecipe(Recipe recipe) {
        return recipe instanceof Keyed keyed?tableRecipes.get(keyed.getKey()):null;
    }
    private boolean tableLevel(Player player,TableRecipe recipe) {
        if(recipe.requirements.isEmpty())return true;
        try {
            var plugin=Bukkit.getPluginManager().getPlugin("AuraSkills");
            if(plugin==null || !plugin.isEnabled())return false;
            var api=Class.forName("dev.aurelium.auraskills.api.AuraSkillsApi",true,plugin.getClass().getClassLoader());
            Object instance=api.getMethod("get").invoke(null);
            Object user=api.getMethod("getUser",UUID.class).invoke(instance,player.getUniqueId());
            var skills=Class.forName("dev.aurelium.auraskills.api.skill.Skills",true,plugin.getClass().getClassLoader());
            var skillType=Class.forName("dev.aurelium.auraskills.api.skill.Skill",true,plugin.getClass().getClassLoader());
            var userType=Class.forName("dev.aurelium.auraskills.api.user.SkillsUser",true,plugin.getClass().getClassLoader());
            for(var req:recipe.requirements.entrySet()) {
                Object skill=skills.getField(req.getKey().split(":")[1].toUpperCase(Locale.ROOT)).get(null);
                if((int)userType.getMethod("getSkillLevel",skillType).invoke(user,skill)<req.getValue())return false;
            }
            return true;
        } catch(ReflectiveOperationException | RuntimeException ex) {return false;}
    }
    private boolean allowedTable(Player p,CraftingInventory inventory,Recipe recipe) {
        TableRecipe data=tableRecipe(recipe);
        if(data!=null) {
            if(tableLevel(p,data))return true;
            long now=System.currentTimeMillis();
            if(now-craftWarnings.getOrDefault(p.getUniqueId(),0L)>2000) {
                craftWarnings.put(p.getUniqueId(),now);
                var names=Map.of("defense","Defensa","fighting","Combate","sorcery","Hechiceria","forging","Forja","mining","Mineria","foraging","Tala","archery","Arqueria");
                String needed=String.join(", ",data.requirements.entrySet().stream().map(e->names.getOrDefault(e.getKey().split(":")[1],e.getKey())+" "+e.getValue()).toList());
                p.sendMessage("Para fabricar necesitas "+needed+" de AuraSkills. Consulta la Guia Astral.");
            }
            return false;
        }
        return Arrays.stream(inventory.getMatrix()).noneMatch(this::astralIngredient);
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void prepareTable(PrepareItemCraftEvent e) {
        if(e.getView().getPlayer() instanceof Player p && !allowedTable(p,e.getInventory(),e.getRecipe()))e.getInventory().setResult(null);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void takeTable(CraftItemEvent e) {
        if(e.getWhoClicked() instanceof Player p && !allowedTable(p,e.getInventory(),e.getRecipe())) {e.setCancelled(true);e.getInventory().setResult(null);}
        // Consumo, sobrantes (cubos), inventario lleno y shift-clic quedan a cargo de Paper.
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void tableQuest(CraftItemEvent e) {
        var data=tableRecipe(e.getRecipe());
        if(data==null || e.getCurrentItem()==null || e.getCurrentItem().getType().isAir() || e.getAction()==InventoryAction.NOTHING)return;
        Player p=(Player)e.getWhoClicked();
        // Registrar solo despues de comprobar que hubo consumo real, sin premios por previsualizar.
        var before=Arrays.stream(e.getInventory().getMatrix()).filter(Objects::nonNull).mapToInt(ItemStack::getAmount).sum();
        getServer().getScheduler().runTask(this,()->{
            int after=Arrays.stream(e.getInventory().getMatrix()).filter(Objects::nonNull).mapToInt(ItemStack::getAmount).sum();
            if(after<before)for(int tier:data.questTiers)Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute as "+p.getName()+" run function astral:quest/event/forge"+tier);
        });
    }
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
    private final Set<UUID> wingWearers = new HashSet<>();
    private final Map<UUID, Float> wingYaw = new HashMap<>();
    private final Random random = new Random();
    private static final Set<String> PLUSH = Set.of("alex","creaking","ocelot","steve","tropical_fish","zombie_horse");
    private static final Map<String,Integer> PLANTS = Map.of("swamp",65,"mangrove_swamp",65,"jungle",70,"sparse_jungle",50,"bamboo_jungle",65,"dark_forest",35,"forest",8,"flower_forest",8,"birch_forest",8);
    private final Set<UUID> skinsApplied = new HashSet<>();
    private void loginSkins() {
        if(!getConfig().getBoolean("skins-after-login",true) || !Bukkit.getPluginManager().isPluginEnabled("SkinsRestorer"))return;
        for(Player p:Bukkit.getOnlinePlayers()) {
            if(!authenticated(p)) { skinsApplied.remove(p.getUniqueId());continue; }
            if(skinsApplied.add(p.getUniqueId()))Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"sr applyskin "+p.getName());
        }
    }
    @EventHandler public void packSkin(PlayerResourcePackStatusEvent e) {
        if(e.getStatus()!=PlayerResourcePackStatusEvent.Status.SUCCESSFULLY_LOADED || !authenticated(e.getPlayer()))return;
        skinsApplied.remove(e.getPlayer().getUniqueId());
    }
    private final Map<UUID,ItemDisplay> hats = new HashMap<>();
    private NamespacedKey selection(String kind) { return new NamespacedKey(this,"cosmetic_"+kind); }
    private boolean authenticated(Player p) {
        var auth=Bukkit.getPluginManager().getPlugin("AuthMe");
        if(auth==null || !auth.isEnabled())return true;
        try {
            var api=Class.forName("fr.xephi.authme.api.v3.AuthMeApi",true,auth.getClass().getClassLoader());
            return (boolean)api.getMethod("isAuthenticated",Player.class).invoke(api.getMethod("getInstance").invoke(null),p);
        } catch(ReflectiveOperationException ex) { return false; }
    }
    private ItemStack selected(Player p,String kind) {
        String key=p.getPersistentDataContainer().get(selection(kind),PersistentDataType.STRING);
        if(key==null || !p.hasPermission("astral.cosmetico."+kind+"."+key))return null;
        String model=getConfig().getString("cosmetics."+kind+"."+key);
        if(model==null)return null;
        ItemStack item=new ItemStack(Material.PAPER);var meta=item.getItemMeta();
        meta.setItemModel(NamespacedKey.fromString("astral:"+model));item.setItemMeta(meta);return item;
    }
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
        if(!(sender instanceof Player p))return true;
        if(!authenticated(p)) { p.sendMessage("Primero inicia sesion.");return true; }
        if(args.length!=2 || !Set.of("sombrero","alas").contains(args[0]))return false;
        String kind=args[0],key=args[1];
        if(key.equals("quitar"))p.getPersistentDataContainer().remove(selection(kind));
        else {
            if(!getConfig().contains("cosmetics."+kind+"."+key) || !p.hasPermission("astral.cosmetico."+kind+"."+key)) {
                p.sendMessage("Todavia no desbloqueaste ese cosmetico.");return true;
            }
            p.getPersistentDataContainer().set(selection(kind),PersistentDataType.STRING,key);
        }
        p.saveData();
        discoverWings(); wings(); hats();
        p.sendMessage(key.equals("quitar")?"Cosmetico quitado. Conservas tu coleccion.":"Cosmetico equipado. Los sombreros se muestran solo sin casco.");
        return true;
    }
    private void removeCosmetics(UUID id) {
        skinsApplied.remove(id);
        wingWearers.remove(id); wingYaw.remove(id);
        var wing=wings.remove(id);if(wing!=null)wing.remove();
        var hat=hats.remove(id);if(hat!=null)hat.remove();
    }
    @EventHandler public void leaveCosmetics(PlayerQuitEvent e) { removeCosmetics(e.getPlayer().getUniqueId()); }
    @EventHandler public void deathCosmetics(PlayerDeathEvent e) { removeCosmetics(e.getEntity().getUniqueId()); }
    @EventHandler(ignoreCancelled=true, priority=EventPriority.MONITOR)
    public void teleportCosmetics(PlayerTeleportEvent e) { removeCosmetics(e.getPlayer().getUniqueId()); }
    @EventHandler public void changedCosmeticWorld(PlayerChangedWorldEvent e) { removeCosmetics(e.getPlayer().getUniqueId()); }
    private void hats() {
        Set<UUID> active=new HashSet<>();
        for(Player p:Bukkit.getOnlinePlayers()) {
            ItemStack item=selected(p,"sombrero");
            if(item==null || !authenticated(p) || p.isDead() || p.isInvisible() || p.getGameMode()==GameMode.SPECTATOR
                || (p.getInventory().getHelmet()!=null && !p.getInventory().getHelmet().getType().isAir()))continue;
            active.add(p.getUniqueId());
            Location loc=p.getEyeLocation().add(0,.15,0);
            ItemDisplay v=hats.get(p.getUniqueId());
            if(v!=null && !v.getWorld().equals(p.getWorld())) {v.remove();v=null;}
            if(v==null || !v.isValid()) {
                v=p.getWorld().spawn(loc,ItemDisplay.class);v.setPersistent(false);v.setInvulnerable(true);
                v.addScoreboardTag("astral.hat");v.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.HEAD);
                v.setTransformation(new Transformation(new Vector3f(),new Quaternionf(),new Vector3f(.625f),new Quaternionf()));
                v.setTeleportDuration(2);hats.put(p.getUniqueId(),v);
                p.hideEntity(this,v); // No tapar la camara propia en primera persona.
            }
            if(!item.equals(v.getItemStack()))v.setItemStack(item);
            v.teleport(loc);
        }
        hats.entrySet().removeIf(e->{if(active.contains(e.getKey()))return false;e.getValue().remove();return true;});
    }
    public void onEnable() {
        saved = new NamespacedKey(this,"item"); display = new NamespacedKey(this,"display");
        saveDefaultConfig();
        // Integrar solo el catalogo nuevo; conservar configuracion NPC del servidor.
        try(var in=getResource("config.yml")) {
            var defaults=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8));
            var catalog=defaults.getConfigurationSection("cosmetics");
            for(String key:catalog.getKeys(true))if(!catalog.isConfigurationSection(key))getConfig().set("cosmetics."+key,catalog.get(key));
            saveConfig();
        } catch(java.io.IOException ex) { throw new IllegalStateException(ex); }
        getServer().getPluginManager().registerEvents(this,this);
        getServer().getScheduler().runTask(this,this::loadTableRecipes);
        getServer().getScheduler().runTaskTimer(this,this::discoverTableRecipes,20,20);
        // Descubrir equipo a 2 Hz; la ruta de 20 Hz solo visita portadores de alas.
        getServer().getScheduler().runTaskTimer(this,this::discoverWings,1,10);
        getServer().getScheduler().runTaskTimer(this,this::wings,2,1);
        getServer().getScheduler().runTaskTimer(this,this::hats,1,2);
        getServer().getScheduler().runTaskTimer(this,this::loginSkins,20,20);
        getServer().getScheduler().runTaskTimer(this,this::plants,400,400);
        getServer().getScheduler().runTaskTimer(this,this::npcs,40,20);
        getServer().getScheduler().runTask(this,()->Bukkit.getWorlds().forEach(w->Arrays.stream(w.getLoadedChunks()).forEach(this::repairPlush)));
        getLogger().info("Tanda 4b: peluches, alas, plantas y mena exterior. WorldGuard obligatorio para construir.");
    }
    public void onDisable() { tableRecipes.keySet().forEach(Bukkit::removeRecipe); tableRecipes.clear(); wings.values().forEach(Entity::remove); wings.clear(); wingWearers.clear(); wingYaw.clear(); hats.values().forEach(Entity::remove);hats.clear(); }
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
            Object sessions = platform.getClass().getMethod("getSessionManager").invoke(platform);
            Object world = adapter.getMethod("adapt",World.class).invoke(null,loc.getWorld());
            for(var m:sessions.getClass().getMethods()) if(m.getName().equals("hasBypass") && m.getParameterCount()==2)
                if((boolean)m.invoke(sessions,player,world)) return true;
            Class<?> flag = Class.forName("com.sk89q.worldguard.protection.flags.StateFlag",true,loader);
            Object flags = Array.newInstance(flag,0);
            for(var m:query.getClass().getMethods()) if(m.getName().equals("testBuild") && m.getParameterCount()==3 && m.getParameterTypes()[2].isArray())
                return (boolean)m.invoke(query,location,player,flags);
        } catch(ReflectiveOperationException ex) { getLogger().warning("WorldGuard: no se pudo consultar build: " + ex.getClass().getSimpleName()); }
        return false;
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void place(PlayerInteractEvent e) {
        if(e.getAction()!=Action.RIGHT_CLICK_BLOCK || e.getHand()!=EquipmentSlot.HAND) return;
        String id = id(e.getItem());
        if(!id.startsWith("peluche_") || !PLUSH.contains(id.substring(8))) return;
        Player p = e.getPlayer();
        if(p.getWorld().getName().equals("lobby")) { e.setCancelled(true); p.sendMessage("Aca no se pueden poner peluches"); return; }
        // No ignorar DENY ajenos: puede ser una proteccion de Bolt u otro plugin.
        if(e.useInteractedBlock()==Event.Result.DENY || e.useItemInHand()==Event.Result.DENY) {
            p.sendMessage("Aca no se pueden poner peluches: otro plugin bloqueo el clic."); return;
        }
        e.setCancelled(true);
        Block support = e.getClickedBlock();
        if(e.getBlockFace()!=BlockFace.UP) support=support.getRelative(e.getBlockFace()).getRelative(BlockFace.DOWN);
        var shape=support.getCollisionShape().getBoundingBoxes();
        if(shape.isEmpty()) { p.sendMessage("El peluche necesita una superficie firme."); return; }
        double top=shape.stream().filter(b->b.getMinX()<=.5 && b.getMaxX()>=.5 && b.getMinZ()<=.5 && b.getMaxZ()>=.5)
            .mapToDouble(b->b.getMaxY()).max().orElse(0);
        if(top<=0) { p.sendMessage("El peluche necesita apoyo en el centro del bloque."); return; }
        Location loc=support.getLocation().add(.5,top,.5);
        loc.setYaw((float)Math.toDegrees(Math.atan2(p.getX()-loc.getX(),loc.getZ()-p.getZ())));
        if(!build(p,support.getLocation()) || !build(p,loc)) { p.sendMessage("Aca no se pueden poner peluches: no tenes permiso para construir."); return; }
        var occupied=new org.bukkit.util.BoundingBox(loc.getX()-.4,loc.getY()+.01,loc.getZ()-.4,loc.getX()+.4,loc.getY()+.9,loc.getZ()+.4);
        for(int y=loc.getBlockY();y<=Math.floor(loc.getY()+.9);y++) {
            Block b=loc.getWorld().getBlockAt(loc.getBlockX(),y,loc.getBlockZ());
            for(var part:b.getCollisionShape().getBoundingBoxes())
                if(part.clone().shift(b.getX(),b.getY(),b.getZ()).overlaps(occupied)) { p.sendMessage("No hay espacio libre para el peluche."); return; }
        }
        if(!loc.getWorld().getNearbyEntities(loc,.8,1,.8,x->x instanceof Interaction).isEmpty()) { p.sendMessage("Ya hay un peluche demasiado cerca."); return; }
        ItemStack item = e.getItem().clone(); item.setAmount(1);
        ItemDisplay visual = null; Interaction hitbox = null;
        try {
            visual = loc.getWorld().spawn(loc,ItemDisplay.class); visual.setItemStack(item); visual.setInvulnerable(true);
            hitbox = loc.getWorld().spawn(loc,Interaction.class); hitbox.setInteractionWidth(.85f); hitbox.setInteractionHeight(.9f); hitbox.setResponsive(true);
            hitbox.getPersistentDataContainer().set(saved,PersistentDataType.BYTE_ARRAY,item.serializeAsBytes());
            hitbox.getPersistentDataContainer().set(display,PersistentDataType.STRING,visual.getUniqueId().toString());
            upright(visual,hitbox,id.substring(8));
            // Siempre consumir, incluso creativo: recoger devuelve exactamente esa unidad.
            p.getInventory().getItemInMainHand().subtract(1);
        } catch(RuntimeException ex) {
            if(visual!=null) visual.remove(); if(hitbox!=null) hitbox.remove(); throw ex;
        }
    }
    // Medidas normalizadas de los seis modelos. NONE evita el fixed=-90 del pack.
    // s, offset XYZ, alto: la dimension mayor mide .8 bloques, base Y=0.
    private static final Map<String,float[]> PLUSH_LAYOUT=Map.of(
        "alex",new float[]{.9423214f,0,.4711607f,.0249853f,.8f},
        "steve",new float[]{.9423214f,0,.4711607f,.0249853f,.8f},
        "creaking",new float[]{.6167065f,-.0054479f,.328266f,.0114544f,.8f},
        "ocelot",new float[]{.9630682f,0,.4825072f,-.0242436f,.7596946f},
        "tropical_fish",new float[]{1.3099642f,-.0409053f,.3888956f,-.5731094f,.8f},
        "zombie_horse",new float[]{.7000782f,0,.3534775f,.0301098f,.5549313f});
    private void upright(ItemDisplay visual,Interaction hitbox,String id) {
        float[] v=PLUSH_LAYOUT.get(id); if(v==null)return;
        visual.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
        // El pez esta acostado en el JSON original: su cara superior pasa al frente.
        Quaternionf rotation=new Quaternionf().rotationX(id.equals("tropical_fish")?-(float)Math.PI/2:0);
        visual.setTransformation(new Transformation(new Vector3f(v[1],v[2],v[3]),rotation,new Vector3f(v[0]),new Quaternionf()));
        hitbox.setInteractionWidth(1.14f); // diagonal .8 x .8, cubre cualquier yaw
        hitbox.setInteractionHeight(v[4]);
        hitbox.addScoreboardTag("astral.plush.upright.v2");
    }
    private void repairPlush(Chunk chunk) {
        for(Entity e:chunk.getEntities()) {
            if(!(e instanceof Interaction h) || h.getScoreboardTags().contains("astral.plush.upright.v2"))continue;
            String uuid=h.getPersistentDataContainer().get(display,PersistentDataType.STRING);
            if(uuid==null || !h.getPersistentDataContainer().has(saved,PersistentDataType.BYTE_ARRAY))continue;
            Entity linked=Bukkit.getEntity(UUID.fromString(uuid));
            if(!(linked instanceof ItemDisplay d))continue;
            String iid=id(d.getItemStack());if(!iid.startsWith("peluche_"))continue;
            Location loc=d.getLocation();loc.setPitch(0);loc.setYaw(loc.getYaw()+180);d.teleport(loc);
            upright(d,h,iid.substring(8));
        }
    }
    @EventHandler public void loadPlush(ChunkLoadEvent e) {
        getServer().getScheduler().runTask(this,()->{if(e.getChunk().isLoaded())repairPlush(e.getChunk());});
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
        if(entity.getLocation().distanceSquared(p.getLocation())>36 || !build(p,entity.getLocation())) { p.sendMessage("Aca no podes recoger peluches."); return; }
        ItemStack item = ItemStack.deserializeBytes(bytes);
        String uuid = entity.getPersistentDataContainer().get(display,PersistentDataType.STRING);
        // Retirar el derecho a devolver antes de emitir items: dos clics nunca cobran dos veces.
        entity.getPersistentDataContainer().remove(saved);
        entity.remove();
        if(uuid!=null) { Entity visual=Bukkit.getEntity(UUID.fromString(uuid)); if(visual!=null) visual.remove(); }
        for(ItemStack overflow:p.getInventory().addItem(item).values()) p.getWorld().dropItemNaturally(p.getLocation(),overflow);
    }
    private ItemStack wingItem(Player p) {
        ItemStack cosmetic=selected(p,"alas");
        if(cosmetic!=null)return cosmetic; // Catalogo extensible, sin lista duplicada de IDs.
        cosmetic=p.getInventory().getItemInOffHand();
        return Set.of("carnivora_alas","asura_alas").contains(id(cosmetic))?cosmetic:null;
    }
    private void discoverWings() {
        for(Player p:Bukkit.getOnlinePlayers())if(wingItem(p)!=null)wingWearers.add(p.getUniqueId());
    }
    private static float approachYaw(float current,float target) {
        float delta=(target-current)%360;
        if(delta>180)delta-=360;
        if(delta< -180)delta+=360;
        return current+Math.max(-12,Math.min(12,delta));
    }
    private void wings() {
        Set<UUID> active = new HashSet<>();
        for(var iterator=wingWearers.iterator();iterator.hasNext();) {
            UUID owner=iterator.next(); Player p=Bukkit.getPlayer(owner);
            if(p==null || !p.isOnline()) { iterator.remove(); continue; }
            // Segunda mano: inventario vanilla se encarga de muerte, tumbas y desconexion.
            ItemStack cosmetic=wingItem(p);
            if(cosmetic==null) { iterator.remove(); continue; }
            if(!authenticated(p) || p.isDead() || p.isInvisible() || p.getGameMode()==GameMode.SPECTATOR
                || p.isSwimming() || p.isGliding() || Set.of(Pose.SWIMMING,Pose.SLEEPING,Pose.SPIN_ATTACK).contains(p.getPose()))continue;
            active.add(p.getUniqueId());
            // Paper 26.1.2 rechaza teleport Bukkit entre mundos si el jugador
            // tiene pasajeros, ANTES de PlayerTeleportEvent. No montar entidades
            // reales: seguir con interpolacion para no romper /spawn/home/portales.
            Location loc=p.getLocation().add(0,p.isSneaking()?1.2:1.45,0); loc.setYaw(0); loc.setPitch(0);
            ItemDisplay v=wings.get(p.getUniqueId());
            if(v!=null && !v.getWorld().equals(p.getWorld())) { v.remove(); v=null; }
            if(v==null || !v.isValid()) {
                v=p.getWorld().spawn(loc,ItemDisplay.class); v.setPersistent(false); v.setInvulnerable(true); v.addScoreboardTag("astral.wings");
                v.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
                v.setInterpolationDuration(2); v.setTeleportDuration(2); wings.put(p.getUniqueId(),v);
                wingYaw.put(owner,p.getBodyYaw());
            }
            if(!cosmetic.equals(v.getItemStack())) v.setItemStack(cosmetic.clone());
            if(v.getLocation().distanceSquared(loc)>.000001)v.teleport(loc);
            // Girar tanto la geometria como el offset local con el cuerpo suavizado.
            float smooth=approachYaw(wingYaw.getOrDefault(owner,p.getBodyYaw()),p.getBodyYaw());
            wingYaw.put(owner,smooth);
            float yaw=(float)Math.toRadians(-smooth);
            Quaternionf rotation=new Quaternionf().rotationY(yaw);
            Vector3f offset=new Vector3f(0,0,-.38f).rotate(rotation);
            Transformation next=new Transformation(offset,rotation,new Vector3f(1),new Quaternionf());
            if(!next.equals(v.getTransformation())) {
                v.setInterpolationDelay(0);
                v.setTransformation(next);
            }
        }
        wings.entrySet().removeIf(e->{if(active.contains(e.getKey())) return false; e.getValue().remove(); wingYaw.remove(e.getKey()); return true;});
    }
    private void npcs() {
        if(!getServer().getPluginManager().isPluginEnabled("MythicMobs") || !getServer().getPluginManager().isPluginEnabled("BetterModel")) return;
        var models=getConfig().getConfigurationSection("npc-models");
        if(models==null) return;
        for(var mob:MythicBukkit.inst().getMobManager().getActiveMobs()) {
            String mid=mob.getType().getInternalName(), model=models.getString(mid);
            if(model==null) continue;
            Entity entity=mob.getEntity().getBukkitEntity();
            if(!entity.isValid() || entity.isDead()) continue;
            if(mid.endsWith("_guia")) {
                Player nearest=entity.getWorld().getPlayers().stream().filter(p->p.getGameMode()!=GameMode.SPECTATOR && p.getLocation().distanceSquared(entity.getLocation())<1024)
                    .min(java.util.Comparator.comparingDouble(p->p.getLocation().distanceSquared(entity.getLocation()))).orElse(null);
                if(nearest!=null) { Location l=entity.getLocation();l.setDirection(nearest.getLocation().subtract(l).toVector());entity.setRotation(l.getYaw(),0); }
            }
            var renderer=BetterModel.modelOrNull(model);
            if(renderer==null) continue; // BetterModel puede seguir armando su catalogo.
            var registry=BetterModel.registryOrNull(entity.getUniqueId());
            if(registry==null || registry.tracker(model)==null) {
                if(registry!=null) registry.close(); // Reemplazar un tracker obsoleto, nunca apilar modelos.
                MythicBukkit.inst().getAPIHelper().castSkill(entity, getConfig().getString("npc-skills."+mid));
            }
            registry=BetterModel.registryOrNull(entity.getUniqueId());
            if(registry==null) continue;
            var tracker=registry.tracker(model);
            if(tracker==null) continue;
            boolean visible=!getConfig().getStringList("hidden-npcs").contains(mid);
            for(var bone:tracker.bones()) if(bone.getNametag()!=null) {
                // BetterModel usa su propio flag, separado de CustomNameVisible de Bukkit.
                bone.getNametag().alwaysVisible(visible);
                if(!visible) bone.getNametag().component(net.kyori.adventure.text.Component.empty());
            }
        }
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
