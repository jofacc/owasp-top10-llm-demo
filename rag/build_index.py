"""
极简 RAG 检索器（纯 numpy 实现 TF-IDF）。

设计：
- 中文分词用 1-gram + 2-gram 滑窗（不需装 jieba）
- corpus 目录下 6 篇常识短文，doc_05_poisoned 是投毒文档
  （把"一天有几小时"投毒写成 30 小时，错误一眼可见，且用"最新规定"话术让模型服从）
- 启动时自动构建索引；topK 余弦相似度
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Optional

import numpy as np

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
INDEX  = ROOT / "index.npz"

POISONED_IDS = {"doc_05_poisoned"}


# ------- 极简分词：英文按词，中文按 1-gram+2-gram ------- #
TOKEN_RE = re.compile(r"[A-Za-z]+|\d+|[\u4e00-\u9fa5]")

def tokenize(text: str) -> list[str]:
    cn = []
    en = []
    for tok in TOKEN_RE.findall(text):
        if "\u4e00" <= tok <= "\u9fa5":
            cn.append(tok)
        else:
            en.append(tok.lower())
    # 中文 1-gram + 2-gram
    bi = ["".join(cn[i:i+2]) for i in range(len(cn)-1)]
    return cn + bi + en


# ------- 索引构建 ------- #
def list_doc_paths() -> list[Path]:
    return sorted(CORPUS.glob("*.txt"))


def list_docs() -> list[dict]:
    out = []
    for p in list_doc_paths():
        text = p.read_text(encoding="utf-8")
        out.append({
            "id": p.stem, "size": len(text),
            "preview": text.strip().splitlines()[0] if text.strip() else "",
            "poisoned": p.stem in POISONED_IDS,
        })
    return out


def build_index() -> dict:
    paths = list_doc_paths()
    if not paths:
        raise RuntimeError(f"corpus is empty: {CORPUS}")
    docs = []
    for p in paths:
        docs.append({"id": p.stem, "text": p.read_text(encoding="utf-8")})

    # 词表
    vocab: dict[str, int] = {}
    tokenized = []
    for d in docs:
        toks = tokenize(d["text"])
        tokenized.append(toks)
        for t in set(toks):
            if t not in vocab:
                vocab[t] = len(vocab)

    N = len(docs); V = len(vocab)
    df = np.zeros(V)
    tf = np.zeros((N, V))
    for i, toks in enumerate(tokenized):
        seen = set()
        for t in toks:
            tf[i, vocab[t]] += 1
            if t not in seen:
                df[vocab[t]] += 1
                seen.add(t)
    idf = np.log((N + 1) / (df + 1)) + 1
    tfidf = tf * idf
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True) + 1e-9
    tfidf_n = tfidf / norms

    return {
        "ids":    np.array([d["id"] for d in docs]),
        "texts":  np.array([d["text"] for d in docs], dtype=object),
        "vocab":  vocab,
        "idf":    idf,
        "tfidf":  tfidf_n,
    }


_CACHE: dict | None = None

def get_index() -> dict:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    _CACHE = build_index()
    return _CACHE


def retrieve(question: str, top_k: int = 3, whitelist_only: bool = False) -> list[dict]:
    idx = get_index()
    vocab = idx["vocab"]; idf = idx["idf"]
    V = len(vocab)
    qvec = np.zeros(V)
    for t in tokenize(question):
        if t in vocab:
            qvec[vocab[t]] += 1
    if qvec.sum() == 0:
        return []
    qvec = qvec * idf
    qvec = qvec / (np.linalg.norm(qvec) + 1e-9)
    sims = idx["tfidf"] @ qvec   # (N,)

    order = np.argsort(-sims)
    out = []
    for i in order:
        doc_id = str(idx["ids"][i])
        if whitelist_only and doc_id in POISONED_IDS:
            continue
        text = str(idx["texts"][i])
        out.append({
            "id": doc_id,
            "score": float(sims[i]),
            "snippet": (text.strip().splitlines() + [""])[0][:160],
            "text": text,
            "poisoned": doc_id in POISONED_IDS,
        })
        if len(out) >= top_k:
            break
    return out


if __name__ == "__main__":
    idx = get_index()
    print(f"docs={len(idx['ids'])}  vocab={len(idx['vocab'])}")
    for q in ["一天有多少个小时", "太阳从哪个方向升起", "水的沸点是多少度"]:
        print(f"\nQ: {q}")
        for h in retrieve(q, 3):
            print(f"  {h['id']:<24} score={h['score']:.3f}  {h['snippet']}")
