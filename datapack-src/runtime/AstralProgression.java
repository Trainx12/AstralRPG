package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.block.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.world.*;
import org.bukkit.inventory.*;
import org.bukkit.loot.LootContext;
import org.bukkit.persistence.*;
import org.bukkit.plugin.java.JavaPlugin;
import dev.aurelium.auraskills.api.event.skill.*;
import io.lumine.mythic.bukkit.MythicBukkit;
import me.ryanhamshire.GriefPrevention.GriefPrevention;
import me.ryanhamshire.GriefPrevention.ClaimsMode;

/** XP por muerte y loot adicional, sin comandos accesibles al jugador. */
public final class AstralProgression extends JavaPlugin implements Listener {
    private NamespacedKey skillKey, playerKey, timeKey, placedKey, generatedKey, mythicKey;
    private String survival;
    private final Random random = new Random();
    private final Set<UUID> buying = new HashSet<>();
    private static final Set<String> SKILLS = Set.of("fighting", "archery", "sorcery");
    public void onEnable() {
        saveDefaultConfig();
        survival = getConfig().getString("survival-world", "world");
        skillKey=new NamespacedKey(this,"skill"); playerKey=new NamespacedKey(this,"player");
        timeKey=new NamespacedKey(this,"time"); placedKey=new NamespacedKey(this,"placed");
        generatedKey=new NamespacedKey(this,"generated");
        mythicKey=new NamespacedKey(this,"mythic");
        getServer().getPluginManager().registerEvents(this,this);
        Bukkit.getWorlds().forEach(this::claims);
        getLogger().info("XP por tier, proteccion 2D y loot aditivo activos; survival="+survival);
    }
    private void claims(World w) {
        GriefPrevention.instance.config_claims_worldModes.put(w,
            w.getName().equals(survival) ? ClaimsMode.Survival : ClaimsMode.Disabled);
    }
    @EventHandler(priority=EventPriority.MONITOR) public void world(WorldLoadEvent e) { claims(e.getWorld()); }
    @EventHandler(ignoreCancelled=true) public void structures(AsyncStructureSpawnEvent e) {
        // Evento asincrono: solo datos inmutables, nunca comandos ni escrituras de mundo.
        if(!e.getWorld().getName().equals(survival) &&
            getConfig().getStringList("structure-namespaces").contains(e.getStructure().getKey().getNamespace()))
            e.setCancelled(true);
    }
    public String weaponSkill(ItemStack item) {
        if(item==null || !item.hasItemMeta()) return "";
        var meta=item.getItemMeta();
        var model=meta.getItemModel();
        if(model==null || !model.getNamespace().equals("astral")) return "";
        var req=meta.getPersistentDataContainer().get(NamespacedKey.fromString("auraskills:item_requirements"),PersistentDataType.TAG_CONTAINER);
        if(req==null) return "";
        for(String s:List.of("sorcery","archery","fighting"))
            if(req.has(NamespacedKey.fromString("auraskills:"+s),PersistentDataType.INTEGER)) return s;
        return "";
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void shoot(EntityShootBowEvent e) {
        if(!(e.getEntity() instanceof Player p)) return;
        String skill=weaponSkill(e.getBow());
        // Vanilla archery tambien usa XP por tier del mob, sin tocar fuentes tier 0.
        if(skill.isEmpty()) skill="archery";
        e.getProjectile().getPersistentDataContainer().set(skillKey,PersistentDataType.STRING,skill);
        e.getProjectile().getPersistentDataContainer().set(playerKey,PersistentDataType.STRING,p.getUniqueId().toString());
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void hit(EntityDamageEvent e) {
        if(!(e.getEntity() instanceof LivingEntity mob) || mob instanceof Player || e.getFinalDamage()<=0) return;
        Entity cause=e.getDamageSource().getCausingEntity();
        Entity direct=e.getDamageSource().getDirectEntity();
        if(!(cause instanceof Player p)) return;
        String skill;
        if(direct instanceof Projectile projectile) {
            skill=projectile.getPersistentDataContainer().get(skillKey,PersistentDataType.STRING);
            // Proyectiles sin captura (tridente, plugins) se atribuyen a la skill disponible.
            if(skill==null) skill=weaponSkill(p.getInventory().getItemInMainHand());
            if(skill.isEmpty()) skill="archery";
        } else {
            skill=weaponSkill(p.getInventory().getItemInMainHand());
            if(p.getScoreboardTags().contains("astral.caster")) skill="sorcery";
            if(skill.isEmpty()) skill="fighting";
        }
        var data=mob.getPersistentDataContainer();
        String mm=mythic(mob);
        if(!mm.isEmpty()) data.set(mythicKey,PersistentDataType.STRING,mm);
        data.set(skillKey,PersistentDataType.STRING,skill);
        data.set(playerKey,PersistentDataType.STRING,p.getUniqueId().toString());
        data.set(timeKey,PersistentDataType.LONG,System.currentTimeMillis());
    }
    private String mythic(LivingEntity mob) {
        return MythicBukkit.inst().getMobManager().getActiveMob(mob.getUniqueId())
            .map(m->m.getType().getInternalName()).orElse(mob.getPersistentDataContainer().getOrDefault(mythicKey,PersistentDataType.STRING,""));
    }
    public int tier(LivingEntity mob) {
        if(mob instanceof Player || mob.getType()==EntityType.ARMOR_STAND) return 0;
        for(int t=10;t>=1;t--) if(mob.getScoreboardTags().contains("astral.mt"+t)) return t;
        String mm=mythic(mob);
        if(!mm.isEmpty()) return getConfig().getInt("mythic."+mm+".tier",0);
        if(!(mob instanceof Monster)) return 0;
        return getConfig().getInt("dungeon-tiers."+mob.getWorld().getName(),0);
    }
    public String creditedSkill(LivingEntity mob, Player p) {
        return p==null?"":creditedSkill(mob,p.getUniqueId());
    }
    private String creditedSkill(LivingEntity mob, UUID player) {
        var data=mob.getPersistentDataContainer();
        Long time=data.get(timeKey,PersistentDataType.LONG);
        if(time==null || System.currentTimeMillis()-time>15000 ||
            !player.toString().equals(data.get(playerKey,PersistentDataType.STRING))) return "";
        String skill=data.get(skillKey,PersistentDataType.STRING);
        return SKILLS.contains(skill==null?"":skill) ? skill : "";
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void vanillaXp(XpGainEvent e) {
        if(e instanceof EntityXpGainEvent entity && SKILLS.contains(e.getSkill().getId().getKey()) &&
            tier(entity.getAttacked())>0 && !creditedSkill(entity.getAttacked(),e.getUser().getUuid()).isEmpty())
            e.setCancelled(true);
    }
    public double reward(LivingEntity mob) {
        int tier=tier(mob);
        if(tier==0) return 0;
        String mm=mythic(mob);
        boolean boss=getConfig().getBoolean("mythic."+mm+".boss",false);
        boolean elite=getConfig().getBoolean("mythic."+mm+".elite",false) ||
            mob.getScoreboardTags().stream().anyMatch(t->t.startsWith("astral.elite"));
        return getConfig().getDouble("xp."+tier) * getConfig().getDouble(boss?"boss-bonus":elite?"elite-bonus":"normal-bonus",1);
    }
    @EventHandler(priority=EventPriority.MONITOR) public void death(EntityDeathEvent e) {
        LivingEntity mob=e.getEntity(); Player p=mob.getKiller();
        if(p==null) {
            String uuid=mob.getPersistentDataContainer().get(playerKey,PersistentDataType.STRING);
            if(uuid!=null) p=Bukkit.getPlayer(UUID.fromString(uuid));
        }
        if(p==null || p.getWorld().getName().equals("lobby") || p.getGameMode()!=GameMode.SURVIVAL) return;
        String skill=creditedSkill(mob,p); double xp=reward(mob);
        if(skill.isEmpty() || xp<=0) return;
        // Command XP no genera EntityXpGainEvent: el filtro anterior no cancela nuestro premio.
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"skills xp add "+p.getName()+" "+skill+" "+String.format(Locale.ROOT,"%.2f",xp));
    }
    private PersistentDataContainer container(InventoryHolder h) {
        return h instanceof PersistentDataHolder p ? p.getPersistentDataContainer() : null;
    }
    private void update(InventoryHolder h) { if(h instanceof TileState tile) tile.update(); }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void placed(BlockPlaceEvent e) {
        if(e.getBlockPlaced().getState() instanceof TileState tile) {
            tile.getPersistentDataContainer().set(placedKey,PersistentDataType.BYTE,(byte)1); tile.update();
        }
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void placedEntity(EntityPlaceEvent e) {
        if(e.getEntity() instanceof org.bukkit.entity.minecart.StorageMinecart cart)
            cart.getPersistentDataContainer().set(placedKey,PersistentDataType.BYTE,(byte)1);
    }
    public int lootTier(String key) {
        for(String s:List.of("stronghold","bastion","ancient_city","end_city","catacomb","toxic_lair","illager_mansion","wizard","keep","structory_towers:"))
            if(key.contains(s)) return 5;
        if(key.startsWith("structory:")) return 2;
        for(String s:List.of("village","shipwreck","tavern","cabin","ruin","camp","supply_cache")) if(key.contains(s)) return 2;
        return 3;
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void loot(LootGenerateEvent e) {
        String key=e.getLootTable().getKey().toString();
        if(!e.getWorld().getName().equals(survival) || key.startsWith("astral:") || e.isPlugin()) return;
        InventoryHolder holder=e.getInventoryHolder();
        // Entidades: solo vagonetas de cofre naturales. Bloques: cofres/barriles con loot table.
        if(!(holder instanceof Chest || holder instanceof Barrel || holder instanceof org.bukkit.entity.minecart.StorageMinecart)) return;
        var data=container(holder);
        if(data==null || data.has(placedKey) || data.has(generatedKey)) return;
        int max=lootTier(key);
        List<ItemStack> additions=new ArrayList<>();
        var catalog=getConfig().getConfigurationSection("loot");
        for(String id:catalog.getKeys(false)) {
            if(catalog.getInt(id+".tier")>max || random.nextDouble()>=catalog.getDouble(id+".chance")) continue;
            var table=Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id));
            if(table==null) { getLogger().warning("Falta item loot "+id); continue; }
            additions.addAll(table.populateLoot(random,new LootContext.Builder(e.getLootContext().getLocation()).build()));
        }
        data.set(generatedKey,PersistentDataType.BYTE,(byte)1); update(holder);
        Location location=e.getLootContext().getLocation().clone();
        // Agregar despues de llenar vanilla conserva hasta cofres llenos; excedentes caen al lado.
        getServer().getScheduler().runTask(this,()->{
            Inventory inv=holder.getInventory();
            for(ItemStack item:additions) inv.addItem(item).values().forEach(left->location.getWorld().dropItemNaturally(location,left));
        });
    }
    private static final class Shop implements InventoryHolder {
        Inventory inventory; final boolean claims;
        Shop(boolean claims) { this.claims=claims; }
        public Inventory getInventory() { return inventory; }
    }
    @EventHandler(ignoreCancelled=true) public void open(InventoryOpenEvent e) {
        String title=e.getView().getTitle();
        if(!(e.getPlayer() instanceof Player p) || (!title.equals("Astral - Proteccion") && !title.equals("Astral - Mochilas"))) return;
        boolean claims=title.equals("Astral - Proteccion");
        getServer().getScheduler().runTask(this,()->{
            if(!p.isOnline() || p.getOpenInventory().getTopInventory()!=e.getInventory()) return;
            Shop shop=new Shop(claims);
            shop.inventory=Bukkit.createInventory(shop,9,claims?"Proteccion - comprar area":"Mochilas Astrales");
            var packages=getConfig().getMapList(claims?"claim-packages":"backpack-packages");
            for(int i=0;i<packages.size();i++) {
                var row=packages.get(i);
                ItemStack item=new ItemStack(claims?Material.GOLDEN_SHOVEL:Material.CHEST);
                var meta=item.getItemMeta();
                meta.setDisplayName((claims?row.get("blocks")+" bloques":"Mochila de "+row.get("name")+" ("+row.get("slots")+" espacios)")+" - $"+row.get("price"));
                meta.setLore(List.of(claims?"Suma area; no define un lado del terreno.":"Se entrega como item. Clic derecho para abrirla.","Click izquierdo para comprar."));
                item.setItemMeta(meta); shop.inventory.setItem(i,item);
            }
            p.openInventory(shop.inventory);
        });
    }
    @EventHandler public void drag(InventoryDragEvent e) { if(e.getInventory().getHolder() instanceof Shop) e.setCancelled(true); }
    @SuppressWarnings({"rawtypes","unchecked"})
    @EventHandler public void buy(InventoryClickEvent e) {
        if(!(e.getView().getTopInventory().getHolder() instanceof Shop shop)) return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p) || !e.isLeftClick() || e.getRawSlot()<0) return;
        var packages=getConfig().getMapList(shop.claims?"claim-packages":"backpack-packages");
        if(e.getRawSlot()>=packages.size() || !buying.add(p.getUniqueId())) return;
        try {
            var row=packages.get(e.getRawSlot());
            if(!shop.claims && Bukkit.getPluginManager().getPlugin("ExpendableBackpacks")==null) {
                p.sendMessage("Las mochilas no estan disponibles; avisa al administrador."); return;
            }
            // La mochila es un item: sin lugar libre se perderia. Revisar antes de cobrar.
            if(!shop.claims && p.getInventory().firstEmpty()==-1) {
                p.sendMessage("Libera un espacio del inventario para recibir la mochila."); return;
            }
            var vault=Bukkit.getPluginManager().getPlugin("Vault");
            if(vault==null) throw new IllegalStateException("Falta Vault");
            Class economy=Class.forName("net.milkbowl.vault.economy.Economy",true,vault.getClass().getClassLoader());
            var registration=Bukkit.getServicesManager().getRegistration(economy);
            if(registration==null) throw new IllegalStateException("Falta proveedor de economia");
            Object provider=registration.getProvider();
            double price=((Number)row.get("price")).doubleValue();
            String command=shop.claims?"griefprevention:adjustbonusclaimblocks "+p.getName()+" "+row.get("blocks"):
                "backpack give "+p.getName()+" "+row.get("tier");
            Object result=economy.getMethod("withdrawPlayer",OfflinePlayer.class,double.class).invoke(provider,p,price);
            if(!(boolean)result.getClass().getMethod("transactionSuccess").invoke(result)) { p.sendMessage("No tenes saldo suficiente."); return; }
            if(!Bukkit.dispatchCommand(Bukkit.getConsoleSender(),command)) {
                economy.getMethod("depositPlayer",OfflinePlayer.class,double.class).invoke(provider,p,price);
                p.sendMessage("No se completo la compra; saldo devuelto."); return;
            }
            p.sendMessage(shop.claims?"Bloques sumados a tu saldo de proteccion.":"Mochila comprada. Clic derecho con ella en la mano para abrirla.");
            p.closeInventory();
        } catch(ReflectiveOperationException | IllegalStateException ex) {
            getLogger().warning("Compra no disponible: "+ex); p.sendMessage("La tienda no esta disponible; avisa al administrador.");
        } finally { buying.remove(p.getUniqueId()); }
    }
}
