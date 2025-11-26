// ------------------------------------------------------------
// CSRFトークンを取得する関数
// ------------------------------------------------------------
// DjangoはPOSTリクエストにCSRFトークンが必要。
// Cookieから「csrftoken」という名前の値を取り出して返す。
// ------------------------------------------------------------
function getCookie(name) {
    let cookieValue = null;

    // Cookieが存在する場合
    if (document.cookie && document.cookie !== '') {
        // Cookie を ; 区切りで配列にする
        const cookies = document.cookie.split(';');

        // 各Cookieをループしながら目的の名前を探す
        for (let cookie of cookies) {
            cookie = cookie.trim(); // 前後の空白を除去

            // cookie が「名前=値」の形になっているか、先頭一致でチェック
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                // 「名前=値」の "=" 以降を取り出す
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue; // 見つかった値を返す
}



// ------------------------------------------------------------
// 「AIで柔らかくする」ボタンが押された時の処理
// ------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {

    const softenBtn = document.getElementById("ai_soften_btn");
    if (!softenBtn) return;  // ← ボタンが無いページでは処理をしない

    softenBtn.addEventListener("click", function () {

        // textarea（コメント入力欄）の中身を取得
        const text = document.getElementById("comment_input").value;

        // --------------------------------------------------------
        // Django の API（/api/comment/soften/）に入力文章を送る
        // --------------------------------------------------------
        fetch("/api/comment/soften/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json", // JSON形式で送信
                "X-CSRFToken": getCookie("csrftoken"), // CSRFトークンをヘッダーにセット
            },
            body: JSON.stringify({ text: text }), // 「text: 入力内容」を送る
        })
            // レスポンス（APIから返ってきたデータ）を JSON として読み込む
            .then(res => res.json())

            // 読み込んだ JSON データで次の処理を行う
            .then(data => {

                // ----------------------------------------------------
                // AI が柔らかく書き換えた文章を textarea に反映
                // ----------------------------------------------------
                document.getElementById("comment_input").value = data.soft_text;

                // 変換完了メッセージを画面に表示
                const result = document.getElementById("ai_result");
                result.style.color = "#007700";   // ← 緑色にする
                result.innerText = "文章を書き換えました！こちらの文章でいかがでしょうか？";
            });
        });
});