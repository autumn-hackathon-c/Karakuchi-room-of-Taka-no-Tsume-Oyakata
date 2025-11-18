document.addEventListener("DOMContentLoaded", function() {
    const optionContainer = document.getElementById("option-container");
    
    // DOMの取得ができない場合は処理を終了
    if (!optionContainer) {
        return;
    }

    const addBtn = document.querySelector(".add-option");
    // {{ formset.management_form }}内の情報、現在出力されているフォームの数を取得
    const totalFormsInput = document.querySelector("input[name='options-TOTAL_FORMS']");
    const emptyWrapper = document.querySelector("#empty-form-template");

    let formCount = parseInt(totalFormsInput.value, 10);
    const maxForms = 4;
    const minForms = 2; 

    const rawHtml = emptyWrapper.innerHTML;

    // フォームの追加
    function addForm() {
        // もし現在の数がmaxforms以上なら追加しない
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
        // もし現在の数が minForms 以下なら削除しない
        if (formCount <= minForms) {
        return;
        }

        item.remove();
        formCount--;
        totalFormsInput.value = formCount;
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
