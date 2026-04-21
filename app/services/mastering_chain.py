from app.core.config import settings

def _db(val: float) -> str:
    return f"{val:.2f}"

def build_safe_filter_chain() -> str:
    # Cadena de máxima compatibilidad para builds de ffmpeg limitadas.
    return "highpass=f=25,acompressor=threshold=0.10:ratio=2.0:attack=20:release=180,alimiter=limit=0.98"

def build_ffmpeg_filter_chain(decision: dict):
    filters = []
    actions = []
    modules = decision.get("advanced_modules", {})
    human_pass_strategy = decision.get("human_pass_strategy", "single_pass_balanced")

    manual_eq = decision.get("manual_eq", {})
    if isinstance(manual_eq, dict):
        eq_plan = [
            ("low_80hz_db", "equalizer=f=80:t=q:w=0.7:g={db}", "manual_eq_low"),
            ("low_mid_250hz_db", "equalizer=f=250:t=q:w=0.9:g={db}", "manual_eq_low_mid"),
            ("mid_1khz_db", "equalizer=f=1000:t=q:w=0.85:g={db}", "manual_eq_mid"),
            ("high_mid_4khz_db", "equalizer=f=4000:t=q:w=0.8:g={db}", "manual_eq_high_mid"),
            ("high_10khz_db", "treble=g={db}", "manual_eq_high"),
        ]
        for key, filter_expr, stage_name in eq_plan:
            db = float(manual_eq.get(key, 0.0))
            if abs(db) < 0.05:
                continue
            filters.append(filter_expr.format(db=_db(db)))
            actions.append({"stage": stage_name, "db": db})

    if decision.get("tighten_low_end"):
        filters.append("highpass=f=25")
        actions.append({"stage": "highpass", "f": 25})

    mud_cut_db = float(decision.get("mud_cut_db", 0.0))
    if mud_cut_db > 0 and modules.get("dynamic_eq", True):
        hz = int(decision.get("mud_center_hz", 280))
        filters.append(f"equalizer=f={hz}:t=q:w=1.0:g=-{_db(mud_cut_db)}")
        actions.append({"stage": "mud_cut", "db": -mud_cut_db, "hz": hz})

    low_mid_cut_db = float(decision.get("low_mid_cut_db", 0.0))
    if low_mid_cut_db > 0:
        hz = int(decision.get("low_mid_center_hz", 450))
        filters.append(f"equalizer=f={hz}:t=q:w=0.9:g=-{_db(low_mid_cut_db)}")
        actions.append({"stage": "low_mid_cleanup", "db": -low_mid_cut_db, "hz": hz})

    presence_boost_db = float(decision.get("presence_boost_db", 0.0))
    if presence_boost_db > 0:
        hz = int(decision.get("presence_center_hz", 3200))
        filters.append(f"equalizer=f={hz}:t=q:w=0.8:g={_db(presence_boost_db)}")
        actions.append({"stage": "presence_boost", "db": presence_boost_db, "hz": hz})

    air_shelf_db = float(decision.get("air_shelf_db", 0.0))
    if air_shelf_db > 0:
        hz = int(decision.get("air_start_hz", 10000))
        filters.append(f"treble=g={_db(air_shelf_db)}")
        actions.append({"stage": "air_shelf", "db": air_shelf_db, "hz": hz})

    if decision.get("use_deharsh"):
        db = float(decision.get("deharsh_db", 1.5))
        hz = int(decision.get("deharsh_center_hz", 3500))
        filters.append(f"equalizer=f={hz}:t=q:w=1.0:g=-{_db(db)}")
        actions.append({"stage": "deharsh", "db": -db, "hz": hz})

    deesser_db = float(decision.get("deesser_db", 0.0))
    if deesser_db > 0:
        deesser_hz = int(decision.get("deesser_hz", 6800))
        filters.append(f"equalizer=f={deesser_hz}:t=q:w=1.2:g=-{_db(deesser_db)}")
        actions.append({"stage": "dynamic_deesser", "db": -deesser_db, "hz": deesser_hz})

    resonance_cut_db = float(decision.get("resonance_cut_db", 0.0))
    if resonance_cut_db > 0:
        resonance_hz = int(decision.get("resonance_hz", 3500))
        filters.append(f"equalizer=f={resonance_hz}:t=q:w=2.2:g=-{_db(resonance_cut_db)}")
        actions.append({"stage": "resonance_hunter", "db": -resonance_cut_db, "hz": resonance_hz})

    drive = decision.get("multiband_drive", "medium")
    if decision.get("enable_main_compressor", False):
        if drive == "high":
            filters.append("acompressor=threshold=0.10:ratio=1.8:attack=20:release=200:makeup=1")
            actions.append({"stage": "compressor", "drive": "high"})
        elif drive == "low":
            filters.append("acompressor=threshold=0.16:ratio=1.25:attack=28:release=260:makeup=1")
            actions.append({"stage": "compressor", "drive": "low"})
        else:
            filters.append("acompressor=threshold=0.12:ratio=1.45:attack=24:release=220:makeup=1")
            actions.append({"stage": "compressor", "drive": "medium"})

    if decision.get("boost_transients") and modules.get("transient_shaper", True):
        # Keep limiter syntax broadly compatible with ffmpeg builds.
        transient_limit = float(decision.get("transient_support", 0.95))
        filters.append(f"alimiter=limit={max(0.85, min(0.99, transient_limit)):.2f}")
        actions.append({"stage": "transient_support", "focus": decision.get("transient_focus", "mid_high"), "limit": transient_limit})

    if decision.get("use_exciter") and modules.get("harmonic_exciter", True):
        exciter_drive = float(decision.get("exciter_drive", 8.0))
        filters.append(f"aexciter=amount=0.6:drive={max(1.0, min(12.0, exciter_drive)):.2f}:blend=0.2")
        actions.append({"stage": "exciter", "band": decision.get("exciter_band", "high_only"), "drive": exciter_drive})

    if modules.get("multiband_glue", True) and decision.get("enable_main_compressor", False):
        glue_strength = float(decision.get("multiband_glue_strength", 1.0))
        ratio = 1.1 + (max(0.0, min(2.0, glue_strength)) * 0.2)
        threshold = max(0.10, 0.18 - (glue_strength * 0.03))
        filters.append(f"acompressor=threshold={threshold:.2f}:ratio={ratio:.2f}:attack=14:release=180:makeup=1")
        actions.append({"stage": "multiband_glue", "profile": "transparent", "strength": glue_strength})

    if decision.get("human_glue_stage", False):
        filters.append("acompressor=threshold=0.16:ratio=1.15:attack=40:release=280:makeup=1")
        actions.append({"stage": "human_glue", "profile": "bus_like"})

    vocal_presence_boost_db = float(decision.get("vocal_presence_boost_db", 0.0))
    if vocal_presence_boost_db > 0:
        hz = int(decision.get("vocal_presence_hz", 2200))
        filters.append(f"equalizer=f={hz}:t=q:w=1.0:g={_db(vocal_presence_boost_db)}")
        actions.append({"stage": "vocal_focus", "db": vocal_presence_boost_db, "hz": hz})

    chorus_smooth_db = float(decision.get("chorus_smooth_db", 0.0))
    if chorus_smooth_db > 0:
        hz = int(decision.get("chorus_smooth_hz", 4800))
        filters.append(f"equalizer=f={hz}:t=q:w=1.1:g=-{_db(chorus_smooth_db)}")
        actions.append({"stage": "chorus_smooth", "db": -chorus_smooth_db, "hz": hz})

    instrument_glue_db = float(decision.get("instrument_glue_db", 0.0))
    if instrument_glue_db > 0:
        filters.append(f"volume={_db(instrument_glue_db)}dB")
        actions.append({"stage": "instrument_glue", "db": instrument_glue_db})

    bass_note_control_db = float(decision.get("bass_note_control_db", 0.0))
    if abs(bass_note_control_db) > 0.05:
        bass_hz = int(decision.get("bass_note_hz", 80))
        filters.append(f"equalizer=f={bass_hz}:t=q:w=1.4:g={_db(bass_note_control_db)}")
        actions.append({"stage": "bass_note_control", "db": bass_note_control_db, "hz": bass_hz})

    if decision.get("mono_low_end_fix"):
        filters.append("highpass=f=28")
        actions.append({"stage": "mono_low_end_fix", "f": 28})

    if decision.get("cd_low_weight_stage"):
        filters.append("equalizer=f=95:t=q:w=0.9:g=0.80")
        actions.append({"stage": "cd_low_weight", "db": 0.8, "hz": 95})

    if decision.get("cd_presence_stage"):
        filters.append("equalizer=f=3300:t=q:w=0.8:g=0.60")
        actions.append({"stage": "cd_presence", "db": 0.6, "hz": 3300})

    if modules.get("stereo_imager", True) and decision.get("widen_stereo", True):
        actions.append({
            "stage": "stereo_imager",
            "band": decision.get("widen_stereo_band", "high_only"),
            "amount": float(decision.get("widen_amount", 0.10)),
        })

    if modules.get("true_peak_limiter", True):
        # Keep limiter syntax broadly compatible with ffmpeg builds.
        limit = float(decision.get("limiter_ceiling_dbtp", -1.0))
        peak_linear = max(0.85, min(0.99, 10 ** (limit / 20.0)))
        if decision.get("smart_limiter"):
            lookahead = float(decision.get("limiter_lookahead_ms", 4.0))
            release = float(decision.get("limiter_release_ms", 60.0))
            filters.append(f"alimiter=limit={peak_linear:.3f}:attack={lookahead}:release={release}")
            actions.append({"stage": "smart_limiter", "lookahead_ms": lookahead, "release_ms": release, "ceiling_dbtp": limit})
        else:
            filters.append(f"alimiter=limit={peak_linear:.3f}")
            actions.append({"stage": "true_peak_limiter", "ceiling": limit})

    if decision.get("smart_ms_sculptor"):
        filters.append("extrastereo=m=1.08")
        actions.append({"stage": "smart_ms_sculptor", "amount": 1.08})

    actions.append({"stage": "human_strategy", "profile": human_pass_strategy})

    if int(settings.enable_free_plugin_hooks) == 1 and settings.ladspa_plugin_spec:
        spec = settings.ladspa_plugin_spec
        filters.append(f"ladspa=file={spec}")
        actions.append({"stage": "ladspa", "spec": spec})

    return ",".join(filters), actions
