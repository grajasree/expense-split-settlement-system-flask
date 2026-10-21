/**
 * Theme Manager for Expense Split and Settlement System
 * Supports Light & Dark themes with localStorage persistence.
 */

(function () {
  const THEME_KEY = 'expense_split_theme';
  const LIGHT = 'light';
  const DARK = 'dark';

  function getSavedTheme() {
    return localStorage.getItem(THEME_KEY) || LIGHT;
  }

  function applyTheme(theme) {
    const isDark = theme === DARK;
    if (isDark) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }

    // Update toggle button icon if exists
    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
      const icon = toggleBtn.querySelector('i');
      if (icon) {
        icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
      }
      toggleBtn.setAttribute('title', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      toggleBtn.setAttribute('aria-label', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }

    localStorage.setItem(THEME_KEY, theme);

    // Notify chart.js and other components that theme changed
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme, isDark } }));
  }

  function toggleTheme() {
    const currentTheme = getSavedTheme();
    const newTheme = currentTheme === DARK ? LIGHT : DARK;
    applyTheme(newTheme);
  }

  // Initialize theme on DOM content loaded
  document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = getSavedTheme();
    applyTheme(savedTheme);

    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleTheme);
    }
  });

  // Export functions to window
  window.ThemeManager = {
    getTheme: getSavedTheme,
    setTheme: applyTheme,
    toggleTheme: toggleTheme
  };
})();
