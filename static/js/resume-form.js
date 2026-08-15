(function () {
  function getFormRow(btn) {
    return btn.closest('[data-form-row]');
  }

  function getContainer(prefix) {
    return document.getElementById(prefix + '-container');
  }

  function updateEmptyHint(prefix) {
    var container = getContainer(prefix);
    if (!container) return;
    var section = container.closest('[data-section]');
    var hints = section ? section.querySelectorAll('[data-empty-hint]') : [];
    var hasRows = container.querySelectorAll('[data-form-row]').length > 0;
    hints.forEach(function (hint) {
      hint.classList.toggle('hidden', hasRows);
    });
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
    updateEmptyHint(prefix);
  }

  function getEditorApi(el) {
    var editor = el && el.closest('.resume-editor');
    if (editor && editor._x_dataStack && editor._x_dataStack[0]) return editor._x_dataStack[0];
    return null;
  }

  function notifyPreview(el) {
    var api = getEditorApi(el);
    if (api && api.queuePreview) api.queuePreview();
  }

  function rowToolbarHtml() {
    return (
      '<div class="form-row-toolbar mb-3 flex items-center gap-1">' +
      '<button type="button" class="drag-handle" aria-label="Drag to reorder" title="Drag to reorder"><i class="bi bi-grip-vertical" aria-hidden="true"></i></button>' +
      '<button type="button" class="row-move-btn" data-move-row="up" aria-label="Move up"><i class="bi bi-arrow-up" aria-hidden="true"></i></button>' +
      '<button type="button" class="row-move-btn" data-move-row="down" aria-label="Move down"><i class="bi bi-arrow-down" aria-hidden="true"></i></button>' +
      '<span class="flex-1"></span>' +
      '<button type="button" class="text-xs font-medium text-rose-600 hover:text-rose-700" data-remove-row><i class="bi bi-trash" aria-hidden="true"></i> Remove</button>' +
      '</div>'
    );
  }

  function moveRow(row, direction) {
    var container = row && row.parentElement;
    if (!container || !container.hasAttribute('data-formset-container')) return;
    var prefix = container.getAttribute('data-prefix');
    if (direction === 'up' && row.previousElementSibling && row.previousElementSibling.hasAttribute('data-form-row')) {
      container.insertBefore(row, row.previousElementSibling);
    } else if (direction === 'down' && row.nextElementSibling && row.nextElementSibling.hasAttribute('data-form-row')) {
      container.insertBefore(row.nextElementSibling, row);
    } else {
      return;
    }
    if (prefix) reindexFormset(prefix);
    notifyPreview(container);
  }

  function initSortable(container) {
    if (!container || typeof Sortable === 'undefined' || container._sortable) return;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    container._sortable = Sortable.create(container, {
      handle: '.drag-handle',
      animation: reduceMotion ? 0 : 150,
      draggable: '[data-form-row]',
      ghostClass: 'form-row-ghost',
      chosenClass: 'form-row-chosen',
      dragClass: 'form-row-drag',
      onEnd: function () {
        var prefix = container.getAttribute('data-prefix');
        if (prefix) reindexFormset(prefix);
        notifyPreview(container);
      },
    });
  }

  function initAllSortables() {
    document.querySelectorAll('[data-formset-container]').forEach(initSortable);
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
    wrap.innerHTML = rowToolbarHtml() + html;
    container.appendChild(wrap);
    reindexFormset(prefix);
    initSortable(container);
    notifyPreview(container);
  };

  document.addEventListener('click', function (e) {
    var addBtn = e.target.closest('[data-add-form]');
    if (addBtn) {
      window.addForm(addBtn.getAttribute('data-add-form'));
      return;
    }
    var moveBtn = e.target.closest('[data-move-row]');
    if (moveBtn) {
      moveRow(getFormRow(moveBtn), moveBtn.getAttribute('data-move-row'));
      return;
    }
    var toggleBtn = e.target.closest('[data-toggle-section]');
    if (toggleBtn) {
      var section = toggleBtn.closest('[data-section]');
      var body = section && section.querySelector('[id$="-body"]');
      if (!body) return;
      var collapsed = body.classList.toggle('hidden');
      toggleBtn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      toggleBtn.textContent = collapsed ? 'Expand' : 'Collapse';
      return;
    }
    var removeBtn = e.target.closest('[data-remove-row]');
    if (removeBtn) {
      var row = getFormRow(removeBtn);
      var section = removeBtn.closest('[data-section]');
      var prefix = section ? section.getAttribute('data-section') : '';
      var container = prefix ? getContainer(prefix) : null;
      if (!row || !container) return;
      row.remove();
      reindexFormset(prefix);
      notifyPreview(container);
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

  ['edu', 'exp', 'proj', 'skill', 'cert', 'ach', 'lang', 'hobby'].forEach(updateEmptyHint);
  initAllSortables();

  var FOCUSABLE = 'a[href], button:not([disabled]), select:not([disabled]), textarea:not([disabled]), input:not([disabled]):not([type="hidden"]), [tabindex]:not([tabindex="-1"])';

  document.addEventListener('alpine:init', function () {
    Alpine.data('resumeEditor', function (config) {
      return {
        resumeId: config.resumeId,
        draftUrlTemplate: config.draftUrlTemplate,
        savedUrlTemplate: config.savedUrlTemplate,
        template: config.initialTemplate || 't1',
        previewLoading: false,
        hasPreview: false,
        sheetOpen: false,
        activeSection: 'section-personal',
        previewTimer: null,
        previewRequestId: 0,
        previousFocus: null,
        boundTrapHandler: null,
        sections: [
          { id: 'section-personal', label: 'Personal' },
          { id: 'section-links', label: 'Links' },
          { id: 'section-experience', label: 'Experience' },
          { id: 'section-education', label: 'Education' },
          { id: 'section-projects', label: 'Projects' },
          { id: 'section-skills', label: 'Skills' },
          { id: 'section-certs', label: 'Certs' },
          { id: 'section-achievements', label: 'Achievements' },
          { id: 'section-languages', label: 'Languages' },
          { id: 'section-interests', label: 'Interests' },
        ],
        init: function () {
          var self = this;
          this.$nextTick(function () {
            self.scalePreview();
            self.refreshPreview(true);
            initAllSortables();
          });
          window.addEventListener('resize', function () {
            self.scalePreview();
          });
          var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
              if (entry.isIntersecting) self.activeSection = entry.target.id;
            });
          }, { rootMargin: '-20% 0px -60% 0px', threshold: 0.1 });
          document.querySelectorAll('[data-editor-section]').forEach(function (el) {
            observer.observe(el);
          });
        },
        scrollToSection: function (id) {
          var el = document.getElementById(id);
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          this.activeSection = id;
        },
        selectTemplate: function (val) {
          this.template = val;
          this.onTemplateChange();
        },
        onTemplateChange: function () {
          var preferred = document.getElementById('id_preferred_template');
          if (preferred) preferred.value = this.template;
          var pdf = document.getElementById('editor-pdf-link');
          if (pdf && this.resumeId) {
            pdf.href = '/resume/' + this.resumeId + '/download/' + this.template + '/';
          }
          this.refreshPreview(true);
        },
        queuePreview: function () {
          var preferred = document.getElementById('id_preferred_template');
          if (preferred && preferred.value !== this.template && document.activeElement === preferred) {
            this.template = preferred.value;
          }
          this.refreshPreview(false);
        },
        getSheetFocusables: function () {
          var sheet = this.$refs.previewSheet;
          if (!sheet) return [];
          return Array.prototype.slice.call(sheet.querySelectorAll(FOCUSABLE)).filter(function (el) {
            return el.offsetParent !== null || el === document.activeElement;
          });
        },
        onSheetKeydown: function (e) {
          if (!this.sheetOpen) return;
          if (e.key === 'Escape') {
            e.preventDefault();
            this.closeSheet();
            return;
          }
          if (e.key !== 'Tab') return;
          var focusables = this.getSheetFocusables();
          if (!focusables.length) {
            e.preventDefault();
            return;
          }
          var first = focusables[0];
          var last = focusables[focusables.length - 1];
          if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
          } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        },
        openSheet: function () {
          this.previousFocus = document.activeElement;
          this.sheetOpen = true;
          document.body.style.overflow = 'hidden';
          var self = this;
          this.boundTrapHandler = function (e) { self.onSheetKeydown(e); };
          document.addEventListener('keydown', this.boundTrapHandler, true);
          this.$nextTick(function () {
            self.mirrorPreviewToSheet();
            self.scalePreview();
            var closeBtn = self.$refs.sheetCloseBtn;
            if (closeBtn) closeBtn.focus();
            else {
              var focusables = self.getSheetFocusables();
              if (focusables[0]) focusables[0].focus();
            }
          });
        },
        closeSheet: function () {
          this.sheetOpen = false;
          document.body.style.overflow = '';
          if (this.boundTrapHandler) {
            document.removeEventListener('keydown', this.boundTrapHandler, true);
            this.boundTrapHandler = null;
          }
          var restore = this.previousFocus || document.getElementById('mobile-preview-toggle');
          this.previousFocus = null;
          if (restore && typeof restore.focus === 'function') {
            this.$nextTick(function () { restore.focus(); });
          }
        },
        mirrorPreviewToSheet: function () {
          var box = this.$refs.previewBox;
          var sheet = this.$refs.sheetPreviewBox;
          if (!box || !sheet) return;
          var iframe = box.querySelector('iframe');
          if (!iframe) return;
          sheet.innerHTML = '';
          var clone = iframe.cloneNode(true);
          clone.srcdoc = iframe.srcdoc;
          sheet.appendChild(clone);
          this.scaleElement(sheet);
        },
        scalePreview: function () {
          if (this.$refs.previewBox) this.scaleElement(this.$refs.previewBox);
          if (this.sheetOpen && this.$refs.sheetPreviewBox) this.scaleElement(this.$refs.sheetPreviewBox);
        },
        scaleElement: function (container) {
          var iframe = container.querySelector('iframe');
          if (!iframe) return;
          var pageWidthPx = 210 * 3.7795275591;
          var available = container.clientWidth - 8;
          var scale = Math.min(1, available / pageWidthPx);
          iframe.style.transform = 'scale(' + scale + ')';
          iframe.style.width = '210mm';
          iframe.style.height = '297mm';
          var wrap = iframe.parentElement;
          if (wrap && wrap.classList.contains('preview-scale-inner')) {
            wrap.style.height = (297 * 3.7795275591 * scale) + 'px';
            wrap.style.width = (pageWidthPx * scale) + 'px';
          } else {
            iframe.style.marginBottom = ((scale - 1) * 297 * 3.7795275591) + 'px';
          }
        },
        showSkeleton: function (container) {
          if (!container) return;
          container.innerHTML = '<div class="preview-skeleton"><div class="preview-skeleton-line w-2/3"></div><div class="preview-skeleton-line w-full"></div><div class="preview-skeleton-line w-5/6"></div><div class="preview-skeleton-line w-4/5"></div></div>';
        },
        mountHtml: function (html) {
          var box = this.$refs.previewBox;
          if (!box) return;
          box.innerHTML = '';
          var inner = document.createElement('div');
          inner.className = 'preview-scale-inner';
          var iframe = document.createElement('iframe');
          iframe.setAttribute('aria-label', 'Resume preview');
          iframe.title = 'Resume preview';
          iframe.srcdoc = html;
          inner.appendChild(iframe);
          box.appendChild(inner);
          this.hasPreview = true;
          var self = this;
          iframe.addEventListener('load', function () {
            self.scalePreview();
            if (self.sheetOpen) self.mirrorPreviewToSheet();
          });
          this.scalePreview();
          if (this.sheetOpen) this.mirrorPreviewToSheet();
        },
        refreshPreview: function (immediate) {
          var self = this;
          if (!this.resumeId) return;
          clearTimeout(this.previewTimer);
          var run = function () {
            self.loadPreview();
          };
          if (immediate) run();
          else this.previewTimer = setTimeout(run, 400);
        },
        loadPreview: function () {
          var self = this;
          var form = document.getElementById('resume-form');
          if (!form || !this.draftUrlTemplate || typeof htmx === 'undefined') return;

          var requestId = ++this.previewRequestId;
          this.previewLoading = true;
          if (!this.hasPreview && this.$refs.previewBox) this.showSkeleton(this.$refs.previewBox);

          var url = this.draftUrlTemplate.replace('__tpl__', this.template);
          var sink = document.getElementById('preview-htmx-sink');

          var onAfter = function (evt) {
            var path = (evt.detail.pathInfo && evt.detail.pathInfo.requestPath) || '';
            var xhr = evt.detail.xhr;
            if (!xhr || path.indexOf('preview-draft') === -1) return;
            if (requestId !== self.previewRequestId) return;
            document.body.removeEventListener('htmx:afterRequest', onAfter);
            if (evt.detail.successful) {
              self.mountHtml(xhr.responseText);
              self.previewLoading = false;
            } else {
              self.previewLoading = false;
              if (!self.hasPreview && self.$refs.previewBox) {
                self.$refs.previewBox.innerHTML = '<p class="p-4 text-xs text-rose-500">Preview unavailable.</p>';
              }
            }
          };

          document.body.addEventListener('htmx:afterRequest', onAfter);

          htmx.ajax('POST', url, {
            source: form,
            target: sink || 'body',
            swap: 'none',
          });
        },
      };
    });
  });
})();
