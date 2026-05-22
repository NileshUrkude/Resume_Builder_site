(function () {
  const STORAGE_KEY = 'resume-builder-theme';
  const root = document.documentElement;

  function getPreferred() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    root.classList.toggle('dark', theme === 'dark');
    localStorage.setItem(STORAGE_KEY, theme);
    document.querySelectorAll('[data-theme-icon]').forEach(function (el) {
      el.classList.toggle('hidden', el.dataset.themeIcon !== theme);
    });
  }

  window.toggleTheme = function () {
    applyTheme(root.classList.contains('dark') ? 'light' : 'dark');
  };

  applyTheme(getPreferred());
})();
