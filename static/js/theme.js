(function () {
  const STORAGE_KEY = 'resume-builder-theme';
  const root = document.documentElement;

  function getPreferred() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function syncToggle(theme) {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    });
  }

  function applyTheme(theme) {
    root.classList.toggle('dark', theme === 'dark');
    localStorage.setItem(STORAGE_KEY, theme);
    syncToggle(theme);
  }

  window.toggleTheme = function () {
    applyTheme(root.classList.contains('dark') ? 'light' : 'dark');
  };

  applyTheme(getPreferred());
})();
