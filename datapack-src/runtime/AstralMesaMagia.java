package astral;

import java.util.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.ItemStack;
import dev.aurelium.auraskills.api.AuraSkillsApi;
import dev.aurelium.auraskills.api.user.SkillsUser;

/** Un solo estado persistente para mesa, Skript y datapack. No concede permiso a otros OP. */
public final class AstralMesaMagia implements Listener {
    public static final Set<String> IDS = Set.of("poder_arcano", "fluidez", "sifon_mana", "marca_arcana",
        "bendicion", "sabio_arcano", "eco_arcano", "escudo_mana");
    static final java.util.regex.Pattern ASTRAL = java.util.regex.Pattern.compile("\"?astral\"?\\s*:\\s*\\{");
    static final java.util.regex.Pattern ID = java.util.regex.Pattern.compile("[{,]\\s*\"?id\"?\\s*:\\s*\"([a-z0-9_]+)\"");
    final AstralMesa plugin;
    final Set<UUID> siphoned = new HashSet<>(), echoes = new HashSet<>(), casting = new HashSet<>();
    record Mark(UUID source, int level, long until) {}
    record Heal(UUID source, int level, long until, double pct, boolean extra) {}
    final Map<UUID, Mark> marks = new HashMap<>();
    final Map<UUID, Heal> healing = new HashMap<>();
    final Map<EntityDamageEvent, Double> shieldCosts = new IdentityHashMap<>();
    java.util.function.DoubleSupplier random = Math::random;
    long tick;
    public AstralMesaMagia(AstralMesa plugin) {
        this.plugin = plugin;
        Bukkit.getPluginManager().registerEvents(this, plugin);
        plugin.getCommand("encmagia").setExecutor(this::command);
        plugin.getCommand("encmagia_interno").setExecutor(this::internal);
        Bukkit.getScheduler().runTaskTimer(plugin, () -> {
            tick++;
            for (Player p : Bukkit.getOnlinePlayers()) sync(p);
            marks.values().removeIf(m -> m.until <= tick || !enabled(Bukkit.getPlayer(m.source)));
            if (tick % 20 == 0) healTick();
        }, 1L, 1L);
    }
    public boolean enabled(Player p) {
        return p != null && (p.getName().equalsIgnoreCase("ByTrainx") || plugin.getConfig().getBoolean("encmagia.publico", false));
    }
    public void sync(Player p) {
        if (enabled(p)) p.addScoreboardTag("astral.encmagia"); else p.removeScoreboardTag("astral.encmagia");
    }
    public static String itemId(ItemStack it) {
        if (it == null || !it.hasItemMeta()) return "";
        String s = it.getItemMeta().getAsComponentString();
        var a = ASTRAL.matcher(s);
        if (!a.find()) return "";
        var id = ID.matcher(s.substring(a.start()));
        return id.find() ? id.group(1) : "";
    }
    public static boolean accepts(String key, ItemStack item) {
        String id = itemId(item);
        boolean staff = id.matches("baston_([1-9]|10)"), heal = id.equals("varita_curacion"), blast = id.equals("varita_estallido");
        return switch (key) {
            case "bendicion" -> heal;
            case "sifon_mana" -> staff || blast;
            case "sabio_arcano", "escudo_mana" -> staff || heal || blast;
            case "poder_arcano", "fluidez", "marca_arcana", "eco_arcano" -> staff;
            default -> false;
        };
    }
    int level(Player p, String key) {
        if (!enabled(p)) return 0;
        ItemStack it = p.getInventory().getItemInMainHand();
        if (!accepts(key, it)) return 0;
        var e = Registry.ENCHANTMENT.get(NamespacedKey.fromString("astral:" + key));
        return e == null ? 0 : Math.min(e.getMaxLevel(), it.getEnchantmentLevel(e));
    }
    boolean command(CommandSender sender, Command c, String label, String[] args) {
        if (!sender.hasPermission("astral.mesa.admin")) return true;
        if (args.length == 1 && (args[0].equals("publico") || args[0].equals("privado"))) {
            plugin.getConfig().set("encmagia.publico", args[0].equals("publico"));
            plugin.saveConfig();
            for (Player p : Bukkit.getOnlinePlayers()) { sync(p); p.closeInventory(); }
        }
        sender.sendMessage("Encantamientos mágicos: " + (plugin.getConfig().getBoolean("encmagia.publico", false) ? "PUBLICOS" : "solo ByTrainx") + ". /encmagia publico|privado");
        return true;
    }
    boolean internal(CommandSender sender, Command c, String label, String[] args) {
        if (!(sender instanceof ConsoleCommandSender) || args.length < 2) return true;
        Player p = Bukkit.getPlayerExact(args[1]);
        if (p == null) return true;
        if (args[0].equals("sync")) sync(p);
        if (args[0].equals("inicio")) begin(p);
        if (args[0].equals("fin")) casting.remove(p.getUniqueId());
        if (args[0].equals("cura") && args.length == 5)
            heal(p, Double.parseDouble(args[2]), Integer.parseInt(args[3]), Double.parseDouble(args[4]));
        return true;
    }
    void begin(Player p) { casting.add(p.getUniqueId()); siphoned.remove(p.getUniqueId()); }
    @EventHandler public void join(PlayerJoinEvent e) { sync(e.getPlayer()); }
    @EventHandler public void quit(PlayerQuitEvent e) {
        UUID id=e.getPlayer().getUniqueId(); casting.remove(id); siphoned.remove(id); echoes.remove(id); healing.remove(id);
        marks.values().removeIf(m -> m.source.equals(id));
    }
    @EventHandler(ignoreCancelled=true)
    public void marker(EntitySpawnEvent e) {
        if (!(e.getEntity() instanceof Marker m)) return;
        boolean start=m.getScoreboardTags().contains("astral.encmagia.inicio");
        if (!start && !m.getScoreboardTags().contains("astral.encmagia.fin")) return;
        Player p=m.getWorld().getPlayers().stream().filter(t -> t.getScoreboardTags().contains("astral.caster"))
            .min(Comparator.comparingDouble(t -> t.getLocation().distanceSquared(m.getLocation()))).orElse(null);
        if (p == null || echoes.contains(p.getUniqueId())) return;
        if (start) begin(p); else { casting.remove(p.getUniqueId()); echo(p); }
    }
    static void console(String cmd) { Bukkit.dispatchCommand(Bukkit.getConsoleSender(), cmd); }
    void echo(Player p) {
        int level=level(p,"eco_arcano");
        if (level == 0 || random.getAsDouble() >= level * .05) return;
        var obj=Bukkit.getScoreboardManager().getMainScoreboard().getObjective("astral.tmp");
        if (obj == null) return;
        int base=obj.getScore("#base").getScore(), scale=obj.getScore("#sk").getScore();
        ItemStack held=p.getInventory().getItemInMainHand().clone();
        World world=p.getWorld();
        String key="p" + UUID.randomUUID().toString().replace("-", "");
        console("data modify storage astral:ecos " + key + " set from storage astral:tmp spell");
        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            var immunity=new HashMap<LivingEntity,Integer>();
            try {
                if (!p.isOnline() || p.isDead() || p.getWorld()!=world || !enabled(p) ||
                    p.getGameMode()==GameMode.SPECTATOR || !p.getInventory().getItemInMainHand().equals(held)) return;
                echoes.add(p.getUniqueId()); p.addScoreboardTag("astral.caster");
                // A los 4 ticks el blanco sigue inmune al golpe original. El eco menor
                // sería descartado por vanilla: abrir solo esta ejecución síncrona y restaurar.
                for (Entity entity:world.getNearbyEntities(p.getEyeLocation(),27,27,27))
                    if (entity instanceof LivingEntity living && living != p) {
                        immunity.put(living,living.getNoDamageTicks());living.setNoDamageTicks(0);
                    }
                obj.getScore("#base").setScore(base / 2); obj.getScore("#sk").setScore(scale); obj.getScore("#steps").setScore(0);
                console("data modify storage astral:tmp spell set from storage astral:ecos " + key);
                console("execute as " + p.getName() + " at @s anchored eyes positioned ^ ^ ^0.8 run function astral:spell/trace with storage astral:tmp spell");
            } finally {
                immunity.forEach((living,ticks)->{ if (living.isValid()) living.setNoDamageTicks(Math.max(ticks,living.getNoDamageTicks())); });
                p.removeScoreboardTag("astral.caster"); echoes.remove(p.getUniqueId());
                console("data remove storage astral:ecos " + key);
            }
        }, 4L);
    }
    boolean spell(EntityDamageByEntityEvent e, Player p) {
        return (p.getScoreboardTags().contains("astral.caster") && e.getEntity().getScoreboardTags().contains("astral.spell.hit")) ||
            (casting.contains(p.getUniqueId()) && itemId(p.getInventory().getItemInMainHand()).equals("varita_estallido") &&
             e.getDamageSource().getDamageType().equals(org.bukkit.damage.DamageType.PLAYER_EXPLOSION));
    }
    @EventHandler(priority=EventPriority.HIGH, ignoreCancelled=true)
    public void marked(EntityDamageByEntityEvent e) {
        if (!(e.getDamager() instanceof Player p) || !enabled(p) || !spell(e,p)) return;
        Mark m=marks.get(e.getEntity().getUniqueId());
        if (m != null && m.until > tick && enabled(Bukkit.getPlayer(m.source)))
            e.setDamage(e.getDamage() * (1 + new double[]{0,.05,.08,.12}[m.level]));
    }
    @EventHandler(priority=EventPriority.MONITOR, ignoreCancelled=true)
    public void hit(EntityDamageByEntityEvent e) {
        if (!(e.getDamager() instanceof Player p) || !enabled(p) || !spell(e,p) || e.getFinalDamage() <= 0) return;
        int mark=level(p,"marca_arcana");
        if (mark > 0 && !(e.getEntity() instanceof Player)) marks.put(e.getEntity().getUniqueId(),new Mark(p.getUniqueId(),mark,tick+80));
        int siphon=level(p,"sifon_mana");
        if (siphon > 0 && !echoes.contains(p.getUniqueId()) && siphoned.add(p.getUniqueId())) {
            SkillsUser u=AuraSkillsApi.get().getUser(p.getUniqueId());
            if (u != null && u.isLoaded()) u.setMana(Math.min(u.getMaxMana(),u.getMana()+u.getMaxMana()*siphon*.01));
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void shield(EntityDamageEvent e) {
        if (!(e.getEntity() instanceof Player p)) return;
        int level=level(p,"escudo_mana");
        if (level == 0 || e.getFinalDamage() <= 0 || e.getDamage() <= 0) return;
        SkillsUser u=AuraSkillsApi.get().getUser(p.getUniqueId());
        if (u == null || !u.isLoaded()) return;
        // Escala: vida real del jugador, sin FACTOR_ARMA de mobs. Bukkit usa puntos (2 = 1 corazón).
        double finalDamage=e.getFinalDamage(), paid=Math.min(u.getMana(), finalDamage * level * .10);
        // Los modificadores (armadura/absorción) pueden ser no lineales: buscar el daño crudo
        // cuya reducción FINAL sea paid, sin cobrar por golpes cancelados posteriormente.
        double low=0, high=e.getDamage(), target=finalDamage-paid;
        for (int n=0;n<40;n++) {
            double mid=(low+high)/2; e.setDamage(mid);
            if (e.getFinalDamage()<target) low=mid; else high=mid;
        }
        e.setDamage(high);
        shieldCosts.put(e,Math.max(0,finalDamage-e.getFinalDamage()));
    }
    @EventHandler(priority=EventPriority.MONITOR)
    public void shieldPay(EntityDamageEvent e) {
        Double cost=shieldCosts.remove(e);
        if (cost == null || e.isCancelled()) return;
        Player p=(Player)e.getEntity();
        SkillsUser u=AuraSkillsApi.get().getUser(p.getUniqueId());
        if (u != null) u.setMana(Math.max(0,u.getMana()-cost));
    }
    @SuppressWarnings("unchecked") List<Player> party(Player p) {
        var other=Bukkit.getPluginManager().getPlugin("AstralParty");
        if (other == null) return List.of(p);
        try { return (List<Player>) other.getClass().getMethod("members",Player.class).invoke(other,p); }
        catch (ReflectiveOperationException ex) { plugin.getLogger().warning("No pude leer AstralParty: " + ex); return List.of(p); }
    }
    void heal(Player p, double radius, int seconds, double pct) {
        int level=level(p,"bendicion");
        var party=level>0 ? party(p) : List.<Player>of();
        for (Player target:p.getWorld().getPlayers()) {
            double d=target.getLocation().distance(p.getLocation());
            boolean extra=d>radius;
            if (!target.isDead() && target.getGameMode()!=GameMode.SPECTATOR &&
                (d<=radius || (level>0 && party.contains(target) && d<=radius+2))) {
                healing.put(target.getUniqueId(),new Heal(p.getUniqueId(),level,tick+seconds*20,pct,extra));
                target.sendActionBar(net.kyori.adventure.text.Component.text("Curación: "+seconds+" s",net.kyori.adventure.text.format.NamedTextColor.GREEN));
            }
        }
    }
    void healTick() {
        healing.entrySet().removeIf(en -> {
            Player target=Bukkit.getPlayer(en.getKey()), source=Bukkit.getPlayer(en.getValue().source);
            Heal h=en.getValue();
            if (target==null || target.isDead() || tick>h.until || (h.extra && !enabled(source))) return true;
            double bonus=enabled(source) ? 1+h.level*.10 : 1;
            double max=target.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH).getValue();
            var event=new EntityRegainHealthEvent(target,max*h.pct/100*bonus,EntityRegainHealthEvent.RegainReason.CUSTOM); // CUSTOM: astral_gameplay.sk multiplica las MAGIC por vida/10 (curaba todo, 26/11)
            Bukkit.getPluginManager().callEvent(event);
            if (!event.isCancelled()) target.setHealth(Math.min(max,target.getHealth()+event.getAmount()));
            target.getWorld().spawnParticle(Particle.HEART,target.getLocation().add(0,2.1,0),2,.3,.2,.3,0);
            return tick>=h.until;
        });
    }
}
