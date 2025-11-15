document.addEventListener("DOMContentLoaded", function() {
    // canvasのDOM要素を取得
    const $chart = document.querySelector("#chart");
    
    // チャートが存在する場合のみ処理を続ける
    if (!$chart) {
        return;
    }

    // canvas要素に対して呼び出すメソッド。描画コンテキストを取得
    const ctx = $chart.getContext("2d");

    // data-　属性からデータを取得
    const labels = [];
    const counts = [];

    // data- 属性の値をループして取得
    Array.from($chart.attributes).forEach(function(attr) {
        if (attr.name.startsWith("data-")) {
            const label = attr.name.replace("data-", "").replace("-", " "); // ラベルを取得
            const count = parseInt(attr.value, 10); // 投票数を取得

            labels.push(label);  // ラベル（選択肢）を追加
            counts.push(count);  // 投票数を追加
        }
    });

    let data;

    // 合計を計算（reduce を使う）
    const totalCount = counts.reduce((sum, count) => sum + count, 0);
    // ここで `0` は初期値。配列が空でも安全に合計を取るため。

    if(totalCount === 0) {
        data ={
            labels: ["まだ投票がありません"],
            datasets: [{
                data: [1],
                backgroundColor: [
                    "#9ca3af"
                ],
            }]
        }
    } else {
        data = {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: labels.map((_, i) => {
                // ラベル数に応じて色を生成、または固定配列から取るなど
                    const colors = ["#34d399", "#f87171", "#60a5fa", "#fbbf24", "#a78bfa"];
                    return colors[i % colors.length];
                })
            }]
        }
    }

    new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            plugins: {
                // 表示されるラベルをどこに置くかという設定
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 18
                        }
                    }
                }
            }
        }
    });
});