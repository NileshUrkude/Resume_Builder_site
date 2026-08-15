(function () {
  function showToast(message) {
    var host = document.getElementById('toast-host');
    if (!host) return;
    host.innerHTML = '';
    var el = document.createElement('div');
    el.className = 'toast';
    el.setAttribute('role', 'status');
    el.textContent = message;
    host.appendChild(el);
    setTimeout(function () {
      if (el.parentNode === host) host.removeChild(el);
    }, 2800);
  }

  window.showToast = showToast;

  window.copyShareLink = function () {
    var input = document.getElementById('share-url-input');
    if (!input) return;
    var btn = document.querySelector('.share-copy-btn');
    navigator.clipboard.writeText(input.value).then(function () {
      if (btn) {
        btn.innerHTML = '<i class="bi bi-check2" aria-hidden="true"></i>';
        btn.setAttribute('aria-label', 'Copied');
        setTimeout(function () {
          btn.innerHTML = '<i class="bi bi-clipboard" aria-hidden="true"></i>';
          btn.setAttribute('aria-label', 'Copy share link');
        }, 2000);
      }
      showToast('Link copied');
    }).catch(function () {
      showToast('Could not copy link');
    });
  };

  document.addEventListener('click', function (e) {
    var link = e.target.closest('[data-busy-download]');
    if (!link) return;
    link.classList.add('btn-busy');
    link.setAttribute('aria-busy', 'true');
    setTimeout(function () {
      link.classList.remove('btn-busy');
      link.removeAttribute('aria-busy');
    }, 4000);
  });

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || form.tagName !== 'FORM') return;
    var btn = form.querySelector('[data-busy-submit]');
    if (!btn) return;
    btn.classList.add('btn-busy');
    btn.setAttribute('aria-busy', 'true');
    btn.disabled = true;
  });
})();
