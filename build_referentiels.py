"""
Build PURE medieval pharmacopoeia reference datasets.
NO Voynich data. Historical truth only.
Sources: AN, CI, Grabadin, Macer, DALME, Alphita, Avicenna.
"""
import json, csv, re
from collections import Counter, defaultdict

OUTDIR = 'datasets'

# ================================================================
# R01_VERBS — All pharmaceutical verbs from medieval sources
# ================================================================

R01 = {
    "_meta": {
        "description": "Pharmaceutical verbs of medieval Latin and vernacular traditions (12th-15th c.)",
        "sources": [
            "Antidotarium Nicolai (van den Berg 1917)",
            "Circa Instans (Dorveaux 1913)",
            "Grabadin / Liber Servitoris (Al-Zahrawi)",
            "Macer Floridus (Choulant 1832)",
            "Ricettario Fiorentino (1498)",
            "Compendium Aromatariorum (Saladino 1488)"
        ],
        "version": "2026-04-11"
    },
    # --- CORE PREPARATION VERBS ---
    "V_recipe": {
        "ref_id": "V_recipe", "canonical": "recipe", "gloss_en": "take/prepare", "gloss_fr": "prends",
        "forms": {"latin": ["recipe", "recipiat", "recipiatur", "recipiantur", "accipe", "accipiat"],
                  "old_french": ["prenez", "pren", "pernez"], "italian": ["prendi", "recipe", "ricevi"],
                  "middle_dutch": ["nemt"], "abbreviation": ["Rp.", "R."]},
        "pos": "verb_imperative", "frequency": {"AN": 137, "CI": 365},
        "notes": "Universal opening verb of every recipe. Abbreviated Rp. in manuscripts.",
        "sources_attested": ["AN", "CI", "Grabadin", "Macer", "Ricettario Fiorentino"]
    },
    "V_misce": {
        "ref_id": "V_misce", "canonical": "misce", "gloss_en": "mix/blend", "gloss_fr": "melange",
        "forms": {"latin": ["misce", "misceatur", "misceantur", "commisce", "commisceatur", "incorpora", "incorporetur"],
                  "old_french": ["meslez", "melliz"], "italian": ["mescola", "mischia"],
                  "abbreviation": ["M."]},
        "pos": "verb_imperative", "frequency": {"AN": 72, "CI": 50},
        "notes": "Core mixing verb. Often final instruction.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_tere": {
        "ref_id": "V_tere", "canonical": "tere", "gloss_en": "grind/crush", "gloss_fr": "broie/pile",
        "forms": {"latin": ["tere", "terantur", "teratur", "contere", "contundantur", "contundatur", "trita", "tritum", "tritus", "pulveriza", "pulverizetur"],
                  "old_french": ["tribliz", "triblez", "pilez", "broiez"], "italian": ["pesta", "trita", "macina"]},
        "pos": "verb_imperative", "frequency": {"AN": 89, "CI": 80},
        "notes": "Grinding in mortar. 'terantur' = most common passive form in AN. 89/137 AN recipes.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_coque": {
        "ref_id": "V_coque", "canonical": "coque", "gloss_en": "cook/boil", "gloss_fr": "cuis",
        "forms": {"latin": ["coque", "coquatur", "coquantur", "coctum", "cocta", "coctus", "decoque", "decoquatur", "bulliat", "bulliatur", "fac bullire"],
                  "old_french": ["cuire", "cuite", "cuisiez", "faites cuire", "cuisez"],
                  "italian": ["cuoci", "cuocere", "cotto", "bollire"]},
        "pos": "verb_imperative", "frequency": {"AN": 45, "CI": 175},
        "notes": "Core cooking verb. Often cum (with) + liquid (aqua, vino). decoque = decoct (reduce by boiling).",
        "sources_attested": ["AN", "CI", "Grabadin", "Macer"]
    },
    "V_cola": {
        "ref_id": "V_cola", "canonical": "cola", "gloss_en": "strain/filter", "gloss_fr": "filtre/passe",
        "forms": {"latin": ["cola", "coletur", "colentur", "colatum", "colata"],
                  "old_french": ["coulez", "colez"], "italian": ["cola", "colate"]},
        "pos": "verb_imperative", "frequency": {"AN": 31, "CI": 40},
        "notes": "Straining through cloth (per pannum). After cooking/infusing.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_solve": {
        "ref_id": "V_solve", "canonical": "solve", "gloss_en": "dissolve", "gloss_fr": "dissous",
        "forms": {"latin": ["solve", "solvatur", "solvantur", "solutum", "soluta", "dissolve", "dissolvatur"],
                  "old_french": ["fondez", "destemperez"], "italian": ["dissolvi", "sciogli"]},
        "pos": "verb_imperative", "frequency": {"AN": 20, "CI": 15},
        "notes": "Dissolving in liquid. solve in aqua/vino.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_infunde": {
        "ref_id": "V_infunde", "canonical": "infunde", "gloss_en": "infuse/steep", "gloss_fr": "infuse/trempe",
        "forms": {"latin": ["infunde", "infundatur", "infundantur", "infusum", "infusa", "macera", "maceretur"],
                  "old_french": ["trempez", "metez tremper"], "italian": ["infundi", "macera"]},
        "pos": "verb_imperative", "frequency": {"AN": 15, "CI": 25},
        "notes": "Steeping in liquid. Often overnight (per noctem).",
        "sources_attested": ["AN", "CI"]
    },
    "V_funde": {
        "ref_id": "V_funde", "canonical": "funde", "gloss_en": "pour", "gloss_fr": "verse",
        "forms": {"latin": ["funde", "fundatur", "effunde", "effundatur", "superfunde"],
                  "old_french": ["versez", "getez"], "italian": ["versa"]},
        "pos": "verb_imperative", "frequency": {"AN": 10, "CI": 20},
        "notes": "Pouring liquid. superfunde = pour over.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_pone": {
        "ref_id": "V_pone", "canonical": "pone", "gloss_en": "place/put", "gloss_fr": "mets/place",
        "forms": {"latin": ["pone", "ponatur", "ponantur", "positum", "impone", "imponatur", "superpone"],
                  "old_french": ["metez", "metez desus", "metez dedenz"], "italian": ["poni", "metti"]},
        "pos": "verb_imperative", "frequency": {"AN": 25, "CI": 422},
        "notes": "Placing ingredient in vessel, on wound, etc. metez is the #1 CI verb.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_adde": {
        "ref_id": "V_adde", "canonical": "adde", "gloss_en": "add", "gloss_fr": "ajoute",
        "forms": {"latin": ["adde", "addatur", "addantur", "additum", "adiunge", "adiice"],
                  "old_french": ["ajostez", "metez"], "italian": ["aggiungi"]},
        "pos": "verb_imperative", "frequency": {"AN": 30, "CI": 20},
        "notes": "Adding ingredient to mixture. adde X ad Y.",
        "sources_attested": ["AN", "CI"]
    },
    "V_liquefac": {
        "ref_id": "V_liquefac", "canonical": "liquefac", "gloss_en": "melt/liquefy", "gloss_fr": "fonds/liquefie",
        "forms": {"latin": ["liquefac", "liquefiat", "liquefactum", "liquefacta"],
                  "old_french": ["fondez"], "italian": ["liquefa", "fondi"]},
        "pos": "verb_imperative", "frequency": {"AN": 15, "Grabadin": 40},
        "notes": "Melting wax, fat, resin. liquefac super ignem lentum (melt over slow fire).",
        "sources_attested": ["AN", "Grabadin"]
    },
    "V_exprime": {
        "ref_id": "V_exprime", "canonical": "exprime", "gloss_en": "press out/squeeze", "gloss_fr": "exprime/presse",
        "forms": {"latin": ["exprime", "exprimatur", "expressum", "pressa"],
                  "old_french": ["premez", "pressez", "espraignez"], "italian": ["spremi"]},
        "pos": "verb_imperative", "frequency": {"AN": 8, "CI": 30},
        "notes": "Pressing juice from herbs. Often succum exprime.",
        "sources_attested": ["AN", "CI"]
    },
    "V_incide": {
        "ref_id": "V_incide", "canonical": "incide", "gloss_en": "cut/chop", "gloss_fr": "coupe/taille",
        "forms": {"latin": ["incide", "incidantur", "incidatur", "concide", "minue", "minutim"],
                  "old_french": ["tailliez", "detrenchiz", "copez"], "italian": ["taglia", "trita"]},
        "pos": "verb_imperative", "frequency": {"AN": 12, "CI": 25},
        "notes": "Cutting herbs before processing. minutim = finely.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "V_ablue": {
        "ref_id": "V_ablue", "canonical": "ablue", "gloss_en": "wash", "gloss_fr": "lave",
        "forms": {"latin": ["ablue", "abluatur", "abluantur", "ablutum", "abluta", "lava", "lavetur"],
                  "old_french": ["lavez"], "italian": ["lava"]},
        "pos": "verb_imperative", "frequency": {"AN": 10, "CI": 36},
        "notes": "Washing ingredients or wound. ablue cum aqua.",
        "sources_attested": ["AN", "CI"]
    },
    # --- DISPENSING VERBS ---
    "V_da": {
        "ref_id": "V_da", "canonical": "da", "gloss_en": "give/administer", "gloss_fr": "donne",
        "forms": {"latin": ["da", "detur", "datur", "dentur", "dantur", "exhibe", "exhibeatur", "propina", "propinetur"],
                  "old_french": ["donez", "donez a boivre"], "italian": ["dai", "somministra"]},
        "pos": "verb_imperative", "frequency": {"AN": 118, "CI": 212},
        "notes": "Administering to patient. detur cum vino/aqua. datur = is given.",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_fiat": {
        "ref_id": "V_fiat", "canonical": "fiat", "gloss_en": "let it be made", "gloss_fr": "qu'il soit fait",
        "forms": {"latin": ["fiat", "fiant", "conficiatur", "conficiantur", "dispensentur", "dispensetur", "formetur", "formentur"],
                  "old_french": ["faites", "soit fait"], "italian": ["sia fatto"],
                  "abbreviation": ["ft."]},
        "pos": "verb_subjunctive", "frequency": {"AN": 198, "CI": 292},
        "notes": "Final instruction. fiat electuarium/unguentum/emplastrum. ft. = abbreviation.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
    # --- PROPERTY/EFFECT VERBS ---
    "V_valet": {
        "ref_id": "V_valet", "canonical": "valet", "gloss_en": "is effective against", "gloss_fr": "vaut contre",
        "forms": {"latin": ["valet", "prodest", "confert", "iuvat", "auxiliatur"],
                  "old_french": ["vaut", "valt", "est bon"], "italian": ["vale", "giova"]},
        "pos": "verb_indicative", "frequency": {"AN": 155, "CI": 300},
        "notes": "Introduces therapeutic indication. valet contra/ad + disease.",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_purgat": {
        "ref_id": "V_purgat", "canonical": "purgat", "gloss_en": "purges/cleanses", "gloss_fr": "purge",
        "forms": {"latin": ["purgat", "purgatur", "mundificat", "mundificatur", "abstergit", "evacuat"],
                  "old_french": ["purge", "nettoie"], "italian": ["purga"]},
        "pos": "verb_indicative", "frequency": {"AN": 104, "CI": 60},
        "notes": "Purgative action. Key concept in humoral medicine.",
        "sources_attested": ["AN", "CI", "Macer", "Avicenna"]
    },
    "V_confortat": {
        "ref_id": "V_confortat", "canonical": "confortat", "gloss_en": "strengthens", "gloss_fr": "conforte/renforce",
        "forms": {"latin": ["confortat", "confortatur", "roborat", "firmat", "corroborat"],
                  "old_french": ["conforte", "renforce"], "italian": ["conforta"]},
        "pos": "verb_indicative", "frequency": {"AN": 40, "CI": 50},
        "notes": "Strengthening organ/body. confortat stomachum/cerebrum.",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_provocat": {
        "ref_id": "V_provocat", "canonical": "provocat", "gloss_en": "provokes/stimulates", "gloss_fr": "provoque",
        "forms": {"latin": ["provocat", "movet", "excitat", "stimulat"],
                  "old_french": ["esmeut", "provoque"], "italian": ["provoca"]},
        "pos": "verb_indicative", "frequency": {"AN": 20, "CI": 60},
        "notes": "provocat urinam/menstrua/sudorem. Key pharma concept.",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_sanat": {
        "ref_id": "V_sanat", "canonical": "sanat", "gloss_en": "heals/cures", "gloss_fr": "guerit/soigne",
        "forms": {"latin": ["sanat", "curat", "medetur", "remediat"],
                  "old_french": ["garist", "sane"], "italian": ["sana", "guarisce"]},
        "pos": "verb_indicative", "frequency": {"AN": 30, "CI": 80},
        "notes": "General healing. sanat vulnera/ulcera.",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_ungue": {
        "ref_id": "V_ungue", "canonical": "ungue", "gloss_en": "anoint/apply ointment", "gloss_fr": "oins",
        "forms": {"latin": ["ungue", "ungatur", "inunge", "inungatur", "lini", "liniatur", "illini"],
                  "old_french": ["oigniez", "enoingnez"], "italian": ["ungi"]},
        "pos": "verb_imperative", "frequency": {"AN": 15, "CI": 79},
        "notes": "Applying ointment/oil to body. oigniez = 4th most common CI verb.",
        "sources_attested": ["AN", "CI"]
    },
    "V_bibe": {
        "ref_id": "V_bibe", "canonical": "bibe", "gloss_en": "drink", "gloss_fr": "bois",
        "forms": {"latin": ["bibe", "bibat", "bibatur", "potetur", "sumat", "sumatur", "sumitur"],
                  "old_french": ["bevez", "boivre", "beu"], "italian": ["bevi"]},
        "pos": "verb_imperative", "frequency": {"AN": 30, "CI": 100},
        "notes": "Taking medicine orally. bibe/sumat cum vino/aqua.",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_sicca": {
        "ref_id": "V_sicca", "canonical": "sicca", "gloss_en": "dry", "gloss_fr": "seche",
        "forms": {"latin": ["sicca", "siccetur", "siccentur", "desiccatur", "exsicca"],
                  "old_french": ["seichiez", "faites secher"], "italian": ["secca"]},
        "pos": "verb_imperative", "frequency": {"AN": 8, "CI": 15},
        "notes": "Drying herbs before grinding. In shade (in umbra) or sun (in sole).",
        "sources_attested": ["AN", "CI", "Macer"]
    },
    "V_cribra": {
        "ref_id": "V_cribra", "canonical": "cribra", "gloss_en": "sift/sieve", "gloss_fr": "tamise",
        "forms": {"latin": ["cribra", "cribretur", "cribrentur", "cerne", "cernatur"],
                  "old_french": ["tamisez", "buletez"], "italian": ["setaccia"]},
        "pos": "verb_imperative", "frequency": {"AN": 10, "CI": 8},
        "notes": "Sifting powder after grinding. per setaceum/cribrum.",
        "sources_attested": ["AN", "CI", "Grabadin"]
    },
}

with open('%s/R01_verbs.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(R01, f, indent=2, ensure_ascii=False)
print('R01_verbs.json: %d verbs' % (len(R01) - 1))  # minus _meta

# ================================================================
# R03_UNITS — Weights, measures, abbreviations
# ================================================================

R03 = {
    "_meta": {
        "description": "Medieval pharmaceutical weights, measures, and dose markers",
        "sources": ["AN (van den Berg 1917)", "Compendium Aromatariorum (Saladino 1488)", "CI (Dorveaux 1913)"],
        "version": "2026-04-11"
    },
    # --- WEIGHTS ---
    "U_granum": {
        "ref_id": "U_granum", "canonical": "granum", "gloss_en": "grain", "type": "weight",
        "forms": {"latin": ["granum", "grani", "grana", "granorum"], "old_french": ["grain", "grains", "corne", "cornes"],
                  "abbreviation": ["gr.", "g."]},
        "weight_grams": 0.065, "subdivisions": "smallest unit",
        "sources_attested": ["AN", "CI", "Compendium"]
    },
    "U_scrupulus": {
        "ref_id": "U_scrupulus", "canonical": "scrupulus", "gloss_en": "scruple", "type": "weight",
        "forms": {"latin": ["scrupulus", "scrupuli", "scrupulum", "scrupulos"],
                  "abbreviation": ["scr.", "3"]},
        "weight_grams": 1.3, "subdivisions": "1 scrupulus = 20 grana",
        "sources_attested": ["AN", "Compendium"]
    },
    "U_drachma": {
        "ref_id": "U_drachma", "canonical": "drachma", "gloss_en": "drachm", "type": "weight",
        "forms": {"latin": ["drachma", "drachmam", "drachmas", "drachmae", "dragma", "dragmam"],
                  "old_french": ["drame", "dragme", "drames"], "abbreviation": [".z.", "dr.", "3"]},
        "weight_grams": 3.9, "subdivisions": "1 drachma = 3 scrupuli = 60 grana",
        "sources_attested": ["AN", "CI", "Compendium"]
    },
    "U_uncia": {
        "ref_id": "U_uncia", "canonical": "uncia", "gloss_en": "ounce", "type": "weight",
        "forms": {"latin": ["uncia", "unciam", "uncias", "unciae", "unciarum"],
                  "old_french": ["once", "onces"], "abbreviation": [".O.", "oz.", "j."]},
        "weight_grams": 31.1, "subdivisions": "1 uncia = 8 drachmae",
        "sources_attested": ["AN", "CI", "Compendium"]
    },
    "U_libra": {
        "ref_id": "U_libra", "canonical": "libra", "gloss_en": "pound", "type": "weight",
        "forms": {"latin": ["libra", "libram", "libras", "librae", "librarum"],
                  "old_french": ["livre", "livres"], "abbreviation": [".lb.", "lb."]},
        "weight_grams": 373.2, "subdivisions": "1 libra = 12 unciae = 96 drachmae",
        "sources_attested": ["AN", "CI", "Compendium"]
    },
    # --- VOLUME / QUANTITY ---
    "U_manipulus": {
        "ref_id": "U_manipulus", "canonical": "manipulus", "gloss_en": "handful", "type": "volume",
        "forms": {"latin": ["manipulus", "manipulum", "manipuli"], "old_french": ["poignee"],
                  "abbreviation": ["M.", "man."]},
        "weight_grams": None, "subdivisions": "approximate, varies by herb",
        "sources_attested": ["CI", "Macer"]
    },
    "U_pugillus": {
        "ref_id": "U_pugillus", "canonical": "pugillus", "gloss_en": "pinch (3 fingers)", "type": "volume",
        "forms": {"latin": ["pugillus", "pugillum", "pugilli"], "old_french": ["pincee"]},
        "weight_grams": None, "subdivisions": "smaller than manipulus",
        "sources_attested": ["CI"]
    },
    "U_cochlear": {
        "ref_id": "U_cochlear", "canonical": "cochlear", "gloss_en": "spoonful", "type": "volume",
        "forms": {"latin": ["cochlear", "cochlearium", "coclearia"], "old_french": ["cuilleree"]},
        "weight_grams": None, "subdivisions": "~5-15ml depending on period",
        "sources_attested": ["CI", "Grabadin"]
    },
    "U_cyathus": {
        "ref_id": "U_cyathus", "canonical": "cyathus", "gloss_en": "cup/measure", "type": "volume",
        "forms": {"latin": ["cyathus", "cyathi", "ciatus"]},
        "weight_grams": None, "subdivisions": "~45ml (Roman measure, still used medieval)",
        "sources_attested": ["AN"]
    },
    # --- DOSE MARKERS ---
    "D_ana": {
        "ref_id": "D_ana", "canonical": "ana", "gloss_en": "of each / equal parts", "type": "dose_marker",
        "forms": {"latin": ["ana", "an"], "abbreviation": ["aa.", "an."]},
        "notes": "All preceding ingredients share the same dose that follows.",
        "sources_attested": ["AN (universal)", "CI", "Grabadin"]
    },
    "D_quantum_sufficit": {
        "ref_id": "D_quantum_sufficit", "canonical": "quantum sufficit", "gloss_en": "as much as needed", "type": "dose_marker",
        "forms": {"latin": ["quantum sufficit", "quod sufficit"], "old_french": ["tant que souffise", "autant qu'il souffist"],
                  "abbreviation": ["q.s."]},
        "notes": "Used for excipients (mel, aqua). No fixed quantity.",
        "sources_attested": ["AN", "CI"]
    },
    "D_semis": {
        "ref_id": "D_semis", "canonical": "semis", "gloss_en": "half", "type": "fraction",
        "forms": {"latin": ["semis", "dimidium", "medium"], "abbreviation": [".S.", "ss."]},
        "notes": ".z.ii. et .S. = 2.5 drachms.",
        "sources_attested": ["AN", "CI"]
    },
}

with open('%s/R03_units.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(R03, f, indent=2, ensure_ascii=False)
print('R03_units.json: %d entries' % (len(R03) - 1))

# ================================================================
# R04_FORMS — Galenic pharmaceutical forms
# ================================================================

R04 = {
    "_meta": {
        "description": "Galenic pharmaceutical forms (types of preparations)",
        "sources": ["AN", "CI", "Grabadin", "Compendium Aromatariorum"],
        "version": "2026-04-11"
    },
    "F_electuarium": {
        "ref_id": "F_electuarium", "canonical": "electuarium", "gloss_en": "electuary (paste with honey)",
        "forms": {"latin": ["electuarium", "electuarii", "electuario"], "old_french": ["letuaire", "electuaire"], "italian": ["elettuario"]},
        "description": "Soft paste of powdered drugs mixed with honey or syrup. Taken orally.",
        "AN_count": 35, "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "F_unguentum": {
        "ref_id": "F_unguentum", "canonical": "unguentum", "gloss_en": "ointment",
        "forms": {"latin": ["unguentum", "unguenti", "unguento"], "old_french": ["oignement", "oingnement"], "italian": ["unguento"]},
        "description": "Fat-based preparation for external application (wax + oil + drugs).",
        "AN_count": 18, "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "F_emplastrum": {
        "ref_id": "F_emplastrum", "canonical": "emplastrum", "gloss_en": "plaster/poultice",
        "forms": {"latin": ["emplastrum", "emplastri", "emplastro"], "old_french": ["emplastre"], "italian": ["impiastro", "empiastro"]},
        "description": "Adhesive preparation applied to skin. Wax/resin base.",
        "AN_count": 12, "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "F_syrupus": {
        "ref_id": "F_syrupus", "canonical": "syrupus", "gloss_en": "syrup",
        "forms": {"latin": ["syrupus", "syrupi", "syrupo", "sirupus"], "old_french": ["syrop", "sirop"], "italian": ["sciroppo"]},
        "description": "Sugar/honey solution infused with drugs. Taken orally.",
        "AN_count": 15, "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "F_pilulae": {
        "ref_id": "F_pilulae", "canonical": "pilulae", "gloss_en": "pills",
        "forms": {"latin": ["pilulae", "pilularum", "pililas"], "old_french": ["pillules", "piloles"], "italian": ["pillole"]},
        "description": "Small balls of drug paste. Rolled by hand.",
        "AN_count": 10, "sources_attested": ["AN", "Grabadin"]
    },
    "F_trochisci": {
        "ref_id": "F_trochisci", "canonical": "trochisci", "gloss_en": "lozenges/tablets",
        "forms": {"latin": ["trochisci", "trochiscorum", "trochiscus"], "old_french": ["trochisques", "pastilles"]},
        "description": "Flat discs of dried drug paste. Dissolved in mouth or reconstituted.",
        "AN_count": 8, "sources_attested": ["AN", "Grabadin"]
    },
    "F_pulvis": {
        "ref_id": "F_pulvis", "canonical": "pulvis", "gloss_en": "powder",
        "forms": {"latin": ["pulvis", "pulveris", "pulvere"], "old_french": ["poldre", "poudre"], "italian": ["polvere"]},
        "description": "Ground drug. Simplest form. Often mixed with liquid before use.",
        "AN_count": 20, "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "F_oleum": {
        "ref_id": "F_oleum", "canonical": "oleum", "gloss_en": "medicated oil",
        "forms": {"latin": ["oleum", "olei", "oleo"], "old_french": ["huile", "oile"], "italian": ["olio"]},
        "description": "Oil infused with drugs by heating/maceration.",
        "AN_count": 5, "sources_attested": ["AN", "CI", "Grabadin"]
    },
    "F_decoctio": {
        "ref_id": "F_decoctio", "canonical": "decoctio", "gloss_en": "decoction",
        "forms": {"latin": ["decoctio", "decoctionis", "decoctione"], "old_french": ["decoction", "cuiture"]},
        "description": "Liquid obtained by boiling plant material in water/wine.",
        "AN_count": 0, "sources_attested": ["CI", "Macer"]
    },
    "F_infusio": {
        "ref_id": "F_infusio", "canonical": "infusio", "gloss_en": "infusion",
        "forms": {"latin": ["infusio", "infusionis", "infusione"]},
        "description": "Liquid obtained by steeping plant material without boiling.",
        "AN_count": 0, "sources_attested": ["CI"]
    },
    "F_cataplasma": {
        "ref_id": "F_cataplasma", "canonical": "cataplasma", "gloss_en": "poultice/cataplasm",
        "forms": {"latin": ["cataplasma", "cataplasma", "cataplasmate"], "old_french": ["cataplasme"]},
        "description": "Warm, moist mass of herbs applied to body.",
        "AN_count": 3, "sources_attested": ["AN", "CI"]
    },
    "F_collyrium": {
        "ref_id": "F_collyrium", "canonical": "collyrium", "gloss_en": "eye-wash/eye-drop",
        "forms": {"latin": ["collyrium", "collyrii", "collyrio"]},
        "description": "Liquid or ointment for eye treatment.",
        "AN_count": 5, "sources_attested": ["AN"]
    },
    "F_gargarisma": {
        "ref_id": "F_gargarisma", "canonical": "gargarisma", "gloss_en": "gargle",
        "forms": {"latin": ["gargarisma", "gargarismum", "gargarismus"]},
        "description": "Liquid for throat gargling.",
        "AN_count": 2, "sources_attested": ["AN", "CI"]
    },
    "F_suppositoria": {
        "ref_id": "F_suppositoria", "canonical": "suppositoria", "gloss_en": "suppository",
        "forms": {"latin": ["suppositoria", "suppositorium", "pessarium", "pessaria"]},
        "description": "Solid preparation inserted rectally or vaginally.",
        "AN_count": 3, "sources_attested": ["AN"]
    },
    "F_ceratum": {
        "ref_id": "F_ceratum", "canonical": "ceratum", "gloss_en": "cerate (wax preparation)",
        "forms": {"latin": ["ceratum", "cerati", "cerato"], "old_french": ["cerat"]},
        "description": "Wax-based preparation, stiffer than ointment.",
        "AN_count": 4, "sources_attested": ["AN", "Grabadin"]
    },
    "F_confectio": {
        "ref_id": "F_confectio", "canonical": "confectio", "gloss_en": "confection",
        "forms": {"latin": ["confectio", "confectionis", "confectione"], "old_french": ["confection"]},
        "description": "General term for prepared compound medicine.",
        "AN_count": 10, "sources_attested": ["AN", "CI"]
    },
    "F_potio": {
        "ref_id": "F_potio", "canonical": "potio", "gloss_en": "potion/drink",
        "forms": {"latin": ["potio", "potionis", "potione", "potus"], "old_french": ["boisson", "bevrage"]},
        "description": "Liquid medicine taken by mouth.",
        "AN_count": 5, "sources_attested": ["AN", "CI"]
    },
}

with open('%s/R04_forms.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(R04, f, indent=2, ensure_ascii=False)
print('R04_forms.json: %d forms' % (len(R04) - 1))

# ================================================================
# R05_TOOLS — Instruments and supports
# ================================================================

R05 = {
    "_meta": {
        "description": "Pharmaceutical instruments and supports mentioned in medieval recipes",
        "sources": ["AN", "CI", "Grabadin"],
        "version": "2026-04-11"
    },
    "T_mortarium": {"ref_id": "T_mortarium", "canonical": "mortarium", "gloss_en": "mortar",
        "forms": {"latin": ["mortarium", "mortarii", "mortario"], "old_french": ["mortier"]},
        "use": "Grinding drugs with pestle", "sources_attested": ["AN", "CI", "Grabadin"]},
    "T_pistillum": {"ref_id": "T_pistillum", "canonical": "pistillum", "gloss_en": "pestle",
        "forms": {"latin": ["pistillum", "pistilli", "pistillo"], "old_french": ["pestel", "pilote"]},
        "use": "Grinding in mortar", "sources_attested": ["AN", "Grabadin"]},
    "T_ignis": {"ref_id": "T_ignis", "canonical": "ignis", "gloss_en": "fire",
        "forms": {"latin": ["ignis", "ignem", "igni", "ignis lentus", "ignem lentum"], "old_french": ["feu", "feu lent"]},
        "use": "Heating/cooking. ignis lentus = slow/gentle fire", "sources_attested": ["AN", "CI", "Grabadin"]},
    "T_pannus": {"ref_id": "T_pannus", "canonical": "pannus", "gloss_en": "cloth (for straining)",
        "forms": {"latin": ["pannus", "pannum", "panno", "linteum", "linteo"], "old_french": ["drap", "linge"]},
        "use": "Straining liquid (cola per pannum)", "sources_attested": ["AN", "CI", "Grabadin"]},
    "T_vas": {"ref_id": "T_vas", "canonical": "vas", "gloss_en": "vessel/container",
        "forms": {"latin": ["vas", "vase", "vasis", "vaso"], "old_french": ["vaissel", "pot"]},
        "use": "Storage or processing", "sources_attested": ["AN", "CI", "Grabadin"]},
    "T_setaceum": {"ref_id": "T_setaceum", "canonical": "setaceum", "gloss_en": "sieve",
        "forms": {"latin": ["setaceum", "setaceo", "cribrum", "cribro"], "old_french": ["tamis", "bultel"]},
        "use": "Sifting powder", "sources_attested": ["AN", "Grabadin"]},
    "T_olla": {"ref_id": "T_olla", "canonical": "olla", "gloss_en": "pot (for cooking)",
        "forms": {"latin": ["olla", "ollam", "olla", "cacabus", "cacabo"], "old_french": ["pot", "chauderon"]},
        "use": "Boiling/decoction", "sources_attested": ["CI", "Grabadin"]},
    "T_spatula": {"ref_id": "T_spatula", "canonical": "spatula", "gloss_en": "spatula",
        "forms": {"latin": ["spatula", "spatulam", "spatula"]},
        "use": "Stirring/mixing ointments", "sources_attested": ["Grabadin"]},
    "T_cera": {"ref_id": "T_cera", "canonical": "cera", "gloss_en": "wax (as base material)",
        "forms": {"latin": ["cera", "ceram", "cerae", "cera alba", "cera nova"], "old_french": ["cire", "cire blanche"]},
        "use": "Base for ointments and cerates. Melted with oil.", "sources_attested": ["AN", "CI", "Grabadin"]},
    "T_aqua": {"ref_id": "T_aqua", "canonical": "aqua", "gloss_en": "water (as vehicle/solvent)",
        "forms": {"latin": ["aqua", "aquam", "aquae", "aqua calida", "aqua frigida", "aqua rosata", "aqua fontana"],
                  "old_french": ["eve", "eave", "iaue", "eve chaude", "eve froide", "eve rose"]},
        "use": "Vehicle for dissolving, washing, decoction. aqua rosata = rose water.", "sources_attested": ["AN", "CI", "Grabadin"]},
    "T_vinum": {"ref_id": "T_vinum", "canonical": "vinum", "gloss_en": "wine (as vehicle/solvent)",
        "forms": {"latin": ["vinum", "vino", "vini", "vinum album", "vinum rubeum", "vinum calidum"],
                  "old_french": ["vin", "vin blanc", "vin vermel", "vin chaut"]},
        "use": "Vehicle for oral medicines. detur cum vino calido.", "sources_attested": ["AN", "CI"]},
    "T_mel": {"ref_id": "T_mel", "canonical": "mel", "gloss_en": "honey (as excipient)",
        "forms": {"latin": ["mel", "melle", "mellis", "mel rosatum", "mel despumatum"],
                  "old_french": ["miel", "miel rosat", "miel escume"]},
        "use": "Excipient for electuaries. mel despumatum = clarified honey.", "sources_attested": ["AN", "CI"]},
    "T_acetum": {"ref_id": "T_acetum", "canonical": "acetum", "gloss_en": "vinegar (as vehicle)",
        "forms": {"latin": ["acetum", "aceto", "aceti", "acetum forte"], "old_french": ["aisil", "vinaigre"]},
        "use": "Vehicle/solvent. Strong solvent for minerals.", "sources_attested": ["AN", "CI"]},
}

with open('%s/R05_tools.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(R05, f, indent=2, ensure_ascii=False)
print('R05_tools.json: %d entries' % (len(R05) - 1))

# ================================================================
# R07_PLANT_PARTS
# ================================================================

R07 = {
    "_meta": {
        "description": "Plant parts used in medieval pharmacy",
        "sources": ["AN", "CI", "Macer", "Alphita"],
        "version": "2026-04-11"
    },
    "P_radix": {"ref_id": "P_radix", "canonical": "radix", "gloss_en": "root",
        "forms": {"latin": ["radix", "radicis", "radicem", "radices", "radicum"], "old_french": ["racine", "racines"]}},
    "P_folium": {"ref_id": "P_folium", "canonical": "folium", "gloss_en": "leaf",
        "forms": {"latin": ["folium", "folii", "folia", "foliorum"], "old_french": ["fuelle", "fuelles", "foille"]}},
    "P_semen": {"ref_id": "P_semen", "canonical": "semen", "gloss_en": "seed",
        "forms": {"latin": ["semen", "seminis", "semina", "seminum"], "old_french": ["semence", "semences", "saet"]}},
    "P_flos": {"ref_id": "P_flos", "canonical": "flos", "gloss_en": "flower",
        "forms": {"latin": ["flos", "floris", "flores", "florum"], "old_french": ["flor", "flors", "fleur"]}},
    "P_cortex": {"ref_id": "P_cortex", "canonical": "cortex", "gloss_en": "bark",
        "forms": {"latin": ["cortex", "corticis", "corticem", "cortices"], "old_french": ["escorce"]}},
    "P_succus": {"ref_id": "P_succus", "canonical": "succus", "gloss_en": "juice/sap",
        "forms": {"latin": ["succus", "succi", "succum", "succo"], "old_french": ["jus", "suc"]}},
    "P_lignum": {"ref_id": "P_lignum", "canonical": "lignum", "gloss_en": "wood",
        "forms": {"latin": ["lignum", "ligni", "ligno"], "old_french": ["bois", "fust"]}},
    "P_gummi": {"ref_id": "P_gummi", "canonical": "gummi", "gloss_en": "gum/resin",
        "forms": {"latin": ["gummi", "gumma", "gummae", "resina", "resinae"], "old_french": ["gomme", "resine"]}},
    "P_fructus": {"ref_id": "P_fructus", "canonical": "fructus", "gloss_en": "fruit/berry",
        "forms": {"latin": ["fructus", "fructi", "fructum", "bacca", "baccae", "baccarum"], "old_french": ["fruit", "baie"]}},
    "P_herba": {"ref_id": "P_herba", "canonical": "herba", "gloss_en": "herb (whole plant)",
        "forms": {"latin": ["herba", "herbae", "herbam", "herbas"], "old_french": ["herbe", "herbes"]}},
    "P_summitas": {"ref_id": "P_summitas", "canonical": "summitas", "gloss_en": "tip/top (flowering top)",
        "forms": {"latin": ["summitas", "summitatis", "summitates"], "old_french": ["somite", "cime"]}},
    "P_tuber": {"ref_id": "P_tuber", "canonical": "tuber", "gloss_en": "tuber/bulb",
        "forms": {"latin": ["tuber", "tuberis", "bulbus", "bulbi"], "old_french": ["bulbe", "oignon"]}},
}

with open('%s/R07_plant_parts.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(R07, f, indent=2, ensure_ascii=False)
print('R07_plant_parts.json: %d entries' % (len(R07) - 1))

# ================================================================
# R06_QUALITIES — Galenic qualities (from existing CI data)
# ================================================================
# Read from existing parsed CSV
galenic_entries = {"_meta": {
    "description": "Galenic qualities (thermal + moisture) for simples from Circa Instans",
    "source": "Circa Instans (Platearius ~1166), ed. Dorveaux 1913",
    "file": "BruteForce/Plants/Corpus_Pharmaceutique/datasets/circa_instans_galenic_degrees.csv",
    "system": {
        "thermal": ["calidum (hot)", "frigidum (cold)"],
        "moisture": ["siccum (dry)", "humidum (wet)"],
        "degrees": ["1 (mild)", "2 (moderate)", "3 (strong)", "4 (extreme)"],
    },
    "version": "2026-04-11"
}}

with open('BruteForce/Plants/Corpus_Pharmaceutique/datasets/circa_instans_galenic_degrees.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        latin = row.get('Latin', '').strip()
        if not latin: continue
        thermal = row.get('Thermal', '').strip()
        tdeg = row.get('ThermalDeg', '').strip()
        moisture = row.get('Moisture', '').strip()
        mdeg = row.get('MoistureDeg', '').strip()

        key = 'Q_%s_%s_%s_%s' % (thermal or 'unknown', tdeg or 'x', moisture or 'unknown', mdeg or 'x')
        ref_id = 'Q_%s' % latin.lower().replace(' ', '_')

        galenic_entries[ref_id] = {
            "ref_id": ref_id,
            "plant_latin": latin,
            "plant_old_french": row.get('OldFrench', ''),
            "plant_french": row.get('French', ''),
            "thermal": thermal,
            "thermal_degree": tdeg,
            "moisture": moisture,
            "moisture_degree": mdeg,
            "quality_key": key,
        }

with open('%s/R06_qualities.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(galenic_entries, f, indent=2, ensure_ascii=False)
print('R06_qualities.json: %d entries' % (len(galenic_entries) - 1))

# ================================================================
# R08_INDICATIONS — Common medieval diseases/symptoms
# ================================================================

R08 = {
    "_meta": {
        "description": "Common medieval diseases and therapeutic indications from pharmaceutical texts",
        "sources": ["AN", "CI", "Macer", "Avicenna"],
        "note": "Seed list. Will grow as more sources are parsed.",
        "version": "2026-04-11"
    },
    # Head
    "M_dolor_capitis": {"ref_id": "M_dolor_capitis", "canonical": "dolor capitis", "gloss_en": "headache",
        "forms": {"latin": ["dolor capitis", "capitis dolor", "capitis vitium", "cephalea", "emigranea"],
                  "old_french": ["dolor del chief", "mal de teste", "hoeftsware"]}},
    "M_vertigo": {"ref_id": "M_vertigo", "canonical": "vertigo", "gloss_en": "dizziness",
        "forms": {"latin": ["vertigo", "vertiginem"]}},
    # Eyes
    "M_dolor_oculorum": {"ref_id": "M_dolor_oculorum", "canonical": "dolor oculorum", "gloss_en": "eye pain",
        "forms": {"latin": ["dolor oculorum", "oculorum dolor", "lippitudo", "caliginem oculorum"],
                  "old_french": ["dolor des oilz", "mal des yex"]}},
    # Stomach
    "M_dolor_stomachi": {"ref_id": "M_dolor_stomachi", "canonical": "dolor stomachi", "gloss_en": "stomach ache",
        "forms": {"latin": ["dolor stomachi", "stomachi dolor", "dolor ventris"],
                  "old_french": ["dolor del ventre", "mal del estomac"]}},
    # Fever
    "M_febris": {"ref_id": "M_febris", "canonical": "febris", "gloss_en": "fever",
        "forms": {"latin": ["febris", "febrem", "febribus", "febris quartana", "febris tertiana", "febris cotidiana"],
                  "old_french": ["fievre", "fievres", "quartaine", "tiercaine"]}},
    # Wounds
    "M_vulnus": {"ref_id": "M_vulnus", "canonical": "vulnus", "gloss_en": "wound",
        "forms": {"latin": ["vulnus", "vulnera", "vulneris", "plaga", "plagam"],
                  "old_french": ["plaie", "plaies"]}},
    "M_ulcus": {"ref_id": "M_ulcus", "canonical": "ulcus", "gloss_en": "ulcer/sore",
        "forms": {"latin": ["ulcus", "ulceris", "ulcera", "ulceribus"],
                  "old_french": ["ulcere", "ulceres"]}},
    # Chest/lungs
    "M_tussis": {"ref_id": "M_tussis", "canonical": "tussis", "gloss_en": "cough",
        "forms": {"latin": ["tussis", "tussim", "tussi"], "old_french": ["toz", "tos"]}},
    "M_asthma": {"ref_id": "M_asthma", "canonical": "asthma", "gloss_en": "difficulty breathing",
        "forms": {"latin": ["asthma", "asma", "dyspnea", "orthopnea"], "old_french": ["asme"]}},
    # Digestion
    "M_constipatio": {"ref_id": "M_constipatio", "canonical": "constipatio", "gloss_en": "constipation",
        "forms": {"latin": ["constipatio", "stipticitas", "ventris constrictio"]}},
    "M_diarrhea": {"ref_id": "M_diarrhea", "canonical": "diarrhea", "gloss_en": "diarrhea",
        "forms": {"latin": ["diarrhea", "diarrhoea", "fluxus ventris", "lienteria"],
                  "old_french": ["flux del ventre"]}},
    # Pain
    "M_dolor": {"ref_id": "M_dolor", "canonical": "dolor", "gloss_en": "pain (general)",
        "forms": {"latin": ["dolor", "dolorem", "dolore", "doloris"],
                  "old_french": ["dolor", "dolur"]}},
    # Humoral
    "M_apostema": {"ref_id": "M_apostema", "canonical": "apostema", "gloss_en": "abscess/swelling",
        "forms": {"latin": ["apostema", "apostemata", "apostematis", "tumor", "tumorem"],
                  "old_french": ["aposteme", "enflement"]}},
    # Urinary
    "M_calculus": {"ref_id": "M_calculus", "canonical": "calculus", "gloss_en": "kidney/bladder stone",
        "forms": {"latin": ["calculus", "calculum", "lapis", "lapidem", "lapidis"],
                  "old_french": ["pierre", "gravele"]}},
    # Skin
    "M_scabies": {"ref_id": "M_scabies", "canonical": "scabies", "gloss_en": "scabies/itch",
        "forms": {"latin": ["scabies", "scabiem", "pruritus", "pruritum"],
                  "old_french": ["roigne", "demangeison"]}},
    # Joints
    "M_arthritis": {"ref_id": "M_arthritis", "canonical": "arthritis", "gloss_en": "joint pain/gout",
        "forms": {"latin": ["arthritis", "articulorum dolor", "podagra", "gutta"],
                  "old_french": ["goute", "artetike"]}},
    # Reproductive
    "M_menstrua": {"ref_id": "M_menstrua", "canonical": "menstrua", "gloss_en": "menstruation",
        "forms": {"latin": ["menstrua", "menstruorum", "menses", "purgatio mulieris"],
                  "old_french": ["flors de feme", "purgation"]}},
    # Poison
    "M_venenum": {"ref_id": "M_venenum", "canonical": "venenum", "gloss_en": "poison/venom",
        "forms": {"latin": ["venenum", "veneni", "venenum", "morsus serpentis", "morsus canis"],
                  "old_french": ["venin", "morsure"]}},
    # Worms
    "M_vermes": {"ref_id": "M_vermes", "canonical": "vermes", "gloss_en": "intestinal worms",
        "forms": {"latin": ["vermes", "vermium", "lumbrici", "lumbricorum"],
                  "old_french": ["vers", "verms"]}},
}

with open('%s/R08_indications.json' % OUTDIR, 'w', encoding='utf-8') as f:
    json.dump(R08, f, indent=2, ensure_ascii=False)
print('R08_indications.json: %d entries' % (len(R08) - 1))

# ================================================================
# SUMMARY
# ================================================================
print('\n=== REFERENTIELS BUILT ===')
print('R01_verbs.json:       %d verbs' % (len(R01) - 1))
print('R03_units.json:       %d entries' % (len(R03) - 1))
print('R04_forms.json:       %d forms' % (len(R04) - 1))
print('R05_tools.json:       %d tools' % (len(R05) - 1))
print('R06_qualities.json:   %d qualities' % (len(galenic_entries) - 1))
print('R07_plant_parts.json: %d parts' % (len(R07) - 1))
print('R08_indications.json: %d indications' % (len(R08) - 1))
print('\nR02_ingredients.json: TODO (needs full parsing of AN/CI/DALME sources)')
