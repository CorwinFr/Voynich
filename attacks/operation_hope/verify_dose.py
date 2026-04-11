"""4 verification tests for the -ain/-aiin/-aiiin dose hypothesis."""
import re,sys,io,json
from collections import Counter,defaultdict
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
sys.path.insert(0,'attacks')
from lib.loader import load_source

with open('data/transcriptions/ZL.txt',encoding='utf-8') as f:
    zl=f.read()

an=load_source('S01')
SUFFIXES=['aiiin','aiin','ain','eedy','edy','eey','ey','dy','ol','or','ar','al','am','om']

def parse_vms():
    seq=[]
    for line in zl.split('\n'):
        mm=re.match(r'<f(\d+)([rv])(\d?)\.(\d+)',line.strip())
        if not mm:continue
        fn=int(mm.group(1))
        fo='f%d%s%s'%(fn,mm.group(2),mm.group(3))
        if fn<=56:sec='herbal'
        elif 58<=fn<=73:sec='astro'
        elif 75<=fn<=84:sec='balnea'
        elif 85<=fn<=102:sec='herbal_B'
        elif 103<=fn<=116:sec='pharma'
        else:continue
        text=re.sub(r'<[^>]*>','',line.strip())
        text=re.sub(r'<!.*?>','',text).replace(',','.').replace('?','')
        text=re.sub(r'\[[^\]]*:([^\]]*)\]',r'\1',text)
        words=[w for w in re.findall(r'[a-z]+',text) if w]
        for i,w in enumerate(words):
            seq.append((w,fo,sec,i,len(words)))
    return seq

all_seq=parse_vms()

# ================================================================
# VERIF 1: AN ratio .i.:.ii. varies per recipe?
# ================================================================
print('='*70)
print('VERIF 1: RATIO .i.:.ii. PAR RECETTE AN')
print('='*70)

recipe_data=[]
for r in an:
    toks=r.get('tokens',[])
    qi=sum(1 for t in toks if t.get('type')=='QTY' and t.get('raw','').strip('.,;:()')=='i')
    qii=sum(1 for t in toks if t.get('type')=='QTY' and t.get('raw','').strip('.,;:()')=='ii')
    qiii=sum(1 for t in toks if t.get('type')=='QTY' and t.get('raw','').strip('.,;:()')=='iii')
    total=qi+qii+qiii
    if total>=3:
        recipe_data.append((r.get('id','?'),qi,qii,qiii))

print('%-10s %4s %4s %5s %8s'%('Recipe','.i.','.ii.','.iii.','ii/i'))
for rid,qi,qii,qiii in sorted(recipe_data,key=lambda x:x[2]/max(x[1],0.5)):
    print('%-10s %4d %4d %5d %8.1f'%(rid,qi,qii,qiii,qii/max(qi,0.5)))

if recipe_data:
    ratios=[qii/max(qi,0.5) for _,qi,qii,_ in recipe_data]
    print('\nAN ratio range: %.1f to %.1f'%(min(ratios),max(ratios)))
    print('VMS ratio range: 0.3 to 37.0')
    print('AN varies: %s'%('YES' if max(ratios)/max(min(ratios),0.1)>5 else 'NO'))

# ================================================================
# VERIF 2: Folios high-aiin vs high-ain — different vocabulary?
# ================================================================
print('\n'+'='*70)
print('VERIF 2: VOCABULAIRE FOLIO HIGH-aiin vs HIGH-ain')
print('='*70)

folio_d=defaultdict(lambda:{'ain':0,'aiin':0,'words':[]})
for w,fo,sec,pos,total in all_seq:
    if sec!='pharma':continue
    folio_d[fo]['words'].append(w)
    if w.endswith('aiiin') and len(w)>5:pass
    elif w.endswith('aiin') and len(w)>4:folio_d[fo]['aiin']+=1
    elif w.endswith('ain') and len(w)>3:folio_d[fo]['ain']+=1

high_aiin=[fo for fo,d in folio_d.items() if d['ain']+d['aiin']>=10 and d['aiin']/max(d['ain'],1)>3]
high_ain=[fo for fo,d in folio_d.items() if d['ain']+d['aiin']>=10 and d['aiin']/max(d['ain'],1)<1]

v1=Counter();v2=Counter()
for fo in high_aiin:
    for w in folio_d[fo]['words']:
        if len(w)>=5 and not any(w.endswith(s) for s in ['aiin','ain','aiiin']):v1[w]+=1
for fo in high_ain:
    for w in folio_d[fo]['words']:
        if len(w)>=5 and not any(w.endswith(s) for s in ['aiin','ain','aiiin']):v2[w]+=1

t1=set(w for w,_ in v1.most_common(30))
t2=set(w for w,_ in v2.most_common(30))
overlap=t1&t2
jaccard=len(overlap)/len(t1|t2) if t1|t2 else 0

print('\nHigh-aiin folios: %s'%high_aiin)
print('High-ain folios:  %s'%high_ain)
print('Top30 vocab overlap: %d (Jaccard=%.2f)'%(len(overlap),jaccard))
print('Overlap words: %s'%sorted(overlap))
if jaccard<0.3:
    print('-> DIFFERENT vocabularies = different recipes/content')
else:
    print('-> SIMILAR = same content, grammar difference only')

# ================================================================
# VERIF 3: Same root takes -aiin AND -ol/-ey on same folio?
# ================================================================
print('\n'+'='*70)
print('VERIF 3: MEME RACINE + SUFFIXE VARIABLE (dose vs non-dose)')
print('='*70)

root_sfx=defaultdict(Counter)
for w,fo,sec,pos,total in all_seq:
    for sx in SUFFIXES:
        if w.endswith(sx) and len(w)>len(sx):
            root_sfx[w[:-len(sx)]][sx]+=1
            break

print('\nRacines avec -aiin(>=20) ET -ol/-ey/-edy(>=5):')
print('%-8s %5s %5s %5s %5s %5s %5s %5s'%('Root','-aiin','-ain','-ol','-ey','-edy','-ar','-al'))
for root in sorted(root_sfx,key=lambda r:-root_sfx[r].get('aiin',0)):
    d=root_sfx[root]
    if d.get('aiin',0)<20:continue
    non_dose=d.get('ol',0)+d.get('ey',0)+d.get('edy',0)
    if non_dose<5:continue
    print('%-8s %5d %5d %5d %5d %5d %5d %5d'%(
        root,d.get('aiin',0),d.get('ain',0),d.get('ol',0),
        d.get('ey',0),d.get('edy',0),d.get('ar',0),d.get('al',0)))

# ================================================================
# VERIF 4: Same root + BOTH -ain and -aiin on SAME folio
# ================================================================
print('\n'+'='*70)
print('VERIF 4: MEME RACINE + -ain ET -aiin SUR MEME FOLIO')
print('='*70)

folio_root_sfx=defaultdict(lambda:defaultdict(set))
for w,fo,sec,pos,total in all_seq:
    if sec!='pharma':continue
    for sx in SUFFIXES:
        if w.endswith(sx) and len(w)>len(sx):
            folio_root_sfx[fo][w[:-len(sx)]].add(sx)
            break

both_count=0
examples=[]
for fo,roots in folio_root_sfx.items():
    for root,sxs in roots.items():
        if 'ain' in sxs and 'aiin' in sxs:
            both_count+=1
            if len(examples)<20:
                examples.append((fo,root,sorted(sxs)))

print('\nCas ou MEME racine a -ain ET -aiin sur MEME folio: %d'%both_count)
print('\nExemples:')
for fo,root,sxs in examples:
    print('  %8s  root=%-8s  suffixes=%s'%(fo,root,sxs))

# ================================================================
# VERIF 5: Pattern [root+ol] ... [root+aiin] on same folio
# = the SAME root appears first as ingredient (ol-form)
#   then later as dose (aiin-form)?
# ================================================================
print('\n'+'='*70)
print('VERIF 5: MEME RACINE en -ol PUIS en -aiin sur meme folio')
print('(= ingredient en mode description puis en mode dosage?)')
print('='*70)

folio_root_order=defaultdict(lambda:defaultdict(list))
for idx,(w,fo,sec,pos,total) in enumerate(all_seq):
    if sec!='pharma':continue
    for sx in SUFFIXES:
        if w.endswith(sx) and len(w)>len(sx):
            folio_root_order[fo][w[:-len(sx)]].append((idx,sx))
            break

cases=[]
for fo,roots in folio_root_order.items():
    for root,occs in roots.items():
        has_ol=any(sx=='ol' for _,sx in occs)
        has_aiin=any(sx=='aiin' for _,sx in occs)
        has_ain=any(sx=='ain' for _,sx in occs)
        if has_ol and (has_aiin or has_ain):
            ol_positions=[idx for idx,sx in occs if sx=='ol']
            dose_positions=[idx for idx,sx in occs if sx in ('aiin','ain')]
            cases.append((fo,root,len(ol_positions),len(dose_positions),
                         min(ol_positions),min(dose_positions)))

print('\nCas ou racine apparait en -ol ET en -aiin/-ain sur meme folio: %d'%len(cases))
print('\nExemples (ol_first = -ol avant -aiin):')
for fo,root,nol,ndose,first_ol,first_dose in sorted(cases,key=lambda x:x[0])[:20]:
    order='ol FIRST' if first_ol<first_dose else 'dose FIRST'
    print('  %8s  root=%-8s  n_ol=%d  n_dose=%d  %s'%(fo,root,nol,ndose,order))

ol_first=sum(1 for _,_,_,_,fo,fd in cases if fo<fd)
dose_first=sum(1 for _,_,_,_,fo,fd in cases if fd<fo)
print('\nOrdre: ol_first=%d  dose_first=%d'%(ol_first,dose_first))
if ol_first>dose_first*1.5:
    print('-> -ol tend a apparaitre AVANT -aiin = description puis dosage?')
elif dose_first>ol_first*1.5:
    print('-> -aiin tend a apparaitre AVANT -ol')
else:
    print('-> Pas de tendance claire dans lordre')

# Save
json.dump({
    'verif1_an_ratio_varies': len(recipe_data)>0 and max(ratios)/max(min(ratios),0.1)>5 if recipe_data else False,
    'verif2_jaccard': jaccard,
    'verif3_dual_roots': both_count,
    'verif4_same_folio_both': both_count,
    'verif5_ol_then_aiin': {'ol_first':ol_first,'dose_first':dose_first,'total':len(cases)},
}, open('attacks/operation_hope/results/verify_dose.json','w'), indent=2)
print('\nSaved verify_dose.json')
