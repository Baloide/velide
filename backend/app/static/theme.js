'use strict';
// Apply the saved/system appearance before the stylesheet loads to avoid a bright flash.
const systemAppearance = window.matchMedia('(prefers-color-scheme: dark)');
let appearancePreference = 'system';
try {
  const saved = localStorage.getItem('baloide-theme');
  if (['light', 'dark', 'system'].includes(saved)) appearancePreference = saved;
} catch {}

function applyAppearance() {
  document.documentElement.dataset.theme = appearancePreference === 'system' ? (systemAppearance
    .matches ? 'dark' : 'light') : appearancePreference;
  document.documentElement.dataset.themePreference = appearancePreference;
}

function setAppearance(preference) {
  if (!['light', 'dark', 'system'].includes(preference)) return;
  appearancePreference = preference;
  try {
    localStorage.setItem('baloide-theme', preference);
  } catch {}
  applyAppearance();
}
systemAppearance.addEventListener('change', () => {
  if (appearancePreference === 'system') applyAppearance();
});
applyAppearance();
