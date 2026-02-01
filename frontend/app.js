function safeId(text) {
  return text.replace(/\s+/g, "-").toLowerCase();
}

const API = "http://127.0.0.1:8000";

function formatLocalTime(utcString) {
  if (!utcString) return "-";

  // Force UTC by appending Z if missing
  const normalized = utcString.endsWith("Z")
    ? utcString
    : utcString.replace(" ", "T") + "Z";

  return new Date(normalized).toLocaleString();
}

async function fetchInventory() {
  const res = await fetch(`${API}/items`);
  const data = await res.json();

  const tbody = document.getElementById("inventory");
  tbody.innerHTML = "";

  data.items.forEach(item => {
    const row = document.createElement("tr");
    if (item.low_stock) row.classList.add("low-stock");

    const safeName = safeId(item.name);

    row.innerHTML = `
      <td class="item-name">${item.name}</td>
      <td>${item.price}</td>
      <td>${item.quantity}</td>
      <td>${item.minimum_quantity}</td>
      <td>${item.low_stock ? "LOW STOCK" : "OK"}</td>
      <td>
        <input
        type="number"
        min="1"
        placeholder="Qty"
        id="sell-${safeName}"
        ${item.quantity === 0 ? "disabled" : ""}
        />
       <button
        onclick="sellItem('${safeName}', '${item.name}')"
        ${item.quantity === 0 ? "disabled" : ""}
        >
          Sell
        </button>
      </td>
      <td>
        <input
          type="number"
          min="1"
          placeholder="Qty"
          id="restock-${safeName}"
          />
        <button onclick="restockItem('${safeName}', '${item.name}')">Restock</button>
      </td>
    `;

    tbody.appendChild(row);
  });
}

async function fetchSalesHistory() {
  const res = await fetch(`${API}/sales`);
  const data = await res.json();

  const tbody = document.getElementById("salesHistory");
  tbody.innerHTML = "";

  data.sales.forEach(sale => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${sale.sale_id}</td>
      <td>${sale.item_name}</td>
      <td>${sale.quantity_sold}</td>
      <td>${sale.price_at_sale}</td>
      <td>${formatLocalTime(sale.sold_at)}</td>
    `;

    tbody.appendChild(row);
  });
}

function showError(message) {
  const box = document.getElementById("errorBox");
  box.innerText = message;
}

function clearError() {
  const box = document.getElementById("errorBox");
  box.innerText = "";
}

async function addItem() {
  clearError(); // clear previous errors

  const nameInput = document.getElementById("name");
  const priceInput = document.getElementById("price");
  const quantityInput = document.getElementById("quantity");
  const minQtyInput = document.getElementById("minimumQuantity");

  const body = {
    name: nameInput.value,
    price: Number(priceInput.value),
    quantity: Number(quantityInput.value),
    minimum_quantity: Number(minQtyInput.value)
  };

  const response = await fetch(`${API}/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  const result = await response.json();

  if (!response.ok) {
    if (response.status === 409) {
      showError(result.detail);
    } else if (response.status === 422) {
      showError("Invalid input. Please check all fields.");
    } else {
      showError("Unexpected error occurred.");
    }
    return;
  }

  fetchInventory(); // refresh table if success
}

async function sellItem(safeName, realName) {
  clearError();

  const input = document.getElementById(`sell-${safeName}`);

  if (!input) {
    showError("Internal UI error. Please refresh the page.");
    return;
  }
  const qty = Number(input.value);

  if (!qty || qty <= 0) {
    showError("Enter a valid quantity to sell.");
    return;
  }

  const response = await fetch(`${API}/sales`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      item_name: realName,
      quantity_sold: qty
    })
  });

  const result = await response.json();

  if (!response.ok) {
    showError(result.detail || "Failed to sell item.");
    return;
  }

  input.value = "";
  fetchInventory();
  fetchSalesHistory();
}

async function restockItem(safeName, realName) {
  clearError();

  const input = document.getElementById(`restock-${safeName}`);

  if (!input) {
    showError("Internal UI error. Please refresh the page.");
    return;
  }

  const qty = Number(input.value);

  if (!qty || qty <= 0) {
    showError("Enter a valid quantity to restock.");
    return;
  }

  const response = await fetch(`${API}/items/${realName}/restock`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ quantity: qty })
  });

  const result = await response.json();

  if (!response.ok) {
    showError(result.detail || "Failed to restock item.");
    return;
  }

  input.value = "";
  fetchInventory();
}

// Load inventory on page load
fetchInventory();
fetchSalesHistory();