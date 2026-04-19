let wave = null;

const els = {
  file: document.getElementById('file'),
  referenceFile: document.getElementById('referenceFile'),
  assistantMode: document.getElementById('assistantMode'),
  genrePreset: document.getElementById('genrePreset'),
  targetLufs: document.getElementById('targetLufs'),
  intensity: document.getElementById('intensity'),
  modDynamicEq: document.getElementById('modDynamicEq'),
  modMultibandGlue: document.getElementById('modMultibandGlue'),
  modStereoImager: document.getElementById('modStereoImager'),
  modExciter: document.getElementById('modExciter'),
  modTransient: document.getElementById('modTransient'),
  modLimiter: document.getElementById('modLimiter'),
  btn: document.getElementById('masterBtn'),
  profile: document.getElementById('profile'),
  state: document.getElementById('state'),
  pluginBackend: document.getElementById('pluginBackend'),
  confidence: document.getElementById('confidence'),
  issues: document.getElementById('issues'),
  advancedPlan: document.getElementById('advancedPlan'),
  arrangementTags: document.getElementById('arrangementTags'),
  actions: document.getElementById('actions'),
  analysisBox: document.getElementById('analysisBox'),
  decisionBox: document.getElementById('decisionBox'),
  progressBar: document.getElementById('progressBar'),
  statusText: document.getElementById('statusText'),
  downloads: document.getElementById('downloads'),
  downloadWav: document.getElementById('downloadWav'),
  downloadMp3: document.getElementById('downloadMp3'),
  meterDynamics: document.getElementById('meterDynamics'),
  meterStereo: document.getElementById('meterStereo'),
  meterTone: document.getElementById('meterTone'),
  meterDynamicsValue: document.getElementById('meterDynamicsValue'),
  meterStereoValue: document.getElementById('meterStereoValue'),
  meterToneValue: document.getElementById('meterToneValue'),
  stepQueued: document.getElementById('stepQueued'),
  stepAnalyze: document.getElementById('stepAnalyze'),
  stepProcess: document.getElementById('stepProcess'),
  stepExport: document.getElementById('stepExport'),
  stepDone: document.getElementById('stepDone'),
};

function setSteps(progress, status) {
  [els.stepQueued, els.stepAnalyze, els.stepProcess, els.stepExport, els.stepDone].forEach(x => x.classList.remove('active'));
  if (progress >= 0) els.stepQueued.classList.add('active');
  if (progress >= 14) els.stepAnalyze.classList.add('active');
  if (progress >= 44) els.stepProcess.classList.add('active');
  if (progress >= 74) els.stepExport.classList.add('active');
  if (status === 'done') els.stepDone.classList.add('active');
}

async function refreshPluginInfo() {
  try {
    const res = await fetch('/api/plugins');
    const data = await res.json();
    if (data.ladspa_filter) els.pluginBackend.textContent = 'ladspa/native';
    else if (data.lv2_filter) els.pluginBackend.textContent = 'lv2/native';
    else els.pluginBackend.textContent = 'native';

    const modules = Object.entries(data.advanced_modules || {})
      .filter(([, enabled]) => Boolean(enabled))
      .map(([name]) => name);
    if (modules.length) {
      els.statusText.textContent = `Módulos disponibles: ${modules.slice(0, 3).join(', ')}${modules.length > 3 ? '...' : ''}`;
    }
  } catch (_) {
    els.pluginBackend.textContent = 'native';
  }
}

function renderWave(file) {
  if (wave) wave.destroy();
  wave = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#3867a7',
    progressColor: '#4ea1ff',
    cursorColor: '#70f0d0',
    height: 150,
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
  const actions = chain?.actions || [];
  if (actions.length) {
    actions.forEach(a => {
      const li = document.createElement('li');
      li.textContent = JSON.stringify(a);
      els.actions.appendChild(li);
    });
  } else if (decision?.actions) {
    decision.actions.forEach(a => {
      const li = document.createElement('li');
      li.textContent = String(a);
      els.actions.appendChild(li);
    });
  }
}

function renderArrangementTags(tags) {
  els.arrangementTags.innerHTML = '';
  (tags || []).forEach((tag) => {
    const li = document.createElement('li');
    li.textContent = tag;
    els.arrangementTags.appendChild(li);
  });
}

function setMeter(fillEl, valueEl, percent, label) {
  fillEl.style.width = `${Math.max(0, Math.min(100, percent))}%`;
  valueEl.textContent = label;
}

function estimateConfidence(issuesCount, intensity) {
  const base = 88 - (issuesCount * 8);
  const intensityPenalty = Math.max(0, (Number(intensity) - 70) * 0.3);
  return Math.round(Math.max(45, Math.min(97, base - intensityPenalty)));
}

async function analyzeLocalAudio(file) {
  const context = new (window.AudioContext || window.webkitAudioContext)();
  const arrayBuffer = await file.arrayBuffer();
  const buffer = await context.decodeAudioData(arrayBuffer);

  const left = buffer.getChannelData(0);
  const right = buffer.numberOfChannels > 1 ? buffer.getChannelData(1) : left;

  let peak = 0;
  let sumSq = 0;
  let monoEnergy = 0;
  let sideEnergy = 0;

  for (let i = 0; i < left.length; i++) {
    const l = left[i];
    const r = right[i] || 0;
    const abs = Math.max(Math.abs(l), Math.abs(r));
    if (abs > peak) peak = abs;
    sumSq += (l * l + r * r) * 0.5;
    const mid = (l + r) * 0.5;
    const side = (l - r) * 0.5;
    monoEnergy += mid * mid;
    sideEnergy += side * side;
  }

  const rms = Math.sqrt(sumSq / left.length);
  const crest = peak / (rms + 1e-8);
  const crestDb = 20 * Math.log10(crest + 1e-8);
  const stereoRatio = sideEnergy / (monoEnergy + sideEnergy + 1e-8);
  const stereoPercent = Math.round(stereoRatio * 100);

  const dynamicMeter = Math.round(Math.max(0, Math.min(100, (crestDb / 18) * 100)));
  const toneMeter = Math.round(Math.max(12, Math.min(95, 70 - (Math.max(0, crestDb - 13) * 2.5))));

  context.close();

  return {
    rms,
    peak,
    crestDb,
    stereoPercent,
    dynamicMeter,
    toneMeter,
  };
}

function buildAdvancedPlan(data, localStats) {
  const genre = els.genrePreset.value;
  const targetLufs = Number(els.targetLufs.value);
  const intensity = Number(els.intensity.value);
  const mode = els.assistantMode.value;
  const referenceLoaded = Boolean(els.referenceFile.files[0]);

  const plan = [];
  plan.push(`Human adaptive mode ${mode}/${genre}: decisión guiada por contexto musical real.`);
  plan.push(`Target final: ${targetLufs} LUFS con limitación transparente y control true-peak preventivo.`);
  if (data.analysis?.arrangement_focus) {
    plan.push(`Arreglo detectado: ${data.analysis.arrangement_focus} con tratamiento específico para voz/instrumentos/coros.`);
  }

  if (localStats) {
    if (localStats.crestDb > 14) {
      plan.push('Transients altos detectados: compresión paralela ligera + soft clip pre-limitador.');
    } else {
      plan.push('Dinámica controlada: conservar punch con micro-automatización multibanda.');
    }
    plan.push(`Stereo map ${localStats.stereoPercent}%: expansión selectiva en rango alto y foco mono en graves.`);
  }

  if ((data.issues || []).some((x) => /bass|grave|low/i.test(x))) {
    plan.push('Low-end cleanup: ecualización dinámica sidechain en 40-120Hz para reducir masking.');
  }

  if (referenceLoaded) {
    plan.push('Referencia activa: matching inteligente de energía por bandas (tilt + glue + limiter timing).');
  }

  if (intensity > 80) {
    plan.push('Modo agresivo: loudness competitivo con priorización de impacto percusivo.');
  }

  return plan.slice(0, 7);
}

function renderAdvancedPlan(items) {
  els.advancedPlan.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    els.advancedPlan.appendChild(li);
  });
}

async function uploadFile() {
  const file = els.file.files[0];
  if (!file) {
    els.statusText.textContent = 'Selecciona un archivo primero.';
    return;
  }

  renderWave(file);
  els.btn.disabled = true;
  els.statusText.textContent = 'Analizando track localmente...';
  els.downloads.classList.add('hidden');
  els.progressBar.style.width = '3%';

  let localStats = null;
  try {
    localStats = await analyzeLocalAudio(file);
    setMeter(els.meterDynamics, els.meterDynamicsValue, localStats.dynamicMeter, `${localStats.crestDb.toFixed(1)} dB crest`);
    setMeter(els.meterStereo, els.meterStereoValue, localStats.stereoPercent, `${localStats.stereoPercent}% side energy`);
    setMeter(els.meterTone, els.meterToneValue, localStats.toneMeter, 'Balance preliminar listo');
  } catch (err) {
    console.warn('No se pudo analizar localmente el audio', err);
  }

  const form = new FormData();
  form.append('file', file);
  form.append('mode', els.assistantMode.value);
  form.append('options_json', JSON.stringify({
    target_lufs: Number(els.targetLufs.value),
    intensity: Number(els.intensity.value),
    stereo_amount: Math.min(0.6, Math.max(0, Number(els.intensity.value) / 200)),
    reference_loaded: Boolean(els.referenceFile.files[0]),
    modules: {
      dynamic_eq: els.modDynamicEq.checked,
      multiband_glue: els.modMultibandGlue.checked,
      stereo_imager: els.modStereoImager.checked,
      harmonic_exciter: els.modExciter.checked,
      transient_shaper: els.modTransient.checked,
      true_peak_limiter: els.modLimiter.checked,
    },
  }));

  try {
    els.statusText.textContent = 'Subiendo al motor de mastering...';
    const res = await fetch('/api/jobs', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    await pollJob(data.job_id, localStats);
  } catch (err) {
    console.error(err);
    els.statusText.textContent = `Error al procesar: ${err.message}`;
  } finally {
    els.btn.disabled = false;
  }
}

async function pollJob(jobId, localStats) {
  for (let i = 0; i < 600; i++) {
    const res = await fetch(`/api/jobs/${jobId}`);
    const data = await res.json();

    els.state.textContent = data.status || '-';
    els.profile.textContent = data.profile || 'Mastering Suite X';
    els.analysisBox.textContent = JSON.stringify(data.analysis || {}, null, 2);
    els.decisionBox.textContent = JSON.stringify(data.decision || {}, null, 2);
    renderIssues(data.issues || []);
    renderActions(data.chain || {}, data.decision || {});
    renderAdvancedPlan(buildAdvancedPlan(data, localStats));
    renderArrangementTags(data.analysis?.arrangement_tags || data.decision?.arrangement_tags || []);

    const confidence = estimateConfidence((data.issues || []).length, els.intensity.value);
    els.confidence.textContent = `${confidence}%`;

    const progress = Math.max(3, data.progress || 0);
    els.progressBar.style.width = `${progress}%`;
    els.statusText.textContent = data.message || 'Procesando...';
    setSteps(progress, data.status || 'queued');

    if (data.status === 'done') {
      els.downloadWav.href = `/api/jobs/${jobId}/download?fmt=wav`;
      els.downloadMp3.href = `/api/jobs/${jobId}/download?fmt=mp3`;
      els.downloads.classList.remove('hidden');
      els.statusText.textContent = 'Master listo. Descarga disponible.';
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
refreshPluginInfo();
