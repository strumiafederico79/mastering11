let wave = null;

const els = {
  file: document.getElementById('file'),
  btn: document.getElementById('masterBtn'),
  profile: document.getElementById('profile'),
  state: document.getElementById('state'),
  pluginBackend: document.getElementById('pluginBackend'),
  issues: document.getElementById('issues'),
  actions: document.getElementById('actions'),
  analysisBox: document.getElementById('analysisBox'),
  decisionBox: document.getElementById('decisionBox'),
  progressBar: document.getElementById('progressBar'),
  progressLabel: document.getElementById('progressLabel'),
  statusText: document.getElementById('statusText'),
  downloads: document.getElementById('downloads'),
  downloadWav: document.getElementById('downloadWav'),
  downloadMp3: document.getElementById('downloadMp3'),
  stepQueued: document.getElementById('stepQueued'),
  stepAnalyze: document.getElementById('stepAnalyze'),
  stepProcess: document.getElementById('stepProcess'),
  stepExport: document.getElementById('stepExport'),
  stepDone: document.getElementById('stepDone'),
  isotopeGrid: document.getElementById('isotopeGrid'),
  filters: document.querySelectorAll('.filter'),
  sorts: document.querySelectorAll('.sort'),
};

function setSteps(progress, status) {
  [els.stepQueued, els.stepAnalyze, els.stepProcess, els.stepExport, els.stepDone].forEach(x => x.classList.remove('active'));
  if (progress >= 0) els.stepQueued.classList.add('active');
  if (progress >= 15) els.stepAnalyze.classList.add('active');
  if (progress >= 45) els.stepProcess.classList.add('active');
  if (progress >= 75) els.stepExport.classList.add('active');
  if (status === 'done') els.stepDone.classList.add('active');
}

function updateProgress(progress) {
  const normalized = Math.max(2, progress || 0);
  els.progressBar.style.width = `${normalized}%`;
  els.progressLabel.textContent = `${Math.round(normalized)}%`;
}

function applyFilter(filterValue) {
  const cards = [...els.isotopeGrid.querySelectorAll('.iso-card')];
  cards.forEach(card => {
    const group = card.dataset.group;
    const shouldShow = filterValue === 'all' || group === filterValue;
    card.classList.toggle('hidden-card', !shouldShow);
  });
}

function applySort(sortType) {
  const cards = [...els.isotopeGrid.querySelectorAll('.iso-card')];
  cards.sort((a, b) => {
    if (sortType === 'score') {
      return Number(b.dataset.score) - Number(a.dataset.score);
    }
    return 0;
  });
  cards.forEach(card => els.isotopeGrid.appendChild(card));
}

function initToolbar() {
  els.filters.forEach(button => {
    button.addEventListener('click', () => {
      els.filters.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      applyFilter(button.dataset.filter);
    });
  });

  els.sorts.forEach(button => {
    button.addEventListener('click', () => {
      els.sorts.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      applySort(button.dataset.sort);
    });
  });
}

async function refreshPluginInfo() {
  try {
    const res = await fetch('/api/plugins');
    const data = await res.json();
    if (data.ladspa_filter) els.pluginBackend.textContent = 'ladspa/native';
    else if (data.lv2_filter) els.pluginBackend.textContent = 'lv2/native';
    else els.pluginBackend.textContent = 'native';
  } catch (_) {
    els.pluginBackend.textContent = 'native';
  }
}

function renderWave(file) {
  if (wave) wave.destroy();
  wave = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#4052ad',
    progressColor: '#6b7cff',
    cursorColor: '#21d0ff',
    height: 138,
    barWidth: 2,
    barGap: 1,
    responsive: true,
  });
  wave.loadBlob(file);
}

function renderIssues(list) {
  els.issues.innerHTML = '';
  (list || []).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    els.issues.appendChild(li);
  });
}

function renderActions(chain, decision) {
  els.actions.innerHTML = '';
  const actions = (chain && chain.actions) ? chain.actions : [];
  if (actions.length) {
    actions.forEach(a => {
      const li = document.createElement('li');
      li.textContent = JSON.stringify(a);
      els.actions.appendChild(li);
    });
  } else if (decision && decision.actions) {
    decision.actions.forEach(a => {
      const li = document.createElement('li');
      li.textContent = a;
      els.actions.appendChild(li);
    });
  }
}

async function uploadFile() {
  const file = els.file.files[0];
  if (!file) {
    els.statusText.textContent = 'Seleccioná un archivo primero.';
    return;
  }

  renderWave(file);
  els.btn.disabled = true;
  els.statusText.textContent = 'Subiendo...';
  els.downloads.classList.add('hidden');
  updateProgress(2);

  const form = new FormData();
  form.append('file', file);
  form.append('mode', 'human_master');

  try {
    const res = await fetch('/api/jobs', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    await pollJob(data.job_id);
  } catch (err) {
    console.error(err);
    els.statusText.textContent = 'Error al subir: ' + err.message;
  } finally {
    els.btn.disabled = false;
  }
}

async function pollJob(jobId) {
  for (let i = 0; i < 600; i++) {
    const res = await fetch(`/api/jobs/${jobId}`);
    const data = await res.json();

    els.state.textContent = data.status || '-';
    els.profile.textContent = data.profile || 'Human Master';
    els.analysisBox.textContent = JSON.stringify(data.analysis || {}, null, 2);
    els.decisionBox.textContent = JSON.stringify(data.decision || {}, null, 2);
    renderIssues(data.issues || []);
    renderActions(data.chain || {}, data.decision || {});
    updateProgress(data.progress || 0);
    els.statusText.textContent = data.message || '';
    setSteps(data.progress || 0, data.status || 'queued');

    if (data.status === 'done') {
      els.downloadWav.href = `/api/jobs/${jobId}/download?fmt=wav`;
      els.downloadMp3.href = `/api/jobs/${jobId}/download?fmt=mp3`;
      els.downloads.classList.remove('hidden');
      return;
    }
    if (data.status === 'error') {
      throw new Error(data.error || 'Error en mastering');
    }
    await new Promise(r => setTimeout(r, 2000));
  }
  throw new Error('Timeout esperando el job.');
}

els.btn.addEventListener('click', uploadFile);
initToolbar();
refreshPluginInfo();
