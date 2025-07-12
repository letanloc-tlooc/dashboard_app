google.charts.load('current', { packages: ['corechart'] });

document.addEventListener("DOMContentLoaded", () => {
  const chartCol = document.getElementById("chartCol");
  const descCol = document.getElementById("descCol");

  if (chartCol) fetchChart(chartCol.value);
  if (descCol) fetchDescribe(descCol.value);

  chartCol?.addEventListener("change", () => fetchChart(chartCol.value));
  descCol?.addEventListener("change", () => fetchDescribe(descCol.value));

  function fetchChart(col) {
    fetch("/api/chart", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `selected_col=${encodeURIComponent(col)}`
    })
      .then(res => res.json())
      .then(data => {
        if (data.error) return alert(data.error);
        google.charts.setOnLoadCallback(() => {
          const chartData = [['Giá trị', 'Tần suất']];
          for (let i = 0; i < data.labels.length; i++) {
            chartData.push([data.labels[i], data.values[i]]);
          }

          const dataTable = google.visualization.arrayToDataTable(chartData);
          const options = {
            title: `📊 Biểu đồ: ${data.column}`,
            legend: { position: 'none' },
            height: 300
          };

          const chart = new google.visualization.ColumnChart(document.getElementById('myChart'));
          chart.draw(dataTable, options);
        });
      });
  }

  function fetchDescribe(col) {
    fetch("/api/describe", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `selected_col=${encodeURIComponent(col)}`
    })
      .then(res => res.json())
      .then(data => {
        const box = document.getElementById("describeBox");
        if (data.error) {
          box.innerHTML = `<div class="text-warning">${data.error}</div>`;
        } else {
          let html = `<h5>📈 Mô tả thuộc tính: <strong>${data.column}</strong></h5><ul>`;
          html += data.table_data.map(d => `<li>${d.label}: <strong>${d.value}</strong></li>`).join("");
          html += "</ul>";
          box.innerHTML = html;
        }
      });
  }
});
