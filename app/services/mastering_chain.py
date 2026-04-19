from app.core.config import settings

def _db(val: float) -> str:
    return f"{val:.2f}"

def build_ffmpeg_filter_chain(decision: dict):
    filters = []
    actions = []
    modules = decision.get("advanced_modules", {})

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

    drive = decision.get("multiband_drive", "medium")
    if drive == "high":
        filters.append("acompressor=threshold=0.08:ratio=2.5:attack=15:release=180:makeup=1")
        actions.append({"stage": "compressor", "drive": "high"})
    elif drive == "low":
        filters.append("acompressor=threshold=0.12:ratio=1.8:attack=20:release=200:makeup=0.5")
        actions.append({"stage": "compressor", "drive": "low"})
    else:
        filters.append("acompressor=threshold=0.10:ratio=2.1:attack=18:release=190:makeup=0.8")
        actions.append({"stage": "compressor", "drive": "medium"})

    if decision.get("boost_transients") and modules.get("transient_shaper", True):
        filters.append("alimiter=limit=0.95:level=disabled")
        actions.append({"stage": "transient_support", "focus": decision.get("transient_focus", "mid_high")})

    if decision.get("use_exciter") and modules.get("harmonic_exciter", True):
        filters.append("aexciter=amount=0.6:drive=8:blend=0.2")
        actions.append({"stage": "exciter", "band": decision.get("exciter_band", "high_only")})

    if modules.get("multiband_glue", True):
        filters.append("acompressor=threshold=0.11:ratio=1.5:attack=6:release=110:makeup=0.3")
        actions.append({"stage": "multiband_glue", "profile": "transparent"})

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

    if modules.get("stereo_imager", True) and decision.get("widen_stereo", True):
        actions.append({
            "stage": "stereo_imager",
            "band": decision.get("widen_stereo_band", "high_only"),
            "amount": float(decision.get("widen_amount", 0.10)),
        })

    if modules.get("true_peak_limiter", True):
        filters.append("alimiter=limit=0.98:level=disabled")
        actions.append({"stage": "true_peak_limiter", "ceiling": decision.get("limiter_ceiling_dbtp", -1.0)})

    if int(settings.enable_free_plugin_hooks) == 1 and settings.ladspa_plugin_spec:
        spec = settings.ladspa_plugin_spec
        filters.append(f"ladspa=file={spec}")
        actions.append({"stage": "ladspa", "spec": spec})

    return ",".join(filters), actions
