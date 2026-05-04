const filters = [
  { id: "all", label: "All" },
  { id: "runtime_pending", label: "Runtime pending" },
  { id: "source_verified", label: "Source verified" },
  { id: "published_checkpoint", label: "Published checkpoint" },
];

const state = {
  filter: "all",
  manifest: null,
};

const statusLabels = {
  available: "Available",
  blocked_missing_runtime_install: "Runtime not installed",
  published_checkpoint: "Published checkpoint",
  runtime_pending: "Runtime pending",
  source_verified: "Source verified",
};

const statusOrder = {
  source_verified: 1,
  available: 2,
  published_checkpoint: 3,
  runtime_pending: 4,
  blocked_missing_runtime_install: 5,
};

const examplesNode = document.querySelector("#examples");
const filtersNode = document.querySelector("#filters");
const summaryNode = document.querySelector("#summary");
const runtimeProbeNode = document.querySelector("#runtimeProbe");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function labelForStatus(status) {
  return statusLabels[status] || status.replaceAll("_", " ");
}

function statusClass(status) {
  return `status status--${status.replaceAll("_", "-")}`;
}

function statusRank(evidence) {
  return evidence
    .map((item) => statusOrder[item.status] || 99)
    .sort((left, right) => left - right)
    .at(-1);
}

function matchesFilter(example) {
  if (state.filter === "all") {
    return true;
  }
  return example.evidence.some((item) => item.status === state.filter);
}

function countEvidence(status) {
  return state.manifest.examples.flatMap((example) => example.evidence).filter((item) => item.status === status).length;
}

function renderSummary() {
  const examples = state.manifest.examples.length;
  const slots = state.manifest.examples.reduce((count, example) => count + example.evidence.length, 0);
  const pending = countEvidence("runtime_pending");
  const checkpointed = countEvidence("published_checkpoint");

  summaryNode.innerHTML = [
    ["Examples", examples],
    ["Evidence slots", slots],
    ["Pending runtime", pending],
    ["Published checkpoints", checkpointed],
  ]
    .map(([label, value]) => `<span><strong>${value}</strong>${label}</span>`)
    .join("");
}

function renderProbe() {
  const probe = state.manifest.runtime_probe;
  runtimeProbeNode.innerHTML = `
    <span class="${statusClass(probe.status)}">${escapeHtml(labelForStatus(probe.status))}</span>
    <code>${escapeHtml(probe.observed)}</code>
  `;
}

function renderFilters() {
  filtersNode.innerHTML = filters
    .map((filter) => {
      const selected = filter.id === state.filter;
      return `
        <button class="filter ${selected ? "filter--active" : ""}" type="button" data-filter="${filter.id}" role="tab" aria-selected="${selected}">
          ${escapeHtml(filter.label)}
        </button>
      `;
    })
    .join("");
}

function renderTags(tags) {
  return tags.map((tag) => `<span>${escapeHtml(tag)}</span>`).join("");
}

function renderEntryPoints(entryPoints) {
  return Object.entries(entryPoints)
    .map(
      ([label, path]) => `
        <div class="fact">
          <dt>${escapeHtml(label)}</dt>
          <dd><code>${escapeHtml(path)}</code></dd>
        </div>
      `
    )
    .join("");
}

function renderEvidence(evidence) {
  return evidence
    .slice()
    .sort((left, right) => (statusOrder[left.status] || 99) - (statusOrder[right.status] || 99))
    .map(
      (item) => `
        <li class="evidence__item">
          <div>
            <strong>${escapeHtml(item.name)}</strong>
            <span class="${statusClass(item.status)}">${escapeHtml(labelForStatus(item.status))}</span>
          </div>
          <p>${escapeHtml(item.detail)}</p>
        </li>
      `
    )
    .join("");
}

function renderCommands(commands) {
  return Object.entries(commands)
    .map(
      ([label, command]) => `
        <div class="command">
          <div class="command__header">
            <strong>${escapeHtml(label)}</strong>
            <button type="button" data-copy="${escapeHtml(command)}">Copy</button>
          </div>
          <pre><code>${escapeHtml(command)}</code></pre>
        </div>
      `
    )
    .join("");
}

function renderArtifacts(artifacts) {
  return artifacts.map((artifact) => `<li><code>${escapeHtml(artifact)}</code></li>`).join("");
}

function renderExamples() {
  const examples = state.manifest.examples
    .filter(matchesFilter)
    .slice()
    .sort((left, right) => statusRank(left.evidence) - statusRank(right.evidence));

  examplesNode.innerHTML = examples
    .map(
      (example) => `
        <article class="card">
          <div class="card__media">
            <img src="${escapeHtml(example.image)}" alt="${escapeHtml(example.alt)}">
          </div>
          <div class="card__body">
            <div class="card__heading">
              <div>
                <p class="eyebrow">${escapeHtml(example.category)}</p>
                <h3>${escapeHtml(example.title)}</h3>
              </div>
              <span class="task">${escapeHtml(example.task)}</span>
            </div>
            <div class="tags">${renderTags(example.tags)}</div>
            <dl class="facts">${renderEntryPoints(example.entry_points)}</dl>
            <ul class="evidence">${renderEvidence(example.evidence)}</ul>
            <div class="commands">${renderCommands(example.commands)}</div>
            <details class="artifacts">
              <summary>Expected artifacts</summary>
              <ul>${renderArtifacts(example.artifacts)}</ul>
            </details>
          </div>
        </article>
      `
    )
    .join("");
}

function render() {
  renderSummary();
  renderProbe();
  renderFilters();
  renderExamples();
}

filtersNode.addEventListener("click", (event) => {
  const button = event.target.closest("[data-filter]");
  if (!button) {
    return;
  }
  state.filter = button.dataset.filter;
  render();
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy]");
  if (!button) {
    return;
  }

  try {
    await navigator.clipboard.writeText(button.dataset.copy);
    button.textContent = "Copied";
    window.setTimeout(() => {
      button.textContent = "Copy";
    }, 1200);
  } catch {
    button.textContent = "Select text";
  }
});

fetch("manifest.json")
  .then((response) => {
    if (!response.ok) {
      throw new Error(`Unable to load manifest: ${response.status}`);
    }
    return response.json();
  })
  .then((manifest) => {
    state.manifest = manifest;
    render();
  })
  .catch((error) => {
    examplesNode.innerHTML = `<p class="load-error">${escapeHtml(error.message)}</p>`;
  });
