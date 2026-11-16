"""One-time, non-destructive migration of the legacy GEDCOM into a quarantine."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research'
DATE = '2026-10-30'
MAPPING = dict(zip(range(1, 23), [
    'P-BARK-001','P-BARK-002','P-BARK-003','P-BARK-004A','P-BARK-005',
    'P-BARK-006','P-BARK-007','P-BARK-GRIGORY-LEGACY','P-DYAK-001',
    'P-DEME-001A','P-DEME-001B','P-DYAK-002','P-DYAK-003','P-DYAK-004',
    'P-ABRO-001','P-ABRO-002','P-DYAK-005','P-DEME-004',
    'P-DEME-002','P-DYAK-009','P-DYAK-008',
    'P-HIST-004']))

def write(name, value):
    path = OUT / name
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite {path}')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

if (OUT/'persons.json').exists():
    raise SystemExit('Already bootstrapped; edit existing registries with an audit decision.')
lines = (ROOT/'family_tree.ged').read_text(encoding='utf-8-sig').splitlines()
records = []
for num, line in enumerate(lines, 1):
    m = re.match(r'0 (@[^@]+@) (INDI|FAM)$', line)
    if m:
        records.append({'xref':m[1], 'kind':m[2], 'line':num, 'lines':[]})
    elif records and not line.startswith('0 '):
        records[-1]['lines'].append((num,line))
persons, claims, relationships, events = [], [], [], []
private_rows = []
for record in records:
    if record['kind'] != 'INDI':
        continue
    number = int(record['xref'][2:-1]); pid = MAPPING[number]
    name = next(v[7:] for _,v in record['lines'] if v.startswith('1 NAME '))
    text = '\n'.join(v for _,v in record['lines'])
    birth = re.search(r'1 BIRT\n2 DATE ([^\n]+)',text)
    year = re.search(r'\d{4}',birth[1]) if birth else None
    # Privacy threshold is an export choice, never proof of death.
    redact = (year is None or int(year[0]) >= 1910) and '1 DEAT' not in text
    persons.append({'id':pid,'aliases':[record['xref']],
        'name':'[Личность скрыта: жизненный статус не установлен]' if redact else name,
        'privacy':'redacted' if redact else 'historical_candidate',
        'life_status':'unverified','origin':'legacy_gedcom','status':'hypothesis',
        'source_ids':['S-LEGACY-GED'],'legacy_line':record['line'],
        'kinship_to_client':'not_established'})
    private_rows.append({'id':pid,'name':name,'record':record})
    # Import each top-level fact as its own unverified claim. Never copy legacy
    # narrative notes into public data: they can identify living third parties.
    facts=[]
    for n,v in record['lines']:
        if v.startswith('1 ') and not v.startswith(('1 FAMC','1 FAMS')):
            facts.append((n,v.split(' ',2)[1],v))
    for n,tag,v in facts:
        cid=f'C-LEGACY-I{number:03d}-L{n:04d}'
        claims.append({'id':cid,'subject_id':pid,'predicate':'legacy_'+tag,
            'object':None,'raw_text':None,'privacy':'metadata_only',
            'source_ids':['S-LEGACY-GED'],'source_locator':f'family_tree.ged:{n}',
            'original_vs_derived':'derived','direct_vs_indirect':'unassessed',
            'corroboration':[],'contradictions':[],'reviewer':None,
            'status':'hypothesis','proof_argument_path':None,
            'note':'Факт старого GEDCOM; значение ещё не принято в доказательную базу.'})
        if tag in ('BIRT','DEAT','BURI','MARR','EVEN','RESI'):
            events.append({'id':f'E-{cid}','person_id':pid,'type':tag,
                'claim_id':cid,'date':None,'place':None,'status':'hypothesis'})

def pid(xref):
    return MAPPING[int(xref[2:-1])]

for record in records:
    if record['kind']!='FAM':
        continue
    parents=[(n,pid(v.split()[2])) for n,v in record['lines'] if v.startswith(('1 HUSB ','1 WIFE '))]
    children=[(n,pid(v.split()[2])) for n,v in record['lines'] if v.startswith('1 CHIL ')]
    edges=[]
    if len(parents)==2:
        edges.append(('spouse',parents[0][1],parents[1][1],parents[1][0]))
    for _,parent in parents:
        for n,child in children:
            edges.append(('parent',parent,child,n))
    for i,(kind,a,b,n) in enumerate(edges,1):
        rid=f'R-LEGACY-{record["xref"].strip("@").replace("_","-")}-{i:02d}'
        cid=rid.replace('R-','C-',1)
        claims.append({'id':cid,'subject_id':a,'predicate':kind,'object':b,
            'raw_text':None,'source_ids':['S-LEGACY-GED'],
            'source_locator':f'family_tree.ged:{n}', 'original_vs_derived':'derived',
            'direct_vs_indirect':'unassessed','corroboration':[],
            'contradictions':[],'status':'hypothesis','reviewer':'T-AUD-001',
            'proof_argument_path':'agent_reports/T-AUD-001.md',
            'note':'Снята прежняя безусловная квалификация; связь не опровергнута, но требует доказательств.'})
        relationships.append({'id':rid,'from_person':a,'to_person':b,'type':kind,
            'temporal_scope':None,'claim_id':cid,'status':'hypothesis',
            'export_to_verified':False,'reviewer':'T-AUD-001'})

# Table-only entries also need IDs, without endorsing the table's assertions.
known = {p['id'] for p in persons}
for num, line in enumerate((ROOT/'master_investigation_report.md').read_text(encoding='utf-8-sig').splitlines(), 1):
    m = re.match(r'\| \*\*`(P-[^`]+)`\*\* \| ([^|]+)', line)
    if not m or m[1] in known:
        continue
    person_id = m[1]
    persons.append({'id':person_id,'aliases':[],
        'name':'[Запись прежней таблицы; персональные сведения ожидают проверки]',
        'privacy':'redacted','life_status':'unverified','origin':'legacy_master_table',
        'status':'hypothesis','source_ids':['S-LEGACY-MASTER'],
        'legacy_line':num,'kinship_to_client':'not_established'})
    known.add(person_id)
    claims.append({'id':f'C-LEGACY-MASTER-L{num:04d}', 'subject_id':person_id,
        'predicate':'legacy_person_profile','object':None,'raw_text':None,
        'source_ids':['S-LEGACY-MASTER'],'source_locator':f'master_investigation_report.md:{num}',
        'original_vs_derived':'derived','direct_vs_indirect':'unassessed',
        'status':'hypothesis','reviewer':None,'proof_argument_path':None})

# Separate identities stated in family memory from archive candidates.
for suffix in ('003','004'):
    persons.append({'id':f'P-BARK-{suffix}-MEM','name':'[Родитель из семейной памяти]',
        'aliases':[],'privacy':'redacted','life_status':'unknown','origin':'family_memory',
        'status':'hypothesis','source_ids':['S-MEM-20261030'],
        'kinship_to_client':'reported_not_documented'})
for p in persons:
    if p['id'] in ('P-BARK-003','P-BARK-004A'):
        p['note']='Архивный кандидат; не отождествлять с одноимённым родителем из семейной памяти.'

inventory=[]
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only','e71e6af'],cwd=ROOT,text=True).splitlines()
for filename in tracked:
    path=ROOT/filename
    if path.is_file():
        inventory.append({'path':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'size':path.stat().st_size,'baseline_commit':'e71e6af',
            'read_status':'inventoried_not_automatically_verified'})
sources=[{'id':'S-LEGACY-GED','type':'legacy_compilation','canonical_url':None,
    'local_copy_if_allowed':'family_tree.ged','access_date':DATE,
    'content_hash':hashlib.sha256((ROOT/'family_tree.ged').read_bytes()).hexdigest(),
    'notes':'Сводный GEDCOM; не первичный акт и не доказательство подтверждения заказчиком.'},
    {'id':'S-LEGACY-MASTER','type':'legacy_compilation','access_date':DATE,
    'local_copy_if_allowed':'master_investigation_report.md','canonical_url':None,
    'content_hash':hashlib.sha256((ROOT/'master_investigation_report.md').read_bytes()).hexdigest(),
    'notes':'Первичная инвентаризация утверждений таблицы; не подтверждение родства.'},
    {'id':'S-MEM-20261030','type':'family_memory_relay','access_date':DATE,
    'local_copy_if_allowed':None,'content_hash':None,
    'notes':'Семейные воспоминания изложены в goal; исходная запись интервью не предоставлена. Новых подтверждений спорных связей нет.'}]
for name,value in [('persons.json',persons),('claims.json',claims),
    ('relationships.json',relationships),('events.json',events),('sources.json',sources),
    ('legacy_file_inventory.json',inventory)]:
    write(name,value)
(OUT/'local_cache').mkdir(exist_ok=True)
(OUT/'local_cache'/'legacy_private_import.json').write_text(
    json.dumps(private_rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'persons':len(persons),'claims':len(claims),
    'relationships_quarantined':len(relationships),'events':len(events),
    'legacy_files_inventoried':len(inventory)}))
