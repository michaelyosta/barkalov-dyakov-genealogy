"""Separate literal record entity from its identification in legacy prose."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(n): return json.loads((R/(n+'.json')).read_text(encoding='utf-8'))
def save(n,v): (R/(n+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
people,claims,rels=[read(n) for n in ('persons','claims','relationships')]
pid='P-REC-1942-SPOUSE'
if any(p['id']==pid for p in people): raise SystemExit('Already recorded.')
people.append({'id':pid,'name':'Антонина Прокофьевна [запись в донесении1942г.]',
    'aliases':[],'privacy':'public_historical_record_entity','life_status':'unknown',
    'status':'supported','origin':'literal_document_inscription',
    'source_ids':['S-MIL-001'],'kinship_to_client':'not_established',
    'note':'Идентификатор записи о человеке, а не доказанное тождество с кандидатами прежней сводки.'})
claim=next(c for c in claims if c['id']=='C-OBS-004')
claim['object']=pid
claim['recorded_name']='Антонина Прокофьевна'
claim['note']='В строке57 жена записана с этим именем. Отождествление с лицом старой сводки, очередность браков и материнство не установлены.'
next(e for e in rels if e['id']=='R-DOC-001')['to_person']=pid
claims.append({'id':'C-ID-005','subject_id':pid,'predicate':'same_person_as',
    'object':'P-BARK-004B','raw_text':None,'source_ids':['S-MIL-001','S-LEGACY-MASTER'],
    'original_vs_derived':'mixed','direct_vs_indirect':'indirect',
    'status':'hypothesis','reviewer':'T-AUD-001','proof_argument_path':'cycle_001.md',
    'note':'Кандидат прежней сводки и запись о жене не сливаются без идентифицирующего доказательства.'})
for n,v in [('persons',people),('claims',claims),('relationships',rels)]:save(n,v)
decision={'id':'D-C001-006','date':'2026-10-30','actor':'orchestrator','reviewer':'T-AUD-001',
    'action':'separate_literal_spouse_record','claims':['C-OBS-004','C-ID-005'],
    'reason':'Наблюдаемое имя в документе отделено от идентичности кандидата старого отчёта.','reversible':True}
with (R/'decisions.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(decision,ensure_ascii=False)+'\n')
print('Literal spouse inscription separated.')
