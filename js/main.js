/* ============================================================
   렌더링 로직 — data.js(PROFILE, UI, PROJECTS)를 화면에 그린다
   · 다국어: T(v) 가 { ko, en } 값에서 현재 언어를 선택 (평문 값은 그대로)
   · 언어는 localStorage("lang")에 저장, 기본 KO, 전환 시 리로드 없이 재렌더링
   ============================================================ */
(function () {
  const $ = (sel) => document.querySelector(sel);
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ── 언어 상태 ── */
  let lang = localStorage.getItem("lang") === "en" ? "en" : "ko";
  const T = (v) =>
    v && typeof v === "object" && !Array.isArray(v) && "ko" in v ? v[lang] : v;
  const tagLabel = (t) => (UI.tagLabels[t] ? T(UI.tagLabels[t]) : t);

  /* ── 필터·모달 상태 (언어 전환 간 유지) ── */
  const ALL = "__all__";
  const tagOrder = ["AI Engineering", "DS·ML", "RPA·자동화", "Data Eng"];
  const tagCount = {};
  PROJECTS.forEach((p) => p.tags.forEach((t) => (tagCount[t] = (tagCount[t] || 0) + 1)));
  let current = ALL;
  let openProject = null;
  let lastFocus = null;

  const modal = $("#modal");
  const modalBody = $("#modal-body");
  const grid = $("#grid");
  const filtersEl = $("#filters");

  /* ── 히어로 ── */
  function renderHero() {
    $("#hero-tag").textContent = PROFILE.heroTag;
    $("#hero-name-ko").textContent = PROFILE.nameKo;
    $("#hero-name-en").textContent = PROFILE.nameEn;
    $("#hero-tagline").textContent = T(PROFILE.tagline);
    $("#hero-about").innerHTML = T(PROFILE.about).map((t) => `<p>${esc(t)}</p>`).join("");

    $("#journey").innerHTML = PROFILE.journey
      .map(
        (j) => `<div class="journey-node">
          <div class="journey-label">${esc(T(j.label))}</div>
          <div class="journey-sub">${esc(T(j.sub))}</div>
        </div>`
      )
      .join("");

    $("#hero-links").innerHTML = `
      <a class="btn" href="${esc(PROFILE.github)}" target="_blank" rel="noopener">GitHub ↗</a>
      <a class="btn" href="${esc(PROFILE.linkedin)}" target="_blank" rel="noopener">LinkedIn ↗</a>
      <a class="btn" href="mailto:${esc(PROFILE.email)}">${esc(T(UI.emailBtn))}</a>`;

    $("#careers").innerHTML = PROFILE.careers
      .map(
        (c) => `<div class="career-item">
          <div class="career-period">${esc(T(c.period))}</div>
          <div class="career-org">${esc(T(c.org))}</div>
          <div class="career-role">${esc(T(c.role))}</div>
        </div>`
      )
      .join("");
  }

  /* ── 푸터 ── */
  function renderFooter() {
    $("#footer-name").textContent = `${T(PROFILE.name)} · ${PROFILE.heroTag}`;
    $("#footer-meta").textContent = `${T(PROFILE.location)} · ${PROFILE.email}`;
    $("#footer-actions").innerHTML = `
      ${PROFILE.resume ? `<a class="btn btn-primary" href="${esc(PROFILE.resume)}" download>${esc(T(UI.resumeBtn))}</a>` : ""}
      <a class="btn" href="${esc(PROFILE.github)}" target="_blank" rel="noopener">GitHub ↗</a>`;
  }

  /* ── 필터 ── */
  function renderFilters() {
    const buttons = [ALL, ...tagOrder.filter((t) => tagCount[t])];
    filtersEl.innerHTML = buttons
      .map((t) => {
        const n = t === ALL ? PROJECTS.length : tagCount[t];
        const label = t === ALL ? T(UI.filterAll) : tagLabel(t);
        return `<button class="filter-btn${t === current ? " active" : ""}" data-tag="${esc(t)}">
          ${esc(label)}<span class="count">${n}</span></button>`;
      })
      .join("");
  }

  filtersEl.addEventListener("click", (e) => {
    const btn = e.target.closest(".filter-btn");
    if (!btn) return;
    current = btn.dataset.tag;
    filtersEl.querySelectorAll(".filter-btn").forEach((b) =>
      b.classList.toggle("active", b.dataset.tag === current));
    renderGrid();
  });

  /* ── 카드 그리드 ── */
  function renderGrid() {
    const list = current === ALL ? PROJECTS : PROJECTS.filter((p) => p.tags.includes(current));
    grid.innerHTML = list
      .map(
        (p) => `<button class="card" data-id="${esc(p.id)}" aria-haspopup="dialog">
          <div class="card-cat">${esc(T(p.catLabel))}</div>
          <div class="card-title">${esc(T(p.title))}</div>
          ${p.subtitle ? `<div class="card-sub">${esc(T(p.subtitle))}</div>` : ""}
          <div class="card-one">${esc(T(p.oneLiner))}</div>
          <div class="card-foot">
            ${p.tags.map((t) => `<span class="chip chip-tag">${esc(tagLabel(t))}</span>`).join("")}
            ${p.period ? `<span class="card-period">${esc(p.period)}</span>` : ""}
          </div>
        </button>`
      )
      .join("");
  }

  grid.addEventListener("click", (e) => {
    const card = e.target.closest(".card");
    if (!card) return;
    lastFocus = document.activeElement;
    openModal(PROJECTS.find((p) => p.id === card.dataset.id));
  });

  /* ── 모달 ── */
  function openModal(p) {
    if (!p) return;
    openProject = p;
    const pdfText = p.pdf
      ? lang === "ko" ? `${T(p.pdf.label)} 보기 ↗` : `View ${T(p.pdf.label)} ↗`
      : "";
    modalBody.innerHTML = `
      <div class="m-cat">${esc(T(p.catLabel))}</div>
      <h2 class="m-title" id="modal-title">${esc(T(p.title))}</h2>
      ${p.subtitle ? `<p class="m-sub">${esc(T(p.subtitle))}</p>` : ""}
      <div class="m-meta">
        ${p.tags.map((t) => `<span class="chip chip-tag">${esc(tagLabel(t))}</span>`).join("")}
        ${p.period ? `<span class="chip">${esc(p.period)}</span>` : ""}
      </div>
      <p class="m-one">${esc(T(p.oneLiner))}</p>

      <div class="m-section">
        <h3>${esc(T(UI.problemH))}</h3>
        <p>${esc(T(p.problem))}</p>
      </div>

      <div class="m-section">
        <h3>${esc(T(UI.roleH))}</h3>
        ${p.roleIntro ? `<p class="m-role-intro">${esc(T(p.roleIntro))}</p>` : ""}
        <ul class="m-list">${T(p.role).map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      </div>

      ${
        p.diagrams && p.diagrams.length
          ? `<div class="m-section"><h3>${esc(T(UI.archH))}</h3>
             ${p.diagrams
               .map(
                 (d) => `<figure class="m-diagram">
                   <img src="${esc(d.src)}" alt="${esc(T(d.cap))}" loading="lazy" />
                   <figcaption>${esc(T(d.cap))}</figcaption>
                 </figure>`
               )
               .join("")}</div>`
          : ""
      }

      <div class="m-section">
        <h3>${esc(T(UI.stackH))}</h3>
        <div class="m-stack">${T(p.stack).map((s) => `<span class="chip">${esc(s)}</span>`).join("")}</div>
      </div>

      <div class="m-section">
        <h3>${esc(T(UI.resultsH))}</h3>
        <ul class="m-list m-results">${T(p.results).map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      </div>

      ${p.pdf ? `<div class="m-section"><a class="btn btn-primary" href="${esc(p.pdf.file)}" target="_blank" rel="noopener">${esc(pdfText)}</a></div>` : ""}
      ${p.privateNote ? `<p class="m-private">${esc(T(p.privateNote))}</p>` : ""}
    `;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    modal.querySelector(".modal-close").focus();
  }

  function closeModal() {
    openProject = null;
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    if (lastFocus) lastFocus.focus();
  }

  modal.addEventListener("click", (e) => {
    if (e.target.matches("[data-close]")) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.hidden) closeModal();
  });

  /* ── 언어 토글 ── */
  const langToggle = $("#lang-toggle");

  function renderAll() {
    document.documentElement.lang = lang;
    langToggle.querySelectorAll(".lang-btn").forEach((b) =>
      b.classList.toggle("active", b.dataset.lang === lang));
    $("#section-sub").textContent = T(UI.sectionSub);
    $(".modal-close").setAttribute("aria-label", T(UI.closeAria));
    renderHero();
    renderFooter();
    renderFilters();
    renderGrid();
    if (openProject) openModal(openProject);   // 모달이 열려 있으면 현재 언어로 재렌더링
  }

  langToggle.addEventListener("click", (e) => {
    const btn = e.target.closest(".lang-btn");
    if (!btn || btn.dataset.lang === lang) return;
    lang = btn.dataset.lang;
    localStorage.setItem("lang", lang);
    renderAll();
  });

  /* ── 프로필 사진 (언어 무관, 1회) ── */
  const heroPhoto = $("#hero-photo");
  heroPhoto.src = PROFILE.photo;
  heroPhoto.onerror = () => heroPhoto.classList.add("hidden");

  $("#projects-heading").setAttribute("data-count", String(PROJECTS.length).padStart(2, "0"));

  renderAll();
})();
