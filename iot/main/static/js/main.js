const body = document.querySelector("body"),
      sidebar = body.querySelector(".sidebar"),
      main_content = body.querySelector(".main-content"),
      modeSwitch = body.querySelector(".toggle-switch"),
      modeText = body.querySelector(".mode-text"),
      toggle = body.querySelector(".toggle");

      modeSwitch.addEventListener("click", () => {
        body.classList.toggle("dark");
      });

      toggle.addEventListener("click", () => {
        sidebar.classList.toggle("close");
        main_content.classList.toggle("close");
      });