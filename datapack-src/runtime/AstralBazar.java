package astral;

import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import net.milkbowl.vault.economy.Economy;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.function.Consumer;
import java.util.regex.*;

/** Private, plain chest UI. All player/economy access is on the primary thread.
 * No native inventory movement is allowed: deposits are explicit, journalled clicks.
 */
public final class AstralBazar extends JavaPlugin implements Listener {
    public record Product(String id,String name,String category,long min,long max,ItemStack item) {}
    record Equipment(ItemStack item,int tier,String identity) {}
    final Map<String,Product> products=new LinkedHashMap<>();
    final List<Equipment> equipment=new ArrayList<>();
    final Map<Integer,Long> equipmentPrices=new HashMap<>();
    final Map<UUID,Consumer<String>> inputs=new java.util.concurrent.ConcurrentHashMap<>();
    final Map<UUID,Long> inputDeadlines=new java.util.concurrent.ConcurrentHashMap<>();
    final Set<UUID> busy=new HashSet<>();
    final Map<UUID,Long> lastClick=new HashMap<>();
    Economy economy;
    BazarStore store;
    NamespacedKey receipt;
    boolean paused, healthy=true;
    String lastBackup="";

    public static final class Screen implements InventoryHolder {
        final Map<Integer,Runnable> actions=new HashMap<>();
        final Map<Integer,Runnable> rightActions=new HashMap<>();
        boolean artwork;
        Inventory inv;
        String basket="";
        Consumer<Integer> deposit;
        @Override public Inventory getInventory(){return inv;}
    }
    @Override public void onEnable(){
        try {
            saveDefaultConfig();saveResourceIfMissing("productos.yml");
            receipt=new NamespacedKey(this,"transfer_receipt");
            var registration=getServer().getServicesManager().getRegistration(Economy.class);
            if(registration==null)throw new IllegalStateException("Falta proveedor EssentialsX/Vault.");
            economy=registration.getProvider();loadCatalog();
            Map<String,BazarStore.Product> definitions=new HashMap<>();
            products.forEach((id,p)->definitions.put(id,new BazarStore.Product(id,p.min,p.max)));
            store=new BazarStore(getDataFolder().toPath().resolve("bazar.sqlite"),definitions);
            store.dynamicEnabled=getConfig().getBoolean("limites-dinamicos.activo",true);
            paused=getConfig().getBoolean("pausado",false);
            // A basket belongs to a window, not a permanent lock; after restart all return.
            store.sql("UPDATE claims SET basket='' WHERE basket<>''");
            recoverMoney();
            loadTitles();
            getServer().getPluginManager().registerEvents(this,this);
            getCommand("bazar").setExecutor(this);
            Bukkit.getScheduler().runTaskTimer(this,this::clock,1200,1200);
            Bukkit.getScheduler().runTaskTimer(this,()->{if(!paused&&healthy)try{store.drain();}catch(Exception e){failure(e);}},20,20);
            getLogger().info("Bazar privado listo: "+products.size()+" productos. publico="+getConfig().getBoolean("publico"));
        } catch(Exception e){getLogger().log(java.util.logging.Level.SEVERE,"No se pudo iniciar Bazar; deshabilitado",e);getServer().getPluginManager().disablePlugin(this);}
    }
    void saveResourceIfMissing(String name){if(!getDataFolder().toPath().resolve(name).toFile().exists())saveResource(name,false);}
    static long cents(double d){if(!Double.isFinite(d)||d<0||d>1e12)throw new IllegalArgumentException("Importe inválido.");return java.math.BigDecimal.valueOf(d).movePointRight(2).setScale(0,java.math.RoundingMode.HALF_UP).longValueExact();}
    static long price(String s){try{return new java.math.BigDecimal(s.replace(',','.')).movePointRight(2).longValueExact();}catch(Exception e){throw new IllegalArgumentException("Usá un precio con hasta dos decimales.");}}
    static String money(long c){return String.format(Locale.forLanguageTag("es-AR"),"$%,.2f",c/100.0);}
    void loadCatalog()throws Exception {
        var cfg=YamlConfiguration.loadConfiguration(getDataFolder().toPath().resolve("productos.yml").toFile());
        var section=Objects.requireNonNull(cfg.getConfigurationSection("productos"));
        for(String id:section.getKeys(false)){
            var c=section.getConfigurationSection(id);
            ItemStack item=Bukkit.getItemFactory().createItemStack(c.getString("item"));
            if(!item.hasItemMeta()||!item.getItemMeta().getAsComponentString().contains("astral"))throw new IllegalArgumentException("Producto sin marca: "+id);
            long min=cents(Math.max(c.getDouble("minimo"),c.getDouble("piso_server"))),max=cents(c.getDouble("maximo"));
            if(min<1||max<min)throw new IllegalArgumentException("Rango inválido: "+id);
            products.put(id,new Product(id,c.getString("nombre"),category(id,c.getString("categoria")),min,max,item));
        }
        var eq=Objects.requireNonNull(cfg.getConfigurationSection("equipo"));
        for(String id:eq.getKeys(false)){
            var c=eq.getConfigurationSection(id);var item=Bukkit.getItemFactory().createItemStack(c.getString("item"));
            equipment.add(new Equipment(item,c.getInt("tier"),identity(item)));
        }
        for(int t=1;t<=10;t++)equipmentPrices.put(t,cents(getConfig().getDouble("equipo-precios."+t)));
    }
    // Extract the astral compound with balanced braces (never an unrelated PDC id).
    static String identity(ItemStack item){
        if(item==null||!item.hasItemMeta())return "";
        String s=item.getItemMeta().getAsComponentString();
        Matcher m=Pattern.compile("(?:\\{|,)\\s*astral\\s*:\\s*\\{").matcher(s);
        if(!m.find())return "";int start=m.end(),depth=1;boolean quoted=false,escape=false;
        for(int i=start;i<s.length();i++){
            char ch=s.charAt(i);if(escape){escape=false;continue;}if(ch=='\\'){escape=true;continue;}
            if(ch=='\"'){quoted=!quoted;continue;}
            if(!quoted){
                if(ch=='{')depth++;
                if(ch=='}'&&--depth==0){
                    String compound=s.substring(start,i);var fields=new TreeMap<String,String>();
                    Matcher f=Pattern.compile("(?:^|,)\\s*(id|type|tier|w|set|piece|tool)\\s*:\\s*(\"[^\"]*\"|[a-zA-Z0-9_.]+)").matcher(compound);
                    while(f.find())fields.put(f.group(1),f.group(2));
                    if(!fields.containsKey("id")||!fields.containsKey("type"))return "";
                    var model=item.getItemMeta().getItemModel();
                    return fields.toString()+" model="+model;
                }
            }
        }
        return "";
    }

    ItemStack fungible(ItemStack item){
        if(item==null||item.getType().isAir())return item;
        var n=org.bukkit.craftbukkit.inventory.CraftItemStack.asNMSCopy(item);
        var custom=n.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);
        if(custom==null)return item;
        var tag=custom.copyTag();var astral=tag.getCompoundOrEmpty("astral");
        if(!astral.contains("id")||!astral.contains("type"))return item;
        // Only presentation and schema version may differ. All other components,
        // PDC, custom names, enchantments and extra upgrade data remain exact.
        astral.remove("v");tag.put("astral",astral);
        n.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA,net.minecraft.world.item.component.CustomData.of(tag));
        var out=org.bukkit.craftbukkit.inventory.CraftItemStack.asBukkitCopy(n);
        var meta=out.getItemMeta();meta.lore(null);out.setItemMeta(meta);return out;
    }
    boolean matches(Product p,ItemStack item){return item!=null&&p.item.getType()==item.getType()&&fungible(p.item).isSimilar(fungible(item));}
    Product product(ItemStack item){if(item==null)return null;for(var p:products.values())if(matches(p,item))return p;return null;}
    Equipment gear(ItemStack item){String ident=identity(item);if(ident.isEmpty())return null;for(var e:equipment)if(e.item.getType()==item.getType()&&e.identity.equals(ident))return e;return null;}
    boolean improved(ItemStack item,Equipment e){return !item.isSimilar(e.item);}
    String owner(Player p){return p.getUniqueId().toString();}
    void say(CommandSender p,String s){p.sendMessage("§6Bazar §7» §f"+s);}
    boolean allowed(Player p){return getConfig().getBoolean("publico",false)||p.hasPermission("astral.bazar.usar");}
    void check(Player p){if(!allowed(p))throw new IllegalArgumentException("Próximamente.");if(paused||!healthy)throw new IllegalArgumentException("Bazar pausado; tus bienes siguen guardados.");
        try{if(store.pending().stream().anyMatch(t->t.owner().equals(owner(p))))throw new IllegalArgumentException("Transferencia pendiente de conciliación; avisá al administrador.");}
        catch(java.sql.SQLException e){throw new IllegalStateException(e);}
    }
    void failure(Exception e){healthy=false;paused=true;getConfig().set("pausado",true);saveConfig();getLogger().log(java.util.logging.Level.SEVERE,"Bazar pausado para proteger transferencias",e);}
    void act(Player p,Runnable r){
        if(!busy.add(p.getUniqueId()))return;
        try{check(p);r.run();}catch(IllegalArgumentException e){say(p,e.getMessage());}
        catch(Exception e){failure(e);say(p,"Operación detenida. Avisá al administrador; no repitas transferencias.");}
        finally{busy.remove(p.getUniqueId());}
    }
    interface Checked{void run()throws Exception;}
    void checked(Checked r){try{r.run();}catch(RuntimeException e){throw e;}catch(Exception e){throw new RuntimeException(e);}}

    @Override public boolean onCommand(CommandSender sender,Command cmd,String label,String[] args){
        if(args.length>0&&args[0].equalsIgnoreCase("admin")){
            if(!sender.hasPermission("astral.bazar.admin")){say(sender,"Sin permiso.");return true;}
            try{
                String sub=args.length>1?args[1]:"";
                switch(sub){
                    case "pausar"->{paused=true;getConfig().set("pausado",true);saveConfig();say(sender,"Pausado.");}
                    case "reanudar"->{if(!healthy||!store.pending().isEmpty())throw new IllegalArgumentException("Hay transferencias sin resolver; revisar journal y recibos antes de reanudar.");paused=false;getConfig().set("pausado",false);saveConfig();say(sender,"Reanudado (se conserva el acceso privado).");}
                    case "recargar"->{reloadConfig();store.dynamicEnabled=getConfig().getBoolean("limites-dinamicos.activo",true);loadTitles();paused=getConfig().getBoolean("pausado")||!healthy;say(sender,"Config recargada. Cambios de catálogo requieren reinicio para preservar órdenes.");}
                    case "ver"->{if(args.length<3)throw new IllegalArgumentException("/bazar admin ver <jugador>");var op=Bukkit.getOfflinePlayer(args[2]);String id=op.getUniqueId().toString();say(sender,"UUID "+id+" saldo "+money(store.wallet(id))+"; órdenes "+store.orders(id)+"; retiros "+store.claims(id).size());}
                    case "cancelar"->{if(args.length<3)throw new IllegalArgumentException("/bazar admin cancelar <orden>");long id=Long.parseLong(args[2]);store.cancel(store.find(id).owner(),id);say(sender,"Cancelada; devolución para retirar.");}
                    default->say(sender,"/bazar admin pausar|reanudar|ver <jugador>|cancelar <orden>|recargar");
                }
            }catch(Exception e){say(sender,e.getMessage());}return true;
        }
        if(!(sender instanceof Player p)){say(sender,"Solo jugadores.");return true;}
        if(!allowed(p)){say(p,"Próximamente.");return true;}
        if(args.length>0&&args[0].equalsIgnoreCase("entrada")){
            String text=String.join(" ",Arrays.copyOfRange(args,1,args.length));acceptInput(p,text);return true;
        }
        inputs.remove(p.getUniqueId());inputDeadlines.remove(p.getUniqueId());act(p,()->home(p));return true;
    }
    // Ventanas con el diseno del dueno (ventanas_bazar.py): el titulo es el dibujo (glifos del pack) y los
    // botones dibujados se atrapan con items invisibles. Con "diseno: false" vuelven las ventanas simples.
    final Map<String,String> titles=new HashMap<>();
    static final NamespacedKey BLANK=new NamespacedKey("astral","viajes/blank");
    boolean design(){return getConfig().getBoolean("diseno",true)&&!titles.isEmpty();}
    void loadTitles(){
        titles.clear();var in=getResource("ventanas.yml");if(in==null)return;
        var y=YamlConfiguration.loadConfiguration(new java.io.InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8));
        for(String k:y.getKeys(false))titles.put(k,y.getString(k));
    }
    Screen screen(Player p,String kind,String title,int rows){
        Screen s=new Screen();s.artwork=design()&&titles.containsKey(kind);s.inv=Bukkit.createInventory(s,rows*9,s.artwork?titles.get(kind):title);return s;
    }
    /** Boton dibujado: items invisibles con nombre/lore en todos sus casilleros (sin diseno: un item visible). */
    void hit(Screen s,int[] slots,Material mat,String name,Runnable action,String...lore){
        for(int i=0;i<slots.length;i++){
            if(!s.artwork&&i>0){if(action!=null)s.actions.put(slots[i],action);continue;}
            button(s,slots[i],s.artwork?Material.PAPER:mat,name,action,lore);
            if(s.artwork){var it=s.inv.getItem(slots[i]);var m=it.getItemMeta();m.setItemModel(BLANK);it.setItemMeta(m);}
        }
    }
    static int[] at(int...slots){return slots;}
    void button(Screen s,int slot,Material mat,String name,Runnable action,String...lore){
        ItemStack item=new ItemStack(mat);var meta=item.getItemMeta();meta.setDisplayName("§e"+name);meta.setLore(Arrays.stream(lore).map(x->"§7"+x).toList());item.setItemMeta(meta);s.inv.setItem(slot,item);if(action!=null)s.actions.put(slot,action);
    }
    void nav(Player p,Screen s,int[] back,int[] close,Runnable action){hit(s,back,Material.ARROW,"Volver",action);if(close!=null)hit(s,close,Material.BARRIER,"Cerrar",p::closeInventory);}
    static final String[] CATS={"Combate","Bosque","Oceano","Consumibles","Especiales"};
    static final String[] CAT_NAMES={"Combate","Bosque","Océano","Consumibles","Especiales"};
    // Older catalogs remain safe to load; orders refer only to product IDs.
    static String category(String id,String old){
        return switch(id){
            case "netherita_fundida","netherita_reforzada" -> "Combate";
            case "madera_estelar","palo_reforzado" -> "Bosque";
            case "perla_abisal","coral_astral" -> "Oceano";
            default -> Arrays.asList(CATS).contains(old)?old:"Especiales";
        };
    }
    static final int[][] CAT_SLOTS={{9,10,18,19},{11,12,20,21},{13,22},{14,15,23,24},{16,17,25,26}};
    static final int PAGE=36;
    void open(Player p,Screen s){p.openInventory(s.inv);}
    void home(Player p){listing(p,CATS[0],"",0);}
    static final int[] PRODUCT_SLOTS={2,3,4,5,6,7,8,11,12,13,14,15,16,17,20,21,22,23,24,25,26,29,30,31,32,33,34,35,38,39,40,41,42,43,44};
    void listing(Player p,String cat,String search,int page){checked(()->{
        List<Product> list=products.values().stream().filter(x->(cat.isEmpty()||cat.equals(x.category))&&(search.isEmpty()||normalize(x.name).contains(normalize(search)))).toList();
        Screen s=screen(p,"productos","Bazar - Inicio",6);int start=page*PRODUCT_SLOTS.length;
        for(int i=0;i<CATS.length;i++){String c=CATS[i];hit(s,at(i*9,i*9+1),Material.CHEST,(c.equals(cat)?"► ":"")+CAT_NAMES[i],()->listing(p,c,"",0),"Clic para ver productos.");}
        for(int i=0;i<PRODUCT_SLOTS.length&&start+i<list.size();i++){
            Product x=list.get(start+i);ItemStack icon=x.item.clone();icon.setAmount(1);var m=icon.getItemMeta();
            var sell=store.book(x.id,false);var buy=store.book(x.id,true);
            m.setLore(List.of("§7Comprar al instante: "+(sell.isEmpty()?"Sin ofertas":money(sell.getFirst().price())+" c/u"),"§7Vender al instante: "+(buy.isEmpty()?"Sin órdenes":money(buy.getFirst().price())+" c/u"),"§eClic para operar."));
            icon.setItemMeta(m);cleanTooltip(icon);s.inv.setItem(PRODUCT_SLOTS[i],icon);s.actions.put(PRODUCT_SLOTS[i],()->detail(p,x));
        }
        // 26/11 diseno Gemini: fila de abajo con un boton por casillero (lupa, libro, cofre, remera, <, pagina, >, X).
        hit(s,at(45),Material.COMPASS,"Buscar",()->ask(p,"Nombre del producto",text->listing(p,"",text,0)));
        hit(s,at(46),Material.BOOK,"Mis órdenes",()->orders(p,0));
        hit(s,at(47),Material.HOPPER,"Vender inventario",()->sellInventory(p),"Vende materiales con órdenes de compra.","No toca equipo.");
        hit(s,at(48),Material.IRON_SWORD,"Vender equipo al server",()->equipmentScreen(p,"eq-"+UUID.randomUUID()));
        hit(s,at(49),Material.ARROW,"Anterior",page>0?()->listing(p,cat,search,page-1):null);
        pageItem(s,50,page,Math.max(1,(list.size()+34)/35));
        hit(s,at(51),Material.ARROW,"Siguiente",start+PRODUCT_SLOTS.length<list.size()?()->listing(p,cat,search,page+1):null);
        hit(s,at(53),Material.BARRIER,"Cerrar",p::closeInventory);open(p,s);
    });}
    void pageItem(Screen s,int slot,int page,int pages){hit(s,at(slot),Material.PAPER,"Página "+(page+1)+" de "+pages,null);}
    static String normalize(String s){return java.text.Normalizer.normalize(s.toLowerCase(Locale.ROOT),java.text.Normalizer.Form.NFD).replaceAll("\\p{M}","");}
    void cleanTooltip(ItemStack item){
        // UI copies only: the canonical trading identity is never modified.
        item.setData(io.papermc.paper.datacomponent.DataComponentTypes.TOOLTIP_DISPLAY,
            io.papermc.paper.datacomponent.item.TooltipDisplay.tooltipDisplay().addHiddenComponents(
                io.papermc.paper.datacomponent.DataComponentTypes.ATTRIBUTE_MODIFIERS,
                io.papermc.paper.datacomponent.DataComponentTypes.ENCHANTMENTS).build());
    }
    String[] marketLore(Player p,Product x,boolean side,String click)throws Exception {
        var lines=new ArrayList<String>();var book=store.book(x.id,side);
        lines.add(book.isEmpty()?(side?"Sin órdenes de compra.":"Sin ofertas de venta."):"Mejor precio: "+money(book.getFirst().price())+" c/u");
        for(var l:book)lines.add(money(l.price())+" × "+l.qty()+" ("+l.orders()+" órdenes)");
        var range=store.range(x.id);lines.add("Rango de hoy: "+money(range.min())+" - "+money(range.max())+" "+range.arrow());
        lines.add("Tenés "+count(p,x)+" en el inventario.");lines.add("Impuesto de venta: 1,25%.");lines.add("Clic para "+click+".");return lines.toArray(String[]::new);
    }
    void detail(Player p,Product x){checked(()->{
        Screen s=screen(p,"producto","Bazar - "+x.name,6);
        if(s.artwork){ItemStack icon=x.item.clone();icon.setAmount(1);var im=icon.getItemMeta();im.setLore(List.of("§7Tenés "+count(p,x)+" en el inventario."));icon.setItemMeta(im);cleanTooltip(icon);s.inv.setItem(4,icon);}
        hit(s,s.artwork?at(9,10,11,12,18,19,20,21):at(10,11,19,20),Material.GOLD_INGOT,"Comprar al instante",()->amount(p,x,true,true),marketLore(p,x,false,"elegir cantidad"));
        hit(s,s.artwork?at(14,15,16,17,23,24,25,26):at(14,15,23,24),Material.EMERALD,"Vender al instante",()->choosePrice(p,x,false,true,count(p,x)),marketLore(p,x,true,"vender todo lo que tenés"));
        hit(s,s.artwork?at(27,28,29,30,36,37,38,39):at(28,29,37,38),Material.WRITABLE_BOOK,"Crear orden de compra",()->amount(p,x,true,false),marketLore(p,x,true,"crear una orden de compra"));
        hit(s,s.artwork?at(32,33,34,35,41,42,43,44):at(32,33,41,42),Material.WRITABLE_BOOK,"Crear oferta de venta",()->amount(p,x,false,false),marketLore(p,x,false,"crear una oferta de venta"));
        hit(s,s.artwork?at(45,46,47):at(45),Material.ARROW,"Volver",()->home(p));hit(s,s.artwork?at(51,52,53):at(49),Material.BOOK,"Mis órdenes",()->orders(p,0));open(p,s);
    });}
    int count(Player p,Product x){int n=0;for(var it:p.getInventory().getStorageContents())if(matches(x,it))n+=it.getAmount();return n;}
    int capacity(Player p,Product x){int n=0,max=x.item.getMaxStackSize();for(var it:p.getInventory().getStorageContents())if(it==null||it.getType().isAir())n+=max;else if(x.item.isSimilar(it))n+=Math.max(0,max-it.getAmount());return n;}
    long best(Product x,boolean buy)throws Exception {var b=store.book(x.id,buy);var r=store.range(x.id);return b.isEmpty()?(buy?r.min():r.max()):b.getFirst().price();}
    void amount(Player p,Product x,boolean buy,boolean instant){
        // 26/11 diseno Gemini: una ventana por caso (las tarjetas traen el numero dibujado).
        Screen s=screen(p,"cantidad_"+(instant?"i":"o")+(buy?"c":"v"),"Bazar - Cantidad",5);
        if(s.artwork){
            int[][] cards={at(9,10,11,18,19,20),at(12,13,14,21,22,23),at(15,16,17,24,25,26)};
            int[] qs=instant?new int[]{1,x.item.getMaxStackSize()}:buy?new int[]{64,160,1024}:new int[]{64,160};
            for(int i=0;i<qs.length;i++){int n=qs[i];hit(s,cards[i],Material.PAPER,n+" unidades",()->choosePrice(p,x,buy,instant,n));}
            if(instant&&buy)hit(s,cards[2],Material.CHEST,"Llenar inventario",()->choosePrice(p,x,true,true,capacity(p,x)));
            if(!buy)hit(s,cards[2],Material.CHEST,"Todo lo que tengo",()->choosePrice(p,x,false,instant,count(p,x)),"Tenés "+count(p,x)+".");
            hit(s,at(28,29,30,31,32,33,34),Material.NAME_TAG,"A mano",()->ask(p,"Cantidad (1 a 71680)",text->{int n;try{n=Integer.parseInt(text);}catch(Exception e){throw new IllegalArgumentException("Cantidad inválida.");}choosePrice(p,x,buy,instant,n);}));
            nav(p,s,at(36,37,38),at(42,43,44),()->detail(p,x));open(p,s);return;
        }
        int[] quantities=instant?new int[]{1,x.item.getMaxStackSize()}:new int[]{64,160,1024};
        for(int i=0;i<quantities.length;i++){int n=quantities[i];button(s,10+i*2,Material.PAPER,n+" unidades",()->choosePrice(p,x,buy,instant,n));}
        if(instant&&buy)button(s,15,Material.CHEST,"Llenar inventario",()->choosePrice(p,x,true,true,capacity(p,x)));
        if(!buy)button(s,15,Material.CHEST,"Todo lo que tengo",()->choosePrice(p,x,false,instant,count(p,x)));
        button(s,16,Material.NAME_TAG,"A mano",()->ask(p,"Cantidad (1 a 71680)",text->{int n;try{n=Integer.parseInt(text);}catch(Exception e){throw new IllegalArgumentException("Cantidad inválida.");}choosePrice(p,x,buy,instant,n);}));
        nav(p,s,at(36),at(44),()->detail(p,x));open(p,s);
    }
    int affordable(Player p,Product x)throws Exception {
        long budget=cents(economy.getBalance(p))+store.wallet(owner(p));int n=0;
        // Quote exact depth; no charging the maximum price for unavailable liquidity.
        try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=0 AND remaining>0 AND owner<>? ORDER BY price,id LIMIT 256")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next()&&n<71680){long price=r.getLong(1);int take=(int)Math.min(Math.min(71680-n,r.getInt(2)),budget/price);n+=take;budget-=take*price;if(take<r.getInt(2))break;}}
        }return n;
    }
    void choosePrice(Player p,Product x,boolean buy,boolean instant,int qty){
        if(qty<1||qty>71680)throw new IllegalArgumentException("Cantidad: 1 a 71.680; puede no haber liquidez.");
        if(instant){checked(()->{var range=store.range(x.id);confirm(p,x,buy,true,qty,buy?range.max():range.min());});return;}
        checked(()->{
            long b=best(x,buy);Screen s=screen(p,"precio","Bazar - Precio",5);
            boolean a=s.artwork;
            hit(s,a?at(9,10,18,19,27,28):at(10),Material.GOLD_NUGGET,"Igual a la mejor: "+money(b),()->confirm(p,x,buy,false,qty,b));
            long better=buy?b+10:b-10;
            var range=store.range(x.id);
            hit(s,a?at(11,12,20,21,29,30):at(12),Material.GOLD_INGOT,(buy?"Mejor +$0,10: ":"Mejor -$0,10: ")+money(Math.max(0,better)),better>=range.min()&&better<=range.max()?()->confirm(p,x,buy,false,qty,better):null);
            long spread=marginPrice(x,buy);
            hit(s,a?at(14,15,23,24,32,33):at(14),Material.EMERALD,"5% del margen",spread>0?()->confirm(p,x,buy,false,qty,spread):null,spread>0?"Precio: "+money(spread):"Necesitás compra y venta con margen positivo.");
            hit(s,a?at(16,17,25,26,34,35):at(16),Material.NAME_TAG,"A mano",()->ask(p,"Precio por unidad",text->confirm(p,x,buy,false,qty,price(text))));
            nav(p,s,at(36,37,38),at(42,43,44),()->amount(p,x,buy,false));open(p,s);
        });
    }
    long marginPrice(Product x,boolean buy)throws Exception {
        var bids=store.book(x.id,true);var asks=store.book(x.id,false);
        if(bids.isEmpty()||asks.isEmpty())return 0;
        long low=bids.getFirst().price(),high=asks.getFirst().price();if(high<=low)return 0;
        long step=Math.max(1,Math.round((high-low)*0.05));long value=buy?low+step:high-step;
        var range=store.range(x.id);return value>=range.min()&&value<=range.max()?value:0;
    }
    void confirm(Player p,Product x,boolean buy,boolean instant,int qty,long price){
        try{var range=store.range(x.id);if(!instant&&(price<range.min()||price>range.max()))throw new IllegalArgumentException("Precio fuera de rango: "+money(range.min())+" - "+money(range.max()));}catch(java.sql.SQLException ex){throw new IllegalStateException(ex);}
        Screen s=screen(p,"confirmar_orden","Bazar - Confirmar orden",5);
        String action=(buy?"Comprar":"Vender")+(instant?" al instante":" mediante orden");
        long estimate;
        try{estimate=instant?(buy?quote(p,x,qty):sellQuote(p,x,qty)):Math.multiplyExact(price,qty);}
        catch(Exception e){throw new IllegalStateException(e);}
        button(s,design()?20:13,x.item.getType(),action+" "+qty+" "+x.name,null,"Límite por unidad: "+money(price),(instant?"Total estimado disponible: ":"Total reservado: ")+money(estimate),instant?"Puede variar al confirmar según la liquidez.":"Sin vencimiento.","Impuesto vendedor: 1,25%; redondeo acumulado al centavo.","No negocia con tus propias órdenes.");
        hit(s,at(36,37,38),Material.LIME_WOOL,"Confirmar",()->checked(()->{
            // Invalidate this window before touching resources: packets cannot submit twice.
            s.actions.clear();p.closeInventory();
            if(buy){long needed=instant?quote(p,x,qty):Math.multiplyExact(price,qty);if(needed==0)throw new IllegalArgumentException("No hay ofertas de venta.");
                fund(p,Math.max(0,needed-store.wallet(owner(p))));
                // Instant orders reserve a depth quote rather than qty * max. Use a
                // separate exact execution with refund of unused cash.
                if(instant){instantBuy(p,x,qty);collectProduct(p,x.id);payAvailable(p);say(p,"Compraste al instante; pagaste "+money(needed)+". Lo que no entra queda en Mis órdenes.");orders(p,0);return;}
            } else depositProduct(p,x,instant?qty:Math.max(0,qty-store.available(owner(p),x.id)));
            long beforeCash=store.wallet(owner(p));long id=store.create(owner(p),x.id,buy,qty,instant?1:price,instant);if(instant){long earned=store.wallet(owner(p))-beforeCash;collectProduct(p,x.id);payAvailable(p);say(p,"Vendiste "+store.find(id).filled()+"; cobraste "+money(earned)+".");}else say(p,"Orden #"+id+" creada por "+money(Math.multiplyExact(price,qty))+".");orders(p,0);
        }));
        hit(s,at(42,43,44),Material.RED_WOOL,"Volver",()->detail(p,x));open(p,s);
    }
    long quote(Player p,Product x,int qty)throws Exception {
        long sum=0;int left=qty;
        try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=0 AND remaining>0 AND owner<>? ORDER BY price,id LIMIT 256")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next()&&left>0){int n=Math.min(left,r.getInt(2));sum=Math.addExact(sum,Math.multiplyExact(n,r.getLong(1)));left-=n;}}
        }return sum;
    }
    long sellQuote(Player p,Product x,int qty)throws Exception {
        long gross=0;int left=qty;
        try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=1 AND remaining>0 AND owner<>? ORDER BY price DESC,id LIMIT 256")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next()&&left>0){int n=Math.min(left,r.getInt(2));gross+=n*r.getLong(1);left-=n;}}
        }return gross-BazarStore.tax(gross);
    }
    int sellable(Player p,Product x,int qty)throws Exception {
        try(var q=store.db.prepareStatement("SELECT COALESCE(SUM(remaining),0) FROM (SELECT remaining FROM orders WHERE product=? AND buy=1 AND remaining>0 AND owner<>? ORDER BY price DESC,id LIMIT 256)")){
            BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){return r.next()?(int)Math.min(qty,r.getLong(1)):0;}
        }
    }
    void instantBuy(Player p,Product x,int qty)throws Exception {
        // Each operation is bounded and runs in one SQLite transaction, reserving
        // actual price levels. No inventory/Vault operations occur inside a match.
        store.tx(()->{
            var levels=new ArrayList<long[]>();
            try(var q=store.db.prepareStatement("SELECT price,remaining FROM orders WHERE product=? AND buy=0 AND remaining>0 AND owner<>? ORDER BY price,id LIMIT 256")){
                BazarStore.bind(q,x.id,owner(p));try(var r=q.executeQuery()){while(r.next())levels.add(new long[]{r.getLong(1),r.getInt(2)});}
            }
            int left=qty;for(var l:levels){
                if(left==0)break;int n=Math.min(left,(int)l[1]);store.create(owner(p),x.id,true,n,l[0],true);left-=n;
            }return null;
        });
    }
    void ask(Player p,String prompt,Consumer<String> callback){
        p.closeInventory();UUID id=p.getUniqueId();inputs.put(id,callback);long deadline=System.currentTimeMillis()+30000;inputDeadlines.put(id,deadline);
        say(p,prompt+": escribilo en el chat. Tenés 30 s; cancelar para salir.");
        Bukkit.getScheduler().runTaskLater(this,()->{if(Objects.equals(inputDeadlines.get(id),deadline)){inputs.remove(id);inputDeadlines.remove(id);say(p,"Venció la entrada. Abrí /bazar para seguir.");}},600);
    }
    void acceptInput(Player p,String text){
        var callback=inputs.remove(p.getUniqueId());Long deadline=inputDeadlines.remove(p.getUniqueId());
        if(callback==null){say(p,"No hay una entrada pendiente.");return;}
        if(deadline==null||System.currentTimeMillis()>deadline){say(p,"Venció la entrada.");return;}
        if(text.strip().equalsIgnoreCase("cancelar")){say(p,"Entrada cancelada.");home(p);return;}
        act(p,()->callback.accept(text.strip()));
    }
    @EventHandler(priority=EventPriority.LOWEST) public void chat(io.papermc.paper.event.player.AsyncChatEvent e){
        if(!inputs.containsKey(e.getPlayer().getUniqueId()))return;e.setCancelled(true);
        String text=net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(e.message());
        Bukkit.getScheduler().runTask(this,()->acceptInput(e.getPlayer(),text));
    }
    void collectProduct(Player p,String id)throws Exception {for(var c:store.claims(owner(p)))if(c.basket().isEmpty()&&c.product().equals(id))withdraw(p,c);}
    void payAvailable(Player p)throws Exception {long n=store.wallet(owner(p));if(n>0)pay(p,n);}
    void collectAll(Player p)throws Exception {for(var c:store.claims(owner(p)))if(c.basket().isEmpty())withdraw(p,c);payAvailable(p);}
    void collectOrder(Player p,long order)throws Exception {
        var o=store.find(order);if(!o.owner().equals(owner(p)))throw new IllegalArgumentException("Orden ajena.");
        for(var c:store.claims(owner(p)))if(c.basket().isEmpty()&&store.claimOrder(c.id())==order)withdraw(p,c);
        long n=store.orderMoney(owner(p),order);if(n>0)pay(p,n,order);
    }
    void orders(Player p,int page){checked(()->{
        var all=store.orders(owner(p));var claimableOrders=store.claimableOrders(owner(p));Screen s=screen(p,"mis_ordenes","Bazar - Mis ordenes",6);int pages=Math.max(1,(all.size()+44)/45);
        for(int i=0;i<45&&page*45+i<all.size();i++){var o=all.get(page*45+i);Product x=products.get(o.product());final int slot=i;
            boolean claimable=claimableOrders.contains(o.id());
            button(s,i,x==null?Material.PAPER:x.item.getType(),"#"+o.id()+" "+(o.buy()?"Compra ":"Venta ")+(x==null?o.product():x.name),()->checked(()->{s.actions.clear();collectOrder(p,o.id());orders(p,page);}),"Llenadas "+o.filled()+" / "+o.quantity()+"; restan "+o.remaining(),"Precio: "+money(o.price()),claimable?"Clic para cobrar":"Sin cobros pendientes",o.remaining()>0?"Clic derecho para cancelar y devolver":"Finalizada");
            s.rightActions.put(slot,()->checked(()->{s.actions.clear();s.rightActions.clear();store.cancel(owner(p),o.id());collectOrder(p,o.id());orders(p,page);}));
        }
        boolean a=s.artwork;
        hit(s,a?at(45,46):at(45),Material.CHEST,"Cobrar todo",()->checked(()->{s.actions.clear();collectAll(p);orders(p,page);}),"Incluye custodia y saldo anteriores a 1.2.0.","Lo que no entra sigue guardado.");
        hit(s,at(a?47:48),Material.ARROW,"Anterior",page>0?()->orders(p,page-1):null);pageItem(s,a?48:49,page,pages);
        hit(s,at(a?49:50),Material.ARROW,"Siguiente",(page+1)*45<all.size()?()->orders(p,page+1):null);
        nav(p,s,a?at(50,51):at(51),a?at(52,53):at(53),()->home(p));open(p,s);
    });}
    void orderDetail(Player p,long id){orders(p,0);}
    void withdrawals(Player p,int page){orders(p,page);}
    void sellInventory(Player p){checked(()->{
        Screen s=screen(p,"inventario","Bazar - Vender inventario",6);var quantities=new LinkedHashMap<Product,Integer>();long total=0;int slot=0;
        for(var x:products.values()){int n=count(p,x);long value=n==0?0:sellQuote(p,x,n);if(value<=0)continue;quantities.put(x,n);total+=value;
            if(slot<45)button(s,slot++,x.item.getType(),x.name+" × "+sellable(p,x,n),null,"De "+n+" en tu inventario; hasta "+money(value),"Solo se vende la cantidad con demanda.");}
        hit(s,s.artwork?at(48,49,50):at(49),Material.LIME_WOOL,"Confirmar: hasta "+money(total),()->checked(()->{
            s.actions.clear();p.closeInventory();long before=store.wallet(owner(p));int sold=0;
            for(var entry:quantities.entrySet()){Product x=entry.getKey();int n=Math.min(entry.getValue(),count(p,x));if(n==0||sellQuote(p,x,n)<=0)continue;
                depositProduct(p,x,n);long order=store.create(owner(p),x.id,false,n,1,true);sold+=store.find(order).filled();collectProduct(p,x.id);}
            long earned=store.wallet(owner(p))-before;payAvailable(p);say(p,"Vendiste "+sold+" ítems; cobraste "+money(earned)+".");home(p);
        }),"Estimado; depende de las órdenes al confirmar.","Impuesto 1,25% incluido.");nav(p,s,s.artwork?at(45,46):at(45),s.artwork?at(52,53):at(53),()->home(p));open(p,s);
    });}
    ItemStack claimItem(BazarStore.Claim c){return c.item()!=null?ItemStack.deserializeBytes(c.item()):Objects.requireNonNull(products.get(c.product()),"Producto retirado del catálogo: "+c.product()).item.clone();}
    void equipmentScreen(Player p,String basket){checked(()->{
        Screen s=screen(p,"vender_equipo","Bazar - Vender equipo",6);s.basket=basket;s.deposit=slot->checked(()->{
            ItemStack item=p.getInventory().getItem(slot);Equipment e=gear(item);
            if(e==null)throw new IllegalArgumentException("Solo armas y armaduras Astrales. No historia, mochilas, mascotas, cosméticos, taladros ni oficios.");
            deposit(p,slot,item.getAmount(),"equipo",basket);refreshEquipment(p,s);
        });refreshEquipment(p,s);nav(p,s,at(45,46),at(52,53),()->home(p));open(p,s);
    });}
    void refreshEquipment(Player p,Screen s)throws Exception {
        for(int i=0;i<45;i++)s.inv.setItem(i,null);
        long total=0;boolean improvements=false;int slot=0;
        for(var c:store.claims(owner(p)))if(c.basket().equals(s.basket)){
            ItemStack item=claimItem(c);Equipment e=gear(item);if(e==null)throw new IllegalArgumentException("Equipo inválido.");
            total+=equipmentPrices.get(e.tier)*c.qty();improvements|=improved(item,e);
            if(slot<45){item.setAmount(Math.min(c.qty(),item.getMaxStackSize()));s.inv.setItem(slot++,item);}
        }
        String b=s.basket;long value=total;boolean warn=improvements;
        hit(s,at(47,48,49,50,51),Material.LIME_WOOL,"Vender por "+money(total),()->{if(value<=0)throw new IllegalArgumentException("Elegí equipo de tu inventario inferior.");confirmEquipment(p,s,b,value,warn);},"Clic en el inventario inferior para depositar piezas.","Al cerrar vuelve todo; si no entra, queda para retirar.",warn?"Este lote tiene mejoras. En la Subasta vale más.":"Conviene más vender en la Subasta.");
    }
    void confirmEquipment(Player p,Screen old,String basket,long total,boolean warn){
        // Keep custody in SQLite when switching windows; close must not return it.
        old.basket="";Screen s=screen(p,"confirmar_equipo","Bazar - Confirmar equipo",design()?6:3);s.basket=basket;
        if(design()){int slot=0;try{for(var c:store.claims(owner(p)))if(c.basket().equals(basket)&&slot<27){ItemStack it=claimItem(c);it.setAmount(Math.min(c.qty(),it.getMaxStackSize()));s.inv.setItem(slot++,it);}}catch(Exception e){throw new IllegalStateException(e);}}
        int[] info=design()?java.util.stream.IntStream.range(27,45).toArray():at(13);
        hit(s,info,Material.ANVIL,"Total: "+money(total),null,warn?"Este lote tiene mejoras. En la Subasta vale más.":"En la Subasta suele valer más.","Se pierden encantamientos, gemas, reforja y mejoras.");
        hit(s,design()?at(45,46,47,48):at(11),Material.LIME_WOOL,"Vender por "+money(total),()->checked(()->{
            s.actions.clear();Map<Long,Integer> tiers=new HashMap<>();
            for(var c:store.claims(owner(p)))if(c.basket().equals(basket)){var e=gear(claimItem(c));if(e==null)throw new IllegalArgumentException("Equipo inválido");tiers.put(c.id(),e.tier);}
            store.sellEquipment(owner(p),basket,equipmentPrices,tiers);s.basket="";say(p,"Equipo vendido: "+money(total)+" para retirar.");orders(p,0);
        }));hit(s,design()?at(50,51,52,53):at(15),Material.RED_WOOL,"Cancelar y devolver todo",p::closeInventory);open(p,s);
    }

    void fund(Player p,long amount)throws Exception {
        if(amount<=0)return;if(amount>cents(economy.getBalance(p)))throw new IllegalArgumentException("Plata insuficiente.");
        long id=store.prepare(owner(p),"money_in",amount,economy.getBalance(p),0,"",0,null,"");
        var response=economy.withdrawPlayer(p,amount/100.0);
        store.settle(id,response.transactionSuccess());if(!response.transactionSuccess())throw new IllegalArgumentException("Vault rechazó el cobro: "+response.errorMessage);
    }
    void pay(Player p,long amount)throws Exception {pay(p,amount,0);}
    void pay(Player p,long amount,long order)throws Exception {
        if(amount<=0){say(p,"No hay plata para retirar.");return;}
        long id=store.prepare(owner(p),"money_out",amount,economy.getBalance(p),0,"",0,null,order>0?"order:"+order:"");
        var response=economy.depositPlayer(p,amount/100.0);store.settle(id,response.transactionSuccess());
        if(!response.transactionSuccess())throw new IllegalArgumentException("Vault rechazó el retiro; el saldo sigue guardado.");say(p,"Retiraste "+money(amount));
    }
    void depositProduct(Player p,Product x,int amount)throws Exception {
        if(count(p,x)<amount)throw new IllegalArgumentException("No tenés suficientes productos idénticos; no se aceptan vanilla, renombrados ni mejorados.");
        for(int slot=0;slot<36&&amount>0;slot++){var it=p.getInventory().getItem(slot);if(matches(x,it)){int n=Math.min(amount,it.getAmount());deposit(p,slot,n,x.id,"");amount-=n;}}
    }
    void deposit(Player p,int slot,int qty,String product,String basket)throws Exception {
        ItemStack it=p.getInventory().getItem(slot);if(it==null||qty<1||qty>it.getAmount())throw new IllegalArgumentException("El ítem ya no está.");
        ItemStack unit=it.clone();unit.setAmount(1);
        long id=store.prepare(owner(p),"item_in",0,0,0,product,qty,unit.serializeAsBytes(),basket);
        ItemStack rest=it.clone();rest.setAmount(it.getAmount()-qty);p.getInventory().setItem(slot,rest.getAmount()==0?null:rest);
        p.getPersistentDataContainer().set(receipt,PersistentDataType.LONG,id);p.saveData();store.settle(id,true);
    }
    void withdraw(Player p,BazarStore.Claim c)throws Exception {
        ItemStack unit=claimItem(c);int free=0,max=unit.getMaxStackSize();
        for(ItemStack it:p.getInventory().getStorageContents())if(it==null||it.getType().isAir())free+=max;else if(it.isSimilar(unit))free+=Math.max(0,max-it.getAmount());
        int qty=Math.min(free,c.qty());if(qty==0){say(p,"Inventario lleno. Todo sigue para retirar.");return;}
        long id=store.prepare(owner(p),"item_out",0,0,c.id(),c.product(),qty,null,"");
        int left=qty;while(left>0){ItemStack stack=unit.clone();int n=Math.min(max,left);stack.setAmount(n);if(!p.getInventory().addItem(stack).isEmpty())throw new IllegalStateException("Inventario cambió durante retiro");left-=n;}
        p.getPersistentDataContainer().set(receipt,PersistentDataType.LONG,id);p.saveData();store.settle(id,true);say(p,"Retiraste "+qty+"; el resto sigue guardado.");
    }
    void recoverMoney()throws Exception {
        for(var t:store.pending())if(t.kind().startsWith("money_")){
            double balance=economy.getBalance(Bukkit.getOfflinePlayer(UUID.fromString(t.owner())));
            double expected=t.before()+(t.kind().equals("money_in")?-1:1)*t.cents()/100.0;
            if(Math.abs(balance-expected)<0.005)store.settle(t.id(),true);
            else if(Math.abs(balance-t.before())<0.005)store.settle(t.id(),false);
            else {paused=true;healthy=false;getConfig().set("pausado",true);saveConfig();getLogger().severe("Pago ambiguo journal #"+t.id()+"; requiere conciliación con Essentials. No se repite.");}
        }
    }
    @EventHandler public void join(PlayerJoinEvent event){Player p=event.getPlayer();Bukkit.getScheduler().runTask(this,()->checked(()->{
        for(var t:store.pending())if(t.owner().equals(owner(p))&&t.kind().startsWith("item_")){
            long saved=p.getPersistentDataContainer().getOrDefault(receipt,PersistentDataType.LONG,0L);store.settle(t.id(),saved==t.id());
            if(!t.basket().isEmpty())store.releaseBasket(owner(p),t.basket());
        }
        if(allowed(p)&&(store.wallet(owner(p))>0||!store.claims(owner(p)).isEmpty()))say(p,"Tenés cosas para retirar en el Bazar.");
    }));}
    @EventHandler public void quit(PlayerQuitEvent e){inputs.remove(e.getPlayer().getUniqueId());inputDeadlines.remove(e.getPlayer().getUniqueId());lastClick.remove(e.getPlayer().getUniqueId());}
    @EventHandler(priority=EventPriority.HIGHEST) public void click(InventoryClickEvent e){
        if(!(e.getView().getTopInventory().getHolder() instanceof Screen s))return;
        e.setCancelled(true);if(!(e.getWhoClicked() instanceof Player p))return;
        if(e.getClick()!=ClickType.LEFT&&e.getClick()!=ClickType.RIGHT)return;
        long now=System.nanoTime(),prev=lastClick.getOrDefault(p.getUniqueId(),0L);if(now-prev<180_000_000L)return;lastClick.put(p.getUniqueId(),now);
        int raw=e.getRawSlot();if(raw<0)return;
        Runnable action=raw<s.inv.getSize()?(e.getClick()==ClickType.RIGHT?s.rightActions.getOrDefault(raw,s.actions.get(raw)):s.actions.get(raw)):null;
        if(action==null&&s.deposit!=null&&raw>=s.inv.getSize()&&e.getClickedInventory()==p.getInventory())action=()->s.deposit.accept(e.getSlot());
        if(action!=null){Runnable selected=action;Bukkit.getScheduler().runTask(this,()->{if(p.isOnline()&&p.getOpenInventory().getTopInventory()==s.inv)act(p,selected);});}
    }
    @EventHandler(priority=EventPriority.HIGHEST) public void drag(InventoryDragEvent e){if(e.getView().getTopInventory().getHolder() instanceof Screen)e.setCancelled(true);}
    @EventHandler public void close(InventoryCloseEvent e){if(e.getInventory().getHolder() instanceof Screen s&&!s.basket.isEmpty()&&e.getPlayer() instanceof Player p){String b=s.basket;s.basket="";try{
        store.releaseBasket(owner(p),b);for(var c:store.claims(owner(p)))if(c.product().equals("equipo")&&c.basket().isEmpty())withdraw(p,c);
    }catch(Exception ex){failure(ex);say(p,"La devolución sigue guardada; requiere revisión del administrador.");}}}
    void clock(){
        try{
            ZoneId zone=ZoneId.of(getConfig().getString("respaldo-zona","America/Argentina/Buenos_Aires"));var now=ZonedDateTime.now(zone);
            String day=now.toLocalDate().toString();LocalTime at=LocalTime.parse(getConfig().getString("respaldo-hora","04:45"));
            store.dynamicEnabled=getConfig().getBoolean("limites-dinamicos.activo",true);
            if(store.dynamicEnabled&&!now.toLocalTime().isBefore(LocalTime.parse(getConfig().getString("limites-dinamicos.hora","05:10")))) {
                long end=now.toLocalDate().atTime(LocalTime.parse(getConfig().getString("limites-dinamicos.hora","05:10"))).atZone(zone).toInstant().toEpochMilli();
                store.adjustRanges(day,end,getConfig().getDouble("limites-dinamicos.tope-maximo",3));
            }
            if(!day.equals(lastBackup)&&!now.toLocalTime().isBefore(at)){
                Path dir=getDataFolder().toPath().resolve("backups");Files.createDirectories(dir);Path dest=dir.resolve(day+".sqlite");
                if(!Files.exists(dest))Bukkit.getScheduler().runTaskAsynchronously(this,()->{try{store.backup(dest);}catch(Exception e){getLogger().log(java.util.logging.Level.SEVERE,"Fallo respaldo Bazar",e);}});
                lastBackup=day;
            }
        }catch(Exception e){getLogger().log(java.util.logging.Level.SEVERE,"Reloj Bazar",e);}
    }
    @Override public void onDisable(){
        for(Player p:Bukkit.getOnlinePlayers())if(p.getOpenInventory().getTopInventory().getHolder() instanceof Screen)p.closeInventory();
        if(store!=null)try{store.close();}catch(Exception e){getLogger().severe(e.toString());}
    }
}
