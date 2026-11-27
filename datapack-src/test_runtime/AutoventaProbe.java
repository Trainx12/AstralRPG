package astraltest;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;
public final class AutoventaProbe extends JavaPlugin {
    int failures, level=100; boolean respond=true; Player player;
    void check(boolean ok,String msg){if(!ok)failures++;getLogger().info("AUTOVENTA "+(ok?"PASS ":"FAIL ")+msg);}
    Player fake(String name, org.bukkit.World target) throws Exception {
        var server=((CraftServer)Bukkit.getServer()).getServer();
        var world=((CraftWorld)target).getHandle();
        var profile=new GameProfile(UUID.nameUUIDFromBytes(("OfflinePlayer:"+name).getBytes(java.nio.charset.StandardCharsets.UTF_8)),name);
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
        var p=fake.getBukkitEntity();p.setInvulnerable(true);p.setGravity(false);
        var essentials=Bukkit.getPluginManager().getPlugin("Essentials");
        var user=essentials.getClass().getMethod("getUser",Player.class).invoke(essentials,p);
        user.getClass().getMethod("setMoney",java.math.BigDecimal.class).invoke(user,java.math.BigDecimal.ZERO);
        return p;
    }

    void cmd(String c){Bukkit.dispatchCommand(Bukkit.getConsoleSender(),c);}
    ItemStack core(){return Bukkit.getLootTable(NamespacedKey.fromString("astral:item/autoventa")).populateLoot(new Random(),new org.bukkit.loot.LootContext.Builder(player.getLocation()).build()).iterator().next();}
    double balance(){
        try {
            var essentials=Bukkit.getPluginManager().getPlugin("Essentials");
            var user=essentials.getClass().getMethod("getUser",Player.class).invoke(essentials,player);
            return ((java.math.BigDecimal)user.getClass().getMethod("getMoney").invoke(user)).doubleValue();
        } catch(Exception e){throw new RuntimeException(e);}
    }
    void measure(){cmd("avtest "+player.getName()+" quote");}
    void prepare(int slot){
        cmd("avtest "+player.getName()+" reset");player.getInventory().clear();
        for(int i=0;i<36;i++)player.getInventory().setItem(i,new ItemStack(Material.DIRT,64));
        var coal=new ItemStack(Material.COAL,64);var meta=coal.getItemMeta();
        meta.getPersistentDataContainer().set(new NamespacedKey("probe","invisible"),org.bukkit.persistence.PersistentDataType.INTEGER,1);coal.setItemMeta(meta);
        player.getInventory().setItem(1,coal);
        var named=new ItemStack(Material.COAL,64);meta=named.getItemMeta();meta.setDisplayName("Protegido");named.setItemMeta(meta);player.getInventory().setItem(2,named);
        var lore=new ItemStack(Material.COAL,64);meta=lore.getItemMeta();meta.setLore(List.of("Protegido"));lore.setItemMeta(meta);player.getInventory().setItem(3,lore);
        if(slot==40)player.getInventory().setItemInOffHand(core());else player.getInventory().setItem(slot,core());
        measure();
    }
    void give(){
        // Llamada directa como desde el evento de minado, fuera del contexto de comandos Brigadier.
        var function=ch.njol.skript.lang.function.Functions.getFunction("am_give");
        function.execute(new Object[][]{{player},{new ch.njol.skript.aliases.ItemType(new ItemStack(Material.COAL,64))}});
        function.resetReturnValue();
    }
    public boolean onCommand(org.bukkit.command.CommandSender sender,org.bukkit.command.Command c,String label,String[] args){
        try{
            if(label.equalsIgnoreCase("dm")){
                // Doble local del puente DeluxeMenus/PAPI; no sustituye su verificacion remota.
                if(respond && args.length>0)cmd("am_autoventa_nivel "+args[1]+" "+level);
                return true;
            }
            if(args[0].equals("start")){
                var w=new WorldCreator("astral_minas").type(WorldType.FLAT).generatorSettings("{\"layers\":[{\"block\":\"minecraft:bedrock\",\"height\":1}],\"biome\":\"minecraft:plains\"}").createWorld();
                player=fake("ByTrainx",w);player.setGameMode(GameMode.SURVIVAL);return true;
            }
            if(args[0].equals("test")){
                Bukkit.getScheduler().runTask(this, () -> { try { runTests(); } catch(Throwable e) { failures++; e.printStackTrace(); getLogger().info("AUTOVENTA RESULT failures="+failures); } });
            }
        }catch(Throwable e){failures++;e.printStackTrace();getLogger().info("AUTOVENTA RESULT failures="+failures);}
        return true;
    }
    void runTests() throws Exception {
                cmd("autoventa privado");
                for(int slot:new int[]{0,10,35,40}){
                    level=100;prepare(slot);double before=balance();double quote=player.getMetadata("avquote").getFirst().asDouble();
                    var old=player.getWorld().dropItem(player.getLocation(),new ItemStack(Material.DIAMOND,3));
                    give();measure();
                    check(Math.abs(balance()-before-quote)<0.001 && quote>0,"pago igual a Venta rapida, slot "+slot+" antes="+before+" despues="+balance()+" cotizacion="+quote);
                    check(player.getInventory().getItem(1).getType()==Material.COAL,"recupera el mineral nuevo, slot "+slot);
                    check(player.getInventory().getItem(1).getItemMeta().getPersistentDataContainer().getKeys().size()>0 && !player.getInventory().getItem(1).getItemMeta().getPersistentDataContainer().has(new NamespacedKey("probe","invisible")),"recupera PDC del mineral nuevo, sin retener el vendido");
                    check(old.isValid()&&old.getItemStack().getAmount()==3,"conserva drop previo ajeno");old.remove();
                    check(player.getInventory().getItem(2).getItemMeta().hasDisplayName()&&player.getInventory().getItem(3).getItemMeta().hasLore(),"protege nombre y lore");
                    before=balance();give();measure();check(balance()==before,"enfriamiento impide segunda venta");
                }
                level=99;prepare(10);double before=balance();give();measure();check(balance()==before,"Mineria 99 bloqueada");
                level=100;respond=false;prepare(10);before=balance();give();measure();check(balance()==before,"sin lectura de Mineria no vende");respond=true;
                prepare(10);player.getInventory().setItem(1,new ItemStack(Material.DIRT,64));before=balance();give();measure();check(balance()==before,"sin minerales vendibles no cobra ni consume equipo");
                prepare(10);var spoof=new ItemStack(Material.HEART_OF_THE_SEA);var meta=spoof.getItemMeta();meta.setDisplayName("Nucleo de Venta Automatica");spoof.setItemMeta(meta);player.getInventory().setItem(10,spoof);before=balance();give();measure();check(balance()==before,"item renombrado no activa");
                player=fake("Visitante",player.getWorld());prepare(10);before=balance();give();measure();check(balance()==before,"Visitante privado bloqueado");
                cmd("autoventa publico");prepare(10);before=balance();give();measure();check(balance()>before,"Visitante publico permitido");
                player.teleport(Bukkit.getWorlds().getFirst().getSpawnLocation());prepare(10);before=balance();give();measure();check(balance()==before,"fuera de Minas bloqueado");
                getLogger().info("AUTOVENTA RESULT failures="+failures);
    }

}
