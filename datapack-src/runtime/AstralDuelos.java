package astral;

import java.util.*;
import java.time.*;
import java.time.temporal.TemporalAdjusters;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.*;
import org.bukkit.plugin.java.JavaPlugin;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import com.meteordevelopments.duels.api.Duels;
import com.meteordevelopments.duels.api.arena.Arena;
import com.meteordevelopments.duels.api.event.match.*;

/** Interfaz Astral. Duels sigue siendo el unico propietario del combate/inventario. */
public final class AstralDuelos extends JavaPlugin implements Listener {
    public Duels duels;
    public final Map<UUID, Pedido> pedidos = new LinkedHashMap<>();
    public final Map<UUID, Long> enviados = new HashMap<>();
    public final Map<UUID, Resultado> resultados = new HashMap<>();
    public final Map<UUID, Long> inicios = new HashMap<>();
    static final List<String> ARENAS = List.of("Astral", "TFT1", "TFT2", "TFT3");
    public record Pedido(UUID id, UUID de, UUID para, String arena, long vence) {}
    public record Resultado(UUID rival, String arena, String texto) {}
    static final class Ventana implements InventoryHolder {
        Inventory inv;
        public final Map<Integer, Runnable> acciones = new HashMap<>();
        public Inventory getInventory() { return inv; }
    }
    @Override public void onEnable() {
        duels = (Duels) Bukkit.getPluginManager().getPlugin("Duels");
        Bukkit.getPluginManager().registerEvents(this, this);
        Bukkit.getScheduler().runTaskTimer(this, this::vencer, 20, 20);
    }
    @Override public void onDisable() {
        for (Player p : Bukkit.getOnlinePlayers())
            if (p.getOpenInventory().getTopInventory().getHolder() instanceof Ventana) p.closeInventory();
        saveConfig();
    }
    static String color(String s) { return ChatColor.translateAlternateColorCodes('&', s); }
    void aviso(Player p, String s) { if (p != null && p.isOnline()) p.sendMessage(color(s)); }
    String nombre(UUID id) { var u = duels.getUserManager().get(id); return u == null ? "Jugador" : u.getName(); }
    boolean libre(Arena a) {
        return a != null && !a.isRemoved() && !a.isDisabled() && !a.isUsed()
            && a.getPosition(1) != null && a.getPosition(2) != null
            && a.getPosition(1).getWorld() != null && a.getPosition(2).getWorld() != null;
    }
    public Arena elegir(String s) {
        if (s.equals("Cualquiera")) return ARENAS.stream().map(duels.getArenaManager()::get).filter(this::libre).findFirst().orElse(null);
        return ARENAS.contains(s) && libre(duels.getArenaManager().get(s)) ? duels.getArenaManager().get(s) : null;
    }
    String ocupado(Player p) {
        if (p == null || !p.isOnline()) return "Desconectado";
        if (duels.getArenaManager().isInMatch(p)) return "En duelo";
        if (duels.getQueueManager().isInQueue(p)) return "En cola";
        if (p.isDead() || p.isInsideVehicle() || p.getGameMode() != GameMode.SURVIVAL) return "Ocupado";
        if (!Set.of("world", "lobby", "arena", "arenas_tft").contains(p.getWorld().getName())) return "En una actividad";
        var u = duels.getUserManager().get(p);
        if (u == null || !duels.getUserManager().isLoaded()) return "Cargando datos";
        if (!u.canRequest()) return "Pedidos desactivados";
        if (u.isInDuelCooldown()) return "Descansando";
        if (p.getMetadata("vanished").stream().anyMatch(v -> v.asBoolean())) return "Ocupado";
        return null;
    }
    boolean disponibles(Player a, Player b) {
        var config = duels.getConfig();
        if (config.getBoolean("request.use-own-inventory.drop-inventory-items", true)
                || config.getBoolean("request.item-betting.enabled", true)
                || config.getBoolean("request.money-betting.enabled", true)) {
            aviso(a, "&cDuelos no esta configurado sin apuestas y sin perdida de items. Avisa a un admin.");
            return false;
        }
        if (a == b || ocupado(a) != null || ocupado(b) != null || !a.canSee(b) || !b.canSee(a)) {
            aviso(a, "&cNo se puede iniciar ahora: alguno esta ocupado o desconectado."); return false;
        }
        return true;
    }
    // Ventanas ilustradas (arte de Gemini, duelos_party_ui.py): titulo = glifos del pack, botones = items.
    final Properties titulos = new Properties();
    static final int[] DESAFIAR = {0, 1, 2, 9, 10, 11, 18, 19, 20, 27, 28, 29}, PEDIDOS = {3, 4, 5, 12, 13, 14},
        DATOS = {6, 7, 8, 15, 16, 17}, RANKING = {21, 22, 23, 30, 31, 32}, SALIR = {24, 25, 26, 33, 34, 35},
        IZQ = {19, 20, 21, 28, 29, 30}, DER = {23, 24, 25, 32, 33, 34};
    static final int CENTRO = 13;
    String titulo(String clave, String respaldo) {
        if (titulos.isEmpty()) try (var in = getResource("titulos-ui.properties")) { if (in != null) titulos.load(in); } catch (Exception ignored) {}
        return titulos.getProperty(clave, color("&8&lAstral &6| &8" + respaldo));
    }
    Ventana ventana(Player p, String clave, String respaldo) {
        Ventana v = new Ventana(); v.inv = Bukkit.createInventory(v, 54, titulo(clave, respaldo));
        boton(v, 45, Material.ARROW, "&fVolver a Duelos", "icon_back", () -> menu(p));
        boton(v, 53, Material.BARRIER, "&cCerrar", "icon_close", p::closeInventory);
        return v;
    }
    ItemStack item(Material m, String titulo, String modelo, String... lore) {
        ItemStack it = new ItemStack(m); ItemMeta meta = it.getItemMeta();
        meta.setDisplayName(color(titulo)); meta.setLore(Arrays.stream(lore).map(AstralDuelos::color).toList());
        if (modelo != null) meta.setItemModel(NamespacedKey.fromString(modelo.contains(":") ? modelo : "astral:menu/" + modelo));
        it.setItemMeta(meta); return it;
    }
    void boton(Ventana v, int slot, Material m, String titulo, String modelo, Runnable r, String... lore) {
        v.inv.setItem(slot, item(m, titulo, modelo, lore)); if (r != null) v.acciones.put(slot, r); else v.acciones.remove(slot);
    }
    /** Boton grande de Gemini partido en casillas: astral:duelparty/<nombre>_<i>. */
    void tarjeta(Ventana v, int[] slots, String nombre, Runnable r, String titulo, String... lore) {
        for (int i = 0; i < slots.length; i++) boton(v, slots[i], Material.PAPER, titulo, "astral:duelparty/" + nombre + "_" + i, r, lore);
    }
    public List<Pedido> recibidos(Player p) { vencer(); return pedidos.values().stream().filter(r -> r.para.equals(p.getUniqueId())).toList(); }
    void menu(Player p) {
        if (duels.getArenaManager().isInMatch(p)) { rendirse(p); return; }
        Ventana v = ventana(p, "duelos.menu.sin_perdida_de_items", "Duelos"); int n = recibidos(p).size();
        tarjeta(v, DESAFIAR, "desafiar", () -> jugadores(p, 0), "&c&lDesafiar", "&7Elegi rival y arena.", "&7Sin apuestas ni perdida de items.");
        tarjeta(v, PEDIDOS, "pedidos", () -> recibidosMenu(p, 0), "&e&lPedidos recibidos (" + n + ")", "&7Aceptar o rechazar desafios.");
        if (n > 0) v.inv.getItem(PEDIDOS[2]).setAmount(Math.min(n, 64));
        tarjeta(v, DATOS, "estadisticas", () -> estadisticas(p), "&bMis estadisticas", "&7Victorias, derrotas y racha.");
        tarjeta(v, RANKING, "ranking", () -> ranking(p, false), "&6Ranking de duelos", "&7Total y semanal.");
        tarjeta(v, SALIR, "salir_cola", () -> salir(p), "&cSalir de la cola", "&7Tambien cancela tus pedidos.");
        boton(v, 45, Material.ARROW, "&fVolver a Arenas", "icon_back", () -> { p.closeInventory(); Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "dm open arenas " + p.getName()); });
        p.openInventory(v.inv);
    }
    void rendirse(Player p) {
        Ventana v = ventana(p, "duelos.dialogo.rendirse", "Rendirse");
        boton(v, CENTRO, Material.WHITE_BANNER, "&fRendirse", null, null, "&7Cuenta como derrota.", "&7Conservas tus items.");
        tarjeta(v, IZQ, "rendirse", () -> { p.closeInventory(); p.performCommand("duels:duel leave"); }, "&c&lRendirme", "&7Termina el duelo como derrota.");
        tarjeta(v, DER, "seguir", p::closeInventory, "&a&lSeguir peleando");
        v.acciones.remove(45); v.inv.setItem(45, null);
        p.openInventory(v.inv);
    }
    static int casilla(int i) { return i; }
    void paginas(Ventana v, Player p, int pagina, int total, java.util.function.IntConsumer abrir) {
        if (pagina > 0) boton(v, 47, Material.ARROW, "&fAnterior", "icon_back", () -> abrir.accept(pagina - 1));
        if ((pagina + 1) * 36 < total) boton(v, 51, Material.ARROW, "&fSiguiente", null, () -> abrir.accept(pagina + 1));
    }
    public void jugadores(Player p, int pagina) {
        var lista = Bukkit.getOnlinePlayers().stream().filter(t -> t != p && p.canSee(t)).sorted(Comparator.comparing(Player::getName)).toList();
        int pag = Math.max(0, Math.min(pagina, Math.max(0, (lista.size() - 1) / 36)));
        Ventana v = ventana(p, "duelos.lista.elegi_a_tu_rival", "Desafiar");
        for (int i = pag * 36; i < Math.min(lista.size(), (pag + 1) * 36); i++) {
            Player t = lista.get(i); String estado = ocupado(t); int slot = casilla(i % 36);
            boton(v, slot, Material.PLAYER_HEAD, "&e" + t.getName(), null, () -> { if (disponibles(p, t)) arenas(p, t.getUniqueId()); },
                estado == null ? "&aDisponible · clic para desafiar" : "&c" + estado);
            var head = v.inv.getItem(slot); var meta = (SkullMeta) head.getItemMeta(); meta.setOwningPlayer(t); head.setItemMeta(meta);
        }
        if (lista.isEmpty()) boton(v, 13, Material.BARRIER, "&7No hay otros jugadores conectados", null, null);
        paginas(v, p, pag, lista.size(), n -> jugadores(p, n)); p.openInventory(v.inv);
    }
    void arenas(Player p, UUID rival) {
        Ventana v = ventana(p, "duelos.lista.elegi_la_arena", "Elegi la arena");
        for (int i = 0; i < ARENAS.size(); i++) {
            String a = ARENAS.get(i); boolean ok = libre(duels.getArenaManager().get(a));
            boton(v, 10 + i * 2, Material.DIAMOND_SWORD, "&6" + a, "icon_duelos", () -> confirmar(p, rival, a), ok ? "&aLibre" : "&cOcupada / no disponible");
        }
        boton(v, 22, Material.ENDER_PEARL, "&dCualquiera", null, () -> confirmar(p, rival, "Cualquiera"), "&7La primera libre al aceptar.");
        boton(v, 45, Material.ARROW, "&fVolver", "icon_back", () -> jugadores(p, 0));
        p.openInventory(v.inv);
    }
    void confirmar(Player p, UUID rival, String arena) {
        Ventana v = ventana(p, "duelos.dialogo.confirmar_desafio", "Confirmar desafio");
        boton(v, CENTRO, Material.DIAMOND_SWORD, "&e" + nombre(rival) + " · " + arena, "icon_duelos", null, "&7El pedido dura 60 segundos.", "&7Sin apuestas. Conservas tus items.");
        tarjeta(v, IZQ, "enviar", () -> enviar(p, Bukkit.getPlayer(rival), arena), "&a&lEnviar pedido", "&7A " + nombre(rival) + " · " + arena);
        tarjeta(v, DER, "cancelar", () -> arenas(p, rival), "&c&lCancelar", "&7Volver a elegir arena");
        p.openInventory(v.inv);
    }
    public void enviar(Player a, Player b, String arena) {
        vencer(); if (!disponibles(a, b)) return;
        if (elegir(arena) == null) { aviso(a, "&cNo hay una arena libre. Elegi otra."); return; }
        long ahora = System.currentTimeMillis();
        if (ahora - enviados.getOrDefault(a.getUniqueId(), 0L) < 3000) { aviso(a, "&eEspera un momento antes de enviar otro pedido."); return; }
        if (pedidos.values().stream().anyMatch(r -> r.de.equals(a.getUniqueId()) && r.para.equals(b.getUniqueId()))) { aviso(a, "&eYa tenes un pedido pendiente para ese jugador."); return; }
        if (pedidos.values().stream().filter(r -> r.de.equals(a.getUniqueId())).count() >= 5 || recibidos(b).size() >= 20) { aviso(a, "&cHay demasiados pedidos pendientes."); return; }
        Pedido r = new Pedido(UUID.randomUUID(), a.getUniqueId(), b.getUniqueId(), arena, ahora + 60000);
        pedidos.put(r.id, r); enviados.put(a.getUniqueId(), ahora); a.closeInventory();
        aviso(a, "&aPedido enviado a " + b.getName() + " · " + arena + ". Vence en 60 s.");
        aviso(b, "&6" + a.getName() + " te desafio · " + arena + " · 60 s");
        b.sendMessage(Component.text("[Aceptar] ").color(net.kyori.adventure.text.format.NamedTextColor.GREEN).clickEvent(ClickEvent.runCommand("/duelos aceptar " + r.id))
            .append(Component.text("[Rechazar]").color(net.kyori.adventure.text.format.NamedTextColor.RED).clickEvent(ClickEvent.runCommand("/duelos rechazar " + r.id))));
        b.sendTitle(color("&6Nuevo desafio"), a.getName() + " · " + arena, 5, 50, 10);
        b.playSound(b.getLocation(), Sound.BLOCK_NOTE_BLOCK_PLING, 0.8f, 1.3f);
    }
    void recibidosMenu(Player p, int pagina) {
        var lista = recibidos(p); int pag = Math.max(0, Math.min(pagina, Math.max(0, (lista.size() - 1) / 36)));
        Ventana v = ventana(p, "duelos.lista.pedidos_recibidos", "Pedidos recibidos");
        for (int i = pag * 36; i < Math.min(lista.size(), (pag + 1) * 36); i++) {
            Pedido r = lista.get(i);
            boton(v, casilla(i % 36), Material.PAPER, "&e" + nombre(r.de), null, () -> pedidoMenu(p, r), "&7Arena: " + r.arena, "&7Vence en " + Math.max(0, (r.vence - System.currentTimeMillis()) / 1000) + " s", "&7Clic: aceptar o rechazar.");
        }
        if (lista.isEmpty()) boton(v, 13, Material.BOOK, "&7No tenes pedidos pendientes", null, null);
        paginas(v, p, pag, lista.size(), n -> recibidosMenu(p, n)); p.openInventory(v.inv);
    }
    void pedidoMenu(Player p, Pedido r) {
        Ventana v = ventana(p, "duelos.dialogo.responder_desafio", "Responder desafio");
        boton(v, CENTRO, Material.PLAYER_HEAD, "&e" + nombre(r.de) + " · " + r.arena, null, null, "&7Te desafio a un duelo.");
        Player de = Bukkit.getPlayer(r.de);
        if (de != null) { var head = v.inv.getItem(CENTRO); var meta = (SkullMeta) head.getItemMeta(); meta.setOwningPlayer(de); head.setItemMeta(meta); }
        tarjeta(v, IZQ, "aceptar", () -> responder(p, r.id, true), "&a&lAceptar", "&7Empieza el duelo");
        tarjeta(v, DER, "rechazar", () -> responder(p, r.id, false), "&c&lRechazar");
        boton(v, 45, Material.ARROW, "&fVolver", "icon_back", () -> recibidosMenu(p, 0));
        p.openInventory(v.inv);
    }
    void responder(Player p, UUID id, boolean aceptar) {
        vencer(); Pedido r = pedidos.get(id);
        if (r == null || !r.para.equals(p.getUniqueId())) { aviso(p, "&cEse pedido ya no esta disponible."); return; }
        if (!aceptar) { pedidos.remove(id); aviso(Bukkit.getPlayer(r.de), "&e" + p.getName() + " rechazo el desafio."); recibidosMenu(p, 0); return; }
        Player a = Bukkit.getPlayer(r.de); if (!disponibles(p, a)) return;
        Arena arena = elegir(r.arena);
        if (arena == null) { aviso(p, "&cLa arena esta ocupada. Podes intentar antes de que venza el pedido."); return; }
        // El comando documentado de Duels inicia con inventario propio, bet=0 y sin GUI.
        // Solo se despacha tras validar ambos participantes y el consentimiento del destinatario.
        pedidos.remove(id); a.closeInventory(); p.closeInventory();
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "duels:duels start " + a.getName() + " " + p.getName() + " own_inventory " + arena.getName());
        Bukkit.getScheduler().runTaskLater(this, () -> {
            if (!duels.getArenaManager().isInMatch(a) || !duels.getArenaManager().isInMatch(p)) {
                aviso(a, "&cDuels no pudo iniciar. Volve a enviar el pedido."); aviso(p, "&cDuels no pudo iniciar el duelo.");
            }
        }, 10);
    }
    public void vencer() {
        long ahora = System.currentTimeMillis();
        for (Pedido r : new ArrayList<>(pedidos.values())) if (r.vence <= ahora) {
            pedidos.remove(r.id); aviso(Bukkit.getPlayer(r.de), "&7Vencio tu desafio a " + nombre(r.para) + "."); aviso(Bukkit.getPlayer(r.para), "&7Vencio el desafio de " + nombre(r.de) + ".");
        }
    }
    void quitar(UUID id) { pedidos.values().removeIf(r -> r.de.equals(id) || r.para.equals(id)); }
    void salir(Player p) {
        p.closeInventory(); quitar(p.getUniqueId());
        if (duels.getQueueManager().isInQueue(p)) { duels.getQueueManager().removeFromQueue(p); aviso(p, "&eSaliste de la cola."); }
        else if (duels.getArenaManager().isInMatch(p)) p.performCommand("duels:duel leave");
        else aviso(p, "&eNo estas en cola ni en duelo. Se cancelaron tus pedidos.");
    }
    public String semana() { return LocalDate.now(ZoneId.of("America/Argentina/Buenos_Aires")).with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY)).toString(); }
    public void estadisticas(Player p) {
        var u = duels.getUserManager().get(p); if (u == null) { aviso(p, "&eTus datos todavia estan cargando."); return; }
        int w = u.getWins(), l = u.getLosses();
        Ventana v = ventana(p, "duelos.dialogo.mis_estadisticas", "Mis estadisticas");
        boton(v, CENTRO, Material.BOOK, "&b" + p.getName(), null, null, "&aVictorias: " + w, "&cDerrotas: " + l,
            "&eRacha Astral: " + getConfig().getInt("racha." + p.getUniqueId()), "&7Victorias: " + (w + l == 0 ? 0 : Math.round(w * 100.0 / (w + l))) + "%", "&8Racha registrada desde esta interfaz.");
        tarjeta(v, IZQ, "seguir", () -> menu(p), "&a&lVolver a Duelos");
        tarjeta(v, DER, "arenas", () -> { p.closeInventory(); Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "dm open arenas " + p.getName()); }, "&f&lArenas");
        p.openInventory(v.inv);
    }
    public void ranking(Player p, boolean semanal) {
        Ventana v = ventana(p, semanal ? "duelos.lista.ranking_semanal" : "duelos.lista.ranking_total", semanal ? "Ranking semanal" : "Ranking total");
        Map<String, Integer> tabla = new LinkedHashMap<>();
        if (semanal) {
            var sec = getConfig().getConfigurationSection("semanas." + semana());
            if (sec != null) for (String key : sec.getKeys(false)) tabla.put(nombre(UUID.fromString(key)), sec.getInt(key));
        } else {
            var top = duels.getUserManager().getTopWins();
            if (top != null) for (var row : top.getData()) tabla.put(row.getName(), row.getValue());
        }
        var rows = tabla.entrySet().stream().sorted(Map.Entry.<String,Integer>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey())).limit(10).toList();
        for (int i = 0; i < rows.size(); i++) {
            var row = rows.get(i); boton(v, 9 + i, Material.GOLD_INGOT, "&6#" + (i + 1) + " " + row.getKey(), null, null, "&7Victorias: " + row.getValue());
        }
        if (rows.isEmpty()) boton(v, 13, Material.PAPER, "&7Todavia no hay resultados", null, null);
        boton(v, 49, Material.CLOCK, semanal ? "&eVer total" : "&eVer semanal", null, () -> ranking(p, !semanal), semanal ? "&7Desde el lunes (Argentina)." : "&7Duels actualiza el total cada 5 min.", "&7Semanal: duelos registrados desde esta instalacion."); p.openInventory(v.inv);
    }
    @EventHandler public void inicio(MatchStartEvent e) {
        for (Player p : e.getPlayers()) {
            quitar(p.getUniqueId()); inicios.put(p.getUniqueId(), System.currentTimeMillis());
            p.sendMessage(Component.text("[Duelos] Si queres abandonar: ").append(Component.text("[Rendirse]")
                .color(net.kyori.adventure.text.format.NamedTextColor.RED).clickEvent(ClickEvent.runCommand("/duelos"))));
            for (int i = 0; i <= 5; i++) {
                int n = 5 - i;
                Bukkit.getScheduler().runTaskLater(this, () -> {
                    if (p.isOnline() && !e.getMatch().isFinished() && duels.getArenaManager().isInMatch(p)) {
                        p.sendTitle(color(n == 0 ? "&a¡A pelear!" : "&6" + n), "Duelos Astral", 0, 22, 0);
                    }
                }, i * 20L + 1);
            }
        }
    }
    @EventHandler public void fin(MatchEndEvent e) {
        var match = e.getMatch();
        if (!ARENAS.contains(match.getArena().getName()) || match.getStartingPlayers().size() != 2) return;
        UUID ganador = e.getWinner(), perdedor = e.getLoser();
        Player win = ganador == null ? null : Bukkit.getPlayer(ganador);
        // 23/11: vida en % (con la escala de vida los "corazones" no decian nada).
        double vida = win == null ? 0 : 100 * win.getHealth() / Math.max(1, win.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue());
        if (ganador != null && perdedor != null) {
            String r = "racha." + ganador; getConfig().set(r, getConfig().getInt(r) + 1); getConfig().set("racha." + perdedor, 0);
            String w = "semanas." + semana() + "." + ganador; getConfig().set(w, getConfig().getInt(w) + 1); saveConfig();
        }
        for (Player p : match.getStartingPlayers()) {
            UUID otro = match.getStartingPlayers().stream().map(Player::getUniqueId).filter(id -> !id.equals(p.getUniqueId())).findFirst().orElse(null);
            long segundos = Math.max(0, (System.currentTimeMillis() - inicios.getOrDefault(p.getUniqueId(), System.currentTimeMillis())) / 1000);
            inicios.remove(p.getUniqueId());
            String tiempo = (segundos / 60) + "m " + String.format(Locale.ROOT, "%02d", segundos % 60) + "s";
            String texto = (ganador == null ? "Sin ganador" : "Gano " + nombre(ganador)) + " · " + tiempo + " · le quedo " + Math.round(vida) + "% de vida";
            resultados.put(p.getUniqueId(), new Resultado(otro, match.getArena().getName(), texto));
            // 23/11 (dueno): el resultado en pantalla unos segundos (tambien al que murio y vuelve al lobby) y el chat destacado.
            boolean gano = p.getUniqueId().equals(ganador);
            String grande = ganador == null ? "&e&lEMPATE" : gano ? "&a&l¡GANASTE!" : "&c&lPERDISTE";
            String chico = "&e⏱ " + tiempo + " &8| &c❤ " + Math.round(vida) + "% " + (ganador == null ? "" : gano ? "&7te quedo" : "&7le quedo a " + nombre(ganador));
            p.sendTitle(color(grande), color(chico), 5, 90, 20);
            Bukkit.getScheduler().runTaskLater(this, () -> { if (p.isOnline()) p.sendTitle(color(grande), color(chico), 0, 70, 20); }, 40L);
            p.sendMessage(color("&6&m                                                  "));
            p.sendMessage(color("  " + grande + " &7en &f" + match.getArena().getName()));
            p.sendMessage(color("  &7Tiempo: &f" + tiempo + "  &7Vida del ganador: &c" + Math.round(vida) + "%"));
            p.sendMessage(Component.text("  ").append(Component.text("[Ver resultado / Revancha]").color(net.kyori.adventure.text.format.NamedTextColor.GOLD)
                .clickEvent(ClickEvent.runCommand("/duelos resultado"))));
            p.sendMessage(color("&6&m                                                  "));
        }
    }
    void resultado(Player p) {
        Resultado r = resultados.get(p.getUniqueId()); if (r == null) { aviso(p, "&7Todavia no tenes un resultado reciente."); return; }
        if (duels.getArenaManager().isInMatch(p)) { aviso(p, "&eEspera a volver al lobby para abrir el resultado."); return; }
        Ventana v = ventana(p, "duelos.dialogo.resultado", "Resultado");
        boton(v, CENTRO, Material.GOLD_INGOT, "&6Resultado", null, null, "&7" + r.texto);
        tarjeta(v, IZQ, "revancha", () -> confirmar(p, r.rival, r.arena), "&c&lRevancha", "&7Requiere un nuevo pedido aceptado.");
        tarjeta(v, DER, "arenas", () -> { p.closeInventory(); Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "dm open arenas " + p.getName()); }, "&f&lVolver a Arenas");
        p.openInventory(v.inv);
    }
    @EventHandler public void clic(InventoryClickEvent e) {
        if (!(e.getView().getTopInventory().getHolder() instanceof Ventana v)) return;
        e.setCancelled(true); Runnable r = v.acciones.get(e.getRawSlot());
        if (r != null) Bukkit.getScheduler().runTask(this, () -> { if (e.getWhoClicked().getOpenInventory().getTopInventory() == v.inv) r.run(); });
    }
    @EventHandler public void arrastrar(InventoryDragEvent e) { if (e.getView().getTopInventory().getHolder() instanceof Ventana) e.setCancelled(true); }
    @EventHandler public void salir(PlayerQuitEvent e) { UUID id = e.getPlayer().getUniqueId(); quitar(id); enviados.remove(id); resultados.remove(id); inicios.remove(id); }
    @Override public boolean onCommand(CommandSender s, Command cmd, String label, String[] args) {
        if (!(s instanceof Player p)) return true;
        if (args.length == 0) { if (cmd.getName().equals("desafiar")) jugadores(p, 0); else menu(p); return true; }
        switch (args[0].toLowerCase(Locale.ROOT)) {
            case "salir" -> salir(p);
            case "resultado" -> resultado(p);
            case "aceptar", "rechazar" -> {
                if (args.length == 2) try { responder(p, UUID.fromString(args[1]), args[0].equalsIgnoreCase("aceptar")); }
                catch (IllegalArgumentException ex) { aviso(p, "&cPedido invalido."); }
            }
            default -> menu(p);
        }
        return true;
    }
    @Override public List<String> onTabComplete(CommandSender s, Command c, String l, String[] a) { return a.length == 1 ? List.of("salir", "resultado") : List.of(); }
}
