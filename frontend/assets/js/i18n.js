// ==========================================================================
// i18n.js - simple internationalization helper.
// Loads /translations/<lang>.json and applies text to any element with
// a data-i18n="key" attribute. Falls back to the element's existing text
// if a key/translation is missing (so nothing breaks if a key is absent).
// ==========================================================================
const I18n = (function () {
    let translations = {};
    let currentLang = localStorage.getItem("language") || "en";

    async function loadLanguage(lang) {
        try {
            const res = await fetch(`/translations/${lang}.json`);
            if (!res.ok) throw new Error("not found");
            translations = await res.json();
        } catch (e) {
            translations = {};
        }
        currentLang = lang;
        localStorage.setItem("language", lang);
        document.body.classList.remove("lang-en", "lang-hi", "lang-ml");
        document.body.classList.add(`lang-${lang}`);
        applyTranslations();
    }

    function applyTranslations() {
        document.querySelectorAll("[data-i18n]").forEach((el) => {
            const key = el.getAttribute("data-i18n");
            if (translations[key]) {
                // Preserve any nested elements (e.g. <span id="userName">) by only
                // replacing top-level text nodes when the element has children we
                // need to keep (dashboard_welcome has a nested <span>).
                if (el.children.length > 0) {
                    const firstChild = el.childNodes[0];
                    if (firstChild && firstChild.nodeType === Node.TEXT_NODE) {
                        firstChild.textContent = translations[key] + " ";
                    }
                } else {
                    el.textContent = translations[key];
                }
            }
        });
    }

    function t(key) {
        return translations[key] || key;
    }

    // Auto-init on load
    document.addEventListener("DOMContentLoaded", () => {
        loadLanguage(currentLang);

        // Wire up any language switchers on the page (e.g. dashboard's selector)
        document.querySelectorAll(".lang-select").forEach((select) => {
            select.value = currentLang;
            select.addEventListener("change", (e) => loadLanguage(e.target.value));
        });
    });

    return { t, loadLanguage, get currentLang() { return currentLang; } };
})();
