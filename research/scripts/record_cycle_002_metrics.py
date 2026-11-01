"""Record the post-login metric findings once; preserve adult identities separately."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'research'
DATE = '2026-10-30'
names = ['persons', 'claims', 'relationships', 'events', 'sources',
         'research_tasks', 'search_log', 'hypotheses', 'archive_leads']
data = {n: json.loads((R / (n + '.json')).read_text(encoding='utf-8')) for n in names}
if any(p['id'] == 'P-MET-1899-SERGEY' for p in data['persons']):
    raise SystemExit('Metric records already recorded; do not rerun.')
review = 'T-AUD-C002'
proof = 'biographies/metric_family_1899_1904.md'
s99, s04 = 'S-C002-MET-1899-49', 'S-C002-MET-1904-17'
book99 = 'https://ya.ru/archive/catalog/c6212baf-b01b-4009-b9df-c5c82bf57608'
book04 = 'https://ya.ru/archive/catalog/0b2dee57-8c04-477f-8c1d-6b389bfad041'

def source(sid, url, delo, locus, record, path, notes):
    data['sources'].append({
        'id': sid, 'type': 'copy_primary_document',
        'archive': 'ОГАОО', 'collection': 'Самарская духовная консистория',
        'fond': '389', 'opis': '1', 'delo': delo, 'list_or_frame': locus,
        'record_id': record, 'canonical_url': url, 'access_date': DATE,
        'content_hash': None, 'local_copy_if_allowed': None,
        'access_rights': 'Viewed through the user-authorized archive viewer; scan not republished.',
        'access_result': 'image_visually_read', 'transcription_path': path,
        'transcription_hash': hashlib.sha256((R/path).read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
        'hash_scope': 'UTF-8 transcription with LF line endings; no local scan image or image hash',
        'reviewer': review if record else None, 'notes': notes,
        'independence_group': 'OGAO-389-1-' + delo})

source('S-C002-MET-935-COVER', book99 + '/1', '935', 'скан 1, обложка', None,
       'transcriptions/OGAO_389_1_935_cover.md',
       'Обложка: Бузулукский уезд, 1899, три села, 188 листов. Сервис показывает 194 скана; это разные единицы.')
source(s99, book99 + '/20', '935', 'рукописная пагинация 19; скан 20/194', 'мужская запись 49',
       'transcriptions/OGAO_389_1_935_record49.md',
       'Оригинальное изображение независимо прочитано оркестратором и аудитором. Даты как записаны, без календарной конверсии.')
source(s04, book04 + '/8', '1466', 'рукописная пагинация 7; скан 8/133', 'мужская запись 17',
       'transcriptions/OGAO_389_1_1466_record17.md',
       'Год визуально читается 1904 с умеренно высокой уверенностью и совпадает с каталогом; OCR 1901 отвергнут. Фамилия Боркалов сохранена.')
source('S-C002-MET-1466-COVER', book04 + '/1', '1466', 'скан 1, обложка', None,
       'transcriptions/OGAO_389_1_1466_cover.md',
       'Дополнительное чтение обложки подтвердило Бузулукский уезд, Димитриевку, Кандауровку и год 1904.')

for pid, name, aliases, sids, note in [
    ('P-MET-1899-SERGEY', 'Сергий [метрическая запись 1899]', ['Сергій'], [s99],
     'Отчество Петрович выводится из записи отца; не отождествлён с военным P-BARK-005.'),
    ('P-MET-1904-MIKHAIL', 'Михаил [метрическая запись 1904]', ['Михаилъ'], [s04],
     'Не отождествлён с военным P-BARK-003 или репрессионным P-REC-1936-MIKHAIL.'),
    ('P-MET-PETR-PROKHOROV', 'Пётр Прохоров Баркалов / Боркалов [метрическая пара]',
     ['Петръ Прохоровъ Баркаловъ', 'Петр Прохоров Боркалов'], [s99, s04],
     'Группировка двух записей как одной родительской пары — supported, косвенный вывод. Дед Прохор не создан по одному отчеству.'),
    ('P-MET-EVGENIA-FEODOROVA', 'Евгения Феодорова [метрическая пара]',
     ['Евгенія Ѳеодорова'], [s99, s04],
     'Девичья фамилия неизвестна. Группировка двух материнских записей — supported, косвенный вывод.')]:
    data['persons'].append({'id': pid, 'name': name, 'aliases': aliases,
        'privacy': 'public_historical_record_entity', 'life_status': 'deceased_historical',
        'status': 'supported', 'origin': 'metric_record_entity', 'source_ids': sids,
        'kinship_to_client': 'not_established', 'note': note})

def claim(cid, subject, predicate, obj, sids, status='supported', note='', indirect=False, raw=None, time=None):
    row = {'id': cid, 'subject_id': subject, 'predicate': predicate, 'object': obj,
           'raw_text': raw, 'time': time, 'place': 'Димитриевка (село родителей/приход)',
           'source_ids': sids, 'original_vs_derived': 'copy_of_primary',
           'direct_vs_indirect': 'indirect' if indirect else 'direct_for_record_content',
           'corroboration': [], 'contradictions': [], 'reviewer': review,
           'status': status, 'proof_argument_path': proof, 'note': note}
    data['claims'].append(row)
    return row

for child, suffix, sid, birth, baptism, rawname in [
    ('P-MET-1899-SERGEY', '99', s99, '1899-09-06', '1899-09-07', 'Сергій'),
    ('P-MET-1904-MIKHAIL', '04', s04, '1904-03-14', '1904-03-15', 'Михаилъ')]:
    claim('C-MET-' + suffix + '-NAME', child, 'recorded_given_name', rawname, [sid], raw=rawname)
    for predicate, value in [('birth_date_as_written', birth), ('baptism_date_as_written', baptism)]:
        cid = 'C-MET-' + suffix + '-' + predicate
        claim(cid, child, predicate, value, [sid],
              note='Дата как в документе. ISO-форма не означает перевод в григорианский календарь.', time=value)
        data['events'].append({'id': 'E-MET-' + suffix + '-' + predicate,
            'person_id': child, 'type': predicate, 'date': value,
            'calendar': 'as_written_not_converted', 'place': None,
            'claim_id': cid, 'status': 'supported'})
    for parent, label in [('P-MET-PETR-PROKHOROV', 'FATHER'), ('P-MET-EVGENIA-FEODOROVA', 'MOTHER')]:
        cid = 'C-MET-' + suffix + '-' + label
        claim(cid, parent, 'parent', child, [sid],
              note='Родитель прямо назван в акте; общность пары между актами — отдельно оговорённый supported-вывод.')
        data['relationships'].append({'id': 'R-MET-' + suffix + '-' + label,
            'from_person': parent, 'to_person': child, 'type': 'parent',
            'temporal_scope': birth[:4], 'claim_id': cid, 'status': 'supported',
            'export_to_verified': False, 'reviewer': review})

claim('C-MET-PAIR-SPOUSE', 'P-MET-PETR-PROKHOROV', 'recorded_spouse',
      'P-MET-EVGENIA-FEODOROVA', [s99, s04], raw='и законная жена его',
      note='Акты называют законную жену, но дату и место венчания не устанавливают.')
data['relationships'].append({'id': 'R-MET-PAIR-SPOUSE', 'from_person': 'P-MET-PETR-PROKHOROV',
    'to_person': 'P-MET-EVGENIA-FEODOROVA', 'type': 'recorded_spouse',
    'temporal_scope': '1899; 1904', 'claim_id': 'C-MET-PAIR-SPOUSE',
    'status': 'supported', 'export_to_verified': False, 'reviewer': review})
claim('C-MET-PAIR-GROUPING', 'P-MET-PETR-PROKHOROV', 'same_recorded_parent_pair_across_acts',
      'Димитриевка: 1899 №49 и 1904 №17', [s99, s04], indirect=True,
      note='Совпадают имя и отчество обоих родителей, село, конфессия; фамилия Баркалов/Боркалов. Общность пары сильно поддержана, но не confirmed.')
for suffix, child, adult, sid, militarysource, taskid, note in [
    ('SERGEY', 'P-MET-1899-SERGEY', 'P-BARK-005', s99, 'S-MIL-003', 'T-MET-ID-SERGEY',
     'Совпадают имя, ожидаемое отчество, год и село; военные документы не дали дня рождения или родителей.'),
    ('MIKHAIL', 'P-MET-1904-MIKHAIL', 'P-BARK-003', s04, 'S-MIL-001', 'T-MET-ID-MIKHAIL',
     'Совместимы имя, ожидаемое отчество и год; военное место рождения город Бузулук расходится с селом родителей/приходом Димитриевка.')]:
    cid = 'C-ID-MET-' + suffix
    identity_claim = claim(cid, child, 'same_person_as', adult, [sid, militarysource], 'hypothesis', note, True)
    identity_claim['export_to_verified'] = False
    data['hypotheses'].append({'id': 'H-ID-MET-' + suffix, 'claim_ids': [cid],
        'status': 'hypothesis', 'question': 'Тождественны ли метрический ребёнок и военный кандидат?', 'next_task': taskid})

taskby = {t['task_id']: t for t in data['research_tasks']}
taskby['T-METRIC-SCANS-C002'].update(status='verified', blocker=None,
    last_cycle_result='Ключевые записи 1899 №49 и 1904 №17 прочитаны после входа пользователя и независимо проверены.',
    follow_up='Этап доступа и чтения выполнен. Идентификации взрослых вынесены в T-MET-ID-SERGEY / MIKHAIL; общий поиск не исчерпан.')
taskby['T-MIL-002'].update(status='open', blocker=None,
    follow_up='Сопоставить метрических детей со взрослыми кандидатами; сохранить расхождение города Бузулук и Димитриевки.')
taskby['T-AUD-C002']['follow_up'] = 'Оригиналы метрик независимо прочитаны. Сверить интеграцию supported-связей и запрет отождествления со взрослыми без мостика.'
for tid, ids, question, priority, suggested, follow in [
    ('T-MET-ID-SERGEY', ['P-MET-1899-SERGEY', 'P-BARK-005'],
     'Совпадает ли метрический Сергий с военным Сергеем Петровичем 1899 г.?', 1,
     'Военные анкеты, документы об образовании и семейные записи с точной датой/родителями',
     'Проверка опубликованной УПК и ещё трёх военных серий не дала дня/родителей. Найти независимый семейный идентификатор.'),
    ('T-MET-ID-MIKHAIL', ['P-MET-1904-MIKHAIL', 'P-BARK-003', 'P-REC-1936-MIKHAIL'],
     'Совпадает ли метрический Михаил с военным и репрессированным кандидатами?', 1,
     'Военная или репрессионная анкета с точной датой, семьёй и местом рождения',
     'Проверить город Бузулук против села родителей Димитриевка; не выбирать удобное объяснение без документа.'),
    ('T-MET-PARENTS-MARRIAGE', ['P-MET-PETR-PROKHOROV', 'P-MET-EVGENIA-FEODOROVA'],
     'Когда венчались Пётр Прохоров Баркалов/Боркалов и Евгения Феодорова, каково её происхождение?', 2,
     'Браки Дмитриевского прихода до сентября 1899 г.; приходские и посемейные списки',
     'Начать с соседних предшествующих книг. Установить девичью фамилию и возраст; не выводить их из отчеств.'),
    ('T-MET-SIBLINGS', ['P-MET-1899-SERGEY', 'P-MET-1904-MIKHAIL'],
     'Какие ещё дети прямо названы у этой родительской пары?', 2,
     'Метрические рождения и смерти Димитриевки, варианты Баркалов/Боркалов и имена родителей',
     'Искать состав семьи, не отождествлять его с рассказом о братьях и сёстрах в Ленинграде без миграционного мостика.')]:
    data['research_tasks'].append({'task_id': tid, 'linked_people': ids, 'precise_question': question,
        'priority': priority, 'suggested_source': suggested, 'owner': 'orchestrator',
        'last_search': DATE, 'status': 'open', 'blocker': None, 'follow_up': follow, 'checkpoint': 'checkpoint.md'})

gate = next(s for s in data['sources'] if s['id'] == 'S-C002-YA-ACCESS')
gate['resolution'] = {'date': DATE, 'result': 'resolved_after_user_login',
    'notes': 'Пользователь вошёл самостоятельно. Последующее чтение оформлено отдельными первичными источниками; прежняя запись фиксирует только раннюю преграду.'}
for lead in data['archive_leads']:
    if lead['id'] == 'AL-C002-OG-935':
        lead.update(original_seen=True, person_named_or_found=True,
            source_ids=lead['source_ids'] + ['S-C002-MET-935-COVER', s99],
            list_or_frame='обложка; рукописная пагинация 19, №49, скан 20',
            notes='Прочитаны обложка и запись №49, не вся книга. Бузулукский уезд подтверждён обложкой; 188 листов на ней, 194 скана в сервисе.',
            reported_total_leaves=None, cover_reported_leaves=188, viewer_total_scans=194)
    elif lead['id'] == 'AL-C002-OG-1463':
        lead['notes'] = 'Выполнен поиск OCR и просмотр найденной строки: взрослый Михаил Васильев — восприемник, не искомый младенец. Сплошной просмотр книги не выполнен.'
data['archive_leads'].append({'id': 'AL-C002-OG-1466', 'archive_id': 'A-OGAO-O',
    'fond': '389', 'opis': '1', 'delo': '1466', 'list_or_frame': 'рукописная пагинация 7, №17, скан 8/133',
    'title_as_described': 'Метрики Димитриевки и Кандауровки', 'date_as_described': '1904',
    'source_ids': [s04, 'S-C002-MET-1466-COVER'], 'source_locator': 'заголовок сервиса и изображение листа',
    'access_date': DATE, 'status': 'supported', 'reviewer': review, 'original_seen': True,
    'person_named_or_found': True, 'task_ids': ['T-MIL-002', 'T-MET-ID-MIKHAIL'],
    'notes': 'Прочитана запись №17, не вся книга. Год 1904 визуально/каталог; OCR 1901 сохранён как отвергнутое разночтение.'})

queries = [
    ('935-NAME', book99, 'Баркалов', 3, 'Найдены сканы 20, 6, 9. Целевая родительская пара — скан 20; остальные попадания не импортированы как родственники.'),
    ('1463-NAME', 'https://ya.ru/archive/catalog/14711b52-8e13-4ae9-98c1-414941290783', 'Баркалов', 1,
     'Точный и затем похожий поиск показали скан 178: взрослый Михаил Васильев — восприемник.'),
    ('1463-FATHER', 'https://ya.ru/archive/catalog/14711b52-8e13-4ae9-98c1-414941290783', 'Петр Прохоров', 2,
     'Два попадания отдельных слов на странице не дали целевой семьи.'),
    ('1466-NAME', book04, 'Баркалов', 7,
     'Поиск одной фамилии не вывел целевую строку с OCR Боркалов; отрицательный поиск не доказывает отсутствия.'),
    ('1466-FATHER', book04, 'Петр Прохоров Баркалов', 1,
     'Скан 8: Михаил, №17, визуальное чтение родительской пары и дат независимо проверено.')]
for suffix, url, query, count, outcome in queries:
    data['search_log'].append({'id': 'SR-C002-MET-' + suffix, 'task_id': 'T-METRIC-SCANS-C002',
        'exact_query': query, 'resource': url, 'date': DATE,
        'filters/time_span': 'Поиск внутри указанной книги; это число OCR-попаданий, не актов о человеке.',
        'result_count': count, 'result_refs': [proof, 'agent_reports/T-AUD-C002.md'],
        'negative_scope': 'Не сплошной ручной просмотр. Ошибки OCR и варианты фамилии оставляют риск пропусков.',
        'outcome': outcome, 'next_action': 'Идентификация взрослых и поиск брака родителей по отдельным задачам.'})
data['search_log'].append({'id': 'SR-C002-MET-SERGEY-MIL', 'task_id': 'T-MET-ID-SERGEY',
    'exact_query': 'Точные запросы и открытые военные записи перечислены в отчёте агента',
    'resource': 'agent_reports/T-SERGEY-METRIC-C002.md', 'date': DATE,
    'result_count': None, 'result_refs': ['agent_reports/T-SERGEY-METRIC-C002.md'],
    'negative_scope': 'Проверенные опубликованные УПК, донесение, госпитальный и наградной документы; не весь архивный комплекс.',
    'outcome': 'Год и село согласуются; день рождения/родители не найдены. Тождество остаётся hypothesis.',
    'next_action': 'Независимый документ с точной датой или семейными признаками.'})

# Restore the actual query spelling recorded during the earlier part of this cycle.
exact = [
    'Государственный архив Карагандинской области каталог фондов 469 описи',
    'Государственный архив Каркаралинского района фонд 132 детский дом опись',
    'Компанейский детский дом Крупской архив книги воспитанников 1936 хранение',
    '"Магнитогорская, 3" "детский" Караганда',
    '"Компанейского" "архив" списки -site:collegy.ucoz.ru -site:vainahkrg.kz']
for i, query in enumerate(exact, 1):
    next(row for row in data['search_log'] if row['id'] == f'SR-C002-{i:03d}')['exact_query'] = query

for name, rows in data.items():
    (R / (name + '.json')).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
with (R / 'decisions.jsonl').open('a', encoding='utf-8') as f:
    f.write(json.dumps({'id': 'D-C002-004', 'date': DATE, 'actor': 'orchestrator', 'reviewer': review,
        'action': 'record_independently_read_metric_family_separate_from_adult_candidates',
        'claims': ['C-MET-PAIR-GROUPING', 'C-ID-MET-SERGEY', 'C-ID-MET-MIKHAIL'],
        'reason': 'Родители прямо названы в двух актах. Общность пары supported; взрослые тождества hypothesis. Фамилия а/о и год OCR/изображения сохранены. Клиентский GEDCOM не расширен.',
        'reversible': True}, ensure_ascii=False) + '\n')
print(json.dumps({n: len(rows) for n, rows in data.items()}, ensure_ascii=False))
