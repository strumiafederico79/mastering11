def decide_mastering(analysis: dict, mode: str = "human_master", options: dict | None = None) -> dict:
    options = options or {}
    low = float(analysis.get("low", 0.0))
    low_mid = float(analysis.get("low_mid", 0.0))
    mid = float(analysis.get("mid", 0.0))
    high = float(analysis.get("high", 0.0))
    air = float(analysis.get("air", 0.0))
    crest = float(analysis.get("crest", 0.0))
    vocal_presence = float(analysis.get("vocal_presence", 0.0))
    chorus_density = float(analysis.get("chorus_density", 0.0))
    harmonic_ratio = float(analysis.get("harmonic_ratio", 1.0))
    sibilance_index = float(analysis.get("sibilance_index", 0.0))
    harshness_index = float(analysis.get("harshness_index", 0.0))
    resonance_hz = int(analysis.get("resonance_hz", 3500))
    clipping_sections = list(analysis.get("clipping_sections", []))
    true_peak_est_db = float(analysis.get("true_peak_est_db", -3.0))
    bass_note_hz = float(analysis.get("bass_note_hz", 80.0))
    arrangement_focus = str(analysis.get("arrangement_focus", "balanced_mix"))
    arrangement_tags = list(analysis.get("arrangement_tags", []))
    macro_dynamics_db = float(analysis.get("macro_dynamics_db", 0.0))
    hook_lift_db = float(analysis.get("hook_lift_db", 0.0))
    issues = list(analysis.get("issues", []))

    decision = {
        "preset_name": "Human Adaptive Master",
        "target_lufs": -12.0,
        "delivery_target": "streaming",
        "tighten_low_end": False,
        "tighten_low_end_strength": "medium",
        "mud_cut_db": 0.0,
        "mud_center_hz": 280,
        "low_mid_cut_db": 0.0,
        "low_mid_center_hz": 450,
        "presence_boost_db": 0.0,
        "presence_center_hz": 3200,
        "air_shelf_db": 0.0,
        "air_start_hz": 10000,
        "use_exciter": False,
        "exciter_band": "off",
        "boost_transients": False,
        "transient_focus": "off",
        "widen_stereo": True,
        "widen_stereo_band": "high_only",
        "widen_amount": 0.10,
        "use_deharsh": False,
        "deharsh_db": 0.0,
        "deharsh_center_hz": 3500,
        "multiband_drive": "low",
        "enable_main_compressor": False,
        "limiter_ceiling_dbtp": -1.0,
        "vocal_presence_boost_db": 0.0,
        "vocal_presence_hz": 2200,
        "chorus_smooth_db": 0.0,
        "chorus_smooth_hz": 4800,
        "instrument_glue_db": 0.0,
        "human_glue_stage": False,
        "cd_presence_stage": False,
        "cd_low_weight_stage": False,
        "ab_match_gain_db": float(analysis.get("ab_match_gain_db", 0.0)),
        "deesser_db": 0.0,
        "deesser_hz": 6800,
        "resonance_cut_db": 0.0,
        "resonance_hz": resonance_hz,
        "mono_low_end_fix": False,
        "dither_profile": "off",
        "smart_limiter": False,
        "limiter_lookahead_ms": 4.0,
        "limiter_release_ms": 60.0,
        "bass_note_control_db": 0.0,
        "bass_note_hz": bass_note_hz,
        "smart_ms_sculptor": False,
        "actions": [],
        "notes": [],
        "genre": "general",
        "arrangement_focus": arrangement_focus,
        "arrangement_tags": arrangement_tags,
        "human_pass_strategy": "single_pass_balanced",
        "advanced_modules": {
            "dynamic_eq": True,
            "multiband_glue": False,
            "stereo_imager": True,
            "harmonic_exciter": False,
            "transient_shaper": True,
            "true_peak_limiter": True,
        },
    }

    low_vs_mid = low / max(mid, 1e-6)
    lowmid_vs_mid = low_mid / max(mid, 1e-6)
    high_vs_mid = high / max(mid, 1e-6)

    if low_vs_mid > 5.0:
        decision["genre"] = "club_or_dark_mix"
    elif air > high * 0.35 and crest > 5.5:
        decision["genre"] = "open_or_hifi"

    if "mud" in issues:
        decision["tighten_low_end"] = True
        decision["tighten_low_end_strength"] = "high" if low_vs_mid > 6.0 else "medium"
        decision["mud_cut_db"] = 2.4 if lowmid_vs_mid > 4.0 else 1.8
        decision["low_mid_cut_db"] = 1.2
        decision["actions"].append("Limpiar barro y ordenar low-mids")
        decision["notes"].append("Se detectó acumulación en graves/medios bajos.")

    if "lack_of_air" in issues:
        decision["air_shelf_db"] = 2.0
        decision["presence_boost_db"] = 1.0 if high_vs_mid < 0.6 else 0.6
        decision["use_exciter"] = True
        decision["exciter_band"] = "high_only"
        decision["actions"].append("Recuperar aire y presencia")
        decision["notes"].append("La mezcla está oscura y cerrada arriba.")

    if "harsh" in issues:
        decision["use_deharsh"] = True
        decision["deharsh_db"] = 1.5
        decision["actions"].append("Suavizar zona agresiva")
        decision["notes"].append("Hay dureza en presencia alta.")

    if "weak_transients" in issues or low_vs_mid > 4.0:
        decision["boost_transients"] = True
        decision["transient_focus"] = "mid_high"
        decision["enable_main_compressor"] = True
        decision["actions"].append("Recuperar pegada")
        decision["notes"].append("Se reforzó ataque percibido.")

    if arrangement_focus == "vocal_led":
        decision["vocal_presence_boost_db"] = 1.2 if vocal_presence < 0.30 else 0.6
        decision["air_shelf_db"] = max(1.0, decision["air_shelf_db"])
        decision["actions"].append("Enfoque humano vocal: inteligibilidad al frente sin romper musicalidad")
    elif arrangement_focus == "instrumental_driven":
        decision["instrument_glue_db"] = 0.8
        decision["actions"].append("Enfoque instrumental: glue y cohesión de buses musicales")

    if chorus_density > 0.62:
        decision["chorus_smooth_db"] = 1.1
        decision["use_deharsh"] = True
        decision["deharsh_db"] = max(decision["deharsh_db"], 1.2)
        decision["actions"].append("Control de coros: suavizado de presencia para evitar fatiga")

    if "vocal_masking" in issues:
        decision["low_mid_cut_db"] = max(decision["low_mid_cut_db"], 1.4)
        decision["presence_boost_db"] = max(decision["presence_boost_db"], 0.8)
        decision["actions"].append("Separación voz/instrumental en low-mid y presencia")

    if "chorus_harshness" in issues:
        decision["use_deharsh"] = True
        decision["deharsh_db"] = max(decision["deharsh_db"], 1.8)
        decision["actions"].append("Control de aspereza en coros densos")

    if macro_dynamics_db >= 4.2:
        decision["human_pass_strategy"] = "macro_dynamic_guard"
        decision["target_lufs"] = min(decision["target_lufs"], -10.8)
        decision["actions"].append("Preservar macro-dinámica entre secciones (estilo humano)")
    elif macro_dynamics_db <= 2.2:
        decision["human_pass_strategy"] = "micro_impact_boost"
        decision["boost_transients"] = True
        decision["actions"].append("Reforzar micro-impacto por dinámica plana")

    if hook_lift_db < 0.4:
        decision["notes"].append("El hook no levanta suficiente frente al inicio; aplicar empuje sutil.")
        decision["presence_boost_db"] = max(decision["presence_boost_db"], 0.7)
    elif hook_lift_db > 2.2:
        decision["notes"].append("Hook con gran lift natural; priorizar estabilidad y evitar over-limit.")
        decision["target_lufs"] = min(decision["target_lufs"], -11.0)

    if decision["genre"] == "club_or_dark_mix":
        decision["target_lufs"] = -10.8
        decision["multiband_drive"] = "high"
        decision["enable_main_compressor"] = True
    elif decision["genre"] == "open_or_hifi":
        decision["target_lufs"] = -10.8
        decision["multiband_drive"] = "low"

    if mode == "assistant_punch":
        decision["preset_name"] = "Human Adaptive Master • Punch Bias"
        decision["target_lufs"] = -10.5
        decision["multiband_drive"] = "high"
        decision["enable_main_compressor"] = True
        decision["boost_transients"] = True
        decision["actions"].append("Modo punch: impacto y loudness competitivo")
    elif mode == "assistant_warm":
        decision["preset_name"] = "Human Adaptive Master • Warm Bias"
        decision["air_shelf_db"] = max(0.4, decision["air_shelf_db"] - 0.5)
        decision["presence_boost_db"] = max(0.3, decision["presence_boost_db"] - 0.4)
        decision["target_lufs"] = -11.2
        decision["actions"].append("Modo warm: suavidad armónica y densidad musical")
    elif mode == "assistant_open":
        decision["preset_name"] = "Human Adaptive Master • Open Bias"
        decision["air_shelf_db"] = max(1.2, decision["air_shelf_db"])
        decision["use_exciter"] = True
        decision["exciter_band"] = "high_only"
        decision["actions"].append("Modo open: más aire y amplitud estéreo")

    requested_lufs = options.get("target_lufs")
    if isinstance(requested_lufs, (int, float)) and -16 <= float(requested_lufs) <= -7:
        decision["target_lufs"] = float(requested_lufs)

    intensity = options.get("intensity")
    if isinstance(intensity, (int, float)):
        if intensity >= 80:
            decision["multiband_drive"] = "high"
            decision["enable_main_compressor"] = True
            decision["boost_transients"] = True
        elif intensity <= 40:
            decision["multiband_drive"] = "low"
            decision["use_deharsh"] = True
            decision["deharsh_db"] = max(1.0, decision["deharsh_db"])

    stereo_amount = options.get("stereo_amount")
    if isinstance(stereo_amount, (int, float)):
        decision["widen_amount"] = max(0.0, min(0.6, float(stereo_amount)))

    modules = options.get("modules")
    if isinstance(modules, dict):
        for module_name, enabled in modules.items():
            if module_name in decision["advanced_modules"]:
                decision["advanced_modules"][module_name] = bool(enabled)

    plugin_params = options.get("plugin_params")
    if isinstance(plugin_params, dict):
        dynamic_eq_amount = float(plugin_params.get("dynamic_eq_amount", 1.0))
        glue_strength = float(plugin_params.get("multiband_glue_strength", 1.0))
        stereo_width = float(plugin_params.get("stereo_width_amount", decision["widen_amount"]))
        exciter_drive = float(plugin_params.get("exciter_drive", 8.0))
        transient_support = float(plugin_params.get("transient_support", 0.95))
        limiter_ceiling = float(plugin_params.get("limiter_ceiling_dbtp", decision["limiter_ceiling_dbtp"]))
        low_cut_hz = float(plugin_params.get("low_cut_hz", 25.0))
        comp_threshold_db = float(plugin_params.get("comp_threshold_db", -18.0))
        comp_ratio = float(plugin_params.get("comp_ratio", 1.8))
        eq_low = float(plugin_params.get("eq_low_db", 0.0))
        eq_low_mid = float(plugin_params.get("eq_low_mid_db", 0.0))
        eq_mid = float(plugin_params.get("eq_mid_db", 0.0))
        eq_high_mid = float(plugin_params.get("eq_high_mid_db", 0.0))
        eq_high = float(plugin_params.get("eq_high_db", 0.0))

        decision["mud_cut_db"] = max(0.0, decision["mud_cut_db"] * max(0.0, min(2.0, dynamic_eq_amount)))
        decision["multiband_glue_strength"] = max(0.0, min(2.0, glue_strength))
        decision["widen_amount"] = max(0.0, min(0.6, stereo_width))
        decision["exciter_drive"] = max(1.0, min(12.0, exciter_drive))
        decision["transient_support"] = max(0.85, min(0.99, transient_support))
        decision["limiter_ceiling_dbtp"] = max(-2.0, min(-0.1, limiter_ceiling))
        decision["low_cut_hz"] = max(20.0, min(60.0, low_cut_hz))
        decision["main_comp_threshold_db"] = max(-30.0, min(-6.0, comp_threshold_db))
        decision["main_comp_ratio"] = max(1.0, min(4.0, comp_ratio))
        decision["manual_eq"] = {
            "low_80hz_db": max(-12.0, min(12.0, eq_low)),
            "low_mid_250hz_db": max(-12.0, min(12.0, eq_low_mid)),
            "mid_1khz_db": max(-12.0, min(12.0, eq_mid)),
            "high_mid_4khz_db": max(-12.0, min(12.0, eq_high_mid)),
            "high_10khz_db": max(-12.0, min(12.0, eq_high)),
        }

    features = options.get("feature_flags", {})
    if not isinstance(features, dict):
        features = {}

    if features.get("ab_match", True):
        decision["actions"].append("A/B match inteligente activado")
    if features.get("section_true_peak_guard", True):
        if clipping_sections or true_peak_est_db > -0.2:
            decision["limiter_ceiling_dbtp"] = min(decision["limiter_ceiling_dbtp"], -1.0)
            decision["target_lufs"] = min(decision["target_lufs"], -10.0)
            decision["notes"].append(f"Guard de clipping por secciones activado ({len(clipping_sections)} secciones en riesgo).")
    if features.get("advanced_human_notes", False):
        decision["notes"].append(
            f"Nota humana avanzada: sibilance={sibilance_index:.2f}, harshness={harshness_index:.2f}, resonance={resonance_hz}Hz."
        )
    if features.get("dynamic_deesser", False) and sibilance_index > 0.22:
        decision["deesser_db"] = min(2.2, 0.8 + (sibilance_index * 2.0))
        decision["deesser_hz"] = 6800
        decision["actions"].append("Control dinámico de sibilancia/harshness por banda")
    if features.get("phase_mono_fix", False):
        decision["mono_low_end_fix"] = True
        decision["actions"].append("Auto-fix mono-compatibilidad en low-end")
    if features.get("resonance_hunter", False):
        decision["resonance_cut_db"] = max(decision["resonance_cut_db"], 1.1)
        decision["actions"].append(f"Detector de resonancias: notch en {resonance_hz}Hz")
    if features.get("dither_noise_shaping", False):
        decision["dither_profile"] = "triangular_hp"
        decision["actions"].append("Dither/noise shaping preparado para entrega final")
    if features.get("vocal_priority_sidechain", False):
        decision["low_mid_cut_db"] = max(decision["low_mid_cut_db"], 1.6)
        decision["vocal_presence_boost_db"] = max(decision["vocal_presence_boost_db"], 1.0)
        decision["actions"].append("Vocal Priority con sidechain musical (aproximado)")
    if features.get("smart_limiter_lookahead", False):
        decision["smart_limiter"] = True
        decision["limiter_lookahead_ms"] = min(8.0, max(2.0, 3.5 + (4.8 - min(4.8, crest))))
        decision["limiter_release_ms"] = 90.0 if macro_dynamics_db > 3.5 else 60.0
        decision["actions"].append("Limiter inteligente con lookahead adaptativo")
    if features.get("bass_note_control", False):
        decision["bass_note_hz"] = bass_note_hz
        decision["bass_note_control_db"] = -1.2 if low_vs_mid > 4.5 else 0.8
        decision["actions"].append(f"Control automático de bajos por nota ({bass_note_hz:.1f}Hz)")
    if features.get("smart_ms_sculptor", False):
        decision["smart_ms_sculptor"] = True
        decision["actions"].append("Smart Mid/Side Sculptor activado")
    if features.get("qa_preflight", True):
        decision["notes"].append("QA pre-flight activado: validación de LUFS/TP/clipping/fase antes de exportar.")

    delivery_target = options.get("delivery_target")
    if delivery_target in {"streaming", "cd_master"}:
        decision["delivery_target"] = delivery_target
        if delivery_target == "cd_master":
            decision["preset_name"] = "Human Adaptive Master • CD Finish"
            decision["target_lufs"] = max(decision["target_lufs"], -9.2)
            decision["limiter_ceiling_dbtp"] = -0.3
            decision["multiband_drive"] = "high"
            decision["enable_main_compressor"] = True
            decision["cd_presence_stage"] = True
            decision["cd_low_weight_stage"] = True
            decision["actions"].append("Entrega CD: loudness, pegada y estabilidad de traducción")

    if not decision["actions"]:
        decision["actions"].append("Glue sutil y control final")
        decision["notes"].append("La mezcla llegó bastante equilibrada.")

    return decision
