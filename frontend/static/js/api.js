// =======================================
// Secure Password Manager - Shared Client
// =======================================

const TOKEN_KEY = "access_token";

function getStoredToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function storeToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function removeStoredToken() {
    localStorage.removeItem(TOKEN_KEY);
}

/**
 * Core request helper used by every page.
 * @param {string} path - API path, e.g. "/vault"
 * @param {RequestInit} options - fetch options (method, body, headers)
 * @param {boolean} authRequired - attach Authorization header
 */
async function apiRequest(path, options = {}, authRequired = true) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    if (authRequired) {
        const token = getStoredToken();

        if (!token) {
            removeStoredToken();
            window.location.href = "/";
            throw new Error("Not authenticated");
        }

        headers["Authorization"] = `Bearer ${token}`;
    }

    let response;

    try {
        response = await fetch(path, {
            ...options,
            headers,
        });
    } catch (networkError) {
        throw new Error(
            "Network error. Please check your connection and try again."
        );
    }

    if (response.status === 204) {
        return null;
    }

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        if (response.status === 401 && authRequired) {
            removeStoredToken();
            window.location.href = "/";
        }

        const detail = data && data.detail;

        let message = "Something went wrong. Please try again.";

        if (typeof detail === "string") {
            message = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
            message = detail
                .map((entry) => entry.msg || "Invalid input")
                .join(" ");
        }

        throw new Error(message);
    }

    return data;
}

// ------------------------
// Toast notifications
// ------------------------

function ensureToastContainer() {
    let container = document.getElementById("toast-container");

    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    return container;
}

function showToast(message, type = "info", duration = 3500) {
    const container = ensureToastContainer();

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("toast-visible");
    });

    setTimeout(() => {
        toast.classList.remove("toast-visible");
        setTimeout(() => toast.remove(), 250);
    }, duration);
}

function showSuccess(message) {
    showToast(message, "success");
}

function showError(message) {
    showToast(message, "error");
}

// ------------------------
// Small helpers
// ------------------------

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function formatDate(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    } catch {
        return "";
    }
}

function setButtonLoading(button, isLoading, normalText) {
    if (!button) return;

    button.disabled = isLoading;
    button.textContent = isLoading ? "Please wait..." : normalText;
}
