document.addEventListener("DOMContentLoaded", () => {
  // Tải dữ liệu ban đầu
  loadPage(1);

  // Hiển thị thông báo khi upload
  const form = document.getElementById("uploadForm");
  if (form) {
    form.addEventListener("submit", () => {
      showAlert("⏳ Đang tải lên...", "info");
    });
  }
});

// Tải dữ liệu bảng và thông tin thiếu
function loadPage(page = 1) {
  fetch(`/api/data?page=${page}`)
    .then((res) => {
      if (!res.ok) throw new Error("Không tìm thấy dữ liệu.");
      return res.json();
    })
    .then((data) => {
      document.getElementById("table-container").innerHTML = data.html;
      renderPagination(data.current_page, data.total_pages);
    })
    .catch(() => {
      document.getElementById("table-container").innerHTML = "<p class='text-danger'></p>";
      document.getElementById("pagination").innerHTML = "";
    });

  fetch("/api/missing-info")
    .then((res) => res.json())
    .then((data) => {
      renderMissingInfo(data);
    });
}

// Phân trang kiểu tròn
function renderPagination(current, total) {
  const container = document.getElementById("pagination");
  container.innerHTML = "";

  if (total <= 1) return;

  // Previous
  if (current > 1) {
    const prev = createCircleLink("❮", false, current - 1);
    container.appendChild(prev);
  }

  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);

  if (start > 1) {
    container.appendChild(createCircleLink(1, current === 1, 1));
    if (start > 2) container.appendChild(createEllipsis());
  }

  for (let i = start; i <= end; i++) {
    container.appendChild(createCircleLink(i, i === current, i));
  }

  if (end < total) {
    if (end < total - 1) container.appendChild(createEllipsis());
    container.appendChild(createCircleLink(total, current === total, total));
  }

  // Next
  if (current < total) {
    const next = createCircleLink("❯", false, current + 1);
    container.appendChild(next);
  }
}

function createCircleLink(text, isActive, page) {
  const a = document.createElement("a");
  a.href = "#";
  a.textContent = text;
  a.className = "circle-page" + (isActive ? " active" : "");
  a.addEventListener("click", (e) => {
    e.preventDefault();
    loadPage(page);
  });
  return a;
}

function createEllipsis() {
  const span = document.createElement("span");
  span.className = "circle-page disabled";
  span.style.pointerEvents = "none";
  span.textContent = "...";
  return span;
}

// Hiển thị form xử lý dữ liệu thiếu
function renderMissingInfo(data) {
  const container = document.getElementById("missing-container");
  if (!data.length) {
    // container.innerHTML = "<p class='text-success'>✅ Không có dữ liệu thiếu.</p>";
    return;
  }

  let html = `
    <h5>🛠️ Xử lý dữ liệu thiếu</h5>
    <form id="missingForm">
      <div class="table-responsive">
      <table class="table table-bordered">
        <thead>
          <tr><th>Thuộc tính</th><th>Số ô thiếu</th><th>Cách xử lý</th></tr>
        </thead>
        <tbody>`;

  data.forEach((item) => {
    html += `
      <tr>
        <td>${item.column}</td>
        <td>${item.missing}</td>
        <td>
          <select name="strategy_${item.column}" class="form-select">
            <option value="">-- Không làm gì --</option>
            ${item.numeric ? '<option value="mean">Trung bình</option><option value="median">Trung vị</option>' : ""}
            <option value="drop">Xoá dòng bị thiếu</option>
          </select>
        </td>
      </tr>`;
  });

  html += `
        </tbody>
      </table>
      </div>
      <button type="submit" class="btn btn-primary mt-2">✅ Xác nhận xử lý</button>
    </form>`;

  container.innerHTML = html;

  const form = document.getElementById("missingForm");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch("/api/handle-missing", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((res) => {
        showAlert(res.message || "✅ Đã xử lý dữ liệu.", "success");
        loadPage(1);
      });
  });
}

// Hiển thị thông báo
function showAlert(msg, type = "success") {
  const container = document.getElementById("alert-container");
  container.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${msg}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
}
