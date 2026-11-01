"""Record reviewed observations once. Does not establish client kinship."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'research'
DATE='2026-10-30'
def read(name): return json.loads((R/name).read_text(encoding='utf-8'))
def save(name,value): (R/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
people,claims,rels,events,sources=[read(n+'.json') for n in ('persons','claims','relationships','events','sources')]
if any(c['id']=='C-OBS-001' for c in claims):
    raise SystemExit('Cycle already recorded; use a new reviewed decision for further edits.')

def source(sid,kind,url,path=None,locator=None,notes='',group=None):
    sources.append({'id':sid,'type':kind,'archive':None,'collection':None,
        'fond':None,'opis':None,'delo':None,'list_or_frame':locator,
        'record_id':None,'canonical_url':url,'access_date':DATE,
        'content_hash':hashlib.sha256((ROOT/path).read_bytes()).hexdigest() if path else None,
        'local_copy_if_allowed':path,'access_rights':'Existing local copy or read-only open source; no new permission to republish assumed.',
        'transcription_path':None,'notes':notes,'independence_group':group})

source('S-MIL-001','copy_primary_document','https://obd-memorial.ru/html/info.htm?id=2153465',
    'documents/tsamo_293sd_barkalov_mp_1.jpg','строка57',
    'ЦАМО ф.58 оп.18001 д.250 л.17 — шифр по прежнему каталогу. Изображение просмотрено двумя исполнителями; обложка дела не сверена.','293sd')
source('S-MIL-002','copy_primary_document','https://obd-memorial.ru/html/info.htm?id=6164832',
    'documents/tsamo_1034sp_barkalov_mp_2.jpg','извещение578 от03.12.1942',
    'ЦАМО ф.58 оп.18001 д.488 л.653 — шифр по прежнему каталогу. Изображение просмотрено; год рождения в нём отсутствует.','293sd')
source('S-MIL-003','copy_primary_document','https://obd-memorial.ru/html/info.htm?id=4487593',
    'documents/tsamo_barkalov_sp_4487593.jpg','первая строка',
    'ЦАМО ф.33 оп.11458 д.366 л.37 — по прежнему каталогу; скан прочитан военным исследователем.','seg282')
source('S-ANT-001','index_transcription','https://ru.openlist.wiki/Баркалова_Антонида_Григорьевна_(1909)',
    'documents/openlist_target_pages.txt','строки69–97',
    'Локальная прежняя выгрузка. Дата исходного получения неизвестна; 2026-10-30 — дата повторного чтения. Прямое открытие сайта вернуло403, поисковая копия не независимый источник.','kz-repression-index')
source('S-KNB-001','official_guidance','https://www.gov.kz/org/knb/activities/15143?lang=ru',
    locator='Об архивных материалах, строки57–64 веб-представления',
    notes='Открыта официальная страница. Разделяет компетенцию МВД и КПСиСУ; это не подтверждение места хранения конкретного дела. Адресные сведения страницы требуют проверки перед отправкой.')
source('S-KUZ-001','journalistic_account','https://shahtinsklib.kz/files/userfiles/karlag/kuznecova_deti_karlaga.pdf',
    'research/local_cache/kuznecova_deti_karlaga.pdf','единственная страница; левая колонка',
    'Е.Кузнецова описывает просмотр книги воспитанников1936г. Учреждение-хранитель, шифр, дата и номер газеты не установлены. PDF и рендер визуально проверены; только локальный кэш.')
source('S-CHILD-2024','scholarly_publication','https://doi.org/10.31489/2024HPh3/7-25',
    'research/local_cache/orphanages_2024.pdf','печатные с.9,22–23; PDF страницы3,16–17',
    'К.К.Абдрахманова, З.Г.Сактаганова,2024. Архивные шифры через публикацию; сами дела не просмотрены. PDF-кэш не публикуется.')
source('S-CAU-1853','published_translation','https://doukhobor.ru/literatura/1853%20TAX%20REGISTER%20OF%20DOUKHOBORS%20IN%20THE%20CAUCASUS.pdf',
    locator='печатнаяс.65, GORELOE, Abrosimov',
    notes='По опубликованному переводу/текстовому слою. Русский оригинал не просмотрен. Старый локальный trdc_1853.pdf — неполная выдержка, не полная книга.')
source('S-CAU-1873-INDEX','surname_index','https://doukhobor.org/1873-villages-families/',
    locator='Village-Surname Index',notes='Индекс фамилий по селениям, без состава семей. См.T-CAU-001.')
source('S-CAU-1853-INDEX','surname_index','https://doukhobor.org/1853-villages-families/',
    locator='Village-Surname Index',notes='Индекс фамилий по селениям, без состава семей. См.T-CAU-001.')
source('S-CAU-1886-CAT','library_catalogue','https://rusneb.ru/catalog/000199_000009_005403186/',
    locator='библиографическая запись',notes='Свод статистических данных, Тифлис1893. Каталог и прежние выдержки; полный скан и первичные семейные листы в этом цикле не просмотрены.')

for sid, fond, opis, delo in [('S-MIL-001','58','18001','250'),('S-MIL-002','58','18001','488'),('S-MIL-003','33','11458','366')]:
    row=next(s for s in sources if s['id']==sid)
    row.update(archive='ЦАМО',fond=fond,opis=opis,delo=delo,catalogue_verified_from_cover=False)
for s in sources:
    s.setdefault('baseline_commit','e71e6af' if s['id'].startswith('S-LEGACY-') else None)
    if s.get('baseline_commit'):
        s['original_worktree_sha256']=s['content_hash']
        s['content_hash']=hashlib.sha256(subprocess.check_output(
            ['git','show',s['baseline_commit']+':'+s['local_copy_if_allowed']],cwd=ROOT)).hexdigest()
        s['content_hash_scope']='git_blob_at_baseline_commit; worktree hash recorded separately because of Windows line endings'

def claim(cid,pid,predicate,value,sids,status='supported',locator=None,reviewer='T-AUD-001',note=''):
    claims.append({'id':cid,'subject_id':pid,'predicate':predicate,'object':value,
        'raw_text':None,'time':None,'place':None,'source_ids':sids,
        'source_locator':locator,'original_vs_derived':'see_source_type',
        'direct_vs_indirect':'direct_for_record_content_only',
        'corroboration':[],'contradictions':[],'reviewer':reviewer,
        'status':status,'proof_argument_path':'cycle_001.md','note':note})

claim('C-OBS-001','P-BARK-003','recorded_death_date','1942-11-15',['S-MIL-001','S-MIL-002'],
    'confirmed','строка57; строка времени гибели',note='Подтверждено содержание военных изображений, не родство с заказчиком. Документы одной части не независимы по происхождению.')
claim('C-OBS-002','P-BARK-003','recorded_birth_year','1904',['S-MIL-001'],
    'confirmed','строка57; графа года рождения',note='Не приписывать этот год извещению578.')
claim('C-OBS-003','P-BARK-003','recorded_rank_and_unit','сержант; командир отделения1034сп293сд',
    ['S-MIL-002'],'confirmed','шапка и первая рукописная строка',note='В списке потерь звание сокращено; изменение звания отдельно не исследовано.')
claim('C-OBS-004','P-BARK-003','recorded_spouse','P-BARK-004B',['S-MIL-001'],
    'supported','строка57; графа родственников',note='Имя в документе: Антонина Прокофьевна. Факт записи не доказывает очередность брака или материнство.')
rels.append({'id':'R-DOC-001','from_person':'P-BARK-003','to_person':'P-BARK-004B',
    'type':'recorded_spouse','claim_id':'C-OBS-004','status':'supported',
    'temporal_scope':'1942','export_to_verified':False,'reviewer':'T-AUD-001'})
claim('C-OBS-005','P-BARK-004A','recorded_sentence_date','1938-10-05',['S-ANT-001'],
    locator='поле осуждение1',note='Производный индекс; не дата исполнения приговора.')
claim('C-OBS-006','P-BARK-004A','recorded_sentence','ВМН',['S-ANT-001'],
    locator='поле приговор1',note='Не получен акт исполнения. Родственные поля отсутствуют.')
claim('C-REV-001','P-BARK-004A','exact_death_date','1938-10-05',['S-LEGACY-GED','S-ANT-001'],
    'hypothesis',note='Прежняя уверенность снята. Эта дата смерти не опровергнута, но имеющийся источник её не устанавливает.')
for cid,who,target in [('C-ID-001','P-BARK-003-MEM','P-BARK-003'),('C-ID-002','P-BARK-004-MEM','P-BARK-004A'),('C-ID-003','P-BARK-004A','P-BARK-004B')]:
    claim(cid,who,'same_person_as',target,['S-MEM-20261030','S-LEGACY-GED'],
        'hypothesis',note='Нет идентифицирующего документа; разное отчество супруги требует разрешения.')
claim('C-KIN-001','P-BARK-003','sibling_of','P-BARK-005',['S-LEGACY-MASTER'],
    'hypothesis',note='Алфавитное соседство и совпадение отчества не доказывают братство.')
claim('C-KIN-002','P-ABRO-002','marriage_in_1959','P-BARK-001',['S-LEGACY-GED'],
    'hypothesis',note='Нет доступного актового документа или датированного прямого подтверждения заказчика.')
claim('C-KIN-003','P-HIST-004','ancestor_of','P-ABRO-001',['S-LEGACY-GED','S-CAU-1853'],
    'hypothesis',note='Исторический двор не соединён с Николаем поколенной цепью.')
claim('C-CAU-001','P-HIST-004','published_household_1853',
    {'head':'Abrosim Petrovich','age':31,'sons':[{'name':'Petr','age':6},{'name':'Fyodor','age':4}]},
    ['S-CAU-1853'],'supported','GORELOE; печатнаяс.65',
    note='Самостоятельное историческое хозяйство. Родство с заказчиком и тождество с фигурой1873г. не установлены.')
claim('C-SEARCH-001','P-BARK-001','orphanage_identity','Компанейский детдом',
    ['S-MEM-20261030','S-KUZ-001','S-CHILD-2024'],'hypothesis',
    note='Подходящее учреждение по семейному рассказу и географии; целевая поимённая запись не обнаружена.')
for eid,cid,person,typ,dt in [('E-OBS-001','C-OBS-001','P-BARK-003','recorded_death','1942-11-15'),('E-OBS-002','C-OBS-005','P-BARK-004A','sentence','1938-10-05')]:
    events.append({'id':eid,'person_id':person,'type':typ,'claim_id':cid,'date':dt,
        'place':None,'status':next(c['status'] for c in claims if c['id']==cid),
        'note':'Дата зафиксированного события; не основание устанавливать родство.'})

tasks=[]
def task(tid,question,ids,priority,source,status='open',owner='orchestrator',next_action=None,blocker=None):
    tasks.append({'task_id':tid,'linked_people':ids,'precise_question':question,
        'priority':priority,'suggested_source':source,'owner':owner,'last_search':DATE,
        'status':status,'blocker':blocker,'follow_up':next_action,
        'checkpoint':'checkpoint.md'})
task('T-MIL-001','Что действительно читается в военных изображениях?', ['P-BARK-003','P-BARK-005'],1,'S-MIL-001/002/003','verified','military_scan','Анкеты призыва и семейные документы')
task('T-AUD-001','Какие ключевые связи и формулы подтверждения не обеспечены источниками?', ['P-BARK-003','P-BARK-004A'],1,'Локальный корпус','verified','critical_audit','Повторный аудит каждого нового ребра')
task('T-CAU-001','Дают ли указатели и свод1886 поколенные мосты?', ['P-DYAK-001','P-ABRO-001'],2,'S-CAU-1853/1873/1886-CAT','verified','caucasus_sources','Смотреть полные именные документы, не статистику')
task('T-ANT-001','Какая дата указана в карточке Антониды и какой хранитель дела?', ['P-BARK-004A'],1,'S-ANT-001; S-KNB-001','verified',next_action='Отдельно получить дело, RQ-001')
task('T-CHILD-001','Какие дела по детдомам цитируются с проверяемыми шифрами?', ['P-BARK-001','P-BARK-002'],1,'S-CHILD-2024; S-KUZ-001','verified',next_action='Поиск описей областного и районного архивов')
task('T-CHILD-002','Где сейчас книга воспитанников1936г., описанная Кузнецовой?', ['P-BARK-001','P-BARK-002'],1,'Описи архивов; правопреемник Компанейского детдома',next_action='Бесплатный поиск каталога/истории передачи; затем RQ-002')
task('T-CHILD-003','Что содержат ф.469 оп.2 д.88/320 и ф.132 оп.1 д.6?', ['P-BARK-001','P-BARK-002'],1,'Каталоги ГАКО и ГА Каркаралинского района',next_action='Найти описи и крайние даты; не обещать поимённых карточек')
task('T-ANT-002','Устанавливает ли дело Антониды мужа/детей и дату исполнения?', ['P-BARK-004A','P-BARK-004-MEM'],1,'Архивно-следственное и реабилитационное дело','needs_human',next_action='Проверить актуальный канал подачи и предложить отправку RQ-001',blocker='Отправка обращения/передача личных документов требуют отдельного разрешения; бесплатные каталоги искать можно')
task('T-KIN-001','Какие родители записаны в актовых записях целевых детей?', ['P-BARK-001','P-BARK-002'],1,'ЗАГС/РАГС, школьные или детдомовские анкеты',next_action='Установить каталог/доступ; персональные сведения хранить частно')
task('T-MIL-002','Есть ли общие родители или явное братство Михаила и Сергея?', ['P-BARK-003','P-BARK-005'],2,'Метрические книги Бузулук/Дмитриевка; личные офицерские дела',next_action='Проверить каталоги и доступные именные листы1899/1904')
task('T-MIL-003','Один ли человек в репрессионной карточке1936 и военных документах1942?', ['P-BARK-003'],1,'КП Коми, лагерная анкета, призывная карточка',next_action='Сверить место рождения, состав семьи, адреса; не объединять по ФИО/году')
task('T-MARR-001','Есть ли первичный акт брака1959?', ['P-BARK-001','P-ABRO-002'],2,'Актовая записьРАГС; именованное семейное свидетельство',next_action='Составить отдельный частный поисковый запрос без утверждения о согласовании')
task('T-CAU-002','Какие дворыАбросимовых в полном переводе1853 и списках1873?', ['P-HIST-004','P-ABRO-001'],2,'Полные таблицы и оригиналы; Национальный архив Грузии',next_action='Сверить печатнуюс.65 со сканом оригинала; каталогизировать1873')
task('T-CAU-003','Где первичные именные семейные листы1886 нужных селений?', ['P-DYAK-001','P-ABRO-001'],2,'Национальные архивыГрузии/Азербайджана',next_action='Найти точное дело, состав списка и порядок доступа')
task('T-ROST-001','Какая точная деревня и родители в записи рождения исходного поколения?', ['P-ABRO-002','P-DYAK-002','P-ABRO-001'],1,'Акт рождения, посемейные/переселенческие карточки',next_action='Каталогизировать ростовские фонды без переноса общеисторической миграции на семью')
task('T-DEME-001','Мария и Антонина — варианты одного воспоминания или разные персоны?', ['P-DEME-001A','P-DEME-001B'],2,'Оригинал семейного интервью; посемейный документ',next_action='Не придумывать второй брак или девять документальных братьев')
task('T-PRIV-001','Как безопасно обращаться с прежними данными потенциально живых людей?', ['P-BARK-001','P-ABRO-002'],1,'Старый публичный срез и правила новых экспортов',next_action='Новые публикации обезличивать; отдельное решение по старой публичной истории без её переписывания')
task('T-EXPORT-001','Импортируется ли будущий непустой проверенныйGEDCOM?', [],3,'Gramps или другое доступное генеалогическое ПО',next_action='Сначала документально подтвердить исходный мост; импорт пока не проверен')

queries=[
 ('T-ANT-001','"Баркалова" "Антонида" "Григорьевна"','web search','Получена индексная карточка; это не следственное дело'),
 ('T-ANT-001','site.gov.kz Карагандинской архив репрессированных запрос архивные дела полиция','web search','Найдена официальная страницаКНБ о компетенции; конкретное дело не локализовано'),
 ('T-ANT-001','"Баркалова Антонида Григорьевна" дети','web search','Родственный мост не получен; поисковая выдача ограничена'),
 ('T-ANT-001','"Баркалова" "Антонина" "БАМ"','web search','Первичного маршрутаБАМ для целевой семьи не получено; не сплошной архивный поиск'),
 ('T-CHILD-001','"Государственный архив Карагандинской" "469"','web search','Научная публикация с архивными ссылками'),
 ('T-CHILD-001','"Компанейский" "детский дом" архив','web search','ПубликацияКузнецовой; шифр книги1936 не указан'),
 ('T-ANT-001','https://ru.openlist.wiki/Баркалова_Антонида_Григорьевна_(1909)','direct web open','403Forbidden; использована отдельно помеченная локальная выгрузка'),
 ('T-CHILD-001','S-CHILD-2024: печатные страницы9,22–23','PDF local read and rendered page9','Уточнены областной/районный фонды; индивидуальных записей не получено')]
logs=[{'id':f'SR-C001-{i:03d}','task_id':tid,'exact_query':q,'resource':res,'date':DATE,
    'filters/time_span':None,'result_count':None,'result_refs':[],
    'negative_scope':'Only this query/page; not proof of absence','outcome':outcome,
    'next_action':'См.research_tasks.json'} for i,(tid,q,res,outcome) in enumerate(queries,1)]
for tid in ('T-MIL-001','T-AUD-001','T-CAU-001'):
    logs.append({'id':'SR-'+tid,'task_id':tid,'exact_query':'Действия перечислены в отчёте исполнителя',
        'resource':f'agent_reports/{tid}.md','date':DATE,'result_count':None,
        'result_refs':[f'agent_reports/{tid}.md'],'negative_scope':'Охват описан в отчёте',
        'next_action':'См.research_tasks.json'})
hypotheses=[{'id':f'H-C001-{i:03d}','claim_ids':cs,'status':'hypothesis','question':q,'next_task':t}
    for i,(cs,q,t) in enumerate([
        (['C-ID-001'],'Военнослужащий и отец из памяти — одно лицо?','T-KIN-001'),
        (['C-ID-002','C-ID-003'],'Кто мать из памяти и как соотносятся два отчества?','T-ANT-002'),
        (['C-REV-001'],'Какова дата исполнения приговора?','T-ANT-002'),
        (['C-KIN-001'],'Братья ли Сергей и Михаил?','T-MIL-002'),
        (['C-KIN-002'],'Каковы документальные данные брака1959?','T-MARR-001'),
        (['C-KIN-003'],'Есть ли поколенный мост от хозяйстваАбросима кНиколаю?','T-CAU-002')],1)]
for name,value in [('persons',people),('claims',claims),('relationships',rels),('events',events),('sources',sources),('research_tasks',tasks),('search_log',logs),('hypotheses',hypotheses)]:
    save(name+'.json',value)
decisions=[
 {'id':'D-C001-001','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-001','action':'quarantine_legacy_edges','count':26,'reason':'Безусловные связи не обеспечены доступными доказательствами; не объявляются ложными.','evidence':['agent_reports/T-AUD-001.md'],'reversible':True,'baseline':'e71e6af'},
 {'id':'D-C001-002','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-001','action':'qualify_military_observations','claims':['C-OBS-001','C-OBS-002','C-OBS-003','C-OBS-004'],'reason':'Два чтения изображений; семейная идентичность отдельно не доказана.','reversible':True},
 {'id':'D-C001-003','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-001','action':'separate_sentence_from_execution','claims':['C-REV-001','C-OBS-005'],'reason':'Дата приговора не заменяет акт исполнения.','reversible':True},
 {'id':'D-C001-004','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-001','action':'qualify_childrens_home_and_caucasus_searches','reason':'Публикация/индекс не заменяет именную архивную запись или мост поколений.','reversible':True}]
(R/'decisions.jsonl').write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in decisions),encoding='utf-8')
print(json.dumps({'persons':len(people),'claims':len(claims),'relationships':len(rels),
    'confirmed_kinship_edges':sum(r['status']=='confirmed' for r in rels),'tasks':len(tasks)},ensure_ascii=False))
