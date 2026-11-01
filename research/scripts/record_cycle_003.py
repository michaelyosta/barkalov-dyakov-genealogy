"""Record reviewed 1895 facts; keep 1893/1894 observations pending independent review."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
R = ROOT/'research'
DATE = '2026-10-30'
NAMES = ['persons','claims','relationships','events','sources','research_tasks','search_log','hypotheses','archive_leads']
d = {n:json.loads((R/(n+'.json')).read_text(encoding='utf-8')) for n in NAMES}
if any(p['id']=='P-MET-1895-MIKHAIL' for p in d['persons']):
    raise SystemExit('Cycle 003 records already present. Do not rerun.')
proof = 'biographies/metric_records_1893_1895.md'
s95,s94,s93 = 'S-C003-B1895','S-C003-B1894','S-C003-M1893'
b95='https://ya.ru/archive/catalog/6a0a53cf-1747-4b73-a589-370329276297'
b94='https://ya.ru/archive/catalog/8a6597bf-e880-4aa3-8401-d558fd39eff8'
b93='https://ya.ru/archive/catalog/5fe4c124-e5e4-4d41-a904-b83f0dcc13a4'
for sid,url,delo,locus,record,path,review in [
    (s95,b95+'/9','795','рукописная пагинация 8; скан 9/200','мужская №23','transcriptions/OGAO_389_1_795_record23.md',True),
    (s94,b94+'/69','753','внутренняя пагинация 19; скан 69/224','женская №38','transcriptions/OGAO_389_1_753_record38.md',False),
    (s93,b93+'/86','726','пагинация 83; скан 86/320','брак №73','transcriptions/OGAO_389_1_726_marriage73.md',False)]:
    d['sources'].append({'id':sid,'type':'copy_primary_document','archive':'ОГАОО',
        'collection':'Самарская духовная консистория','fond':'389','opis':'1','delo':delo,
        'list_or_frame':locus,'record_id':record,'canonical_url':url,'access_date':DATE,
        'content_hash':None,'local_copy_if_allowed':None,
        'access_rights':'Read in the user-authorized viewer; image not republished.',
        'access_result':'image_visually_read_by_orchestrator_and_independent_auditor' if review else 'image_visually_read_by_orchestrator',
        'transcription_path':path,
        'transcription_hash':hashlib.sha256((R/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
        'hash_scope':'UTF-8 transcription with LF line endings; no scan image hash',
        'reviewer':'T-AUD-C003' if review else None,
        'independent_image_review':'completed' if review else 'pending_access',
        'independence_group':'OGAO-389-1-'+delo,
        'notes':'Содержание акта и тождество лиц между актами разделены. Независимый аудит обязателен перед структурным повышением.'})

for pid,name,sid,review,note in [
    ('P-MET-1895-MIKHAIL','Михаил [метрическая запись 1895]',s95,True,'Рождение 1895 года; не объединён с Михаилом 1904 или военным кандидатом.'),
    ('P-MET-1895-PETR','Пётр Прохоров Баркалов [отец в акте 1895]',s95,True,'Отдельный актовый взрослый, тождество с поздним Петром не доказано.'),
    ('P-MET-1895-ELENA','Елена Федорова [мать в акте 1895]',s95,True,'Федорова — форма отчества; девичья фамилия неизвестна. Не исправлять имя на Евгению.'),
    ('P-MET-1894-NATALIA','Наталия [запись 1894, аудит ожидается]',s94,False,'Кандидатная актовая запись; parent-рёбра не внесены до независимого чтения.'),
    ('P-MAR-1893-PETR','Пётр Прохоров Баркалов [жених 1893, аудит ожидается]',s93,False,'Отдельный актовый кандидат; по чтению оркестратора возраст 21, первый брак.'),
    ('P-MAR-1893-EVGENIA','Евгения [невеста 1893, аудит ожидается]',s93,False,'По чтению оркестратора дочь Феодора Карпова Мяскова, возраст 20; девичья фамилия производна из отцовской. Родительское ребро пока не создано.'),
    ('P-MAR-1893-FEODOR','Феодор Карпов Мясков [назван в браке 1893, аудит ожидается]',s93,False,'Кандидатная актовая запись; дед Карп не создаётся по одному отчеству.')]:
    d['persons'].append({'id':pid,'name':name,'aliases':[],'privacy':'public_historical_record_entity',
        'life_status':'deceased_historical','status':'supported' if review else 'hypothesis',
        'origin':'reviewed_metric_record_entity' if review else 'pending_independent_metric_review',
        'source_ids':[sid],'kinship_to_client':'not_established','note':note})

def claim(cid,subject,predicate,obj,sids,status='supported',note='',reviewer='T-AUD-C003'):
    c={'id':cid,'subject_id':subject,'predicate':predicate,'object':obj,'raw_text':None,
       'source_ids':sids,'original_vs_derived':'derived' if predicate=='same_person_as' else 'copy_of_primary','direct_vs_indirect':
       'indirect' if predicate=='same_person_as' else 'direct_for_record_content',
       'corroboration':[],'contradictions':[],'reviewer':reviewer,'status':status,
       'proof_argument_path':proof,'note':note,'export_to_verified':False}
    d['claims'].append(c)
    return c

for predicate in ['birth_date_as_written','baptism_date_as_written']:
    cid='C-C003-M95-'+predicate
    claim(cid,'P-MET-1895-MIKHAIL',predicate,'1895-11-07',[s95],note='Дата как в документе; календарь не конвертирован.')
    d['events'].append({'id':'E-C003-M95-'+predicate,'person_id':'P-MET-1895-MIKHAIL',
        'type':predicate,'date':'1895-11-07','calendar':'as_written_not_converted',
        'place':None,'claim_id':cid,'status':'supported'})
for parent,label in [('P-MET-1895-PETR','FATHER'),('P-MET-1895-ELENA','MOTHER')]:
    cid='C-C003-M95-'+label
    claim(cid,parent,'parent','P-MET-1895-MIKHAIL',[s95],note='Прямое содержание независимо прочитанного акта, без отождествления с поздними родителями.')
    d['relationships'].append({'id':'R-C003-M95-'+label,'from_person':parent,
        'to_person':'P-MET-1895-MIKHAIL','type':'parent','temporal_scope':'1895',
        'claim_id':cid,'status':'supported','export_to_verified':False,'reviewer':'T-AUD-C003'})
claim('C-C003-M95-SPOUSE','P-MET-1895-PETR','recorded_spouse','P-MET-1895-ELENA',[s95],
      note='Названа законной женой в акте рождения; дата и место брака не установлены.')
d['relationships'].append({'id':'R-C003-M95-SPOUSE','from_person':'P-MET-1895-PETR',
    'to_person':'P-MET-1895-ELENA','type':'recorded_spouse','temporal_scope':'1895',
    'claim_id':'C-C003-M95-SPOUSE','status':'supported','export_to_verified':False,'reviewer':'T-AUD-C003'})

identities=[
 ('PETR95-LATE','P-MET-1895-PETR','P-MET-PETR-PROKHOROV',[s95,'S-C002-MET-1899-49'],'T-C003-PARENTS-CONFLICT',
  'Совпадают ФИО и село, но матери детей названы Еленой и Евгенией. Тождество взрослых не доказано.'),
 ('ELENA-EVGENIA','P-MET-1895-ELENA','P-MET-EVGENIA-FEODOROVA',[s95,'S-C002-MET-1899-49'],'T-C003-PARENTS-CONFLICT',
  'Проверяемая возможность, не утверждение варианта имени. Прямое расхождение имён сохраняется; причина неизвестна.'),
 ('GROOM93-LATE','P-MAR-1893-PETR','P-MET-PETR-PROKHOROV',[s93,'S-C002-MET-1899-49'],'T-C003-INDEPENDENT-READ',
  'ФИО, деревня и имя супруги согласуются; изображение брака независимо не проверено. Слияние запрещено.'),
 ('BRIDE93-LATE','P-MAR-1893-EVGENIA','P-MET-EVGENIA-FEODOROVA',[s93,'S-C002-MET-1899-49'],'T-C003-INDEPENDENT-READ',
  'Имя/ожидаемое отчество и супруг согласуются; девичья фамилия не переносится на позднюю мать до независимой проверки и идентификации.')]
for suffix,subject,obj,sids,task,note in identities:
    cid='C-ID-C003-'+suffix
    c=claim(cid,subject,'same_person_as',obj,sids,'hypothesis',note,
            'T-AUD-C003' if s93 not in sids else None)
    if suffix=='ELENA-EVGENIA':c['contradictions']=['Имя Елена в 1895 против Евгении в 1899/1904; не разрешено.']
    d['hypotheses'].append({'id':'H-ID-C003-'+suffix,'claim_ids':[cid],'status':'hypothesis',
        'question':note,'next_task':task})

for tid,ids,question,priority,suggested,follow in [
 ('T-C003-INDEPENDENT-READ',['P-MET-1894-NATALIA','P-MAR-1893-PETR','P-MAR-1893-EVGENIA','P-MAR-1893-FEODOR'],
  'Подтверждаются ли по независимому чтению акты 1894 №38 и 1893 №73?',1,
  'ОГАОО 389/1/753 скан 69; 389/1/726 скан 86',
  'У аудитора IAB не обнаружен. Повторить при фактическом доступе; root может продолжать другие источники. Не создавать по этим актам parent/spouse-рёбра до проверки.'),
 ('T-C003-PARENTS-CONFLICT',['P-MET-1895-PETR','P-MET-1895-ELENA','P-MET-PETR-PROKHOROV','P-MET-EVGENIA-FEODOROVA'],
  'Почему при совпадающем ФИО отца матери названы Еленой и Евгенией?',1,
  'Брачные обыски, посемейные списки, другие рождения и смерти, возраст и происхождение супругов',
  'Проверить тёзок и документальный состав семьи; не выбирать версию повторного брака или ошибки по вероятности.'),
 ('T-C003-EARLY-DEATH',['P-MET-1895-MIKHAIL','P-MET-1904-MIKHAIL'],
  'Какова судьба Михаила 1895 года; есть ли запись о смерти до 1904?',2,
  'Дмитриевские смерти 1895–1904, варианты Баркалов/Боркалов и имя отца',
  'Фамильный OCR-поиск по 1895 дал 8 сканов, явной целевой смерти в сниппетах нет. Сплошной просмотр смертей и последующие годы ещё не выполнены.')]:
    d['research_tasks'].append({'task_id':tid,'linked_people':ids,'precise_question':question,
        'priority':priority,'suggested_source':suggested,'owner':'orchestrator','last_search':DATE,
        'status':'open','blocker':None,'follow_up':follow,'checkpoint':'checkpoint.md'})
for t in d['research_tasks']:
    if t['task_id']=='T-MET-PARENTS-MARRIAGE':
        t.update(status='in_progress',last_search=DATE,
            follow_up='Найден акт 1893 №73 с Петром и Евгенией; требуется независимое чтение, точный приход и мост к поздней паре. Не объявлять задачу решённой по одному совпадению.')
    elif t['task_id']=='T-MET-SIBLINGS':
        t.update(status='in_progress',last_search=DATE,
            follow_up='Ранние акты с Еленой 1894/1895 отделены от пары с Евгенией. Не добавлять Наталию или раннего Михаила как братьев/сестёр поздних детей без разрешения идентичностей.')

for sid,delo,locus,task in [(s95,'795','8; №23; скан 9','T-C003-PARENTS-CONFLICT'),
                           (s94,'753','внутренняя 19; №38; скан 69','T-C003-INDEPENDENT-READ'),
                           (s93,'726','83; №73; скан 86','T-C003-INDEPENDENT-READ')]:
    d['archive_leads'].append({'id':'AL-C003-OG-'+delo,'archive_id':'A-OGAO-O',
        'fond':'389','opis':'1','delo':delo,'list_or_frame':locus,
        'title_as_described':'Выборочно прочитанный метрический акт; заголовок книги и транскрипция в sources',
        'date_as_described':{'795':'1895','753':'1894','726':'1893'}[delo],
        'source_ids':[sid],'source_locator':locus,'access_date':DATE,'status':'supported',
        'reviewer':'T-AUD-C003' if sid==s95 else None,'original_seen':True,
        'person_named_or_found':True,'task_ids':[task],
        'notes':'Прочитан оркестратором только указанный акт, не вся книга. Независимый аудит '+('выполнен.' if sid==s95 else 'ожидается; структурные рёбра не созданы.')})

for i,(resource,query,count,outcome,refs) in enumerate([
    (b95,'Петр Прохоров',17,'Скан 9: целевой ранний акт; скан 14: поручитель. Иные попадания не импортированы как родственники.',[s95]),
    (b95,'Баркалов',8,'Сканы 4,9,13,14,18,11,17,8. Сниппеты не показали смерти раннего Михаила; это не сплошной просмотр.',[s95]),
    (b94,'Петр Прохоров Баркалов',2,'Сканы 69 и 76. Прочитан акт Наталии 69; 76 остаётся OCR-ориентиром, не именной находкой в графе.',[s94]),
    (b93,'Петр Прохоров Баркалов',3,'Сканы 86,285,83. Прочитан брак 86; 285 содержит разрозненные слова, 83 — Ольга Прохорова, не доказанная сестра.',[s93]),
    ('https://ya.ru/archive/catalog/c6212baf-b01b-4009-b9df-c5c82bf57608/20','Повторное визуальное чтение имени матери',None,
     'Оркестратор заново читает Евгения в акте 1899. Предыдущая транскрипция не изменена.',['S-C002-MET-1899-49'])],1):
    d['search_log'].append({'id':f'SR-C003-{i:03d}','task_id':'T-C003-PARENTS-CONFLICT',
        'exact_query':query,'resource':resource,'date':DATE,
        'filters/time_span':'Поиск внутри указанного дела, похожие слова выключены; кроме явно обозначенного визуального перечтения.',
        'result_count':count,'result_refs':refs,'negative_scope':'OCR, выбранные строки и указанные сканы; не полная проверка дела или прихода.',
        'outcome':outcome,'next_action':'См. очередь и доказательную записку.'})
for n,rows in d.items():
    (R/(n+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'decisions.jsonl').open('a',encoding='utf-8') as f:
    for row in [
      {'id':'D-C003-002','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-C003',
       'action':'separate_reviewed_1895_family','reason':'Елена прочитана независимо, не заменена на Евгению. Созданы только отдельные актовые связи 1895; тождества между группами hypothesis.','reversible':True},
      {'id':'D-C003-003','date':DATE,'actor':'orchestrator','action':'hold_1893_1894_structural_promotion',
       'source_ids':[s93,s94],'reason':'Оркестратор прочитал акты, но независимый аудитор не получил доступ к изображениям. Кандидатные лица и источники сохранены, брачные/родительские рёбра по этим актам не созданы.','reversible':True}]:
        f.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps({n:len(rows) for n,rows in d.items()},ensure_ascii=False))
