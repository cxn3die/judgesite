# -*- coding: utf-8 -*-
"""Выгружает все тексты сайта в один Markdown-файл, из которого pandoc делает Word.
Запуск: python3 -I tools/export_texts.py /home/user/judgesite out.md
Порядок: шапка и подвал, главная, услуги, адвокаты, юристы, материалы, статьи, документы.
Правки из возвращённого файла переносятся в tools/build.py вручную или скриптом.
"""
import os, re, sys, html
from html.parser import HTMLParser

ROOT, OUT = sys.argv[1], sys.argv[2]

SKIP_TAGS = {'script', 'style', 'svg', 'noscript', 'template'}
SKIP_CLASSES = {'crumbs', 'article-nav', 'back-link', 'cnt', 'article-list', 'mobile-menu',
                'menu-btn', 'skip', 'portrait', 'hero-emblem', 'monogram', 'avatar', 'nav'}
BLOCK = {'h1': '## ', 'h2': '### ', 'h3': '#### ', 'h4': '##### ', 'p': '', 'li': '- ', 'dt': '', 'dd': '',
         'blockquote': '> ', 'figcaption': '', 'label': '', 'legend': '', 'th': '', 'td': ''}
ROLE = {'kicker': 'Подпись над заголовком: ', 'form-note': 'Примечание под формой: ', 'hero-note': '',
        'profile-registry': '', 'form-done': 'Сообщение после отправки: ', 'brand-sub': 'Подпись под названием: ',
        'brand-name': 'Название: ', 'text-link': 'Ссылка: ', 'btn': 'Кнопка: '}


BR = ' '   # метка переноса строки внутри абзаца (<br>)


def esc(s):
    s = re.sub(r'[ \t\r\n]+', ' ', s).strip()
    s = s.replace('\\', '\\\\')
    for ch in '*_`[]<>|':
        s = s.replace(ch, '\\' + ch)
    s = re.sub(r'^(#+|-|\d+\.)\s', lambda m: '\\' + m.group(0), s)
    s = re.sub(r'\s+([,.;:!?)])', r'\1', s)
    s = re.sub(r'\s*' + BR + r'\s*', '\\\\\n', s).strip('\\\n ')
    # жирный и курсив: метки ставятся до экранирования, чтобы звёздочки не экранировались
    s = re.sub(r'\x01\s*\x01', '', s); s = re.sub(r'\x02\s*\x02', '', s)
    s = re.sub(r'\x01\s*(.*?)\s*\x01', r'**\1**', s); s = re.sub(r'\x02\s*(.*?)\s*\x02', r'*\1*', s)
    return s


class Extract(HTMLParser):
    """Собирает текст блочных элементов внутри заданного контейнера."""
    def __init__(self, start_tag, start_attr=None):
        super().__init__(convert_charrefs=True)
        self.start_tag, self.start_attr = start_tag, start_attr
        self.inside = 0; self.depth = 0; self.skip = 0
        self.lines = []; self.cur = None; self.role = ''; self.inline = []
        self.in_table = False; self.row = None; self.rows = []
        self.list_depth = 0

    def classes(self, attrs):
        return set((dict(attrs).get('class') or '').split())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = self.classes(attrs)
        if not self.inside:
            if tag == self.start_tag and (self.start_attr is None or self.start_attr in cls or a.get('id') == self.start_attr):
                self.inside = 1; self.depth = 1
            return
        self.depth += 1
        if self.skip:
            self.skip += 1; return
        if tag in SKIP_TAGS or cls & SKIP_CLASSES:
            self.skip = 1; return
        if tag == 'table':
            self.in_table = True; self.rows = []
        elif tag == 'tr':
            self.row = []
        elif tag in ('ul', 'ol'):
            self.list_depth += 1
        elif tag in BLOCK or tag == 'button':
            self.flush()
            self.cur = tag if tag != 'button' else 'p'
            self.role = ''
            for c in cls:
                if c in ROLE: self.role = ROLE[c]
            if tag == 'button' or 'btn' in cls: self.role = 'Кнопка: '
            self.inline = []
            if tag == 'li' and self.list_depth > 1: self.inline.append('    ' * 0)
        elif tag == 'a' and self.cur is None:
            # ссылка вне абзаца (кнопка в шапке, «Все материалы»)
            self.flush(); self.cur = 'p'; self.inline = []
            self.role = 'Кнопка: ' if 'btn' in cls else ('Ссылка: ' if 'text-link' in cls else '')
            self._a_block = True
        elif tag in ('strong', 'b') and self.cur: self.inline.append('\x01')
        elif tag in ('em', 'i') and self.cur: self.inline.append('\x02')
        elif tag == 'br' and self.cur: self.inline.append(BR)
        elif tag == 'span' and self.cur: self.inline.append(' ')
        elif tag in ('input', 'textarea') and a.get('placeholder'):
            self.flush(); self.lines.append('Подсказка в поле: ' + esc(a['placeholder'])); self.lines.append('')
        if tag == 'span' and 'k' in cls and self.cur: self._k = True
        if tag == 'span' and 'v' in cls and self.cur and getattr(self, '_k', False):
            self.inline.append(': '); self._k = False

    def handle_endtag(self, tag):
        if not self.inside: return
        if self.skip:
            self.skip -= 1; self.depth -= 1
            return
        if tag in ('strong', 'b') and self.cur: self.inline.append('\x01')
        elif tag in ('em', 'i') and self.cur: self.inline.append('\x02')
        elif tag == 'span' and self.cur: self.inline.append(' ')
        elif tag in BLOCK or tag == 'button' or (tag == 'a' and getattr(self, '_a_block', False)):
            if tag == 'a': self._a_block = False
            self.flush()
        elif tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None
        elif tag == 'table':
            self.in_table = False
            if self.rows:
                w = max(len(r) for r in self.rows)
                rows = [r + [''] * (w - len(r)) for r in self.rows]
                # ширина колонок пропорциональна длине текста в них (pandoc читает её из числа дефисов)
                widths = [max(3, min(40, max(len(r[i]) for r in rows) // 4)) for i in range(w)]
                if self.lines and self.lines[-1] != '': self.lines.append('')
                self.lines.append('| ' + ' | '.join(rows[0]) + ' |')
                self.lines.append('|' + '|'.join('-' * n for n in widths) + '|')
                for r in rows[1:]: self.lines.append('| ' + ' | '.join(r) + ' |')
                self.lines.append('')
        elif tag in ('ul', 'ol'):
            self.list_depth -= 1
        self.depth -= 1
        if self.depth == 0: self.inside = 0

    def handle_data(self, data):
        if self.inside and not self.skip and self.cur is not None:
            self.inline.append(data)

    def flush(self):
        if self.cur is None: return
        clean = esc(''.join(self.inline))
        if clean:
            if self.cur in ('th', 'td') and self.row is not None:
                self.row.append(clean.replace('|', '\\|'))
            else:
                prefix = BLOCK.get(self.cur, '')
                if self.cur == 'li' and self.list_depth > 1: prefix = '    - '
                if self.cur != 'li' and self.lines and self.lines[-1] != '': self.lines.append('')
                self.lines.append(prefix + self.role + clean)
                if self.cur != 'li': self.lines.append('')
        self.cur = None; self.inline = []; self.role = ''


def page_meta(src):
    t = re.search(r'<title>(.*?)</title>', src, re.S); d = re.search(r'<meta name="description" content="([^"]*)"', src)
    return html.unescape(t.group(1).strip() if t else ''), html.unescape(d.group(1) if d else '')


def extract(src, tag='main', attr='main'):
    p = Extract(tag, attr); p.feed(src); p.flush()
    out = []
    for ln in p.lines:
        if ln == '' and out and out[-1] == '': continue
        out.append(ln)
    return '\n'.join(out).strip() + '\n'


def read(rel):
    return open(os.path.join(ROOT, rel), encoding='utf-8').read()


def h1_of(src):
    m = re.search(r'<h1>(.*?)</h1>', src, re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''


def section(title, rel, src, kind=''):
    t, d = page_meta(src)
    body = [f'# {title}', '', f'Адрес страницы: {rel if rel != "index.html" else "главная"}', '',
            f'Заголовок вкладки браузера: {esc(t)}', '', f'Описание для поисковиков: {esc(d)}', '']
    if kind: body += [kind, '']
    return '\n'.join(body) + '\n' + extract(src)


def listing(folder):
    files = sorted(f for f in os.listdir(os.path.join(ROOT, folder)) if f.endswith('.html') and f != 'index.html')
    # страницы-переадресации со старых адресов текста не содержат
    return [folder + '/' + f for f in files if 'http-equiv="refresh"' not in read(folder + '/' + f)]


parts = []
parts.append('''# Тексты сайта Capital Defence

Это все тексты сайта в том порядке, в котором они идут на страницах. Как править:

- Правьте текст прямо в документе. Удобно включить «Рецензирование → Исправления», тогда видно, что менялось.
- Заголовки «Страница: …» и строки «Адрес страницы», «Заголовок вкладки», «Описание для поисковиков», «Кнопка:», «Подпись над заголовком:» помогают понять, где текст стоит на сайте. Сами эти пометки менять не нужно, меняйте текст после двоеточия.
- Телефон, адрес, часы работы и подписи в шапке и подвале одинаковы на всех страницах, они собраны в первом разделе. Поменяйте один раз там.
- Названия услуг на главной повторяют страницу «Услуги». Правьте их в разделе «Услуги», на главную они подтянутся.
- Статьи и документы по персональным данным вынесены в конец. В документах поля в квадратных скобках нужно заполнить реквизитами.
- Когда закончите, верните файл. Правки перенесём на сайт.
''')

home = read('index.html')
hdr = extract(home, 'header', 'site-header'); ftr = extract(home, 'footer', 'footer')
parts.append('# Шапка и подвал (одинаковые на всех страницах)\n\n### Шапка\n\n' + hdr + '\n### Подвал\n\n' + ftr)
parts.append(section('Страница: Главная', 'index.html', home))
parts.append(section('Страница: Услуги', 'uslugi/', read('uslugi/index.html')))
parts.append(section('Страница: Команда', 'komanda/', read('komanda/index.html')))
for rel in listing('komanda'):
    s = read(rel); parts.append(section(f'Страница: {h1_of(s)}', rel, s))
parts.append(section('Страница: Материалы', 'materialy/', read('materialy/index.html'),
                     'Список статей на этой странице собирается из самих статей: названия правьте в разделе каждой статьи ниже.'))
for rel in listing('materialy'):
    s = read(rel); parts.append(section(f'Статья: {h1_of(s)}', rel, s))
for rel in listing('dokumenty'):
    s = read(rel); parts.append(section(f'Документ: {h1_of(s)}', rel, s))

open(OUT, 'w', encoding='utf-8').write('\n\n'.join(parts))
print('sections:', len(parts), '| lines:', sum(p.count('\n') for p in parts))
