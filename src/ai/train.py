import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

MODEL_NAME = "distilbert-base-multilingual-cased"
ROOT = Path(__file__).resolve().parents[2]


class ToxicDataset(torch.utils.data.Dataset):
    def __init__(self, df, tokenizer, max_length=128):
        enc = tokenizer(
            list(df["message"].astype(str)),
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.labels = torch.tensor(list(df["label"]), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        return {
            "input_ids": self.input_ids[i],
            "attention_mask": self.attention_mask[i],
            "labels": self.labels[i],
        }


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    return {
        "accuracy": accuracy_score(labels, preds),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main():
    ap = argparse.ArgumentParser(description="Fine-tuning Transformer para toxicidad")
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--model", default=MODEL_NAME)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {device}")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=2)
    model.to(device)

    train_df = pd.read_csv(ROOT / "data" / "processed" / "train.csv")
    val_df = pd.read_csv(ROOT / "data" / "processed" / "val.csv")

    train_ds = ToxicDataset(train_df, tokenizer)
    val_ds = ToxicDataset(val_df, tokenizer)

    out_dir = ROOT / "models" / "toxic_transformer"
    args_ts = TrainingArguments(
        output_dir=str(out_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        per_device_eval_batch_size=args.batch * 2,
        learning_rate=args.lr,
        warmup_steps=100,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        fp16=(device == "cuda"),
        logging_steps=50,
        save_total_limit=2,
        seed=42,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args_ts,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))

    metrics = trainer.evaluate()
    print("\nMétricas en validación:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")

    print(f"\nModelo guardado en: {out_dir}")


if __name__ == "__main__":
    main()
