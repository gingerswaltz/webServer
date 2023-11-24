const body = document.querySelector("body"),
      sidebar = body.querySelector(".sidebar"),
      main_content = body.querySelector(".main-content"),
      toggle = body.querySelector(".toggle");

      toggle.addEventListener("click", () => {
        sidebar.classList.toggle("close");
        main_content.classList.toggle("close");
      });