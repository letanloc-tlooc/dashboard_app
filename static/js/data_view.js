document.addEventListener("DOMContentLoaded", function () {
  const categorical = window.categoricalColumns || [];
  const numeric = window.numericColumns || [];

  const updateNumericOptions = () => {
    const selectedCat = document.getElementById("col_cat").value;
    const numericSelect = document.getElementById("col_num");
    numericSelect.innerHTML = "";

    numeric.forEach(col => {
      if (!categorical.includes(col)) {
        const opt = document.createElement("option");
        opt.value = col;
        opt.textContent = col;
        numericSelect.appendChild(opt);
      }
    });
  };

  // Gắn lại function vào global để onchange gọi được
  window.updateNumericOptions = updateNumericOptions;
});
