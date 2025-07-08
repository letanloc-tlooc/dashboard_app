document.getElementById("uploadForm")?.addEventListener("submit", function (e) {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return;

  const allowedExtensions = ["csv", "xls", "xlsx"];
  const ext = file.name.split(".").pop().toLowerCase();
  if (!allowedExtensions.includes(ext)) {
    e.preventDefault();

    Swal.fire({
      icon: "error",
      title: "Không hợp lệ",
      text: "❌ Chỉ hỗ trợ file .csv, .xls, .xlsx",
    });
  }
});
