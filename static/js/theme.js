document.addEventListener("DOMContentLoaded", function () {
  const themeSwitch = document.getElementById("theme-switch");
  const body = document.body;
  const themeIcon = document.getElementById("theme-icon");

  function setThemeAndIcon(theme) {
    if (theme === "dark") {
      body.classList.add("dark-mode");
      themeSwitch.checked = true;
      localStorage.setItem("theme", "dark");
      if (themeIcon) {
        themeIcon.classList.remove("fa-sun");
        themeIcon.classList.add("fa-moon");
      }
    } else {
      body.classList.remove("dark-mode");
      themeSwitch.checked = false;
      localStorage.setItem("theme", "light");
      if (themeIcon) {
        themeIcon.classList.remove("fa-moon");
        themeIcon.classList.add("fa-sun");
      }
    }
  }

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    setThemeAndIcon(savedTheme);
  } else if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    setThemeAndIcon("dark");
  } else {
    setThemeAndIcon("light");
  }

  themeSwitch.addEventListener("change", function () {
    if (themeSwitch.checked) {
      setThemeAndIcon("dark");
    } else {
      setThemeAndIcon("light");
    }
  });
});
