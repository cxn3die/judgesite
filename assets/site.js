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
})();
