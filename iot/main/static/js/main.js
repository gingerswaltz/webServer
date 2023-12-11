const body = document.querySelector("body"),
  sidebar = body.querySelector(".sidebar"),
  main_content = body.querySelector(".main-content"),
  modeSwitch = body.querySelector(".toggle-switch"),
  modeText = body.querySelector(".mode-text"),
  toggle = body.querySelector(".toggle");

modeSwitch.addEventListener("click", () => {
  if (getCookie("night_mode") === "on") {
    body.classList.toggle("dark");
    setCookie("night_mode", "off");
  } else {
    body.classList.toggle("dark");
    setCookie("night_mode", "on");
  }
});

toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
  main_content.classList.toggle("close");
});

//
function setCookie(name, value, options = {}) {
  options = {
    path: "/",
    // при необходимости добавьте другие значения по умолчанию
    ...options,
  };

  if (options.expires instanceof Date) {
    options.expires = options.expires.toUTCString();
  }

  let updatedCookie =
    encodeURIComponent(name) + "=" + encodeURIComponent(value);

  for (let optionKey in options) {
    updatedCookie += "; " + optionKey;
    let optionValue = options[optionKey];
    if (optionValue !== true) {
      updatedCookie += "=" + optionValue;
    }
  }

  document.cookie = updatedCookie;
}

// Геттер куки для режима ночного режима
function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
        name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
        "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

function checkCookie() {
  let status = getCookie("night_mode");
  if (status === "on") {
    body.classList.toggle("dark");
  }
}
