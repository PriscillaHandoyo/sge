/* ====================================================================
   SGE — Shared UI Components
   Hal-hal yang berulang di semua halaman CRUD: buka/tutup modal,
   konfirmasi hapus. Dipisah biar gak di-copy-paste di tiap halaman.
   ==================================================================== */

/**
 * Buka modal berdasarkan id overlay-nya.
 * Contoh: openModal("modal-overlay")
 */
function openModal(overlayId) {
  const overlay = document.getElementById(overlayId);
  if (overlay) overlay.style.display = "flex";
}

/**
 * Tutup modal berdasarkan id overlay-nya.
 * Contoh: closeModal("modal-overlay")
 */
function closeModal(overlayId) {
  const overlay = document.getElementById(overlayId);
  if (overlay) overlay.style.display = "none";
}

/**
 * Tampilkan pesan error di dalam form (elemen <p> dengan id tertentu).
 * Contoh: showFormError("form-error", "Kode sudah dipakai")
 */
function showFormError(errorElId, message) {
  const el = document.getElementById(errorElId);
  if (!el) return;
  el.textContent = message;
  el.style.display = "block";
}

function hideFormError(errorElId) {
  const el = document.getElementById(errorElId);
  if (!el) return;
  el.style.display = "none";
}

/**
 * Konfirmasi hapus dengan format pesan yang konsisten di semua halaman.
 * Contoh: confirmDelete("customer", "PT Maju Jaya")
 */
function confirmDelete(itemType, itemName) {
  return confirm(`Hapus ${itemType} "${itemName}"? Tindakan ini tidak bisa dibatalkan.`);
}

/**
 * Bikin 1 baris mobile-card (label di kiri, value di kanan).
 * Contoh: mobileCardRow("Kode", "CUST-001")
 */
function mobileCardRow(label, value, mono = false) {
  return `<div class="mobile-card-row">
    <span class="mobile-card-label">${label}</span>
    <span class="mobile-card-value${mono ? " font-mono" : ""}">${value ?? "—"}</span>
  </div>`;
}

/**
 * Bikin 2 tombol aksi (Edit/Hapus) buat kolom terakhir tabel desktop.
 * Contoh: actionButtons(`openEditModal(${c.id})`, `deleteCustomer(${c.id})`)
 */
function actionButtons(onEdit, onDelete) {
  return `
    <button class="btn-icon" onclick="${onEdit}" title="Edit">${editIcon()}</button>
    <button class="btn-icon" onclick="${onDelete}" title="Hapus">${trashIcon()}</button>
  `;
}

/**
 * Bikin 2 tombol aksi versi mobile card (full width, label teks).
 * Contoh: actionButtonsMobile(`openEditModal(${c.id})`, `deleteCustomer(${c.id})`)
 */
function actionButtonsMobile(onEdit, onDelete) {
  return `
    <div class="flex gap-2" style="margin-top:8px;">
      <button class="btn" style="flex:1;" onclick="${onEdit}">Edit</button>
      <button class="btn btn-danger" style="flex:1;" onclick="${onDelete}">Hapus</button>
    </div>
  `;
}

/**
 * Bungkus teks panjang biar dipotong (ellipsis) sesuai max-width, dan
 * munculin teks lengkapnya lewat tooltip (atribut title) pas di-hover.
 * Dipake di cell tabel yang kontennya bisa panjang (nama, alamat, dst).
 */
function truncatedCell(text, maxWidthPx = 200) {
  const safe = text === null || text === undefined || text === "" ? "—" : text;
  const escaped = String(safe).replace(/"/g, "&quot;");
  return `<span style="display:inline-block; max-width:${maxWidthPx}px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; vertical-align:bottom;" title="${escaped}">${safe}</span>`;
}

/* ====================================================================
   Table Sort & Filter — generic engine (kayak AutoFilter Excel)
   Dipakai bareng di semua halaman Master. Tiap halaman cuma perlu:
   1. Definisiin array `columns` (key, label, getValue opsional)
   2. Set window.currentTableAllData, window.currentTableColumns,
      window.currentTableRefresh pas init()
   3. Pas render <thead>, panggil sortableHeader(tableId, col) per kolom
   4. Pas mau render <tbody>, panggil processTableData(...) dulu
   ==================================================================== */

const _tableState = {};

function _getTableState(tableId) {
  if (!_tableState[tableId]) {
    _tableState[tableId] = { sortField: null, sortDir: "asc", filters: {}, page: 1, pageSize: 100 };
  }
  return _tableState[tableId];
}

function _colValue(row, col) {
  const raw = col.getValue ? col.getValue(row) : row[col.key];
  return raw === null || raw === undefined || raw === "" ? "—" : String(raw);
}

/**
 * Buat keperluan SORT (beda dari _colValue yang buat filter) — balikin
 * value mentahnya (bukan di-string-in dulu), biar angka bisa dibandingin
 * sebagai angka, bukan teks ("10" < "2" secara teks, padahal seharusnya
 * 10 > 2 secara angka).
 */
function _rawColValue(row, col) {
  return col.getValue ? col.getValue(row) : row[col.key];
}

function _compareValues(va, vb) {
  const na = typeof va === "number" ? va : (va !== null && va !== undefined && va !== "" && !isNaN(va) ? Number(va) : null);
  const nb = typeof vb === "number" ? vb : (vb !== null && vb !== undefined && vb !== "" && !isNaN(vb) ? Number(vb) : null);
  if (na !== null && nb !== null) return na - nb;
  return String(va ?? "").localeCompare(String(vb ?? ""));
}

/**
 * Proses data: search bebas -> filter per-kolom -> sort. Balikin array baru,
 * gak ngubah array aslinya.
 */
function processTableData(tableId, allData, searchValue, searchFields, columns) {
  const state = _getTableState(tableId);
  let result = allData;

  if (searchValue) {
    const v = searchValue.toLowerCase();
    result = result.filter(row =>
      searchFields.some(f => String(row[f] ?? "").toLowerCase().includes(v))
    );
  }

  columns.forEach(col => {
    const activeValues = state.filters[col.key];
    if (activeValues) {
      result = result.filter(row => activeValues.has(_colValue(row, col)));
    }
  });

  if (state.sortField) {
    const col = columns.find(c => c.key === state.sortField);
    const dir = state.sortDir === "asc" ? 1 : -1;
    result = [...result].sort((a, b) => {
      const va = col ? _rawColValue(a, col) : "";
      const vb = col ? _rawColValue(b, col) : "";
      return _compareValues(va, vb) * dir;
    });
  }

  return result;
}

/**
 * Potong data sesuai halaman aktif. Otomatis "clamp" page kalau lagi di
 * halaman yang udah gak ada (misal abis filter, datanya jadi lebih sedikit).
 */
function paginate(tableId, data) {
  const state = _getTableState(tableId);
  const totalPages = Math.max(1, Math.ceil(data.length / state.pageSize));
  if (state.page > totalPages) state.page = totalPages;
  if (state.page < 1) state.page = 1;

  const start = (state.page - 1) * state.pageSize;
  return {
    pageData: data.slice(start, start + state.pageSize),
    page: state.page,
    totalPages,
    totalItems: data.length,
  };
}

function paginationControls(tableId, page, totalPages, totalItems) {
  if (totalPages <= 1) return "";
  return `
    <div class="pagination">
      <button class="btn" ${page <= 1 ? "disabled" : ""} onclick="changePage('${tableId}', ${page - 1})">&lsaquo; Sebelumnya</button>
      <span class="pagination-info">Halaman ${page} dari ${totalPages} &mdash; ${totalItems} baris total</span>
      <button class="btn" ${page >= totalPages ? "disabled" : ""} onclick="changePage('${tableId}', ${page + 1})">Selanjutnya &rsaquo;</button>
    </div>
  `;
}

function changePage(tableId, newPage) {
  const state = _getTableState(tableId);
  state.page = newPage;
  if (typeof window.currentTableRefresh === "function") window.currentTableRefresh();
}

/**
 * Bikin markup <th> lengkap (label + caret sort + tombol filter).
 * col = { key: "nama_material", label: "Nama Material", getValue: (row) => ... }
 */
function sortableHeader(tableId, col, alignRight = false) {
  const state = _getTableState(tableId);
  const isSorted = state.sortField === col.key;
  const arrow = isSorted ? (state.sortDir === "asc" ? "&#9650;" : "&#9660;") : "";
  const hasFilter = state.filters[col.key] != null;

  return `
    <th class="${alignRight ? "text-right" : ""}">
      <div class="th-control" style="${alignRight ? "justify-content:flex-end;" : ""}">
        <span class="th-sort-label" onclick="toggleTableSort('${tableId}', '${col.key}')">${col.label} ${arrow}</span>
        <span class="th-filter-btn ${hasFilter ? "active" : ""}" onclick="openFilterDropdown(event, '${tableId}', '${col.key}')">&#9662;</span>
      </div>
    </th>
  `;
}

function toggleTableSort(tableId, field) {
  const state = _getTableState(tableId);
  if (state.sortField === field) {
    state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
  } else {
    state.sortField = field;
    state.sortDir = "asc";
  }
  if (typeof window.currentTableRefresh === "function") window.currentTableRefresh();
}

function openFilterDropdown(event, tableId, field) {
  event.stopPropagation();
  closeFilterDropdown();

  const allData = window.currentTableAllData ? window.currentTableAllData() : [];
  const columns = window.currentTableColumns || [];
  const col = columns.find(c => c.key === field);
  if (!col) return;

  const uniqueValues = [...new Set(allData.map(row => _colValue(row, col)))].sort(_compareValues);
  const state = _getTableState(tableId);
  const activeSet = state.filters[field] || new Set(uniqueValues);

  const dropdown = document.createElement("div");
  dropdown.className = "filter-dropdown";
  dropdown.id = "active-filter-dropdown";
  dropdown.innerHTML = `
    <div class="filter-dropdown-sort">
      <button type="button" onclick="_sortFromDropdown('${tableId}', '${field}', 'asc')">&#9650; A-Z</button>
      <button type="button" onclick="_sortFromDropdown('${tableId}', '${field}', 'desc')">&#9660; Z-A</button>
    </div>
    <div class="filter-dropdown-actions">
      <button type="button" onclick="_filterSelectAll(true)">Pilih Semua</button>
      <button type="button" onclick="_filterSelectAll(false)">Kosongkan</button>
    </div>
    <div class="filter-dropdown-list">
      ${uniqueValues.map(val => `
        <label class="filter-dropdown-item">
          <input type="checkbox" value="${val.replace(/"/g, "&quot;")}" ${activeSet.has(val) ? "checked" : ""} />
          <span>${val}</span>
        </label>
      `).join("")}
    </div>
    <div class="filter-dropdown-footer" style="justify-content:space-between;">
      <button type="button" class="btn" onclick="_resetColumn('${tableId}', '${field}')" style="color:var(--red);">Reset</button>
      <div class="flex gap-2">
        <button type="button" class="btn" onclick="closeFilterDropdown()">Batal</button>
        <button type="button" class="btn btn-primary" onclick="_applyFilterDropdown('${tableId}', '${field}')">Terapkan</button>
      </div>
    </div>
  `;

  document.body.appendChild(dropdown);

  const rect = event.target.getBoundingClientRect();
  const top = rect.bottom + window.scrollY + 4;
  const left = Math.min(rect.left + window.scrollX, window.innerWidth - 272);
  dropdown.style.top = `${top}px`;
  dropdown.style.left = `${left}px`;

  setTimeout(() => document.addEventListener("click", _outsideFilterClick), 0);
}

function _outsideFilterClick(e) {
  const dropdown = document.getElementById("active-filter-dropdown");
  if (dropdown && !dropdown.contains(e.target)) closeFilterDropdown();
}

function closeFilterDropdown() {
  const dropdown = document.getElementById("active-filter-dropdown");
  if (dropdown) dropdown.remove();
  document.removeEventListener("click", _outsideFilterClick);
}

function _resetColumn(tableId, field) {
  const state = _getTableState(tableId);
  delete state.filters[field];
  if (state.sortField === field) {
    state.sortField = null;
    state.sortDir = "asc";
  }
  closeFilterDropdown();
  if (typeof window.currentTableRefresh === "function") window.currentTableRefresh();
}

function _sortFromDropdown(tableId, field, dir) {
  const state = _getTableState(tableId);
  state.sortField = field;
  state.sortDir = dir;
  closeFilterDropdown();
  if (typeof window.currentTableRefresh === "function") window.currentTableRefresh();
}

function _filterSelectAll(checked) {
  const dropdown = document.getElementById("active-filter-dropdown");
  if (!dropdown) return;
  dropdown.querySelectorAll('input[type="checkbox"]').forEach(cb => { cb.checked = checked; });
}

function _applyFilterDropdown(tableId, field) {
  const dropdown = document.getElementById("active-filter-dropdown");
  if (!dropdown) return;

  const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
  const checked = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
  const state = _getTableState(tableId);

  if (checked.length === checkboxes.length) {
    delete state.filters[field]; // semua dicentang = sama aja gak difilter
  } else {
    state.filters[field] = new Set(checked);
  }

  closeFilterDropdown();
  if (typeof window.currentTableRefresh === "function") window.currentTableRefresh();
}
