package astral.stellarity;

import java.util.*;
import com.google.gson.*;
import org.bukkit.*;
import org.bukkit.attribute.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.inventory.CraftItemStack;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.nbt.CompoundTag;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.*;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;

/** Paper 26.1.2 / Java 25. Datos generados; los componentes stellarity:* nunca se reemplazan. */
public final class AstralStellarity extends JavaPlugin implements Listener {
    volatile JsonObject rows;
    NamespacedKey original;
    final Map<UUID, UUID> meleeTargets = new HashMap<>();
    final Map<UUID, String> projectiles = new HashMap<>();
    void remember(Entity projectile, String key) {
        projectiles.put(projectile.getUniqueId(),key);
        Bukkit.getScheduler().runTaskLater(this,()->projectiles.remove(projectile.getUniqueId()),1200);
    }
    public String[] priceInfo(ItemMeta meta) {
        var m=java.util.regex.Pattern.compile("[\"']?stellarity:item[\"']?\\s*:\\s*[\"']([a-z0-9_]+)[\"']").matcher(meta.getAsComponentString());
        if(!m.find() || !rows.has(m.group(1))) return null;
        var r=rows.getAsJsonObject(m.group(1));
        return new String[]{"stellarity_"+m.group(1),"stellarity_"+str(r,"kind"),Integer.toString(num(r,"tier"))};
    }
    public long fixedPrice(String id) { return val(rows.getAsJsonObject(id.substring("stellarity_".length())),"price")>0 ? (long)val(rows.getAsJsonObject(id.substring("stellarity_".length())),"price") : 0; }
    public boolean allowed(Player p) { return getConfig().getBoolean("publico", false) || p.getName().equals("ByTrainx"); }
    @Override public void onEnable() {
        original = new NamespacedKey(this, "original");
        saveDefaultConfig();
        if(!new java.io.File(getDataFolder(),"tiers.json").isFile()) saveResource("tiers.json",false);
        loadTable();
        getServer().getPluginManager().registerEvents(this, this);
        // Un tick: cubre loot por funciones y recalculos de Harvester sin recorrer entidades del mundo.
        getServer().getScheduler().runTaskTimer(this, () -> Bukkit.getOnlinePlayers().forEach(this::scan), 1, 1);
    }
    void loadTable() {
        try (var r = java.nio.file.Files.newBufferedReader(new java.io.File(getDataFolder(),"tiers.json").toPath(), java.nio.charset.StandardCharsets.UTF_8)) {
            rows = JsonParser.parseReader(r).getAsJsonObject();
        } catch (Exception e) { throw new IllegalStateException(e); }
    }
    public String id(ItemStack it) {
        if (it == null || it.getType().isAir()) return "";
        var n = CraftItemStack.asNMSCopy(it).get(DataComponents.CUSTOM_DATA);
        return n == null ? "" : n.copyTag().getStringOr("stellarity:item", "");
    }
    JsonObject row(ItemStack it) { return rows.has(id(it)) ? rows.getAsJsonObject(id(it)) : null; }
    static int num(JsonObject r, String k) { return r.has(k) ? r.get(k).getAsInt() : 0; }
    static double val(JsonObject r, String k) { return r.has(k) ? r.get(k).getAsDouble() : 0; }
    static String str(JsonObject r, String k) { return r.has(k) ? r.get(k).getAsString() : ""; }
    static boolean gear(JsonObject r) { return r != null && num(r,"tier") > 0 && !str(r,"kind").equals("horse"); }
    static boolean mine(AttributeModifier m) { return m.getKey().getNamespace().equals("astralstellarity"); }
    void attr(ItemMeta m, Attribute a, double value, String key, EquipmentSlotGroup slot) {
        m.addAttributeModifier(a, new AttributeModifier(new NamespacedKey(this, key), value, AttributeModifier.Operation.ADD_NUMBER, slot));
    }
    void remove(ItemMeta m, Attribute a) { m.removeAttributeModifier(a); }
    public ItemStack convert(Player p, ItemStack it) {
        JsonObject r = row(it);
        if (!gear(r)) return it; // apilables y caballo intactos, tambien su lore y PDC
        var meta = it.getItemMeta();
        byte[] backup = meta.getPersistentDataContainer().get(original, PersistentDataType.BYTE_ARRAY);
        if (!allowed(p)) {
            if (backup == null) return it;
            ItemStack base = ItemStack.deserializeBytes(backup);
            var bm = base.getItemMeta();
            // Restaurar solo nuestros atributos y lineas; conservar encantamientos, dano, nombre y datos del autor actuales.
            for (Attribute a : List.of(Attribute.ATTACK_DAMAGE, Attribute.ARMOR, Attribute.ARMOR_TOUGHNESS, Attribute.MAX_HEALTH)) {
                meta.removeAttributeModifier(a);
                var modifiers = bm.getAttributeModifiers(a);
                if (modifiers != null) modifiers.forEach(x -> meta.addAttributeModifier(a,x));
            }
            cleanLore(meta);
            meta.getPersistentDataContainer().remove(original);
            for (String kind : List.of("item", "armor")) meta.getPersistentDataContainer().remove(NamespacedKey.fromString("auraskills:"+kind+"_requirements"));
            ItemStack result=it.clone(); result.setItemMeta(meta);
            return data(result,null);
        }
        // Validacion estructural, no solo version: el datapack puede reescribir atributos/lore de Harvester.
        if (backup != null && correct(it,r)) return it;
        ItemStack out = it.clone();
        if (backup == null) meta.getPersistentDataContainer().set(original,PersistentDataType.BYTE_ARRAY,it.serializeAsBytes());
        cleanLore(meta);
        if (str(r,"kind").equals("weapon") && !List.of("bow","crossbow").contains(str(r,"family"))) {
            remove(meta,Attribute.ATTACK_DAMAGE);
            attr(meta,Attribute.ATTACK_DAMAGE,val(r,"damage")-1,"damage",EquipmentSlotGroup.MAINHAND);
        }
        if (str(r,"kind").equals("armor")) {
            remove(meta,Attribute.ARMOR); remove(meta,Attribute.ARMOR_TOUGHNESS); remove(meta,Attribute.MAX_HEALTH);
            // Un modificador cero evita que reaparezcan los atributos por defecto del material.
            var slot=switch(str(r,"piece")) { case "helmet" -> EquipmentSlotGroup.HEAD; case "leggings" -> EquipmentSlotGroup.LEGS; case "boots" -> EquipmentSlotGroup.FEET; default -> EquipmentSlotGroup.CHEST; };
            attr(meta,Attribute.ARMOR,0,"armor_zero",slot);
            attr(meta,Attribute.MAX_HEALTH,val(r,"health"),"health",slot);
        }
        var req = meta.getPersistentDataContainer().getAdapterContext().newPersistentDataContainer();
        req.set(NamespacedKey.fromString("auraskills:"+str(r,"skill")),PersistentDataType.INTEGER,num(r,"level"));
        meta.getPersistentDataContainer().set(NamespacedKey.fromString("auraskills:"+(str(r,"kind").equals("armor")?"armor":"item")+"_requirements"),PersistentDataType.TAG_CONTAINER,req);
        var lore = meta.lore()==null ? new ArrayList<Component>() : new ArrayList<>(meta.lore());
        for (var line:r.getAsJsonArray("lore")) lore.add(Component.text("Astral | "+line.getAsString(),NamedTextColor.GOLD).decoration(TextDecoration.ITALIC,false));
        meta.lore(lore); out.setItemMeta(meta);
        return data(out,r);
    }
    void cleanLore(ItemMeta m) {
        if (m.lore()!=null) m.lore(m.lore().stream().filter(c -> !PlainTextComponentSerializer.plainText().serialize(c).startsWith("Astral | ")).toList());
    }
    boolean correct(ItemStack it, JsonObject r) {
        var n=CraftItemStack.asNMSCopy(it).get(DataComponents.CUSTOM_DATA);
        if(n==null) return false;
        var a=n.copyTag().getCompoundOrEmpty("astral");
        if(a.getIntOr("stellarity",0)!=num(r,"version")) return false;
        var m=it.getItemMeta();
        if(m.lore()==null || m.lore().stream().noneMatch(c -> PlainTextComponentSerializer.plainText().serialize(c).equals("Astral | Tier: "+num(r,"tier")))) return false;
        if(str(r,"kind").equals("weapon") && !List.of("bow","crossbow").contains(str(r,"family"))) {
            var mods=m.getAttributeModifiers(Attribute.ATTACK_DAMAGE);
            return mods!=null && mods.stream().anyMatch(x -> mine(x) && Math.abs(x.getAmount()-(val(r,"damage")-1))<.001);
        }
        return true;
    }
    ItemStack data(ItemStack it, JsonObject r) {
        var n=CraftItemStack.asNMSCopy(it);
        CustomData.update(DataComponents.CUSTOM_DATA,n,t -> {
            if(r==null) { t.remove("astral"); return; }
            var a=new CompoundTag();
            a.putString("id","stellarity_"+id(it)); a.putString("type",str(r,"kind"));
            a.putString("w",str(r,"family")); a.putInt("tier",num(r,"tier")); a.putInt("stellarity",num(r,"version"));
            if(r.has("defense")) a.putInt("def",num(r,"defense"));
            if(r.has("damage")) a.putDouble("damage",val(r,"damage"));
            t.put("astral",a);
        });
        return CraftItemStack.asBukkitCopy(n);
    }
    public void scan(Player p) {
        var inv=p.getInventory();
        for(int i=0;i<inv.getSize();i++) {
            ItemStack old=inv.getItem(i), n=convert(p,old);
            if(n!=old) inv.setItem(i,n);
        }
        var armor=inv.getArmorContents(); boolean changed=false;
        for(int i=0;i<armor.length;i++) if(gear(row(armor[i])) && allowed(p) && !meets(p,row(armor[i]))) {
            ItemStack removed=armor[i]; armor[i]=null; changed=true;
            inv.setArmorContents(armor);
            for(var left:inv.addItem(removed).values()) p.getWorld().dropItem(p.getLocation(),left).setOwner(p.getUniqueId());
        }
        if(changed) inv.setArmorContents(armor);
    }
    public boolean meets(Player p, JsonObject r) {
        if(!gear(r)) return true;
        return skill(p,str(r,"skill"))>=num(r,"level");
    }
    int skill(Player p,String name) {
        try {
            var plugin=Bukkit.getPluginManager().getPlugin("AuraSkills");
            if(plugin==null || !plugin.isEnabled()) return -1;
            var loader=plugin.getClass().getClassLoader();
            var api=Class.forName("dev.aurelium.auraskills.api.AuraSkillsApi",true,loader);
            var userType=Class.forName("dev.aurelium.auraskills.api.user.SkillsUser",true,loader);
            Object user=api.getMethod("getUser",UUID.class).invoke(api.getMethod("get").invoke(null),p.getUniqueId());
            if(user==null || !(boolean)userType.getMethod("isLoaded").invoke(user)) return -1;
            Object skill=Class.forName("dev.aurelium.auraskills.api.skill.Skills",true,loader).getField(name.toUpperCase(Locale.ROOT)).get(null);
            return (int)userType.getMethod("getSkillLevel",Class.forName("dev.aurelium.auraskills.api.skill.Skill",true,loader)).invoke(user,skill);
        } catch(ReflectiveOperationException | RuntimeException ex) { return -1; }
    }
    boolean blocked(Player p, ItemStack it) { return allowed(p) && gear(row(it)) && !meets(p,row(it)); }
    @EventHandler(priority=EventPriority.LOWEST) public void interact(PlayerInteractEvent e) {
        scan(e.getPlayer()); if(blocked(e.getPlayer(),e.getItem())) { e.setCancelled(true); e.getPlayer().sendMessage("§cNo cumplis el requisito de este objeto Stellarity."); }
    }
    @EventHandler(priority=EventPriority.LOWEST) public void block(BlockBreakEvent e) { if(blocked(e.getPlayer(),e.getPlayer().getInventory().getItemInMainHand())) e.setCancelled(true); }
    @EventHandler(priority=EventPriority.LOWEST) public void shoot(EntityShootBowEvent e) {
        if(e.getEntity() instanceof Player p) { scan(p); if(blocked(p,e.getBow())) { e.setCancelled(true); return; }
            if(allowed(p)&&gear(row(e.getBow()))) remember(e.getProjectile(),id(e.getBow())); }
    }
    @EventHandler(priority=EventPriority.LOWEST) public void launch(ProjectileLaunchEvent e) {
        if(e.getEntity().getShooter() instanceof Player p) {
            scan(p); var it=p.getInventory().getItemInMainHand();
            if(blocked(p,it)) { e.setCancelled(true); return; }
            if(allowed(p)&&gear(row(it))) remember(e.getEntity(),id(it));
        }
    }
    @EventHandler(priority=EventPriority.MONITOR) public void hit(ProjectileHitEvent e) { Bukkit.getScheduler().runTaskLater(this,()->projectiles.remove(e.getEntity().getUniqueId()),2); }
    @EventHandler(priority=EventPriority.LOWEST) public void preAttack(io.papermc.paper.event.player.PrePlayerAttackEntityEvent e) {
        meleeTargets.put(e.getPlayer().getUniqueId(),e.getAttacked().getUniqueId());
        Bukkit.getScheduler().runTask(this,()->meleeTargets.remove(e.getPlayer().getUniqueId()));
    }
    @EventHandler(priority=EventPriority.LOWEST,ignoreCancelled=true) public void damage(EntityDamageEvent e) {
        Entity causing=e.getDamageSource().getCausingEntity();
        String type=e.getDamageSource().getDamageType().getKey().toString();
        if(causing==null && type.startsWith("kohara:") && e.getEntity().getScoreboardTags().stream().anyMatch(t -> t.startsWith("stellarity.damage."))) {
            // Kohara quita el atacante del segundo impacto de penetracion. Su marca transitoria es la prueba de autoria.
            var owners=Bukkit.getOnlinePlayers().stream().filter(q -> q.getWorld().equals(e.getEntity().getWorld()) && q.getScoreboardTags().contains("kohara.attacker")).toList();
            if(owners.size()==1) causing=owners.getFirst();
        }
        if(!(causing instanceof Player p)) return;
        scan(p);
        Entity direct=e.getDamageSource().getDirectEntity();
        String key=direct==null?"":projectiles.getOrDefault(direct.getUniqueId(),"");
        if(key.isEmpty()) key=id(p.getInventory().getItemInMainHand());
        String off=id(p.getInventory().getItemInOffHand());
        if((type.equals("stellarity:electric") && off.equals("copper_elektra_shield")) ||
           (type.equals("kohara:simulated_explosion") && off.equals("crest_of_the_end")) ||
           ((type.equals("stellarity:carcanet") || e.getEntity().getScoreboardTags().contains("stellarity.damage.carcanet")) && off.equals("starstruck_shield"))) key=off;
        if(!rows.has(key) || !allowed(p)) return;
        var r=rows.getAsJsonObject(key); if(!gear(r)) return;
        if(!meets(p,r)) { e.setCancelled(true); return; }
        boolean melee=type.equals("minecraft:player_attack") || e.getCause()==EntityDamageEvent.DamageCause.ENTITY_SWEEP_ATTACK;
        // Chorus dagger calcula el dano desde attack_damage: ya esta escalado y usa player_attack.
        boolean spectralWisp=key.equals("spectral_fury") && type.equals("minecraft:player_attack") && !e.getEntity().getUniqueId().equals(meleeTargets.get(p.getUniqueId()));
        if(melee && !spectralWisp) return;
        // Prismember obtiene el dano real por atributo ANTES de llamar Kohara (incluida su penetracion).
        if(type.equals("stellarity:prismember") || e.getEntity().getScoreboardTags().contains("stellarity.damage.prismember")) return;
        boolean tierMob=e.getEntity().getScoreboardTags().stream().anyMatch(t -> t.matches("astral\\.mt[1-9][0-9]?"));
        // PvP queda al circuito existente de arenas. Nunca agregar aqui otro divisor.
        if(!tierMob && !(e.getEntity() instanceof Player)) return;
        double factor=val(r,"factor");
        if(type.equals("minecraft:arrow") && List.of("bow","crossbow").contains(str(r,"family")))
            factor*=val(r,"damage")/(9*factor);
        e.setDamage(e.getDamage()*factor);
    }
    @EventHandler public void join(PlayerJoinEvent e) { scan(e.getPlayer()); }
    @EventHandler public void open(InventoryOpenEvent e) { if(e.getPlayer() instanceof Player p) scan(p); }
    @EventHandler public void click(InventoryClickEvent e) { if(e.getWhoClicked() instanceof Player p) Bukkit.getScheduler().runTask(this,()->scan(p)); }
    @EventHandler public void drag(InventoryDragEvent e) { if(e.getWhoClicked() instanceof Player p) Bukkit.getScheduler().runTask(this,()->scan(p)); }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void pickup(EntityPickupItemEvent e) { if(e.getEntity() instanceof Player p) e.getItem().setItemStack(convert(p,e.getItem().getItemStack())); }
    @Override public boolean onCommand(CommandSender s,Command c,String label,String[] args) {
        if(!s.hasPermission("astral.stellarity.admin")) return true;
        if(args.length==2 && args[0].equalsIgnoreCase("publico") && List.of("si","no").contains(args[1])) {
            getConfig().set("publico",args[1].equals("si")); saveConfig(); Bukkit.getOnlinePlayers().forEach(this::scan);
        } else if(args.length==1 && args[0].equalsIgnoreCase("recargar")) { reloadConfig(); loadTable(); Bukkit.getOnlinePlayers().forEach(this::scan); }
        else if(args.length==1 && args[0].equalsIgnoreCase("ver") && s instanceof Player p) {
            scan(p); s.sendMessage("Stellarity: "+id(p.getInventory().getItemInMainHand())+" "+row(p.getInventory().getItemInMainHand()));
        }
        s.sendMessage("Stellarity: "+(getConfig().getBoolean("publico",false)?"PUBLICO":"solo ByTrainx")+". /stellarity publico si|no, recargar, ver");
        return true;
    }
}
