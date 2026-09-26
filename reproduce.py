"""Reproduce the UCDP 1946–2023 termination chart from the bundled snapshot."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

PROJECT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, default=PROJECT / 'output')
args = parser.parse_args()
ROOT = args.output_dir
ROOT.mkdir(parents=True, exist_ok=True)
source = PROJECT / 'data/source.csv'
metadata = json.loads((PROJECT / 'data/provenance.json').read_text(encoding='utf-8'))
if hashlib.sha256(source.read_bytes()).hexdigest() != metadata['sha256_stored']:
    raise ValueError('Source snapshot changed: review provenance before reproducing.')
with source.open(encoding='utf-8-sig', newline='') as f:
    original = list(csv.DictReader(f))
terminated = [r for r in original if r['c_epterm'] == '1']
assert len(original) == 2752
assert len(terminated) == 507
outcomes = {'1':'Accord de paix', '2':'Accord de cessez-le-feu',
            '3':'Victoire du camp A', '4':'Victoire du camp B',
            '5':'Activité sous le seuil de 25 morts de combat/an',
            '6':'Disparition ou transformation d’un acteur'}
types = {'1':'Extraétatique / décolonisation', '2':'Interétatique',
         '3':'Intraétatique, avec ou sans intervention étrangère'}
fields = ['id_conflit_ucdp','id_episode_source_non_unique','lieu_ucdp',
          'territoire_en_jeu','camp_A_derniere_annee','camp_B_derniere_annee',
          'debut_episode_annee_ucdp','derniere_annee_active','date_fin_source',
          'precision_date_code_ucdp','type_conflit','issue_code_ucdp',
          'issue_libelle','source_version','source_url']
rows = []
for r in sorted(terminated, key=lambda r:(int(r['year']),r['location'],r['conflict_id'])):
    values = [r['conflict_id'],r['c_epid'],r['location'],r['territory_name'],
              r['side_a'],r['side_b'],r['c_ep_startyear'],r['year'],
              r['c_ependdate'],r['c_ependprec'],types[r['type_of_conflict2']],
              r['c_outcome'],outcomes[r['c_outcome']],r['version'],
              metadata['source_url']]
    rows.append(dict(zip(fields, values)))
with (ROOT/'fins-conflits-ucdp-1946-2023.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter=';')
    writer.writeheader()
    writer.writerows(rows)
assert len({(r['id_conflit_ucdp'],r['derniere_annee_active']) for r in rows}) == 507
periods = [(1946,1949)] + [(y,y+9) for y in range(1950,2020,10)] + [(2020,2023)]
keys = ['victoire','paix','cessez','faible','acteur']
mapping = {'1':'paix','2':'cessez','3':'victoire','4':'victoire','5':'faible','6':'acteur'}
colors = ['#C05B43','#197C70','#65ACCA','#9AA2AD','#DBD1C3']
labels = ['Victoire militaire (un camp)', 'Accord de paix', 'Accord de cessez-le-feu',
          'Activité sous le seuil UCDP', 'Disparition / transformation d’un acteur']
counts = []
for start, end in periods:
    c = Counter(mapping[r['issue_code_ucdp']] for r in rows if start <= int(r['derniere_annee_active']) <= end)
    counts.append(c)
assert sum(sum(c.values()) for c in counts) == len(rows)
assert [sum(c[k] for c in counts) for k in keys] == [151,60,67,209,20]
ns = [sum(c.values()) for c in counts]
shares = [[100*c[k]/n for c,n in zip(counts,ns)] for k in keys]
assert all(abs(sum(shares[j][i] for j in range(5))-100)<1e-8 for i in range(len(ns)))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':'#202C38',
                     'axes.labelcolor':'#202C38','xtick.color':'#202C38','ytick.color':'#53606C'})
fig = plt.figure(figsize=(13,9), facecolor='#FAF8F3')
fig.text(.07,.94,'Comment les conflits armés s’interrompent',fontsize=25,weight='bold')
fig.text(.07,.898,'Évolution des modes de terminaison · 1946–2023',fontsize=16,color='#53606C')
fig.text(.07,.859,'Part des épisodes terminés dans chaque période — pas part de toutes les guerres',fontsize=12)
legend = [Patch(facecolor=c,label=l) for c,l in zip(colors,labels)]
fig.legend(handles=legend[:3],loc='upper left',bbox_to_anchor=(.064,.831),ncol=3,frameon=False,fontsize=11.5,
           columnspacing=1.9,handlelength=1.15)
fig.legend(handles=legend[3:],loc='upper left',bbox_to_anchor=(.064,.791),ncol=2,frameon=False,fontsize=11.5,
           columnspacing=2.2,handlelength=1.15)
ax = fig.add_axes([.085,.25,.86,.47],facecolor='#FAF8F3')
ax.set_ylim(0,109)
ax.set_xlim(-.65,len(periods)-.35)
ax.set_yticks([0,20,40,60,80,100])
ax.yaxis.set_major_formatter(PercentFormatter(xmax=100,decimals=0))
ax.set_axisbelow(True)
ax.grid(axis='y',color='#DEDCD7',linewidth=.8)
for spine in ax.spines.values():spine.set_visible(False)
ax.tick_params(axis='both',length=0,pad=8)
bottom = [0.0]*len(ns)
for j,k in enumerate(keys):
    ax.bar(range(len(ns)),shares[j],bottom=bottom,width=.7,color=colors[j],edgecolor='#FAF8F3',linewidth=.8,zorder=3)
    for i,value in enumerate(shares[j]):
        if value >= 8:
            txt = f'{value:.0f} %'
            color = 'white' if j in (0,1) else '#15212D'
            ax.text(i,bottom[i]+value/2,txt,ha='center',va='center',fontsize=11.5,color=color,weight='bold')
        bottom[i] += value
for i,n in enumerate(ns):
    ax.text(i,103,f'n = {n}',ha='center',va='center',fontsize=11,color='#53606C')
ax.set_xticks(range(len(ns)))
ax.set_xticklabels([f'{a}\n–{b}' + ('*' if i in (0,len(periods)-1) else '') for i,(a,b) in enumerate(periods)],fontsize=11.5)
fig.text(.07,.182,'507 fins d’épisodes au total. Chaque épisode compte une fois, quelle que soit sa gravité.',fontsize=12,weight='bold')
fig.text(.07,.125,'« Activité sous le seuil » : moins de 25 morts liés aux combats dans l’année suivante,\nsans victoire ni accord codé. Cela ne signifie pas que le différend est résolu.',fontsize=11.5,linespacing=1.55)
fig.text(.07,.074,'n = nombre de fins d’épisodes. * Périodes partielles : 4 ans. Classement par dernière année active.\nReprises possibles ; épisodes encore actifs exclus. Les conflits de faible intensité sont inclus.',fontsize=10.5,color='#53606C',linespacing=1.5)
fig.text(.07,.025,'Source : UCDP Conflict Termination Dataset v4-2024 · calculs à partir des 507 terminaisons codées.',fontsize=10,color='#53606C')
output=ROOT/'fins-conflits-evolution-1946-2023.png'
fig.savefig(output,dpi=180,facecolor=fig.get_facecolor())
plt.close(fig)
assert output.stat().st_size > 10000
from PIL import Image
with Image.open(output) as im:
    im.verify()
print('PNG:',output)
print('Période | n | victoire % | paix % | cessez-le-feu % | faible % | acteur %')
for i,(a,b) in enumerate(periods):
    print(f'{a}-{b} | {ns[i]} | '+' | '.join(f'{shares[j][i]:.1f}' for j in range(5)))
with (ROOT/'fins-conflits-par-periode.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';')
    w.writerow(['debut','fin','n']+[k+'_nombre' for k in keys]+[k+'_pourcent' for k in keys])
    for i,(a,b) in enumerate(periods):
        w.writerow([a,b,ns[i]]+[counts[i][k] for k in keys]+[round(shares[j][i],4) for j in range(5)])
print('Validated totals:',[sum(c[k] for c in counts) for k in keys])
