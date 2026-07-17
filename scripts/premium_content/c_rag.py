# -*- coding: utf-8 -*-
from _res import res


def course():
    m1 = """# لماذا يفشل RAG الساذج في الإنتاج؟ وإعداد التضمينات

## ماذا ستبني في هذه الدورة؟
نظام **استرجاع معزّز بالتوليد (RAG)** جاهز للإنتاج: تقسيم ذكي (مع دعم عربي)، بحث هجين (BM25 + Dense)، دمج **RRF**، إعادة ترتيب (Rerank)، برومبتات مضادّة للهلوسة، وتقييم RAGAS-style مع نشر ومراقبة.

هذه ليست «اربط PDF بـ ChatGPT». الهدف: **هندسة نظام** يُقاس ويُحسَّن ويُباع.

## مسار الإنتاج باختصار
```
مستندات → Chunking + Metadata → Embeddings → Vector DB
                                              ↓
استعلام → Sparse + Dense → RRF → Rerank → Context → LLM → إجابة + اقتباسات
                                              ↓
                                         تقييم / مراقبة
```

## لماذا يفشل RAG «الساذج»؟
| فشل شائع | السبب | أثر الإنتاج |
|----------|--------|-------------|
| أرقام/رموز دقيقة | التشابه الدلالي ضعيف | إجابة خاطئة بثقة |
| مصطلحات نادرة | لا مرادفات في التضمين | استرجاع صفر |
| Chunking رديء | سياق مقطوع أو صاخب | هلوسة أو «لا أعرف» زائد |
| Top-k ثابت بلا Rerank | سياق ملوّث | تكلفة توكن + ضجيج |
| بلا تقييم | لا خط أساس | انحدار صامت بعد تحديث البيانات |

## إعداد بيئة احترافية

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install "openai>=1.40" "numpy>=1.26" "httpx>=0.27" "tiktoken>=0.7"
```

## طبقة التضمين (Embeddings) — عقد إنتاج

```python
from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Sequence

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
EMBED_MODEL = "text-embedding-3-small"  # رخيص وسريع للبداية
# للإنتاج العربي الأقوى: جرّب text-embedding-3-large أو نموذج متعدد اللغات محلي


@dataclass(frozen=True)
class EmbedBatch:
    texts: tuple[str, ...]
    vectors: tuple[tuple[float, ...], ...]
    model: str
    latency_ms: int


def _normalize(text: str) -> str:
    # توحيد بسيط قبل التضمين — يمنع تكرار متجهات لنفس المعنى تقريباً
    return " ".join(text.replace("\\u200f", " ").replace("\\u200e", " ").split())


def embed_texts(
    texts: Sequence[str],
    *,
    model: str = EMBED_MODEL,
    batch_size: int = 64,
    max_retries: int = 4,
) -> EmbedBatch:
    cleaned = [_normalize(t) for t in texts]
    if not cleaned:
        raise ValueError("embed_texts: قائمة فارغة")

    all_vecs: list[tuple[float, ...]] = []
    t0 = time.perf_counter()

    for i in range(0, len(cleaned), batch_size):
        batch = cleaned[i : i + batch_size]
        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                resp = client.embeddings.create(model=model, input=batch)
                # API قد يعيد بترتيب index — لا تعتمد على ترتيب القائمة وحدها
                ordered = sorted(resp.data, key=lambda d: d.index)
                all_vecs.extend(tuple(d.embedding) for d in ordered)
                last_err = None
                break
            except Exception as e:
                last_err = e
                time.sleep(0.5 * (2 ** attempt))
        if last_err is not None:
            raise RuntimeError("فشل التضمين بعد إعادة المحاولة") from last_err

    ms = int((time.perf_counter() - t0) * 1000)
    return EmbedBatch(tuple(cleaned), tuple(all_vecs), model, ms)


def content_hash(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()[:16]
```

**قواعد إنتاج للتضمين:**
1. ثبّت اسم النموذج والإصدار في metadata — تغيير النموذج = إعادة فهرسة كاملة.
2. خزّن `content_hash` لتجنب إعادة تضمين نص لم يتغيّر.
3. قِس latency وعدد التوكنات؛ لا تضع التضمين داخل مسار الاستعلام دون cache.
4. لا تخلط أبعاد نماذج مختلفة في نفس الفهرس.

## خط أساس (Baseline) قبل أي «تحسين»

```python
# قِس قبل وبعد كل تغيير في الـ pipeline
BASELINE = {
    "retrieval_hit_at_5": 0.0,   # هل السياق الصحيح ضمن أفضل 5؟
    "answer_with_citation": 0.0,
    "avg_latency_ms": 0.0,
    "unknown_rate": 0.0,         # نسبة «لا أعرف» الصحيحة vs الخاطئة
}
```

بدون خط أساس ستحسّن «شعوراً» وتكسر الإنتاج.

## قائمة تحقق الوحدة 1
- [ ] مفتاح API في متغير بيئة وليس في الكود
- [ ] دالة `embed_texts` تعمل على دفعة 3 نصوص عربية/إنجليزية
- [ ] حفظ `model` + `content_hash` مع كل متجه
- [ ] جدول فشل RAG الساذج مفهوم لفريقك

## تمرين (مجاني — لكنه عميق)
1. ضمّن 20 فقرة من سياسة داخلية وهمية (إجازات، فوترة، SLA).
2. اطرح 10 أسئلة: 5 دلالية + 5 literal (أرقام/رموز).
3. سجّل يدوياً: هل أفضل 5 نتائج تحتوي الإجابة؟
4. اكتب فقرة: أين فشل التشابه الدلالي وحده؟

> الوحدة التالية: Chunking عربي + metadata — حيث يُربَح أو يُخسَر نصف جودة الاسترجاع.
""" + res([
        ("paper", "Retrieval-Augmented Generation (Lewis et al.) arXiv:2005.11401", "https://arxiv.org/abs/2005.11401"),
        ("docs", "OpenAI Embeddings guide", "https://platform.openai.com/docs/guides/embeddings"),
        ("blog", "Pinecone: What is RAG?", "https://www.pinecone.io/learn/retrieval-augmented-generation/"),
        ("video", "What is RAG? Retrieval-Augmented Generation explained (IBM)", "https://www.youtube.com/watch?v=T-D1OfcDW1M"),
        ("podcast", "Latent Space — RAG & retrieval", "https://www.latent.space/"),
    ])

    m2 = """# استراتيجيات التقسيم (Chunking) للعربية والبيانات الوصفية

## الهدف
تحويل المستندات إلى **وحدات استرجاع** قابلة للتتبع: حجم مناسب، حدود لغوية صحيحة، وmetadata كافية للاقتباس والتصفية.

## مبادئ قبل الكود
1. **الوحدة الدلالية** أهم من العدد السحري للأحرف.
2. العربية: فواصل الفقرات `\\n\\n` والجمل (`.` `؟` `!`) أوثق من التقسيم على مسافات فقط.
3. كل chunk يحتاج: `doc_id`, `source`, `section`, `page` أو `offset`, `language`, `content_hash`.
4. overlap يمنع قطع تعريف عبر حدود الجزء — لكن overlap زائد = تكرار وضجيج.

## مقسّم عملي (Recursive + فواصل عربية)

```python
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    source: str
    section: str
    page: int | None
    char_start: int
    char_end: int
    language: str
    content_hash: str


AR_SEP_PRIORITY = [
    "\\n\\n",
    "\\n",
    "۔",   # فاصلة أردو/فارسية أحياناً في نصوص مختلطة
    ". ",
    "؟ ",
    "! ",
    "، ",
    " ",
    "",
]


def _split_once(text: str, sep: str) -> list[str]:
    if sep == "":
        return list(text)
    if not sep:
        return [text]
    parts = text.split(sep)
    out: list[str] = []
    for i, p in enumerate(parts):
        if i < len(parts) - 1:
            out.append(p + sep)
        elif p:
            out.append(p)
    return [x for x in out if x]


def recursive_split(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    for sep in AR_SEP_PRIORITY:
        pieces = _split_once(text, sep) if sep != "" else list(text)
        if len(pieces) == 1 and sep != "":
            continue
        # دمج القطع حتى تقترب من chunk_size
        merged: list[str] = []
        buf = ""
        for piece in pieces:
            if not buf:
                buf = piece
            elif len(buf) + len(piece) <= chunk_size:
                buf += piece
            else:
                merged.append(buf)
                buf = piece
        if buf:
            merged.append(buf)

        # إن بقيت قطع أطول من الحد — قسّم بمستوى أعمق
        final: list[str] = []
        for m in merged:
            if len(m) > chunk_size and sep != "":
                final.extend(recursive_split(m, chunk_size, overlap))
            else:
                final.append(m)

        if overlap > 0 and len(final) > 1:
            with_ov: list[str] = []
            for i, ch in enumerate(final):
                if i == 0:
                    with_ov.append(ch)
                else:
                    prev_tail = final[i - 1][-overlap:]
                    with_ov.append(prev_tail + ch)
            return with_ov
        return final

    # fallback: نوافذ ثابتة
    step = max(1, chunk_size - overlap)
    return [text[i : i + chunk_size] for i in range(0, len(text), step)]


def chunk_document(
    text: str,
    *,
    doc_id: str,
    source: str,
    section: str = "",
    page: int | None = None,
    language: str = "ar",
    chunk_size: int = 700,
    overlap: int = 100,
) -> list[Chunk]:
    import hashlib

    parts = recursive_split(text, chunk_size=chunk_size, overlap=overlap)
    chunks: list[Chunk] = []
    cursor = 0
    for part in parts:
        # تقدير offset (مع overlap قد لا يكون فريداً — احتفظ بـ char_start تقريبي)
        idx = text.find(part[:80], cursor) if part else -1
        start = idx if idx >= 0 else cursor
        end = start + len(part)
        h = hashlib.sha256(part.encode("utf-8")).hexdigest()[:16]
        chunks.append(
            Chunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                text=part,
                source=source,
                section=section,
                page=page,
                char_start=start,
                char_end=end,
                language=language,
                content_hash=h,
            )
        )
        cursor = max(cursor, start + 1)
    return chunks
```

## Metadata للتصفية والاقتباس

```python
def to_index_record(chunk: Chunk, vector: list[float]) -> dict:
    return {
        "id": chunk.chunk_id,
        "values": vector,
        "metadata": {
            "doc_id": chunk.doc_id,
            "source": chunk.source,
            "section": chunk.section,
            "page": chunk.page,
            "language": chunk.language,
            "content_hash": chunk.content_hash,
            "text": chunk.text[:2000],  # حدّ حسب قاعدة المتجهات
            "char_start": chunk.char_start,
            "char_end": chunk.char_end,
        },
    }
```

## أنماط Chunking حسب نوع المستند
| نوع | استراتيجية | ملاحظة |
|-----|------------|--------|
| سياسات / FAQ | فقرة أو Q/A كامل | لا تقطع السؤال عن الجواب |
| عقود | بند (Article) + overlap | metadata: رقم البند |
| كود | دالة/ملف | استخدم AST لا أحرفاً فقط |
| جداول | صف + ترويسة مكررة | وإلا يضيع المعنى |

## أخطاء مكلفة
- `chunk_size=2000` بلا تجربة → سياق صاخب وتكلفة توليد عالية
- تجاهل العناوين → كل الأجزاء تبدو متشابهة دلالياً
- metadata ناقصة → لا تستطيع قول «حسب صفحة 12 من الدليل»
- تنظيف HTML سيء → ضجيج في التضمين

## تمرين
1. خذ مستنداً عربياً 5–10 صفحات.
2. جرّب `chunk_size` = 400 / 700 / 1200 مع overlap 80–120.
3. لنفس 10 أسئلة الوحدة 1: أي إعداد يعطي أفضل hit@5؟
4. أضف تصفية `language=ar` و `doc_id` في استعلام وهمي.
""" + res([
        ("docs", "LangChain text splitters", "https://python.langchain.com/docs/how_to/recursive_text_splitter/"),
        ("blog", "Chunking strategies for RAG (Pinecone)", "https://www.pinecone.io/learn/chunking-strategies/"),
        ("paper", "Lost in the Middle arXiv:2307.03172", "https://arxiv.org/abs/2307.03172"),
        ("video", "Chunking strategies for RAG (LangChain)", "https://www.youtube.com/watch?v=8OJC21T2SL4"),
        ("podcast", "Practical AI — retrieval systems", "https://changelog.com/practicalai"),
    ])

    m3 = """# البحث الهجين وتنفيذ Reciprocal Rank Fusion (RRF)

## لماذا الهجين؟
- **Dense (متجهات)**: يفهم المعنى والمرادفات والصياغة.
- **Sparse (BM25 / كلمات مفتاحية)**: يتفوّق على الرموز، الأرقام، الأسماء الحرفية، والمصطلحات النادرة.

الدمج يغطّي ضعف كل طرف. في الإنتاج: استرجع من الاثنين ثم ادمج بـ **RRF** (لا تحتاج معايرة درجات معقّدة بين نظامين).

## BM25 مبسّط للتجربة المحلية

```python
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Sequence


_token_re = re.compile(r"[\\w\\u0600-\\u06FF]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _token_re.findall(text)]


class BM25Index:
    def __init__(self, docs: Sequence[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = list(docs)
        self.tokenized = [tokenize(d) for d in self.docs]
        self.N = len(self.docs)
        self.doc_len = [len(t) for t in self.tokenized]
        self.avgdl = sum(self.doc_len) / self.N if self.N else 0.0
        self.df: dict[str, int] = defaultdict(int)
        for toks in self.tokenized:
            for term in set(toks):
                self.df[term] += 1

    def _idf(self, term: str) -> float:
        n = self.df.get(term, 0)
        # idf سلس يتجنّب السالب للصفر
        return math.log(1 + (self.N - n + 0.5) / (n + 0.5))

    def search(self, query: str, top_k: int = 20) -> list[tuple[int, float]]:
        q_terms = tokenize(query)
        scores = [0.0] * self.N
        for i, toks in enumerate(self.tokenized):
            tf = Counter(toks)
            dl = self.doc_len[i]
            s = 0.0
            for term in q_terms:
                if term not in tf:
                    continue
                idf = self._idf(term)
                freq = tf[term]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1.0))
                s += idf * (freq * (self.k1 + 1)) / denom
            scores[i] = s
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [(idx, sc) for idx, sc in ranked[:top_k] if sc > 0]
```

## Dense: تشابه جيب التمام

```python
import numpy as np


def cosine_search(
    query_vec: Sequence[float],
    matrix: np.ndarray,
    top_k: int = 20,
) -> list[tuple[int, float]]:
    q = np.asarray(query_vec, dtype=np.float32)
    q = q / (np.linalg.norm(q) + 1e-12)
    # matrix: (N, D) مفترض مطبّع صفياً للأداء
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12
    m = matrix / norms
    sims = m @ q
    idx = np.argpartition(-sims, min(top_k, len(sims) - 1))[:top_k]
    idx = idx[np.argsort(-sims[idx])]
    return [(int(i), float(sims[i])) for i in idx]
```

## RRF — الدمج الذهبي البسيط

```python
def reciprocal_rank_fusion(
    rankings: list[list[int]],
    *,
    k: int = 60,
    top_n: int = 20,
) -> list[tuple[int, float]]:
    \"\"\"rankings: كل عنصر قائمة معرّفات مرتّبة من الأفضل للأضعف.\"\"\"
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]


def hybrid_search(
    query: str,
    query_vec: Sequence[float],
    bm25: BM25Index,
    dense_matrix: np.ndarray,
    *,
    sparse_k: int = 30,
    dense_k: int = 30,
    rrf_k: int = 60,
    final_k: int = 20,
) -> list[tuple[int, float]]:
    sparse = [i for i, _ in bm25.search(query, top_k=sparse_k)]
    dense = [i for i, _ in cosine_search(query_vec, dense_matrix, top_k=dense_k)]
    return reciprocal_rank_fusion([sparse, dense], k=rrf_k, top_n=final_k)
```

## ملاحظات إنتاج
- **k=60** شائع في أدبيات RRF؛ لا تُفرط في ضبطه قبل قياس hit@k.
- صفِّ بـ metadata قبل أو بعد الدمج (مثلاً `doc_type=policy`).
- في قواعد متجهية (Qdrant/pgvector): نفّذ dense هناك وBM25 في Elasticsearch/OpenSearch أو sparse vectors إن وُجدت.
- سجّل: عدد نتائج sparse/dense، تقاطع القائمتين، latency كل فرع.

## أخطاء مكلفة
- جمع درجات BM25 و cosine مباشرة بلا تطبيع → يسيطر مقياس واحد
- top_k صغير جداً قبل RRF → تفقد مرشحين جيدين
- تجاهل الاستعلامات الحرفية (SKU، أرقام تذاكر)

## تمرين
1. ابنِ فهرس BM25 + مصفوفة dense على 100 chunk.
2. قارن: dense فقط vs hybrid على 15 سؤالاً (hit@5).
3. غيّر `rrf_k` بين 20 و 60 و 100 — هل يتغيّر الترتيب كثيراً؟
""" + res([
        ("paper", "Reciprocal Rank Fusion (Cormack et al.)", "https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf"),
        ("docs", "Qdrant hybrid queries", "https://qdrant.tech/documentation/concepts/hybrid-queries/"),
        ("blog", "Elastic: hybrid search explained", "https://www.elastic.co/what-is/hybrid-search"),
        ("video", "Hybrid search — combining BM25 and dense vectors", "https://www.youtube.com/watch?v=r-uOLxNrNk8"),
        ("podcast", "TWIML AI — information retrieval", "https://twimlai.com/podcast/twimlai/"),
    ])

    m4 = """# إعادة الترتيب (Reranking) وبرومبتات مضادّة للهلوسة

## الفكرة
الهجين يجلب **مرشحين** (مثلاً 20–50). الـ **Cross-Encoder / Reranker** يقرأ (استعلام، مقطع) معاً ويعطي درجة أدق — ثم ترسل أفضل 3–8 مقاطع فقط للنموذج التوليدي.

```
Hybrid top-30  →  Rerank  →  top-5 context  →  LLM (grounded prompt)
```

## Rerank عبر API أو نموذج محلي (نمط واجهة موحّد)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass
class RankedChunk:
    chunk_id: str
    text: str
    score: float
    source: str
    page: int | None


class Reranker(Protocol):
    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        ...


class HeuristicReranker:
    \"\"\"بديل خفيف للتطوير المحلي دون GPU — ليس بديلاً نهائياً للإنتاج الثقيل.\"\"\"

    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        q = set(query.lower().split())
        out: list[float] = []
        for p in passages:
            toks = p.lower().split()
            if not toks:
                out.append(0.0)
                continue
            overlap = len(q.intersection(toks)) / max(1, len(q))
            # عقوبة المقاطع الطويلة جداً قليلاً
            length_pen = min(1.0, 400 / max(20, len(toks)))
            out.append(overlap * 0.8 + length_pen * 0.2)
        return out


def rerank(
    query: str,
    chunks: Sequence[RankedChunk],
    reranker: Reranker,
    top_n: int = 5,
) -> list[RankedChunk]:
    scores = reranker.score(query, [c.text for c in chunks])
    ranked = [
        RankedChunk(c.chunk_id, c.text, float(s), c.source, c.page)
        for c, s in zip(chunks, scores)
    ]
    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:top_n]
```

### استخدام Cross-Encoder (عند توفر transformers)

```python
# pip install sentence-transformers
# from sentence_transformers import CrossEncoder
# model = CrossEncoder("BAAI/bge-reranker-v2-m3")
# scores = model.predict([(query, p) for p in passages])
```

للإنتاج متعدد اللغات (ومنها العربية) يُفضَّل reranker معروف مثل **bge-reranker** أو خدمة Cohere Rerank — قِس latency وVRAM.

## بناء السياق مع حدود توكن

```python
def build_context(chunks: Sequence[RankedChunk], max_chars: int = 6000) -> str:
    blocks: list[str] = []
    used = 0
    for i, c in enumerate(chunks, start=1):
        cite = c.source + (f" p.{c.page}" if c.page is not None else "")
        block = f"[{i}] ({cite})\\n{c.text.strip()}\\n"
        if used + len(block) > max_chars:
            break
        blocks.append(block)
        used += len(block)
    return "\\n".join(blocks)
```

## برومبت مضادّ للهلوسة (إنتاج)

```python
SYSTEM_GROUNDED = (
    "أنت مساعد إجابات مؤسسي. قواعد صارمة: "
    "1) أجب فقط اعتماداً على مقاطع CONTEXT المرقّمة. "
    "2) إن لم تكفِ المعلومات، قل صراحة: لا تتوفر معلومات كافية في المصادر. "
    "3) بعد كل ادّعاء جوهري ضع اقتباساً مثل [1] أو [2]. "
    "4) لا تختلق أرقاماً أو تواريخ أو سياسات غير موجودة في السياق. "
    "5) إن تعارضت المقاطع، اذكر التعارض ولا ترجّح بلا دليل."
)


def build_user_prompt(question: str, context: str) -> str:
    return (
        "CONTEXT:\\n"
        + context
        + "\\n\\nQUESTION:\\n"
        + question
        + "\\n\\nأجب بالعربية الفصحى الموجزة مع اقتباسات."
    )


def generate_answer(client, model: str, question: str, context: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_GROUNDED},
            {"role": "user", "content": build_user_prompt(question, context)},
        ],
    )
    return resp.choices[0].message.content or ""
```

## طبقات إضافية ضد الهلوسة
1. **Refusal عند درجات منخفضة**: إن أعلى score بعد rerank < عتبة → «لا أعرف» دون استدعاء توليد مكلف.
2. **تحقق اقتباس**: هل الأرقام في الإجابة تظهر في السياق؟
3. **فصل الاسترجاع عن الأسلوب**: لا تطلب إبداعاً أدبياً في سياسات الامتثال.
4. **سجل audit**: query, chunk_ids, scores, answer, model, latency.

```python
def should_refuse(ranked: Sequence[RankedChunk], min_score: float = 0.15) -> bool:
    if not ranked:
        return True
    return ranked[0].score < min_score
```

## أخطاء مكلفة
- إرسال top-20 كاملاً للنموذج «للاحتياط» → ضياع في الوسط (Lost in the Middle) + تكلفة
- temperature عالية في إجابات حقائق
- عدم عرض المصادر للمستخدم النهائي (يفقد الثقة)

## تمرين
1. خذ top-20 من الوحدة 3، أعد ترتيبها، واحفظ top-5 فقط.
2. ولّد إجابتين: برومبت حر vs SYSTEM_GROUNDED — قارن الهلوسة.
3. نفّذ عتبة refuse على 5 أسئلة خارج النطاق.
""" + res([
        ("paper", "Sentence-BERT / cross-encoders arXiv:1908.10084", "https://arxiv.org/abs/1908.10084"),
        ("docs", "Cohere Rerank documentation", "https://docs.cohere.com/docs/rerank-guide"),
        ("blog", "Anthropic: reducing hallucinations", "https://www.anthropic.com/research"),
        ("video", "Reranking in RAG with cross-encoders", "https://www.youtube.com/watch?v=Uh9bYiVrW_s"),
        ("podcast", "Latent Space — evaluation & groundedness", "https://www.latent.space/"),
    ])

    m5 = """# التقييم (RAGAS-style) والنشر والمراقبة

## لماذا التقييم أولاً؟
بدون مجموعة ذهبية صغيرة (30–100 سؤال) أي «تحسين» تخمين. في الإنتاج نراقب **الاسترجاع** و**الإخلاص للمصادر** و**الصلة** و**الlatency** و**التكلفة**.

## مجموعة تقييم خفيفة

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass
class EvalItem:
    question: str
    golden_answer: str
    # معرفات المقاطع التي يجب أن تظهر في الاسترجاع
    relevant_chunk_ids: set[str]


@dataclass
class PipelineResult:
    answer: str
    retrieved_ids: list[str]
    contexts: list[str]
    latency_ms: int
    refused: bool


def hit_at_k(retrieved: Sequence[str], relevant: set[str], k: int = 5) -> float:
    top = set(retrieved[:k])
    return 1.0 if top.intersection(relevant) else 0.0


def context_precision_proxy(retrieved: Sequence[str], relevant: set[str], k: int = 5) -> float:
    top = retrieved[:k]
    if not top:
        return 0.0
    good = sum(1 for r in top if r in relevant)
    return good / len(top)


def faithfulness_proxy(answer: str, contexts: Sequence[str]) -> float:
    \"\"\"تقريب بسيط بدون LLM-as-judge: نسبة توكنات الإجابة التي تظهر في السياق.
    للإنتاج استخدم قاضياً (RAGAS faithfulness) فوق هذا الخط الأساس.\"\"\"
    if not answer.strip():
        return 0.0
    ctx = " ".join(contexts).lower()
    toks = [t for t in answer.lower().split() if len(t) > 3]
    if not toks:
        return 0.0
    hit = sum(1 for t in toks if t in ctx)
    return hit / len(toks)


def evaluate_pipeline(
    items: Sequence[EvalItem],
    run: Callable[[str], PipelineResult],
    k: int = 5,
) -> dict:
    hits, precs, faiths, latencies = [], [], [], []
    for it in items:
        r = run(it.question)
        hits.append(hit_at_k(r.retrieved_ids, it.relevant_chunk_ids, k=k))
        precs.append(context_precision_proxy(r.retrieved_ids, it.relevant_chunk_ids, k=k))
        faiths.append(faithfulness_proxy(r.answer, r.contexts))
        latencies.append(r.latency_ms)
    n = max(1, len(items))
    return {
        "hit_at_%d" % k: sum(hits) / n,
        "context_precision@%d" % k: sum(precs) / n,
        "faithfulness_proxy": sum(faiths) / n,
        "p50_latency_ms": sorted(latencies)[len(latencies) // 2] if latencies else 0,
        "n": len(items),
    }
```

### ربط ذهني مع RAGAS
| مقياس RAGAS | ماذا يقيس | بديلنا السريع |
|-------------|-----------|----------------|
| Faithfulness | هل الإجابة مدعومة بالسياق؟ | `faithfulness_proxy` + قاضي LLM لاحقاً |
| Answer relevancy | هل تجيب السؤال؟ | مراجعة بشرية + قاضي |
| Context precision/recall | جودة الاسترجاع | hit@k + precision@k |

## نشر FastAPI جاهز للربط

```python
import logging
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("rag")
api = FastAPI(title="Production RAG")


class AskIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    session_id: str = Field(..., min_length=3)
    top_k: int = Field(5, ge=1, le=10)


class AskOut(BaseModel):
    answer: str
    citations: list[dict]
    refused: bool
    latency_ms: int


@api.post("/v1/ask", response_model=AskOut)
def ask(body: AskIn):
    t0 = time.perf_counter()
    try:
        # pipeline: hybrid → rrf → rerank → generate (من الوحدات السابقة)
        result = run_rag_pipeline(body.question, top_k=body.top_k)
    except Exception:
        log.exception("rag_fail session=%s", body.session_id)
        raise HTTPException(status_code=500, detail="rag_error")
    ms = int((time.perf_counter() - t0) * 1000)
    log.info(
        "ok session=%s ms=%s refused=%s n_cite=%s",
        body.session_id,
        ms,
        result["refused"],
        len(result["citations"]),
    )
    return AskOut(
        answer=result["answer"],
        citations=result["citations"],
        refused=result["refused"],
        latency_ms=ms,
    )
```

## مراقبة (الحد الأدنى للإنتاج)
- **RED**: Rate, Errors, Duration لمسار `/v1/ask`
- **جودة**: معدل الرفض، نسبة إجابات بلا اقتباس، hit@5 على عينة أسبوعية
- **تكلفة**: توكنات تضمين + توليد لكل طلب
- **بيانات**: زمن آخر إعادة فهرسة، عدد chunks، نموذج التضمين

```python
METRICS = {
    "requests_total": 0,
    "errors_total": 0,
    "refuse_total": 0,
    "latency_ms_sum": 0,
}


def observe(ok: bool, refused: bool, latency_ms: int) -> None:
    METRICS["requests_total"] += 1
    if not ok:
        METRICS["errors_total"] += 1
    if refused:
        METRICS["refuse_total"] += 1
    METRICS["latency_ms_sum"] += latency_ms
```

## قائمة إطلاق
- [ ] مجموعة تقييم ≥ 30 سؤالاً مع relevant_chunk_ids
- [ ] خط أساس hit@5 و latency قبل الإطلاق
- [ ] cache للتضمين والاستعلامات المتكررة
- [ ] أسرار في secret manager
- [ ] حد معدل (rate limit) لكل session/API key
- [ ] لا تسجّل بيانات شخصية خاماً في اللوجات
- [ ] خطة إعادة فهرسة عند تحديث المستندات
- [ ] تنبيه عند انخفاض hit@5 أو ارتفاع errors

## مشروع تخرج الدورة
نظام FAQ داخلي: 50+ مستنداً، hybrid+RRF+rerank، API، تقرير مقاييس صفحة واحدة، ومقارنة before/after لتغيير chunk_size واحد فقط.

> إن قِست قبل أن «تحسّن»، فأنت مهندس إنتاج — لا هاوٍ تجميع مكتبات.
""" + res([
        ("paper", "RAGAS framework arXiv:2309.15217", "https://arxiv.org/abs/2309.15217"),
        ("docs", "RAGAS documentation", "https://docs.ragas.io/"),
        ("blog", "LangSmith / tracing RAG pipelines", "https://docs.smith.langchain.com/"),
        ("video", "Evaluating RAG pipelines with RAGAS", "https://www.youtube.com/watch?v=fWC4VxolWAk"),
        ("podcast", "Software Engineering Daily — ML in production", "https://softwareengineeringdaily.com/"),
    ])

    return {
        "title": "بناء نظام RAG للإنتاج مع البحث الهجين وإعادة الترتيب",
        "description": "دورة هندسية مدفوعة: من فشل RAG الساذج إلى Embeddings وChunking عربي، Hybrid+RRF، Reranking، برومبتات مضادّة للهلوسة، تقييم RAGAS-style، ونشر FastAPI مع مراقبة — بكود بايثون جاهز للإنتاج.",
        "tags": ["RAG", "Hybrid Search", "Reranking", "Embeddings", "RRF", "Production", "Arabic NLP"],
        "price": 39,
        "duration": "10 ساعات",
        "gradient": "from-emerald-500 to-teal-500",
        "modules": [
            {"title": "الوحدة 1: لماذا يفشل RAG الساذج وإعداد التضمينات", "content": m1},
            {"title": "الوحدة 2: استراتيجيات Chunking للعربية والـ Metadata", "content": m2},
            {"title": "الوحدة 3: البحث الهجين وتنفيذ RRF", "content": m3},
            {"title": "الوحدة 4: إعادة الترتيب وبرومبتات مضادّة للهلوسة", "content": m4},
            {"title": "الوحدة 5: التقييم (RAGAS-style) والنشر والمراقبة", "content": m5},
        ],
    }
