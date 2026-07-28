const state = {
  cases: [],
  caseId: "",
  rows: [],
  summary: { total: 0, pending: 0, approved: 0, ignored: 0 },
  selected: new Set(),
  datasets: [],
};
const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `요청 실패: ${response.status}`);
  return data;
}

function currentCase() {
  return state.cases.find((item) => item.id === state.caseId);
}

function caseQuery(path) {
  const joiner = path.includes("?") ? "&" : "?";
  return `${path}${joiner}case=${encodeURIComponent(state.caseId)}`;
}

function statusLabel(status) {
  return {
    reconstructed: "화면 기반 복구 완료",
    "fixture-ready": "UI 기준선 준비",
    "run-loaded": "실행 결과 로드됨",
    "schema-ready-not-run": "스키마 준비 · 실행 전",
  }[status] || status;
}

function kindLabel(kind) {
  return {
    "international-standard": "CASE 01 · INTERNATIONAL STANDARD",
    "screenshot-guided-reconstruction": "CASE 02 · REFERENCE RECONSTRUCTION",
    "domestic-standardization": "CASE 03 · KOREAN STANDARDIZATION",
  }[kind] || kind;
}

function renderCases() {
  $("#case-tabs").replaceChildren(
    ...state.cases.map((item, index) => {
      const button = document.createElement("button");
      button.className = `case-tab${item.id === state.caseId ? " active" : ""}`;
      button.innerHTML = `<span>0${index + 1}</span><b>${item.short_name}</b><small>${item.language}</small>`;
      button.addEventListener("click", () => switchCase(item.id));
      return button;
    }),
  );
}

function renderCaseBrief() {
  const item = currentCase();
  if (!item) return;
  $("#case-kind").textContent = kindLabel(item.kind);
  $("#case-title").textContent = item.name;
  $("#case-description").textContent = item.description;
  $("#case-status").textContent = statusLabel(item.status);
  $("#result-note").textContent = item.result_note;
}

function renderSummary() {
  const summary = state.summary;
  $("#pending-count").textContent = summary.pending;
  $("#total-count").textContent = `/ ${summary.total}`;
  $("#decision-counts").innerHTML = `
    <span><i class="approved-dot"></i> 승인 ${summary.approved}</span>
    <span><i class="ignored-dot"></i> 무시 ${summary.ignored}</span>
  `;
}

function updateSelected() {
  $("#selected-count").textContent = `${state.selected.size}건 선택`;
}

async function review(ids, status) {
  if (!ids.length) return;
  await api("/api/reviews", {
    method: "POST",
    body: JSON.stringify({ ids, status, case_id: state.caseId }),
  });
  state.selected.clear();
  updateSelected();
  await loadRecommendations();
}

function scoreFor(row) {
  const numeric = Number.parseFloat(row.vector_score);
  return Number.isFinite(numeric) ? Math.round(numeric * 100) : "—";
}

function linkLabel(row) {
  const source = row.source_column.replaceAll("_", " ");
  const target = row.target_property.replaceAll("_", " ");
  return source === target ? "동일 의미" : `${source} 연결`;
}

function makeRow(row) {
  const element = $("#row-template").content.firstElementChild.cloneNode(true);
  element.dataset.status = row.status;
  element.querySelector(".score strong").textContent = scoreFor(row);
  element.querySelector(".from strong").textContent = row.source_column;
  element.querySelector(".from span").textContent = row.source_table;
  element.querySelector(".to strong").textContent = row.target_property;
  element.querySelector(".to span").textContent = row.target_object_type;
  element.querySelector(".link-name strong").textContent = linkLabel(row);
  const grade = element.querySelector(".grade");
  grade.textContent = { High: "높음", Medium: "중간", Low: "낮음" }[row.rank_grade] || row.rank_grade;
  grade.dataset.grade = row.rank_grade.toLowerCase();
  const summary = element.querySelector(".reason summary");
  summary.textContent = row.explanation || "추천 근거 보기";
  element.querySelector(".explanation").textContent = row.explanation || "설명이 없습니다.";
  element.querySelector(".source-definition").textContent = row.source_definition || "—";
  element.querySelector(".target-definition").textContent = row.target_definition || "—";
  element.querySelector(".raw-scores").textContent =
    `순위 ${row.rank} · 검색 방식 ${row.retrieval_methods || "—"} · vector ${row.vector_score || "—"} · BM25 ${row.bm25_score || "—"}`;

  const checkbox = element.querySelector(".select-row");
  checkbox.checked = state.selected.has(row.id);
  checkbox.addEventListener("change", () => {
    checkbox.checked ? state.selected.add(row.id) : state.selected.delete(row.id);
    updateSelected();
  });
  element.querySelector(".approve").addEventListener("click", () => review([row.id], "approved"));
  element.querySelector(".ignore").addEventListener("click", () => review([row.id], "ignored"));
  element.querySelector(".pending").addEventListener("click", () => review([row.id], "pending"));
  return element;
}

async function loadRecommendations() {
  const q = encodeURIComponent($("#search").value);
  const status = encodeURIComponent($("#status").value);
  $("#notice").textContent = "추천을 불러오는 중입니다…";
  try {
    const [summary, candidates] = await Promise.all([
      api(caseQuery("/api/summary")),
      api(caseQuery(`/api/candidates?q=${q}&status=${status}&limit=1000`)),
    ]);
    state.summary = summary;
    state.rows = candidates.rows;
    renderSummary();
    $("#rows").replaceChildren(...state.rows.map(makeRow));
    $("#shown-count").textContent = `${candidates.filtered_total}건 표시`;
    const empty = $("#empty");
    empty.hidden = state.rows.length > 0;
    if (!empty.hidden) {
      const item = currentCase();
      empty.innerHTML = item.status === "schema-ready-not-run"
        ? "<strong>아직 추천 결과가 없습니다.</strong><p>공식 한글 Source·Target 스키마와 초안 정답지만 준비된 상태입니다. 실행 전에는 점수를 표시하지 않습니다.</p>"
        : "<strong>조건에 맞는 추천이 없습니다.</strong><p>검색어나 상태 필터를 변경해보세요.</p>";
    }
    $("#notice").textContent = "";
  } catch (error) {
    $("#notice").textContent = error.message;
  }
}

async function switchCase(caseId) {
  state.caseId = caseId;
  state.selected.clear();
  $("#search").value = "";
  $("#status").value = "all";
  renderCases();
  renderCaseBrief();
  updateSelected();
  await loadRecommendations();
}

function renderDataset(dataset) {
  const content = $("#dataset-content");
  const table = document.createElement("table");
  const head = document.createElement("thead");
  head.innerHTML = `<tr>${dataset.columns.map((column) => `<th>${column}</th>`).join("")}</tr>`;
  const body = document.createElement("tbody");
  dataset.rows.forEach((row) => {
    const tr = document.createElement("tr");
    row.forEach((cell) => {
      const td = document.createElement("td");
      td.textContent = cell;
      tr.append(td);
    });
    body.append(tr);
  });
  table.append(head, body);
  const meta = document.createElement("div");
  meta.className = "dataset-meta";
  meta.innerHTML = `<span>${dataset.role}</span><b>${dataset.name}</b><small>${dataset.format} · ${dataset.rows.length}개 샘플/필드</small>`;
  content.replaceChildren(meta, table);
}

async function openDatasets() {
  const payload = await api(caseQuery("/api/datasets"));
  state.datasets = payload.datasets;
  $("#dataset-title").textContent = `${currentCase().short_name} 데이터셋`;
  $("#dataset-notice").textContent = payload.notice;
  const tabs = $("#dataset-tabs");
  tabs.replaceChildren(
    ...state.datasets.map((dataset, index) => {
      const button = document.createElement("button");
      button.className = `dataset-tab${index === 0 ? " active" : ""}`;
      button.textContent = dataset.name;
      button.setAttribute("role", "tab");
      button.addEventListener("click", () => {
        tabs.querySelectorAll("button").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        renderDataset(dataset);
      });
      return button;
    }),
  );
  if (state.datasets.length) renderDataset(state.datasets[0]);
  $("#dataset-dialog").showModal();
}

async function init() {
  try {
    const payload = await api("/api/cases");
    state.cases = payload.cases;
    state.caseId = state.cases[0].id;
    renderCases();
    renderCaseBrief();
    await loadRecommendations();
  } catch (error) {
    $("#notice").textContent = error.message;
  }
}

let debounce;
$("#search").addEventListener("input", () => {
  clearTimeout(debounce);
  debounce = setTimeout(loadRecommendations, 180);
});
$("#status").addEventListener("change", loadRecommendations);
$("#approve-selected").addEventListener("click", () => review([...state.selected], "approved"));
$("#ignore-selected").addEventListener("click", () => review([...state.selected], "ignored"));
$("#reload").addEventListener("click", async () => {
  await api("/api/reload", { method: "POST", body: JSON.stringify({ case_id: state.caseId }) });
  await loadRecommendations();
});
$("#open-datasets").addEventListener("click", openDatasets);
$("#close-datasets").addEventListener("click", () => $("#dataset-dialog").close());
$("#dataset-dialog").addEventListener("click", (event) => {
  if (event.target === $("#dataset-dialog")) $("#dataset-dialog").close();
});

init();
