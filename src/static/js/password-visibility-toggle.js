document.addEventListener("DOMContentLoaded", () => {
  // data 属性で指定されたトグルアイコン要素を全部取得
    const toggles = document.querySelectorAll("[data-toggle-password]");

    toggles.forEach(toggle => {
        const targetSelector = toggle.getAttribute("data-toggle-password");
        const input = document.querySelector(targetSelector);
        const icon = toggle.querySelector("i");

        if (!input) {
        // 対応する入力が見つからなければスキップ
        return;
        }

        toggle.addEventListener("click", () => {
        const isPwd = input.type === "password";
        input.type = isPwd ? "text" : "password";

        // Bootstrap Icons のアイコンを切り替え（bi-eye と bi-eye-slash を使う）
        icon.classList.toggle("bi-eye");
        icon.classList.toggle("bi-eye-slash");
        });
    });
});
