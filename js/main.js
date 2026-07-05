/* ============================================================
   렌더링 로직 — data.js(PROFILE, PROJECTS)를 화면에 그린다
   ============================================================ */
(function () {
  const $ = (sel) => document.querySelector(sel);
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ── 히어로 ── */
  $("#hero-tag").textContent = PROFILE.heroTag;
  $("#hero-name-ko").textContent = PROFILE.name;
  $("#hero-name-en").textContent = PROFILE.nameEn;
  $("#hero-tagline").textContent = PROFILE.tagline;
  $("#hero-about").innerHTML = PROFILE.about.map((t) => `<p>${esc(t)}</p>`).join("");

  $("#journey").innerHTML = PROFILE.journey
    .map(
      (j) => `<div class="journey-node">
        <div class="journey-label">${esc(j.label)}</div>
        <div class="journey-sub">${esc(j.sub)}</div>
      </div>`
    )
    .join("");

  $("#hero-links").innerHTML = `
    <a class="btn" href="${esc(PROFILE.github)}" target="_blank" rel="noopener">GitHub ↗</a>
    <a class="btn" href="${esc(PROFILE.linkedin)}" target="_blank" rel="noopener">LinkedIn ↗</a>
    <a class="btn" href="mailto:${esc(PROFILE.email)}">이메일 보내기</a>`;

  /* ── 히어로 오른쪽 열: 프로필 사진 + 경력 타임라인 ── */
  const heroPhoto = $("#hero-photo");
  heroPhoto.src = PROFILE.photo;
  heroPhoto.onerror = () => heroPhoto.classList.add("hidden");

  $("#careers").innerHTML = PROFILE.careers
    .map(
      (c) => `<div class="career-item">
        <div class="career-period">${esc(c.period)}</div>
        <div class="career-org">${esc(c.org)}</div>
        <div class="career-role">${esc(c.role)}</div>
      </div>`
    )
    .join("");

  /* ── 푸터 ── */
  $("#footer-name").textContent = `${PROFILE.name} · ${PROFILE.heroTag}`;
  $("#footer-meta").textContent = `${PROFILE.location} · ${PROFILE.email}`;
  $("#footer-actions").innerHTML = `
    ${PROFILE.resume ? `<a class="btn btn-primary" href="${esc(PROFILE.resume)}" download>이력서 PDF 다운로드</a>` : ""}
    <a class="btn" href="${esc(PROFILE.github)}" target="_blank" rel="noopener">GitHub ↗</a>`;

  /* ── 필터 ── */
  const ALL = "전체";
  const tagOrder = ["AI Engineering", "DS·ML", "RPA·자동화", "Data Eng"];
  const tagCount = {};
  PROJECTS.forEach((p) => p.tags.forEach((t) => (tagCount[t] = (tagCount[t] || 0) + 1)));

  let current = ALL;
  const filtersEl = $("#filters");
  const buttons = [ALL, ...tagOrder.filter((t) => tagCount[t])];
  filtersEl.innerHTML = buttons
    .map((t) => {
      const n = t === ALL ? PROJECTS.length : tagCount[t];
      return `<button class="filter-btn${t === current ? " active" : ""}" data-tag="${esc(t)}">
        ${esc(t)}<span class="count">${n}</span></button>`;
    })
    .join("");

  filtersEl.addEventListener("click", (e) => {
    const btn = e.target.closest(".filter-btn");
    if (!btn) return;
    current = btn.dataset.tag;
    filtersEl.querySelectorAll(".filter-btn").forEach((b) =>
      b.classList.toggle("active", b.dataset.tag === current));
    renderGrid();
  });

  /* ── 카드 그리드 ── */
  const grid = $("#grid");
  $("#projects-heading").setAttribute("data-count", String(PROJECTS.length).padStart(2, "0"));

  function renderGrid() {
    const list = current === ALL ? PROJECTS : PROJECTS.filter((p) => p.tags.includes(current));
    grid.innerHTML = list
      .map(
        (p) => `<button class="card" data-id="${esc(p.id)}" aria-haspopup="dialog">
          <div class="card-cat">${esc(p.catLabel)}</div>
          <div class="card-title">${esc(p.title)}</div>
          ${p.subtitle ? `<div class="card-sub">${esc(p.subtitle)}</div>` : ""}
          <div class="card-one">${esc(p.oneLiner)}</div>
          <div class="card-foot">
            ${p.tags.map((t) => `<span class="chip chip-tag">${esc(t)}</span>`).join("")}
            ${p.period ? `<span class="card-period">${esc(p.period)}</span>` : ""}
          </div>
        </button>`
      )
      .join("");
  }
  renderGrid();

  /* ── 모달 ── */
  const modal = $("#modal");
  const modalBody = $("#modal-body");
  let lastFocus = null;

  grid.addEventListener("click", (e) => {
    const card = e.target.closest(".card");
    if (!card) return;
    openModal(PROJECTS.find((p) => p.id === card.dataset.id));
  });

  function openModal(p) {
    if (!p) return;
    lastFocus = document.activeElement;
    modalBody.innerHTML = `
      <div class="m-cat">${esc(p.catLabel)}</div>
      <h2 class="m-title" id="modal-title">${esc(p.title)}</h2>
      ${p.subtitle ? `<p class="m-sub">${esc(p.subtitle)}</p>` : ""}
      <div class="m-meta">
        ${p.tags.map((t) => `<span class="chip chip-tag">${esc(t)}</span>`).join("")}
        ${p.period ? `<span class="chip">${esc(p.period)}</span>` : ""}
      </div>
      <p class="m-one">${esc(p.oneLiner)}</p>

      <div class="m-section">
        <h3>문제 / 배경</h3>
        <p>${esc(p.problem)}</p>
      </div>

      <div class="m-section">
        <h3>내 역할 · 구현</h3>
        ${p.roleIntro ? `<p class="m-role-intro">${esc(p.roleIntro)}</p>` : ""}
        <ul class="m-list">${p.role.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      </div>

      ${
        p.diagrams && p.diagrams.length
          ? `<div class="m-section"><h3>아키텍처 · 흐름</h3>
             ${p.diagrams
               .map(
                 (d) => `<figure class="m-diagram">
                   <img src="${esc(d.src)}" alt="${esc(d.cap)}" loading="lazy" />
                   <figcaption>${esc(d.cap)}</figcaption>
                 </figure>`
               )
               .join("")}</div>`
          : ""
      }

      <div class="m-section">
        <h3>기술 스택</h3>
        <div class="m-stack">${p.stack.map((s) => `<span class="chip">${esc(s)}</span>`).join("")}</div>
      </div>

      <div class="m-section">
        <h3>결과 · 임팩트</h3>
        <ul class="m-list m-results">${p.results.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      </div>

      ${p.pdf ? `<div class="m-section"><a class="btn btn-primary" href="${esc(p.pdf.file)}" target="_blank" rel="noopener">${esc(p.pdf.label)} 보기 ↗</a></div>` : ""}
      ${p.privateNote ? `<p class="m-private">${esc(p.privateNote)}</p>` : ""}
    `;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    modal.querySelector(".modal-close").focus();
  }

  function closeModal() {
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
})();
