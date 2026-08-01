// =======================================
// Secure Password Manager - Auth Page
// =======================================

const loginTab = document.getElementById("login-tab");
const registerTab = document.getElementById("register-tab");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

const messageElement = document.getElementById("message");


function showMessage(message, type = "error") {
    messageElement.textContent = message;
    messageElement.className = `message ${type}`;
}

function clearMessage() {
    messageElement.textContent = "";
    messageElement.className = "message hidden";
}

function showLoginForm() {
    clearMessage();

    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
}

function showRegisterForm() {
    clearMessage();

    registerTab.classList.add("active");
    loginTab.classList.remove("active");

    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
}

loginTab.addEventListener("click", showLoginForm);
registerTab.addEventListener("click", showRegisterForm);

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const loginButton = document.getElementById("login-button");

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    setButtonLoading(loginButton, true, "Sign in");

    try {
        const responseData = await apiRequest(
            "/login",
            {
                method: "POST",
                body: JSON.stringify({ email, password }),
            },
            false
        );

        storeToken(responseData.access_token);

        window.location.href = "/dashboard";
    } catch (error) {
        showMessage(error.message);
    } finally {
        setButtonLoading(loginButton, false, "Sign in");
    }
});

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const registerButton = document.getElementById("register-button");

    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (password.length < 8) {
        showMessage("Password must be at least 8 characters long.");
        return;
    }

    if (password !== confirmPassword) {
        showMessage("Passwords do not match.");
        return;
    }

    setButtonLoading(registerButton, true, "Create account");

    try {
        await apiRequest(
            "/register",
            {
                method: "POST",
                body: JSON.stringify({ email, password }),
            },
            false
        );

        showLoginForm();

        document.getElementById("login-email").value = email;

        showMessage("Account created successfully. You can now sign in.", "success");

        registerForm.reset();
    } catch (error) {
        showMessage(error.message);
    } finally {
        setButtonLoading(registerButton, false, "Create account");
    }
});

async function redirectAuthenticatedUser() {
    const token = getStoredToken();

    if (!token) {
        return;
    }

    try {
        await apiRequest("/me", { method: "GET" }, true);
        window.location.href = "/dashboard";
    } catch {
        removeStoredToken();
    }
}

redirectAuthenticatedUser();
