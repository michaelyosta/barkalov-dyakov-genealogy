"""Record visually checked translation as a separate historical household."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'research'
def read(n): return json.loads((R/(n+'.json')).read_text(encoding='utf-8'))
def save(n,v): (R/(n+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
persons,claims,rels,sources=[read(n) for n in ('persons','claims','relationships','sources')]
if any(p['id']=='P-HIST-1853-ABROSIM' for p in persons):
    raise SystemExit('Household already recorded; do not duplicate.')
source=next(s for s in sources if s['id']=='S-CAU-1853')
source.update(local_copy_if_allowed='research/local_cache/tax_register_1853_full.pdf',
    content_hash=hashlib.sha256((R/'local_cache/tax_register_1853_full.pdf').read_bytes()).hexdigest(),
    list_or_frame='печатнаяс.65; PDF-страница73 из103; нижняя семейная группа',
    notes='Оркестратор открыл полный PDF и визуально проверил рендер страницы73. Это опубликованный перевод, не русский архивный оригинал. Копия и рендер остаются локально; права перепубликации не установлены.')
for suffix,name in [('ABROSIM','Абросим Петрович Абросимов'),('PETR','Пётр [сын Абросима в записи1853]'),('FYODOR','Фёдор [сын Абросима в записи1853]')]:
    persons.append({'id':'P-HIST-1853-'+suffix,'name':name,'aliases':[],
        'life_status':'historical','privacy':'historical_candidate',
        'origin':'published_translation_1853','status':'supported',
        'source_ids':['S-CAU-1853'],'kinship_to_client':'not_established',
        'note':'Отдельное историческое хозяйство; не объединять автоматически с одноимёнными фигурами1873г.'})
household=next(c for c in claims if c['id']=='C-CAU-001')
household['subject_id']='P-HIST-1853-ABROSIM'
household['object']['head_person_id']='P-HIST-1853-ABROSIM'
for child,suffix in zip(household['object']['sons'],('PETR','FYODOR')):
    child['person_id']='P-HIST-1853-'+suffix
household['source_locator']='печатнаяс.65; PDF-страница73/103, нижняя группа Abrosimov'
def claim(cid,subject,predicate,value,sids,status,note):
    claims.append({'id':cid,'subject_id':subject,'predicate':predicate,'object':value,
        'raw_text':None,'source_ids':sids,'original_vs_derived':'derived',
        'direct_vs_indirect':'direct_as_reported_not_originally_verified',
        'status':status,'reviewer':'T-AUD-001','proof_argument_path':'cycle_001.md','note':note})
claim('C-ID-004','P-HIST-1853-ABROSIM','same_person_as','P-HIST-004',['S-CAU-1853','S-LEGACY-GED'],
    'hypothesis','Отождествление фигур1853 и1873гг. не завершено; разница возрастных ориентиров требует проверки.')
for suffix in ('PETR','FYODOR'):
    cid='C-CAU-PARENT-'+suffix
    claim(cid,'P-HIST-1853-ABROSIM','parent','P-HIST-1853-'+suffix,
        ['S-CAU-1853'],'supported','Связь son в опубликованном переводе; оригинал не проверен. К семье заказчика не присоединяется.')
    rels.append({'id':'R-CAU-1853-'+suffix,'from_person':'P-HIST-1853-ABROSIM',
        'to_person':'P-HIST-1853-'+suffix,'type':'parent','temporal_scope':'1853',
        'claim_id':cid,'status':'supported','export_to_verified':False,'reviewer':'T-AUD-001'})
for suffix in ('003','004'):
    for target in ('001','002'):
        cid=f'C-MEM-PARENT-{suffix}-{target}'
        claim(cid,'P-BARK-'+suffix+'-MEM','parent','P-BARK-'+target,
            ['S-MEM-20261030'],'hypothesis','Связь сообщена в семейной памяти через goal; исходный акт или запись интервью не получены.')
        rels.append({'id':cid.replace('C-','R-',1),'from_person':'P-BARK-'+suffix+'-MEM',
            'to_person':'P-BARK-'+target,'type':'parent','temporal_scope':None,
            'claim_id':cid,'status':'hypothesis','export_to_verified':False,'reviewer':'T-AUD-001'})
for n,v in [('persons',persons),('claims',claims),('relationships',rels),('sources',sources)]: save(n,v)
decision={'id':'D-C001-005','date':'2026-10-30','actor':'orchestrator','reviewer':'T-AUD-001',
    'action':'record_separate_1853_household_and_memory_parents',
    'reason':'Полная опубликованная таблица визуально проверена на PDFс.73. Исторические персоны и родители из памяти не слиты с другими кандидатами.',
    'source_ids':['S-CAU-1853','S-MEM-20261030'],'reversible':True}
with (R/'decisions.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(decision,ensure_ascii=False)+'\n')
print('Household and family-memory edges recorded separately.')
