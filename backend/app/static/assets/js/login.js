document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const resultDiv = document.getElementById('loginResult');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Stop page reload

        resultDiv.classList.add('hidden');
        loginBtn.textContent = 'Authenticating...';
        loginBtn.disabled = true;

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            // Your FastAPI /login endpoint expects JSON data
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Success! Save the token to localStorage so the browser remembers we are logged in
                localStorage.setItem('admin_token', data.access_token);
                
                showResult('Login successful! Redirecting...', 'success');
                
                // Redirect to the dashboard (we will build this next!)
                setTimeout(() => {
                    window.location.href = '/admin/dashboard.html';
                }, 1000);

            } else {
                // Wrong username or password
                showResult(data.detail || 'Invalid login credentials.', 'error');
            }

        } catch (error) {
            console.error('Login Error:', error);
            showResult('Cannot connect to the server.', 'error');
        } finally {
            loginBtn.textContent = 'Log In';
            loginBtn.disabled = false;
        }
    });

    function showResult(message, type) {
        resultDiv.textContent = message;
        resultDiv.className = `result-message ${type}`;
        resultDiv.classList.remove('hidden');
    }
});