const state = {
  cases: [],
  caseId: "",
  rows: [],
  summary: { total: 0, pending: 0, approved: 0, ignored: 0 },
  selected: new Set(),
  datasets: [],
  viewMode: "schemora",
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
    "pipeline-ready-not-run": "SCHEMORA 연결 완료 · 실행 전",
    "schemora-results-loaded": "SCHEMORA 결과 로드됨",
    "schema-ready-not-run": "스키마 준비 · 실행 전",
  }[status] || status;
}

function kindLabel(kind) {
  return {
    "screenshot-guided-reconstruction": "C2 DEMO · OBSERVABLE REFERENCE COMPARISON",
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
  $("#result-mode").hidden = false;
  $("#result-mode").querySelectorAll("button").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === state.viewMode);
  });
  renderScoreGuide();
}

function renderScoreGuide() {
  const reference = state.viewMode === "reference";
  $("#score-guide-kicker").textContent = reference
    ? "REFERENCE DISPLAY RULE"
    : "SCHEMORA DISPLAY RULE";
  $("#score-guide-title").textContent = reference
    ? "원 화면의 표시값을 그대로 보존"
    : "세 신호를 RRF로 결합한 전역 검토 우선순위";
  $("#score-column-label").textContent = reference ? "표시 점수" : "RRF 우선순위";
  $("#grade-column-label").textContent = reference ? "표시 등급" : "신호 합의";
  const points = reference
    ? [
      "점수는 원 데모 화면에 보인 95·47 등의 숫자입니다. 산식·정규화·확률 보정 방식은 공개되지 않았습니다.",
      "표시 등급은 원 화면의 구간(높음 ≥90, 중간 70–89, 낮음 <70)을 따릅니다. 모델 확률로 해석하지 않습니다.",
      "9건은 화면에서 완전히 보인 후보만 기록한 읽기 전용 관찰값이며, 저장 정답이나 전체 16건을 뜻하지 않습니다.",
    ]
    : [
      "후보는 LLM·Vector·BM25의 질의 내 순위를 동일 가중치 RRF(k=60)로 결합한 점수 내림차순입니다.",
      "Vector와 BM25 원점수는 단위가 달라 직접 합산하지 않습니다. 검색 결과에 없는 신호의 RRF 기여는 0입니다.",
      "RRF 값은 정확도나 신뢰확률이 아닙니다. 같은 순위 패턴은 공동순위이며, 3/3·2/3 표시는 기여한 신호 수입니다.",
    ];
  $("#score-guide-points").replaceChildren(
    ...points.map((text) => {
      const item = document.createElement("li");
      item.textContent = text;
      return item;
    }),
  );
}

function renderSummary() {
  const summary = state.summary;
  $("#pending-count").textContent = summary.pending;
  $("#total-count").textContent = `/ ${summary.total}`;
  $("#decision-counts").innerHTML = `
    <span><i class="approved-dot"></i> 승인 ${summary.approved}</span>
    <span><i class="ignored-dot"></i> 무시 ${summary.ignored}</span>
  `;
  const readOnly = state.viewMode === "reference";
  $("#summary-label").textContent = readOnly ? "관찰 후보 · 읽기 전용" : "검토 대기";
  $(".bulk").hidden = readOnly;
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
  if (row.reference) return row.original_score;
  const numeric = Number.parseFloat(row.global_priority_score);
  return Number.isFinite(numeric) ? numeric.toFixed(1) : "—";
}

function linkLabel(row) {
  if (row.link_name) return row.link_name;
  const source = row.source_column.replaceAll("_", " ");
  const target = row.target_property.replaceAll("_", " ");
  return source === target ? "동일 의미" : `${source} 연결`;
}

function makeRow(row) {
  const element = $("#row-template").content.firstElementChild.cloneNode(true);
  element.dataset.status = row.status;
  element.querySelector(".score strong").textContent = scoreFor(row);
  element.querySelector(".score small").textContent = row.reference
    ? "원 데모 점수"
    : `검토 #${row.global_priority_rank}`;
  element.querySelector(".from strong").textContent = row.source_column;
  element.querySelector(".from span").textContent = row.source_table;
  element.querySelector(".to strong").textContent = row.target_property;
  element.querySelector(".to span").textContent = row.target_object_type;
  element.querySelector(".link-name strong").textContent = linkLabel(row);
  const grade = element.querySelector(".grade");
  grade.textContent = row.reference
    ? row.reference_confidence
    : `${row.contributing_signals}/3 신호`;
  grade.dataset.grade = row.reference
    ? row.rank_grade.toLowerCase()
    : ({ 3: "high", 2: "medium", 1: "low" }[row.contributing_signals] || "low");
  const summary = element.querySelector(".reason summary");
  summary.textContent = row.explanation || "추천 근거 보기";
  element.querySelector(".explanation").textContent = row.explanation || "설명이 없습니다.";
  element.querySelector(".source-definition").textContent = row.source_definition || "—";
  element.querySelector(".target-definition").textContent = row.target_definition || "—";
  element.querySelector(".raw-scores").textContent = row.reference
    ? `화면 표시 순서 ${row.rank} · 원 데모 점수 ${row.original_score} · 점수 산식과 보정 방식은 공개되지 않음`
    : `표시 순번 ${row.display_order} · 공동 검토 순위 ${row.global_priority_rank} · RRF ${row.global_priority_score} · LLM 질의 순위 ${row.llm_query_rank} · vector ${row.vector_score || "—"} (#${row.vector_query_rank || "—"}) · BM25 ${row.bm25_score || "—"} (#${row.bm25_query_rank || "—"}) · 정확도·신뢰확률이 아님`;

  const checkbox = element.querySelector(".select-row");
  checkbox.checked = state.selected.has(row.id);
  checkbox.addEventListener("change", () => {
    checkbox.checked ? state.selected.add(row.id) : state.selected.delete(row.id);
    updateSelected();
  });
  if (row.reference) {
    checkbox.disabled = true;
    element.querySelector(".actions").innerHTML = "<span class=\"read-only\">관찰값</span>";
  } else {
    element.querySelector(".approve").addEventListener("click", () => review([row.id], "approved"));
    element.querySelector(".ignore").addEventListener("click", () => review([row.id], "ignored"));
    element.querySelector(".pending").addEventListener("click", () => review([row.id], "pending"));
  }
  return element;
}

async function loadRecommendations() {
  const q = encodeURIComponent($("#search").value);
  const status = encodeURIComponent($("#status").value);
  $("#notice").textContent = "추천을 불러오는 중입니다…";
  try {
    if (state.viewMode === "reference") {
      const payload = await api(caseQuery("/api/reference"));
      state.rows = payload.candidates.map((row) => ({
        id: `observable-${row.visible_order}`,
        reference: true,
        original_score: row.score,
        source_table: row.from_table,
        source_column: row.from_field,
        target_object_type: row.to_table,
        target_property: row.to_field,
        link_name: row.link_name,
        rank: row.visible_order,
        rank_grade: row.confidence === "높음" ? "High" : "Low",
        reference_confidence: row.confidence,
        explanation: row.visible_reason,
        source_definition: "사진의 From 열에서 직접 관찰된 필드",
        target_definition: "사진의 To 열에서 직접 관찰된 필드",
        status: "reference",
      }));
      state.summary = {
        total: state.rows.length,
        pending: state.rows.length,
        approved: 0,
        ignored: 0,
      };
      renderSummary();
      $("#rows").replaceChildren(...state.rows.map(makeRow));
      $(".table-shell").hidden = false;
      $("#shown-count").textContent = `${state.rows.length}건 표시 · 화면상 전체 16건 중 완전 가시 9건`;
      $("#empty").hidden = true;
      $("#notice").textContent = "설명은 사진에서 보이는 지점까지만 기록했으며 숨은 문장을 완성하지 않았습니다.";
      return;
    }
    const [summary, candidates] = await Promise.all([
      api(caseQuery("/api/summary")),
      api(caseQuery(`/api/candidates?q=${q}&status=${status}&limit=1000`)),
    ]);
    state.summary = summary;
    state.rows = candidates.rows;
    renderSummary();
    $("#rows").replaceChildren(...state.rows.map(makeRow));
    $(".table-shell").hidden = state.rows.length === 0;
    $("#shown-count").textContent = `${candidates.filtered_total}건 표시`;
    const empty = $("#empty");
    empty.hidden = state.rows.length > 0;
    if (!empty.hidden) {
      const item = currentCase();
      empty.innerHTML = ["schema-ready-not-run", "pipeline-ready-not-run"].includes(item.status)
        ? "<strong>아직 SCHEMORA 추천 결과가 없습니다.</strong><p>5개 온톨로지 입력과 고정 실행 파이프라인은 준비됐지만 변환된 실제 결과 파일이 없습니다. Reference 탭의 관찰값은 모델 결과가 아닙니다.</p>"
        : "<strong>조건에 맞는 추천이 없습니다.</strong><p>검색어나 상태 필터를 변경해보세요.</p>";
    }
    $("#notice").textContent = "";
  } catch (error) {
    $("#notice").textContent = error.message;
  }
}

async function switchCase(caseId) {
  state.caseId = caseId;
  state.viewMode = "reference";
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
    const params = new URLSearchParams(window.location.search);
    const requestedCase = params.get("case");
    state.caseId = state.cases.some((item) => item.id === requestedCase)
      ? requestedCase
      : state.cases[0].id;
    state.viewMode = params.get("mode") === "schemora" ? "schemora" : "reference";
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
$("#result-mode").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-mode]");
  if (!button) return;
  state.viewMode = button.dataset.mode;
  state.selected.clear();
  renderCaseBrief();
  updateSelected();
  await loadRecommendations();
});
$("#dataset-dialog").addEventListener("click", (event) => {
  if (event.target === $("#dataset-dialog")) $("#dataset-dialog").close();
});

init();
