"""Append cycle 002 finding aids and a separate repression-index identity."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'research'
DATE='2026-10-30'
def read(name):return json.loads((R/(name+'.json')).read_text(encoding='utf-8'))
def save(name,value):(R/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
people,claims,events,sources,tasks,logs,hypotheses=[read(n) for n in ('persons','claims','events','sources','research_tasks','search_log','hypotheses')]
if any(s['id']=='S-C002-CHILD-2023' for s in sources):raise SystemExit('Cycle002 already recorded; update with a new decision.')

def source(sid,typ,url,locator,note,path=None,access='read',group=None):
    sources.append({'id':sid,'type':typ,'archive':None,'collection':None,'fond':None,
        'opis':None,'delo':None,'list_or_frame':locator,'record_id':None,
        'canonical_url':url,'access_date':DATE,
        'content_hash':hashlib.sha256((ROOT/path).read_bytes()).hexdigest() if path else None,
        'local_copy_if_allowed':path,'access_rights':'Read-only public source; new copies stay in ignored local_cache unless republication rights are established.',
        'access_result':access,'transcription_path':None,'notes':note,'independence_group':group})

source('S-C002-CHILD-2023','scholarly_publication','https://bulhistphaa.enu.kz/index.php/main/article/download/396/242/817',
    'печатные с.92–93,96–97; PDF7–8,11–12',
    'З.Г.Сактаганова,Д.Д.Шапагатова,2023, DOI10.32523/2616-7255-2023-143-2-86-107. PDFс.11–12 визуально сверены; архивные оригиналы не получены.',
    'research/local_cache/orphanages_2023.pdf',group='central-kz-orphanage-publications')
source('S-C002-GORECKY-1999','published_archivist_account','https://www.shahtinsklib.kz/files/userfiles/karlag/goreckiy_deti_karlaga_1.pdf',
    'одна газетная полоса; правая колонка; выходные данные внизу',
    'В.Горецкий, Дети Карлага. Азия Транзит,15–21.04.1999,с.5. Описание картотеки на1999г.; современный хранитель не установлен. Визуально проверено.',
    'research/local_cache/goreckiy_children_karlag.pdf')
source('S-C002-GAKO-OFFICIAL','official_organization_page','https://www.gov.kz/org/karaganda-madeniet/about/structure/organization/leadership/13558/1?lang=ru',
    'поля юридического адреса и контакта учреждения',
    'HTML получен прямым read-only запросом, web-open не открыл. Локально сохранена ограниченная выдержка; имена сотрудников исключены.',
    'research/local_cache/gako_official_C002.txt')
source('S-C002-KARK-OFFICIAL','official_organization_page','https://www.gov.kz/org/karaganda-madeniet/about/structure/organization/leadership/13707/1?lang=ru',
    'поля юридического адреса и контакта учреждения',
    'Официальная страница прочитана через HTML. Адрес учреждения не доказывает хранение целевого дела. Кэш — выдержка.',
    'research/local_cache/karkaraly_official_C002.txt')
source('S-C002-CENTER-OFFICIAL','official_directory','https://www.gov.kz/article/651?lang=ru',
    'Карагандинская область,строка5; дата обновления11.02.2026',
    'Название центра и адрес прочитаны; правопреемство Компанейского детдома/передача книг не следуют из адреса. Кэш — выдержка без персональных данных.',
    'research/local_cache/center_directory_excerpt_C002.txt')
source('S-C002-TSAFT-2012','local_history_account','https://vainahkrg.kz/e/3168928-iz-istorii-kompaneyskogo-detskogo-doma-im-n/',
    'абзац о переводе1998г.; обновление31.10.2012',
    'Краеведческий рассказ о переводе на Магнитогорскую3. Нет акта правопреемства или передачи архива. Комментарии с данными третьих лиц не собирались.')
source('S-C002-BKO-DIRECTORY','official_archive_directory','https://muragat-bko.gov.kz/ru/publikatsii-izdaniya/izdaniya/biblioteka/adresa-arhivnyh-uchrezhdenij-respubliki-kazahstan',
    'строки121,132 таблицы учреждений',
    'Справочник другого государственного архива. Для районного архива указан отличный адрес; дата актуальности строк не установлена. Предпочтение актуальной странице профильного управления.')
source('S-C002-EMEMORY-DIRECTORY','institution_directory','https://e-memory.kz/archive/karagandinskaya-oblast/',
    'таблица,строки1,10,21,22',
    'Доступна страница учреждений; это не каталог фондов. Полный URL старой персональной карточкиАнтониды на портале не раскрыл документ.')
source('S-C002-CAT-935','volunteer_finding_aid','https://nashipredki.com/archive/ogaoo-orenburg/fond-389/opis-1/delo-935',
    'Описание,год,число листов; ссылка Яндекс',
    'Каталожная карточка:1899,194л.,три села. Уезд/волость в заголовке отсутствуют. Запись оСергее не прочитана.')
source('S-C002-CAT-1463','volunteer_finding_aid','https://nashipredki.com/archive/ogaoo-orenburg/fond-389/opis-1/delo-1463',
    'Описание,год,число листов',
    'Городские книгиБузулука1904,237л. Подлинный заголовочный лист и записи не просмотрены.')
source('S-C002-CAT-OP3','volunteer_finding_aid','https://nashipredki.com/archive/ogaoo-orenburg/fond-389/opis-3',
    'дела17,28,56',
    'Отдельные городские тома1904г. Д.17/28 открывались исследователем как карточки; д.56 отмечено только в поисковой выдаче описи.')
source('S-C002-GE-CAT1','volunteer_finding_aid','https://inv.velikie.org/archive/ciag-gruziya/254/3-1/',
    '1873: буквенные группы д.111,118,119,123,189,191,202',
    'Открыты таблица и описания JSON. Наличие фамилии/села внутри тома не проверено; материалы выбранных карточек пусты.')
source('S-C002-GE-CAT2','volunteer_finding_aid','https://inv.velikie.org/archive/ciag-gruziya/254/3-1/page2.htm',
    '1886: буквенные группы Борчалинского и Ахалкалакского уездов',
    'Пометка копии относится к архивной единице, не к доступному онлайн-изображению. Опись3-1 не смешивается с описью1.')
source('S-C002-YA-ACCESS','observed_access_gate','https://ya.ru/archive/catalog/c6212baf-b01b-4009-b9df-c5c82bf57608',
    'перенаправление на главнуюya.ru/archive; текст требования входа',
    'Оркестратор подтвердил во встроенном браузере. Вход не выполнялся, сканы не просмотрены. Это предел конкретной сессии, не отсутствие метрической записи.',access='login_required')
source('S-C002-REP-COPY','index_transcription','https://ru.openlist.wiki/Баркалов_Михаил_Петрович_(1904)',
    'documents/openlist_target_pages.txt:250–269',
    'Повторно прочитана полная старая выгрузка; исходная дата получения/том/страницаКПКоми неизвестны. Новый прямой запрос403.',
    'documents/openlist_target_pages.txt',group='komi-memory-index')
source('S-C002-GE-ACCESS','unretrieved_official_page','https://www.archive.gov.ge/en/khelmisatsvdomoba-1',
    'прямое открытие403',
    'Поисковый индекс упоминает читальный зал и копирование; полный текст/актуальные тарифы не получены. Не считать это проверенными условиями услуги.',access='403')
source('S-C002-OG-ACCESS','unretrieved_official_page','https://archive.orb.ru/activity/10585/',
    'прямое открытие403',
    'Недоступна в web-инструменте. Полная проверка официального каталога не выполнена.',access='403')

rep='P-REC-1936-MIKHAIL'
people.append({'id':rep,'name':'Михаил Петрович Баркалов [репрессионная индексная запись]',
    'aliases':['CAND-T-MIL-003-REP-01'],'privacy':'public_historical_record_entity',
    'life_status':'unknown','status':'supported','origin':'separate_index_record',
    'source_ids':['S-C002-REP-COPY'],'kinship_to_client':'not_established',
    'note':'Не объединён с военной записьюP-BARK-003 или отцом из семейной памяти.'})
facts=[('BIRTH-YEAR','indexed_birth_year','1904'),('BIRTH-PLACE','indexed_birth_place','Самарская губ.'),
    ('ARREST','indexed_arrest_date','1936-04-06'),('SENTENCE','indexed_sentence_date','1936-09-10'),
    ('AUTHORITY','indexed_sentencing_authority','ОСО при НКВД СССР'),
    ('CHARGE','indexed_charge','КРТД'),('TERM','indexed_term','3 г. л/св.'),
    ('PLACE','indexed_place_of_detention','Воркута'),('ARRIVAL','indexed_arrival_date','1936-10-22'),
    ('RELEASE','indexed_release_date','1939-04-06')]
for suffix,predicate,value in facts:
    claims.append({'id':'C-C002-REP-'+suffix,'subject_id':rep,'predicate':predicate,
        'object':value,'raw_text':None,'source_ids':['S-C002-REP-COPY'],
        'source_locator':'старая выгрузка,строки250–269','original_vs_derived':'derived',
        'direct_vs_indirect':'direct_for_index_content_only','corroboration':[],
        'contradictions':[],'reviewer':'T-AUD-C002','status':'supported',
        'proof_argument_path':'cycle_002.md','note':'Содержание производной записи; первичное дело не получено.'})
    if suffix in ('ARREST','SENTENCE','ARRIVAL','RELEASE'):
        events.append({'id':'E-C002-REP-'+suffix,'person_id':rep,'type':predicate,
            'date':value,'place':None,'claim_id':'C-C002-REP-'+suffix,'status':'supported'})
claims.append({'id':'C-ID-C002-MIL-REP','subject_id':rep,'predicate':'same_person_as',
    'object':'P-BARK-003','raw_text':None,'source_ids':['S-C002-REP-COPY','S-MIL-001'],
    'original_vs_derived':'mixed','direct_vs_indirect':'indirect','status':'hypothesis',
    'reviewer':'T-AUD-C002','proof_argument_path':'cycle_002.md',
    'note':'ФИО/год совпадают, губерния совместима. Нет точного города/семейного/адресного признака для доказанного тождества.'})

institutions=[
 {'id':'A-KRG-REG','name':'Государственный архив Карагандинской области',
  'kind':'archive','published_address':'Караганда,ул.Ержанова,6',
  'source_ids':['S-C002-GAKO-OFFICIAL'],'access_date':DATE,'status':'supported',
  'notes':'Адрес на официальной странице; не свидетельство хранения определённого дела. Отличается от прежнего пакета запросов.'},
 {'id':'A-KRK-DIST','name':'Государственный архив Каркаралинского района',
  'kind':'archive','published_address':'Каркаралинск,ул.Ауэзова,19А',
  'source_ids':['S-C002-KARK-OFFICIAL','S-C002-BKO-DIRECTORY'],'access_date':DATE,'status':'supported',
  'alternative_published_addresses':[{'address':'Каркаралинск,ул.Ермекова,32','source_id':'S-C002-BKO-DIRECTORY','current':None}],
  'notes':'Приоритет официальной страницы профильного управления; перед отправкой проверить заново.'},
 {'id':'I-KOMP-HIST','name':'Компанейский детский дом','kind':'historical_childrens_home',
  'published_address':None,'source_ids':['S-C002-TSAFT-2012','S-KUZ-001'],
  'access_date':DATE,'status':'supported','notes':'Учреждение известно по публикациям; книги конкретных детей не обнаружены.'},
 {'id':'I-MAG3-CENTER','name':'Центр поддержки детей с особыми образовательными потребностями',
  'kind':'possible_institutional_successor','published_address':'Караганда,ул.Магнитогорская,3',
  'source_ids':['S-C002-CENTER-OFFICIAL','S-C002-TSAFT-2012'],'access_date':DATE,'status':'hypothesis',
  'notes':'Официальный список подтверждает учреждение по адресу; краеведческий текст сообщает о переводе тудаКомпанейского в1998. Юридическое преемство и передача архива не доказаны.'},
 {'id':'A-OGAO-O','name':'Объединённый государственный архив Оренбургской области','kind':'archive',
  'published_address':None,'source_ids':['S-C002-CAT-935','S-C002-CAT-1463'],
  'access_date':DATE,'status':'supported','notes':'Назван держателем в справочном каталоге; официальный каталог в этом цикле не открыт.'},
 {'id':'A-GE-HIST','name':'Центральный исторический архив Грузии / Национальный архив Грузии',
  'kind':'archive','published_address':None,'source_ids':['S-C002-GE-CAT1','S-C002-GE-CAT2'],
  'access_date':DATE,'status':'supported','notes':'Каталог с обозначениемЦИАГ-Грузия; оригиналы описанных дел не просмотрены.'}]
leads=[]
def lead(lid,archive,fond,opis,delo,title,year,sids,locus,task,reviewer=None,notes='',status='supported',leaf=None):
    leads.append({'id':lid,'archive_id':archive,'fond':str(fond),'opis':str(opis),
        'delo':delo,'list_or_frame':leaf,'title_as_described':title,
        'date_as_described':year,'source_ids':sids,'source_locator':locus,
        'access_date':DATE,'status':status,'reviewer':reviewer,'original_seen':False,
        'task_ids':[task],'notes':notes,'person_named_or_found':False})
lead('AL-C002-KRK-6','A-KRK-DIST',132,1,'6','Годовой отчёт о работе детского дома за1951г. — содержание цитируемого листа','1951',
 ['S-C002-CHILD-2023'],'печатнаяс.97/PDF12','T-CHILD-003','T-AUD-C002',
 'Не установлен полный заголовок или крайние даты дела; это не книга воспитанников1936г.',leaf='1;2–3')
lead('AL-C002-KRK-5','A-KRK-DIST',132,1,'5','Устройство детдома после переводаСаранского; опубликованный контекст','1948–1949 (контекст)',
 ['S-C002-CHILD-2023'],'печатнаяс.96/PDF11','T-CHILD-003','T-AUD-C002',
 'Л.85 относится к помещению; диапазон дела и преемство с лечебным детдомом1938 не установлены.',leaf='85;58;96')
lead('AL-C002-KRG-335','A-KRG-REG',469,2,'335','Материалы,цитируемые при историиКомпанейского детдома',None,
 ['S-C002-CHILD-2023'],'печатнаяс.92/PDF7','T-CHILD-003','T-AUD-C002',
 'Историческое повествование о1934г. не определяет дату самого дела.',leaf='51;55')
lead('AL-C002-KRG-1188-45','A-KRG-REG',1188,1,'45','Санитарная докладная и проверкаКомпанейского детдома',None,
 ['S-C002-CHILD-2023'],'печатнаяс.93/PDF8','T-CHILD-003','T-AUD-C002',
 'В публикации только относительный интервалпятьмесяцев; названиефонда и даты дела проверить.',leaf='26;30')
lead('AL-C002-KRG-7A','A-KRG-REG',469,2,'7а','Решение о переводеСаранского детдома вКаркаралинск','1948 (контекст)',
 ['S-C002-CHILD-2023'],'печатнаяс.96/PDF11','T-CHILD-003','T-AUD-C002',
 'Цитируется как решение20.08.1948; подлинник и полный диапазон дела не проверены.',leaf='40')
for lid,opis,delo,title,year,sid,nleaf,review in [
 ('935',1,'935','Метрики Димитриевки,Кандауровки,Курманаевки','1899','S-C002-CAT-935',194,'T-AUD-C002'),
 ('1463',1,'1463','ГородБузулук:Троицкий собор иАлександро-Невская церковь','1904','S-C002-CAT-1463',237,'T-AUD-C002'),
 ('3-17',3,'17','Бузулук:Троицкий собор','1904','S-C002-CAT-OP3',150,None),
 ('3-28',3,'28','Бузулук:Александро-Невская церковь','1904','S-C002-CAT-OP3',92,None),
 ('3-56',3,'56','Бузулук:Покровская церковь','1904','S-C002-CAT-OP3',38,None)]:
    lead('AL-C002-OG-'+lid,'A-OGAO-O',389,opis,delo,title,year,[sid],
        'каталожная карточка/опись','T-MIL-002',review,
        'Листы не просмотрены; число листов по справочнику. Для935 уезд не указан в заголовке.',
        'hypothesis' if lid=='3-56' else 'supported')
    leads[-1]['reported_total_leaves']=nleaf

groups1873=[('111','Тифлисский уезд,букваБ','Башкичет'),('118-119','Тифлисский уезд,букваК','Караклис'),
    ('123','Тифлисский уезд,букваО','Ормашени'),('189','Ахалкалакский уезд,букваГ','Горелое'),
    ('191','Ахалкалакский уезд,букваЕ','Ефремовка'),('202','Ахалкалакский уезд,букваТ','Троицкое')]
groups1886=[('1538-1541','Борчалинский уезд,букваБ','Башкичет'),('1551-1554','Борчалинский уезд,букваК','Караклис'),
    ('1559','Борчалинский уезд,букваО','Ормашени'),('1870-1871','Ахалкалакский уезд,букваГ','Горелое'),
    ('1874','Ахалкалакский уезд,букваЕ','Ефремовка'),('1892','Ахалкалакский уезд,букваТ','Троицкое')]
for year,groups,sid,taskid in [('1873',groups1873,'S-C002-GE-CAT1','T-CAU-002'),('1886',groups1886,'S-C002-GE-CAT2','T-CAU-003')]:
    for delo,title,village in groups:
        lead(f'AL-C002-GE-{year}-{delo}','A-GE-HIST',254,'3-1',delo,title,year,[sid],
            'групповой заголовок описи',taskid,
            'T-AUD-C002' if delo in ('189','1870-1871') else None,
            'Наличие села '+village+' внутри тома не подтверждено; это кандидат по уезду/букве. Сканы не получены.')
        leads[-1]['target_village_hypothesis']=village
        leads[-1]['digital_materials_observed']=False

taskby={t['task_id']:t for t in tasks}
for tid,follow in [('T-CHILD-002','Уточнить передачу книг; отдельно запросить справочныйаппарат картотеки1999г.'),
 ('T-CHILD-003','Уточнить крайние даты/описи, теперь с контекстомд.6=1951 и новыми ссылками1188/1/45.'),
 ('T-MIL-002','Открыть метрические листы найденных книг; сначала решить доступЯндекс или найти альтернативный архивный просмотр.'),
 ('T-MIL-003','Сверить репрессионную запись с первичной анкетой/точными местом и семьёй; совпадениеФИО недостаточно.'),
 ('T-CAU-002','Уточнить состав буквенных групп1873 и искать русские оригиналы.'),
 ('T-CAU-003','Уточнить состав буквенных групп1886; пометкакопии не означает цифровуюдоступность.')]:
    taskby[tid].update(last_search=DATE,status='open',last_cycle='002',last_cycle_result='inconclusive_for_target_records',follow_up=follow)
def task(tid,question,ids,priority,status,source,follow,blocker=None):
    tasks.append({'task_id':tid,'linked_people':ids,'precise_question':question,
        'priority':priority,'suggested_source':source,'owner':'orchestrator',
        'last_search':DATE,'status':status,'blocker':blocker,'follow_up':follow,'checkpoint':'checkpoint.md'})
task('T-CHILD-004','Были ли переданы книгиКомпанейского детдома центру наМагнитогорской3?',
 ['P-BARK-001','P-BARK-002'],1,'open','S-C002-CENTER-OFFICIAL;S-C002-TSAFT-2012',
 'Найти актперевода/передачи архива или справочныйкаталог, не выводить хранение поадресу.')
task('T-CARD-1999','Где и в каком составе сохранилась картотекаДетиКарлага?',
 ['P-BARK-001','P-BARK-002'],1,'open','S-C002-GORECKY-1999',
 'Открытый поиск сведений о картотеке; проектRQ-003 готов. Отправка отдельно согласуется.')
task('T-METRIC-SCANS-C002','Можно ли прочитать рождение кандидатов в найденных метрических книгах?',
 ['P-BARK-003','P-BARK-005'],1,'needs_human','S-C002-CAT-935;S-C002-CAT-1463;S-C002-YA-ACCESS',
 'Для путиЯндекс пользователь может войти в своюучётнуюзапись во встроенномбраузере. Альтернативный архивный просмотр искать независимо.',
 'Текущая браузернаясессия неавторизована; вход/созданиеаккаунта не выполнялись. Нет отрицательного результата поименам.')
task('T-AUD-C002','Проверены ли новые каталожныеориентиры и ограничения?',[],1,'verified','agent_reports/T-AUD-C002.md',
 'Независимо проверять каждый новый родственныйвывод; в этом цикле таких повышений нет.')
task('T-CAU-CATALOG-C002','Найдены ли конкретные группы дел1873/1886?',
 ['P-DYAK-001','P-ABRO-001'],2,'verified','S-C002-GE-CAT1;S-C002-GE-CAT2',
 'Этап поискакаталога выполнен; содержание селенныхлистов не проверено, T-CAU-002/003 остаютсяopen.')
hypotheses.append({'id':'H-C002-MIL-REP','claim_ids':['C-ID-C002-MIL-REP'],
    'status':'hypothesis','question':'Отождествляется ли репрессионная запись с военнослужащим?',
    'next_task':'T-MIL-003'})
queries=[
 ('T-CHILD-003','Государственный архив Карагандинской области каталог фондов 469 описи','web_search','Общедоступная опись не установлена; найдены публикации и официальные страницы учреждений.'),
 ('T-CHILD-003','Государственный архив Каркаралинского района фонд 132 детский дом опись','web_search','Найдена публикация2023; д.6 относится к отчёту1951г.'),
 ('T-CHILD-002','Компанейский детский дом Крупской архив книги воспитанников 1936 хранение','web_search','Современный хранитель книги1936г. не установлен.'),
 ('T-CHILD-004','"Магнитогорская, 3" "детский" Караганда','web_search','Официальный список и краеведческий адресныйслед; не актправопреемства.'),
 ('T-CARD-1999','"Компанейского" "архив" списки -site:collegy.ucoz.ru -site:vainahkrg.kz','web_search','Найдена газетная полоса1999г. о картотеке.'),
 ('T-METRIC-SCANS-C002','https://ya.ru/archive/catalog/c6212baf-b01b-4009-b9df-c5c82bf57608','in_app_browser','Переадресовано наya.ru/archive; явное требованиеавторизации, сканы непрочитаны.'),
 ('T-MIL-002','https://archive.orb.ru/activity/10585/','direct_web_open','403Forbidden; официальныйкаталог не прочитан.'),
 ('T-ANT-002','https://e-memory.kz/search/zhertvy-borby/?ID=15872/barkalova-antonida-grigorevna','direct_web_open','Страница недоступна черезweb; первичная карточка не получена.'),
 ('T-CHILD-003','Печатные страницы96–97/PDF11–12 orphanages_2023.pdf','pdf_text_and_render','Визуально уточнён контекст1948/1951; не просмотр архивныхдел.'),
 ('T-CARD-1999','Газетнаяполоса goreckiy_children_karlag.pdf','pdf_text_and_render','Проверены подпись/дата1999/описанныйохват; актуальнаясохранность не доказана.')]
for i,(tid,q,res,result) in enumerate(queries,1):
    logs.append({'id':f'SR-C002-{i:03d}','task_id':tid,'exact_query':q,'resource':res,
        'date':DATE,'filters/time_span':None,'result_count':None,'result_refs':['cycle_002.md'],
        'negative_scope':'Ограничен указанным запросом/страницей; не доказывает отсутствие человека или дела.',
        'outcome':result,'next_action':'См.research_tasks.json'})
for tid,path in [('T-MIL-003','T-MIL-003-C002.md'),('T-CAU-002','T-CAU-002-C002.md'),('T-AUD-C002','T-AUD-C002.md')]:
    logs.append({'id':'SR-C002-'+tid,'task_id':tid,'exact_query':'Действия и запросы подробно перечислены в отчёте',
        'resource':'agent_reports/'+path,'date':DATE,'result_count':None,
        'result_refs':['agent_reports/'+path],'negative_scope':'В пределах отчёта; сканы не прочитаны, если явно не указано иное.',
        'next_action':'См.research_tasks.json'})
for n,v in [('persons',people),('claims',claims),('events',events),('sources',sources),('research_tasks',tasks),('search_log',logs),('hypotheses',hypotheses),('institutions',institutions),('archive_leads',leads)]:save(n,v)
decisions=[{'id':'D-C002-001','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-C002',
 'action':'separate_repression_index_identity','claims':['C-ID-C002-MIL-REP'],
 'reason':'Старая карточка даёт лишь губернию/год/ФИО и даты репрессии; точных идентификаторов семьи нет.','reversible':True},
 {'id':'D-C002-002','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-C002',
 'action':'record_finding_aids_without_genealogical_promotion',
 'reason':'Каталоги метрик и буквенные группыГрузии не заменяют именные записи. Поздние документы детдома не доказывают преемства/раннихпробелов.','reversible':True},
 {'id':'D-C002-003','date':DATE,'actor':'orchestrator','reviewer':'T-AUD-C002',
 'action':'prepare_card_index_preservation_inquiry',
 'reason':'Публикация1999г. даёт след картотеки, а не подтверждение её современной сохранности/включения целевыхлиц. Запрос не отправлен.','reversible':True}]
with (R/'decisions.jsonl').open('a',encoding='utf-8') as f:
    for d in decisions:f.write(json.dumps(d,ensure_ascii=False)+'\n')
print(json.dumps({'persons':len(people),'claims':len(claims),'events':len(events),
    'sources':len(sources),'tasks':len(tasks),'institutions':len(institutions),'archive_leads':len(leads)}))
