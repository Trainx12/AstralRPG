package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.craftbukkit.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.*;
import net.minecraft.server.network.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import com.mojang.authlib.GameProfile;

/** Registro nativo y apertura de cada dialogo. No certifica pixeles del cliente. */
public final class AtlasProbe extends JavaPlugin {
    int failures, checks;
    void check(boolean ok, String s) {
        checks++; if (!ok) failures++;
        getLogger().info("ATLAS " + (ok ? "PASS " : "FAIL ") + s);
    }
    public void onEnable() {
        Bukkit.getScheduler().runTaskLater(this, () -> {
            try {
                var server = ((CraftServer) Bukkit.getServer()).getServer();
                var registry = server.registryAccess().lookupOrThrow(Registries.DIALOG);
                Set<String> keys = new HashSet<>();
                registry.keySet().forEach(k -> keys.add(k.toString()));
                var expected = new String(getResource("expected.txt").readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).lines().toList();
                var world = ((CraftWorld) Bukkit.getWorlds().getFirst()).getHandle();
                var profile = new GameProfile(UUID.randomUUID(), "AtlasProbe");
                var fake = new ServerPlayer(server, world, profile, ClientInformation.createDefault());
                var connection = new Connection(PacketFlow.SERVERBOUND);
                connection.channel = new io.netty.channel.embedded.EmbeddedChannel();
                connection.channel.pipeline().addLast("packet_handler", connection);
                connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
                fake.connection = new ServerGamePacketListenerImpl(server, connection, fake, CommonListenerCookie.createInitial(profile, false));
                fake.setPos(0, 100, 0); world.addNewPlayer(fake);
                var list = server.getPlayerList(); list.players.add(fake);
                for (String key : List.of("playersByUUID", "playersByName")) {
                    var field = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); field.setAccessible(true);
                    ((Map) field.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fake);
                }
                var player = fake.getBukkitEntity(); player.setGravity(false); player.setInvulnerable(true);
                for (String key : expected) {
                    check(keys.contains(key), "registro " + key);
                    check(Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "minecraft:dialog show AtlasProbe " + key), "apertura " + key);
                }
                var objective = Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.guia2");
                check(objective != null, "objetivo trigger cargado");
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "scoreboard players enable AtlasProbe astral.guia2");
                check(Bukkit.dispatchCommand(player, "trigger astral.guia2 set 1"), "trigger como jugador sin OP");
                Bukkit.getScheduler().runTaskLater(this, () -> {
                    var s = objective.getScore("AtlasProbe"); check(!s.isScoreSet() || s.getScore() == 0, "tick consume el trigger y abre el indice");
                    getLogger().info("ATLAS RESULT checks=" + checks + " failures=" + failures);
                }, 20L);
            } catch (Throwable e) {
                check(false, e.toString()); e.printStackTrace();
                getLogger().info("ATLAS RESULT checks=" + checks + " failures=" + failures);
            }
        }, 80L);
    }
}
