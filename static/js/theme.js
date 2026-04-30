document.addEventListener("DOMContentLoaded", function () {
  const themeSwitch = document.getElementById("theme-switch");
  const html = document.documentElement;
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');

  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    if (themeSwitch) themeSwitch.checked = theme === "dark";
    localStorage.setItem("theme", theme);
  }

  function persistTheme(theme) {
    if (!csrfMeta) return;
    fetch("/set-theme", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfMeta.content,
      },
      body: JSON.stringify({ theme }),
    }).catch(() => {});
  }

  const saved = localStorage.getItem("theme");
  const serverTheme = html.getAttribute("data-theme");
  let initial;
  if (saved === "dark" || saved === "light") {
    initial = saved;
  } else if (serverTheme === "dark" || serverTheme === "light") {
    initial = serverTheme;
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    initial = "dark";
  } else {
    initial = "light";
  }
  applyTheme(initial);

  if (themeSwitch) {
    themeSwitch.addEventListener("change", function () {
      const theme = this.checked ? "dark" : "light";
      applyTheme(theme);
      persistTheme(theme);
    });
  }
});
