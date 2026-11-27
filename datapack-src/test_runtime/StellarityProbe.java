package astraltest;
import org.bukkit.*;
import org.bukkit.attribute.*;
import org.bukkit.entity.*;
import org.bukkit.inventory.*;
import org.bukkit.damage.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.plugin.java.JavaPlugin;
import net.minecraft.core.component.DataComponents;
import org.bukkit.craftbukkit.inventory.CraftItemStack;
import astral.stellarity.AstralStellarity;
import astral.AstralMesa;

public final class StellarityProbe extends JavaPlugin implements Listener {
    double damage=-1, nativeTotal=0; boolean cancelled;
    @Override public void onEnable() { Bukkit.getPluginManager().registerEvents(this,this); }
    void check(boolean ok,String label) { if(!ok) throw new AssertionError(label); getLogger().info("STELLAR PASS "+label); }
    @EventHandler(priority=EventPriority.MONITOR) public void damage(EntityDamageEvent e) { if(e.getEntity().getScoreboardTags().contains("prismprobe")) nativeTotal+=e.getDamage(); if(e.getEntity().getScoreboardTags().contains("stellarprobe")) { damage=e.getDamage(); cancelled=e.isCancelled(); } }
    ItemStack loot(String key) {
        var table=(org.bukkit.craftbukkit.CraftLootTable)Bukkit.getLootTable(NamespacedKey.fromString("stellarity:item/"+key));
        var params=new net.minecraft.world.level.storage.loot.LootParams.Builder(((org.bukkit.craftbukkit.CraftWorld)Bukkit.getWorlds().getFirst()).getHandle())
            .withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.ORIGIN,new net.minecraft.world.phys.Vec3(0,-59,0))
            .create(net.minecraft.world.level.storage.loot.parameters.LootContextParamSets.CHEST);
        return CraftItemStack.asBukkitCopy(table.getHandle().getRandomItems(params).getFirst());
    }
    void hand(Player p,ItemStack item) {p.getInventory().setHeldItemSlot(0);p.getInventory().setItemInMainHand(item);}
    boolean converted(ItemStack i) { var d=CraftItemStack.asNMSCopy(i).get(DataComponents.CUSTOM_DATA);return d!=null && d.copyTag().contains("astral"); }
    double amount(ItemStack i,Attribute a) { var mods=i.getItemMeta().getAttributeModifiers(a);return mods==null?0:mods.stream().filter(x->x.getOperation()==AttributeModifier.Operation.ADD_NUMBER).mapToDouble(AttributeModifier::getAmount).sum(); }
    @Override public boolean onCommand(org.bukkit.command.CommandSender s,org.bukkit.command.Command c,String l,String[] args) {
        var plugin=(AstralStellarity)Bukkit.getPluginManager().getPlugin("AstralStellarity");
        var mesa=(AstralMesa)Bukkit.getPluginManager().getPlugin("AstralMesa");
        Player p=Bukkit.getPlayerExact("ByTrainx"), other=Bukkit.getPlayerExact("StellarOther");
        switch(args[0]) {
        case "initial" -> {
            com.google.gson.JsonObject table;
            try(var reader=java.nio.file.Files.newBufferedReader(plugin.getDataFolder().toPath().resolve("tiers.json"))) {
                table=com.google.gson.JsonParser.parseReader(reader).getAsJsonObject();
            } catch(Exception ex) { throw new RuntimeException(ex); }
            for(var entry:table.entrySet()) {
                var row=entry.getValue().getAsJsonObject();
                if(!row.has("max_attack_speed")) continue;
                String key=entry.getKey();
                String path=key.startsWith("shulker_") ? "tool/"+key : "weapon/"+switch(key) {
                    case "alpha_wooden_sword" -> "ancient_wooden_sword";
                    case "spirit_dagger" -> "the_beginning_and_the_end";
                    default -> key;
                };
                var source=loot(path);
                var result=plugin.convert(p,source);
                double cap=row.get("max_attack_speed").getAsDouble();
                getLogger().info("STELLAR SPEED CHECK "+key+" "+plugin.attackSpeed(source)+" -> "+plugin.attackSpeed(result)+" cap "+cap+" "+result.getItemMeta().getAttributeModifiers(Attribute.ATTACK_SPEED));
                check(plugin.attackSpeed(result)<=cap+.000001,"tope velocidad "+entry.getKey());
                check(Math.abs(plugin.attackSpeed(result)-Math.min(plugin.attackSpeed(source),cap))<.000001,"conserva lentas "+entry.getKey());
                var restored=plugin.convert(other,result);
                check(java.util.Objects.equals(restored.getItemMeta().getAttributeModifiers(Attribute.ATTACK_SPEED),source.getItemMeta().getAttributeModifiers(Attribute.ATTACK_SPEED)),"restaura velocidad "+entry.getKey());
                if(plugin.attackSpeed(source)>cap+.000001) getLogger().info("STELLAR SPEED "+entry.getKey()+" "+plugin.attackSpeed(source)+" -> "+plugin.attackSpeed(result));
                if(entry.getKey().equals("alpha_wooden_sword")) {
                    check(Math.abs(plugin.attackSpeed(result)-1.6)<.000001,"Ancient Wooden Sword 1.6/s");
                    var old=CraftItemStack.asNMSCopy(result);
                    net.minecraft.world.item.component.CustomData.update(DataComponents.CUSTOM_DATA,old,t -> {
                        var a=t.getCompoundOrEmpty("astral");a.putInt("stellarity",1);t.put("astral",a);
                    });
                    var legacy=CraftItemStack.asBukkitCopy(old);var meta=legacy.getItemMeta();
                    meta.removeAttributeModifier(Attribute.ATTACK_SPEED);
                    source.getItemMeta().getAttributeModifiers(Attribute.ATTACK_SPEED).forEach(x -> meta.addAttributeModifier(Attribute.ATTACK_SPEED,x));
                    legacy.setItemMeta(meta);
                    check(Math.abs(plugin.attackSpeed(plugin.convert(p,legacy))-1.6)<.000001,"migra velocidad version 1");
                }
            }
            var raw=loot("weapon/dragonblade");
            var n=plugin.convert(p,raw);
            check(converted(n),"conversion ByTrainx");
            check(plugin.id(n).equals("dragonblade"),"custom_data autor conservado");
            check(amount(n,Attribute.ATTACK_DAMAGE)==62499,"Dragonblade dano 62500");
            check(n.getItemMeta().getEnchants().equals(raw.getItemMeta().getEnchants()),"habilidades y encantamientos conservados");
            check(n.getItemMeta().getAttributeModifiers(Attribute.ATTACK_SPEED).equals(raw.getItemMeta().getAttributeModifiers(Attribute.ATTACK_SPEED)),"velocidad conservada");
            check(n.equals(plugin.convert(p,n)),"conversion idempotente");
            check(!converted(plugin.convert(other,raw)),"otro jugador sin conversion");
            check(!converted(plugin.convert(other,n)),"prestamo privado restaura atributos originales");
            var food=loot("food/chorus_pie");
            check(food.equals(plugin.convert(p,food)),"consumible apilable intacto");
            var prism=plugin.convert(p,loot("weapon/prismember"));
            check(amount(prism,Attribute.ATTACK_DAMAGE)==312499,"Prismember T6");
            hand(p,n);other.getInventory().setItem(0,raw);
        }
        case "high" -> {
            hand(p,plugin.convert(p,loot("weapon/dragonblade")));
            var z=p.getWorld().spawn(p.getLocation().add(3,0,0),Zombie.class);z.setAI(false);z.addScoreboardTag("astral.mt5");z.addScoreboardTag("stellarprobe");
            z.getAttribute(Attribute.MAX_HEALTH).setBaseValue(262500);z.setHealth(262500);
            z.getAttribute(Attribute.ARMOR).setBaseValue(0);
            z.damage(62500,DamageSource.builder(DamageType.PLAYER_ATTACK).withCausingEntity(p).withDirectEntity(p).build());
            getLogger().info("DAMAGE melee="+damage+" cancelled="+cancelled+" hp="+z.getHealth());
            check(!cancelled && damage>=62500 && damage<125000,"golpe T5 sin doble multiplicacion");
            z.setNoDamageTicks(0);z.damage(12,DamageSource.builder(Registry.DAMAGE_TYPE.get(NamespacedKey.fromString("stellarity:dragonblade"))).withCausingEntity(p).withDirectEntity(p).build());
            getLogger().info("DAMAGE skill="+damage+" cancelled="+cancelled);
            check(!cancelled && damage>=62500 && damage<125000,"habilidad T5 escalada una vez");
            z.setNoDamageTicks(0);z.addScoreboardTag("stellarity.damage.dragonblade");p.addScoreboardTag("kohara.attacker");
            z.damage(4,DamageSource.builder(Registry.DAMAGE_TYPE.get(NamespacedKey.fromString("kohara:armor_piercing"))).build());
            check(Math.abs(damage-4*62500.0/12)<2,"penetracion sin atacante directo conserva autor");p.removeScoreboardTag("kohara.attacker");
            z.remove();
            var info=AstralMesa.infoAstral(p.getInventory().getItemInMainHand().getItemMeta());
            check(info!=null && info.id().equals("stellarity_dragonblade"),"Mesa reconoce equipo");
            check(mesa.sugerido(p.getInventory().getItemInMainHand().getItemMeta(),info)>0,"precio sugerido positivo");
            var f=loot("food/chorus_pie");var fi=AstralMesa.infoAstral(f.getItemMeta());
            check(fi!=null && mesa.sugerido(f.getItemMeta(),fi)==10000,"precio fijo comida sin convertir");
            var decorated=mesa.decorar(f,true,false,true);
            check(decorated!=null && decorated.getItemMeta().lore().stream().anyMatch(t->net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(t).contains("Precio sugerido")),"linea de precio enviada al cliente");
            var y=new org.bukkit.configuration.file.YamlConfiguration();
            y.set("Items.a.Item",java.util.Base64.getEncoder().encodeToString(loot("weapon/dragonblade").serializeAsBytes()));y.set("Items.a.Price",2222222);
            y.set("Items.b.Item",java.util.Base64.getEncoder().encodeToString(p.getInventory().getItemInMainHand().serializeAsBytes()));y.set("Items.b.Price",1111111);
            try {var file=new java.io.File(getDataFolder().getParentFile(),"CrazyAuctions/data.yml");file.getParentFile().mkdirs();y.save(file);} catch(Exception ex) {throw new RuntimeException(ex);}
            getLogger().info("AUCTION FOUND "+mesa.leerSubastas(true));
            var auction=mesa.decorar(p.getInventory().getItemInMainHand(),true,false,true);
            String auctionText=auction.getItemMeta().lore().stream().map(t->net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(t)).collect(java.util.stream.Collectors.joining(" "));
            getLogger().info("AUCTION TEXT "+auctionText);
            check(auctionText.contains("Subasta") && auctionText.contains("1.111.111$") && auctionText.contains("2 en venta"),"subasta minima une originales y convertidos");
            var privateView=mesa.decorar(f,true,false,false);
            check(privateView==null || privateView.getItemMeta().lore().stream().noneMatch(t->net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(t).contains("Precio sugerido")),"precio Stellarity sigue oculto a terceros");
            p.getInventory().setChestplate(plugin.convert(p,loot("armor/shulker/chestplate")));
            plugin.scan(p);
            check(p.getInventory().getChestplate()!=null,"requisito alto permite pechera");
            check(amount(p.getInventory().getChestplate(),Attribute.ARMOR)==0,"sin armadura vanilla");
            check(amount(p.getInventory().getChestplate(),Attribute.MAX_HEALTH)==1975,"vida pieza T5");
        }
        case "native_prepare" -> {
            hand(p,plugin.convert(p,loot("weapon/prismember")));nativeTotal=0;
            var z=p.getWorld().spawn(p.getLocation().add(3,0,0),Zombie.class);z.setAI(false);z.addScoreboardTag("astral.mt6");z.addScoreboardTag("prismprobe");
            z.getAttribute(Attribute.MAX_HEALTH).setBaseValue(10000000);z.setHealth(10000000);z.getAttribute(Attribute.ARMOR).setBaseValue(0);
        }
        case "native_check" -> {
            getLogger().info("NATIVE PRISMEMBER "+nativeTotal);
            check(nativeTotal>=200000 && nativeTotal<1000000,"funcion original Prismember sin doble factor, incluida penetracion");
            p.getWorld().getEntities().stream().filter(x->x.getScoreboardTags().contains("prismprobe")).forEach(Entity::remove);
        }
        case "arena_prepare" -> {
            var w=Bukkit.createWorld(new WorldCreator("arena").type(WorldType.FLAT).generateStructures(false));
            p.teleport(new Location(w,0,-59,0));other.teleport(new Location(w,3,-59,0));
            other.addScoreboardTag("stellarprobe");
            hand(p,plugin.convert(p,loot("weapon/dragonblade")));
            other.getAttribute(Attribute.MAX_HEALTH).setBaseValue(1000);other.setHealth(1000);
        }
        case "arena_check" -> {
            other.setNoDamageTicks(0);other.damage(12,DamageSource.builder(Registry.DAMAGE_TYPE.get(NamespacedKey.fromString("stellarity:dragonblade"))).withCausingEntity(p).withDirectEntity(p).build());
            getLogger().info("ARENA DAMAGE "+damage);
            check(!cancelled && damage>0 && damage<400,"PvP usa tope de arenas existente");
            other.removeScoreboardTag("stellarprobe");
            p.teleport(Bukkit.getWorlds().getFirst().getSpawnLocation());other.teleport(Bukkit.getWorlds().getFirst().getSpawnLocation());
        }
        case "low" -> {
            hand(p,plugin.convert(p,loot("weapon/dragonblade")));
            var z=p.getWorld().spawn(p.getLocation().add(3,0,0),Zombie.class);z.setAI(false);z.addScoreboardTag("astral.mt5");z.addScoreboardTag("stellarprobe");
            z.damage(5,DamageSource.builder(DamageType.PLAYER_ATTACK).withCausingEntity(p).withDirectEntity(p).build());
            check(cancelled,"requisito bloquea dano");z.remove();
            p.getInventory().setChestplate(plugin.convert(p,loot("armor/shulker/chestplate")));plugin.scan(p);
            getLogger().info("LOW CHEST "+p.getInventory().getChestplate());
            check(p.getInventory().getChestplate()==null || p.getInventory().getChestplate().getType().isAir(),"requisito impide stats de armadura");
        }
        case "functions" -> {
            plugin.scan(p);
            var sb=Bukkit.getScoreboardManager().getMainScoreboard();
            check(sb.getObjective("astral.wt").getScore("ByTrainx").getScore()==5,"tier mundo incluye Stellarity");
            check(sb.getObjective("astraldef").getScore("ByTrainx").getScore()==200,"Defensa T5 sin descuento de barra");
            check(p.getScoreboardTags().contains("astral.db7") && p.getScoreboardTags().contains("astral.db6") && p.getScoreboardTags().contains("astral.db3"),"Defensa binaria Skript");
        }
        case "public" -> {
            var n=plugin.convert(other,loot("weapon/dragonblade"));
            check(converted(n),"interruptor publico convierte otro jugador");other.getInventory().setItem(0,n);
        }
        case "closed" -> {plugin.scan(other);check(!converted(other.getInventory().getItem(0)),"volver a privado restaura otro jugador");}
        }
        getLogger().info("STELLAR PHASE "+args[0]+" OK");return true;
    }
}
