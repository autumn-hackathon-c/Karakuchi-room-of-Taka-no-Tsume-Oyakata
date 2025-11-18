document.addEventListener("DOMContentLoaded", function() {
    const optionContainer = document.getElementById("option-container");

    // DOMの取得ができない場合は処理を終了
    if (!optionContainer) {
        return;
    }

    const addBtn = document.querySelector(".add-option");
    const totalFormsInput = document.querySelector("input[name='options-TOTAL_FORMS']");
    const emptyWrapper = document.querySelector("#empty-form-template");

    let formCount = parseInt(totalFormsInput.value, 10);
    const maxForms = 4;
    const minForms = 2;

    const rawHtml = emptyWrapper.innerHTML;

    // フォームの追加
    function addForm() {
        if (formCount >= maxForms) return;

        const newHtml = rawHtml.replace(/__prefix__/g, formCount);
        const wrapper = document.createElement("div");
        wrapper.className = "option-item mb-3 d-flex justify-content-center align-items-center";
        wrapper.innerHTML = newHtml;

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-none remove-option";
        btn.textContent = "✕";
        wrapper.appendChild(btn);

        optionContainer.appendChild(wrapper);

        formCount++;
        totalFormsInput.value = formCount;
    }

    // フォームの削除
    function removeForm(item) {
        if (formCount <= minForms) return;

        item.remove();
        formCount--;
        totalFormsInput.value = formCount;

        // 削除後、フォームのインデックスを更新
        updateFormIndexes();
    }

    // インデックスを再計算して更新
    function updateFormIndexes() {
        const formItems = optionContainer.querySelectorAll(".option-item");
        
        // 各フォームのインデックスを再設定
        formItems.forEach((item, index) => {
            const inputs = item.querySelectorAll("input, select, textarea");
            
            inputs.forEach(input => {
                const name = input.name.replace(/\d+/, index);  // インデックスを置き換える
                const id = input.id.replace(/\d+/, index);    // インデックスを置き換える
                input.name = name;
                input.id = id;
            });
        });

        // TOTAL_FORMSの値を再計算
        totalFormsInput.value = formItems.length;
    }

    // フォーム削除とイベントの紐づけ
    optionContainer.addEventListener("click", function(e) {
        if (e.target.classList.contains("remove-option")) {
            const item = e.target.closest(".option-item");
            if (item) {
                removeForm(item);
            }
        }
    });

    // フォーム追加とイベントの紐づけ
    addBtn.addEventListener("click", addForm);
});
