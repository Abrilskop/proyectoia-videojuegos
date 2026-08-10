import json
import re
import unicodedata
from collections import deque
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_blacklist(path=BASE_DIR / "lista_negra.txt"):
    words = []
    for line in path.read_text(encoding="utf-8").splitlines():
        w = line.strip().lower()
        if w:
            words.append(w)
    return words


def load_leet(path=BASE_DIR / "leet_mapping.json"):
    return json.loads(path.read_text(encoding="utf-8"))


def strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def normalize(text):
    return strip_accents(text.lower())


def normalize_leetspeak(text, leet):
    t = normalize(text)
    for key in sorted(leet, key=len, reverse=True):
        t = t.replace(key, leet[key])
    return t


def clean_noise(text):
    t = re.sub(r"[^a-z0-9\s]", "", text)
    t = re.sub(r"(.)\1+", r"\1", t)
    return t


def word_pattern(word):
    return r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])"


def contains_blacklist(text, blacklist):
    for w in blacklist:
        if re.search(word_pattern(w), text):
            return w
    return None


def rule1_blacklist(message, blacklist):
    return contains_blacklist(normalize(message), blacklist)


def rule2_leetspeak(message, blacklist, leet):
    cleaned = clean_noise(normalize_leetspeak(message, leet))
    return contains_blacklist(cleaned, blacklist)


def rule3_shouting(message):
    if len(message) <= 40:
        return False
    letters = [c for c in message if c.isalpha()]
    if not letters:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) > 0.9


class SpamTracker:
    def __init__(self, window_seconds=10.0, max_repeats=5):
        self.window_seconds = window_seconds
        self.max_repeats = max_repeats
        self.history = {}

    def _prune(self, user_id, now):
        q = self.history.setdefault(user_id, deque())
        while q and now - q[0][1] > self.window_seconds:
            q.popleft()

    def is_spam(self, user_id, message, now):
        key = normalize(message)
        self._prune(user_id, now)
        q = self.history[user_id]
        q.append((key, now))
        count = sum(1 for k, _ in q if k == key)
        return count > self.max_repeats
