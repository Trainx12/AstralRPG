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
    // HUD: la vida se dibuja como UNA barra de 10 segmentos (hotbar del pack). Solo cambia el dibujo del cliente:
    // la vida real (y lo que muestra AuraSkills arriba: vida, defensa y mana) sigue igual.
    static void vidaEnBarra(Player p) { p.setHealthScale(20.0); p.setHealthScaled(true); }
    @EventHandler(priority=EventPriority.MONITOR) public void hudVida(PlayerJoinEvent e) { vidaEnBarra(e.getPlayer()); }
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
    private final Set<UUID> hats = new HashSet<>();
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
        if(key==null || !ownsHat(p,key))return null;
        String model=getConfig().getString("cosmetics."+kind+"."+key);
        if(model==null)return null;
        ItemStack item=new ItemStack(Material.PAPER);var meta=item.getItemMeta();
        meta.setItemModel(NamespacedKey.fromString("astral:"+model));item.setItemMeta(meta);return item;
    }
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
        if(!(sender instanceof Player p))return true;
        if(!authenticated(p)) { p.sendMessage("Primero inicia sesion.");return true; }
        if(args.length!=2 || !Set.of("sombrero").contains(args[0]))return false;
        String kind=args[0],key=args[1];
        if(key.equals("quitar"))p.getPersistentDataContainer().remove(selection(kind));
        else {
            if(!getConfig().contains("cosmetics."+kind+"."+key) || !ownsHat(p,key)) {
                p.sendMessage("Todavia no desbloqueaste ese cosmetico.");return true;
            }
            p.getPersistentDataContainer().set(selection(kind),PersistentDataType.STRING,key);
        }
        p.saveData();
        hats();
        p.sendMessage(key.equals("quitar")?"Cosmetico quitado. Conservas tu coleccion.":"Cosmetico equipado. Se ve sobre tu casco; tu casco sigue puesto.");
        return true;
    }
    private void removeCosmetics(UUID id) {
        skinsApplied.remove(id);
        if(hats.remove(id)) {
            Player p=Bukkit.getPlayer(id);
            if(p!=null)showHead(p,p.getInventory().getHelmet());
        }
    }
    @EventHandler public void leaveCosmetics(PlayerQuitEvent e) { removeCosmetics(e.getPlayer().getUniqueId()); }
    @EventHandler public void deathCosmetics(PlayerDeathEvent e) { removeCosmetics(e.getEntity().getUniqueId()); }
    @EventHandler(ignoreCancelled=true, priority=EventPriority.MONITOR)
    public void teleportCosmetics(PlayerTeleportEvent e) { removeCosmetics(e.getPlayer().getUniqueId()); }
    @EventHandler public void changedCosmeticWorld(PlayerChangedWorldEvent e) { removeCosmetics(e.getPlayer().getUniqueId()); }
    private boolean ownsHat(Player p,String key) {
        return p.hasPermission("astral.cosmetico.sombrero."+key)
            || (key.equals("carnivora") && p.hasPermission("astral.cosmetico.alas.carnivora"))
            || (key.equals("diablo") && p.hasPermission("astral.cosmetico.alas.asura"));
    }
    private void showHead(Player p,ItemStack item) {
        ItemStack visual=item==null?new ItemStack(Material.AIR):item;
        // Nunca al propio jugador: el paquete de equipo le pondria el gorro en su casilla de casco
        // (pedido del dueno 13/11: el gorro solo se ve en el personaje y se quita desde /cosmeticos).
        for(Player viewer:p.getWorld().getPlayers())if(viewer!=p && viewer.canSee(p))
            viewer.sendEquipmentChange(p,EquipmentSlot.HEAD,visual);
    }
    // Sombrero sobre el casco (13/11): el casco PUESTO pasa a dibujar el sombrero en la cabeza (definicion
    // astral:cosmeticos/casco_<sombrero> del pack, sombreros_casco.py) y sin la armadura (equippable sin asset).
    // En la casilla, la mano o el suelo sigue viendose el casco (custom_model_data con su modelo original),
    // conserva atributos y Defensa. Se guarda el casco original entero y se devuelve apenas sale de la cabeza.
    private NamespacedKey hatOriginal() { return new NamespacedKey(this,"hat_original"); }
    private NamespacedKey hatWorn() { return new NamespacedKey(this,"hat_worn"); }
    private boolean hatHelmet(ItemStack item) {
        if(wearsHat(item)) return true;
        if(item==null || item.getType().isAir() || !item.hasItemMeta()) return item!=null && item.getType().name().endsWith("_HELMET");
        var model=item.getItemMeta().getItemModel();
        if(model==null) return item.getType().name().endsWith("_HELMET");
        return model.getNamespace().equals("astral") && model.getKey().endsWith("_helmet") && !model.getKey().contains("/");
    }
    private boolean wearsHat(ItemStack item) {
        return item!=null && item.hasItemMeta() && item.getItemMeta().getPersistentDataContainer().has(hatOriginal(),PersistentDataType.BYTE_ARRAY);
    }
    private ItemStack restoreHat(ItemStack item) {
        if(!wearsHat(item)) return item;
        ItemStack original=ItemStack.deserializeBytes(item.getItemMeta().getPersistentDataContainer().get(hatOriginal(),PersistentDataType.BYTE_ARRAY));
        // El desgaste mientras estuvo puesto se conserva.
        if(item.getItemMeta() instanceof org.bukkit.inventory.meta.Damageable worn && original.getItemMeta() instanceof org.bukkit.inventory.meta.Damageable back) {
            back.setDamage(worn.getDamage()); original.setItemMeta(back);
        }
        original.setAmount(item.getAmount());
        return original;
    }
    private ItemStack wearHat(ItemStack helmet,String key) {
        ItemStack original=restoreHat(helmet);
        ItemStack worn=original.clone(); var meta=worn.getItemMeta();
        NamespacedKey model=meta.getItemModel()!=null?meta.getItemModel():original.getType().getKey();
        meta.setItemModel(new NamespacedKey("astral","cosmeticos/casco_"+key));
        var cmd=meta.getCustomModelDataComponent(); cmd.setStrings(List.of(model.toString())); meta.setCustomModelDataComponent(cmd);
        var equip=meta.getEquippable(); equip.setModel(null); meta.setEquippable(equip);
        meta.getPersistentDataContainer().set(hatOriginal(),PersistentDataType.BYTE_ARRAY,original.serializeAsBytes());
        meta.getPersistentDataContainer().set(hatWorn(),PersistentDataType.STRING,key);
        worn.setItemMeta(meta);
        return worn;
    }
    private void restoreHelmet(Player p) {
        ItemStack helmet=p.getInventory().getHelmet();
        if(wearsHat(helmet)) p.getInventory().setHelmet(restoreHat(helmet));
        else if(hatOnly(helmet)) p.getInventory().setHelmet(null);
    }
    // Sin casco (13/11): un objeto propio en la casilla de la cabeza dibuja el sombrero; en el inventario no se
    // ve (definicion astral:cosmeticos/solo_<sombrero>) y nunca sale de la cabeza.
    private NamespacedKey hatOnlyKey() { return new NamespacedKey(this,"hat_only"); }
    private boolean hatOnly(ItemStack item) {
        return item!=null && item.hasItemMeta() && item.getItemMeta().getPersistentDataContainer().has(hatOnlyKey(),PersistentDataType.STRING);
    }
    private ItemStack hatOnlyItem(String key) {
        ItemStack item=new ItemStack(Material.PAPER);var meta=item.getItemMeta();
        meta.setItemModel(new NamespacedKey("astral","cosmeticos/solo_"+key));
        meta.setHideTooltip(true); meta.setMaxStackSize(1);
        meta.getPersistentDataContainer().set(hatOnlyKey(),PersistentDataType.STRING,key);
        item.setItemMeta(meta);return item;
    }
    // Ponerse un casco con clic derecho: primero se libera la cabeza.
    @EventHandler(priority=EventPriority.LOWEST)
    public void hatEquipByHand(org.bukkit.event.player.PlayerInteractEvent e) {
        var item=e.getItem();
        if(item!=null && item.hasItemMeta() && item.getItemMeta().hasEquippable() && item.getItemMeta().getEquippable().getSlot()==EquipmentSlot.HEAD
            && hatOnly(e.getPlayer().getInventory().getHelmet())) e.getPlayer().getInventory().setHelmet(null);
        else if(item!=null && item.getType().name().endsWith("_HELMET") && hatOnly(e.getPlayer().getInventory().getHelmet()))
            e.getPlayer().getInventory().setHelmet(null);
    }
    private void restoreStrays(Player p) {
        var inv=p.getInventory();
        ItemStack[] items=inv.getStorageContents();
        for(int i=0;i<items.length;i++) if(wearsHat(items[i])) inv.setItem(i,restoreHat(items[i]));
        for(int i=0;i<items.length;i++) if(hatOnly(items[i])) inv.setItem(i,null);
        if(wearsHat(inv.getItemInOffHand())) inv.setItemInOffHand(restoreHat(inv.getItemInOffHand()));
        if(hatOnly(inv.getItemInOffHand())) inv.setItemInOffHand(null);
        if(wearsHat(p.getItemOnCursor())) p.setItemOnCursor(restoreHat(p.getItemOnCursor()));
        if(hatOnly(p.getItemOnCursor())) p.setItemOnCursor(null);
    }
    // Antes de cualquier movimiento de inventario, el casco vuelve a ser el original; si sigue en la cabeza,
    // hats() lo vuelve a vestir en el proximo ciclo. Asi nunca sale un casco cambiado de la cabeza.
    @EventHandler(priority=EventPriority.LOWEST)
    public void hatClick(InventoryClickEvent e) {
        if(e.getWhoClicked() instanceof Player p) { restoreHelmet(p); restoreStrays(p); }
        if(wearsHat(e.getCurrentItem())) e.setCurrentItem(restoreHat(e.getCurrentItem()));
        if(hatOnly(e.getCurrentItem())) e.setCurrentItem(null);
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void hatDrag(InventoryDragEvent e) { if(e.getWhoClicked() instanceof Player p) { restoreHelmet(p); restoreStrays(p); } }
    @EventHandler(priority=EventPriority.LOWEST)
    public void hatDrop(PlayerDropItemEvent e) {
        var item=e.getItemDrop().getItemStack();
        if(wearsHat(item)) e.getItemDrop().setItemStack(restoreHat(item));
        if(hatOnly(item)) e.getItemDrop().remove();
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void hatDeath(PlayerDeathEvent e) {
        e.getDrops().replaceAll(this::restoreHat);
        e.getDrops().removeIf(this::hatOnly);
        restoreHelmet(e.getEntity());
    }
    @EventHandler(priority=EventPriority.LOWEST)
    public void hatQuit(PlayerQuitEvent e) { restoreHelmet(e.getPlayer()); restoreStrays(e.getPlayer()); }
    private void hats() {
        Set<UUID> active=new HashSet<>();
        for(Player p:Bukkit.getOnlinePlayers()) {
            p.getPersistentDataContainer().remove(selection("alas"));
            restoreStrays(p);
            ItemStack helmet=p.getInventory().getHelmet();
            ItemStack item=selected(p,"sombrero");
            String key=item==null?null:p.getPersistentDataContainer().get(selection("sombrero"),PersistentDataType.STRING);
            boolean on=item!=null && authenticated(p) && !p.isDead() && !p.isInvisible() && p.getGameMode()!=GameMode.SPECTATOR;
            if(on && hatHelmet(helmet) && helmet!=null && !helmet.getType().isAir()) {
                // Casco real con el sombrero: lo ven todos, tambien el propio jugador en F5.
                String current=wearsHat(helmet)?helmet.getItemMeta().getPersistentDataContainer().get(hatWorn(),PersistentDataType.STRING):null;
                if(!key.equals(current)) p.getInventory().setHelmet(wearHat(helmet,key));
                continue;
            }
            if(wearsHat(helmet)) p.getInventory().setHelmet(restoreHat(helmet));
            boolean empty=helmet==null || helmet.getType().isAir();
            if(hatOnly(helmet)) {
                if(!on) { p.getInventory().setHelmet(null); continue; }
                if(!key.equals(helmet.getItemMeta().getPersistentDataContainer().get(hatOnlyKey(),PersistentDataType.STRING)))
                    p.getInventory().setHelmet(hatOnlyItem(key));
                continue;
            }
            if(!on)continue;
            if(empty) { p.getInventory().setHelmet(hatOnlyItem(key)); continue; }
            // Casco raro (calabaza, cabeza...): el sombrero se muestra a los demas como equipo visual.
            active.add(p.getUniqueId()); showHead(p,item);
        }
        for(UUID id:hats)if(!active.contains(id)) {
            Player p=Bukkit.getPlayer(id);if(p!=null)showHead(p,p.getInventory().getHelmet());
        }
        hats.clear(); hats.addAll(active);
    }
    public void onEnable() {
        saved = new NamespacedKey(this,"item"); display = new NamespacedKey(this,"display");
        for (Player p : Bukkit.getOnlinePlayers()) vidaEnBarra(p);
        saveDefaultConfig();
        // Integrar solo el catalogo nuevo; conservar configuracion NPC del servidor.
        try(var in=getResource("config.yml")) {
            var defaults=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8));
            getConfig().set("cosmetics.alas",null);
            var catalog=defaults.getConfigurationSection("cosmetics");
            for(String key:catalog.getKeys(true))if(!catalog.isConfigurationSection(key))getConfig().set("cosmetics."+key,catalog.get(key));
            saveConfig();
        } catch(java.io.IOException ex) { throw new IllegalStateException(ex); }
        getServer().getPluginManager().registerEvents(this,this);
        getServer().getScheduler().runTask(this,this::loadTableRecipes);
        getServer().getScheduler().runTaskTimer(this,this::discoverTableRecipes,20,20);
        getServer().getScheduler().runTaskTimer(this,this::hats,1,2);
        getServer().getScheduler().runTaskTimer(this,this::loginSkins,20,20);
        getServer().getScheduler().runTaskTimer(this,this::plants,400,400);
        getServer().getScheduler().runTaskTimer(this,this::npcs,40,20);
        getServer().getScheduler().runTaskTimer(this,this::modelNames,45,20);
        getServer().getScheduler().runTaskTimer(this,this::separateMobs,50,4);
        getServer().getScheduler().runTask(this,()->Bukkit.getWorlds().forEach(w->Arrays.stream(w.getLoadedChunks()).forEach(this::repairPlush)));
        getLogger().info("Tanda 4b: peluches, gorros, plantas y mena exterior. WorldGuard obligatorio para construir.");
    }
    public void onDisable() { tableRecipes.keySet().forEach(Bukkit::removeRecipe); tableRecipes.clear();
        for(UUID id:new HashSet<>(hats))removeCosmetics(id);
        for(Player p:Bukkit.getOnlinePlayers()) { restoreHelmet(p); restoreStrays(p); } }
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
    // Armaduras Astral: dan la barra de armadura vanilla completa (3/8/6/3) solo como indicador.
    // La proteccion real es la DEFENSA de escala.py (astral_gameplay.sk), asi que la reduccion
    // vanilla por armadura se anula en los jugadores.
    @SuppressWarnings("deprecation")
    @EventHandler(ignoreCancelled=true, priority=EventPriority.HIGHEST)
    public void armorBarOnly(EntityDamageEvent e) {
        if(!(e.getEntity() instanceof Player p) || !e.isApplicable(EntityDamageEvent.DamageModifier.ARMOR)) return;
        var armor=p.getAttribute(org.bukkit.attribute.Attribute.ARMOR);
        if(armor==null) return;
        double bar=0;
        for(var mod:armor.getModifiers()) if(mod.getKey().getKey().endsWith(".barra")) bar+=mod.getAmount();
        if(bar<=0) return;
        // Misma formula vanilla, pero sin la parte de la barra: otros bonus de armadura siguen protegiendo.
        double a=Math.max(0,armor.getValue()-bar), d=e.getDamage(EntityDamageEvent.DamageModifier.BASE);
        var tough=p.getAttribute(org.bukkit.attribute.Attribute.ARMOR_TOUGHNESS);
        double t=tough==null?0:tough.getValue();
        double reduction=Math.min(20,Math.max(a/5,a-d/(2+t/4)))/25;
        e.setDamage(EntityDamageEvent.DamageModifier.ARMOR,-d*reduction);
    }
    // Mobs con modelo 3D: BetterModel oculta la entidad base y con ella su nombre ("[T3] Zombi ❤ 11.500").
    // El hueso mtag_nombre de cada modelo muestra el mismo texto, actualizado cada segundo.
    private void modelNames() {
        if(!getServer().getPluginManager().isPluginEnabled("BetterModel")) return;
        for(var registry:kr.toxicity.model.api.tracker.EntityTrackerRegistry.registries()) {
            Entity entity=Bukkit.getEntity(registry.uuid());
            if(!(entity instanceof LivingEntity) || entity instanceof Player || entity instanceof Villager) continue;
            var name=entity.customName();
            boolean visible=name!=null && entity.isCustomNameVisible() && !entity.isDead();
            for(var tracker:registry.trackers()) for(var bone:tracker.bones()) if(bone.getNametag()!=null) {
                bone.getNametag().alwaysVisible(visible);
                bone.getNametag().component(visible?name:net.kyori.adventure.text.Component.empty());
            }
        }
    }
    // Los mobs no se pelean entre ellos, solo atacan a jugadores (13/11: en el Santuario el Coloso y el Chaman
    // se golpeaban). Los lobos domesticados de un jugador siguen pudiendo pelear.
    private static boolean wildMob(Entity e) {
        return e instanceof Mob && !(e instanceof Tameable t && t.isTamed());
    }
    @EventHandler(ignoreCancelled=true, priority=EventPriority.HIGH)
    public void noInfighting(EntityDamageByEntityEvent e) {
        Entity attacker=e.getDamager();
        if(attacker instanceof Projectile pr && pr.getShooter() instanceof Entity shooter) attacker=shooter;
        if(wildMob(attacker) && e.getEntity() instanceof LivingEntity && !(e.getEntity() instanceof Player)
            && !(e.getEntity() instanceof ArmorStand)) e.setCancelled(true);
    }
    @EventHandler(ignoreCancelled=true, priority=EventPriority.HIGH)
    public void noInfightingTarget(EntityTargetLivingEntityEvent e) {
        if(wildMob(e.getEntity()) && e.getTarget()!=null && !(e.getTarget() instanceof Player)) e.setCancelled(true);
    }
    // Colision entre mobs: si dos cajas se meten una en otra, se empujan suave hacia afuera (no se solapan).
    private void separateMobs() {
        Set<Entity> seen=new HashSet<>();
        for(Player p:Bukkit.getOnlinePlayers()) {
            if(p.getGameMode()==GameMode.SPECTATOR) continue;
            for(Entity e:p.getNearbyEntities(24,12,24)) {
                if(!(e instanceof Mob m) || !seen.add(e) || !m.hasAI() || e instanceof Villager || e.isInsideVehicle()
                    || !wildMob(e)) continue;
                var box=e.getBoundingBox();
                for(Entity o:e.getWorld().getNearbyEntities(box,x->x!=e && x instanceof Mob om && om.hasAI() && !(x instanceof Villager) && wildMob(x))) {
                    var other=o.getBoundingBox();
                    double dx=box.getCenterX()-other.getCenterX(), dz=box.getCenterZ()-other.getCenterZ();
                    double dist=Math.sqrt(dx*dx+dz*dz);
                    double overlap=(box.getWidthX()+other.getWidthX())/2-dist;
                    if(overlap<=0.05) continue;
                    if(dist<0.01) { double a=random.nextDouble()*Math.PI*2; dx=Math.cos(a); dz=Math.sin(a); dist=1; }
                    double push=Math.min(0.25,0.06+overlap*0.08);
                    var v=e.getVelocity();
                    e.setVelocity(v.setX(v.getX()+dx/dist*push).setZ(v.getZ()+dz/dist*push));
                }
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
