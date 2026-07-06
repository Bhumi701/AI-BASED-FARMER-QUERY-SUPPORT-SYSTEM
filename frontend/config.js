// ==========================================================================
// CONFIG.js - central config used by all pages.
// CHANGE API_URL to your deployed backend URL before going live.
// ==========================================================================
const CONFIG = {
    // Local dev default. On Render, set this to your backend service URL,
    // e.g. "https://agri-ai-backend.onrender.com"
    API_URL: (window.__AGRI_API_URL__ || (
        ["localhost", "127.0.0.1"].includes(window.location.hostname)
            ? "http://localhost:8080"
            : "https://agri-ai-backend-7zmv.onrender.com"
    )),

    ENDPOINTS: {
        AUTH: {
            LOGIN: "/api/auth/login",
            REGISTER: "/api/auth/register",
            ME: "/api/auth/me",
        },
        CROP: {
            RECOMMEND: "/api/crop/recommend",
            HISTORY: "/api/crop/history",
        },
        DISEASE: {
            DETECT: "/api/disease/detect",
            HISTORY: "/api/disease/history",
        },
        WEATHER: {
            CURRENT: "/api/weather/current",
            FORECAST: "/api/weather/forecast",
        },
    },

    // chat.js appends "/chat" to this itself -> results in /api/chat/chat
    get CHATBOT_URL() {
        return `${this.API_URL}/api/chat`;
    },

    STORAGE_KEYS: {
        TOKEN: "token",
        USER: "user",
        LANGUAGE: "language",
    },
};

// ==========================================================================
// Utils - shared helper functions used across pages
// ==========================================================================
const Utils = {
    getToken() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    },
    setToken(token) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
    },
    getUser() {
        const raw = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
        return raw ? JSON.parse(raw) : null;
    },
    setUser(user) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(user));
    },
    isAuthenticated() {
        return !!Utils.getToken();
    },
    clearAuth() {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
    },
    formatDate(isoString) {
        if (!isoString) return "";
        const d = new Date(isoString);
        return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    },
    showNotification(message, type = "success") {
        const existing = document.querySelector(".app-notification");
        if (existing) existing.remove();

        const el = document.createElement("div");
        el.className = "app-notification";
        el.textContent = message;
        el.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            padding: 14px 22px; border-radius: 8px; color: white;
            font-family: inherit; font-size: 0.95rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            background: ${type === "error" ? "#ef4444" : "#10b981"};
            animation: slideIn 0.3s ease-out;
        `;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 3000);
    },
};
