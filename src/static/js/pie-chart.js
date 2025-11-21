document.addEventListener("DOMContentLoaded", function() {
    
    // canvasのDOM要素を取得
    const $chart = document.querySelector("#chart");
    
    // チャートが存在する場合のみ処理を続ける
    if (!$chart) {
        return;
    }
    
    // 埋め込まれた JSON データを取得
    const labels = JSON.parse(document.getElementById("chart-labels").textContent);
    const counts = JSON.parse(document.getElementById("chart-counts").textContent);
    const colors = JSON.parse(document.getElementById("chart-colors").textContent);

    // canvas要素に対して呼び出すメソッド。描画コンテキストを取得
    const ctx = $chart.getContext("2d");

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
                backgroundColor: colors
            }]
        }
    }

    // プラグイン登録
    Chart.register(ChartDataLabels);
    
    // プラグイン：HTMLに凡例を出す
    const htmlLegendPlugin = {
        id: 'htmlLegend',
        //チャートの描画前に凡例を再構築する
        afterUpdate(chart, args, options) {
            if (chart._legendBuilt) {
                return;
            }
            chart._legendBuilt = true;
            const legendContainer = document.getElementById(options.containerID);
            let ul = legendContainer.querySelector('ul');
            if (!ul) {
            ul = document.createElement('ul');
            legendContainer.appendChild(ul);
            }

            // 古いアイテムを消す
            while (ul.firstChild) {
            ul.firstChild.remove();
            }

            // 凡例アイテムをChart.js本体の設定に基づいて取得
            const items = chart.options.plugins.legend.labels.generateLabels(chart);
            items.forEach(item => {
            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.alignItems = 'center';
            li.style.cursor = 'pointer';

            // クリック時の処理
            li.onclick = () => {
                chart.toggleDataVisibility(item.index);
                chart.update();  // 更新を呼ぶ
            };

            const boxSpan = document.createElement('span');
            boxSpan.className = 'box';

            // fillStyle が無ければ dataset の backgroundColor を参照する
            const color = item.fillStyle ?? chart.data.datasets[0].backgroundColor[item.index];
            boxSpan.style.background = color;

            boxSpan.style.width = '16px';
            boxSpan.style.height = '16px';
            boxSpan.style.marginRight = '6px';

            li.appendChild(boxSpan);

            const text = document.createElement('span');
            text.textContent = item.text;
            if (item.hidden) {
                text.style.textDecoration = 'line-through';
            }
            li.appendChild(text);

            ul.appendChild(li);
            console.log(item);
            });
        }
    };


    new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            maintainAspectRatio: false,
            responsible: false,
            plugins: {
                datalabels: {
                    color: "#fff", // ラベル文字色
                    // totalCountが0の時はラベルを表示しない
                    display: (context) => {
                        return totalCount !== 0;
                    },
                    formatter: (value, context) => {
                        // 値が 0 のときは空文字を返してラベルを実質消す
                        if (value === 0) {
                            return '';
                        }
                        const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0); 
                        const percentage = (value / total * 100).toFixed(1) + "%";
                        return value + "票\n" + percentage;
                    },
                    font: {
                        weight: "bold",
                        size: 12,
                    }
                },
                // 表示されるラベルをどこに置くかという設定
                legend: {
                    display: false,
                },
                // 凡例が見切れないようにHTMLで出力
                htmlLegend: {
                    containerID: "legend-container"
                }
            }
        },
        plugins: [htmlLegendPlugin, ChartDataLabels]
    });
});