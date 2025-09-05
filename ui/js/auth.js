// Handle login and registration
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        // Redirect to chat if already logged in
        window.location.href = 'chat.html';
        return;
    }
    
    // Tab switching
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    });
    
    registerTab.addEventListener('click', () => {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    });
    
    // Login form submission
    const loginButton = document.getElementById('login-button');
    loginButton.addEventListener('click', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        const errorElement = document.getElementById('login-error');
        
        if (!username || !password) {
            errorElement.textContent = 'Username and password are required';
            return;
        }
        
        try {
            loginButton.disabled = true;
            loginButton.textContent = 'Logging in...';
            
            const response = await API.login(username, password);
            localStorage.setItem('token', response.access_token);
            window.location.href = 'chat.html';
        } catch (error) {
            errorElement.textContent = error.message || 'Login failed';
        } finally {
            loginButton.disabled = false;
            loginButton.textContent = 'Login';
        }
    });
    
    // Register form submission
    const registerButton = document.getElementById('register-button');
    registerButton.addEventListener('click', async (e) => {
        e.preventDefault();
        const name = document.getElementById('register-name').value;
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const errorElement = document.getElementById('register-error');
        
        if (!name || !username || !password) {
            errorElement.textContent = 'All fields are required';
            return;
        }
        
        if (password.length < 8) {
            errorElement.textContent = 'Password must be at least 8 characters';
            return;
        }
        
        try {
            registerButton.disabled = true;
            registerButton.textContent = 'Registering...';
            
            await API.register(name, username, password);
            
            // Switch to login tab and show success message
            loginTab.click();
            document.getElementById('login-error').textContent = 'Registration successful! Please login.';
            document.getElementById('login-error').style.color = 'green';
            
            // Pre-fill username for convenience
            document.getElementById('login-username').value = username;
        } catch (error) {
            errorElement.textContent = error.message || 'Registration failed';
        } finally {
            registerButton.disabled = false;
            registerButton.textContent = 'Register';
        }
    });
});