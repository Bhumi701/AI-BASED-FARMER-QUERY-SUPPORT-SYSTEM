// ==========================================================================
// main.js - small shared helpers used across pages beyond auth/crop/disease/chat.
// Currently: keeps nav in sync with logged-in user, mobile-friendly nav toggle hook.
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
    const user = typeof Utils !== "undefined" ? Utils.getUser() : null;
    const nameEl = document.getElementById("userNameNav");
    if (user && nameEl) {
        nameEl.textContent = user.name;
    }
});
