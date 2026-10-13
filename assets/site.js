(function () {
  'use strict';

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
