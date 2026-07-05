// Login Form Handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${CONFIG.ENDPOINTS.AUTH.LOGIN}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                Utils.setToken(data.token);
                Utils.setUser(data.user);
                Utils.showNotification('Login successful!', 'success');
                setTimeout(() => window.location.href = 'dashboard.html', 1000);
            } else {
                Utils.showNotification(data.message || 'Login failed', 'error');
            }
        } catch (error) {
            Utils.showNotification('Network error. Please try again.', 'error');
            console.error('Login error:', error);
        }
    });
}

// Register Form Handler
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            password: document.getElementById('password').value,
            state: document.getElementById('state').value,
            district: document.getElementById('district').value,
            language: document.getElementById('language').value
        };
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${CONFIG.ENDPOINTS.AUTH.REGISTER}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                Utils.showNotification('Registration successful! Please login.', 'success');
                setTimeout(() => window.location.href = 'login.html', 1500);
            } else {
                Utils.showNotification(data.message || 'Registration failed', 'error');
            }
        } catch (error) {
            Utils.showNotification('Network error. Please try again.', 'error');
            console.error('Register error:', error);
        }
    });
}

// Check if already authenticated
if (Utils.isAuthenticated() && window.location.pathname.includes('login.html')) {
    window.location.href = 'dashboard.html';
}