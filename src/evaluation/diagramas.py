"""Genera diagramas de flujo (PNG) de ambos paradigmas para el informe de la actividad."""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

AZUL = "#2b6cb0"
MORADO = "#6b46c1"
TEAL = "#319795"
ROJO = "#c53030"
AMARILLO = "#d69e2e"
VERDE = "#38a169"
GRIS = "#4a5568"


def box(ax, cx, cy, w, h, text, fc, ec, fs=8.5):
    ax.add_patch(
        FancyBboxPatch(
            (cx - w / 2, cy - h / 2),
            w,
            h,
            boxstyle="round,pad=0.05",
            linewidth=1.4,
            facecolor=fc,
            edgecolor=ec,
        )
    )
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color="#1a202c")


def diamond(ax, cx, cy, w, h, text, fc="#fde68a", ec="#b45309"):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=8.0, color="#1a202c")


def arrow(ax, x1, y1, x2, y2, label="", dx=0.0, dy=0.0):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=GRIS, lw=1.4),
    )
    if label:
        ax.text(
            (x1 + x2) / 2 + dx,
            (y1 + y2) / 2 + dy,
            label,
            fontsize=8.5,
            ha="center",
            va="center",
            color=GRIS,
        )


def diagrama_tradicional():
    fig, ax = plt.subplots(figsize=(11, 13))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 21)
    ax.axis("off")
    ax.set_title(
        "Flujo de Ejecución — Sistema Tradicional (paradigma simbólico)", fontsize=13
    )

    box(ax, 4.2, 19.7, 4.6, 1.4, "ENTRADA\nMensaje + ID de usuario + timestamp", "#e2e8f0", GRIS)
    arrow(ax, 4.2, 19.0, 4.2, 18.1)
    box(ax, 4.2, 17.4, 4.6, 1.4, "NORMALIZACIÓN\nminúsculas, sin tildes", "#e3f0fb", AZUL)
    arrow(ax, 4.2, 16.7, 4.2, 15.75)

    diamond(ax, 4.2, 14.9, 4.0, 1.8, "R1\n¿Palabra en\nlista negra?")
    arrow(ax, 4.2, 14.0, 4.2, 12.9)
    arrow(ax, 6.2, 15.1, 8.0, 15.5, "Sí", dx=0.1, dy=0.2)
    box(ax, 9.4, 15.5, 2.6, 1.4, "BLOQUEAR\nTóxico", "#fed7d7", ROJO)

    diamond(ax, 4.2, 12.0, 4.0, 1.8, "R2\n¿Leetspeak\nnormalizado?")
    arrow(ax, 4.2, 11.1, 4.2, 10.0)
    arrow(ax, 6.2, 12.2, 8.0, 12.6, "Sí", dx=0.1, dy=0.2)
    box(ax, 9.4, 12.6, 2.6, 1.4, "BLOQUEAR\nTóxico", "#fed7d7", ROJO)

    diamond(ax, 4.2, 9.0, 4.0, 1.8, "R4\n¿Spam?\n(>5 en 10 s)")
    arrow(ax, 4.2, 8.1, 4.2, 7.0)
    arrow(ax, 6.2, 9.2, 8.0, 9.6, "Sí", dx=0.1, dy=0.2)
    box(ax, 9.4, 9.6, 2.6, 1.4, "SILENCIAR\nSpam", "#fefcbf", AMARILLO)

    diamond(ax, 4.2, 6.0, 4.0, 1.8, "R3\n¿Grito?\n(>40, >90% MAYÚS)")
    arrow(ax, 4.2, 5.1, 4.2, 4.0)
    arrow(ax, 6.2, 6.2, 8.0, 6.6, "Sí", dx=0.1, dy=0.2)
    box(ax, 9.4, 6.6, 2.6, 1.4, "ADVERTIR\nGrito", "#fefcbf", AMARILLO)

    box(ax, 4.2, 3.3, 4.6, 1.4, "APROBAR\nAdecuado", "#c6f6d5", VERDE)

    fig.tight_layout()
    out = REPORTS / "diagrama_tradicional.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Guardado: {out}")


def diagrama_ia():
    fig, ax = plt.subplots(figsize=(11, 13))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 21)
    ax.axis("off")
    ax.set_title(
        "Flujo de Ejecución — Sistema de IA (Transformer, fine-tuning)", fontsize=13
    )

    ax.text(0.6, 11.9, "FASE DE ENTRENAMIENTO", fontsize=9, color=MORADO, weight="bold")
    ax.text(0.6, 10.6, "FASE DE INFERENCIA", fontsize=9, color=TEAL, weight="bold")
    ax.plot([0.5, 11.5], [11.1, 11.1], "--", color="#a0aec0", lw=1.2)

    box(ax, 4.2, 19.7, 5.0, 1.5, "DATOS DE ENTRENAMIENTO\n6000 ejemplos sintéticos\n(message, label) 45% / 55%", "#e9d8fd", MORADO)
    arrow(ax, 4.2, 18.95, 4.2, 18.0)
    box(ax, 4.2, 17.2, 5.0, 1.5, "PREPROCESAMIENTO\nTokenización distilBERT\n(padding/truncation a 128)", "#e9d8fd", MORADO)
    arrow(ax, 4.2, 16.45, 4.2, 15.5)
    box(ax, 4.2, 14.6, 5.0, 1.5, "FINE-TUNING\ndistilbert-base-multilingual-cased\nclasificación binaria (2 clases)", "#e9d8fd", MORADO)
    arrow(ax, 4.2, 13.85, 4.2, 12.9)
    box(ax, 4.2, 12.1, 5.0, 1.4, "MODELO ENTRENADO\n(Transformer con pesos ajustados)", "#faf5ff", MORADO)

    arrow(ax, 4.2, 11.4, 4.2, 10.45)
    box(ax, 4.2, 9.7, 5.0, 1.4, "ENTRADA EN TIEMPO REAL\nmensaje del chat", "#e6fffa", TEAL)
    arrow(ax, 4.2, 9.0, 4.2, 8.1)
    box(ax, 4.2, 7.3, 5.0, 1.4, "softmax → P(tóxico)", "#e6fffa", TEAL)
    arrow(ax, 4.2, 6.6, 4.2, 5.75)
    box(ax, 4.2, 5.0, 5.0, 1.4, "AJUSTE POR REPUTACIÓN\nhistórica del jugador", "#e6fffa", TEAL)
    arrow(ax, 4.2, 4.3, 4.2, 3.4)

    diamond(ax, 4.2, 2.6, 4.4, 1.7, "Aplicar umbrales\nde decisión", "#fde68a", "#b45309")

    box(ax, 9.5, 4.3, 3.0, 1.5, "BLOQUEAR\n(P ≥ 0.80)", "#fed7d7", ROJO)
    box(ax, 9.5, 2.6, 3.0, 1.5, "REVISIÓN HUMANA\n(0.50 ≤ P < 0.80)", "#fefcbf", AMARILLO)
    box(ax, 9.5, 0.9, 3.0, 1.5, "ADECUADO\n(P < 0.50)", "#c6f6d5", VERDE)

    arrow(ax, 6.4, 3.1, 8.0, 4.3, "≥ 0.80")
    arrow(ax, 6.4, 2.6, 8.0, 2.6, "0.50–0.80", dy=0.2)
    arrow(ax, 6.4, 2.1, 8.0, 0.9, "< 0.50")

    fig.tight_layout()
    out = REPORTS / "diagrama_ia.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Guardado: {out}")


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    diagrama_tradicional()
    diagrama_ia()


if __name__ == "__main__":
    main()
