(function () {
  'use strict';

  /* Новая страница открывается с начала ------------------------------
     Без этого при показе сайта внутри фрейма (превью, встраивание)
     внешняя прокрутка остаётся на месте и страница открывается «посередине».
     Не трогаем переходы по якорю, возврат «назад» и перезагрузку. */
  (function () {
    if (location.hash) return;
    var framed = false;
    try { framed = window.top !== window.self; } catch (e) { framed = true; }
    if (!framed) return;
    var nav = window.performance && performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
    if (nav && nav.type === 'back_forward') return;
    function toTop() {
      try { window.scrollTo(0, 0); } catch (e) {}
      try { var t = document.getElementById('top'); if (t) t.scrollIntoView({ block: 'start' }); } catch (e) {}
    }
    toTop();
    // Переход по якорю браузер прокручивает сквозь границы фреймов: «#top» указывает на шапку.
    try { if (!location.hash) location.replace(location.pathname + location.search + '#top'); } catch (e) {}
    window.addEventListener('load', function () { toTop(); setTimeout(toTop, 300); });
  })();

  /* Мобильное меню ------------------------------------------------- */
  var body = document.body;
  var btn = document.querySelector('.menu-btn');
  var menu = document.querySelector('.mobile-menu');

  function closeMenu() {
    body.classList.remove('menu-open');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }
  function toggleMenu() {
    var open = !body.classList.contains('menu-open');
    body.classList.toggle('menu-open', open);
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (btn && menu) {
    btn.addEventListener('click', toggleMenu);
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 980) closeMenu();
    });
  }

  /* Форма заявки → Telegram ----------------------------------------- */
  var form = document.getElementById('requestForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
        if (form.reportValidity) form.reportValidity();
        return;
      }
      var name = (document.getElementById('f-name').value || '').trim();
      var phone = (document.getElementById('f-phone').value || '').trim();
      var message = (document.getElementById('f-message').value || '').trim();
      var text = 'Заявка с сайта.\nИмя: ' + name + '\nКонтакт: ' + phone + (message ? '\nСитуация: ' + message : '');
      var url = 'https://t.me/Capital_Defence?text=' + encodeURIComponent(text);
      var win = window.open(url, '_blank', 'noopener');
      var fallback = form.querySelector('.form-done a');
      if (fallback) fallback.href = url;
      form.classList.add('is-done');
      if (!win) {
        // Браузер заблокировал окно — покажем ссылку, чтобы открыть вручную
        var done = form.querySelector('.form-done');
        if (done) done.classList.add('blocked');
      }
    });
  }

  /* Лента со статьями законов на странице услуг ----------------------
     Для каждой секции с data-laws рисуем волну (SVG path) на всю секцию
     и пускаем по ней номера статей разного размера. Текст медленно течёт
     вдоль волны; за экраном и при prefers-reduced-motion стоит на месте. */
  (function () {
    var secs = document.querySelectorAll('.svc[data-laws]');
    if (!secs.length || !window.SVGPathElement || !('getTotalLength' in SVGPathElement.prototype)) return;
    var NS = 'http://www.w3.org/2000/svg', XL = 'http://www.w3.org/1999/xlink';
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var SIZES = [40, 72, 48, 96, 56, 84, 44, 64];   // px, по кругу: крупные и мелкие чередуются
    var SPEED = 24;                                  // px в секунду вдоль волны
    var ribbons = [];

    // Плавная кривая через точки (Catmull-Rom → кубические Безье)
    function spline(pts) {
      var d = 'M' + pts[0][0] + ',' + pts[0][1];
      for (var i = 0; i < pts.length - 1; i++) {
        var p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
        var c = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]];
        d += ' C' + c.map(function (n) { return Math.round(n * 10) / 10; }).join(',');
      }
      return d;
    }

    Array.prototype.forEach.call(secs, function (sec, idx) {
      var svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('class', 'law-ribbon'); svg.setAttribute('aria-hidden', 'true'); svg.setAttribute('focusable', 'false');
      var path = document.createElementNS(NS, 'path'), pid = 'law-path-' + idx;
      path.setAttribute('id', pid); path.setAttribute('fill', 'none');
      var text = document.createElementNS(NS, 'text'), tp = document.createElementNS(NS, 'textPath');
      tp.setAttributeNS(XL, 'xlink:href', '#' + pid); tp.setAttribute('href', '#' + pid);
      text.appendChild(tp); svg.appendChild(path); svg.appendChild(text);
      sec.insertBefore(svg, sec.firstChild);
      ribbons.push({ sec: sec, svg: svg, path: path, tp: tp, laws: sec.getAttribute('data-laws').split('|'), unit: 0, offset: 0, w: 0, h: 0, visible: false });
    });

    function build(r) {
      var w = r.sec.clientWidth, h = r.sec.clientHeight;
      if (!w || !h) return;
      r.w = w; r.h = h;
      r.svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
      var tp = r.tp;
      while (tp.firstChild) tp.removeChild(tp.firstChild);
      if (w <= 860) {
        // Телефон и планшет: колонки стоят друг под другом, лента не нужна
        r.unit = 0;
        return;
      }
      // Волна: из-под левого блока вверх, над списком вниз, у правого края снова вверх
      var pts = [[-160, h * 0.8], [w * 0.2, h * 0.56], [w * 0.44, h * 0.12], [w * 0.62, h * 0.5], [w * 0.76, h * 0.88], [w * 0.9, h * 0.6], [w + 160, h * 0.26]];
      r.path.setAttribute('d', spline(pts));
      var len = r.path.getTotalLength();
      var scale = Math.max(0.7, Math.min(1, w / 1200));
      function addUnit() {
        r.laws.forEach(function (law, i) {
          var ts = document.createElementNS(NS, 'tspan');
          ts.setAttribute('font-size', Math.max(11, Math.round(SIZES[i % SIZES.length] * scale)));
          ts.textContent = law + '  ';
          tp.appendChild(ts);
        });
      }
      tp.setAttribute('startOffset', 0);
      addUnit();
      r.unit = tp.getComputedTextLength();
      if (!r.unit) return;
      for (var k = Math.ceil(len / r.unit) + 1; k > 1; k--) addUnit();
      if (r.offset < -r.unit || r.offset >= 0) r.offset = -r.unit;
      tp.setAttribute('startOffset', r.offset);
    }

    var last = 0, raf = 0;
    function tick(ts) {
      raf = 0;
      var dt = last ? Math.min((ts - last) / 1000, 0.1) : 0;
      last = ts;
      var any = false;
      ribbons.forEach(function (r) {
        if (!r.visible || !r.unit) return;
        any = true;
        r.offset += SPEED * dt;
        if (r.offset >= 0) r.offset -= r.unit;
        r.tp.setAttribute('startOffset', r.offset);
      });
      if (any) raf = requestAnimationFrame(tick); else last = 0;
    }
    function kick() { if (!raf && !reduce) raf = requestAnimationFrame(tick); }

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          ribbons.forEach(function (r) { if (r.sec === e.target) r.visible = e.isIntersecting; });
        });
        kick();
      }, { rootMargin: '120px' });
      ribbons.forEach(function (r) { io.observe(r.sec); });
    } else {
      ribbons.forEach(function (r) { r.visible = true; });
    }

    function buildAll() { ribbons.forEach(build); kick(); }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(buildAll); else buildAll();
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        ribbons.forEach(function (r) { if (r.sec.clientWidth !== r.w || r.sec.clientHeight !== r.h) build(r); });
      }, 150);
    });
  })();
})();
