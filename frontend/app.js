let wave = null;
let previewCtx = null;
let previewAudioObjectUrl = null;
let previewElementSource = null;
let previewGraphNodes = [];
let previewRunning = false;
let currentJobId = null;
let pollingPaused = false;

const els = {
  file: document.getElementById('file'),
  referenceFile: document.getElementById('referenceFile'),
  assistantMode: document.getElementById('assistantMode'),
  genrePreset: document.getElementById('genrePreset'),
  targetLufs: document.getElementById('targetLufs'),
  deliveryTarget: document.getElementById('deliveryTarget'),
  intensity: document.getElementById('intensity'),
  modDynamicEq: document.getElementById('modDynamicEq'),
  modMultibandGlue: document.getElementById('modMultibandGlue'),
  modStereoImager: document.getElementById('modStereoImager'),
  modExciter: document.getElementById('modExciter'),
  modTransient: document.getElementById('modTransient'),
  modLimiter: document.getElementById('modLimiter'),
  modPreviewEq: document.getElementById('modPreviewEq'),
  modParallelMix: document.getElementById('modParallelMix'),
  fxAbMatch: document.getElementById('fxAbMatch'),
  fxSectionTp: document.getElementById('fxSectionTp'),
  fxHumanNotes: document.getElementById('fxHumanNotes'),
  fxDeesser: document.getElementById('fxDeesser'),
  fxPhaseFix: document.getElementById('fxPhaseFix'),
  fxResonance: document.getElementById('fxResonance'),
  fxDither: document.getElementById('fxDither'),
  fxVocalPriority: document.getElementById('fxVocalPriority'),
  fxSmartLimiter: document.getElementById('fxSmartLimiter'),
  fxLoudnessRadar: document.getElementById('fxLoudnessRadar'),
  fxBassNoteControl: document.getElementById('fxBassNoteControl'),
  fxMsSculptor: document.getElementById('fxMsSculptor'),
  fxQaPreflight: document.getElementById('fxQaPreflight'),
  pDynamicEq: document.getElementById('pDynamicEq'),
  pDynamicEqVal: document.getElementById('pDynamicEqVal'),
  pDynamicEqFreq: document.getElementById('pDynamicEqFreq'),
  pDynamicEqFreqVal: document.getElementById('pDynamicEqFreqVal'),
  pDynamicEqQ: document.getElementById('pDynamicEqQ'),
  pDynamicEqQVal: document.getElementById('pDynamicEqQVal'),
  pMultibandGlue: document.getElementById('pMultibandGlue'),
  pMultibandGlueVal: document.getElementById('pMultibandGlueVal'),
  pMultibandAttack: document.getElementById('pMultibandAttack'),
  pMultibandAttackVal: document.getElementById('pMultibandAttackVal'),
  pMultibandRelease: document.getElementById('pMultibandRelease'),
  pMultibandReleaseVal: document.getElementById('pMultibandReleaseVal'),
  pStereoWidth: document.getElementById('pStereoWidth'),
  pStereoWidthVal: document.getElementById('pStereoWidthVal'),
  pStereoPan: document.getElementById('pStereoPan'),
  pStereoPanVal: document.getElementById('pStereoPanVal'),
  pExciterDrive: document.getElementById('pExciterDrive'),
  pExciterDriveVal: document.getElementById('pExciterDriveVal'),
  pExciterTone: document.getElementById('pExciterTone'),
  pExciterToneVal: document.getElementById('pExciterToneVal'),
  pTransientAmount: document.getElementById('pTransientAmount'),
  pTransientAmountVal: document.getElementById('pTransientAmountVal'),
  pTransientMix: document.getElementById('pTransientMix'),
  pTransientMixVal: document.getElementById('pTransientMixVal'),
  pLimiterCeiling: document.getElementById('pLimiterCeiling'),
  pLimiterCeilingVal: document.getElementById('pLimiterCeilingVal'),
  pLimiterRelease: document.getElementById('pLimiterRelease'),
  pLimiterReleaseVal: document.getElementById('pLimiterReleaseVal'),
  pParallelMix: document.getElementById('pParallelMix'),
  pParallelMixVal: document.getElementById('pParallelMixVal'),
  pOutputGain: document.getElementById('pOutputGain'),
  pOutputGainVal: document.getElementById('pOutputGainVal'),
  pLowCutHz: document.getElementById('pLowCutHz'),
  pLowCutHzVal: document.getElementById('pLowCutHzVal'),
  pCompThreshold: document.getElementById('pCompThreshold'),
  pCompThresholdVal: document.getElementById('pCompThresholdVal'),
  pCompRatio: document.getElementById('pCompRatio'),
  pCompRatioVal: document.getElementById('pCompRatioVal'),
  eqLow: document.getElementById('eqLow'),
  eqLowVal: document.getElementById('eqLowVal'),
  eqLowMid: document.getElementById('eqLowMid'),
  eqLowMidVal: document.getElementById('eqLowMidVal'),
  eqMid: document.getElementById('eqMid'),
  eqMidVal: document.getElementById('eqMidVal'),
  eqHighMid: document.getElementById('eqHighMid'),
  eqHighMidVal: document.getElementById('eqHighMidVal'),
  eqHigh: document.getElementById('eqHigh'),
  eqHighVal: document.getElementById('eqHighVal'),
  previewMode: document.getElementById('previewMode'),
  pollIntervalMs: document.getElementById('pollIntervalMs'),
  livePlayBtn: document.getElementById('livePlayBtn'),
  livePauseBtn: document.getElementById('livePauseBtn'),
  liveStopBtn: document.getElementById('liveStopBtn'),
  livePreviewAudio: document.getElementById('livePreviewAudio'),
  btn: document.getElementById('masterBtn'),
  pausePollBtn: document.getElementById('pausePollBtn'),
  resumePollBtn: document.getElementById('resumePollBtn'),
  cancelJobBtn: document.getElementById('cancelJobBtn'),
  applyLiveBtn: document.getElementById('applyLiveBtn'),
  profile: document.getElementById('profile'),
  state: document.getElementById('state'),
  pluginBackend: document.getElementById('pluginBackend'),
  confidence: document.getElementById('confidence'),
  issues: document.getElementById('issues'),
  advancedPlan: document.getElementById('advancedPlan'),
  arrangementTags: document.getElementById('arrangementTags'),
  sectionMap: document.getElementById('sectionMap'),
  loudnessRadar: document.getElementById('loudnessRadar'),
  humanNote: document.getElementById('humanNote'),
  actions: document.getElementById('actions'),
  analysisBox: document.getElementById('analysisBox'),
  decisionBox: document.getElementById('decisionBox'),
  progressBar: document.getElementById('progressBar'),
  progressLabel: document.getElementById('progressLabel'),
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
  isotopeGrid: document.getElementById('isotopeGrid'),
  filters: document.querySelectorAll('.filter'),
  sorts: document.querySelectorAll('.sort'),
};

function setText(el, value) {
  if (el) el.textContent = value;
}

function setSteps(progress, status) {
  [els.stepQueued, els.stepAnalyze, els.stepProcess, els.stepExport, els.stepDone]
    .filter(Boolean)
    .forEach(x => x.classList.remove('active'));
  if (progress >= 0) els.stepQueued?.classList.add('active');
  if (progress >= 14) els.stepAnalyze?.classList.add('active');
  if (progress >= 44) els.stepProcess?.classList.add('active');
  if (progress >= 74) els.stepExport?.classList.add('active');
  if (status === 'done') els.stepDone?.classList.add('active');
}

function updateProgress(progress) {
  const normalized = Math.max(2, progress || 0);
  if (els.progressBar) els.progressBar.style.width = `${normalized}%`;
  setText(els.progressLabel, `${Math.round(normalized)}%`);
}

function applyFilter(filterValue) {
  if (!els.isotopeGrid) return;
  const cards = [...els.isotopeGrid.querySelectorAll('.iso-card')];
  cards.forEach(card => {
    const group = card.dataset.group;
    const shouldShow = filterValue === 'all' || group === filterValue;
    card.classList.toggle('hidden-card', !shouldShow);
  });
}

function applySort(sortType) {
  if (!els.isotopeGrid) return;
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

function initLivePluginControls() {
  const controls = [
    [els.pDynamicEq, els.pDynamicEqVal, 2],
    [els.pDynamicEqFreq, els.pDynamicEqFreqVal, 0],
    [els.pDynamicEqQ, els.pDynamicEqQVal, 2],
    [els.pMultibandGlue, els.pMultibandGlueVal, 2],
    [els.pMultibandAttack, els.pMultibandAttackVal, 3],
    [els.pMultibandRelease, els.pMultibandReleaseVal, 3],
    [els.pStereoWidth, els.pStereoWidthVal, 2],
    [els.pStereoPan, els.pStereoPanVal, 2],
    [els.pExciterDrive, els.pExciterDriveVal, 2],
    [els.pExciterTone, els.pExciterToneVal, 0],
    [els.pTransientAmount, els.pTransientAmountVal, 2],
    [els.pTransientMix, els.pTransientMixVal, 2],
    [els.pLimiterCeiling, els.pLimiterCeilingVal, 2],
    [els.pLimiterRelease, els.pLimiterReleaseVal, 3],
    [els.pParallelMix, els.pParallelMixVal, 2],
    [els.pOutputGain, els.pOutputGainVal, 2],
    [els.pLowCutHz, els.pLowCutHzVal, 0],
    [els.pCompThreshold, els.pCompThresholdVal, 1],
    [els.pCompRatio, els.pCompRatioVal, 2],
    [els.eqLow, els.eqLowVal, 1, ' dB'],
    [els.eqLowMid, els.eqLowMidVal, 1, ' dB'],
    [els.eqMid, els.eqMidVal, 1, ' dB'],
    [els.eqHighMid, els.eqHighMidVal, 1, ' dB'],
    [els.eqHigh, els.eqHighVal, 1, ' dB'],
  ];
  controls.forEach(([input, out, digits, suffix = '']) => {
    if (!input || !out) return;
    const refresh = () => { out.textContent = `${Number(input.value).toFixed(digits)}${suffix}`; };
    input.addEventListener('input', refresh);
    refresh();
  });
  const rebuildInputs = [
    els.modDynamicEq, els.modMultibandGlue, els.modStereoImager, els.modExciter, els.modTransient, els.modLimiter, els.modPreviewEq, els.modParallelMix,
    els.pDynamicEq, els.pDynamicEqFreq, els.pDynamicEqQ,
    els.pMultibandGlue, els.pMultibandAttack, els.pMultibandRelease,
    els.pStereoWidth, els.pStereoPan,
    els.pExciterDrive, els.pExciterTone,
    els.pTransientAmount, els.pTransientMix,
    els.pLimiterCeiling, els.pLimiterRelease,
    els.pParallelMix, els.pOutputGain, els.pLowCutHz, els.pCompThreshold, els.pCompRatio,
    els.eqLow, els.eqLowMid, els.eqMid, els.eqHighMid, els.eqHigh,
    els.previewMode,
  ];
  rebuildInputs.forEach((el) => {
    if (!el) return;
    el.addEventListener('input', () => {
      if (previewRunning) restartPreview();
    });
    el.addEventListener('change', () => {
      if (previewRunning) restartPreview();
    });
  });
}

function setProcessControlsState({ running = false, paused = false }) {
  if (els.pausePollBtn) els.pausePollBtn.disabled = !running || paused;
  if (els.resumePollBtn) els.resumePollBtn.disabled = !running || !paused;
  if (els.cancelJobBtn) els.cancelJobBtn.disabled = !running;
}

function releasePreviewAudioUrl() {
  if (previewAudioObjectUrl) {
    URL.revokeObjectURL(previewAudioObjectUrl);
    previewAudioObjectUrl = null;
  }
}

async function ensurePreviewMediaReady() {
  const file = els.file?.files?.[0];
  if (!file) throw new Error('Selecciona un archivo para preview.');
  if (!previewCtx) previewCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (!els.livePreviewAudio) throw new Error('No se encontró el reproductor de preview.');

  if (!previewAudioObjectUrl || els.livePreviewAudio.dataset.fileName !== file.name || Number(els.livePreviewAudio.dataset.fileSize || 0) !== file.size) {
    releasePreviewAudioUrl();
    previewAudioObjectUrl = URL.createObjectURL(file);
    els.livePreviewAudio.src = previewAudioObjectUrl;
    els.livePreviewAudio.dataset.fileName = file.name;
    els.livePreviewAudio.dataset.fileSize = String(file.size);
  }

  if (!previewElementSource) previewElementSource = previewCtx.createMediaElementSource(els.livePreviewAudio);
}

function teardownPreviewGraph() {
  previewGraphNodes.forEach((node) => {
    try { node.disconnect(); } catch (_) {}
  });
  previewGraphNodes = [];
  if (previewElementSource) {
    try { previewElementSource.disconnect(); } catch (_) {}
  }
}

function applyPreviewMode(node) {
  const mode = els.previewMode?.value || 'full_mix';
  if (!previewCtx || mode === 'full_mix') return node;

  const splitter = previewCtx.createChannelSplitter(2);
  const merger = previewCtx.createChannelMerger(2);
  node.connect(splitter);

  const connectMix = (inChannel, outChannel, gainValue) => {
    const gain = previewCtx.createGain();
    gain.gain.value = gainValue;
    splitter.connect(gain, inChannel);
    gain.connect(merger, 0, outChannel);
    previewGraphNodes.push(gain);
  };

  if (mode === 'vocals_only') {
    connectMix(0, 0, 0.5);
    connectMix(1, 0, 0.5);
    connectMix(0, 1, 0.5);
    connectMix(1, 1, 0.5);
  }

  previewGraphNodes.push(splitter, merger);
  return merger;
}

function buildPreviewChain(source) {
  let node = applyPreviewMode(source);
  const dryNode = node;

  const lowCut = previewCtx.createBiquadFilter();
  lowCut.type = 'highpass';
  lowCut.frequency.value = Number(els.pLowCutHz?.value || 25);
  lowCut.Q.value = 0.707;
  node.connect(lowCut);
  node = lowCut;

  if (els.modDynamicEq?.checked) {
    const eq = previewCtx.createBiquadFilter();
    eq.type = 'peaking';
    eq.frequency.value = Number(els.pDynamicEqFreq?.value || 280);
    eq.Q.value = Number(els.pDynamicEqQ?.value || 1.0);
    eq.gain.value = (Number(els.pDynamicEq?.value || 1) - 1) * -6;
    node.connect(eq);
    node = eq;
  }

  if (els.modMultibandGlue?.checked) {
    const comp = previewCtx.createDynamicsCompressor();
    comp.threshold.value = Number(els.pCompThreshold?.value || -18);
    comp.ratio.value = Number(els.pCompRatio?.value || 1.8);
    comp.attack.value = Number(els.pMultibandAttack?.value || 0.01);
    comp.release.value = Number(els.pMultibandRelease?.value || 0.2);
    node.connect(comp);
    node = comp;
  }

  if (els.modStereoImager?.checked) {
    const pan = previewCtx.createStereoPanner();
    const widthPan = Number(els.pStereoWidth?.value || 0.1) * 1.5;
    pan.pan.value = Math.max(-1, Math.min(1, widthPan + Number(els.pStereoPan?.value || 0)));
    node.connect(pan);
    node = pan;
  }

  if (els.modPreviewEq?.checked) {
    const eqBands = [
      ['lowshelf', 80, Number(els.eqLow?.value || 0)],
      ['peaking', 250, Number(els.eqLowMid?.value || 0)],
      ['peaking', 1000, Number(els.eqMid?.value || 0)],
      ['peaking', 4000, Number(els.eqHighMid?.value || 0)],
      ['highshelf', 10000, Number(els.eqHigh?.value || 0)],
    ];
    eqBands.forEach(([type, frequency, gain]) => {
      if (Math.abs(gain) < 0.05) return;
      const eq = previewCtx.createBiquadFilter();
      eq.type = type;
      eq.frequency.value = frequency;
      eq.Q.value = type === 'peaking' ? 0.85 : 0.7;
      eq.gain.value = gain;
      node.connect(eq);
      node = eq;
    });
  }

  if (els.modExciter?.checked) {
    const exciter = previewCtx.createBiquadFilter();
    exciter.type = 'highshelf';
    exciter.frequency.value = Number(els.pExciterTone?.value || 6000);
    exciter.gain.value = Number(els.pExciterDrive?.value || 8) * 0.6;
    node.connect(exciter);
    node = exciter;
  }

  if (els.modTransient?.checked) {
    const transient = previewCtx.createDynamicsCompressor();
    transient.threshold.value = -18 + ((1 - Number(els.pTransientAmount?.value || 0.95)) * 50);
    transient.ratio.value = 2 + ((1 - Number(els.pTransientAmount?.value || 0.95)) * 8);
    transient.attack.value = 0.001;
    transient.release.value = 0.05;
    node.connect(transient);
    node = transient;
  }

  if (els.modLimiter?.checked) {
    const lim = previewCtx.createDynamicsCompressor();
    lim.threshold.value = Number(els.pLimiterCeiling?.value || -1) - 1.5;
    lim.ratio.value = 20;
    lim.attack.value = 0.003;
    lim.release.value = Number(els.pLimiterRelease?.value || 0.08);
    node.connect(lim);
    node = lim;
  }

  if (els.modParallelMix?.checked) {
    const dryGain = previewCtx.createGain();
    const wetGain = previewCtx.createGain();
    const mixOut = previewCtx.createGain();
    const wetMix = Math.max(0, Math.min(1, Number(els.pParallelMix?.value || 1)));
    dryGain.gain.value = 1 - wetMix;
    wetGain.gain.value = wetMix * Number(els.pTransientMix?.value || 1);
    dryNode.connect(dryGain);
    node.connect(wetGain);
    dryGain.connect(mixOut);
    wetGain.connect(mixOut);
    node = mixOut;
    previewGraphNodes.push(dryGain, wetGain, mixOut);
  }

  const outGain = previewCtx.createGain();
  outGain.gain.value = 10 ** (Number(els.pOutputGain?.value || 0) / 20);
  node.connect(outGain);
  node = outGain;

  previewGraphNodes.push(node);
  return node;
}

async function restartPreview() {
  try {
    if (!previewElementSource) return;
    teardownPreviewGraph();
    const tail = buildPreviewChain(previewElementSource);
    tail.connect(previewCtx.destination);
  } catch (err) {
    setText(els.statusText, `Preview: ${err.message}`);
  }
}

function stopPreview() {
  if (els.livePreviewAudio) {
    els.livePreviewAudio.pause();
    els.livePreviewAudio.currentTime = 0;
  }
  previewRunning = false;
}

async function playPreview() {
  await ensurePreviewMediaReady();
  await restartPreview();
  if (previewCtx.state === 'suspended') await previewCtx.resume();
  await els.livePreviewAudio.play();
  previewRunning = true;
}

async function pausePreview() {
  if (!els.livePreviewAudio) return;
  els.livePreviewAudio.pause();
  previewRunning = false;
  if (previewCtx?.state === 'running') await previewCtx.suspend();
}

async function handleLivePlay() {
  try {
    await playPreview();
  } catch (err) {
    setText(els.statusText, `Preview: ${err.message}`);
  }
}

async function refreshPluginInfo() {
  try {
    const res = await fetch('/api/plugins');
    const data = await res.json();
    if (data.ladspa_filter) setText(els.pluginBackend, 'ladspa/native');
    else if (data.lv2_filter) setText(els.pluginBackend, 'lv2/native');
    else setText(els.pluginBackend, 'native');

    const modules = Object.entries(data.advanced_modules || {})
      .filter(([, enabled]) => Boolean(enabled))
      .map(([name]) => name);
    if (modules.length) {
      setText(els.statusText, `Módulos disponibles: ${modules.slice(0, 3).join(', ')}${modules.length > 3 ? '...' : ''}`);
    }
  } catch (_) {
    setText(els.pluginBackend, 'native');
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
  if (!els.issues) return;
  els.issues.innerHTML = '';
  (list || []).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    els.issues.appendChild(li);
  });
}

function renderActions(chain, decision) {
  if (!els.actions) return;
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
  if (!els.arrangementTags) return;
  els.arrangementTags.innerHTML = '';
  (tags || []).forEach((tag) => {
    const li = document.createElement('li');
    li.textContent = tag;
    els.arrangementTags.appendChild(li);
  });
}

function renderSectionMap(analysis) {
  if (!els.sectionMap) return;
  const sections = analysis?.section_rms_db || [];
  if (!sections.length) {
    els.sectionMap.textContent = 'Sin datos de secciones.';
    return;
  }
  const min = Math.min(...sections);
  const max = Math.max(...sections);
  const rows = sections.map((db, i) => {
    const norm = max === min ? 0.5 : (db - min) / (max - min);
    const bars = '█'.repeat(Math.max(1, Math.round(norm * 14)));
    return `S${i + 1}: ${bars.padEnd(14, '·')} ${db.toFixed(1)} dB`;
  });
  rows.push(`Macro dinámica: ${(analysis?.macro_dynamics_db || 0).toFixed(2)} dB`);
  rows.push(`Hook lift: ${(analysis?.hook_lift_db || 0).toFixed(2)} dB`);
  els.sectionMap.textContent = rows.join('\n');
}

function renderLoudnessRadar(analysis) {
  if (!els.loudnessRadar) return;
  const points = analysis?.loudness_radar || analysis?.section_rms_db || [];
  if (!points.length) {
    els.loudnessRadar.textContent = 'Sin datos de radar.';
    return;
  }
  const min = Math.min(...points);
  const max = Math.max(...points);
  const rows = points.map((v, i) => {
    const norm = max === min ? 0.5 : (v - min) / (max - min);
    const bars = '▮'.repeat(Math.max(1, Math.round(norm * 12)));
    return `T${i + 1}: ${bars.padEnd(12, '·')} ${v.toFixed(1)} LU-ish`;
  });
  els.loudnessRadar.textContent = rows.join('\n');
}

function buildHumanNote(analysis, decision) {
  const focus = analysis?.arrangement_focus || 'balanced_mix';
  const tags = (analysis?.arrangement_tags || []).join(', ') || 'sin tags relevantes';
  const strategy = decision?.human_pass_strategy || 'single_pass_balanced';
  const target = decision?.target_lufs ?? '--';
  const actions = (decision?.actions || []).slice(0, 4).join(' | ') || 'glue general';
  return [
    `Se detectó un arreglo ${focus} con tags: ${tags}.`,
    `Aplicaremos estrategia ${strategy} con objetivo ${target} LUFS para mantener musicalidad.`,
    `Prioridades de la pasada humana: ${actions}.`,
  ].join(' ');
}

function setMeter(fillEl, valueEl, percent, label) {
  if (!fillEl || !valueEl) return;
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
  const deliveryTarget = els.deliveryTarget?.value || 'streaming';
  const intensity = Number(els.intensity.value);
  const mode = els.assistantMode.value;
  const referenceLoaded = Boolean(els.referenceFile.files[0]);

  const plan = [];
  plan.push(`Human adaptive mode ${mode}/${genre}: decisión guiada por contexto musical real.`);
  plan.push(`Target final: ${targetLufs} LUFS con limitación transparente y control true-peak preventivo.`);
  if (deliveryTarget === 'cd_master') {
    plan.push('Entrega CD: cadena extra de glue humano + loudness competitivo estilo disco físico.');
  }
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
  if (!els.advancedPlan) return;
  els.advancedPlan.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    els.advancedPlan.appendChild(li);
  });
}

function buildCurrentOptionsPayload() {
  return {
    target_lufs: Number(els.targetLufs.value),
    delivery_target: els.deliveryTarget?.value || 'streaming',
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
    plugin_params: {
      dynamic_eq_amount: Number(els.pDynamicEq?.value || 1.0),
      dynamic_eq_freq_hz: Number(els.pDynamicEqFreq?.value || 280),
      dynamic_eq_q: Number(els.pDynamicEqQ?.value || 1.0),
      multiband_glue_strength: Number(els.pMultibandGlue?.value || 1.0),
      multiband_attack_s: Number(els.pMultibandAttack?.value || 0.01),
      multiband_release_s: Number(els.pMultibandRelease?.value || 0.2),
      stereo_width_amount: Number(els.pStereoWidth?.value || 0.10),
      stereo_pan: Number(els.pStereoPan?.value || 0),
      exciter_drive: Number(els.pExciterDrive?.value || 8.0),
      exciter_tone_hz: Number(els.pExciterTone?.value || 6000),
      transient_support: Number(els.pTransientAmount?.value || 0.95),
      transient_mix: Number(els.pTransientMix?.value || 1.0),
      limiter_ceiling_dbtp: Number(els.pLimiterCeiling?.value || -1.0),
      limiter_release_s: Number(els.pLimiterRelease?.value || 0.08),
      preview_parallel_mix: Number(els.pParallelMix?.value || 1.0),
      output_gain_db: Number(els.pOutputGain?.value || 0),
      low_cut_hz: Number(els.pLowCutHz?.value || 25),
      comp_threshold_db: Number(els.pCompThreshold?.value || -18.0),
      comp_ratio: Number(els.pCompRatio?.value || 1.8),
      eq_low_db: Number(els.eqLow?.value || 0),
      eq_low_mid_db: Number(els.eqLowMid?.value || 0),
      eq_mid_db: Number(els.eqMid?.value || 0),
      eq_high_mid_db: Number(els.eqHighMid?.value || 0),
      eq_high_db: Number(els.eqHigh?.value || 0),
    },
    feature_flags: {
      ab_match: Boolean(els.fxAbMatch?.checked),
      section_true_peak_guard: Boolean(els.fxSectionTp?.checked),
      advanced_human_notes: Boolean(els.fxHumanNotes?.checked),
      dynamic_deesser: Boolean(els.fxDeesser?.checked),
      phase_mono_fix: Boolean(els.fxPhaseFix?.checked),
      resonance_hunter: Boolean(els.fxResonance?.checked),
      dither_noise_shaping: Boolean(els.fxDither?.checked),
      vocal_priority_sidechain: Boolean(els.fxVocalPriority?.checked),
      smart_limiter_lookahead: Boolean(els.fxSmartLimiter?.checked),
      loudness_radar: Boolean(els.fxLoudnessRadar?.checked),
      bass_note_control: Boolean(els.fxBassNoteControl?.checked),
      smart_ms_sculptor: Boolean(els.fxMsSculptor?.checked),
      qa_preflight: Boolean(els.fxQaPreflight?.checked),
    },
  };
}

async function uploadFile() {
  const file = els.file.files[0];
  if (!file) {
    setText(els.statusText, 'Selecciona un archivo primero.');
    return;
  }

  renderWave(file);
  els.btn.disabled = true;
  setText(els.statusText, 'Analizando track localmente...');
  els.downloads?.classList.add('hidden');
  if (els.progressBar) els.progressBar.style.width = '3%';

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
  form.append('options_json', JSON.stringify(buildCurrentOptionsPayload()));

  try {
    setText(els.statusText, 'Subiendo al motor de mastering...');
    const res = await fetch('/api/jobs', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    currentJobId = data.job_id;
    pollingPaused = false;
    setProcessControlsState({ running: true, paused: false });
    await pollJob(data.job_id, localStats);
  } catch (err) {
    console.error(err);
    setText(els.statusText, `Error al procesar: ${err.message}`);
  } finally {
    currentJobId = null;
    pollingPaused = false;
    setProcessControlsState({ running: false, paused: false });
    stopPreview();
    releasePreviewAudioUrl();
    if (els.livePreviewAudio) {
      els.livePreviewAudio.removeAttribute('src');
      els.livePreviewAudio.load();
    }
    els.btn.disabled = false;
  }
}

async function pollJob(jobId, localStats) {
  for (let i = 0; i < 600; i++) {
    if (pollingPaused) {
      await new Promise(r => setTimeout(r, 350));
      continue;
    }

    const res = await fetch(`/api/jobs/${jobId}`);
    const data = await res.json();

    setText(els.state, data.status || '-');
    setText(els.profile, data.profile || 'PGR Mastering');
    setText(els.analysisBox, JSON.stringify(data.analysis || {}, null, 2));
    setText(els.decisionBox, JSON.stringify(data.decision || {}, null, 2));
    renderIssues(data.issues || []);
    renderActions(data.chain || {}, data.decision || {});
    renderAdvancedPlan(buildAdvancedPlan(data, localStats));
    renderArrangementTags(data.analysis?.arrangement_tags || data.decision?.arrangement_tags || []);
    renderSectionMap(data.analysis || {});
    renderLoudnessRadar(data.analysis || {});
    setText(els.humanNote, buildHumanNote(data.analysis || {}, data.decision || {}));

    const confidence = estimateConfidence((data.issues || []).length, els.intensity.value);
    setText(els.confidence, `${confidence}%`);

    const progress = Math.max(3, data.progress || 0);
    updateProgress(progress);
    setText(els.statusText, data.message || 'Procesando...');
    setSteps(progress, data.status || 'queued');

    if (data.status === 'done') {
      if (els.downloadWav) els.downloadWav.href = `/api/jobs/${jobId}/download?fmt=wav&variant=master`;
      if (els.downloadMp3) els.downloadMp3.href = `/api/jobs/${jobId}/download?fmt=mp3&variant=master`;
      els.downloads?.classList.remove('hidden');
      setText(els.statusText, 'Master listo. Descarga disponible.');
      return;
    }
    if (data.status === 'cancelled') {
      setText(els.statusText, data.message || 'Render cancelado.');
      return;
    }
    if (data.status === 'error') {
      throw new Error(data.error || 'Error en mastering');
    }
    const pollEveryMs = Math.max(300, Number(els.pollIntervalMs?.value || 2000));
    await new Promise(r => setTimeout(r, pollEveryMs));
  }
  throw new Error('Timeout esperando el job.');
}

function pausePolling() {
  if (!currentJobId) return;
  pollingPaused = true;
  setProcessControlsState({ running: true, paused: true });
  setText(els.statusText, 'Monitoreo pausado. El render sigue ejecutándose.');
}

function resumePolling() {
  if (!currentJobId) return;
  pollingPaused = false;
  setProcessControlsState({ running: true, paused: false });
  setText(els.statusText, 'Monitoreo en vivo reactivado.');
}

async function cancelCurrentJob() {
  if (!currentJobId) return;
  try {
    const res = await fetch(`/api/jobs/${currentJobId}/cancel`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    setText(els.statusText, data.message || 'Cancelación enviada. Deteniendo proceso...');
  } catch (err) {
    setText(els.statusText, `No se pudo cancelar: ${err.message}`);
  }
}

async function applyLiveChangesToJob() {
  if (!currentJobId) {
    setText(els.statusText, 'No hay render activo para aplicar cambios live.');
    return;
  }
  try {
    const form = new FormData();
    form.append('options_json', JSON.stringify(buildCurrentOptionsPayload()));
    const res = await fetch(`/api/jobs/${currentJobId}/live-options`, { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    setText(els.statusText, 'Cambios live enviados al motor.');
  } catch (err) {
    setText(els.statusText, `No se aplicaron cambios live: ${err.message}`);
  }
}

els.btn?.addEventListener('click', uploadFile);
els.livePlayBtn?.addEventListener('click', handleLivePlay);
els.livePauseBtn?.addEventListener('click', pausePreview);
els.liveStopBtn?.addEventListener('click', stopPreview);
els.pausePollBtn?.addEventListener('click', pausePolling);
els.resumePollBtn?.addEventListener('click', resumePolling);
els.cancelJobBtn?.addEventListener('click', cancelCurrentJob);
els.applyLiveBtn?.addEventListener('click', applyLiveChangesToJob);
els.livePreviewAudio?.addEventListener('play', async () => {
  if (previewCtx?.state === 'suspended') await previewCtx.resume();
  await restartPreview();
  previewRunning = true;
});
els.livePreviewAudio?.addEventListener('pause', () => {
  previewRunning = false;
});
els.livePreviewAudio?.addEventListener('ended', () => {
  previewRunning = false;
});
initToolbar();
initLivePluginControls();
refreshPluginInfo();
setProcessControlsState({ running: false, paused: false });
