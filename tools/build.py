# -*- coding: utf-8 -*-
"""Собирает все страницы сайта Capital Defence из общего шаблона.
Запуск: python3 -I build.py /home/user/judgesite
Статьи берутся из старых HTML (папка materialy) и переводятся в семантическую разметку.
"""
import os, re, sys, json, html

ROOT = sys.argv[1]
SITE = 'https://capitaldefence.ru'
PHONE = '+7 (953) 023‑68‑03'
PHONE_TEL = '+79530236803'
TG = 'https://t.me/Capital_Defence'
MAP = 'https://yandex.ru/maps/?text=%D0%9F%D0%B5%D0%BD%D0%B7%D0%B0%2C%20%D0%BF%D1%80%D0%BE%D1%81%D0%BF%D0%B5%D0%BA%D1%82%20%D0%9F%D0%BE%D0%B1%D0%B5%D0%B4%D1%8B%2C%2097'
ADDR = 'Пенза, просп. Победы, 97'
HOURS = 'Пн–Сб, 10:00–22:00'

ICON = {
 'phone': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
 'send': '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
 'radio': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>',
 'ext': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
}

def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + '\n</script>'

def breadcrumb_ld(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(items)]}

ORG = {"@type":"LegalService","name":"Capital Defence","alternateName":"Финансовая защита","url":SITE+"/",
       "telephone":PHONE_TEL,"address":{"@type":"PostalAddress","streetAddress":"просп. Победы, 97","addressLocality":"Пенза","addressCountry":"RU"}}

def shell(*, root, path, title, description, body, active=None, ld=None, og_type='website', crumbs=None):
    """root: '' или '../'; path: канонический путь вида '/advokaty/'."""
    ld = list(ld or [])
    if crumbs:
        ld.append(breadcrumb_ld(crumbs))
    ld_html = '\n'.join(jsonld(x) for x in ld)
    def cur(key):
        return ' aria-current="page"' if key == active else ''
    nav_items = [('uslugi', root + 'uslugi/', 'Услуги'), ('advokaty', root + 'advokaty/', 'Адвокаты'),
                 ('yuristy', root + 'yuristy/', 'Юристы'), ('materialy', root + 'materialy/', 'Материалы'),
                 ('contact', root + '#contact', 'Контакты')]
    nav = '\n      '.join(f'<a href="{h}"{cur(k)}>{t}</a>' for k, h, t in nav_items)
    mnav = '\n      '.join(f'<a href="{h}"{cur(k)}>{t}</a>' for k, h, t in [('home', root or './', 'Главная')] + nav_items)
    crumb_html = ''
    if crumbs:
        parts = []
        for i, (n, u) in enumerate(crumbs):
            if i == len(crumbs) - 1:
                parts.append(f'<span class="current">{n}</span>')
            else:
                parts.append(f'<a href="{root + u.lstrip("/") if u != "/" else (root or "./")}">{n}</a>')
        crumb_html = f'<div class="crumbs"><nav class="wrap breadcrumb" aria-label="Хлебные крошки">' + '<span class="sep">/</span>'.join(parts) + '</nav></div>\n'
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Capital Defence">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F7F6F2">
<link rel="icon" href="{root}favicon.ico" sizes="32x32">
<link rel="icon" href="{root}assets/img/favicon-32.png" type="image/png">
<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-icon.png">
<link rel="stylesheet" href="{root}assets/style.css">
<script src="{root}assets/site.js" defer></script>
{ld_html}
</head>
<body>
<a class="skip" href="#main">К содержанию</a>

<header class="site-header" id="top">
  <div class="header-inner">
    <a class="brand" href="{root or './'}" aria-label="Capital Defence, на главную">
      <img src="{root}assets/img/emblem-96.jpg" alt="" width="42" height="42">
      <span><span class="brand-name">Capital Defence</span><span class="brand-sub">Финансовая защита · Пенза</span></span>
    </a>
    <nav class="nav" aria-label="Основная навигация">
      {nav}
    </nav>
    <div class="header-actions">
      <a class="header-phone" href="tel:{PHONE_TEL}">{PHONE}</a>
      <a class="btn btn-sm" href="{root}#contact">Консультация</a>
      <button class="menu-btn" type="button" aria-label="Меню" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobileMenu">
  <nav aria-label="Мобильная навигация">
      {mnav}
  </nav>
  <div class="mobile-contacts">
    <a class="btn" href="tel:{PHONE_TEL}">Позвонить {PHONE}</a>
    <a class="btn btn-ghost" href="{TG}" target="_blank" rel="noopener">Написать в Telegram</a>
  </div>
  <p class="mobile-meta">{ADDR}<br>{HOURS}</p>
</div>

{crumb_html}<main id="main">
{body}
</main>

<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{root or './'}">
          <img src="{root}assets/img/emblem-96.jpg" alt="" width="40" height="40">
          <span><span class="brand-name">Capital Defence</span><span class="brand-sub">Финансовая защита</span></span>
        </a>
        <p class="footer-addr">Юридическое агентство в Пензе<br>{ADDR}<br>{HOURS}</p>
      </div>
      <div>
        <h4>Разделы</h4>
        <ul>
          <li><a href="{root}uslugi/">Услуги</a></li>
          <li><a href="{root}advokaty/">Адвокаты</a></li>
          <li><a href="{root}yuristy/">Юристы</a></li>
          <li><a href="{root}materialy/">Материалы</a></li>
        </ul>
      </div>
      <div>
        <h4>Документы</h4>
        <ul>
          <li><a href="{root}dokumenty/politika-obrabotki-pd.html">Политика обработки персональных данных</a></li>
          <li><a href="{root}dokumenty/polozhenie-o-pd.html">Положение о защите персональных данных</a></li>
          <li><a href="{root}dokumenty/soglasie-na-obrabotku-pd.html">Согласие на обработку персональных данных</a></li>
        </ul>
      </div>
      <div>
        <h4>Контакты</h4>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
          <li><a href="{TG}" target="_blank" rel="noopener">Telegram: @Capital_Defence</a></li>
          <li><a href="{MAP}" target="_blank" rel="noopener">Открыть на Яндекс Картах</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Capital Defence · Финансовая защита</span>
      <span>Юридические услуги, Пенза</span>
    </div>
  </div>
</footer>

</body>
</html>
'''

def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print('wrote', rel)

def contact_list(items):
    """items: list of (icon, label, value, href, external)"""
    out = ['<ul class="contact-list">']
    for icon, k, v, href, ext in items:
        extra = ' target="_blank" rel="noopener"' if ext else ''
        out.append(f'  <li><a href="{href}"{extra}>{ICON[icon]}<span><span class="k">{k}</span><span class="v">{v}</span></span></a></li>')
    out.append('</ul>')
    return '\n'.join(out)

# ---------------------------------------------------------------------------
# Люди
# ---------------------------------------------------------------------------
PEOPLE = {
 'simkin': dict(name='Ярослав Симкин', role='Адвокат, налоговый консультант, медиатор', img='simkin.jpg', url='/advokaty/simkin.html',
                short='Экономические дела, банковское и налоговое право, медиация с ФНС.'),
 'chinokalov': dict(name='Максим Чинокалов', role='Адвокат по уголовным делам', img='chinokalov.jpg', url='/advokaty/chinokalov.html',
                short='15 лет в уголовном процессе, 10 из них — в Следственном комитете. Экономические, должностные и коррупционные дела.'),
 'truevtsev': dict(name='Михаил Труевцев', role='Адвокат по уголовным, административным и гражданским делам', img=None, initials='МТ', url='/advokaty/truevtsev.html',
                short='15 лет в Следственном комитете, более 5 лет адвокатской практики.'),
 'bakoyan': dict(name='Эдгар Бакоян', role='Юрист, налоговый консультант', img=None, initials='ЭБ', url='/yuristy/bakoyan.html',
                short='НДС, налоговые споры, блокировки счетов по 115-ФЗ.'),
 'shitov': dict(name='Иван Шитов', role='Ведущий юрист', img='shitov.jpg', url='/yuristy/shitov.html',
                short='Судебная практика, юридический аутсорсинг для бизнеса, 44-ФЗ/РНП, комплаенс.'),
}

def portrait(root, key, w=600, h=800, lazy=True):
    p = PEOPLE[key]
    if p['img']:
        return f'<div class="portrait"><img src="{root}assets/img/{p["img"]}" alt="{p["name"]}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else ""}></div>'
    return f'<div class="portrait"><div class="monogram" aria-label="{p["name"]}">{p["initials"]}</div></div>'

def person_card(root, key, desc=False, more=False):
    p = PEOPLE[key]
    d = f'\n    <p class="person-desc">{p["short"]}</p>' if desc else ''
    m = '\n    <span class="person-more">Профиль</span>' if more else ''
    return f'''  <a class="person" href="{root}{p["url"].lstrip("/")}">
    {portrait(root, key)}
    <p class="person-name">{p["name"]}</p>
    <p class="person-role">{p["role"]}</p>{d}{m}
  </a>'''

# ---------------------------------------------------------------------------
# Статьи: метаданные
# ---------------------------------------------------------------------------
ARTICLES = [
 dict(slug='chinokalov-doverie-i-tayna', author='chinokalov', type='Колонка', topic='Уголовная защита',
      h1='О доверии к адвокату и адвокатской тайне', title='О доверии к адвокату и адвокатской тайне — Максим Чинокалов',
      desc='Почему доверие клиента к адвокату и адвокатская тайна — не формальность, а инструмент защиты. Колонка адвоката Максима Чинокалова.',
      cta='Нужна консультация по уголовному делу?'),
 dict(slug='chinokalov-obysk-chast-1', author='chinokalov', type='Колонка', topic='Уголовная защита, обыск, часть 1 из 2',
      h1='Обыск. Часть 1 — незваные гости', title='Обыск. Часть 1 — незваные гости — Максим Чинокалов',
      desc='Почему обыск начинается в шесть утра, зачем на нём нужен адвокат и как следствие получает показания до его прихода. Колонка Максима Чинокалова.',
      cta='Нужна консультация по уголовному делу?'),
 dict(slug='chinokalov-obysk-chto-delat', author='chinokalov', type='Инструкция', topic='Уголовная защита, обыск, часть 2 из 2',
      h1='К вам пришли с обыском. Что делать?', title='К вам пришли с обыском. Что делать? — Максим Чинокалов',
      desc='Пошаговая инструкция адвоката: что делать до того, как открыли дверь, во время обыска, при подписании протокола и после. Максим Чинокалов.',
      cta='Обыск уже начался или ожидаете его?', urgent=True),
 dict(slug='chinokalov-zaderzhanie-chto-delat', author='chinokalov', type='Инструкция', topic='Уголовная защита',
      h1='Вас задержали. Что делать?', title='Вас задержали. Что делать? — Максим Чинокалов',
      desc='Правила поведения при задержании: как не навредить себе показаниями, что требовать и что говорить до прихода адвоката. Максим Чинокалов.',
      cta='Задержали вас или близкого человека?', urgent=True),
 dict(slug='chinokalov-ii-ne-zamena-advokatu', author='chinokalov', type='Колонка', topic='Уголовная защита',
      h1='Заменит ли ИИ адвоката?', title='Заменит ли ИИ адвоката? — Максим Чинокалов',
      desc='Чем нейросети реально помогают в юридических вопросах, а где доверие к ним опасно для защиты по уголовному делу. Колонка Максима Чинокалова.',
      cta='Есть похожая ситуация?'),
 dict(slug='bakoyan-bmw-nds-delo', author='bakoyan', type='Разбор практики', topic='Налоги, НДС',
      h1='Схема с НДС при продаже автомобиля: дело BMW X5', title='Схема с НДС при продаже автомобиля: дело BMW X5 — Эдгар Бакоян',
      desc='Разбор судебного дела о занижении цены продажи автомобиля, выкупленного из лизинга, для уменьшения НДС. Колонка юриста Эдгара Бакояна.',
      cta='Похожая ситуация с продажей актива или доначислением НДС?'),
 dict(slug='bakoyan-115-fz-chast-1', author='bakoyan', type='Инструкция', topic='Блокировка счетов, часть 1 из 2',
      h1='Почему банк блокирует операции и что с этим делать. Часть 1: 115-ФЗ', title='Почему банк блокирует операции. Часть 1: 115-ФЗ — Эдгар Бакоян',
      desc='Как банк оценивает клиента по 115-ФЗ, почему первый ответ банку решает всё и чем ограничения по 161-ФЗ отличаются от 115-ФЗ. Эдгар Бакоян.',
      cta='Банк ограничил операции или запросил документы?'),
 dict(slug='bakoyan-zsk-svetofor-chast-2', author='bakoyan', type='Ликбез', topic='Блокировка счетов, часть 2 из 2',
      h1='Почему банк блокирует операции. Часть 2: ЗСК («Светофор»)', title='Платформа ЗСК («Светофор»): как банки оценивают риск — Эдгар Бакоян',
      desc='Как работает платформа ЗСК Центробанка, какие показатели алгоритм считает подозрительными и почему это часто ошибка. Колонка Эдгара Бакояна.',
      cta='Банк оценил вас как «повышенный риск»?'),
 dict(slug='bakoyan-nds-azy-i-stavki', author='bakoyan', type='Ликбез', topic='НДС, часть 1 из 3',
      h1='НДС: азы и ставки', title='НДС: азы, вычеты и ставки 2026 года — Эдгар Бакоян',
      desc='Как устроен НДС: входящий и исходящий налог, вычеты, ставки 0, 10 и 22 % и специальные ставки 5 и 7 % для УСН. Ликбез юриста Эдгара Бакояна.',
      cta='Нужно посчитать, какой режим выгоднее именно вам?'),
 dict(slug='bakoyan-bumazhnyi-nds', author='bakoyan', type='Разбор практики', topic='НДС, часть 2 из 3',
      h1='Бумажный НДС: экономика жанра', title='Бумажный НДС: экономика жанра — Эдгар Бакоян',
      desc='Кого на самом деле обкрадывает бумажный НДС, как работает статья 54.1 НК РФ и что изменила уголовная статья 173.3. Разбор Эдгара Бакояна.',
      cta='Получили требование по «разрыву» в цепочке контрагентов?'),
 dict(slug='bakoyan-razryvy-po-nds', author='bakoyan', type='Разбор практики', topic='НДС, часть 3 из 3',
      h1='Как налоговая находит разрывы по НДС и почему «крайним» может стать честный бизнес', title='Как налоговая находит разрывы по НДС — Эдгар Бакоян',
      desc='АСК НДС, реестр выгодоприобретателей и балльная система ФНС: как находят разрывы и как не стать «крайним» по чужому разрыву. Эдгар Бакоян.',
      cta='Получили требование как «выгодоприобретатель» по чужому разрыву?'),
]
ART = {a['slug']: a for a in ARTICLES}
for i, a in enumerate(ARTICLES):
    same = [x for x in ARTICLES if x['author'] == a['author']]
    j = same.index(a)
    a['prev'] = same[j-1]['slug'] if j > 0 else None
    a['next'] = same[j+1]['slug'] if j < len(same)-1 else None

AUTHOR_CTA = {
 'chinokalov': [('tel:' + PHONE_TEL, 'Позвонить в офис', 'btn'), ('https://t.me/Maxim_Chinokalov', 'Написать Максиму Чинокалову', 'btn btn-ghost')],
 'bakoyan': [('tel:+79024076631', 'Позвонить лично', 'btn'), ('https://t.me/Ed_Law1', 'Написать Эдгару Бакояну', 'btn btn-ghost')],
}
AUTHOR_ROLE = {'chinokalov': 'адвокат по уголовным делам', 'bakoyan': 'юрист, налоговый консультант'}

# ---------------------------------------------------------------------------
# Статьи: преобразование текста из старой разметки
# ---------------------------------------------------------------------------
MARKERS = [  # (regex в начале строки, класс списка)
    (r'[❗❕]️?\s*', 'alert'),
    (r'[✔✅]️?\s*', 'check'),
    (r'❌️?\s*', 'cross'),
    (r'[1-9]️?⃣\s*', 'ol'),
    (r'📌\s*', 'pin'),
    (r'🔹\s*', 'plain'),
    (r'⚡️?\s*', 'plain'),
    (r'[🟢🟡🔴]\s*', 'plain'),
    (r'—\s+', 'plain'),
]
STRIP_EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿⭐⬆↔-↪️‍⃣]+')

def classify(line):
    for rx, cls in MARKERS:
        m = re.match(rx, line)
        if m:
            return cls, line[m.end():].strip()
    return None, line

def clean_text(t):
    t = STRIP_EMOJI.sub('', t)
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'\s+([,.;:!?»)])', r'\1', t)
    return t.strip()

def build_list(cls, items):
    items_html = '\n'.join(f'  <li>{clean_text(x)}</li>' for x in items)
    if cls == 'ol':
        return f'<ol>\n{items_html}\n</ol>'
    c = {'alert': ' class="alert"', 'check': ' class="check"', 'cross': ' class="cross"'}.get(cls, '')
    return f'<ul{c}>\n{items_html}\n</ul>'

def transform_body(raw):
    """raw: содержимое между первым .article-text и .article-cta (старая разметка)."""
    raw = raw.replace('<div class="article-text">', '').replace('</div>', '')
    # вынести таблицы и примечания к ним как отдельные блоки
    tokens = re.split(r'(<table.*?</table>|<p class="section-note"[^>]*>.*?</p>)', raw, flags=re.S)
    out = []
    pending = None  # (cls, items) для объединения соседних однострочных абзацев-пунктов
    def flush():
        nonlocal pending
        if pending:
            out.append(build_list(*pending)); pending = None
    for tok in tokens:
        if not tok.strip():
            continue
        if tok.startswith('<table'):
            flush()
            tok = re.sub(r'<table class="article-table">', '<table>', tok)
            out.append('<div class="table-wrap">\n' + tok.strip() + '\n</div>')
            continue
        if tok.startswith('<p class="section-note"'):
            flush()
            txt = re.sub(r'<p[^>]*>|</p>', '', tok).strip()
            out.append(f'<p class="table-note">{txt}</p>')
            continue
        for m in re.finditer(r'<p>(.*?)</p>', tok, flags=re.S):
            inner = m.group(1).strip()
            lines = [l.strip() for l in re.split(r'<br\s*/?>', inner)]
            lines = [re.sub(r'\s*\n\s*', ' ', l) for l in lines if l.strip()]
            classes = [classify(l) for l in lines]
            marker_set = {c for c, _ in classes}
            # Подзаголовок: <p><strong>…</strong></p>
            if len(lines) == 1 and re.fullmatch(r'<strong>.*?</strong>', lines[0], flags=re.S):
                flush()
                head = re.sub(r"</?strong>", "", lines[0])
                head = re.sub(r'^([1-9])️?⃣\s*', r'\1. ', head)  # 1️⃣ → «1. »
                out.append(f'<p class="subhead">{clean_text(head)}</p>')
                continue
            # Жирная первая строка + текст: <p><strong>Заголовок</strong><br>текст</p> → подзаголовок + абзац
            if len(lines) >= 2 and re.fullmatch(r'<strong>.*?</strong>', lines[0], flags=re.S) and all(c is None for c, _ in classes[1:]):
                flush()
                out.append(f'<p class="subhead">{clean_text(re.sub(r"</?strong>", "", lines[0]))}</p>')
                out.append('<p>' + '<br>'.join(clean_text(l) for l in lines[1:]) + '</p>')
                continue
            # Все строки с одинаковым маркером → список
            if len(lines) >= 2 and len(marker_set) == 1 and None not in marker_set:
                flush()
                cls = classes[0][0]
                items = [t for _, t in classes]
                if cls == 'pin':
                    cls = 'plain'
                out.append(build_list(cls, items))
                continue
            # Одна строка с маркером
            if len(lines) == 1 and classes[0][0] not in (None,):
                cls, txt = classes[0]
                if cls == 'pin':
                    flush()
                    txt = clean_text(txt)
                    if txt.startswith('Сначала коротко'):  # вводная фраза, а не вывод
                        out.append(f'<p>{txt}</p>')
                        continue
                    txt = re.sub(r'^<strong>Вывод:</strong>\s*(\w)', lambda m: '<strong>Вывод.</strong> ' + m.group(1).upper(), txt)
                    out.append(f'<div class="note"><p>{txt}</p></div>')
                    continue
                if cls == 'plain':  # одиночная строка с «⚡/—» — это абзац, а не список из одного пункта
                    flush()
                    out.append(f'<p>{clean_text(txt)}</p>')
                    continue
                if pending and pending[0] == cls:
                    pending[1].append(txt)
                else:
                    flush(); pending = (cls, [txt])
                continue
            # Смешанный абзац: первая строка — вводная, остальные — пункты
            if len(lines) >= 2 and classes[0][0] is None and all(c is not None for c, _ in classes[1:]) and len({c for c, _ in classes[1:]}) == 1:
                flush()
                out.append(f'<p>{clean_text(lines[0])}</p>')
                out.append(build_list(classes[1][0] if classes[1][0] != 'pin' else 'plain', [t for _, t in classes[1:]]))
                continue
            # Обычный абзац (переносы строк внутри — просто пробелы; <br> сохраняем)
            flush()
            txt = '<br>'.join(clean_text(l) for l in lines)
            out.append(f'<p>{txt}</p>')
    flush()
    return '\n\n'.join(out)

def extract_old_article(slug):
    p = os.path.join(ROOT, 'materialy', slug + '.html')
    s = open(p, encoding='utf-8').read()
    m = re.search(r'(<div class="article-text">.*?)<div class="article-cta">', s, flags=re.S)
    return m.group(1)

def article_page(a):
    author = PEOPLE[a['author']]
    root = '../'
    body_html = transform_body(extract_old_article(a['slug']))
    if a['author'] == 'chinokalov':
        avatar = f'<img src="{root}assets/img/chinokalov.jpg" alt="" width="44" height="44">'
    else:
        avatar = f'<span class="avatar" aria-hidden="true">{author["initials"]}</span>'
    cta_links = '\n      '.join(f'<a class="{cls.replace("btn btn-ghost", "btn btn-ghost").replace("btn\"", "btn btn-gold\"") if False else ("btn btn-gold" if cls == "btn" else cls)}" href="{href}"{" target=\"_blank\" rel=\"noopener\"" if href.startswith("http") else ""}>{txt}</a>' for href, txt, cls in AUTHOR_CTA[a['author']])
    prev_html = next_html = ''
    if a['prev']:
        prev_html = f'<a class="prev" href="{a["prev"]}.html"><small>Предыдущий материал</small>{ART[a["prev"]]["h1"]}</a>'
    if a['next']:
        next_html = f'<a class="next" href="{a["next"]}.html"><small>Следующий материал</small>{ART[a["next"]]["h1"]}</a>'
    else:
        next_html = f'<a class="next" href="./"><small>Дальше</small>Все материалы</a>'
    ld = [{"@context":"https://schema.org","@type":"Article","headline":a['h1'],"description":a['desc'],
           "mainEntityOfPage":SITE+'/materialy/'+a['slug']+'.html',"inLanguage":"ru",
           "author":{"@type":"Person","name":author['name'],"jobTitle":AUTHOR_ROLE[a['author']],"url":SITE+author['url']},
           "publisher":{"@type":"Organization","name":"Capital Defence","url":SITE+"/","logo":{"@type":"ImageObject","url":SITE+"/assets/img/emblem-320.jpg"}},
           "image":SITE+"/assets/img/og.png"}]
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <header class="article-head">
      <p class="kicker">{a['type']}. {a['topic']}</p>
      <h1>{a['h1']}</h1>
      <p class="byline">{avatar}<span>Автор: <a href="{root}{author['url'].lstrip('/')}">{author['name']}</a>, {AUTHOR_ROLE[a['author']]}</span></p>
    </header>
  </div>
</section>
<article class="article band-light">
  <div class="wrap">
    <div class="prose">
{body_html}
    </div>

    <aside class="article-cta">
      <strong>{a['cta']}</strong>
      <div class="actions">
      {cta_links}
      </div>
    </aside>

    <nav class="article-nav" aria-label="Соседние материалы">
      {prev_html}
      {next_html}
    </nav>
  </div>
</article>'''
    title = a['title'] + ' | Capital Defence'
    if len(title) > 70:
        title = a['title']
    write(f'materialy/{a["slug"]}.html', shell(root=root, path=f'/materialy/{a["slug"]}.html', title=title, description=a['desc'],
          body=body, active='materialy', ld=ld, og_type='article',
          crumbs=[('Главная', '/'), ('Материалы', '/materialy/'), (a['h1'], f'/materialy/{a["slug"]}.html')]))

def article_rows(root, slugs, show_author=True):
    rows = []
    for s in slugs:
        a = ART[s]
        by = f'<span class="by">{PEOPLE[a["author"]]["name"]}</span>' if show_author else ''
        rows.append(f'  <li><a href="{root}materialy/{s}.html"><span class="type">{a["type"]}</span><span class="title">{a["h1"]}</span>{by}</a></li>')
    return '<ul class="article-list">\n' + '\n'.join(rows) + '\n</ul>'

# ---------------------------------------------------------------------------
# Услуги: единый источник для главной (список) и страницы услуг (описания)
# ---------------------------------------------------------------------------
SERVICES = [
 dict(id='bankrotstvo', short='Банкротство', title='Банкротство и защита от кредиторов',
      intro='Долги, которые не получается платить, блокировка счёта, деньги, ушедшие не туда. Банкротство, работа с банком и приставами, возврат переводов.',
      items=[
        ('bankrotstvo-fizlic-ip', 'Банкротство физлиц и ИП',
         'Сначала смотрим, подходит ли вам процедура и что в ней придётся показать: имущество, сделки, доходы. Потом документы, заявление в арбитражный суд и сопровождение до списания долгов.'),
        ('zashchita-ot-kollektorov', 'Защита от коллекторов и приставов',
         'Проверяем, законны ли требования и действия взыскателей. Обжалуем нарушения, снимаем необоснованные аресты, договариваемся о рассрочке, если это выгоднее.'),
        ('razblokirovka-schetov', 'Разблокировка счетов (115-ФЗ, 161-ФЗ)',
         'Выясняем, на каком основании банк ограничил операции, и готовим ответ на запрос с документами. Если банк не отступает, идём в межведомственную комиссию при Банке России и в суд.'),
        ('neosnovatelnoe-obogashchenie', 'Споры о неосновательном обогащении (ст. 1102 ГК РФ)',
         'Деньги ушли без договора или по сделке, которая не состоялась, в том числе через биржу или P2P-перевод. Собираем доказательства перевода, направляем претензию, ведём дело в суде.'),
      ]),
 dict(id='biznes', short='Бизнес и налоги', title='Бизнес и налоги',
      intro='Для компаний и ИП: договоры, налоги, регистрация и ликвидация, кадры.',
      items=[
        ('sdelki-i-dogovory', 'Сопровождение сделок и договоров',
         'Готовим и проверяем договоры, согласовываем условия с другой стороной, показываем риски до подписания. Если условия нарушили, ведём претензионную работу.'),
        ('mediaciya-fns', 'Медиация и переговоры с ФНС',
         'Представляем бизнес на комиссиях и в переговорах с налоговой, готовим пояснения и возражения на требования. Цель: закрыть вопрос без суда.'),
        ('nalogovaya-optimizaciya', 'Налоговая оптимизация и комплаенс',
         'Смотрим структуру бизнеса и договоры на налоговые риски, предлагаем законные способы снизить нагрузку, готовим документы под вычеты и расходы.'),
        ('registraciya-likvidaciya', 'Регистрация, реорганизация, ликвидация',
         'Регистрация ООО и ИП, изменения в учредительных документах, реорганизация и ликвидация с закрытием долгов перед налоговой и кредиторами.'),
        ('trudovye-spory', 'Трудовые споры и кадровые риски',
         'Приём, увольнение и дисциплинарные взыскания оформляем так, чтобы они устояли в суде и трудовой инспекции. В спорах представляем и работодателя, и работника.'),
      ]),
 dict(id='advokat', short='Адвокатская защита', title='Адвокатская защита',
      intro='Дела, где нужен адвокат со статусом: уголовные, административные и гражданские, на следствии и в суде.',
      items=[
        ('ugolovnye-dela', 'Уголовные дела: следствие и суд',
         'Подключаемся с задержания, обыска или вызова на допрос. Участвуем в следственных действиях, обжалуем меру пресечения, ведём защиту в первой инстанции, апелляции и кассации. После приговора: УДО и пересмотр.'),
        ('administrativnye-dela', 'Административные дела',
         'От протокола до обжалования постановления в суде: штрафы, лишение прав, приостановление деятельности.'),
        ('grazhdanskie-spory', 'Гражданские споры, представительство в суде',
         'Подготовка иска, сбор доказательств, заседания, обжалование, исполнение решения.'),
        ('zashchita-predprinimatelei', 'Защита прав предпринимателей',
         'Проверки, давление контролирующих органов, уголовное преследование по экономическим статьям.'),
      ]),
 dict(id='semya', short='Семья и наследство', title='Семья и наследство',
      intro='Развод, имущество, дети, наследство. Если договориться возможно, помогаем договориться без суда.',
      items=[
        ('razvod', 'Развод, раздел имущества, алименты',
         'Расторжение брака через ЗАГС или суд, раздел нажитого, место жительства детей и порядок общения, взыскание и изменение алиментов.'),
        ('semeinaya-mediaciya', 'Медиация в семейных конфликтах',
         'Переговоры с медиатором, чтобы закрепить договорённости соглашением, а не решением суда. Быстрее и спокойнее, особенно когда есть дети.'),
        ('nasledstvo', 'Наследственные споры, вступление в наследство',
         'Оформление наследства, восстановление пропущенного срока, оспаривание завещания, раздел имущества между наследниками.'),
      ]),
 dict(id='nedvizhimost', short='Недвижимость', title='Недвижимость и сделки',
      intro='Жильё и коммерческая недвижимость: проверка перед покупкой, сделка, споры.',
      items=[
        ('proverka-sdelok', 'Юридическая проверка сделок (due diligence)',
         'Проверяем объект, продавца и историю переходов права. Обременения, долги и риск оспаривания находим до того, как вы внесёте аванс.'),
        ('spory-nedvizhimost', 'Споры по недвижимости, снятие обременений',
         'Признание права собственности, снятие ареста и залога, споры с застройщиком, выдел доли, выселение и вселение.'),
        ('arenda-kuplya-prodazha', 'Сопровождение аренды и купли-продажи',
         'Договор, согласование условий, расчёты, регистрация в Росреестре.'),
      ]),
 dict(id='chastnym', short='Частным клиентам', title='Частным клиентам',
      intro='Споры с магазином, страховой, банком, управляющей компанией.',
      items=[
        ('potrebitelskie-spory', 'Потребительские споры',
         'Возврат денег за некачественный товар или услугу, неустойка и штраф по закону о защите прав потребителей. Претензия, затем иск.'),
        ('strakhovye-banki', 'Споры со страховыми и банками',
         'Занижение или отказ в страховой выплате, навязанные услуги и комиссии, споры по кредитам.'),
        ('sud-obshchei-yurisdikcii', 'Консультации и представительство в судах общей юрисдикции',
         'Разовая консультация с оценкой ситуации. Если нужно, дальше ведём дело в суде.'),
      ]),
]

def uslugi_index():
    root = '../'
    subnav = '\n'.join(f'    <a href="#{s["id"]}">{s["short"]}</a>' for s in SERVICES)
    blocks = []
    for i, s in enumerate(SERVICES):
        items = '\n'.join(f'''      <li class="svc-item" id="{iid}">
        <h3>{t}</h3>
        <p>{d}</p>
      </li>''' for iid, t, d in s['items'])
        blocks.append(f'''<section class="svc band {'band-light' if i % 2 == 0 else 'band-light-2'}" id="{s['id']}">
  <div class="wrap svc-grid">
    <div class="svc-head">
      <h2>{s['title']}</h2>
      <p class="lead">{s['intro']}</p>
    </div>
    <ul class="svc-list">
{items}
    </ul>
  </div>
</section>''')
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <h1>Чем мы занимаемся</h1>
    <p class="lead">Шесть направлений, внутри каждого конкретные задачи. Если не нашли своей, напишите, что случилось: скажем, кто из команды этим занимается.</p>
  </div>
</section>
<nav class="subnav" aria-label="Направления">
  <div class="wrap">
{subnav}
  </div>
</nav>
{chr(10).join(blocks)}
<section class="band band-dark">
  <div class="wrap">
    <div class="panel-dark svc-cta" style="padding:0;margin:0;background:transparent;">
      <div>
        <h2>Не нашли свою ситуацию?</h2>
        <p>Опишите её в двух словах. Разберём бесплатно и скажем, с чего начать.</p>
      </div>
      <div class="actions">
        <a class="btn btn-gold" href="{root}#contact">Записаться на консультацию</a>
        <a class="btn btn-ghost" href="{TG}" target="_blank" rel="noopener">Написать в Telegram</a>
      </div>
    </div>
  </div>
</section>'''
    write('uslugi/index.html', shell(root=root, path='/uslugi/', title='Услуги юристов и адвокатов в Пензе | Capital Defence',
        description='Банкротство и разблокировка счетов, бизнес и налоги, уголовная защита, семейные и наследственные дела, недвижимость, споры частных лиц. Capital Defence, Пенза.',
        body=body, active='uslugi', crumbs=[('Главная', '/'), ('Услуги', '/uslugi/')]))

# ---------------------------------------------------------------------------
# Главная
# ---------------------------------------------------------------------------
def services_count(n):
    """«4 услуги», «5 услуг», «1 услуга»: подпись под направлением на телефоне."""
    if n % 10 == 1 and n % 100 != 11:
        word = 'услуга'
    elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        word = 'услуги'
    else:
        word = 'услуг'
    return f'{n} {word}'


def home():
    root = ''
    svc = '\n'.join(f'''  <li>
    <h3><a href="uslugi/#{s['id']}"><span class="name">{s['title']}</span><span class="cnt">{services_count(len(s['items']))}</span></a></h3>
    <p>{' '.join(f'<a href="uslugi/#{iid}" data-text="{t}{"," if i < len(s["items"]) - 1 else ""}">{t}{"<span class=\"sep\">,</span>" if i < len(s["items"]) - 1 else ""}</a>' for i, (iid, t, _) in enumerate(s['items']))}</p>
  </li>''' for s in SERVICES)
    team = '\n'.join(person_card(root, k) for k in ['simkin', 'chinokalov', 'truevtsev', 'bakoyan', 'shitov'])
    latest = article_rows(root, ['chinokalov-obysk-chto-delat', 'chinokalov-zaderzhanie-chto-delat', 'bakoyan-115-fz-chast-1', 'bakoyan-razryvy-po-nds'])
    body = f'''<section class="hero band-dark">
  <div class="wrap hero-grid">
    <div>
      <p class="kicker">Юридическое агентство, Пенза</p>
      <h1>Адвокаты, юристы и медиаторы в Пензе</h1>
      <p class="lead">Уголовные дела, налоги, банкротство, споры с банками, разблокировка счетов, защита бизнеса, семейные споры, представительство в суде. Первый разбор ситуации бесплатный: после него вы понимаете, что делать и с кем.</p>
      <div class="actions">
        <a class="btn btn-gold" href="#contact">Записаться на консультацию</a>
        <a class="text-link" href="{TG}" target="_blank" rel="noopener">Написать в Telegram</a>
      </div>
    </div>
    <aside class="hero-aside">
      <img class="hero-emblem" src="assets/img/emblem-320.jpg" alt="Эмблема Capital Defence" width="132" height="132">
      <ul class="facts">
        <li><span class="k">Адрес</span><span class="v">{ADDR}</span></li>
        <li><span class="k">Часы</span><span class="v">{HOURS}</span></li>
        <li><span class="k">Telegram</span><span class="v"><a href="{TG}" target="_blank" rel="noopener">@Capital_Defence</a></span></li>
        <li><span class="k">Команда</span><span class="v">3 адвоката, 2 юриста, медиатор</span></li>
      </ul>
      <p class="hero-note">Принимаем в офисе на проспекте Победы. С другими городами работаем удалённо.</p>
    </aside>
  </div>
</section>

<section class="band band-light" id="practice">
  <div class="wrap">
    <div class="band-head">
      <h2>Направления работы</h2>
      <p class="lead">Договоры, сделки и споры ведут юристы. На следствии и в суде работают адвокаты. Медиатор помогает договориться без суда.</p>
    </div>
    <ul class="rows">
{svc}
    </ul>
  </div>
</section>

<section class="band band-dark-2" id="team">
  <div class="wrap">
    <div class="band-head">
      <h2>Команда</h2>
      <p class="lead">Каждый ведёт дело лично. На странице специалиста: чем занимается, где учился, опыт и как с ним связаться.</p>
    </div>
    <div class="team-grid">
{team}
    </div>
    <div class="team-links">
      <a class="text-link" href="advokaty/">Все адвокаты</a>
      <a class="text-link" href="yuristy/">Все юристы</a>
    </div>
  </div>
</section>

<section class="band band-light" id="materials">
  <div class="wrap">
    <div class="band-head">
      <h2>Материалы</h2>
      <p class="lead">Пишут адвокаты и юристы агентства.</p>
    </div>
{latest}
    <div class="team-links">
      <a class="text-link" href="materialy/">Все материалы</a>
    </div>
  </div>
</section>

<section class="contact band band-dark" id="contact">
  <div class="wrap">
    <h2>Запишитесь на консультацию</h2>
    <div class="contact-grid">
      <div>
        <ul class="facts">
          <li><span class="k">Адрес</span><span class="v">{ADDR}</span></li>
          <li><span class="k">Телефон</span><span class="v"><a href="tel:{PHONE_TEL}">{PHONE}</a></span></li>
          <li><span class="k">Telegram</span><span class="v"><a href="{TG}" target="_blank" rel="noopener">@Capital_Defence</a></span></li>
          <li><span class="k">Часы</span><span class="v">{HOURS}</span></li>
        </ul>
        <a class="map-link" href="{MAP}" target="_blank" rel="noopener">Открыть на Яндекс Картах</a>
        <ol class="process">
          <li><span>Вы звоните, пишете в Telegram или оставляете заявку в форме.</span></li>
          <li><span>Уточняем, что произошло и какие есть документы, оцениваем риски.</span></li>
          <li><span>Говорим, что делать, и, если нужно, заключаем соглашение.</span></li>
        </ol>
      </div>
      <form class="form" id="requestForm">
        <div class="form-fields">
          <div class="field">
            <label for="f-name">Имя</label>
            <input id="f-name" name="name" type="text" placeholder="Как к вам обращаться" required autocomplete="name">
          </div>
          <div class="field">
            <label for="f-phone">Телефон или Telegram</label>
            <input id="f-phone" name="phone" type="text" placeholder="+7 … или @username" required autocomplete="tel">
          </div>
          <div class="field">
            <label for="f-message">Кратко о ситуации</label>
            <textarea id="f-message" name="message" placeholder="Например: заблокировали счёт по 115-ФЗ"></textarea>
          </div>
          <label class="consent">
            <input type="checkbox" id="f-consent" required>
            <span>Я принимаю <a href="dokumenty/politika-obrabotki-pd.html" target="_blank" rel="noopener">политику обработки персональных данных</a> и даю <a href="dokumenty/soglasie-na-obrabotku-pd.html" target="_blank" rel="noopener">согласие на обработку персональных данных</a></span>
          </label>
          <button class="btn btn-gold" type="submit">Отправить в Telegram</button>
          <p class="form-note">Заявка откроется в Telegram-диалоге с @Capital_Defence. На сайте ничего не сохраняется.</p>
        </div>
        <div class="form-done">
          <p>Заявка подготовлена и открыта в Telegram. Если окно не появилось, <a href="{TG}" target="_blank" rel="noopener">откройте диалог вручную</a> или позвоните: <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
        </div>
      </form>
    </div>
  </div>
</section>'''
    ld = [dict({"@context":"https://schema.org"}, **ORG, **{
        "image":SITE+"/assets/img/og.png","logo":SITE+"/assets/img/emblem-320.jpg","sameAs":[TG],
        "openingHoursSpecification":{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"10:00","closes":"22:00"},
        "areaServed":"RU","description":"Юридическое агентство в Пензе: адвокаты по уголовным, экономическим и административным делам, юристы для бизнеса, медиация с ФНС."})]
    write('index.html', shell(root=root, path='/', title='Capital Defence — юридическое агентство в Пензе',
        description='Юридическое агентство Capital Defence в Пензе: адвокаты по уголовным, экономическим и административным делам, юристы для бизнеса, медиация с ФНС. Просп. Победы, 97.',
        body=body, active=None, ld=ld))

# ---------------------------------------------------------------------------
# Адвокаты
# ---------------------------------------------------------------------------
def advokaty_index():
    root = '../'
    cards = '\n'.join(person_card(root, k, desc=True, more=True) for k in ['simkin', 'chinokalov', 'truevtsev'])
    situations = [
        ('Задержание и доставление', 'Установление места и статуса, фиксация времени, право на защитника с первой минуты.'),
        ('Обыск, осмотр, выемка', 'Контроль постановления и протокола — что и как изымается, замечания по ходу действия.'),
        ('Допрос и объяснения', 'Разбор оснований вызова, подготовка позиции, участие и проверка протокола перед подписанием.'),
        ('Мера пресечения', 'Заседания об аресте, домашнем аресте, запрете действий — доводы и документы против изоляции.'),
        ('Экономические и налоговые дела', 'Защита по экономическим составам, споры и медиация с ФНС.'),
        ('Административные и гражданские споры', 'Представительство в судах общей юрисдикции по смежным вопросам.'),
    ]
    sit = '\n'.join(f'  <div><h4>{t}</h4><p>{d}</p></div>' for t, d in situations)
    steps = [
        ('Узнайте, где он и какой орган ведёт дело', 'Отдел полиции, следственное подразделение, район. О задержании должны уведомить родственников не позднее 3 часов (ст. 96 УПК РФ).'),
        ('Звоните адвокату, а не «решателю»', 'Обещания «договориться» за деньги — обычно мошенничество или посредничество во взяточничестве (ст. 291.1 УК РФ), по которому потом отвечает и тот, кто платил.'),
        ('Заключите соглашение в интересах задержанного', 'Это вправе сделать любой родственник (ч. 1 ст. 25 ФЗ № 63-ФЗ) — адвокат вступает в дело и получает право на свидание наедине.'),
        ('Соберите документы к заседанию по мере пресечения', 'Паспорт, справки о работе, документы о собственности, характеристики — это реально влияет на решение суда.'),
        ('Не обсуждайте детали дела по телефону', 'И не пересылайте документы в незащищённые чаты — всё существенное обсуждайте с защитником лично.'),
    ]
    st = '\n'.join(f'  <li><div><strong>{t}</strong><p>{d}</p></div></li>' for t, d in steps)
    faq = [
        ('Может ли адвоката вызвать родственник?', 'Да. Соглашение об оказании юридической помощи вправе заключить любое лицо в интересах задержанного (ч. 1 ст. 25 ФЗ № 63-ФЗ).'),
        ('Разговор с адвокатом — это тайна?', 'Да, факт обращения и его содержание охраняются адвокатской тайной (ст. 8 ФЗ № 63-ФЗ).'),
        ('Как быстро вы подключаетесь к делу?', 'Как можно скорее после звонка — точное время зависит от адреса и времени суток, конкретику проще обсудить по телефону.'),
    ]
    fq = '\n'.join(f'  <details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq)
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <h1>Защита на следствии, в суде и при силовых мероприятиях</h1>
    <p class="lead">Каждый адвокат ведёт дело лично, от первого звонка до итогового решения. У каждого своя страница с полным профилем и контактами.</p>
  </div>
</section>
<section class="band band-light"><div class="wrap">
  <div class="panel-dark">
    <div>
      <p class="kicker">Срочная ситуация</p>
      <h2>Задержание, обыск, допрос, вызов в суд</h2>
      <p>Выезд и подключение к делу по звонку. Расскажите по телефону четыре вещи: где находитесь, какой орган работает, что происходит и есть ли документы на руках.</p>
    </div>
    <div class="actions">
      <a class="btn btn-gold" href="tel:{PHONE_TEL}">Позвонить {PHONE}</a>
      <a class="btn btn-ghost" href="{TG}" target="_blank" rel="noopener">Написать в Telegram</a>
    </div>
  </div>

  <div class="directory">
{cards}
  </div>

  <div class="sub-head"><h2>С какими ситуациями обращаются чаще всего</h2></div>
  <div class="situations">
{sit}
  </div>

  <div class="sub-head"><h2>Если проблема случилась с близким человеком</h2></div>
  <ol class="steps">
{st}
  </ol>

  <div class="sub-head"><h2>Частые вопросы</h2></div>
  <div class="faq">
{fq}
  </div>
</div></section>'''
    write('advokaty/index.html', shell(root=root, path='/advokaty/', title='Адвокаты в Пензе — уголовные, экономические и административные дела | Capital Defence',
        description='Адвокаты юридического агентства Capital Defence в Пензе: Ярослав Симкин, Максим Чинокалов, Михаил Труевцев. Защита на следствии и в суде, срочный выезд.',
        body=body, active='advokaty', crumbs=[('Главная', '/'), ('Адвокаты', '/advokaty/')]))

def profile_page(key, *, path, title, description, role_line, intro, sections, contacts, registry=None, articles=None, ld_extra=None, section='advokaty'):
    root = '../'
    p = PEOPLE[key]
    secs = ''
    for h, content in sections:
        secs += f'\n    <div class="profile-section">\n      <h2>{h}</h2>\n{content}\n    </div>'
    arts = ''
    if articles:
        arts = f'\n    <div class="profile-section">\n      <h2>Статьи</h2>\n{article_rows(root, articles, show_author=False)}\n    </div>'
    reg = f'<p class="profile-registry">{registry}</p>' if registry else ''
    intro_html = f'<p class="lead">{intro}</p>' if intro else ''
    back = ('Ко всем адвокатам', 'advokaty/') if section == 'advokaty' else ('Ко всем юристам', 'yuristy/')
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <p class="kicker">{role_line}</p>
    <h1>{p['name']}</h1>
    {intro_html}
  </div>
</section>
<section class="band-light"><div class="wrap profile">
  <div class="profile-side">
    {portrait(root, key, lazy=False)}
    {reg}
  </div>
  <div>
{contact_list(contacts)}
{secs}{arts}
    <a class="back-link" href="{root}{back[1]}">← {back[0]}</a>
  </div>
</div></section>'''
    ld = [dict({"@context":"https://schema.org","@type":"Person","name":p['name'],"jobTitle":p['role'].replace(' · ', ', '),
                "url":SITE+p['url'],"worksFor":ORG}, **(ld_extra or {}))]
    if p['img']:
        ld[0]['image'] = SITE + '/assets/img/' + p['img']
    sect_name = 'Адвокаты' if section == 'advokaty' else 'Юристы'
    write(path.lstrip('/'), shell(root=root, path=path, title=title, description=description, body=body, active=section, ld=ld,
          crumbs=[('Главная', '/'), (sect_name, f'/{section}/'), (p['name'], path)]))

def ul(items):
    return '      <ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
def para(*ps):
    return '\n'.join(f'      <p>{x}</p>' for x in ps)

def profiles():
    profile_page('simkin', path='/advokaty/simkin.html', title='Адвокат Ярослав Симкин — Пенза | Capital Defence',
        description='Ярослав Симкин — адвокат по экономическим делам, налоговый консультант и медиатор в Пензе. Образование, опыт, контакты. Capital Defence.',
        role_line='Адвокат, налоговый консультант, медиатор', intro=None,
        contacts=[('phone', 'Телефон', '+7 (902) 209‑73‑33', 'tel:+79022097333', False),
                  ('send', 'Telegram', '@true_law333', 'https://t.me/true_law333', True),
                  ('radio', 'Канал агентства', '@Capital_Defence', TG, True)],
        sections=[('Сфера деятельности', ul(['Адвокат по экономическим делам', 'Специалист по банковскому и налоговому праву',
                        'Налоговый консультант для бизнеса и физических лиц', 'Медиатор — досудебное урегулирование споров, включая медиацию между бизнесом и ФНС'])),
                  ('Образование', ul(['ПГУ — юридический факультет, юриспруденция', 'РАНХиГС им. П. А. Столыпина — магистратура и аспирантура, юриспруденция', 'РУАН им. Г. Б. Мирзоева — кафедра адвокатуры'])),
                  ('Опыт', para('С 2019 года — адвокат Пензенского филиала коллегии адвокатов г. Москвы «Гарант».'))],
        ld_extra={"alumniOf":["ПГУ","РАНХиГС им. П. А. Столыпина","РУАН им. Г. Б. Мирзоева"],"sameAs":["https://t.me/true_law333"]})

    profile_page('chinokalov', path='/advokaty/chinokalov.html', title='Адвокат Максим Чинокалов — уголовные дела, Пенза | Capital Defence',
        description='Максим Чинокалов — адвокат по уголовным делам в Пензе. 15 лет в уголовном процессе, 10 лет в Следственном комитете. Защита на следствии и в суде, УДО, пересмотр приговора.',
        role_line='Адвокат по уголовным делам',
        intro='Защищаю по уголовным делам в Пензе и Пензенской области — от первого объяснения до обжалования приговора. Выезд в другие регионы по согласованию.',
        contacts=[('phone', 'Телефон', '+7 (999) 612‑11‑15', 'tel:+79996121115', False),
                  ('send', 'Telegram', '@Maxim_Chinokalov', 'https://t.me/Maxim_Chinokalov', True),
                  ('radio', 'Канал «Вправе»', '@chinokalov_vprave', 'https://t.me/chinokalov_vprave', True)],
        registry='Сведения об адвокате внесены в Единый государственный реестр адвокатов, рег. № 58/912. Проверить статус можно на <a href="https://minjust.gov.ru/ru/pages/advokaty-rossijskoj-federacii/" target="_blank" rel="noopener">сайте Минюста России</a>.',
        sections=[('О себе', para('Более 15 лет в уголовном процессе. 10 лет — в Следственном комитете: от рядового следователя до следователя по особо важным делам следственного управления. Более 5 лет — адвокатская практика. Знаю уголовный процесс с обеих сторон. Ежегодно повышаю квалификацию, в том числе по обжалованию судебных актов, тактике судебных допросов и изменению меры пресечения.',
                        'Два высших образования — юридическое и экономическое.', 'Углублённое направление — экономические, должностные и коррупционные преступления.')),
                  ('Чем помогаю', ul(['<strong>Задержали или пришли с обыском</strong> — выезжаю незамедлительно, беру на себя общение со следствием. Вы ничего не подписываете и не даёте показаний без меня.',
                        '<strong>Идёт следствие</strong> — обжалую незаконные действия, добиваюсь изменения меры пресечения, работаю над прекращением дела или смягчением обвинения там, где есть основания.',
                        '<strong>Дело в суде</strong> — первая инстанция, апелляция, кассация. Строю защиту на нарушениях процедуры и слабых доказательствах.',
                        '<strong>Приговор вступил в силу</strong> — УДО, замена наказания, пересмотр по новым обстоятельствам.']))],
        articles=[a['slug'] for a in ARTICLES if a['author'] == 'chinokalov'],
        ld_extra={"identifier":"Реестровый № 58/912","sameAs":["https://t.me/Maxim_Chinokalov","https://t.me/chinokalov_vprave"]})

    profile_page('truevtsev', path='/advokaty/truevtsev.html', title='Адвокат Михаил Труевцев — Пенза | Capital Defence',
        description='Михаил Труевцев — адвокат по уголовным, административным и гражданским делам в Пензе. 15 лет в Следственном комитете, более 5 лет адвокатской практики.',
        role_line='Адвокат по уголовным, административным и гражданским делам', intro=None,
        contacts=[('phone', 'Телефон офиса', PHONE, 'tel:' + PHONE_TEL, False),
                  ('send', 'Telegram агентства', '@Capital_Defence', TG, True)],
        sections=[('Опыт', ul(['15 лет работы в Следственном комитете', 'Более 5 лет адвокатской практики', '30 судебных дел']))])

    profile_page('bakoyan', section='yuristy', path='/yuristy/bakoyan.html', title='Юрист Эдгар Бакоян — налоговый консультант, Пенза | Capital Defence',
        description='Эдгар Варданович Бакоян — юрист, налоговый консультант Capital Defence. НДС, 115-ФЗ, налоговые споры. Контакты и статьи.',
        role_line='Юрист, налоговый консультант', intro=None,
        contacts=[('phone', 'Телефон', '+7 (902) 407‑66‑31', 'tel:+79024076631', False),
                  ('send', 'Telegram', '@Ed_Law1', 'https://t.me/Ed_Law1', True),
                  ('radio', 'Канал агентства', '@Capital_Defence', TG, True)],
        sections=[('Сфера деятельности', ul(['Налоговые споры и налоговое консультирование бизнеса', 'НДС: ставки, вычеты, «бумажный» НДС, разрывы в цепочке контрагентов',
                        'Сопровождение при блокировке счетов (115-ФЗ, 161-ФЗ), взаимодействие с банковским комплаенсом', 'Анализ судебной практики по налоговым делам']))],
        articles=[a['slug'] for a in ARTICLES if a['author'] == 'bakoyan'],
        ld_extra={"sameAs":["https://t.me/Ed_Law1"]})

    profile_page('shitov', section='yuristy', path='/yuristy/shitov.html', title='Юрист Иван Шитов — судебная практика и аутсорсинг, Пенза | Capital Defence',
        description='Иван Шитов — ведущий юрист Capital Defence. Судебная практика, юридический аутсорсинг для бизнеса, 44-ФЗ/РНП, комплаенс 152-ФЗ.',
        role_line='Ведущий юрист',
        intro='Полный цикл судебной работы и комплексное юридическое сопровождение бизнеса — от проверки поставщика и согласования контракта до победы в суде и сопровождения банкротства.',
        contacts=[('phone', 'Телефон офиса', PHONE, 'tel:' + PHONE_TEL, False),
                  ('send', 'Telegram агентства', '@Capital_Defence', TG, True)],
        sections=[('Судебная практика и защита интересов', ul(['Полное ведение дел в арбитражных судах и судах общей юрисдикции — от расчёта госпошлины и подготовки иска до получения решения и сопровождения исполнительного производства в ФССП',
                        'Разработка судебной стратегии: поиск и анализ практики, допрос экспертов, подготовка и опрос свидетелей, формирование устной позиции для заседаний',
                        'Банкротство физических лиц: сбор документов, подготовка и подача заявления, полное сопровождение процедуры',
                        'Представление интересов бизнеса и граждан в госорганах'])),
                  ('Договорная и претензионная работа (B2B-аутсорсинг)', ul(['Юридическое сопровождение компаний из сферы оптовой и розничной торговли (продукты питания, косметика, медтехника), производства (пластмассовые изделия, товарный бетон), а также инженерных изысканий',
                        'Проверка контрагентов, ведение переговоров, подготовка и согласование договоров, допсоглашений, протоколов разногласий, счетов и актов',
                        'Подготовка претензий, ответов на претензии и мировых соглашений'])),
                  ('Комплаенс и административные споры', ul(['Подготовка документов и правил по ФЗ «О персональных данных» (152-ФЗ)',
                        'Оспаривание в ФАС и арбитражных судах отказов от заключения контрактов и решений о включении в Реестр недобросовестных поставщиков (РНП) по 44-ФЗ'])),
                  ('Образование', ul(['СГЮА — институт юстиции, юриспруденция', 'ПГУ — магистратура, кафедра частного и публичного права'])),
                  ('Опыт', para('Сопровождение производственных, строительных и торговых компаний. Знает отраслевую специфику и закрывает весь спектр правовых задач — от договора до победы в суде. Опыт работы с производственными, торговыми и проектными компаниями позволяет говорить с бизнесом на одном языке.'))],
        ld_extra={"alumniOf":["СГЮА — институт юстиции","ПГУ — магистратура, кафедра частного и публичного права"]})

# ---------------------------------------------------------------------------
# Юристы
# ---------------------------------------------------------------------------
def yuristy_index():
    root = '../'
    cards = '\n'.join(person_card(root, k, desc=True, more=True) for k in ['bakoyan', 'shitov'])
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <h1>Договорная работа, бизнес и представительство без статуса адвоката</h1>
    <p class="lead">Юристы ведут договоры, сопровождение сделок и споров там, где не требуется адвокатский статус, и подключают адвоката, когда дело доходит до следствия или суда.</p>
  </div>
</section>
<section class="band band-light"><div class="wrap">
  <div class="directory">
{cards}
  </div>
  <div class="panel-dark" style="margin:clamp(48px,6vw,80px) 0 0;">
    <div>
      <p class="kicker">Для бизнеса</p>
      <h2>Юридическое сопровождение на аутсорсинге</h2>
      <p>Договоры, претензии, проверка контрагентов, споры в арбитраже и работа с налоговой без штатного юриста.</p>
    </div>
    <div class="actions">
      <a class="btn btn-gold" href="{root}#contact">Обсудить задачу</a>
      <a class="btn btn-ghost" href="{TG}" target="_blank" rel="noopener">Написать в Telegram</a>
    </div>
  </div>
</div></section>'''
    write('yuristy/index.html', shell(root=root, path='/yuristy/', title='Юристы в Пензе — договоры, налоги и сопровождение бизнеса | Capital Defence',
        description='Юристы агентства Capital Defence в Пензе: Эдгар Бакоян и Иван Шитов. Договорная работа, налоговые споры, 115-ФЗ, сопровождение сделок и бизнеса.',
        body=body, active='yuristy', crumbs=[('Главная', '/'), ('Юристы', '/yuristy/')]))

# ---------------------------------------------------------------------------
# Материалы
# ---------------------------------------------------------------------------
def materialy_index():
    root = '../'
    ch = [a['slug'] for a in ARTICLES if a['author'] == 'chinokalov']
    bk = [a['slug'] for a in ARTICLES if a['author'] == 'bakoyan']
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <h1>Практические материалы от команды Capital Defence</h1>
    <p class="lead">Что делать при обыске и задержании, как отвечать банку по 115-ФЗ, как устроен НДС и где заканчиваются возможности ИИ-помощников. Пишут адвокаты и юристы агентства.</p>
  </div>
</section>
<section class="band band-light"><div class="wrap">
  <div class="author-block">
    <img src="{root}assets/img/chinokalov.jpg" alt="" width="56" height="56">
    <div>
      <h2><a href="{root}advokaty/chinokalov.html">Максим Чинокалов</a></h2>
      <p class="meta">Адвокат по уголовным делам, {len(ch)} материалов</p>
    </div>
  </div>
{article_rows(root, ch, show_author=False)}

  <div class="author-block">
    <span class="avatar" aria-hidden="true">ЭБ</span>
    <div>
      <h2><a href="{root}yuristy/bakoyan.html">Эдгар Бакоян</a></h2>
      <p class="meta">Юрист, налоговый консультант, {len(bk)} материалов</p>
    </div>
  </div>
{article_rows(root, bk, show_author=False)}
</div></section>'''
    write('materialy/index.html', shell(root=root, path='/materialy/', title='Материалы — статьи адвокатов и юристов Capital Defence',
        description='Практические материалы команды Capital Defence: обыск, задержание, допрос, блокировка счетов по 115-ФЗ, НДС и налоговые разрывы.',
        body=body, active='materialy', crumbs=[('Главная', '/'), ('Материалы', '/materialy/')]))

# ---------------------------------------------------------------------------
# Документы
# ---------------------------------------------------------------------------
def legal_page(path, title, description, h1, meta, note, content):
    root = '../'
    body = f'''<section class="page-head band-dark">
  <div class="wrap">
    <h1>{h1}</h1>
    {f'<p class="meta" style="margin-top:16px;">{meta}</p>' if meta else ''}
  </div>
</section>
<section class="band-light"><div class="wrap legal">
  {f'<div class="draft-note">{note}</div>' if note else ''}
{content}
  <a class="back-link" href="{root}">← На главную</a>
</div></section>'''
    write(path.lstrip('/'), shell(root=root, path=path, title=title, description=description, body=body,
          crumbs=[('Главная', '/'), (h1, path)]))

def documents():
    F = lambda t: f'<span class="fill">{t}</span>'
    legal_page('/dokumenty/politika-obrabotki-pd.html', 'Политика обработки персональных данных | Capital Defence',
        'Политика в отношении обработки персональных данных Capital Defence в соответствии со ст. 18.1 Федерального закона № 152-ФЗ «О персональных данных».',
        'Политика в отношении обработки персональных данных', f'Редакция от {F("[дата утверждения]")}',
        'Документ находится на утверждении: поля в квадратных скобках будут заполнены реквизитами Оператора.',
        f'''
  <h2>1. Общие положения</h2>
  <p>Настоящая Политика в отношении обработки персональных данных (далее — «Политика») разработана в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных» (далее — «Закон о персональных данных») и действует в отношении всех персональных данных, которые Оператор может получить от субъекта персональных данных — пользователя сайта capitaldefence.ru.</p>
  <p>Оператором персональных данных является {F("[полное наименование: ООО «…» / ИП Фамилия Имя Отчество]")}, ОГРН/ОГРНИП {F("[номер]")}, ИНН {F("[номер]")}, адрес: г. Пенза, просп. Победы, 97 (далее — «Оператор»).</p>

  <h2>2. Основные понятия</h2>
  <ul>
    <li><strong>Персональные данные</strong> — любая информация, относящаяся прямо или косвенно к определённому или определяемому физическому лицу (субъекту персональных данных).</li>
    <li><strong>Обработка персональных данных</strong> — любое действие (операция) или совокупность действий (операций), совершаемых с использованием средств автоматизации или без их использования с персональными данными, включая сбор, запись, систематизацию, накопление, хранение, уточнение, извлечение, использование, передачу, обезличивание, блокирование, удаление, уничтожение персональных данных.</li>
    <li><strong>Сайт</strong> — совокупность информации, текстов, графических элементов, дизайна, изображений, фото и видеоматериалов, размещённых по адресу capitaldefence.ru.</li>
  </ul>

  <h2>3. Правовые основания обработки персональных данных</h2>
  <p>Оператор обрабатывает персональные данные пользователя на основании его согласия на обработку персональных данных, направленного через форму обратной связи или мессенджер, а также в соответствии со ст. 6 Закона о персональных данных — в целях исполнения договора, стороной которого либо выгодоприобретателем по которому является субъект персональных данных.</p>

  <h2>4. Категории и объём обрабатываемых персональных данных</h2>
  <p>Оператор обрабатывает следующие персональные данные пользователей сайта, оставивших заявку через форму обратной связи или написавших в Telegram:</p>
  <ul>
    <li>имя;</li>
    <li>номер телефона и/или имя пользователя (username) в Telegram;</li>
    <li>содержание обращения — краткое описание ситуации, которое пользователь указывает добровольно.</li>
  </ul>
  <p>Сайт не собирает персональные данные автоматически без действия пользователя (обращение через форму или в мессенджер).</p>

  <h2>5. Цели обработки персональных данных</h2>
  <ul>
    <li>связь с пользователем, включая направление уведомлений и ответ на обращение;</li>
    <li>оказание юридических и консультационных услуг по запросу пользователя;</li>
    <li>заключение и исполнение соглашения об оказании юридической помощи.</li>
  </ul>

  <h2>6. Порядок и условия обработки персональных данных</h2>
  <p>Обработка персональных данных осуществляется с согласия субъекта персональных данных на обработку его персональных данных. Оператор вправе поручить обработку персональных данных третьим лицам (например, оператору связи, мессенджеру) с согласия субъекта персональных данных, если иное не предусмотрено законом, на основании заключаемого с этими лицами договора.</p>
  <p>Персональные данные обрабатываются в течение срока, необходимого для достижения целей обработки, если иной срок хранения не установлен законом или соглашением с субъектом персональных данных.</p>

  <h2>7. Права субъекта персональных данных</h2>
  <p>Субъект персональных данных имеет право:</p>
  <ul>
    <li>получать информацию, касающуюся обработки его персональных данных;</li>
    <li>требовать уточнения, блокирования или уничтожения персональных данных в случае, если они являются неполными, устаревшими, неточными, незаконно полученными или не являются необходимыми для заявленной цели обработки;</li>
    <li>отозвать согласие на обработку персональных данных;</li>
    <li>обжаловать действия или бездействие Оператора в уполномоченный орган по защите прав субъектов персональных данных (Роскомнадзор) или в судебном порядке.</li>
  </ul>
  <p>Для реализации указанных прав пользователь может обратиться к Оператору по адресу электронной почты {F("[email для обращений по ПД]")} или по телефону, указанному в разделе «Контакты».</p>

  <h2>8. Меры по обеспечению безопасности персональных данных</h2>
  <p>Оператор принимает необходимые организационные и технические меры для защиты персональных данных пользователя от неправомерного или случайного доступа, уничтожения, изменения, блокирования, копирования, распространения, а также от иных неправомерных действий третьих лиц.</p>

  <h2>9. Заключительные положения</h2>
  <p>Пользователь может получить разъяснения по интересующим вопросам, касающимся обработки его персональных данных, обратившись к Оператору по контактам, указанным на сайте.</p>
  <p>Оператор вправе вносить изменения в настоящую Политику. Действующая редакция всегда размещена на данной странице.</p>
  <p class="meta" style="margin-top:30px;">Ответственный за организацию обработки персональных данных: {F("[ФИО, должность]")}.</p>''')

    legal_page('/dokumenty/polozhenie-o-pd.html', 'Положение о защите персональных данных | Capital Defence',
        'Положение о защите персональных данных Capital Defence — внутренний порядок обработки и защиты персональных данных в соответствии с 152-ФЗ.',
        'Положение о защите персональных данных', f'Утверждено {F("[ФИО / должность руководителя]")}, редакция от {F("[дата]")}',
        'Внутренний регламент Оператора. Документ находится на утверждении: поля в квадратных скобках будут заполнены реквизитами.',
        f'''
  <h2>1. Общие положения</h2>
  <p>Настоящее Положение определяет порядок работы с персональными данными у Оператора — {F("[полное наименование]")} — и устанавливает процедуры, направленные на выявление и предотвращение нарушений законодательства Российской Федерации в сфере обработки персональных данных.</p>
  <p>Положение разработано в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных», постановлениями Правительства РФ и иными нормативными актами в области защиты персональных данных.</p>

  <h2>2. Цель и задачи защиты персональных данных</h2>
  <p>Целью настоящего Положения является обеспечение защиты прав и свобод субъектов персональных данных при обработке их персональных данных, в том числе защиты прав на неприкосновенность частной жизни, личную и семейную тайну.</p>
  <ul>
    <li>предотвращение несанкционированного доступа к персональным данным;</li>
    <li>недопущение неправомерных сбора, хранения, использования, распространения персональных данных;</li>
    <li>соблюдение прав субъектов персональных данных.</li>
  </ul>

  <h2>3. Перечень персональных данных, подлежащих защите</h2>
  <p>Защите подлежат персональные данные клиентов (доверителей) и пользователей сайта, которые Оператор получает в рамках оказания юридических услуг и обработки обращений через сайт и мессенджеры: фамилия, имя, отчество, контактный телефон, адрес электронной почты, username в Telegram, а также сведения, содержащиеся в документах, переданных Оператору в рамках оказания услуг.</p>

  <h2>4. Лица, допущенные к обработке персональных данных</h2>
  <p>К обработке персональных данных допускаются сотрудники Оператора, чьи должностные обязанности требуют доступа к персональным данным для исполнения трудовых функций, и которые ознакомлены с настоящим Положением и приняли на себя обязательства по соблюдению конфиденциальности персональных данных.</p>
  <p>Ответственный за организацию обработки персональных данных: {F("[ФИО, должность]")}.</p>

  <h2>5. Условия обработки и передачи персональных данных</h2>
  <p>Передача персональных данных третьим лицам допускается только в случаях, предусмотренных законодательством, с согласия субъекта персональных данных, либо в рамках исполнения поручения, данного Оператору субъектом персональных данных.</p>
  <p>Трансграничная передача персональных данных не осуществляется, за исключением случаев, прямо согласованных с субъектом персональных данных.</p>

  <h2>6. Меры по обеспечению безопасности</h2>
  <ul>
    <li>ограничение доступа к персональным данным по кругу лиц;</li>
    <li>использование средств защиты информации при хранении данных в электронном виде;</li>
    <li>хранение бумажных носителей с персональными данными в местах, исключающих доступ посторонних лиц;</li>
    <li>контроль за соблюдением настоящего Положения.</li>
  </ul>

  <h2>7. Права субъекта персональных данных</h2>
  <p>Субъект персональных данных вправе получать сведения об обработке своих персональных данных, требовать уточнения, блокирования или уничтожения данных, отозвать согласие на обработку, а также обжаловать действия Оператора в Роскомнадзор или в судебном порядке.</p>

  <h2>8. Ответственность</h2>
  <p>Лица, виновные в нарушении норм, регулирующих обработку и защиту персональных данных, несут дисциплинарную, административную, гражданско-правовую или уголовную ответственность в порядке, установленном законодательством Российской Федерации.</p>''')

    legal_page('/dokumenty/soglasie-na-obrabotku-pd.html', 'Согласие на обработку персональных данных | Capital Defence',
        'Текст согласия на обработку персональных данных при обращении через сайт Capital Defence.',
        'Согласие на обработку персональных данных', None,
        'С этим текстом пользователь соглашается, отправляя форму на сайте, либо начиная переписку в Telegram или разговор по телефону после ознакомления с документом. Поля в квадратных скобках будут заполнены реквизитами Оператора.',
        f'''
  <p>Я, пользователь сайта capitaldefence.ru, действуя свободно, своей волей и в своём интересе, а также подтверждая свою дееспособность, даю своё согласие {F("[полное наименование Оператора: ООО «…» / ИП Фамилия Имя Отчество]")}, ОГРН/ОГРНИП {F("[номер]")}, ИНН {F("[номер]")}, расположенному по адресу: г. Пенза, просп. Победы, 97 (далее — «Оператор»), на обработку моих персональных данных, а именно:</p>
  <ul>
    <li>фамилия, имя, отчество;</li>
    <li>номер контактного телефона и/или username в мессенджере Telegram;</li>
    <li>содержание обращения, указанное мной в форме или сообщении.</li>
  </ul>

  <h2>Цель обработки персональных данных</h2>
  <p>Обработка персональных данных осуществляется в целях связи со мной, предоставления консультации, оказания юридических услуг по моему запросу, подготовки и заключения соглашения об оказании юридической помощи.</p>

  <h2>Перечень действий с персональными данными</h2>
  <p>Согласие даётся на совершение следующих действий с персональными данными: сбор, запись, систематизация, накопление, хранение, уточнение (обновление, изменение), извлечение, использование, передача (предоставление, доступ), блокирование, удаление, уничтожение — как с использованием средств автоматизации, так и без их использования.</p>

  <h2>Срок действия согласия</h2>
  <p>Настоящее согласие действует с момента его предоставления и до момента его отзыва в письменной форме либо до достижения целей обработки персональных данных.</p>

  <h2>Порядок отзыва согласия</h2>
  <p>Я проинформирован(-а), что могу отозвать настоящее согласие, направив письменное уведомление Оператору на адрес электронной почты {F("[email для обращений по ПД]")} или на почтовый адрес Оператора, указанный выше.</p>

  <p style="margin-top:30px;">Подтверждая согласие, я ознакомлен(-а) с <a href="politika-obrabotki-pd.html">Политикой в отношении обработки персональных данных</a> Оператора.</p>''')

# ---------------------------------------------------------------------------
def sitemap():
    today = '2026-10-13'
    urls = ['/', '/uslugi/', '/advokaty/', '/advokaty/simkin.html', '/advokaty/chinokalov.html', '/advokaty/truevtsev.html',
            '/yuristy/', '/yuristy/bakoyan.html', '/yuristy/shitov.html', '/materialy/'] + \
           [f'/materialy/{a["slug"]}.html' for a in ARTICLES] + \
           ['/dokumenty/politika-obrabotki-pd.html', '/dokumenty/polozhenie-o-pd.html', '/dokumenty/soglasie-na-obrabotku-pd.html']
    body = '\n'.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>' for u in urls)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '\n</urlset>\n')

if __name__ == '__main__':
    # статьи читаем из старых файлов до перезаписи; кэшируем, чтобы повторная сборка работала
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'old_articles.json')
    if os.path.exists(cache):
        bodies = json.load(open(cache, encoding='utf-8'))
    else:
        bodies = {a['slug']: extract_old_article(a['slug']) for a in ARTICLES}
        json.dump(bodies, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
    extract_old_article = lambda slug: bodies[slug]  # noqa
    home(); uslugi_index(); advokaty_index(); yuristy_index(); profiles(); materialy_index(); documents(); sitemap()
    for a in ARTICLES:
        article_page(a)
