#!/usr/bin/env python3
"""Parse all DALME inventories - V2 with massive lemmatization."""
import re, csv

BASE = '/sessions/laughing-jolly-bell/mnt/PlantCypher'

# ============================================================================
# MEGA LEMMA: covers Provençal, Latin nominative+genitive, Italian, Catalan
# ============================================================================
LEMMA = {}

def add(latin, *forms):
    for f in forms:
        LEMMA[f.lower().strip()] = latin

# --- Core pharmaceutical ingredients (all variant forms) ---
add('Acacia', 'acasia', 'acassia', 'acacia', 'acacia vera')
add('Aconitum', 'aconiti', 'aconito')
add('Acorus', 'acori', 'acorus', 'radices acori', 'calami aromatici', 'calamy aromaticy', 'calami aromaticy')
add('Agaricus', 'agaric', 'agaryc', 'agarici', 'agarico', 'agarico sano', 'agarico in poluere')
add('Aloe', 'aloe', 'aloen', 'aloes', 'aloes cabalinum', 'aloes epatico', 'aloes hepaticum', 'aloe epatico pisto', 'aloe fuccotrino pisto', 'aloe succotrino', 'aloe epatico')
add('Alumen', 'alum de roqua', 'alum de plume', 'alume di rocca', 'alume di rocca adusto', 'aluminis', 'aluminis plume', 'alluminis')
add('Ammoniacum', 'armonyac', 'ammoniaco', 'ammoniacum', 'gommi armoniaci', 'gommi amoniaci', 'sal armoniac')
add('Amygdala', 'amendes doulces', 'amendas amaras', 'amandes', 'amigdon')
add('Anacardium', 'anacardy', 'anacardi', 'anacardium')
add('Anethum', 'semen aneti', 'aneti', 'grana d\'annet')
add('Anisum', 'anys cru', 'enis', 'enis confit', 'anisi', 'anisi capati', 'aniso', 'anis')
add('Antimonium', 'anthymonium', 'antimonio crudo', 'antimoni', 'antimonium')
add('Apium', 'semen apii', 'apii', 'apium')
add('Aristolochia', 'aristologia', 'aristolochie', 'radicis aristologie rotonde', 'aristologie longe', 'aristologie')
add('Artemisia', 'arthimisie', 'arthemisia', 'arthemisie')
add('Asa_foetida', 'aza fetida', 'assa fetida', 'assa phetida', 'asa fetida')
add('Asparagus', 'semen esparagi', 'speragi', 'semen speragi')
add('Auripigmentum', 'aurpiment', 'orpiment', 'orpigment')
add('Balsamum', 'balsamo', 'balsamo del peru', 'balsami', 'balsamum', 'ligni balsami', 'carpo balsami')
add('Balaustium', 'balaustes', 'balausti', 'balaustia')
add('Bdellium', 'bdellium', 'bdellii')
add('Bistorta', 'bistorta', 'bistorte')
add('Blatta_byzantia', 'blacte bysancye')
add('Bolus', 'boli armenici', 'boli armenici en pouldre', 'bolo armeno')
add('Borago', 'borraginis', 'buglosse', 'boraginis')
add('Borax', 'borrays', 'borratis', 'borace')
add('Calamus_aromaticus', 'calami aromatici', 'calamy aromaticy')
add('Calamintha', 'calamenti', 'calamento')
add('Camphora', 'camphora', 'canfora', 'camphore')
add('Cardamomum', 'cardamomy', 'cardamomi', 'cardamomum')
add('Carum', 'carvy', 'carvi')
add('Caryophyllus', 'giroffles', 'garofoli', 'gariofili', 'garyophillorum', 'caryophilli')
add('Cassia_fistula', 'cassia fistula', 'cassia fistule', 'cassia fistula mundata', 'cassie', 'cassie cum sacharo', 'cassie cum melle')
add('Cassia_lignea', 'cassia lignea', 'cassie lignee')
add('Castoreum', 'castoryum', 'castoreum', 'castorei', 'castoreo')
add('Centaurea', 'centaurei')
add('Cerusa', 'ceruse', 'cerusa', 'ceruze', 'ceruse lote')
add('Chamomilla', 'camamille', 'camomille', 'camomilla', 'camomille romane')
add('Cinnamomum', 'cynamomy', 'cinnamomum', 'canella', 'canelle', 'cinnamomi', 'cannella')
add('Colocynthis', 'coloquintida', 'coloquintide', 'coloquintidis', 'pulpe coloquintide')
add('Colophonia', 'calofonia', 'colophonia')
add('Corallium', 'coral blanc', 'coral rouge', 'coralh', 'corallii', 'corallo')
add('Coriandrum', 'colyandre', 'coriandri', 'coriandre')
add('Costus', 'costus', 'costi dulci', 'costi')
add('Cubeba', 'cubebes', 'cubebe', 'cubeborum')
add('Cuminum', 'comin', 'cumini', 'cymini', 'cumino')
add('Cuscuta', 'cuscute', 'cuscuta')
add('Cyclamen', 'panis porcinis')
add('Cyperus', 'radicis cypery', 'ciperi', 'cyperus')
add('Daucus', 'semen dauci', 'semen daulcy', 'dauci')
add('Dictamnus', 'radices diptamy', 'diptami', 'dittamo')
add('Doronicum', 'deronicy', 'doronici')
add('Euphorbia', 'euforbium', 'euforbe', 'euphorbii', 'euforbio', 'euphorbio')
add('Euphorbia_esula', 'ezula', 'esula', 'esula maior')
add('Foeniculum', 'fenolh', 'feniculi', 'fenuculi', 'semen fenuculi', 'fenochio')
add('Fumaria', 'fumoterre', 'fumiterre', 'fummis terre', 'fumis terre')
add('Galbanum', 'galbanum', 'galbani')
add('Galanga', 'galanga', 'galange', 'galanga minor')
add('Galla', 'galles', 'galles de romanye', 'gallorum', 'galle')
add('Gentiana', 'genciana', 'gentiana', 'gentiane')
add('Glycyrrhiza', 'succis liquirencis', 'liquiritia', 'regolizia', 'liquiritie', 'succi liquiritie')
add('Gummi_arabicum', 'gomma arabica', 'gommi arabici', 'gomma arabiga')
add('Helleborus', 'ellebory nigri', 'ellebori albi', 'elebori nigri', 'elebori albi', 'elleboro')
add('Hermodactylus', 'ermodaptily', 'hermodactillorum', 'ermodattili')
add('Hyoscyamus', 'semen jusquiamy', 'jusquiami', 'giusquiamo')
add('Hyssopus', 'hyssopi', 'hyssopus', 'hyssopus humida', 'ysopi', 'hisopo')
add('Inula', 'enulla campana', 'enule campane')
add('Iris', 'yreos', 'iris', 'yridis', 'yridis florentie', 'ireos')
add('Juniperus', 'genibre', 'ginepro', 'juniperi', 'semen juniperi')
add('Lactuca', 'semen lectuce', 'lactuce', 'lattuca')
add('Ladanum', 'lagdanum', 'laudano', 'ladani')
add('Lapis_lazuli', 'lapis lazuli')
add('Lavandula', 'spica romana', 'spic', 'lavanda', 'spica', 'olei de spica')
add('Lignum_aloes', 'lignum aloes', 'ligni aloes')
add('Linum', 'grane de lyn', 'lini')
add('Lithospermum', 'semen millium folis')
add('Macis', 'macys', 'macis', 'mace')
add('Magnes', 'lapis magnetici', 'calamita')
add('Mandragora', 'cortices mandragore', 'mandragore', 'semen mandragule', 'mandragora')
add('Mastix', 'mastic', 'mastice', 'mastich', 'masticis')
add('Mel', 'mel', 'melle', 'mellis rosati', 'mellis violati', 'mel anthozati', 'mellis antbosati', 'miel')
add('Melilotum', 'flor de melliloth', 'melliloto', 'melliloti')
add('Mentha', 'mente', 'menthe', 'menta')
add('Mumia', 'momye', 'mumia', 'mumie')
add('Myrobalanus', 'mirabolans', 'myrabolanorum citrinorum', 'myrabolanorum indorum', 'myrabolanorum chebulorum', 'myrabolanorum emblicorum', 'mirabolan')
add('Myrrha', 'mirra', 'mirre', 'myrre', 'mirra eletta', 'myrrhae')
add('Myrtus', 'grana de nerta', 'myrtillorum', 'mirtillorum', 'mortella')
add('Nardus', 'spicanardy', 'spice nardi', 'spica nardi', 'nardi', 'spigo nardo')
add('Nigella', 'semen geth', 'semen giti', 'nigella')
add('Nux_moschata', 'nozes muscades', 'noce moscata', 'nucis muscate', 'nux moschata')
add('Nymphaea', 'nenupharis', 'nenufar')
add('Olibanum', 'ensens', 'ensens bon', 'ensens menut', 'olibanum', 'incenso', 'thuris')
add('Opium', 'opium', 'opio', 'opii')
add('Origanum', 'origanum', 'origani', 'origano')
add('Paeonia', 'radices pyonye', 'semen pyonie', 'peonie', 'semen peonie', 'peonia')
add('Papaver', 'semen papaveris', 'semen papaveris nigri', 'semen papaveris albi', 'papaveris')
add('Petroselinum', 'persine', 'petroselinum', 'petroselini', 'petrosilie')
add('Piper', 'pebre', 'pepe', 'piper', 'piperis')
add('Plantago', 'semen plantaginis', 'plantaginis', 'plantago')
add('Polypodium', 'polipody', 'polipodio', 'polipodi quircini', 'polipodii')
add('Portulaca', 'semen portulace', 'portulace')
add('Pyrethrum', 'piretri', 'piretro')
add('Rhabarbarum', 'reubarby', 'reubarbe', 'reubarbaro', 'rabarbaro', 'rhabarbari')
add('Rhaponticum', 'reuponticum', 'rhaponticum', 'rhapontico')
add('Rosa', 'roze seca', 'rose', 'rosis', 'rosarum', 'rosa')
add('Rubia', 'rubea maior', 'grana tinctorum', 'rubee tintorum', 'rubee tinctorum')
add('Ruta', 'ruta', 'ruthe', 'rhute', 'ruyte')
add('Sagapenum', 'sagapenum', 'sagapeni')
add('Sal', 'sal', 'salis geme', 'salis gemme', 'sal gemma')
add('Santalum', 'sandalys', 'sandalis', 'sandili', 'sandali rubei', 'sandali albi', 'santalum', 'sandalo')
add('Sanguis_draconis', 'sang de dragon', 'sangue di drago', 'sanguinis draconis', 'sanguinis draconis fin')
add('Sarcocolla', 'cercacola', 'sercacollo', 'sarcocolla')
add('Scammonia', 'escamonea', 'scammonii', 'scamonea')
add('Senna', 'sene', 'sena', 'senne', 'sene mundati')
add('Siler', 'sileris montany', 'semen sileris montani', 'sileris')
add('Spodium', 'espodyum', 'spodium', 'spodii')
add('Squilla', 'escalholle', 'squille', 'scille')
add('Squinanthum', 'squinanto', 'squinanti', 'squinanthi')
add('Staphisagria', 'stafisagrea', 'semen staphisagrie', 'stafisagria')
add('Storax', 'storax', 'storax rubea', 'storace', 'storacis rubei', 'storacis calamite', 'storacis liquide')
add('Sulfur', 'sonffre', 'souffre', 'solfo', 'solphre jaulne', 'sulfuris')
add('Sumac', 'sumac', 'sumach', 'sommaco')
add('Terebinthina', 'trebentine', 'trementina', 'terebintina')
add('Terra_sigillata', 'terra sigillata', 'terra sigillata vera', 'terra sigilata')
add('Tragacanthum', 'gomma dragant', 'gommi dragacanthi', 'gomme dragant', 'dragaganti', 'tragacanthi')
add('Trigonella', 'senigrec', 'fenugrec', 'fenugrecy', 'fenu greco')
add('Turbith', 'turby', 'turbith', 'turbit', 'turbithi')
add('Tutia', 'thutye', 'tuthie', 'tuthia', 'tutia')
add('Viola', 'flor de violetas', 'violarum', 'viola', 'violette')
add('Vitex', 'agnus castus', 'semen agni casti', 'seminis vitice')
add('Zedoaria', 'zedoarium', 'zedoaria', 'zedoarie')
add('Zingiber', 'gingibre', 'zenzero', 'zinziber', 'zinziber vert', 'zingiberis')
add('Nux_indica', 'nucis iudice')
add('Cera', 'cere albe', 'ciera', 'cyera', 'cera')

def lemmatize(name):
    nl = name.lower().strip()
    nl = re.sub(r'^(item\s+plus\s+|plus\s+|item\s+|primo\s+)', '', nl)
    nl = re.sub(r'\s+', ' ', nl).strip()
    # Remove trailing weights
    nl = re.sub(r'\s+\d+\s*(ll|on|qr|℥|ʒ).*$', '', nl)
    nl = re.sub(r'\s+(en\s+)?(deux|trois|quatre)\s+potz.*$', '', nl)
    nl = nl.strip()

    if nl in LEMMA: return LEMMA[nl]
    # Try without trailing 's', 'i', 'is', 'ii', 'orum'
    for suffix in ['orum', 'arum', 'ii', 'is', 'i', 'um', 'ae', 'e', 's']:
        if nl.endswith(suffix) and nl[:-len(suffix)] in LEMMA:
            return LEMMA[nl[:-len(suffix)]]
    # Partial match (longest key first)
    for key in sorted(LEMMA.keys(), key=len, reverse=True):
        if key in nl and len(key) > 4:
            return LEMMA[key]
    return None

def categorize(name):
    nl = name.lower()
    if re.match(r'^(aqua |aygua |acque |aquae )', nl): return 'AQUA'
    if re.match(r'^(ol[eiy] |oley |oleo |oleum |olei )', nl): return 'OLEUM'
    if re.match(r'^(unguent|onguent|ungento)', nl): return 'UNGUENT'
    if re.match(r'^(empiast|emplast|ceroto|ceroti|cerotum)', nl): return 'EMPLASTRUM'
    if re.match(r'^(conserv|corticis .* conditi)', nl): return 'CONSERVA'
    if re.match(r'^(syrup|cirup|cyrup|sirop|yssarop|ycirop)', nl): return 'CYRUPUS'
    if re.match(r'^(pillul)', nl): return 'PILLULA'
    if re.match(r'^(pulvi|polver|podre|pouldre)', nl): return 'PULVIS'
    if re.match(r'^(troci|trocis|trochis)', nl): return 'TROCISCUS'
    if re.match(r'^(lapis |lapidis )', nl): return 'LAPIS'
    if re.match(r'^(dya |dia |electuar|confectio|iera |triffera|triphera|hocsimel|oximel|lohoc|metridat|theriaca|triaca|benedicte|dyamoron|dyaprunis|aurea |athenasia|manus christi)', nl): return 'ELECTUARIUM'
    if re.match(r'^(mel |mell)', nl): return 'CONFITURE'
    if re.match(r'^(axungi|medule |grassa )', nl): return 'GRAISSE'
    if re.match(r'^(semen |grana |seminis )', nl): return 'SEMEN'
    if re.match(r'^(succi |succis )', nl): return 'SUCCUS'
    if re.match(r'^(radicis |radices )', nl): return 'RADIX'
    return 'SIMPLE'

# ============================================================================
# PARSERS
# ============================================================================

def read_file(name):
    with open(f'{BASE}/{name}', 'r', encoding='utf-8') as f:
        return f.read()

def is_junk(line):
    """Filter out weight-only lines, blanks, section headers."""
    l = line.strip()
    if not l: return True
    if 'blank line' in l: return True
    if l.startswith('==='): return True
    if re.match(r'^[\d\s.¼½¾,]+$', l): return True
    if re.match(r'^\d+\s*(ll|on|qr|℥|ʒ|b\.)', l): return True
    if re.match(r'^(ll|on|qr)\s', l): return True
    if re.match(r'^½\s*(ll|on|qr|℥)', l): return True
    if re.match(r'^¼', l): return True
    if len(l) < 3: return True
    return False

def parse_greoux():
    items = []
    text = read_file('dalme_Inventory_of_Rostaing_de_Gr_oux.txt')
    skip_starts = ['Sensuit', 'Rostang', 'Jacques', 'Premierement', 'Les ', 'Las ', 'Lo ', 'Et ', 'tout au poys', 'Simples net', 'Confitures', 'Tres potz', 'panis tout', 'ensemble']

    for line in text.split('\n'):
        line = line.strip()
        if is_junk(line): continue
        if any(line.startswith(s) for s in skip_starts): continue
        # Remove weight from end
        name = re.sub(r'\s+\d+\s*(ll|on|℥|ʒ).*$', '', line)
        name = re.sub(r'\s+$', '', name)
        if len(name) > 2 and not re.match(r'^\d', name) and name not in ['net', 'tout']:
            items.append(name)
    return items

def parse_villa():
    items = []
    text = read_file('dalme_Inventory_of_the_boutique_of_Steve_Villa.txt')
    for line in text.split('\n'):
        line = line.strip()
        if is_junk(line): continue
        # "Item plus NAME" pattern
        m = re.match(r'^(?:Item\s+plus\s+|Item\s+)(.+?)$', line)
        if m:
            name = m.group(1).strip()
            name = re.sub(r'\s+[\dIVXL½¼¾]+\s*(℥|ʒ|qr|ll|lb|quar).*$', '', name)
            name = re.sub(r'\s+$', '', name)
            if len(name) > 2:
                items.append(name)
    return items

def parse_cambarelli():
    items = []
    text = read_file('dalme_Inventory_of_the_shop_of_Johannes_Cambarelli.txt')
    # Split concatenated items
    for line in text.split('\n'):
        line = line.strip()
        if is_junk(line): continue
        # Split on known prefixes
        parts = re.split(r'(?=(?:Siropus |Sirupus |Oley? |Melle |Diamoro|Diaprunis|Sandilis|Squinanti|Plonbi|Lapis |Plus |Oximel))', line)
        for part in parts:
            part = part.strip()
            if not part or is_junk(part): continue
            name = re.sub(r'\s+[\dIVXL½]+\s*(ll|℥|qr|on|gros|Fl|Cls|Cl).*$', '', part)
            name = re.sub(r'^\.\d+\.\s*', '', name)
            name = re.sub(r'\s+$', '', name)
            if len(name) > 2 and not re.match(r'^(Anno |Hec |dicta|notum|Actum|Item en |Item hun |Item dos|Item una|Item unes|Item tres|Item sis|Item cinch|Item quatre|Item vuit|Primo una|N\. |In villa|Noverint|ego |cupiens|propter|viri mei|expressum|post |Primo hun|Item ung|Iten hun)', name):
                items.append(name)
    return items

def parse_rome1674():
    items = []
    text = read_file('dalme_A_table_of_prices_of_medicines_in_Rome_1674.txt')
    skip_starts = ['TAVOLA', 'Alli ', 'Dal ', 'Auanti', 'IN ROMA', 'Nella', 'Con ', 'Prezzi', 'C1', 'ACque', 'Nota', 'Modo', 'half page', '.']
    skip_sections = ['Acque Termali', 'Acque Stillate', 'Herbe secche', 'Radiche', 'Semi', 'Scorze', 'Fiori', 'Frutti', 'Legni', 'Gomme', 'Succi', 'Animali', 'Minerali', 'Pietre', 'Composti', 'Sciroppi', 'Olij', 'Vnguenti', 'Cerotti', 'Empiastri', 'Pillole', 'Trocisci', 'Polueri', 'Elettuarij', 'Confettioni', 'Prezzi de medicinali']

    for line in text.split('\n'):
        line = line.strip()
        if is_junk(line): continue
        if any(line.startswith(s) for s in skip_starts): continue
        if any(line == s for s in skip_sections): continue
        # Skip thermal water locations
        if re.match(r'^(Del |Della |Di |Dello )', line) and len(line) < 25: continue
        # Skip price-only
        if re.match(r'^b[\.\s]*\d', line): continue

        name = re.sub(r'\s+b[\.\s]*\d.*$', '', line)
        name = re.sub(r'\s+(la |l\'|il |per |lo ).*$', '', name)
        name = re.sub(r'\s+$', '', name)
        if len(name) > 2 and not re.match(r'^\d', name) and name != 'mo':
            items.append(name)
    return items

def parse_coll():
    items = []
    text = read_file('dalme_Inventory_of_Guillem_Coll.txt')
    pharma_kw = ['gingibre', 'scorsa', 'sucre', 'confits', 'conserv', 'sirop', 'cerda', 'alembich', 'Nicolau', 'Mesue', 'medecina', 'torrons', 'enguents', 'exerops', 'cere', 'saffran']
    for line in text.split('\n'):
        parts = re.split(r'(?=Item )', line)
        for part in parts:
            if any(k.lower() in part.lower() for k in pharma_kw):
                name = re.sub(r'^Item\s+', '', part.strip())
                name = re.sub(r'\s+$', '', name)
                if len(name) > 3:
                    items.append(name)
    return items

def parse_miquella():
    items = []
    text = read_file('dalme_Inventory_of_the_shop_of_Donna_Miquella.txt')
    pharma = ['conserve rosarum', 'barbotina confida', 'litargiri auri', 'senisa', 'torbit', 'pillulle balsami', 'macis', 'saffran', 'triacla', 'ciera verda gomada', 'Mesue']
    for pat in pharma:
        if pat.lower() in text.lower():
            items.append(pat)
    return items

# ============================================================================
# RUN
# ============================================================================
parsers = {
    'Rostaing de Greoux (Manosque, 1547)': parse_greoux,
    'Steve Villa (Aix, 1506)': parse_villa,
    'Johannes Cambarelli (Marseille, 1432)': parse_cambarelli,
    'Rome Price Table (1674)': parse_rome1674,
    'Guillem Coll (Girona, 1454)': parse_coll,
    'Donna Miquella (Avignon, 1492)': parse_miquella,
}

all_unified = []
inventory_stats = {}

for inv_name, parser_fn in parsers.items():
    print(f"\n{'='*60}")
    print(f"{inv_name}")
    print(f"{'='*60}")
    raw = parser_fn()
    print(f"Raw items: {len(raw)}")

    processed = []
    for item in raw:
        cat = categorize(item)
        latin = lemmatize(item)
        processed.append({
            'Inventaire': inv_name,
            'Item_Original': item,
            'Latin_Standard': latin if latin else '',
            'Categorie': cat,
        })
        all_unified.append(processed[-1])

    # Stats
    resolved = [p for p in processed if p['Latin_Standard']]
    latin_set = sorted(set(p['Latin_Standard'] for p in resolved))
    cats = {}
    for p in processed:
        cats[p['Categorie']] = cats.get(p['Categorie'], 0) + 1

    print(f"Resolved: {len(resolved)} / {len(processed)} ({100*len(resolved)/max(1,len(processed)):.0f}%)")
    print(f"Unique Latin: {len(latin_set)}")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:8]:
        print(f"  {cat}: {count}")
    inventory_stats[inv_name] = {'total': len(processed), 'resolved': len(resolved), 'unique_latin': len(latin_set), 'latin_set': latin_set}

# Save unified CSV
output = f'{BASE}/dalme_all_inventories_unified.csv'
with open(output, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Inventaire', 'Item_Original', 'Latin_Standard', 'Categorie'])
    for p in all_unified:
        w.writerow([p['Inventaire'], p['Item_Original'], p['Latin_Standard'], p['Categorie']])

print(f"\n{'='*60}")
print(f"TOTAL: {len(all_unified)} items from {len(parsers)} inventories")
print(f"Saved: {output}")

# AN cross-reference
an_top = ['Myrrha', 'Amomum', 'Cinnamomum', 'Aloe', 'Crocus', 'Anisum', 'Zingiber',
          'Mastix', 'Foeniculum', 'Rosa', 'Cardamomum', 'Lavandula', 'Caryophyllus',
          'Opium', 'Mel', 'Glycyrrhiza', 'Petroselinum', 'Euphorbia', 'Rhabarbarum',
          'Gentiana', 'Camphora', 'Plantago', 'Hyssopus', 'Viola', 'Papaver',
          'Costus', 'Nardus', 'Piper', 'Galanga', 'Aristolochia', 'Acorus',
          'Galbanum', 'Ammoniacum', 'Olibanum', 'Tragacanthum', 'Colocynthis',
          'Mandragora', 'Hyoscyamus', 'Cassia_lignea', 'Rhaponticum']

print(f"\n{'='*60}")
print("AN TOP 40 CROSS-REFERENCE")
print(f"{'='*60}")

for inv_name in parsers:
    inv_latin = inventory_stats[inv_name]['latin_set']
    found = [lat for lat in an_top if lat in inv_latin]
    print(f"\n{inv_name}: {len(found)}/{len(an_top)}")
    if found:
        print(f"  {', '.join(sorted(found))}")

# Also show ALL unique Latin across all inventories
all_latin_set = set()
for stats in inventory_stats.values():
    all_latin_set.update(stats['latin_set'])
print(f"\nTotal unique Latin across all DALME inventories: {len(all_latin_set)}")
found_total = [lat for lat in an_top if lat in all_latin_set]
print(f"AN top 40 found in at least one inventory: {len(found_total)}/{len(an_top)}")
print(f"  {', '.join(sorted(found_total))}")
