import time

from src.core import TOXICO


def evaluate(y_true, decisions, is_toxic_callable):
    y_pred = [1 if is_toxic_callable(d) else 0 for d in decisions]
    return binary_metrics(y_true, y_pred)


def binary_metrics(y_true, y_pred):
    n = len(y_true)
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp + tn) / n if n else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision, "recall": recall, "f1": f1, "accuracy": accuracy,
        "n": n,
    }


def print_metrics_table(title, rows):
    header = f"| {title} | Precisión | Recall | F1 | Exactitud | TP | FP | FN |"
    sep = "|" + "-" * (len(title) + 2) + "|-----------|--------|----|-----------|----|----|----|"
    print(header)
    print(sep)
    for name, m in rows:
        print(
            f"| {name} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} "
            f"| {m['accuracy']:.3f} | {m['tp']} | {m['fp']} | {m['fn']} |"
        )


def is_toxic_traditional(d):
    return d.code == TOXICO


def is_toxic_ai(d):
    return d.code == TOXICO


def is_toxic_ai_detection(d):
    from src.core import REVISION_HUMANA

    return d.code in (TOXICO, REVISION_HUMANA)


def benchmark_classify(moderator, cases):
    start = time.perf_counter()
    decisions = []
    for msg, _, _ in cases:
        d = moderator.classify(msg) if hasattr(moderator, "classify") else moderator(msg)
        decisions.append(d)
    elapsed = time.perf_counter() - start
    return decisions, elapsed
