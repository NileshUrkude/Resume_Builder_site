(function () {
  function getFormRow(btn) {
    return btn.closest('[data-form-row]');
  }

  function getContainer(prefix) {
    return document.getElementById(prefix + '-container');
  }

  function reindexFormset(prefix) {
    var container = getContainer(prefix);
    var total = document.querySelector('[name="' + prefix + '-TOTAL_FORMS"]');
    if (!container || !total) return;
    var rows = container.querySelectorAll('[data-form-row]');
    rows.forEach(function (row, idx) {
      row.querySelectorAll('input, select, textarea, label').forEach(function (el) {
        if (el.name) el.name = el.name.replace(new RegExp('^' + prefix + '-\\d+-'), prefix + '-' + idx + '-');
        if (el.id) el.id = el.id.replace(new RegExp('^id_' + prefix + '-\\d+-'), 'id_' + prefix + '-' + idx + '-');
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(new RegExp('^id_' + prefix + '-\\d+-'), 'id_' + prefix + '-' + idx + '-');
      });
    });
    total.value = rows.length;
  }

  window.addForm = function (prefix) {
    var total = document.querySelector('[name="' + prefix + '-TOTAL_FORMS"]');
    var empty = document.getElementById(prefix + '-empty');
    var container = getContainer(prefix);
    if (!total || !empty || !container) return;
    var count = parseInt(total.value, 10);
    var html = empty.innerHTML.replace(/__prefix__/g, count);
    var wrap = document.createElement('div');
    wrap.className = 'form-row rounded-lg border border-slate-100 bg-slate-50/50 p-4 dark:border-slate-800 dark:bg-slate-900/30';
    wrap.setAttribute('data-form-row', '');
    wrap.innerHTML = html + '<button type="button" class="mt-3 text-xs font-medium text-rose-600 hover:text-rose-700" data-remove-row><i class="bi bi-trash"></i> Remove</button>';
    container.appendChild(wrap);
    reindexFormset(prefix);
  };

  document.addEventListener('click', function (e) {
    var addBtn = e.target.closest('[data-add-form]');
    if (addBtn) {
      window.addForm(addBtn.getAttribute('data-add-form'));
      return;
    }
    var removeBtn = e.target.closest('[data-remove-row]');
    if (removeBtn) {
      var row = getFormRow(removeBtn);
      var section = removeBtn.closest('[data-section]');
      var prefix = section ? section.getAttribute('data-section') : '';
      var container = prefix ? getContainer(prefix) : null;
      if (row && container && container.querySelectorAll('[data-form-row]').length > 1) {
        row.remove();
        reindexFormset(prefix);
      }
    }
  });

  var isPublic = document.getElementById('id_is_public');
  var shareField = document.getElementById('share-password-field');
  function toggleSharePassword() {
    if (!shareField) return;
    shareField.classList.toggle('hidden', !isPublic || !isPublic.checked);
  }
  if (isPublic) {
    isPublic.addEventListener('change', toggleSharePassword);
    toggleSharePassword();
  }

  var resumeId = window.RESUME_ID;
  var previewTemplate = window.PREVIEW_URL_TEMPLATE;

  function loadPreview() {
    if (!resumeId || !previewTemplate) return;
    var sel = document.getElementById('preview-template');
    var box = document.getElementById('live-preview');
    if (!sel || !box) return;
    var url = previewTemplate.replace('__tpl__', sel.value);
    fetch(url)
      .then(function (r) { return r.text(); })
      .then(function (html) {
        // Render preview in an iframe so full HTML (with <head>/<style>) works correctly
        box.innerHTML = '';
        var iframe = document.createElement('iframe');
        iframe.setAttribute('aria-label', 'Resume preview');
        iframe.style.width = '210mm';
        iframe.style.height = '297mm';
        iframe.style.border = '1px solid #e5e7eb';
        iframe.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
        iframe.style.display = 'block';
        iframe.style.margin = '12px auto';
        iframe.srcdoc = html;
        box.appendChild(iframe);
      })
      .catch(function () { box.innerHTML = '<p class="p-4 text-xs text-rose-500">Preview unavailable.</p>'; });
  }

  var previewSel = document.getElementById('preview-template');
  if (previewSel) previewSel.addEventListener('change', loadPreview);
  if (resumeId) loadPreview();

  var fab = document.getElementById('mobile-preview-toggle');
  var panel = document.getElementById('preview-panel');
  if (fab && panel) {
    fab.addEventListener('click', function () {
      panel.classList.toggle('preview-panel-open');
      fab.classList.toggle('preview-fab-active');
      if (panel.classList.contains('preview-panel-open')) {
        panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }
})();
