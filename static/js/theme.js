document.addEventListener('DOMContentLoaded', function() {
    const themeSwitch = document.getElementById('theme-switch');
    const body = document.body;

    function applyTheme(themeSetting) {
        body.classList.remove('light-mode', 'dark-mode');
        body.classList.add(themeSetting + '-mode');
        themeSwitch.checked = (themeSetting === 'dark');
    }

    function saveThemePreference(themeSetting) {
        fetch('/set-theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ theme: themeSetting })
        })
        .then(response => {
            if (!response.ok) {
                console.error('Failed to save theme preference on server. Status:', response.status);
            }
        })
        .catch(error => {
            console.error('Error sending theme preference to server:', error);
        });
    }

    let storedTheme = localStorage.getItem('theme');

    if (storedTheme) {
        applyTheme(storedTheme);
        saveThemePreference(storedTheme);
    } else {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            applyTheme('dark');
            localStorage.setItem('theme', 'dark');
            saveThemePreference('dark');
        } else {
            applyTheme('light');
            localStorage.setItem('theme', 'light');
            saveThemePreference('light');
        }
    }

    themeSwitch.addEventListener('change', function() {
        if (this.checked) {
            applyTheme('dark');
            localStorage.setItem('theme', 'dark');
            saveThemePreference('dark');
        } else {
            applyTheme('light');
            localStorage.setItem('theme', 'light');
            saveThemePreference('light');
        }
    });
});