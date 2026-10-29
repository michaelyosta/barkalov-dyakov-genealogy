"""Check evidence references and export eligibility, not historical truth."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'research'
errors=[]
def require(condition,message):
    if not condition: errors.append(message)
def load(name,key='id'):
    rows=json.loads((R/(name+'.json')).read_text(encoding='utf-8'))
    require(len({r[key] for r in rows})==len(rows),f'{name}: duplicate IDs')
    return rows,{r[key]:r for r in rows}
people,pids=load('persons')
claims,cids=load('claims')
relationships,rids=load('relationships')
events,eids=load('events')
sources,sids=load('sources')
tasks,tids=load('research_tasks','task_id')
logs,lids=load('search_log')
hypotheses,hids=load('hypotheses')
statuses={'confirmed','supported','hypothesis','contradicted','rejected'}
for person in people:
    require(person['status'] in statuses,person['id']+': invalid status')
    require(all(s in sids for s in person['source_ids']),person['id']+': source missing')
    if person['privacy']=='redacted':
        require(person['name'].startswith('['),person['id']+': unredacted name')
for claim in claims:
    require(claim['status'] in statuses,claim['id']+': invalid status')
    require(claim['subject_id'] in pids,claim['id']+': subject missing')
    require(all(s in sids for s in claim['source_ids']),claim['id']+': source missing')
    if claim['predicate'] in ('parent','spouse','recorded_spouse','same_person_as','ancestor_of','sibling_of','marriage_in_1959'):
        require(claim['object'] in pids,claim['id']+': target missing')
    if claim['status']=='confirmed':
        require(claim.get('reviewer') is not None,claim['id']+': no independent review')
        require(bool(claim.get('proof_argument_path')),claim['id']+': no proof argument')
    if claim.get('proof_argument_path'):
        require((R/claim['proof_argument_path']).is_file(),claim['id']+': proof file missing')
for edge in relationships:
    require(edge['from_person'] in pids and edge['to_person'] in pids,edge['id']+': endpoint missing')
    require(edge['claim_id'] in cids,edge['id']+': claim missing')
    claim=cids.get(edge['claim_id'],{})
    require(claim.get('subject_id')==edge['from_person'] and claim.get('object')==edge['to_person'],edge['id']+': inconsistent endpoints')
    require(claim.get('status')==edge['status'],edge['id']+': inconsistent status')
    if edge['export_to_verified']:
        require(edge['status']=='confirmed',edge['id']+': unsupported export')
        require(edge.get('reviewer') is not None,edge['id']+': unreviewed export')
for event in events:
    require(event['person_id'] in pids and event['claim_id'] in cids,event['id']+': broken reference')
for task in tasks:
    require(all(p in pids for p in task['linked_people']),task['task_id']+': person missing')
    require(task['status'] in {'open','in_progress','blocked','needs_human','verified','exhausted'},task['task_id']+': bad status')
for log in logs:
    require(log['task_id'] in tids,log['id']+': task missing')
for hypothesis in hypotheses:
    require(all(c in cids for c in hypothesis['claim_ids']),hypothesis['id']+': claim missing')
    require(hypothesis['next_task'] in tids,hypothesis['id']+': task missing')
for source in sources:
    local=source.get('local_copy_if_allowed')
    if local:
        path=ROOT/local
        # Cache may be absent on another checkout; source URLs/hash survive.
        if not local.startswith('research/local_cache/'):
            require(path.is_file(),source['id']+': local source missing')
        if path.exists() and source.get('content_hash'):
            if source.get('baseline_commit'):
                content=subprocess.check_output(['git','show',source['baseline_commit']+':'+local],cwd=ROOT)
            else:
                content=path.read_bytes()
            require(hashlib.sha256(content).hexdigest()==source['content_hash'],source['id']+': source hash changed')
ged=(ROOT/'family_tree_verified.ged').read_text(encoding='utf-8')
definitions=set(re.findall(r'^0 (@[^@]+@) \w+',ged,re.M))
references=set(re.findall(r'^\d+ (?:SUBM|FAMC|FAMS|HUSB|WIFE|CHIL) (@[^@]+@)',ged,re.M))
require(references<=definitions,'GEDCOM dangling cross-references')
require(ged.startswith('0 HEAD\n') and ged.rstrip().endswith('0 TRLR'),'GEDCOM boundary missing')
require('2 VERS 5.5.1' in ged and '1 CHAR UTF-8' in ged,'GEDCOM encoding/version missing')
require(not re.search(r'^0 @[^@]+@ FAM',ged,re.M),'Cycle001 export unexpectedly contains family edges')
original=next(s for s in sources if s['id']=='S-LEGACY-GED')
require(hashlib.sha256((ROOT/'family_tree.ged').read_bytes().replace(b'\r\n',b'\n')).hexdigest()==original['content_hash'],'Legacy GEDCOM modified')
report={'date':'2026-10-30','errors':errors,'counts':{k:len(v) for k,v in [('persons',people),('claims',claims),('relationships',relationships),('events',events),('sources',sources),('tasks',tasks)]},
    'verified_family_edges':sum(e['export_to_verified'] for e in relationships),
    'scope':'JSON links, status/export constraints, source hashes, basic GEDCOM structure. Not a genealogical software import or proof of historical truth.'}
(R/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
