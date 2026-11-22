package astraltest;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.potion.*;

/** Ensayo local de la Nave del Vacio: vista desde afuera, salas, compuertas, caida al casco, escudo de los Ojos y fin.
 *  Nunca va al server. Los datos (llegadas, centros) vienen por nave-probe.properties. */
public final class NaveProbe extends JavaPlugin {
    int failures; Player a; World nave;
    final List<double[]> llegadas = new ArrayList<>(), centros = new ArrayList<>();
    void check(boolean ok, String s) { if (!ok) failures++; getLogger().info("NAVE " + (ok ? "PASS " : "FAIL ") + s); }
    void cmd(String c) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), c); }
    void later(int ticks, Runnable r) { Bukkit.getScheduler().runTaskLater(this, () -> { try { r.run(); } catch (Throwable t) { check(false, "" + t); t.printStackTrace(); finish(); } }, ticks); }
    static double[] xyz(String s) { String[] p = s.split(","); return new double[]{Double.parseDouble(p[0]), Double.parseDouble(p[1]), Double.parseDouble(p[2])}; }

    @Override public void onEnable() {
        try (var in = getResource("nave-probe.properties")) {
            var p = new Properties(); p.load(in);
            for (String s : p.getProperty("llegadas").split(";")) llegadas.add(xyz(s));
            for (String s : p.getProperty("centros").split(";")) centros.add(xyz(s));
        } catch (Exception e) { throw new IllegalStateException(e); }
        Bukkit.getScheduler().runTaskLater(this, () -> {
            nave = Bukkit.createWorld(new WorldCreator("nave").generator("AstralOceano:vacio"));
            nave.setGameRule(GameRule.DO_MOB_SPAWNING, false);
            for (int cx = -6; cx <= 6; cx++) for (int cz = -7; cz <= 7; cz++) nave.setChunkForceLoaded(cx, cz, true);
            cmd("/world nave"); cmd("/pos1 -80,40,-100"); cmd("/schem load spaceship.schem");
        }, 40);
        // La schematic se carga en segundo plano: pegar despues.
        Bukkit.getScheduler().runTaskLater(this, () -> { cmd("/placement pos1"); cmd("/paste -a"); }, 240);
        Bukkit.getScheduler().runTaskLater(this, this::start, 700);
    }

    Player fake(World w, String name) throws Exception {
        var server = ((org.bukkit.craftbukkit.CraftServer) Bukkit.getServer()).getServer();
        var lvl = ((org.bukkit.craftbukkit.CraftWorld) w).getHandle();
        var profile = new com.mojang.authlib.GameProfile(UUID.randomUUID(), name);
        var fp = new net.minecraft.server.level.ServerPlayer(server, lvl, profile, net.minecraft.server.level.ClientInformation.createDefault());
        var connection = new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND);
        connection.channel = new io.netty.channel.embedded.EmbeddedChannel();
        connection.channel.pipeline().addLast("packet_handler", connection);
        connection.address = new java.net.InetSocketAddress("127.0.0.1", 0);
        fp.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(server, connection, fp,
            net.minecraft.server.network.CommonListenerCookie.createInitial(profile, false));
        fp.setPos(0.5, 100, 0.5); lvl.addNewPlayer(fp); var list = server.getPlayerList(); list.players.add(fp);
        for (String key : List.of("playersByUUID", "playersByName")) {
            var f = net.minecraft.server.players.PlayerList.class.getDeclaredField(key); f.setAccessible(true);
            ((Map) f.get(list)).put(key.equals("playersByUUID") ? profile.id() : profile.name().toLowerCase(Locale.ROOT), fp);
        }
        var ch = (io.netty.channel.embedded.EmbeddedChannel) connection.channel;
        Bukkit.getScheduler().runTaskTimer(this, () -> { ch.releaseOutbound(); try { fp.doTick(); } catch (Throwable ignored) {} }, 1, 1);
        Player p = fp.getBukkitEntity(); p.setGameMode(GameMode.SURVIVAL);
        p.addPotionEffect(new PotionEffect(PotionEffectType.RESISTANCE, -1, 255, false, false));
        return p;
    }

    boolean cerca(Player p, double[] c, double r) { return p.getWorld() == nave && p.getLocation().distance(new Location(nave, c[0] + 0.5, c[1], c[2] + 0.5)) < r; }
    List<Entity> tag(String t) { List<Entity> o = new ArrayList<>(); for (Entity e : nave.getEntities()) if (!e.isDead() && e.getScoreboardTags().contains(t)) o.add(e); return o; }

    void start() {
        try {
            double[] l0 = llegadas.get(0);
            check(nave.getBlockAt((int) l0[0], (int) l0[1] - 1, (int) l0[2]).getType().isSolid(), "nave pegada: piso en la llegada del Hangar " + nave.getBlockAt((int) l0[0], (int) l0[1] - 1, (int) l0[2]).getType());
            check(nave.getBlockAt((int) l0[0], (int) l0[1], (int) l0[2]).getType().isAir(), "aire en la llegada del Hangar");
            for (int i = 0; i < centros.size(); i++) { double[] c = centros.get(i); check(nave.getBlockAt((int) c[0], (int) c[1] - 1, (int) c[2]).getType().isSolid(), "piso en el centro de la sala " + (i + 1)); }
            a = fake(Bukkit.getWorlds().get(0), "Piloto");
            later(20, () -> cmd("mazentrar Piloto nave"));
            later(60, () -> {
                check(a.getWorld() == nave, "mazentrar lleva a la nave: " + a.getWorld().getName());
                check(a.getGameMode() == GameMode.SPECTATOR, "vista desde afuera: espectador (" + a.getGameMode() + ")");
                check(a.getSpectatorTarget() != null && a.getSpectatorTarget().getScoreboardTags().contains("nave.camara"), "mira por la camara");
                Location c1 = a.getSpectatorTarget() == null ? null : a.getSpectatorTarget().getLocation();
                later(60, () -> {
                    Location c2 = a.getSpectatorTarget() == null ? null : a.getSpectatorTarget().getLocation();
                    check(c1 != null && c2 != null && c1.distance(c2) > 10, "la camara se mueve alrededor de la nave");
                    check(c2 != null && Math.abs(c2.getX()) > 60 || c2 != null && Math.abs(c2.getZ()) > 100, "la camara esta afuera de la nave: " + c2);
                });
                later(300, () -> {
                    check(a.getGameMode() == GameMode.SURVIVAL, "al terminar la vista vuelve a supervivencia (" + a.getGameMode() + ")");
                    check(cerca(a, llegadas.get(0), 3), "y aparece en la llegada del Hangar: " + a.getLocation());
                    check(tag("nave.camara").isEmpty(), "la camara se borra");
                    // Caida al casco: vuelve a la sala.
                    a.teleport(new Location(nave, l0[0] + 0.5, 45, l0[2] + 0.5));
                    later(30, () -> { check(cerca(a, llegadas.get(0), 3), "caer al casco hueco devuelve a la llegada"); sala(0); });
                });
            });
        } catch (Throwable t) { check(false, "inicio: " + t); t.printStackTrace(); finish(); }
    }

    /** Limpia las oleadas de la sala i hasta que se abre la compuerta; la pisa y comprueba la sala siguiente. */
    void sala(int i) {
        if (i == centros.size() - 1) { jefe(); return; }
        later(100, () -> {
            List<Entity> mobs = tag("nave.mob");
            Map<String, Integer> tipos = new TreeMap<>();
            for (Entity e : mobs) tipos.merge(e.getType().name(), 1, Integer::sum);
            if (!mobs.isEmpty()) {
                getLogger().info("NAVE sala " + (i + 1) + " mobs " + tipos);
                if (i == 0) check(mobs.stream().filter(e -> e instanceof Enderman && e.getTicksLived() > 20).allMatch(e -> e.getScoreboardTags().stream().anyMatch(t -> t.equals("astral.mt4") || t.equals("astral.mt5") || t.equals("astral.mt6"))), "los mobs de la nave son tier 5 (o uno arriba/abajo, como en toda mazmorra)");
                if (i == 4) check(mobs.stream().anyMatch(e -> e instanceof Enderman && e.getName().contains("Timonel")), "Puente de Mando: aparece el Timonel");
                mobs.forEach(Entity::remove);
                sala(i);   // puede haber otra oleada
                return;
            }
            double[] c = centros.get(i);
            a.teleport(new Location(nave, c[0] + 0.5, c[1], c[2] + 0.5));
            later(30, () -> {
                check(cerca(a, llegadas.get(i + 1), 3), "la compuerta de la sala " + (i + 1) + " lleva a la sala " + (i + 2) + ": " + a.getLocation().toVector());
                sala(i + 1);
            });
        });
    }

    void jefe() {
        later(120, () -> {
            List<Entity> j = tag("nave.jefe");
            check(j.size() == 1, "Palma: aparece el Capitan del Vacio (" + j.size() + ")");
            if (j.isEmpty()) { finish(); return; }
            LivingEntity cap = (LivingEntity) j.get(0);
            getLogger().info("NAVE vida del Capitan " + cap.getHealth() + " / " + cap.getAttribute(Attribute.MAX_HEALTH).getValue());
            check(cap.getAttribute(Attribute.MAX_HEALTH).getValue() >= 19_000_000, "vida del Capitan ~19,7 millones");
            cap.damage(cap.getMaxHealth() * 0.35, a);   // baja de 70%
            later(10, () -> cap.damage(1000, a));          // el siguiente golpe dispara la fase 2 (Ojos Vigias)
            later(50, () -> {
                List<Entity> ojos = tag("nave.ojo");
                check(ojos.size() == 3, "fase 2: 3 Ojos Vigias (" + ojos.size() + ")");
                double antes = cap.getHealth();
                cap.damage(100000, a);
                double con = antes - cap.getHealth();
                ojos.forEach(Entity::remove);
                later(10, () -> {
                    double antes2 = cap.getHealth();
                    cap.damage(100000, a);
                    double sin = antes2 - cap.getHealth();
                    check(sin > 0 && Math.abs(con / sin - 0.2) < 0.02, "con Ojos vivos recibe 20% del dano: " + con + " contra " + sin + " sin Ojos");
                    cap.setHealth(0);
                    later(60, () -> {
                        check(!tag("nave.premio").isEmpty(), "al morir el jefe aparecen cofre y guia (" + tag("nave.premio").size() + ")");
                        finish();
                    });
                });
            });
        });
    }

    void finish() { later(20, () -> { getLogger().info("NAVE RESULT failures=" + failures); Bukkit.shutdown(); }); }
}
