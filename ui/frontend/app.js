const state = { rows: [], selected: new Set() };
const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed: ${response.status}`);
  return data;
}

function text(node, value, fallback = "—") {
  node.textContent = value || fallback;
}

function renderSummary(summary) {
  const labels = { total: "All candidates", pending: "Pending", approved: "Approved", ignored: "Ignored" };
  $("#summary").innerHTML = Object.entries(labels)
    .map(([key, label]) => `<div class="metric"><span>${label}</span><strong>${summary[key]}</strong></div>`)
    .join("");
}

function updateSelected() {
  $("#selected-count").textContent = `${state.selected.size} selected`;
}

async function review(ids, status) {
  if (!ids.length) return;
  await api("/api/reviews", { method: "POST", body: JSON.stringify({ ids, status }) });
  state.selected.clear();
  updateSelected();
  await load();
}

function makeCard(row) {
  const card = $("#card-template").content.firstElementChild.cloneNode(true);
  text(card.querySelector(".rank"), `Rank ${row.rank}`);
  text(card.querySelector(".grade"), row.rank_grade);
  const status = card.querySelector(".state");
  text(status, row.status);
  status.classList.add(row.status);
  text(card.querySelector(".source"), `${row.source_table}.${row.source_column}`);
  text(card.querySelector(".target"), `${row.target_object_type}.${row.target_property}`);
  text(card.querySelector(".mapping-type"), row.mapping_type);
  text(card.querySelector(".retrieval"), row.retrieval_methods);
  text(card.querySelector(".vector"), row.vector_score);
  text(card.querySelector(".bm25"), row.bm25_score);
  text(card.querySelector(".explanation"), row.explanation);
  text(card.querySelector(".source-definition"), row.source_definition);
  text(card.querySelector(".target-definition"), row.target_definition);
  const checkbox = card.querySelector(".select-row");
  checkbox.checked = state.selected.has(row.id);
  checkbox.addEventListener("change", () => {
    checkbox.checked ? state.selected.add(row.id) : state.selected.delete(row.id);
    updateSelected();
  });
  card.querySelector(".approve").addEventListener("click", () => review([row.id], "approved"));
  card.querySelector(".ignore").addEventListener("click", () => review([row.id], "ignored"));
  card.querySelector(".pending").addEventListener("click", () => review([row.id], "pending"));
  return card;
}

async function load() {
  const q = encodeURIComponent($("#search").value);
  const status = encodeURIComponent($("#status").value);
  $("#notice").textContent = "Loading recommendations…";
  try {
    const [summary, candidates] = await Promise.all([
      api("/api/summary"),
      api(`/api/candidates?q=${q}&status=${status}&limit=1000`),
    ]);
    state.rows = candidates.rows;
    renderSummary(summary);
    const cards = $("#cards");
    cards.replaceChildren(...state.rows.map(makeCard));
    $("#notice").textContent = `${candidates.filtered_total} recommendations shown`;
  } catch (error) {
    $("#notice").textContent = error.message;
  }
}

let debounce;
$("#search").addEventListener("input", () => {
  clearTimeout(debounce);
  debounce = setTimeout(load, 180);
});
$("#status").addEventListener("change", load);
$("#approve-selected").addEventListener("click", () => review([...state.selected], "approved"));
$("#ignore-selected").addEventListener("click", () => review([...state.selected], "ignored"));
$("#reload").addEventListener("click", async () => {
  await api("/api/reload", { method: "POST", body: "{}" });
  await load();
});
load();

