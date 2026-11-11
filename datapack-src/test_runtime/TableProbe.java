package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import org.bukkit.craftbukkit.entity.CraftPlayer;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
import net.minecraft.world.inventory.CraftingMenu;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.skill.Skills;

/** Integracion en Paper real, cliente NMS simulado: no verifica pixeles ni conexion. */
public final class TableProbe extends JavaPlugin {
    Player player; int failures; CraftingMenu menu;
    void check(boolean ok,String message) {if(!ok)failures++;getLogger().info("TABLE "+(ok?"PASS ":"FAIL ")+message);}
    void call(String method) throws Exception {
        var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");
        var m=plugin.getClass().getDeclaredMethod(method);m.setAccessible(true);m.invoke(plugin);
    }
    Player fake() throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)Bukkit.getWorlds().getFirst()).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes("AstralTableProbe".getBytes()),"TableProbe");
        var fake=new ServerPlayer(server,world,profile,ClientInformation.createDefault());
        var connection=new Connection(PacketFlow.SERVERBOUND);
        connection.channel=new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler",connection);
        connection.address=new java.net.InetSocketAddress("127.0.0.1",0);
        fake.connection=new ServerGamePacketListenerImpl(server,connection,fake,CommonListenerCookie.createInitial(profile,false));
        world.getWorld().getChunkAt(0,0).setForceLoaded(true);fake.setPos(0,100,0);world.addNewPlayer(fake);
        var list=server.getPlayerList();list.players.add(fake);
        for(String key:List.of("playersByUUID","playersByName")) {
            var field=net.minecraft.server.players.PlayerList.class.getDeclaredField(key);field.setAccessible(true);
            ((Map)field.get(list)).put(key.equals("playersByUUID")?profile.id():profile.name().toLowerCase(Locale.ROOT),fake);
        }
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);return p;
    }
    ItemStack item(String id) {
        return Bukkit.getLootTable(NamespacedKey.fromString("astral:item/"+id)).populateLoot(new Random(),new org.bukkit.loot.LootContext.Builder(player.getLocation()).build()).iterator().next();
    }
    ShapelessRecipe recipe(String id) {return (ShapelessRecipe)Bukkit.getRecipe(NamespacedKey.fromString("astral:mesa/"+id));}
    CraftingInventory inv() {return (CraftingInventory)player.getOpenInventory().getTopInventory();}
    void open() {
        player.closeInventory();player.openWorkbench(null,true);
        menu=(CraftingMenu)((CraftPlayer)player).getHandle().containerMenu;
    }
    void fill(String id,int count) {
        inv().setMatrix(new ItemStack[9]);var ingredients=recipe(id).getChoiceList();
        for(int i=0;i<ingredients.size();i++) {var stack=ingredients.get(i).getItemStack();stack.setAmount(count);inv().setItem(i+1,stack);}
        menu.slotsChanged(menu.craftSlots);
    }
    boolean result(String id) {return inv().getResult()!=null && inv().getResult().isSimilar(item(id));}
    void levels(int n) {var user=AuraSkillsApi.get().getUser(player.getUniqueId());for(var skill:Skills.values())user.setSkillLevel(skill,n);}
    int count(String id) {var target=item(id);return Arrays.stream(player.getInventory().getContents()).filter(Objects::nonNull).filter(target::isSimilar).mapToInt(ItemStack::getAmount).sum();}
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command command,String label,String[] args) {
      try {
        switch(args[0]) {
        case "start" -> {
            player=fake();Bukkit.getPluginManager().callEvent(new org.bukkit.event.player.PlayerJoinEvent(player,net.kyori.adventure.text.Component.empty()));
            check(recipe("shadowsteel")!=null,"recetas registradas despues del arranque");
            check(Bukkit.getRecipe(NamespacedKey.fromString("astral:mesa/asura_espada"))==null,"receta grande solo Forja");
            open();
        }
        case "exact" -> {
            levels(50);
            for(String id:List.of("shadowsteel","netherita_reforzada","espada_1","talisman_vida_1")) {
                fill(id,1);check(result(id),"materiales exactos: "+id);
                for(int i=0;i<9;i++) {
                    var stack=inv().getItem(i+1);
                    if(stack!=null && stack.hasItemMeta()) {inv().setItem(i+1,new ItemStack(stack.getType()));break;}
                }
                menu.slotsChanged(menu.craftSlots);check(!result(id),"rechaza sustitucion vanilla: "+id);
            }
        }
        case "level" -> {levels(1);fill("espada_1",1);check(inv().getResult()==null || inv().getResult().getType().isAir(),"sin nivel no hay resultado");levels(50);menu.slotsChanged(menu.craftSlots);check(result("espada_1"),"con nivel vuelve resultado");}
        case "vanilla" -> {
            inv().setMatrix(new ItemStack[9]);
            var vanilla=new ItemStack[9];for(int i=0;i<9;i++)vanilla[i]=new ItemStack(Material.IRON_INGOT);
            inv().setMatrix(vanilla);menu.slotsChanged(menu.craftSlots);check(inv().getResult()!=null && inv().getResult().getType()==Material.IRON_BLOCK,"vanilla conserva receta");
            var custom=item("shadowsteel");
            inv().setItem(1,custom);menu.slotsChanged(menu.craftSlots);check(inv().getResult()==null || inv().getResult().getType().isAir(),"Astral no se consume en receta vanilla");
        }
        case "shift" -> {
            player.getInventory().clear();fill("shadowsteel",3);
            menu.clicked(0,0,net.minecraft.world.inventory.ContainerInput.QUICK_MOVE,((CraftPlayer)player).getHandle());
            check(count("shadowsteel")==3,"shift-clic produce exactamente 3");
            check(Arrays.stream(inv().getMatrix()).allMatch(s->s==null || s.getType().isAir()),"shift-clic consume exactamente ingredientes");
            fill("shadowsteel",2);
            menu.clicked(0,0,net.minecraft.world.inventory.ContainerInput.PICKUP,((CraftPlayer)player).getHandle());
            check(menu.getCarried().getCount()==1,"clic normal produce una unidad en cursor");
            check(Arrays.stream(inv().getMatrix()).filter(Objects::nonNull).filter(s->!s.getType().isAir()).mapToInt(ItemStack::getAmount).sum()==2,"clic normal consume un juego de ingredientes");
            menu.setCarried(net.minecraft.world.item.ItemStack.EMPTY);
            player.getInventory().clear();for(int i=0;i<36;i++)player.getInventory().setItem(i,new ItemStack(Material.COBBLESTONE,64));
            fill("shadowsteel",2);menu.clicked(0,0,net.minecraft.world.inventory.ContainerInput.QUICK_MOVE,((CraftPlayer)player).getHandle());
            check(Arrays.stream(inv().getMatrix()).filter(Objects::nonNull).filter(s->!s.getType().isAir()).mapToInt(ItemStack::getAmount).sum()==4 && count("shadowsteel")==0,"inventario lleno no consume ni duplica");
        }
        case "book" -> {
            inv().setMatrix(new ItemStack[9]);player.getInventory().clear();
            var key=NamespacedKey.fromString("astral:mesa/shadowsteel");player.undiscoverRecipe(key);call("discoverTableRecipes");
            check(!player.hasDiscoveredRecipe(key),"no desbloquea sin ingrediente");
            player.getInventory().addItem(item("esencia_nether"),new ItemStack(Material.IRON_INGOT));call("discoverTableRecipes");
            check(player.hasDiscoveredRecipe(key),"desbloquea al conseguir material");
            var handle=((CraftPlayer)player).getHandle();var manager=((CraftServer)Bukkit.getServer()).getServer().getRecipeManager();
            var holder=manager.getRecipes().stream().filter(r->r.id().identifier().toString().equals(key.toString())).findFirst().orElseThrow();
            manager.listDisplaysForRecipe(holder.id(),entry->handle.connection.handlePlaceRecipe(new net.minecraft.network.protocol.game.ServerboundPlaceRecipePacket(menu.containerId,entry.id(),false)));
            check(result("shadowsteel"),"clic de libro autocompleta ExactChoice");
            check(Arrays.stream(inv().getMatrix()).filter(Objects::nonNull).filter(s->!s.getType().isAir()).mapToInt(ItemStack::getAmount).sum()==2,"autollenado mueve 2 ingredientes exactos");
        }
        case "migration" -> {
            inv().setMatrix(new ItemStack[9]);player.getInventory().clear();var old=item("esencia_nether");var meta=old.getItemMeta();meta.lore(List.of(net.kyori.adventure.text.Component.text("Lore anterior")));old.setItemMeta(meta);old.setAmount(7);player.getInventory().setItem(0,old);
            call("discoverTableRecipes");check(player.getInventory().getItem(0).isSimilar(item("esencia_nether")) && player.getInventory().getItem(0).getAmount()==7,"migracion de lore conserva cantidad e identidad");
        }
        case "forge" -> {
            player.closeInventory();player.getInventory().clear();player.getInventory().addItem(item("esencia_nether"),new ItemStack(Material.IRON_INGOT));
            // shadowsteel es la tercera receta de la fuente; resolver el indice desde el JSON empacado.
            var plugin=Bukkit.getPluginManager().getPlugin("AstralDecor");
            var rows=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(plugin.getResource("mesa.json"))).getAsJsonArray();
            for(int i=0;i<rows.size();i++)if(rows.get(i).getAsJsonObject().get("output").getAsString().equals("shadowsteel"))Bukkit.dispatchCommand(Bukkit.getConsoleSender(),"execute as "+player.getName()+" run function astral:forge/r/"+(i+1));
        }
        case "forgecheck" -> check(count("shadowsteel")==1,"Forja sigue produciendo mismo item");
        case "result" -> {player.saveData();getLogger().info("TABLE RESULT failures="+failures);}
        }
      } catch(Throwable ex) {failures++;getLogger().log(java.util.logging.Level.SEVERE,"TABLE FAIL exception",ex);}
      return true;
    }
}
