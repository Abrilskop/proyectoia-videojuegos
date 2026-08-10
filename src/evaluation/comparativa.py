import time
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.core import ADECUADO, GRITO, SPAM, TOXICO, ensure_utf8
from src.evaluation.metrics import (
    benchmark_classify,
    binary_metrics,
    is_toxic_ai,
    is_toxic_ai_detection,
    is_toxic_traditional,
    print_metrics_table,
)
from src.evaluation.test_cases import SPAM_REPEATS, SPAM_WINDOW, CASES
from src.traditional.detector import TraditionalModerator

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"


def markdown_table(title, rows):
    lines = [f"## {title}\n"]
    lines.append("| Sistema | Precisión | Recall | F1 | Exactitud |")
    lines.append("|---------|-----------|--------|----|-----------|")
    for name, m in rows:
        lines.append(
            f"| {name} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['accuracy']:.3f} |"
        )
    return "\n".join(lines)


def main():
    ensure_utf8()
    REPORTS.mkdir(parents=True, exist_ok=True)

    print("=== EVALUACIÓN COMPARATIVA: Tradicional vs IA ===\n")

    # --- Sistema Tradicional ---
    mod_trad = TraditionalModerator()
    trad_codes = []
    for msg, _, _ in CASES:
        trad_codes.append(mod_trad.classify(msg, user_id="eval_t").code)
    trad_decisions = [type("D", (), {"code": c})() for c in trad_codes]

    # --- Sistema IA ---
    from src.ai.inference import ToxicClassifier

    mod_ai = ToxicClassifier()
    ai_decisions, ai_time = benchmark_classify(lambda m: mod_ai.classify(m)[0], CASES)
    trad_decisions, trad_time = benchmark_classify(
        lambda m: mod_trad.classify(m, user_id="eval_t"), CASES
    )

    y_true = [label for _, label, _ in CASES]
    categories = [cat for _, _, cat in CASES]

    # --- Sistema Tradicional (bloqueo binario: TOXICO = positivo) ---
    trad_metrics = binary_metrics(y_true, [1 if d.code == TOXICO else 0 for d in trad_decisions])

    # --- IA: bloqueo automático (>= 80%) ---
    ai_metrics = binary_metrics(y_true, [1 if is_toxic_ai(d) else 0 for d in ai_decisions])

    # --- IA: detección (incluye cola humana) ---
    ai_det_metrics = binary_metrics(
        y_true, [1 if is_toxic_ai_detection(d) else 0 for d in ai_decisions]
    )

    print_metrics_table(
        "Bloqueo binario (positivo = mensaje tóxico)",
        [
            ("Tradicional (reglas)", trad_metrics),
            ("IA - bloqueo auto (>=80%)", ai_metrics),
            ("IA - detección (incl. revisión humana)", ai_det_metrics),
        ],
    )

    # --- Detalle por caso ---
    print("\n=== DETALLE POR CASO ===")
    rows = []
    for (msg, label, cat), td, ad in zip(CASES, trad_decisions, ai_decisions):
        mark = "OK " if (label == 1) == is_toxic_ai_detection(ad) else "FAIL"
        rows.append((msg, label, cat, td.code, ad.code, f"{ad.detail}", mark))
        print(
            f"{mark} [{cat:18s}] esperado={label} | TRAD={td.code:<9s} | IA={ad.code:<16s} | {msg!r}"
        )

    # --- Bulk sobre test.csv ---
    test_df = pd.read_csv(ROOT / "data" / "processed" / "test.csv")
    n_bulk = 400
    bulk = test_df.sample(n=min(n_bulk, len(test_df)), random_state=7)
    yb_true = list(bulk["label"])
    tb_decisions, tb_time = benchmark_classify(
        lambda m: mod_trad.classify(m, user_id="bulk"), list(zip(bulk["message"], yb_true, ["bulk"] * len(bulk)))
    )
    ab_decisions, ab_time = benchmark_classify(
        lambda m: mod_ai.classify(m)[0], list(zip(bulk["message"], yb_true, ["bulk"] * len(bulk)))
    )
    tb_metrics = binary_metrics(yb_true, [1 if d.code == TOXICO else 0 for d in tb_decisions])
    ab_metrics = binary_metrics(yb_true, [1 if is_toxic_ai(d) else 0 for d in ab_decisions])

    print("\n=== MUESTRA SOBRE DATASET DE TEST (n=%d) ===" % len(yb_true))
    print_metrics_table(
        "Clasificación binaria",
        [
            ("Tradicional (reglas)", tb_metrics),
            ("IA - bloqueo auto (>=80%)", ab_metrics),
        ],
    )

    # --- Gráfica ---
    systems = ["Tradicional", "IA\n(bloqueo >=80%)", "IA\n(detección)"]
    precision = [trad_metrics["precision"], ai_metrics["precision"], ai_det_metrics["precision"]]
    recall = [trad_metrics["recall"], ai_metrics["recall"], ai_det_metrics["recall"]]
    f1 = [trad_metrics["f1"], ai_metrics["f1"], ai_det_metrics["f1"]]
    accuracy = [trad_metrics["accuracy"], ai_metrics["accuracy"], ai_det_metrics["accuracy"]]

    x = range(len(systems))
    w = 0.2
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - 1.5 * w for i in x], precision, w, label="Precisión")
    ax.bar([i - 0.5 * w for i in x], recall, w, label="Recall")
    ax.bar([i + 0.5 * w for i in x], f1, w, label="F1")
    ax.bar([i + 1.5 * w for i in x], accuracy, w, label="Exactitud")
    ax.set_xticks(list(x))
    ax.set_xticklabels(systems)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Puntuación")
    ax.set_title("Comparativa: Paradigma Tradicional vs IA (casos del reporte)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    chart = REPORTS / "comparativa_grafica.png"
    fig.savefig(chart, dpi=150)
    print(f"\nGráfica guardada en: {chart}")

    # --- Reporte Markdown ---
    md = [
        "# Informe de Evaluación Comparativa",
        "",
        "## Descripción",
        "Ambos sistemas (paradigma tradicional basado en reglas y paradigma de IA basado en un Transformer)",
        "se evalúan con los **mismos casos de entrada**, incluyendo leetspeak, sarcasmo, contexto de juego",
        "y falsos positivos típicos del filtro por palabras clave.",
        "",
        f"**Modelo IA:** distilbert-base-multilingual-cased (fine-tuning) · 6000 ejemplos sintéticos.",
        "",
    ]
    md.append(markdown_table("Métricas sobre casos curados (n=%d)" % len(CASES), [
        ("Tradicional (reglas)", trad_metrics),
        ("IA - bloqueo automático (>=80%)", ai_metrics),
        ("IA - detección (incl. revisión humana)", ai_det_metrics),
    ]))
    md.append("")
    md.append(markdown_table("Muestra sobre dataset de test (n=%d)" % len(yb_true), [
        ("Tradicional (reglas)", tb_metrics),
        ("IA - bloqueo automático (>=80%)", ab_metrics),
    ]))

    md.append("")
    md.append("## Detalle por caso curado")
    md.append("")
    md.append("| Mensaje | Categoría | Etiqueta real | Tradicional | IA |")
    md.append("|---|---|---|---|---|")
    for (msg, label, cat), td, ad in zip(CASES, trad_decisions, ai_decisions):
        md.append(f"| `{msg}` | {cat} | {label} | {td.label} | {ad.label} |")

    md.append("")
    md.append(f"![Gráfica comparativa](comparativa_grafica.png)")
    md.append("")
    md.append(f"Tiempo de inferencia (casos curados): Tradicional {trad_time*1000:.1f} ms | IA {ai_time*1000:.1f} ms")
    md.append("")

    report = REPORTS / "comparativa_report.md"
    report.write_text("\n".join(md), encoding="utf-8")
    print(f"Reporte guardado en: {report}")


if __name__ == "__main__":
    main()
