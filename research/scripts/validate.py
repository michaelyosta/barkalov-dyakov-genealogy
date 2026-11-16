"""Check evidence references and export eligibility, not historical truth."""
from datetime import date
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'research'
TEXT_EXTS=('.txt','.md','.ged','.json','.jsonl','.html','.csv','.py')
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
institutions,aids=load('institutions') if (R/'institutions.json').exists() else ([],{})
archive_leads,alids=load('archive_leads') if (R/'archive_leads.json').exists() else ([],{})
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
for institution in institutions:
    require(all(s in sids for s in institution['source_ids']),institution['id']+': source missing')
    require(institution['status'] in statuses,institution['id']+': invalid status')
for lead in archive_leads:
    require(lead['archive_id'] in aids,lead['id']+': archive missing')
    require(all(s in sids for s in lead['source_ids']),lead['id']+': source missing')
    require(all(t in tids for t in lead['task_ids']),lead['id']+': task missing')
    require(lead['status'] in statuses,lead['id']+': invalid status')
    if not lead['original_seen']:
        require(not lead.get('person_named_or_found'),lead['id']+': catalogue-only person assertion')
for source in sources:
    transcription=source.get('transcription_path')
    if transcription:
        path=R/transcription
        require(path.is_file(),source['id']+': transcription missing')
        if path.exists() and source.get('transcription_hash'):
            require(hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()==source['transcription_hash'],source['id']+': transcription hash changed')
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
            if local.lower().endswith(TEXT_EXTS):
                content=content.replace(b'\r\n',b'\n')
            require(hashlib.sha256(content).hexdigest()==source['content_hash'],source['id']+': source hash changed')
def validate_gedcom(ged_path,label,require_no_fam=False):
    """Validate basic GEDCOM 5.5.1 framing, cross-references, and INDI<->FAM symmetry."""
    ged=ged_path.read_text(encoding='utf-8-sig').replace('\r\n','\n')
    definitions=set(re.findall(r'^0 (@[^@]+@) \w+',ged,re.M))
    references=set(re.findall(r'^\d+ (?:SUBM|FAMC|FAMS|HUSB|WIFE|CHIL|SOUR) (@[^@]+@)',ged,re.M))
    require(references<=definitions,f'{label}: dangling cross-references {sorted(references-definitions)}')
    require(ged.startswith('0 HEAD\n') and ged.rstrip().endswith('0 TRLR'),f'{label}: GEDCOM boundary missing')
    require('2 VERS 5.5.1' in ged and '1 CHAR UTF-8' in ged,f'{label}: GEDCOM encoding/version missing')
    if require_no_fam:
        require(not re.search(r'^0 @[^@]+@ FAM',ged,re.M),f'{label}: verified export unexpectedly contains family edges')
    recs={}
    cur_id=None
    for line in ged.splitlines():
        m0=re.match(r'^0 (@[^@]+@) (\w+)',line)
        if m0:
            cur_id=m0.group(1)
            recs[cur_id]={'type':m0.group(2),'FAMS':set(),'FAMC':set(),'HUSB':set(),'WIFE':set(),'CHIL':set()}
        elif line.startswith('0 '):
            cur_id=None
        elif cur_id:
            m1=re.match(r'^1 (FAMS|FAMC|HUSB|WIFE|CHIL) (@[^@]+@)',line)
            if m1:
                recs[cur_id][m1.group(1)].add(m1.group(2))
    for iid,d in recs.items():
        if d['type']=='INDI':
            for fid in d['FAMS']:
                fam=recs.get(fid,{})
                require(fam.get('type')=='FAM' and (iid in fam.get('HUSB',set()) or iid in fam.get('WIFE',set())),
                        f'{label}: {iid} FAMS {fid} missing HUSB/WIFE backlink')
            for fid in d['FAMC']:
                fam=recs.get(fid,{})
                require(fam.get('type')=='FAM' and iid in fam.get('CHIL',set()),
                        f'{label}: {iid} FAMC {fid} missing CHIL backlink')
        elif d['type']=='FAM':
            for sid in d['HUSB']|d['WIFE']:
                ind=recs.get(sid,{})
                require(ind.get('type')=='INDI' and iid in ind.get('FAMS',set()),
                        f'{label}: {iid} spouse {sid} missing FAMS backlink')
            for cid in d['CHIL']:
                ind=recs.get(cid,{})
                require(ind.get('type')=='INDI' and iid in ind.get('FAMC',set()),
                        f'{label}: {iid} CHIL {cid} missing FAMC backlink')
def validate_markdown_links():
    """Verify relative Markdown links across repository docs resolve to existing paths."""
    link_re=re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
    for md in sorted(ROOT.rglob('*.md')):
        if '.git' in md.parts:
            continue
        cleaned=re.sub(r'```.*?```','',md.read_text(encoding='utf-8',errors='ignore'),flags=re.S)
        for target in link_re.findall(cleaned):
            raw=target.strip()
            if not raw or raw.startswith(('http://','https://','mailto:','#','data:')):
                continue
            rel_part=raw.split('#',1)[0].split(' ',1)[0]
            if not rel_part:
                continue
            resolved=(md.parent/rel_part).resolve()
            require(resolved.exists(),f'{md.relative_to(ROOT)}: broken relative link -> {raw}')
verified_edges=sum(e['export_to_verified'] for e in relationships)
validate_gedcom(ROOT/'family_tree_verified.ged','family_tree_verified.ged',require_no_fam=(verified_edges==0))
validate_gedcom(ROOT/'family_tree.ged','family_tree.ged',require_no_fam=False)
validate_markdown_links()
report={'date':date.today().isoformat(),'errors':errors,'counts':{k:len(v) for k,v in [('persons',people),('claims',claims),('relationships',relationships),('events',events),('sources',sources),('tasks',tasks),('institutions',institutions),('archive_leads',archive_leads)]},
    'verified_family_edges':verified_edges,
    'scope':'JSON links, status/export constraints, source hashes, bidirectional GEDCOM structure, relative Markdown links. Not a genealogical software import or proof of historical truth.'}
(R/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
