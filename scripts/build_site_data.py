"""Genera docs/site/data.json para la página interactiva (docs/index.html).

Usa las mismas funciones de análisis que la matriz de docs/dimensiones_datos/,
así que la página muestra exactamente los números del README.
Uso: python scripts/build_site_data.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.aggregate import load_category_df, load_e2e_df  # noqa: E402
from analysis.generate_six_dimensions import _build_master_rows  # noqa: E402
from common.run_context import load_manifest  # noqa: E402

OUT = ROOT / "docs" / "site" / "data.json"
LOCAL = {"ollama", "faster-whisper", "piper"}


def _num(value, digits: int = 1):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return round(float(value), digits)


def _models() -> dict[str, str]:
    models: dict[str, str] = {}
    for cat in ("llm", "stt", "tts"):
        df = load_category_df(cat, latest_only=True)
        for (provider, model), _ in df.groupby(["provider", "model"]):
            models[f"{cat}/{provider}"] = str(model)
    return models


def _runs() -> dict[str, list]:
    """Cada llamada medida: [proveedor, test_id, latencia_ms] (+ WER en STT)."""
    out: dict[str, list] = {}
    for cat in ("llm", "stt", "tts"):
        df = load_category_df(cat, latest_only=True)
        rows = []
        for r in df.itertuples():
            row = [r.provider, r.test_id, _num(r.latency_ms)]
            if cat == "stt":
                row.append(_num(r.quality_metric, 4))
            rows.append(row)
        out[cat] = rows
    return out


def _json_rate() -> dict[str, float]:
    """Tasa de JSON válido publicada en llm_calidad.md.

    Se calculó con las respuestas completas de results/raw/, que no están en el repo;
    los CSV solo guardan un recorte y darían otra tasa.
    """
    md = (ROOT / "docs" / "dimensiones_datos" / "llm_calidad.md").read_text(encoding="utf-8")
    rates: dict[str, float] = {}
    for line in md.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[1].isdigit():
            rates[cells[0]] = float(cells[3])
    return rates


def _quality() -> dict[str, dict]:
    json_rate = _json_rate()
    notes = json.loads((ROOT / "data" / "llm_quality_notes.json").read_text(encoding="utf-8"))
    mos = json.loads((ROOT / "data" / "tts_mos_scores.json").read_text(encoding="utf-8"))
    q: dict[str, dict] = {}
    for p in notes["providers"]:
        q[f"llm/{p['provider']}"] = {
            "coherencia": p["coherencia_1_5"],
            "instrucciones": p["instrucciones_1_5"],
            "json": json_rate.get(p["provider"]),
        }
    for p in mos["providers"]:
        q[f"tts/{p['provider']}"] = {"naturalidad": p["mos_naturalidad"], "inteligibilidad": p["mos_inteligibilidad"]}
    return q


def _e2e() -> list[dict]:
    df = load_e2e_df(latest_only=True)
    stacks = []
    for esc, g in df.groupby("escenario", sort=False):
        first = g.iloc[0]
        stacks.append(
            {
                "escenario": esc,
                "stt": first["stt_provider"],
                "llm": first["llm_provider"],
                "tts": first["tts_provider"],
                "turnos": int(len(g)),
                "stt_ms": _num(g["stt_latency_ms"].mean()),
                "llm_ms": _num(g["llm_latency_ms"].mean()),
                "tts_ms": _num(g["tts_latency_ms"].mean()),
                "overhead_ms": _num(g["overhead_ms"].mean()),
                "total_ms": _num(g["total_latency_ms"].mean()),
                "costo_usd": _num(g["total_cost_usd"].mean(), 5),
                "corridas": [
                    {
                        "test_id": r.test_id,
                        "total_ms": _num(r.total_latency_ms),
                        "transcripcion": r.transcript_preview,
                        "respuesta": r.llm_response_preview,
                    }
                    for r in g.itertuples()
                ],
            }
        )
    return sorted(stacks, key=lambda s: s["total_ms"])


def main() -> None:
    models = _models()
    quality = _quality()
    services = []
    for row in _build_master_rows():
        key = row["servicio"]
        services.append(
            {
                "id": key,
                "categoria": row["categoria"],
                "proveedor": row["proveedor"],
                "modelo": models.get(key, ""),
                "local": row["proveedor"] in LOCAL,
                "latencia_ms": _num(row["latencia_ms"]),
                "ttft_ms": _num(row["ttft_ms"]),
                "wer": _num(row["wer"], 4),
                "costo_usd": _num(row["costo_usd"], 6),
                "privacidad": row["privacidad_1_5"],
                "customizacion": row["customizacion_1_5"],
                "integracion": row["integracion_1_5"],
                "calidad": quality.get(key, {}),
            }
        )
    data = {
        "run_batch_id": load_manifest().get("run_batch_id"),
        "servicios": services,
        "llamadas": _runs(),
        "e2e": _e2e(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(services)} servicios, {sum(len(v) for v in data['llamadas'].values())} llamadas, {len(data['e2e'])} stacks E2E")


if __name__ == "__main__":
    main()
