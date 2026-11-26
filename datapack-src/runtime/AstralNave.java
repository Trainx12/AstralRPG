package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.boss.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;

/**
 * Nave del Vacio (generado por datapack-src/nave.py): mazmorra tier 5 en 3 copias.
 * - Vista de la mano desde afuera al entrar: el jugador queda en espectador y recorre una ruta alrededor de la nave
 *   (23/11: antes miraba por un soporte invisible y no cargaba el mapa). Agacharse la saltea. Despues aparece en la sala del grupo.
 * - Salas por compuertas: al limpiar la sala se abre la compuerta (centro); pisarla, o esperar, lleva a todo el grupo
 *   a la sala siguiente. Cada sala es una capsula de adentro de la mano, cerrada con barreras en puertas y ventanas
 *   (nave_barreras.txt, se ponen solas). Quien sale de la zona de su sala vuelve; los mobs tambien.
 * - Mobs siempre agresivos: cada medio segundo buscan al jugador mas cercano. Sin perlas ni coros (ni se sueltan),
 *   sin abrir shulkers ni cofres del mapa.
 * - Palma: Capitan del Vacio. Con Ojos Vigias vivos recibe solo el % de "escudo". Al morir: mazfin, cofre y guia.
 */
public final class AstralNave extends JavaPlugin implements Listener {
    record Sala(String id, String nombre, double[] llegada, double[] centro, List<double[]> puntos, List<Map<String, Integer>> oleadas) {}

    static final class Estado {
        int sala = 0;        // sala actual (indice)
        int oleada = 0;      // 0 = esperando, n = oleada en curso, -1 = compuerta abierta
        long cuando = 0;     // proxima accion (ms)
        int maxVivos = 1;
        boolean terminado = false;
    }

    List<String> mundos = List.of();
    final List<Sala> salas = new ArrayList<>();
    int espera = 20, tope = 9; double extra = 0.5, escudo = 0.2;
    String jefe = "astral_nave_capitan", minijefe = "astral_nave_timonel";
    final Map<String, Estado> estado = new HashMap<>();
    final Map<String, BossBar> barras = new HashMap<>();
    final Map<UUID, Intro> intros = new HashMap<>();
    NamespacedKey introKey;
    boolean abierta;   // cerrada hasta el evento: /nave abrir

    @Override public void onEnable() {
        saveResource("config.yml", true);   // la config sale siempre del jar (nave.py); lo que cambia el admin va en estado.yml
        reloadConfig();
        introKey = new NamespacedKey(this, "intro_modo");
        var c = getConfig();
        mundos = c.getStringList("mundos");
        espera = c.getInt("espera-compuerta", 20); tope = c.getInt("tope", 9);
        extra = c.getDouble("extra-jugador", 0.5); escudo = c.getDouble("escudo", 0.2);
        abierta = org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.File(getDataFolder(), "estado.yml")).getBoolean("abierta", false);
        jefe = c.getString("jefe", jefe); minijefe = c.getString("minijefe", minijefe);
        for (var m : c.getMapList("salas")) {
            List<double[]> pts = new ArrayList<>();
            for (Object o : (List<?>) m.get("puntos")) pts.add(xyz(o.toString()));
            List<Map<String, Integer>> olas = new ArrayList<>();
            for (Object o : (List<?>) m.get("oleadas")) {
                Map<String, Integer> ola = new LinkedHashMap<>();
                for (String part : o.toString().split(",")) { int i = part.lastIndexOf(':'); ola.put(part.substring(0, i).trim(), Integer.parseInt(part.substring(i + 1).trim())); }
                olas.add(ola);
            }
            salas.add(new Sala(m.get("id").toString(), m.get("nombre").toString(), xyz(m.get("llegada").toString()), xyz(m.get("centro").toString()),
                pts, olas));
        }
        cargarZonas();
        getServer().getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::tick, 40, 10);
        Bukkit.getScheduler().runTaskTimer(this, this::camaras, 1, 1);
        Bukkit.getScheduler().runTaskLater(this, () -> { for (String m : mundos) barreras(Bukkit.getWorld(m), false); }, 100);
        getLogger().info("Nave del Vacio: " + salas.size() + " salas en " + mundos);
    }

    @Override public void onDisable() { for (var p : new ArrayList<>(intros.keySet())) { var pl = Bukkit.getPlayer(p); if (pl != null) terminarIntro(pl, false); } }

    static double[] xyz(String s) { String[] p = s.split(","); double[] o = new double[p.length]; for (int i = 0; i < p.length; i++) o[i] = Double.parseDouble(p[i].trim()); return o; }
    boolean nave(World w) { return w != null && mundos.contains(w.getName()); }
    static boolean pelea(Player p) { return p.getGameMode() == GameMode.SURVIVAL || p.getGameMode() == GameMode.ADVENTURE; }
    Location loc(World w, double[] c, float yaw) { return new Location(w, c[0] + 0.5, c[1], c[2] + 0.5, yaw, 0); }
    /** Llegada de la sala mirando hacia su centro (la compuerta). */
    Location llegada(World w, Sala s) {
        Location l = loc(w, s.llegada(), 0);
        l.setDirection(new Vector(s.centro()[0] - s.llegada()[0], 0, s.centro()[2] - s.llegada()[2]));
        l.setPitch(0);
        return l;
    }
    static void msg(Player p, String s) { p.sendMessage(ChatColor.translateAlternateColorCodes('&', s)); }
    void consola(String c) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), c); }

    List<Entity> mobs(World w) {
        List<Entity> out = new ArrayList<>();
        for (Entity e : w.getEntities()) { var t = e.getScoreboardTags(); if (!e.isDead() && (t.contains("nave.mob") || t.contains("nave.jefe"))) out.add(e); }
        return out;
    }

    // ------------------------------------------------------------------------------------------ salas y oleadas
    void tick() {
        long now = System.currentTimeMillis();
        for (String name : mundos) {
            World w = Bukkit.getWorld(name);
            if (w == null) continue;
            Estado st = estado.computeIfAbsent(name, k -> new Estado());
            List<Player> ps = w.getPlayers().stream().filter(p -> pelea(p) && !intros.containsKey(p.getUniqueId())).toList();
            barra(w, st, ps);
            for (LivingEntity le : w.getLivingEntities()) if (!(le instanceof Player) && !le.isGlowing() && !le.getScoreboardTags().contains("nave.premio") && !(le instanceof ArmorStand)) le.setGlowing(true);
            if (ps.isEmpty()) {
                if (w.getPlayers().stream().noneMatch(p -> intros.containsKey(p.getUniqueId()))) reiniciar(w, st);
                continue;
            }
            Sala s = salas.get(st.sala);
            for (Player p : ps) if (fuera(p, s)) { p.teleport(llegada(w, s)); p.setFallDistance(0); msg(p, "&5El vacio te devuelve a la sala."); }
            mobsSala(w, st, ps);
            if (st.terminado) continue;
            if (st.oleada == 0) {
                if (st.cuando == 0) { st.cuando = now + 4000; titulo(ps, s.nombre(), "Sala " + (st.sala + 1) + "/" + salas.size()); }
                else if (now >= st.cuando) oleada(w, st, 1, ps.size());
                continue;
            }
            if (st.oleada == -1) { compuerta(w, st, ps, now); continue; }
            if (!mobs(w).isEmpty()) continue;
            if (st.cuando == 0) {
                if (st.oleada < s.oleadas().size()) { st.cuando = now + 4000; ps.forEach(p -> msg(p, "&dOleada &f" + st.oleada + "/" + s.oleadas().size() + " &dsuperada. Viene otra...")); }
                else if (st.sala == salas.size() - 1) ganar(w, st, s);
                else { st.oleada = -1; st.cuando = now + espera * 1000L; titulo(ps, "Compuerta abierta", "Pisala para seguir (o espera " + espera + " s)"); }
            } else if (now >= st.cuando) oleada(w, st, st.oleada + 1, ps.size());
        }
    }

    boolean fuera(Player p, Sala s) { return !enZona(p.getLocation(), salas.indexOf(s)); }

    // ------------------------------------------------------------------------------------------ zonas y barreras
    int zx0, zy0, zz0; int[][] zonas = new int[0][];   // [z][3x..3x+2] -> bits de las salas, y min y max del aire de adentro
    final List<int[]> tiras = new ArrayList<>();  // x0 x1 y z
    int tirasHash;

    List<String> recurso(String nombre) {
        try (var in = getResource(nombre)) {
            if (in == null) return List.of();
            return new String(in.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).lines().toList();
        } catch (java.io.IOException e) { return List.of(); }
    }

    void cargarZonas() {
        List<int[]> filas = new ArrayList<>();
        for (String l : recurso("nave_zonas.txt")) {
            if (l.startsWith("#")) { var m = java.util.regex.Pattern.compile("z desde (-?\\d+).*x desde (-?\\d+).*y desde (-?\\d+)").matcher(l); if (m.find()) { zz0 = Integer.parseInt(m.group(1)); zx0 = Integer.parseInt(m.group(2)); zy0 = Integer.parseInt(m.group(3)); } continue; }
            int[] f = new int[l.length() / 2];
            for (int i = 0; i < f.length; i++) f[i] = Integer.parseInt(l.substring(2 * i, 2 * i + 2), 16);
            filas.add(f);
        }
        zonas = filas.toArray(new int[0][]);
        List<String> b = recurso("nave_barreras.txt");
        for (String l : b) {
            if (l.isBlank() || l.startsWith("#")) continue;
            String[] p = l.trim().split("\\s+");
            tiras.add(new int[]{Integer.parseInt(p[0]), Integer.parseInt(p[1]), Integer.parseInt(p[2]), Integer.parseInt(p[3])});
        }
        tirasHash = String.join("\n", b).hashCode();
        getLogger().info("Zonas: " + zonas.length + " filas; barreras: " + tiras.size() + " tiras");
    }

    /** La columna de esa posicion tiene aire de adentro de la sala i (y no esta metido en un bloque). */
    boolean enZona(Location l, int i) {
        if (zonas.length == 0 || i < 0) return true;
        int z = l.getBlockZ() - zz0, x = l.getBlockX() - zx0;
        if (z < 0 || z >= zonas.length || x < 0 || 3 * x + 2 >= zonas[z].length) return false;
        int[] f = zonas[z]; double y = l.getY() - zy0;
        return (f[3 * x] >> i & 1) == 1 && y >= f[3 * x + 1] - 0.5 && y <= f[3 * x + 2] + 1 && !l.getBlock().getType().isSolid();
    }

    /** Pone las paredes de barrera (solo donde hay aire). Una vez por version de nave_barreras.txt, o forzado. */
    int barreras(World w, boolean forzar) {
        if (w == null || tiras.isEmpty()) return 0;
        var f = new java.io.File(getDataFolder(), "estado.yml");
        var est = org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(f);
        if (!forzar && est.getInt("barreras." + w.getName(), 0) == tirasHash) return 0;
        int n = 0;
        for (int[] t : tiras) for (int x = t[0]; x <= t[1]; x++) {
            var b = w.getBlockAt(x, t[2], t[3]);
            if (b.getType().isAir()) { b.setType(Material.BARRIER, false); n++; }
        }
        est.set("barreras." + w.getName(), tirasHash);
        try { est.save(f); } catch (java.io.IOException ex) { getLogger().warning("estado.yml: " + ex); }
        getLogger().info("Barreras de la nave en " + w.getName() + ": " + n + " bloques nuevos");
        return n;
    }

    /** Mobs: siempre contra el jugador mas cercano, y de vuelta a la sala si se salen (vex que atraviesan paredes). */
    void mobsSala(World w, Estado st, List<Player> ps) {
        Sala s = salas.get(st.sala);
        Random r = new Random();
        for (Entity e : mobs(w)) {
            if (!(e instanceof LivingEntity le)) continue;
            if (!enZona(le.getEyeLocation(), st.sala) && !enZona(le.getLocation(), st.sala) && !s.puntos().isEmpty()) {
                double[] pt = s.puntos().get(r.nextInt(s.puntos().size()));
                le.teleport(loc(w, pt, r.nextFloat() * 360));
            }
            if (le instanceof Mob m && !e.getScoreboardTags().contains("nave.ojo")) {
                var t = m.getTarget();
                if (!(t instanceof Player tp) || !ps.contains(tp) || tp.isDead()) objetivo(m, ps);
            }
        }
    }

    void oleada(World w, Estado st, int n, int jugadores) {
        Sala s = salas.get(st.sala);
        st.oleada = n; st.cuando = 0; st.maxVivos = 1;
        Map<String, Integer> def = s.oleadas().get(n - 1);
        double mult = 1 + extra * Math.max(0, jugadores - 2);
        Random r = new Random();
        int puestos = 0;
        for (var e : def.entrySet()) {
            String tipo = e.getKey();
            if (tipo.equals("jefe") || tipo.equals("minijefe")) {
                String id = tipo.equals("jefe") ? jefe : minijefe;
                spawnMM(w, id, s.centro(), tipo.equals("jefe") ? "nave.jefe" : "nave.mob");
                w.getPlayers().forEach(p -> msg(p, tipo.equals("jefe") ? "&5&lEl nucleo de la nave late..." : "&d&lEl Timonel del Vacio toma el mando."));
                continue;
            }
            int cant = (int) Math.ceil(e.getValue() * mult);
            for (int i = 0; i < cant; i++) {
                double[] pt = s.puntos().get(r.nextInt(s.puntos().size()));
                if (tipo.startsWith("mm:")) { spawnMM(w, tipo.substring(3), pt, "nave.mob"); continue; }
                Location at = loc(w, pt, r.nextFloat() * 360);
                Entity mob = w.spawnEntity(at, EntityType.valueOf(tipo.toUpperCase(Locale.ROOT)));
                mob.addScoreboardTag("nave.mob"); mob.setGlowing(true);
                if (mob instanceof Mob m) { m.setRemoveWhenFarAway(false); agresivo(m); }
                puestos++;
            }
        }
        int total = s.oleadas().size();
        if (!def.containsKey("jefe") && !def.containsKey("minijefe")) w.getPlayers().forEach(p -> msg(p, "&dOleada &f" + n + "/" + total + " &7(" + s.nombre() + ")"));
    }

    void objetivo(Mob m) { objetivo(m, m.getWorld().getPlayers().stream().filter(p -> pelea(p) && !intros.containsKey(p.getUniqueId())).toList()); }
    void objetivo(Mob m, List<Player> ps) {
        Player near = null; double best = Double.MAX_VALUE;
        for (Player p : ps) if (p.getLocation().distanceSquared(m.getLocation()) < best) { best = p.getLocation().distanceSquared(m.getLocation()); near = p; }
        if (near != null) m.setTarget(near);
    }

    /** Ven a los jugadores desde toda la sala y los persiguen (los endermans dejan de ser neutrales). */
    void agresivo(Mob m) {
        try { var a = m.getAttribute(org.bukkit.attribute.Attribute.FOLLOW_RANGE); if (a != null && a.getBaseValue() < 64) a.setBaseValue(64); } catch (Throwable ignored) {}
        if (m instanceof Enderman en) en.setScreaming(true);
        objetivo(m);
    }

    /** Aparece un mob de MythicMobs por consola y le pone la etiqueta (los que aparecieron ahi y no la tenian). */
    void spawnMM(World w, String id, double[] c, String tag) {
        Set<UUID> antes = new HashSet<>();
        for (Entity e : w.getEntities()) antes.add(e.getUniqueId());
        consola("mm mobs spawn " + id + " 1 " + w.getName() + "," + (c[0] + 0.5) + "," + c[1] + "," + (c[2] + 0.5));
        for (Entity e : w.getNearbyEntities(new Location(w, c[0] + 0.5, c[1], c[2] + 0.5), 4, 6, 4))
            if (!(e instanceof Player) && !antes.contains(e.getUniqueId())) { e.addScoreboardTag(tag); if (e instanceof Mob m) { m.setRemoveWhenFarAway(false); agresivo(m); } }
    }

    void compuerta(World w, Estado st, List<Player> ps, long now) {
        Sala s = salas.get(st.sala);
        Location c = loc(w, s.centro(), 0);
        w.spawnParticle(Particle.REVERSE_PORTAL, c.clone().add(0, 1, 0), 40, 0.6, 1.2, 0.6, 0.05);
        w.spawnParticle(Particle.END_ROD, c.clone().add(0, 0.2, 0), 12, 1.2, 0.05, 1.2, 0.01);
        w.spawnParticle(Particle.DUST, c.clone().add(0, 0.1, 0), 20, 1.4, 0.02, 1.4, new Particle.DustOptions(Color.fromRGB(0xC43BFF), 1.6f));
        boolean pisa = ps.stream().anyMatch(p -> p.getLocation().distanceSquared(c) < 2.6 * 2.6 && Math.abs(p.getY() - c.getY()) < 2);
        long falta = (st.cuando - now) / 1000;
        if (falta > 0 && falta <= 5) ps.forEach(p -> p.sendActionBar(net.kyori.adventure.text.Component.text("La compuerta te lleva en " + falta + "...", net.kyori.adventure.text.format.NamedTextColor.LIGHT_PURPLE)));
        if (!pisa && now < st.cuando) return;
        st.sala++; st.oleada = 0; st.cuando = 0;
        Sala sig = salas.get(st.sala);
        for (Player p : w.getPlayers()) {
            if (intros.containsKey(p.getUniqueId())) continue;
            p.teleport(llegada(w, sig));
            p.setFallDistance(0);
            p.playSound(p.getLocation(), Sound.ENTITY_ENDERMAN_TELEPORT, 1f, 0.6f);
        }
        for (Entity e : w.getEntities()) if (e instanceof Item || e instanceof AbstractArrow || e instanceof ExperienceOrb) e.remove();
    }

    void ganar(World w, Estado st, Sala s) {
        st.terminado = true;
        for (Entity e : w.getEntities()) if (e.getScoreboardTags().contains("nave.ojo") || "Cria del Vacio".equals(ChatColor.stripColor(e.getName()))) e.remove();
        consola("mazfin " + w.getName());
        double[] c = s.centro();
        consola("mm mobs spawn astral_nave_cofre 1 " + w.getName() + "," + (c[0] + 0.5) + "," + c[1] + "," + (c[2] + 0.5));
        consola("mm mobs spawn astral_nave_guia 1 " + w.getName() + "," + (c[0] + 3) + "," + c[1] + "," + (c[2] + 0.5));
        w.getPlayers().forEach(p -> msg(p, "&5&l¡La Nave del Vacio es suya! &7El cofre los espera en la Palma."));
    }

    void reiniciar(World w, Estado st) {
        if (st.sala == 0 && st.oleada == 0 && st.cuando == 0 && !st.terminado && mobs(w).isEmpty()) return;
        for (Entity e : w.getEntities()) {
            var t = e.getScoreboardTags();
            if (t.contains("nave.mob") || t.contains("nave.jefe") || t.contains("nave.ojo") || t.contains("nave.premio") || e instanceof Item || e instanceof AbstractArrow
                || (e instanceof Mob && !(e instanceof Player))) e.remove();
        }
        estado.put(w.getName(), new Estado());
    }

    void barra(World w, Estado st, List<Player> ps) {
        var bar = barras.computeIfAbsent(w.getName(), k -> Bukkit.createBossBar("Nave del Vacio", BarColor.PURPLE, BarStyle.SOLID));
        for (Player p : new ArrayList<>(bar.getPlayers())) if (!ps.contains(p)) bar.removePlayer(p);
        if (ps.isEmpty()) { bar.setVisible(false); return; }
        for (Player p : ps) if (!bar.getPlayers().contains(p)) bar.addPlayer(p);
        bar.setVisible(true);
        Sala s = salas.get(st.sala);
        String sala = s.nombre() + " (" + (st.sala + 1) + "/" + salas.size() + ")";
        int vivos = mobs(w).size();
        if (st.terminado) { bar.setTitle("Nave del Vacio conquistada"); bar.setProgress(1); return; }
        if (st.oleada == 0) { bar.setTitle(sala + " - preparate"); bar.setProgress(1); return; }
        if (st.oleada == -1) { bar.setTitle(sala + " - compuerta abierta"); bar.setProgress(1); return; }
        st.maxVivos = Math.max(st.maxVivos, vivos);
        boolean jefeSala = s.oleadas().get(st.oleada - 1).containsKey("jefe");
        bar.setTitle(jefeSala ? "Jefe: Capitan del Vacio" : sala + " - oleada " + st.oleada + "/" + s.oleadas().size() + " - " + vivos + " restantes");
        bar.setProgress(Math.max(0, Math.min(1, vivos / (double) st.maxVivos)));
    }

    void titulo(List<Player> ps, String a, String b) {
        for (Player p : ps) p.showTitle(net.kyori.adventure.title.Title.title(
            net.kyori.adventure.text.Component.text(a, net.kyori.adventure.text.format.NamedTextColor.LIGHT_PURPLE),
            net.kyori.adventure.text.Component.text(b, net.kyori.adventure.text.format.NamedTextColor.GRAY)));
    }

    // ------------------------------------------------------------------------------------------ escudo de los Ojos
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true) public void escudo(EntityDamageEvent e) {
        if (!e.getEntity().getScoreboardTags().contains("nave.jefe") || !nave(e.getEntity().getWorld())) return;
        boolean ojos = false;
        for (Entity o : e.getEntity().getWorld().getEntities()) if (!o.isDead() && o.getScoreboardTags().contains("nave.ojo")) { ojos = true; break; }
        if (!ojos) return;
        e.setDamage(e.getDamage() * escudo);
        if (e instanceof EntityDamageByEntityEvent ev && ev.getDamager() instanceof Player p)
            p.sendActionBar(net.kyori.adventure.text.Component.text("Los Ojos Vigias protegen al Capitan: rompelos", net.kyori.adventure.text.format.NamedTextColor.GREEN));
    }

    // Nada se rompe ni se pone; sin perlas ni coros (WorldGuard tambien lo bloquea).
    boolean constructor(Player p) { return p.isOp() && p.getGameMode() == GameMode.CREATIVE; }
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void romper(BlockBreakEvent e) { if (nave(e.getBlock().getWorld()) && !constructor(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true) public void poner(BlockPlaceEvent e) { if (nave(e.getBlock().getWorld()) && !constructor(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(ignoreCancelled = true) public void perla(PlayerTeleportEvent e) {
        if (nave(e.getTo().getWorld()) && (e.getCause() == PlayerTeleportEvent.TeleportCause.ENDER_PEARL || e.getCause() == PlayerTeleportEvent.TeleportCause.CONSUMABLE_EFFECT)) e.setCancelled(true);
    }
    // Sin perlas ni coros: no se tiran, no se comen y no aparecen en el piso (drops de endermans y otros).
    static boolean prohibido(org.bukkit.inventory.ItemStack i) { return i != null && (i.getType() == Material.ENDER_PEARL || i.getType() == Material.CHORUS_FRUIT); }
    @EventHandler(ignoreCancelled = true) public void tirarPerla(ProjectileLaunchEvent e) {
        if (e.getEntity() instanceof EnderPearl && nave(e.getEntity().getWorld())) e.setCancelled(true);
    }
    @EventHandler(ignoreCancelled = true) public void comerCoro(PlayerItemConsumeEvent e) {
        if (nave(e.getPlayer().getWorld()) && prohibido(e.getItem())) e.setCancelled(true);
    }
    @EventHandler public void sinDrops(EntityDeathEvent e) {
        if (nave(e.getEntity().getWorld()) && !(e.getEntity() instanceof Player)) e.getDrops().removeIf(AstralNave::prohibido);
    }
    @EventHandler(ignoreCancelled = true) public void sinItem(ItemSpawnEvent e) {
        if (nave(e.getEntity().getWorld()) && prohibido(e.getEntity().getItemStack())) e.setCancelled(true);
    }
    // Shulkers y cofres del mapa: no se abren (son decoracion).
    @EventHandler(priority = EventPriority.HIGH) public void abrir(PlayerInteractEvent e) {
        var b = e.getClickedBlock();
        if (b == null || e.getAction() != org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK || !nave(b.getWorld()) || constructor(e.getPlayer())) return;
        if (b.getType().name().endsWith("SHULKER_BOX") || b.getState(false) instanceof org.bukkit.block.Container) e.setUseInteractedBlock(Event.Result.DENY);
    }
    @EventHandler(ignoreCancelled = true) public void abrirInv(org.bukkit.event.inventory.InventoryOpenEvent e) {
        if (!(e.getPlayer() instanceof Player p) || !nave(p.getWorld()) || constructor(p)) return;
        var h = e.getInventory().getHolder(false);
        if (h instanceof org.bukkit.block.Container || h instanceof org.bukkit.block.DoubleChest) e.setCancelled(true);
    }
    // Endermans de las oleadas: no se teletransportan solos (se irian al casco).
    @EventHandler(ignoreCancelled = true) public void enderTp(EntityTeleportEvent e) {
        if (e.getEntity() instanceof Enderman && nave(e.getEntity().getWorld())) e.setCancelled(true);
    }

    // ------------------------------------------------------------------------------------------ vista desde afuera
    /** Recorrido de la camara alrededor de la nave (puntos y adonde mira), en coordenadas del mundo. */
    // 23/11: sin camara. Antes el jugador miraba por un soporte invisible, pero el server carga y manda el mapa
    // alrededor del JUGADOR (que quedaba lejos): el dueno veia solo estrellas. Ahora el jugador mismo (espectador)
    // recorre la ruta, bien cerca de la nave (view-distance del server = 8 chunks).
    final class Intro {
        int t = -50; final GameMode antes;   // 2,5 s quieto en el primer punto: que llegue el mapa
        Intro(GameMode g) { antes = g; }
    }
    static final int INTRO_TICKS = 300;   // 15 segundos
    double[][] ruta() {
        List<double[]> pts = new ArrayList<>();
        for (Object o : getConfig().getStringList("intro.ruta")) pts.add(xyz(o.toString()));
        return pts.toArray(new double[0][]);
    }

    static double cr(double p0, double p1, double p2, double p3, double t) {
        return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t);
    }

    /** Punto de la ruta (Catmull-Rom) para f en 0..1: x, y, z, mira-x, mira-y, mira-z. */
    static double[] punto(double[][] r, double f) {
        int n = r.length - 1; double u = Math.min(f, 0.9999) * n; int i = (int) u; double t = u - i;
        double[] a = r[Math.max(0, i - 1)], b = r[i], c = r[Math.min(n, i + 1)], d = r[Math.min(n, i + 2)];
        double[] o = new double[6];
        for (int k = 0; k < 6; k++) o[k] = cr(a[k], b[k], c[k], d[k], t);
        return o;
    }

    void empezarIntro(Player p) {
        if (intros.containsKey(p.getUniqueId()) || !getConfig().getBoolean("intro.activa", true)) return;
        double[][] r = ruta();
        if (r.length < 2) return;
        World w = p.getWorld();
        double[] o = punto(r, 0);
        Location at = mirar(new Location(w, o[0], o[1], o[2]), o);
        GameMode antes = p.getGameMode() == GameMode.SPECTATOR ? GameMode.SURVIVAL : p.getGameMode();
        p.getPersistentDataContainer().set(introKey, PersistentDataType.STRING, antes.name());
        intros.put(p.getUniqueId(), new Intro(antes));
        try { p.setSendViewDistance(Math.max(8, getConfig().getInt("intro.distancia-vista", 14))); } catch (Throwable ignored) {}
        p.setGameMode(GameMode.SPECTATOR);
        cargarNave(w, true);
        p.teleport(at);
        // Afuera es de noche y el casco no tiene luces: sin esto se ve negro contra el cielo (23/11).
        p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION, INTRO_TICKS + 60, 0, false, false, false));
        p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1f, 0.5f);
        titulo(List.of(p), "Nave del Vacio", "Agachate para saltear");
    }

    static Location mirar(Location l, double[] o) {
        Vector v = new Vector(o[3] - o[0], o[4] - o[1], o[5] - o[2]);
        l.setDirection(v);
        return l;
    }

    void camaras() {
        if (intros.isEmpty()) return;
        double[][] r = ruta();
        for (var en : new ArrayList<>(intros.entrySet())) {
            Player p = Bukkit.getPlayer(en.getKey());
            Intro in = en.getValue();
            if (p == null || !nave(p.getWorld())) { if (p != null) terminarIntro(p, false); else intros.remove(en.getKey()); continue; }
            in.t++;
            if (in.t >= INTRO_TICKS) { terminarIntro(p, true); continue; }
            double[] o = punto(r, Math.max(0, in.t) / (double) INTRO_TICKS);
            if (p.getGameMode() != GameMode.SPECTATOR) p.setGameMode(GameMode.SPECTATOR);
            p.teleport(mirar(new Location(p.getWorld(), o[0], o[1], o[2]), o));
            if (in.t == INTRO_TICKS - 30) titulo(List.of(p), "", "Entrando al Hangar...");
        }
    }

    /** Toda la nave cargada en el server mientras alguien mira la vista (si no, el mapa llega tarde: 23/11). */
    void cargarNave(World w, boolean si) {
        if (w == null) return;
        if (!si) for (UUID u : intros.keySet()) { Player o = Bukkit.getPlayer(u); if (o != null && o.getWorld().equals(w)) return; }
        for (int cx = -5; cx <= 5; cx++) for (int cz = -7; cz <= 6; cz++) {
            if (si) w.addPluginChunkTicket(cx, cz, this); else w.removePluginChunkTicket(cx, cz, this);
        }
    }

    void terminarIntro(Player p, boolean llevar) {
        Intro in = intros.remove(p.getUniqueId());
        for (String m : mundos) cargarNave(Bukkit.getWorld(m), false);
        var nv = p.getPotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION);
        if (nv != null && !nv.hasParticles() && nv.getDuration() <= INTRO_TICKS + 60) p.removePotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION);
        String g = p.getPersistentDataContainer().get(introKey, PersistentDataType.STRING);
        p.getPersistentDataContainer().remove(introKey);
        GameMode modo = in != null ? in.antes : (g != null ? GameMode.valueOf(g) : GameMode.SURVIVAL);
        try { p.setSendViewDistance(-1); } catch (Throwable ignored) {}
        if (llevar && nave(p.getWorld())) {
            Estado st = estado.computeIfAbsent(p.getWorld().getName(), k -> new Estado());
            p.teleport(llegada(p.getWorld(), salas.get(st.sala)));
            p.setFallDistance(0);
        }
        p.setGameMode(modo);
    }

    @EventHandler public void entra(PlayerChangedWorldEvent e) {
        Player p = e.getPlayer();
        if (!nave(p.getWorld())) { if (intros.containsKey(p.getUniqueId())) terminarIntro(p, false); return; }
        if (!abierta && !p.hasPermission("astral.nave.admin")) {   // cerrada hasta el evento (los OP pueden probar)
            Bukkit.getScheduler().runTaskLater(this, () -> {
                if (!p.isOnline() || !nave(p.getWorld())) return;
                World lobby = Bukkit.getWorld("lobby") != null ? Bukkit.getWorld("lobby") : Bukkit.getWorlds().get(0);
                p.teleport(lobby.getSpawnLocation());
                msg(p, "&dLa Nave del Vacio todavia no abrio. &7Se abre con el evento del End.");
            }, 2);
            return;
        }
        Bukkit.getScheduler().runTaskLater(this, () -> { if (p.isOnline() && nave(p.getWorld())) empezarIntro(p); }, 10);
    }

    // Se desconecto durante la vista: al volver recupera su modo de juego y va a la sala del grupo.
    @EventHandler public void vuelve(PlayerJoinEvent e) {
        Player p = e.getPlayer();
        if (!p.getPersistentDataContainer().has(introKey, PersistentDataType.STRING)) return;
        Bukkit.getScheduler().runTaskLater(this, () -> terminarIntro(p, true), 5);
    }
    @EventHandler public void sale(PlayerQuitEvent e) {
        if (intros.remove(e.getPlayer().getUniqueId()) != null) for (String m : mundos) cargarNave(Bukkit.getWorld(m), false);
    }
    // Agacharse saltea la vista.
    @EventHandler public void saltear(PlayerToggleSneakEvent e) {
        Intro in = intros.get(e.getPlayer().getUniqueId());
        if (in != null && e.isSneaking() && in.t > -25) terminarIntro(e.getPlayer(), true);
    }
    // Durante la vista no se puede mover por su cuenta (la ruta lo lleva).
    @EventHandler(ignoreCancelled = true) public void quieto(PlayerMoveEvent e) {
        if (intros.containsKey(e.getPlayer().getUniqueId()) && e.getFrom().distanceSquared(e.getTo()) > 0
            && !(e instanceof PlayerTeleportEvent)) e.setTo(e.getFrom().setDirection(e.getTo().getDirection()));
    }

    // ------------------------------------------------------------------------------------------ comandos de admin
    @Override public boolean onCommand(CommandSender s, Command c, String l, String[] a) {
        if (a.length > 0 && (a[0].equals("abrir") || a[0].equals("cerrar"))) {
            abierta = a[0].equals("abrir");
            var est = new org.bukkit.configuration.file.YamlConfiguration(); est.set("abierta", abierta);
            try { est.save(new java.io.File(getDataFolder(), "estado.yml")); } catch (java.io.IOException ex) { getLogger().warning("No se pudo guardar estado.yml: " + ex); }
            consola("lp group default permission set astral.nave.abierta " + abierta);
            s.sendMessage("Nave del Vacio " + (abierta ? "ABIERTA: aparece en Portales (pagina 2)." : "CERRADA."));
            if (abierta) for (Player p : Bukkit.getOnlinePlayers()) msg(p, "&5&l✦ &d&lLa Nave del Vacio abrio sus compuertas. &7Entra desde &fPortales&7 (pagina 2).");
            return true;
        }
        if (a.length == 0) { s.sendMessage("/nave abrir | cerrar | estado | saltar <mundo> | sala <mundo> <n> | intro <jugador> | reiniciar <mundo> | barreras"); return true; }
        switch (a[0]) {
            case "estado" -> { s.sendMessage("Nave del Vacio: " + (abierta ? "ABIERTA" : "cerrada (/nave abrir)"));
                for (String m : mundos) { var st = estado.get(m); s.sendMessage(m + ": " + (st == null ? "libre" : "sala " + (st.sala + 1) + " oleada " + st.oleada + (st.terminado ? " (ganada)" : ""))); } }
            case "saltar", "sala" -> {
                World w = a.length > 1 ? Bukkit.getWorld(a[1]) : null;
                if (!nave(w)) { s.sendMessage("Mundo de la nave invalido"); return true; }
                Estado st = estado.computeIfAbsent(w.getName(), k -> new Estado());
                for (Entity e : mobs(w)) e.remove();
                int n = a[0].equals("sala") && a.length > 2 ? Integer.parseInt(a[2]) - 1 : Math.min(salas.size() - 1, st.sala + 1);
                st.sala = Math.max(0, Math.min(salas.size() - 1, n)); st.oleada = 0; st.cuando = 0; st.terminado = false;
                for (Player p : w.getPlayers()) if (!intros.containsKey(p.getUniqueId())) p.teleport(llegada(w, salas.get(st.sala)));
                s.sendMessage("Sala " + (st.sala + 1) + ": " + salas.get(st.sala).nombre());
            }
            case "intro" -> { Player p = a.length > 1 ? Bukkit.getPlayer(a[1]) : (s instanceof Player pp ? pp : null); if (p != null && nave(p.getWorld())) empezarIntro(p); else s.sendMessage("El jugador tiene que estar en la nave"); }
            case "reiniciar" -> { World w = a.length > 1 ? Bukkit.getWorld(a[1]) : null; if (nave(w)) { var st = estado.computeIfAbsent(w.getName(), k -> new Estado()); st.terminado = true; reiniciar(w, st); estado.put(w.getName(), new Estado()); s.sendMessage("Reiniciada " + w.getName()); } }
            case "barreras" -> { int n = 0; for (String m : mundos) n += barreras(Bukkit.getWorld(m), true); s.sendMessage("Barreras puestas: " + n + " bloques nuevos"); }
            default -> s.sendMessage("?");
        }
        return true;
    }
}
