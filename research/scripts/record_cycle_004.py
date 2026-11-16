"""Record a death candidate with conflicting age and an indexed student-file lead."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'research'
DATE='2026-10-30'
names=['persons','claims','relationships','events','sources','research_tasks','search_log','hypotheses','institutions','archive_leads']
d={n:json.loads((R/(n+'.json')).read_text(encoding='utf-8')) for n in names}
sd,se='S-C004-DEATH1896','S-C004-CGA-STUDENT'
if any(s['id']==sd for s in d['sources']):raise SystemExit('Cycle 004 already recorded; do not rerun.')
proof='cycle_004.md'
for sid,path,url,kind,archive,fond,opis,delo,locus,review,notes in [
 (sd,'transcriptions/OGAO_389_1_854_death17.md','https://ya.ru/archive/catalog/f5a43f77-e7b2-48bb-b08e-372f1b5bfd3c/116',
  'copy_primary_document','ОГАОО','389','1','854','внешняя 113, внутренняя 34; мужская №17; скан 116/124',None,
  'Изображение прочитано только оркестратором. Возраст 8 месяцев конфликтует с ноябрьским рождением кандидата. Мать не названа.'),
 (se,'evidence_notes/CGA_R7409_op12_student_barkalov.md','https://spbarchives.ru/infres/-/archive/cga/R-7409/12',
  'search_indexed_official_catalogue','ЦГА СПб','Р-7409','12',None,'первая страница выдачи, порядковая строка 10',None,
  'Индексированный текст официального каталога; прямое открытие не удалось, личное дело не читалось. Порядковая строка 10 не принята за номер дела.')]:
    d['sources'].append({'id':sid,'type':kind,'archive':archive,'collection':None,
      'fond':fond,'opis':opis,'delo':delo,'list_or_frame':locus,'record_id':None,
      'canonical_url':url,'access_date':DATE,'content_hash':None,'local_copy_if_allowed':None,
      'access_rights':'Read-only research; underlying image/file not republished.',
      'access_result':'image_visually_read_by_orchestrator' if sid==sd else 'search_index_text_only_direct_page_unavailable',
      'transcription_path':path,'transcription_hash':hashlib.sha256((R/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
      'hash_scope':'UTF-8 research transcription/note with LF; not source page or image hash',
      'reviewer':review,'independent_image_review':'pending' if sid==sd else 'not_applicable_catalogue_only',
      'notes':notes})
for pid,name,sid,note in [
 ('P-REC-1896-MIKHAIL-DEATH','Михаил [запись о смерти 1896]',sd,
  'Отдельная актовая запись. Не объединена с ребёнком 1895 или Михаилом 1904; возраст 8 месяцев сохранён.'),
 ('P-CAT-1921-SERGEY','Сергей Петрович Баркалов [студенческая каталожная запись 1921]',se,
  'Год/место рождения неизвестны. Дело не прочитано, номер не установлен. Не объединён с военным или метрическим Сергеем.')]:
    d['persons'].append({'id':pid,'name':name,'aliases':[],'privacy':'public_historical_record_entity',
      'life_status':'deceased' if sid==sd else 'unknown','status':'supported','origin':'separate_source_record_entity',
      'source_ids':[sid],'kinship_to_client':'not_established','note':note})
def claim(cid,pid,pred,value,sids,status='supported',note=''):
    row={'id':cid,'subject_id':pid,'predicate':pred,'object':value,'raw_text':None,
      'source_ids':sids,'status':status,'reviewer':None,'export_to_verified':False,
      'original_vs_derived':'derived' if pred=='same_person_as' else ('copy_of_primary' if sids==[sd] else 'search_index'),
      'direct_vs_indirect':'indirect' if pred=='same_person_as' else 'direct_for_observed_record_content',
      'corroboration':[],'contradictions':[],'proof_argument_path':proof,'note':note}
    d['claims'].append(row);return row
pd='P-REC-1896-MIKHAIL-DEATH'
for suffix,pred,value in [
 ('DEATH','death_date_as_written','1896-05-02'),('BURIAL','burial_date_as_written','1896-05-03'),
 ('AGE','recorded_age_at_death','8 месяцев'),('FATHER','recorded_father_text','Петр Прохоров Баркалов'),
 ('CAUSE','recorded_historical_cause_of_death','отъ младенскаго')]:
    cid='C-C004-D96-'+suffix
    claim(cid,pd,pred,value,[sd],note='Содержание строки по чтению оркестратора; независимое чтение ожидается. Календарь не конвертирован.')
    if suffix in ['DEATH','BURIAL']:
      d['events'].append({'id':'E-C004-D96-'+suffix,'person_id':pd,'type':pred,'date':value,
        'calendar':'as_written_not_converted','place':None,'claim_id':cid,'status':'supported'})
ps='P-CAT-1921-SERGEY'
for suffix,pred,value in [
 ('TITLE','catalogued_record_description','Личное дело студента ветеринарного института, исключённого и выбывшего; Баркалов Сергей Петрович'),
 ('DATE','catalogued_document_date','1921-08-22'),('EXTENT','catalogued_extent','8 листов')]:
    claim('C-C004-STUDENT-'+suffix,ps,pred,value,[se],
      note='Только содержание поискового индекса официальной описи; дата не отождествляется с зачислением или выбытием, квалификация не установлена.')
c=claim('C-ID-C004-DEATH-BIRTH',pd,'same_person_as','P-MET-1895-MIKHAIL',[sd,'S-C003-B1895'],'hypothesis',
  'Имя, ФИО отца и село согласуются, но возраст в смерти 8 месяцев, а по рождению было бы около 6. Мать не названа; причина расхождения неизвестна.')
c['contradictions']=['Возраст 8 месяцев против около 6 месяцев между 07.11.1895 и 02.05.1896.']
claim('C-ID-C004-STUDENT-MILITARY',ps,'same_person_as','P-BARK-005',[se,'S-MIL-003'],'hypothesis',
  'Совпадает полное ФИО; год/место рождения студента неизвестны. Ветеринарный и медицинский профиль не отождествляются; содержание дела нужно прочитать.')
d['hypotheses'] += [
 {'id':'H-ID-C004-DEATH','claim_ids':['C-ID-C004-DEATH-BIRTH'],'status':'hypothesis','question':'Совпадает ли умерший с ребёнком 1895 при конфликте возраста?','next_task':'T-C003-EARLY-DEATH'},
 {'id':'H-ID-C004-STUDENT','claim_ids':['C-ID-C004-STUDENT-MILITARY'],'status':'hypothesis','question':'Связывает ли личное дело студента военного Сергея с гражданской семьёй?','next_task':'T-C004-CGA-STUDENT'}]
for tid,ids,q,source,follow in [
 ('T-C004-CGA-STUDENT',[ps,'P-BARK-005','P-MET-1899-SERGEY'],
  'Каков точный номер и содержание личного дела студента Сергея Петровича Баркалова, Р-7409/12?',se,
  'Найти детальную карточку или скан описи; строка10 — номер выдачи. В анкете искать точный день/место рождения, родителей и квалификацию. Запрос не отправлять.'),
 ('T-C004-INDEPENDENT-DEATH',[pd,'P-MET-1895-MIKHAIL'],
  'Подтверждаются ли независимым изображением смерть 02.05.1896 и возраст 8 месяцев?',sd,
  'Прочитать 854/116; не исправлять возраст и не объединять умершего с ребёнком1895 до разрешения противоречия.')]:
    d['research_tasks'].append({'task_id':tid,'linked_people':ids,'precise_question':q,'priority':1,
      'suggested_source':source,'owner':'orchestrator','last_search':DATE,'status':'open',
      'blocker':None,'follow_up':follow,'checkpoint':'checkpoint.md'})
for t in d['research_tasks']:
    if t['task_id']=='T-C003-EARLY-DEATH':t.update(status='in_progress',last_search=DATE,
      follow_up='Найден акт смерти 1896 №17 с тем же ФИО отца; возраст8 конфликтует с ноябрьским рождением. Проверить оригинал независимо и другие одноимённые рождения; не считать задачу решённой.')
    if t['task_id']=='T-MET-ID-SERGEY':t.update(last_search=DATE,
      follow_up='Новый ориентир — личное дело студента в Р-7409/12, дата22.08.1921,8листов. Номер дела и идентичность не установлены; см.T-C004-CGA-STUDENT.')
if not any(i['id']=='A-CGA-SPB' for i in d['institutions']):
    d['institutions'].append({'id':'A-CGA-SPB','name':'Центральный государственный архив Санкт-Петербурга',
      'kind':'archive','published_address':None,'source_ids':[se],'access_date':DATE,
      'status':'supported','notes':'Держатель описи по названию официального портала; адрес и условия доступа в этом этапе не проверялись.'})
for lid,aid,fond,opis,delo,sid,seen,task,note in [
 ('AL-C004-OG-854','A-OGAO-O','389','1','854',sd,True,'T-C004-INDEPENDENT-DEATH','Выборочно прочитан акт, не вся книга. Независимое чтение ожидается.'),
 ('AL-C004-CGA-STUDENT','A-CGA-SPB','Р-7409','12',None,se,False,'T-C004-CGA-STUDENT','Строка10 поисковой выдачи не считается номером дела. Оригинал личного дела не получен.')]:
    d['archive_leads'].append({'id':lid,'archive_id':aid,'fond':fond,'opis':opis,'delo':delo,
      'list_or_frame':'№17, скан116' if seen else 'первая страница описи, строка10',
      'title_as_described':'Смерть Михаила' if seen else 'Личное дело студента Баркалова Сергея Петровича',
      'date_as_described':'1896' if seen else '22.08.1921','source_ids':[sid],
      'source_locator':'См. источник и запись наблюдения','access_date':DATE,'status':'supported',
      'reviewer':None,'original_seen':seen,'person_named_or_found':seen,'task_ids':[task],'notes':note})
for i,(task,q,res,count,result,sids) in enumerate([
 ('T-C003-EARLY-DEATH','Петр Прохоров Баркалов','https://ya.ru/archive/catalog/f5a43f77-e7b2-48bb-b08e-372f1b5bfd3c',2,
  'Сканы116 и31;116 — смерть сына Михаила.31 — Фекла, не проверенный родственник.',[sd]),
 ('T-C004-CGA-STUDENT','site:spbarchives.ru/infres/-/archive/cga/R-7409/12 "Баркалов Сергей Петрович"','web_search',None,
  'Отображён индексированный текст официальной описи: строка10, дата22.08.1921,8листов; оригинал дела не читался.',[se]),
 ('T-C004-CGA-STUDENT','https://spbarchives.ru/infres/-/archive/cga/R-7409/12','web_open_and_public_http',None,
  'Прямое открытие тайм-аут, Python HTTP WinError10060; детали дела не получены.',[se]),
 ('T-C004-CGA-STUDENT','https://spbarchives.ru/infres/-/archive/cga/R-7409/12/10','single_candidate_detail_open',None,
  'Предполагаемая карточка недоступна. Этот URL не принят за подтверждённый шифр.',[se])],1):
    d['search_log'].append({'id':f'SR-C004-{i:03d}','task_id':task,'exact_query':q,'resource':res,
      'date':DATE,'result_count':count,'result_refs':sids,'negative_scope':'Только указанная книга/запрос/канал. Не доказывает отсутствие человека или дела.',
      'outcome':result,'next_action':'См. очередь и cycle_004.md'})
for n,rows in d.items():(R/(n+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'decisions.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps({'id':'D-C004-001','date':DATE,'actor':'orchestrator','action':'preserve_death_age_conflict_and_catalogue_student_separately',
      'source_ids':[sd,se],'reason':'Возраст смерти не исправлен под найденное рождение. Студент не отождествлён с военным по ФИО, номер строки не выдан за номер дела. Новые родственные рёбра не созданы.','reversible':True},ensure_ascii=False)+'\n')
print(json.dumps({n:len(rows) for n,rows in d.items()},ensure_ascii=False))
