const PAGE_ROLES = {
  "master-user": ["admin"],
};

function checkPageAccess(activePage) {
  requireAuth();

  const role = getRole();
  const allowed = PAGE_ROLES[activePage];

  if (allowed && !allowed.includes(role)) {
    document.body.innerHTML = `
      <div style="height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg);">
        <div style="text-align:center;padding:40px;">
          <div style="font-size:48px;margin-bottom:16px;">🔒</div>
          <h1 class="heading" style="margin-bottom:8px;">Halaman ini terkunci</h1>
          <p class="text-muted" style="font-size:14px;margin-bottom:24px;">
            Role kamu ("${role}") tidak punya akses ke halaman ini.
          </p>
          <a href="${getPagesRootPrefix()}dashboard.html" class="font-mono text-amber" style="font-size:12px;">&larr; Kembali</a>
        </div>
      </div>
    `;
    return false;
  }
  return true;
}

function renderNav(activePage) {
  if (!checkPageAccess(activePage)) return;

  const nav = document.getElementById("nav");
  if (!nav) return;

  if (!document.querySelector(".hamburger-btn")) {
    const hamburger = document.createElement("div");
    hamburger.className = "hamburger-btn";
    hamburger.innerHTML = hamburgerIcon();
    hamburger.onclick = toggleMobileNav;
    document.body.appendChild(hamburger);

    const overlay = document.createElement("div");
    overlay.className = "mobile-overlay";
    overlay.onclick = closeMobileNav;
    document.body.appendChild(overlay);
  }

  const role = getRole();
  const isAdmin = role === "admin";
  const isHomeActive = activePage === "dashboard";
  const isImportActive = activePage === "upload";
  const isMasterActive = activePage.startsWith("master-");
  const isEvaluasiActive = activePage.startsWith("evaluasi-");
  const isCustomerActive = activePage.startsWith("customer-");
  const isSupplierActive = activePage.startsWith("supplier-");
  const isStockActive = activePage.startsWith("stock-");
  const isProduksiActive = activePage.startsWith("produksi-");

  // Master Pages
  const masterBase = getPagesRootPrefix() + "master/";
  const masterItems = [
    { id: "master-customer", href: masterBase + "customer.html", label: "Customer", icon: customerIcon() },
    { id: "master-supplier", href: masterBase + "supplier.html", label: "Supplier", icon: supplierIcon() },
    { id: "master-jasa", href: masterBase + "jasa.html", label: "Jasa", icon: jasaIcon() },
    { id: "master-kategori", href: masterBase + "kategori.html", label: "Kategori", icon: kategoriIcon() },
    { id: "master-satuan", href: masterBase + "satuan.html", label: "Satuan", icon: satuanIcon() },
    { id: "master-material", href: masterBase + "material.html", label: "Material", icon: materialIcon() },
    { id: "master-kbc", href: masterBase + "kode-barang-customer.html", label: "Kode Barang Cust", icon: kbcIcon() },
    { id: "master-bom", href: masterBase + "bom.html", label: "BOM", icon: bomIcon() },
    { id: "master-barang-jasa", href: masterBase + "barang-jasa.html", label: "Barang Jasa", icon: barangJasaIcon() },
  ];
  if (isAdmin) {
    masterItems.push({ id: "master-user", href: masterBase + "user.html", label: "User", icon: userIcon() });
  }

  // Evaluasi Pages
  const evaluasiBase = getPagesRootPrefix() + "evaluasi/";
  const evaluasiItems = [
    { id: "evaluasi-summary",  href: evaluasiBase + "summary.html", label: "Summary", icon: summaryIcon() },
  ]

  // Customer Pages
  const customerBase = getPagesRootPrefix() + "customer/";
  const customerItems = [
    { id: "customer-summary", href: customerBase + "summary.html", label: "Summary", icon: summaryIcon() },
    { id: "customer-os-po-cust", href: customerBase + "os-po-cust.html", label: "OS PO Customer", icon: osPoCustIcon() },
  ]

  // Supplier Pages
  const supplierBase = getPagesRootPrefix() + "supplier/";
  const supplierItems = [
    { id: "supplier-summary", href: supplierBase + "summary.html", label: "Summary", icon: summaryIcon() },
    { id: "supplier-os", href: supplierBase + "os-supplier.html", label: "O/S Supplier", icon: osPoCustIcon() },
  ]

  // Stock Pages
  const stockBase = getPagesRootPrefix() + "stock/";
  const stockItems = [
    { id: "stock-summary", href: stockBase + "summary.html", label: "Summary", icon: summaryIcon() },
    { id: "stock-material-kurang", href: stockBase + "material-kurang.html", label: "Material Kurang", icon: materialKurangIcon() },
  ]

  // Produksi Pages
  const produksiBase = getPagesRootPrefix() + "produksi/";
  const produksiItems = [
    { id: "produksi-summary", href: produksiBase + "summary.html", label: "Summary", icon: summaryIcon() },
    { id: "produksi-po-cust-spk", href: produksiBase + "po-cust-ada-spk.html", label: "PO Cust + SPK", icon: osPoCustIcon() },
    { id: "produksi-material-spk", href: produksiBase + "material-dibutuhkan-spk.html", label: "Material SPK", icon: materialKebutuhanIcon() },
  ]

  nav.innerHTML = `
    <div class="nav-logo"><span class="logo-text">SGE</span></div>
    <div class="nav-items">

      <a href="${getPagesRootPrefix()}dashboard.html" class="nav-item ${isHomeActive ? "active" : ""}">
        <span class="nav-icon">${homeIcon()}</span>
        <span class="nav-label">Home</span>
      </a>

      <a href="${getPagesRootPrefix()}upload.html" class="nav-item ${isImportActive ? "active" : ""}">
        <span class="nav-icon">${uploadCloudIcon()}</span>
        <span class="nav-label">Import</span>
      </a>

      <!-- Master -->
      <div class="nav-item ${isMasterActive ? "active" : ""}" onclick="toggleSection('master-subs','master-chevron')">
        <span class="nav-icon">${masterIcon()}</span>
        <span class="nav-label" style="flex:1;">Master</span>
        <span class="nav-chevron nav-label" id="master-chevron"
          style="transition:transform 0.2s;${isMasterActive ? "transform:rotate(180deg);" : ""}">
          ${chevronIcon()}
        </span>
      </div>
      <div id="master-subs" class="nav-subs"
        style="display:${isMasterActive ? "flex" : "none"};flex-direction:column;gap:2px;">
        ${masterItems.map(item => subItem(item.href, item.id, activePage, item.label, item.icon)).join("")}
      </div>

      <!-- Evaluasi -->
      <div class="nav-item ${isEvaluasiActive ? "active" : ""}" onclick="toggleSection('evaluasi-subs', 'evaluasi-chevron')">
        <span class="nav-icon">${evaluasiIcon()}</span>
        <span class="nav-label" style="flex:1;">Data Evaluasi</span>
        <span class="nav-chevron nav-label" id="evaluasi-chevron"
          style="transition:transform 0.2s;${isEvaluasiActive ? "transform:rotate(180deg);" : ""}">
          ${chevronIcon()}
        </span>
      </div>
      <div id="evaluasi-subs" class="nav-subs"
        style="display:${isEvaluasiActive ? "flex" : "none"};flex-direction:column;gap:2px;">
        ${evaluasiItems.map(item => subItem(item.href, item.id, activePage, item.label, item.icon)).join("")}
      </div>

      <!-- Customer -->
      <div class="nav-item ${isCustomerActive ? "active" : ""}" onclick="toggleSection('customer-subs', 'customer-chevron')">
        <span class="nav-icon">${customerIcon()}</span>
        <span class="nav-label" style="flex:1;">Customer</span>
        <span class="nav-chevron nav-label" id="customer-chevron"
          style="transition:transform 0.2s;${isCustomerActive ? "transform:rotate(180deg);" : ""}">
          ${chevronIcon()}
        </span>
      </div>
      <div id="customer-subs" class="nav-subs"
        style="display:${isCustomerActive ? "flex" : "none"};flex-direction:column;gap:2px;">
        ${customerItems.map(item => subItem(item.href, item.id, activePage, item.label, item.icon)).join("")}
      </div>

      <!-- Supplier -->
      <div class="nav-item ${isSupplierActive ? "active" : ""}" onclick="toggleSection('supplier-subs', 'supplier-chevron')">
        <span class="nav-icon">${supplierIcon()}</span>
        <span class="nav-label" style="flex:1;">Supplier</span>
        <span class="nav-chevron nav-label" id="supplier-chevron"
          style="transition:transform 0.2s;${isSupplierActive ? "transform:rotate(180deg);" : ""}">
          ${chevronIcon()}
        </span>
      </div>
      <div id="supplier-subs" class="nav-subs"
        style="display:${isSupplierActive ? "flex" : "none"};flex-direction:column;gap:2px;">
        ${supplierItems.map(item => subItem(item.href, item.id, activePage, item.label, item.icon)).join("")}
      </div>

      <!-- Stock -->
      <div class="nav-item ${isStockActive ? "active" : ""}" onclick="toggleSection('stock-subs', 'stock-chevron')">
        <span class="nav-icon">${stockIcon()}</span>
        <span class="nav-label" style="flex:1;">Stock</span>
        <span class="nav-chevron nav-label" id="stock-chevron"
          style="transition:transform 0.2s;${isStockActive ? "transform:rotate(180deg);" : ""}">
          ${chevronIcon()}
        </span>
      </div>
      <div id="stock-subs" class="nav-subs"
        style="display:${isStockActive ? "flex" : "none"};flex-direction:column;gap:2px;">
        ${stockItems.map(item => subItem(item.href, item.id, activePage, item.label, item.icon)).join("")}
      </div>

      <!-- Produksi -->
      <div class="nav-item ${isProduksiActive ? "active" : ""}" onclick="toggleSection('produksi-subs', 'produksi-chevron')">
        <span class="nav-icon">${produksiIcon()}</span>
        <span class="nav-label" style="flex:1;">Produksi</span>
        <span class="nav-chevron nav-label" id="produksi-chevron"
          style="transition:transform 0.2s;${isProduksiActive ? "transform:rotate(180deg);" : ""}">
          ${chevronIcon()}
        </span>
      </div>
      <div id="produksi-subs" class="nav-subs"
        style="display:${isProduksiActive ? "flex" : "none"};flex-direction:column;gap:2px;">
        ${produksiItems.map(item => subItem(item.href, item.id, activePage, item.label, item.icon)).join("")}
      </div>

    </div>
    <div class="nav-footer" onclick="logout()">
      <span class="nav-icon">${logoutIcon()}</span>
      <span class="nav-label">Logout (${getUsername() || ""})</span>
    </div>
  `;
}

function subItem(href, id, activePage, label, icon) {
  return `<a href="${href}" class="nav-sub-item ${activePage === id ? "active" : ""}" title="${label}">
      <span class="nav-sub-icon">${icon}</span>
      <span class="nav-label">${label}</span>
    </a>`;
}

function toggleSection(subsId, chevronId) {
  const subs = document.getElementById(subsId);
  const chevron = document.getElementById(chevronId);
  const isOpen = subs.style.display !== "none";
  subs.style.display = isOpen ? "none" : "flex";
  chevron.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
}

function toggleMobileNav() {
  document.getElementById("nav").classList.toggle("mobile-open");
  document.querySelector(".mobile-overlay").classList.toggle("active");
}

function closeMobileNav() {
  document.getElementById("nav").classList.remove("mobile-open");
  document.querySelector(".mobile-overlay").classList.remove("active");
}
