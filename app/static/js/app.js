(function () {
  // 全局 Toast 容器：统一承接页面内提示消息。
  function ensureToastContainer() {
    let c = document.getElementById("hs-toast-container");
    if (!c) {
      c = document.createElement("div");
      c.id = "hs-toast-container";
      c.className = "toast-container position-fixed top-0 end-0 p-3";
      c.style.zIndex = "1080";
      document.body.appendChild(c);
    }
    return c;
  }

  function escapeHtml(str) {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function categoryToBootstrap(category) {
    const allowed = new Set(["success", "danger", "warning", "info", "primary", "secondary", "dark", "light"]);
    return allowed.has(category) ? category : "info";
  }

  window.hsToast = function (message, category, opts) {
    opts = opts || {};
    const c = ensureToastContainer();
    const bs = categoryToBootstrap(category || "info");
    const delay = typeof opts.delay === "number" ? opts.delay : 3500;

    const wrapper = document.createElement("div");
    wrapper.innerHTML = `
      <div class="toast align-items-center text-bg-${bs} border-0" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">${escapeHtml(message)}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `;
    const toastEl = wrapper.firstElementChild;
    c.appendChild(toastEl);

    const t = new bootstrap.Toast(toastEl, { delay });
    t.show();

    toastEl.addEventListener("hidden.bs.toast", function () {
      toastEl.remove();
    });
  };

  function moveFlashAlertsToToasts() {
    // 将后端 flash 消息转换为前端 toast，统一交互体验。
    const flashArea = document.getElementById("hs-flash-area");
    if (!flashArea) return;

    const alerts = flashArea.querySelectorAll(".alert[data-hs-flash='1']");
    alerts.forEach((a) => {
      const category = a.getAttribute("data-hs-category") || "info";
      const msg = a.getAttribute("data-hs-message") || a.textContent || "";
      if (msg.trim()) window.hsToast(msg.trim(), category);
      a.remove();
    });
  }

  function preventDoubleSubmit() {
    // 防止重复提交按钮，降低重复下单/重复提交风险。
    document.querySelectorAll("form[data-hs-prevent-double-submit='1']").forEach((form) => {
      form.addEventListener("submit", function () {
        const btns = form.querySelectorAll("button[type='submit'], input[type='submit']");
        btns.forEach((b) => {
          b.disabled = true;
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    moveFlashAlertsToToasts();
    preventDoubleSubmit();
  });
})();
