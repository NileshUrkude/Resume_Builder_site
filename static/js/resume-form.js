(function () {
  function getCsrf() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }

  function getFormRow(btn) {
    return btn.closest('[data-form-row]');
  }

  function getContainer(prefix) {
    return document.getElementById(prefix + '-container');
  }

  function updateTotalForms(prefix) {
    const total = document.querySelector('[name="' + prefix + '-TOTAL_FORMS"]');
    const container = getContainer(prefix);
    if (total && container) {
      total.value = container.querySelectorAll('[data-form-row]').length;
    }
  }

  window.addForm = function (prefix) {
    const total = document.querySelector('[name="' + prefix + '-TOTAL_FORMS"]');
    const empty = document.getElementById(prefix + '-empty');
    const container = getContainer(prefix);
    if (!total || !empty || !container) return;

    const count = parseInt(total.value, 10);
    const html = empty.innerHTML.replace(/__prefix__/g, count);
    const wrap = document.createElement('div');
    wrap.className = prefix + '-form form-row rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800/50';
    wrap.setAttribute('draggable', 'true');
    wrap.setAttribute('data-form-row', '');
    wrap.innerHTML =
      '<div class="mb-2 flex items-center gap-2">' +
      '<span class="drag-handle cursor-grab text-slate-400" title="Drag">⠿</span>' +
      '<button type="button" class="rounded border px-2 text-xs" data-move="up">↑</button>' +
      '<button type="button" class="rounded border px-2 text-xs" data-move="down">↓</button></div>' +
      html +
      '<button type="button" class="mt-2 text-xs text-rose-600" data-remove-row>Remove</button>';
    container.appendChild(wrap);
    total.value = count + 1;
    initDragDrop(container);
  };

  window.formatBullets = function (id) {
    const el = document.getElementById(id);
    if (!el) return;
    const lines = el.value.split(/\n/).map(function (l) {
      return l.trim();
    }).filter(Boolean);
    el.value = lines.map(function (l) {
      return '• ' + l.replace(/^[•\-*]\s*/, '');
    }).join('\n');
  };

  function moveRow(row, dir) {
    const parent = row.parentNode;
    if (dir === 'up' && row.previousElementSibling) {
      parent.insertBefore(row, row.previousElementSibling);
    }
    if (dir === 'down' && row.nextElementSibling) {
      parent.insertBefore(row.nextElementSibling, row);
    }
  }

  function initDragDrop(container) {
    if (!container || container.dataset.dragInit) return;
    container.dataset.dragInit = '1';
    let dragged = null;

    container.addEventListener('dragstart', function (e) {
      const row = getFormRow(e.target);
      if (!row) return;
      dragged = row;
      row.classList.add('opacity-50');
      e.dataTransfer.effectAllowed = 'move';
    });

    container.addEventListener('dragend', function () {
      if (dragged) dragged.classList.remove('opacity-50');
      dragged = null;
    });

    container.addEventListener('dragover', function (e) {
      e.preventDefault();
      const row = getFormRow(e.target);
      if (!row || !dragged || row === dragged) return;
      const rect = row.getBoundingClientRect();
      const after = e.clientY > rect.top + rect.height / 2;
      if (after) {
        row.parentNode.insertBefore(dragged, row.nextSibling);
      } else {
        row.parentNode.insertBefore(dragged, row);
      }
    });
  }

  document.addEventListener('click', function (e) {
    const addBtn = e.target.closest('[data-add-form]');
    if (addBtn) {
      window.addForm(addBtn.getAttribute('data-add-form'));
      return;
    }

    const removeBtn = e.target.closest('[data-remove-row]');
    if (removeBtn) {
      const row = getFormRow(removeBtn);
      const section = removeBtn.closest('[data-section]');
      const prefix = section ? section.getAttribute('data-section') : '';
      const container = prefix ? getContainer(prefix) : null;
      if (row && container && container.querySelectorAll('[data-form-row]').length > 1) {
        row.remove();
        updateTotalForms(prefix);
      }
      return;
    }

    const move = e.target.closest('[data-move]');
    if (move) {
      const row = getFormRow(move);
      if (row) moveRow(row, move.getAttribute('data-move'));
      return;
    }

    const bulletBtn = e.target.closest('[data-bullet-btn]');
    if (bulletBtn) {
      window.formatBullets(bulletBtn.getAttribute('data-target'));
    }
  });

  document.querySelectorAll('.sortable-list').forEach(initDragDrop);

  const resumeId = window.RESUME_ID;
  const aiBtn = document.getElementById('ai-summary-btn');
  if (aiBtn) {
    aiBtn.addEventListener('click', async function () {
      if (!resumeId) return;
      const r = await fetch('/resume/' + resumeId + '/ai-summary/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
      });
      if (!r.ok) return;
      const d = await r.json();
      const ta = document.getElementById('id_summary');
      if (ta) ta.value = d.summary;
    });
  }

  async function loadPreview() {
    if (!resumeId) return;
    const sel = document.getElementById('preview-template');
    const box = document.getElementById('live-preview');
    if (!sel || !box) return;
    try {
      const r = await fetch('/resume/' + resumeId + '/preview/' + sel.value + '/');
      box.innerHTML = await r.text();
    } catch (err) {
      box.innerHTML = '<p class="text-rose-500 text-xs">Preview failed to load.</p>';
    }
  }

  const previewSel = document.getElementById('preview-template');
  if (previewSel) previewSel.addEventListener('change', loadPreview);
  if (resumeId) loadPreview();

  if (resumeId) {
    setInterval(async function () {
      const data = {};
      ['resume_name', 'title', 'full_name', 'email', 'phone', 'summary', 'github', 'linkedin', 'preferred_template', 'accent_color', 'font_family'].forEach(function (f) {
        const el = document.getElementById('id_' + f);
        if (el) data[f] = el.value;
      });
      try {
        const r = await fetch('/resume/' + resumeId + '/autosave/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
          body: JSON.stringify(data),
        });
        if (r.ok) {
          const d = await r.json();
          const st = document.getElementById('autosave-status');
          if (st) st.textContent = 'Autosaved ' + new Date(d.updated_at).toLocaleTimeString();
          loadPreview();
        }
      } catch (e) { /* ignore */ }
    }, 20000);
  }
})();
