// =======================================
// Secure Password Manager - Dashboard
// =======================================

const PAGE_SIZE = 10;

// State
let vaultItems = [];
let currentOffset = 0;
let currentSearch = "";
let currentSortBy = "created_at";
let currentSortOrder = "desc";
let editingItemId = null;
let visiblePasswordIds = new Set();

// ------------------------
// Element references
// ------------------------

const userEmailElement = document.getElementById("user-email");
const avatarLetterElement = document.getElementById("avatar-letter");
const logoutButton = document.getElementById("logout-button");

const statTotalElement = document.getElementById("stat-total");
const statWeakElement = document.getElementById("stat-weak");
const statReusedElement = document.getElementById("stat-reused");
const statRecentElement = document.getElementById("stat-recent");

const vaultBody = document.getElementById("vault-body");
const emptyState = document.getElementById("empty-state");
const vaultTableWrapper = document.getElementById("vault-table-wrapper");
const loadingSpinner = document.getElementById("loading-spinner");

const searchInput = document.getElementById("search-input");
const sortBySelect = document.getElementById("sort-by");
const sortOrderButton = document.getElementById("sort-order-button");
const refreshButton = document.getElementById("refresh-button");

const prevPageButton = document.getElementById("prev-page");
const nextPageButton = document.getElementById("next-page");
const pageIndicator = document.getElementById("page-indicator");

const addItemButton = document.getElementById("add-item-button");
const emptyStateAddButton = document.getElementById("empty-state-add-button");
const settingsButton = document.getElementById("settings-button");
const generatorNavButton = document.getElementById("generator-nav-button");

// Vault item modal
const itemModal = document.getElementById("item-modal");
const itemModalTitle = document.getElementById("item-modal-title");
const itemForm = document.getElementById("item-form");
const itemWebsiteInput = document.getElementById("item-website");
const itemUsernameInput = document.getElementById("item-username");
const itemPasswordInput = document.getElementById("item-password");
const itemPasswordToggle = document.getElementById("item-password-toggle");
const itemGenerateButton = document.getElementById("item-generate-button");
const itemSaveButton = document.getElementById("item-save-button");
const itemModalClose = document.getElementById("item-modal-close");
const itemModalCancel = document.getElementById("item-modal-cancel");

// Delete confirm modal
const deleteModal = document.getElementById("delete-modal");
const deleteModalClose = document.getElementById("delete-modal-close");
const deleteModalCancel = document.getElementById("delete-modal-cancel");
const deleteModalConfirm = document.getElementById("delete-modal-confirm");
const deleteModalItemName = document.getElementById("delete-modal-item-name");
let itemPendingDeleteId = null;

// Generator modal
const generatorModal = document.getElementById("generator-modal");
const generatorModalClose = document.getElementById("generator-modal-close");
const generatorLength = document.getElementById("generator-length");
const generatorLengthValue = document.getElementById("generator-length-value");
const generatorUppercase = document.getElementById("generator-uppercase");
const generatorLowercase = document.getElementById("generator-lowercase");
const generatorNumbers = document.getElementById("generator-numbers");
const generatorSymbols = document.getElementById("generator-symbols");
const generatorOutput = document.getElementById("generator-output");
const generatorRegenerate = document.getElementById("generator-regenerate");
const generatorCopy = document.getElementById("generator-copy");
const generatorUse = document.getElementById("generator-use");
let generatorReturnsToItemForm = false;

// Settings modal
const settingsModal = document.getElementById("settings-modal");
const settingsModalClose = document.getElementById("settings-modal-close");
const changePasswordForm = document.getElementById("change-password-form");
const currentPasswordInput = document.getElementById("current-password");
const newPasswordInput = document.getElementById("new-password");
const changePasswordButton = document.getElementById("change-password-button");
const deleteAccountButton = document.getElementById("delete-account-button");
const deleteAccountPasswordInput = document.getElementById("delete-account-password");

// ------------------------
// Init
// ------------------------

loadCurrentUser();
loadVault();
loadVaultStats();

// ------------------------
// Current user
// ------------------------

async function loadCurrentUser() {
    try {
        const user = await apiRequest("/me", { method: "GET" }, true);

        userEmailElement.textContent = user.email;
        avatarLetterElement.textContent = user.email.charAt(0).toUpperCase();
    } catch {
        removeStoredToken();
        window.location.href = "/";
    }
}

logoutButton.addEventListener("click", () => {
    removeStoredToken();
    window.location.href = "/";
});

// ------------------------
// Vault loading & rendering
// ------------------------

function setLoading(isLoading) {
    loadingSpinner.classList.toggle("hidden", !isLoading);
    vaultTableWrapper.classList.toggle("hidden", isLoading);
}

async function loadVault() {
    setLoading(true);

    const params = new URLSearchParams({
        offset: String(currentOffset),
        limit: String(PAGE_SIZE),
        sort_by: currentSortBy,
        sort_order: currentSortOrder,
    });

    if (currentSearch.trim() !== "") {
        params.set("search", currentSearch.trim());
    }

    try {
        vaultItems = await apiRequest(`/vault?${params.toString()}`, { method: "GET" }, true);
        renderVault();
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

async function loadVaultStats() {
    try {
        const stats = await apiRequest("/vault/stats/summary", { method: "GET" }, true);

        statTotalElement.textContent = stats.total;
        statWeakElement.textContent = stats.weak_count;
        statReusedElement.textContent = stats.reused_count;
        statRecentElement.textContent = stats.added_this_week;
    } catch {
        statTotalElement.textContent = "—";
        statWeakElement.textContent = "—";
        statReusedElement.textContent = "—";
        statRecentElement.textContent = "—";
    }
}

function renderVault() {
    vaultBody.innerHTML = "";

    const hasItems = vaultItems.length > 0;

    emptyState.classList.toggle("hidden", hasItems);
    document.getElementById("vault-table").classList.toggle("hidden", !hasItems);

    vaultItems.forEach((item, index) => {
        const row = document.createElement("tr");

        const isVisible = visiblePasswordIds.has(item.id);
        const passwordDisplay = isVisible ? escapeHtml(item.password) : "••••••••••••";
        const boxNumber = String(currentOffset + index + 1).padStart(3, "0");

        row.innerHTML = `
            <td><span class="box-tag">№ ${boxNumber}</span></td>
            <td>
                <div class="cell-primary">${escapeHtml(item.website)}</div>
                <div class="cell-secondary">Added ${formatDate(item.created_at)}</div>
            </td>
            <td>
                <span class="copyable" data-copy="${escapeHtml(item.username)}" title="Click to copy">
                    ${escapeHtml(item.username)}
                </span>
            </td>
            <td>
                <span class="password-mask" id="password-text-${item.id}">${passwordDisplay}</span>
            </td>
            <td>
                <div class="row-actions">
                    <button class="icon-button" data-action="toggle" data-id="${item.id}" title="Show/hide password">
                        ${isVisible ? "Hide" : "Show"}
                    </button>
                    <button class="icon-button" data-action="copy" data-id="${item.id}" title="Copy password">
                        Copy
                    </button>
                    <button class="icon-button" data-action="edit" data-id="${item.id}" title="Edit">
                        Edit
                    </button>
                    <button class="icon-button icon-button-danger" data-action="delete" data-id="${item.id}" title="Delete">
                        Delete
                    </button>
                </div>
            </td>
        `;

        vaultBody.appendChild(row);
    });

    prevPageButton.disabled = currentOffset === 0;
    nextPageButton.disabled = vaultItems.length < PAGE_SIZE;

    const pageNumber = Math.floor(currentOffset / PAGE_SIZE) + 1;
    pageIndicator.textContent = `Page ${pageNumber}`;
}

vaultBody.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");

    if (target) {
        const id = Number(target.dataset.id);

        if (target.dataset.action === "toggle") togglePasswordVisibility(id);
        if (target.dataset.action === "copy") copyItemPassword(id);
        if (target.dataset.action === "edit") openEditModal(id);
        if (target.dataset.action === "delete") openDeleteModal(id);

        return;
    }

    const copyTarget = event.target.closest("[data-copy]");

    if (copyTarget) {
        copyToClipboard(copyTarget.dataset.copy, "Username copied to clipboard.");
    }
});

function togglePasswordVisibility(id) {
    if (visiblePasswordIds.has(id)) {
        visiblePasswordIds.delete(id);
    } else {
        visiblePasswordIds.add(id);
    }

    renderVault();
}

async function copyItemPassword(id) {
    const item = vaultItems.find((entry) => entry.id === id);

    if (!item) return;

    await copyToClipboard(item.password, "Password copied to clipboard.");
}

async function copyToClipboard(value, successMessage) {
    try {
        await navigator.clipboard.writeText(value);
        showSuccess(successMessage);
    } catch {
        showError("Unable to copy to clipboard.");
    }
}

// ------------------------
// Search, sort, pagination
// ------------------------

let searchDebounceTimer = null;

searchInput.addEventListener("input", () => {
    clearTimeout(searchDebounceTimer);

    searchDebounceTimer = setTimeout(() => {
        currentSearch = searchInput.value;
        currentOffset = 0;
        loadVault();
    }, 350);
});

sortBySelect.addEventListener("change", () => {
    currentSortBy = sortBySelect.value;
    currentOffset = 0;
    loadVault();
});

sortOrderButton.addEventListener("click", () => {
    currentSortOrder = currentSortOrder === "asc" ? "desc" : "asc";
    sortOrderButton.textContent = currentSortOrder === "asc" ? "↑ Ascending" : "↓ Descending";
    currentOffset = 0;
    loadVault();
});

refreshButton.addEventListener("click", () => {
    searchInput.value = "";
    currentSearch = "";
    currentOffset = 0;
    loadVault();
});

prevPageButton.addEventListener("click", () => {
    currentOffset = Math.max(0, currentOffset - PAGE_SIZE);
    loadVault();
});

nextPageButton.addEventListener("click", () => {
    currentOffset += PAGE_SIZE;
    loadVault();
});

// ------------------------
// Add / Edit item modal
// ------------------------

function openAddModal() {
    editingItemId = null;
    itemModalTitle.textContent = "Add Password";
    itemForm.reset();
    itemPasswordInput.type = "password";
    itemPasswordToggle.textContent = "Show";
    openModal(itemModal);
    itemWebsiteInput.focus();
}

function openEditModal(id) {
    const item = vaultItems.find((entry) => entry.id === id);

    if (!item) return;

    editingItemId = id;
    itemModalTitle.textContent = "Edit Password";
    itemWebsiteInput.value = item.website;
    itemUsernameInput.value = item.username;
    itemPasswordInput.value = item.password;
    itemPasswordInput.type = "password";
    itemPasswordToggle.textContent = "Show";
    openModal(itemModal);
    itemWebsiteInput.focus();
}

addItemButton.addEventListener("click", openAddModal);
emptyStateAddButton.addEventListener("click", openAddModal);

itemModalClose.addEventListener("click", () => closeModal(itemModal));
itemModalCancel.addEventListener("click", () => closeModal(itemModal));

itemPasswordToggle.addEventListener("click", () => {
    const isHidden = itemPasswordInput.type === "password";
    itemPasswordInput.type = isHidden ? "text" : "password";
    itemPasswordToggle.textContent = isHidden ? "Hide" : "Show";
});

itemGenerateButton.addEventListener("click", () => {
    generatorReturnsToItemForm = true;
    openGeneratorModal();
});

itemForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        website: itemWebsiteInput.value.trim(),
        username: itemUsernameInput.value.trim(),
        password: itemPasswordInput.value,
    };

    if (!payload.website || !payload.username || !payload.password) {
        showError("All fields are required.");
        return;
    }

    setButtonLoading(itemSaveButton, true, "Save");

    try {
        if (editingItemId === null) {
            await apiRequest(
                "/vault",
                { method: "POST", body: JSON.stringify(payload) },
                true
            );
            showSuccess("Password saved.");
        } else {
            await apiRequest(
                `/vault/${editingItemId}`,
                { method: "PATCH", body: JSON.stringify(payload) },
                true
            );
            showSuccess("Password updated.");
        }

        closeModal(itemModal);
        loadVault();
        loadVaultStats();
    } catch (error) {
        showError(error.message);
    } finally {
        setButtonLoading(itemSaveButton, false, "Save");
    }
});

// ------------------------
// Delete confirmation modal
// ------------------------

function openDeleteModal(id) {
    const item = vaultItems.find((entry) => entry.id === id);

    if (!item) return;

    itemPendingDeleteId = id;
    deleteModalItemName.textContent = item.website;
    openModal(deleteModal);
}

deleteModalClose.addEventListener("click", () => closeModal(deleteModal));
deleteModalCancel.addEventListener("click", () => closeModal(deleteModal));

deleteModalConfirm.addEventListener("click", async () => {
    if (itemPendingDeleteId === null) return;

    setButtonLoading(deleteModalConfirm, true, "Delete");

    try {
        await apiRequest(`/vault/${itemPendingDeleteId}`, { method: "DELETE" }, true);
        showSuccess("Password deleted.");
        closeModal(deleteModal);

        if (vaultItems.length === 1 && currentOffset > 0) {
            currentOffset = Math.max(0, currentOffset - PAGE_SIZE);
        }

        loadVault();
        loadVaultStats();
    } catch (error) {
        showError(error.message);
    } finally {
        setButtonLoading(deleteModalConfirm, false, "Delete");
        itemPendingDeleteId = null;
    }
});

// ------------------------
// Password generator modal
// ------------------------

function openGeneratorModal() {
    openModal(generatorModal);
    generateNewPassword();
}

generatorNavButton.addEventListener("click", () => {
    generatorReturnsToItemForm = false;
    openGeneratorModal();
});

generatorModalClose.addEventListener("click", () => closeModal(generatorModal));

generatorLength.addEventListener("input", () => {
    generatorLengthValue.textContent = generatorLength.value;
});

[generatorUppercase, generatorLowercase, generatorNumbers, generatorSymbols].forEach((checkbox) => {
    checkbox.addEventListener("change", generateNewPassword);
});

generatorLength.addEventListener("change", generateNewPassword);
generatorRegenerate.addEventListener("click", generateNewPassword);

async function generateNewPassword() {
    const atLeastOneOptionSelected =
        generatorUppercase.checked ||
        generatorLowercase.checked ||
        generatorNumbers.checked ||
        generatorSymbols.checked;

    if (!atLeastOneOptionSelected) {
        generatorOutput.value = "";
        showError("Select at least one character type.");
        return;
    }

    try {
        const result = await apiRequest(
            "/generate-password",
            {
                method: "POST",
                body: JSON.stringify({
                    length: Number(generatorLength.value),
                    include_uppercase: generatorUppercase.checked,
                    include_lowercase: generatorLowercase.checked,
                    include_numbers: generatorNumbers.checked,
                    include_symbols: generatorSymbols.checked,
                }),
            },
            true
        );

        generatorOutput.value = result.password;
    } catch (error) {
        showError(error.message);
    }
}

generatorCopy.addEventListener("click", async () => {
    if (!generatorOutput.value) return;
    await copyToClipboard(generatorOutput.value, "Generated password copied.");
});

generatorUse.addEventListener("click", () => {
    if (!generatorOutput.value) return;

    if (generatorReturnsToItemForm) {
        itemPasswordInput.value = generatorOutput.value;
        itemPasswordInput.type = "text";
        itemPasswordToggle.textContent = "Hide";
        closeModal(generatorModal);
        openModal(itemModal);
    } else {
        copyToClipboard(generatorOutput.value, "Generated password copied.");
    }
});

// ------------------------
// Settings modal
// ------------------------

settingsButton.addEventListener("click", () => {
    changePasswordForm.reset();
    deleteAccountPasswordInput.value = "";
    openModal(settingsModal);
});

settingsModalClose.addEventListener("click", () => closeModal(settingsModal));

changePasswordForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const currentPassword = currentPasswordInput.value;
    const newPassword = newPasswordInput.value;

    if (newPassword.length < 8) {
        showError("New password must be at least 8 characters.");
        return;
    }

    setButtonLoading(changePasswordButton, true, "Change password");

    try {
        await apiRequest(
            "/account/password",
            {
                method: "PATCH",
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                }),
            },
            true
        );

        showSuccess("Password changed successfully.");
        changePasswordForm.reset();
    } catch (error) {
        showError(error.message);
    } finally {
        setButtonLoading(changePasswordButton, false, "Change password");
    }
});

deleteAccountButton.addEventListener("click", async () => {
    const password = deleteAccountPasswordInput.value;

    if (!password) {
        showError("Enter your current password to delete your account.");
        return;
    }

    const confirmed = confirm(
        "This will permanently delete your account and all stored passwords. This cannot be undone. Continue?"
    );

    if (!confirmed) return;

    setButtonLoading(deleteAccountButton, true, "Delete account");

    try {
        await apiRequest(
            "/account",
            {
                method: "DELETE",
                body: JSON.stringify({ current_password: password }),
            },
            true
        );

        removeStoredToken();
        window.location.href = "/";
    } catch (error) {
        showError(error.message);
        setButtonLoading(deleteAccountButton, false, "Delete account");
    }
});

// ------------------------
// Generic modal helpers
// ------------------------

function openModal(modal) {
    modal.classList.remove("hidden");
    document.body.classList.add("modal-open");
}

function closeModal(modal) {
    modal.classList.add("hidden");
    document.body.classList.remove("modal-open");
}

document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) {
            closeModal(overlay);
        }
    });
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        document.querySelectorAll(".modal-overlay:not(.hidden)").forEach(closeModal);
    }
});
