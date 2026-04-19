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
    arrangement_focus = str(analysis.get("arrangement_focus", "balanced_mix"))
    arrangement_tags = list(analysis.get("arrangement_tags", []))
    issues = list(analysis.get("issues", []))

    decision = {
        "preset_name": "Human Adaptive Master",
        "target_lufs": -10.5,
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
        "multiband_drive": "medium",
        "limiter_ceiling_dbtp": -1.0,
        "vocal_presence_boost_db": 0.0,
        "vocal_presence_hz": 2200,
        "chorus_smooth_db": 0.0,
        "chorus_smooth_hz": 4800,
        "instrument_glue_db": 0.0,
        "actions": [],
        "notes": [],
        "genre": "general",
        "arrangement_focus": arrangement_focus,
        "arrangement_tags": arrangement_tags,
        "advanced_modules": {
            "dynamic_eq": True,
            "multiband_glue": True,
            "stereo_imager": True,
            "harmonic_exciter": True,
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

    if decision["genre"] == "club_or_dark_mix":
        decision["target_lufs"] = -9.8
        decision["multiband_drive"] = "high"
    elif decision["genre"] == "open_or_hifi":
        decision["target_lufs"] = -10.8
        decision["multiband_drive"] = "low"

    if mode == "assistant_punch":
        decision["preset_name"] = "Human Adaptive Master • Punch Bias"
        decision["target_lufs"] = -9.5
        decision["multiband_drive"] = "high"
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

    if not decision["actions"]:
        decision["actions"].append("Glue sutil y control final")
        decision["notes"].append("La mezcla llegó bastante equilibrada.")

    return decision
