document.addEventListener("DOMContentLoaded", () => {
  const chartCol = document.getElementById("chartCol");
  const descCol = document.getElementById("descCol");
  const ctx = document.getElementById("myChart")?.getContext("2d");
  let chartInstance = null;

  // Gọi ban đầu
  if (chartCol) fetchChart(chartCol.value);
  if (descCol) fetchDescribe(descCol.value);

  chartCol?.addEventListener("change", () => {
    fetchChart(chartCol.value);
  });

  descCol?.addEventListener("change", () => {
    fetchDescribe(descCol.value);
  });

  function fetchChart(col) {
    fetch("/api/chart", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `selected_col=${encodeURIComponent(col)}`
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) return alert(data.error);

        if (chartInstance) chartInstance.destroy();
        chartInstance = new Chart(ctx, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: [{
              label: `Tần suất: ${data.column}`,
              data: data.values,
              backgroundColor: "rgba(54, 162, 235, 0.6)"
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true }
            }
          }
        });
      });
  }

  function fetchDescribe(col) {
    fetch("/api/describe", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `selected_col=${encodeURIComponent(col)}`
    })
      .then((res) => res.json())
      .then((data) => {
        const box = document.getElementById("describeBox");
        if (data.error) {
          box.innerHTML = `<div class="text-warning">${data.error}</div>`;
          return;
        }

        let html = `<h5>📈 Thống kê mô tả cho: <strong>${data.column}</strong></h5>`;
        html += `<table class="table table-bordered mt-2"><tbody>`;
        data.table_data.forEach((item) => {
          html += `<tr><th>${item.label}</th><td>${item.value}</td></tr>`;
        });
        html += `</tbody></table>`;
        box.innerHTML = html;
      });
  }
});
document.addEventListener('DOMContentLoaded', () => {
  const corrTable = document.getElementById('corrTable');

  fetch('/api/corr')
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        corrTable.innerHTML = `<tr><td colspan="999" class="text-danger">${data.error}</td></tr>`;
        return;
      }

      const labels = data.labels;
      const matrix = data.matrix;

      // Tạo header
      let html = '<thead><tr><th></th>';
      labels.forEach(col => html += `<th>${col}</th>`);
      html += '</tr></thead><tbody>';

      // Tạo body
      labels.forEach(row => {
        html += `<tr><th>${row}</th>`;
        labels.forEach(col => {
          const value = matrix[row][col];
          let color = 'transparent';
          if (value >= 0.75) color = '#d1e7dd';       // xanh
          else if (value <= -0.75) color = '#f8d7da'; // đỏ
          else if (Math.abs(value) >= 0.4) color = '#fff3cd'; // vàng

          html += `<td style="background-color:${color}">${value.toFixed(2)}</td>`;
        });
        html += '</tr>';
      });

      html += '</tbody>';
      corrTable.innerHTML = html;
    })
    .catch(err => {
      corrTable.innerHTML = `<tr><td colspan="999" class="text-danger">Lỗi tải bảng tương quan</td></tr>`;
    });
});
