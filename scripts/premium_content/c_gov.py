# -*- coding: utf-8 -*-
from _res import res


def course():
    m1 = """# تصنيف مخاطر الذكاء الاصطناعي ولماذا يهم السياق العربي

## تنويه
هذه الوحدة **تعليمية هندسية** وليست استشارة قانونية. للامتثال التنظيمي استشر مستشاراً مؤهلاً في ولايتك القضائية.

## ماذا ستبني في الدورة؟
إطار عمل تطبيقي: تصنيف مخاطر → وعي تنظيمي عالي المستوى → تدقيق بيانات ولهجات → تفسير وSHAP-level + سجلات تدقيق → **بوابة امتثال** داخل MLOps قبل الإنتاج.

## ما هي حوكمة الذكاء الاصطناعي؟
مجموعة سياسات + أدوار + ضوابط تقنية تضمن أن النظام: **آمن نسبياً، عادل بقدر ممكن، قابل للمساءلة، وقابل للتدقيق** — طوال دورة الحياة لا لحظة الإطلاق فقط.

## تصنيف مخاطر عملي للفرق الهندسية

| مستوى | أمثلة | ضوابط دنيا |
|-------|--------|------------|
| منخفض | تلخيص داخلي غير حسّاس | سياسة بيانات + سجل إصدار |
| محدود | شات دعم عام | إفصاح أنه ذكاء اصطناعي + حواجز |
| مرتفع | ائتمان، توظيف، صحة، هوية | تقييم أثر، بشر في الحلقة، مقاييس عدالة، audit log |
| محظور/مرفوض داخلياً | تلاعب سلوكي خادع، تجسس جماعي غير مشروع | لا تُبنَى |

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List

class RiskLevel(str, Enum):
    low = "low"
    limited = "limited"
    high = "high"
    prohibited_internal = "prohibited_internal"

@dataclass
class SystemCard:
    name: str
    purpose: str
    data_categories: List[str]
    users: List[str]
    automated_decision: bool
    human_appeal: bool
    risk: RiskLevel
    residual_notes: str = ""

def classify_risk(card: SystemCard) -> RiskLevel:
    high_triggers = {"health", "credit", "biometrics", "employment", "identity"}
    if card.risk == RiskLevel.prohibited_internal:
        return card.risk
    if card.automated_decision and set(card.data_categories) & high_triggers:
        return RiskLevel.high
    if card.automated_decision:
        return RiskLevel.limited
    return RiskLevel.low
```

## لماذا السياق العربي ليس «ترجمة للإنجليزية»؟
1. **تمثيل لغوي**: كثير من النماذج تُدرَّب بكثافة على الإنجليزية؛ العربية الفصحى واللهجات تمثيلها أضعف → أخطاء فهم وتوليد.
2. **تنوّع لهجي**: خليجي، مصري، شامي، مغاربي… معيار «دقة عامة» يخفي فشلاً على شرائح.
3. **حساسية ثقافية ودينية**: هلوسة في سياقات مقدّسة أو قانونية قد تكون أشد ضرراً.
4. **بيانات أقل تنظيفاً**: زحف ويب بلا مراجعة يُدخل تحيّزاً وسُمية.
5. **قنوات خدمة**: مستخدمون يتوقعون عربية طبيعية لا فصحى صلبة فقط — أو العكس في الوثائق الرسمية.

## مخاطر شائعة في منتجات عربية
| خطر | مظهر |
|-----|------|
| تحيّز لهجي | لهجة «أ» تُصنَّف سلبية أكثر |
| تمييز جغرافي | أداء أضعف على أسماء/مدن معيّنة |
| هلوسة معرفية | فتاوى/قوانين مختلقة |
| خصوصية | تسريب أرقام هوية/جوال في السجلات |
| إقصاء | واجهة تفترض إتقان الإنجليزية للتصحيح |

## بطاقة نظام (System Card) — تمرين إلزامي
قبل أي كود إنتاج، املأ:
- الغرض والجمهور
- فئات البيانات (هل تشمل بيانات شخصية؟)
- هل القرار آلي ويؤثر على حقوق؟
- مسار اعتراض بشري؟
- ماذا يحدث عند فشل النموذج؟

## قائمة تحقق سريعة
- [ ] مستوى خطر موثّق وموافق عليه
- [ ] مالك المنتج + مالك المخاطر محددان
- [ ] حالات سوء الاستخدام (misuse) مكتوبة
- [ ] قرار: نمضي / نعدّل / نتوقف

## تمرين
اختر منتجاً (مثلاً فرز سير ذاتية، أو شات بنكي). اكتب `SystemCard` وحدّد 5 سيناريوهات فشل في السياق العربي (لهجة، اسم، وثيقة رسمية، كود مخلوط عربي/إنجليزي، محتوى ديني حساس).
""" + res([
        ("docs", "NIST AI Risk Management Framework", "https://www.nist.gov/itl/ai-risk-management-framework"),
        ("paper", "On the Dangers of Stochastic Parrots (Bender et al.)", "https://dl.acm.org/doi/10.1145/3442188.3445922"),
        ("blog", "Google — Responsible AI practices", "https://ai.google/responsibility/responsible-ai-practices/"),
        ("docs", "OECD AI Principles", "https://oecd.ai/en/ai-principles"),
        ("video", "NIST — AI Risk Management Framework overview", "https://www.nist.gov/video/nist-ai-rmf-overview"),
        ("podcast", "Data & Society — technology, society & AI", "https://listen.datasociety.net/"),
    ])

    m2 = """# المشهد التنظيمي العالمي والإقليمي (مستوى مفاهيمي)

## تنويه مهم
المحتوى **مبسّط وعالي المستوى** لأغراض هندسية وتوعوية. القوانين تتغيّر؛ لا تعتمد على هذه الدورة كاستشارة قانونية أو كخريطة امتثال نهائية. راجع النصوص الرسمية والمستشار القانوني لشركتك.

## لماذا يتابع المهندس التنظيم؟
لأن المتطلبات تتحول إلى: توثيق، سجلات، حدود استخدام، تقييمات أثر، وإمكانية إشراف بشري — أي **تذاكر هندسية** وليست فقط سياسات PDF.

## الاتحاد الأوروبي — مفاهيم قانون الذكاء الاصطناعي (AI Act) باختصار
الاتجاه العام: **تصنيف حسب المخاطر** مع واجبات أثقل على الأنظمة عالية المخاطر، وقيود/حظر على ممارسات معيّنة، ومتطلبات شفافية لفئات أخرى.

مفاهيم عملية للفريق:
1. **Risk-based approach**: ليس كل نموذج يُعامل سواء.
2. **High-risk systems**: غالباً ما تتطلب إدارة مخاطر، بيانات بجودة مناسبة، تسجيل/توثيق، مراقبة بعد السوق (حسب التصنيف والاستخدام).
3. **Transparency**: إعلام المستخدم عند التفاعل مع ذكاء اصطناعي في حالات محددة.
4. **Governance roles**: من المزود؟ من الناشر؟ من المستخدم المهني؟ (تعاريف قانونية — راجع النص).

**ماذا يفعل المهندس الآن؟**
- احتفظ بـ model cards + data sheets
- اربط الإصدار المنشور بهوية واضحة
- لا تُخفي أن الواجهة آلية إذا كان الإفصاح مطلوباً في سياقك

## مبادئ إقليمية عربية (عالي المستوى — ليست نقلاً حرفياً للمواد)
### الإمارات
اتجاهات منشورة حول حوكمة واستخدام أخلاقي للذكاء الاصطناعي تشدد عادة على: **الشفافية، المساءلة، العدالة، الأمان، والخصوصية** ضمن أجندات وطنية للذكاء الاصطناعي. التفاصيل التنفيذية تختلف حسب الجهة والقطاع.

### السعودية
أطر ومبادئ وطنية للذكاء الاصطناعي (عبر جهات مختصة) تركز مفاهيمياً على **استخدام مسؤول، موثوقية، عدالة، ومواءمة مع الأولويات الوطنية**. التطبيق على شركتك يعتمد على قطاعك (مالي، صحي، حكومي…) والتنظيم القطاعي.

### قاسم مشترك هندسي
| مبدأ | ترجمة تقنية |
|------|-------------|
| المساءلة | مالك نموذج + سجل قرارات |
| الشفافية | إفصاح للمستخدم + توثيق قدرات/حدود |
| العدالة | قياسات تحيّز + تمثيل بيانات |
| الخصوصية | تقليل بيانات، إخفاء هوية، صلاحيات |
| الأمان | اختبارات خصومية + مراقبة |

## خصوصية البيانات (طبقة ملازمة)
حتى بلا «قانون AI» مستقل، قوانين حماية البيانات الشخصية في عدة دول عربية وخليجية تفرض أساساً: أساس معالجة، حقوق فرد، أمن، وإخطارات. للمهندس:
- لا تدرّب على بيانات عملاء بلا سند
- افصل البيئات
- راقب التسريب عبر prompts/logs

```python
# سجل قرار حوكمة — الحد الأدنى
import json, time
from pathlib import Path

def log_governance_event(event: dict, path="audit/gov_events.jsonl"):
    event = {**event, "ts": time.time()}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\\n")

log_governance_event({
    "system": "loan-assist-ar",
    "action": "risk_classified",
    "risk": "high",
    "actor": "product_owner@example.com",
})
```

## خريطة واجبات الفريق (عملية لا قانونية)

| دور | يسلّم |
|-----|--------|
| Product | غرض النظام + حدود الاستخدام |
| Data | مصدر البيانات + تراخيص + PII |
| ML | مقاييس أداء وعدالة + قيود |
| Eng | سجلات، صلاحيات، إفصاح واجهة |
| Legal/Compliance | تفسير الالتزام في ولايتك |

## تمرين
اكتب جدولاً: متطلب مفاهيمي (شفافية / بشري في الحلقة / توثيق) → تذكرة Jira هندسية → دليل تحقق. لا تكتب «نمتثل للقانون» بلا آلية.
""" + res([
        ("docs", "EU AI Act — official overview (European Commission)", "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai"),
        ("docs", "UAE AI strategies & ethics materials (overview hub)", "https://ai.gov.ae/"),
        ("docs", "SDAIA — Saudi Data & AI Authority", "https://sdaia.gov.sa/"),
        ("blog", "IAPP — AI governance resources", "https://iapp.org/"),
        ("paper", "Regulating AI: challenges and perspectives (survey literature)", "https://arxiv.org/abs/2301.11616"),
        ("video", "The EU AI Act explained (European Parliament)", "https://www.europarl.europa.eu/news/en/headlines/society/20230601STO93804/eu-ai-act-first-regulation-on-artificial-intelligence"),
        ("podcast", "Data & Society — technology, society & AI", "https://listen.datasociety.net/"),
    ])

    m3 = """# عدالة البيانات وتدقيق تمثيل اللهجات

## المشكلة
مؤشر accuracy الإجمالي قد يبدو ممتازاً بينما اللهجة المغاربية أو الأسماء المركبة أو العربية المخلوطة بالإنجليزية تفشل صامتاً. **العدالة هنا = قياس الشرائح لا الاكتفاء بالمتوسط**.

## أبعاد تدقيق مقترحة للمنتجات العربية
1. **اللهجة / المنطقة**
2. **الفصحى مقابل العامية**
3. **طول النص والتشكيل**
4. **كود-سويتشينغ** (عربي+English)
5. **الجنس/الاسم** إن كان القرار يمس أفراداً (بحذر قانوني وأخلاقي)
6. **جودة OCR** للنصوص المصوّرة

## تدقيق توازن التسميات (Labels)

```python
from collections import Counter
from typing import Dict, Iterable

def distribution(labels: Iterable[str]) -> Dict[str, float]:
    c = Counter(labels)
    total = sum(c.values()) or 1
    return {k: round(v / total, 4) for k, v in sorted(c.items())}

def assert_min_share(dist: Dict[str, float], key: str, min_share: float = 0.1):
    share = dist.get(key, 0.0)
    assert share >= min_share, f"{key} under-represented: {share} < {min_share}"
```

## مقاييس أداء شرائحية

```python
from sklearn.metrics import f1_score
import pandas as pd

def slice_report(df: pd.DataFrame, label_col="y", pred_col="yhat", slice_col="dialect"):
    rows = []
    for name, g in df.groupby(slice_col):
        rows.append({
            "slice": name,
            "n": len(g),
            "f1": f1_score(g[label_col], g[pred_col], average="weighted"),
        })
    return pd.DataFrame(rows).sort_values("f1")
```

## فجوات بين الشرائح (Gap)

```python
def max_min_gap(slice_f1: dict[str, float]) -> float:
    vals = list(slice_f1.values())
    return max(vals) - min(vals)

# سياسة داخلية مثال: ارفض الإطلاق إن الفجوة > 0.1
def fairness_gate(slice_f1: dict[str, float], max_gap: float = 0.1) -> bool:
    if min(slice_f1.values()) < 0.7:
        return False
    return max_min_gap(slice_f1) <= max_gap
```

## تدقيق تمثيل اللهجات في بيانات التدريب

```python
# مثال: عمود dialect من وسم بشري أو مصنّف لهجات
required_dialects = ["gulf", "egyptian", "levantine", "maghrebi", "msa"]

def dialect_coverage(df, col="dialect") -> dict:
    counts = df[col].value_counts(normalize=True).to_dict()
    missing = [d for d in required_dialects if counts.get(d, 0) < 0.05]
    return {"shares": counts, "below_5pct": missing}
```

## تخفيف عملي (ليست وصفة سحرية)
- اجمع عينات مستهدفة للشرائح الضعيفة (مع موافقة وترخيص)
- أعد وزن الخسارة / oversample بحذر من الإفراط
- أضف أمثلة قليلة (few-shot) أو محولات لهجة في طبقة الخدمة
- وفّر مساراً بشرياً عندما confidence منخفضة على شريحة ضعيفة
- وثّق حدود اللغة في بطاقة النموذج

## قائمة تدقيق بيانات قبل التدريب
- [ ] مصادر البيانات وتراخيصها
- [ ] وجود PII؟ خطة إزالة/إخفاء
- [ ] توزيع اللهجات والمناطق
- [ ] معدل الضوضاء في الوسوم
- [ ] اختبار شرائحي في التقييم لا فقط overall
- [ ] مجموعة اختبار «صعبة عربية» ثابتة (code-switch، أخطاء إملائية شائعة)

## تمرين
أنشئ `eval_ar_hard.jsonl` بـ 40 جملة: 8 لكل لهجة تقريبية + 8 code-switch. قِس النموذج الحالي. اكتب فجوة max-min وخطة جمع بيانات لأضعف شريحة.
""" + res([
        ("paper", "Language (Technology) is Power: A Critical Survey of Fairness (Blodgett et al.)", "https://aclanthology.org/2020.acl-main.485/"),
        ("paper", "The Arabic Natural Language Processing resources survey literature", "https://arxiv.org/abs/1805.08928"),
        ("docs", "Hugging Face — Evaluate / fairness discussions", "https://huggingface.co/docs/evaluate/index"),
        ("blog", "Measuring fairness in ML systems", "https://developers.google.com/machine-learning/crash-course/fairness/video-lecture"),
        ("video", "Google — Fairness in Machine Learning (crash course)", "https://developers.google.com/machine-learning/crash-course/fairness/video-lecture"),
        ("podcast", "Data & Society — technology, society & AI", "https://listen.datasociety.net/"),
    ])

    m4 = """# قابلية التفسير (مستوى SHAP) وسجلات التدقيق

## لماذا التفسير؟
في القرارات عالية الأثر يسأل أصحاب المصلحة: **لماذا رُفض؟** وفي الحوادث يسأل المدقق: **أي إصدار؟ بأي مدخل؟** التفسير التقني + سجل التدقيق يكملان بعضهما: الأول يشرح المساهمات، والثاني يُثبّت الوقائع.

## مستويات التفسير
| مستوى | الأداة الذهنية |
|-------|----------------|
| عام | بطاقة نموذج: قدرات وحدود |
| محلي | لماذا هذا القرار؟ (SHAP/LIME) |
| عالمي | أي الميزات أهم عموماً؟ |
| إجرائي | من اعتمد؟ متى تغيّر الإصدار؟ |

## SHAP — المفهوم لا السحر
SHAP يقرّب مساهمة كل ميزة في انحراف التنبؤ عن خط أساس. مفيد للنماذج الجدولية؛ للنصوص يُستخدم بحذر (tokens/features مشتقة).

```python
# مفهومي — يتطلب نموذجاً جدولاً وبيانات خلفية
import shap

# explainer = shap.Explainer(model.predict, background_X)
# sv = explainer(X_sample)
# shap.plots.waterfall(sv[0])

def top_contributors(feature_names, shap_values_row, k=5):
    pairs = sorted(
        zip(feature_names, shap_values_row),
        key=lambda t: abs(t[1]),
        reverse=True,
    )
    return pairs[:k]
```

## تفسير للنماذج اللغوية (حدود صريحة)
- «أبرز الجمل المسترجعة» في RAG أفضل من ادّعاء SHAP دقيق على كل token دائماً
- اعرض **مصادر** و**ثقة** بدل تفسير مزيف
- سجّل prompt_version + model_name + temperature

```python
def rag_trace(query: str, retrieved: list[dict], answer: str) -> dict:
    return {
        "query": query,
        "sources": [
            {"id": d.get("id"), "score": d.get("score"), "snippet": d.get("text", "")[:200]}
            for d in retrieved
        ],
        "answer_hash": str(hash(answer)),
    }
```

## سجل تدقيق (Audit Log) — حد أدنى إنتاجي

```python
import hashlib
import json
import time
from pathlib import Path

def _hash(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def write_audit(
    *,
    actor: str,
    action: str,
    model_version: str,
    request: dict,
    response: dict,
    path: str = "audit/decisions.jsonl",
):
    # لا تسجّل أسراراً خاماً — اخفِ الحقول الحساسة قبل الاستدعاء
    rec = {
        "ts": time.time(),
        "actor": actor,
        "action": action,
        "model_version": model_version,
        "request_hash": _hash(request),
        "response_hash": _hash(response),
        "request_redacted": request,
        "response_redacted": response,
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\\n")
```

## سياسة إخفاء قبل التسجيل
- أرقام هوية/جواز → `[ID]`
- جوال → آخر 4 فقط إن لزم
- محتوى صحي خام → مراجع داخلية لا نص كامل إن أمكن

## قائمة تحقق قابلية المساءلة
- [ ] model_version في كل استجابة API
- [ ] ربط القرار بـ request_id
- [ ] احتفاظ بالسجلات حسب سياسة الاحتفاظ
- [ ] مسار استئناف بشري موثّق للقرارات عالية الأثر
- [ ] أمثلة تفسير تُراجع دورياً (هل تضلّل؟)

## تمرين
لأحد نماذجك الجدولية: ولّد top-5 مساهمات لثلاث عينات (قبول/رفض/حدّي). اكتب فقرة للمستخدم النهائي بلغة غير تقنية. قارن: هل التفسير صادق أم تجميلي؟
""" + res([
        ("docs", "SHAP documentation", "https://shap.readthedocs.io/"),
        ("paper", "A Unified Approach to Interpreting Model Predictions (Lundberg & Lee)", "https://arxiv.org/abs/1705.07874"),
        ("docs", "Model Cards for Model Reporting", "https://arxiv.org/abs/1810.03993"),
        ("blog", "Google — Model Cards", "https://modelcards.withgoogle.com/about"),
        ("video", "SHAP author — explaining model predictions", "https://www.youtube.com/watch?v=VB9uV-x0gtg"),
        ("podcast", "Data & Society — technology, society & AI", "https://listen.datasociety.net/"),
    ])

    m5 = """# بوابة امتثال داخل MLOps (مراجعة بشرية + بوابات مقاييس)

## الهدف
لا يصل نموذج إلى Production لأنه «تحسّن 0.5% accuracy» فقط. يجب أن يمر عبر **Compliance Gate**: مقاييس أداء + عدالة شرائحية + وثائق + موافقة بشرية عند الخطر العالي.

## موقع البوابة في الخط
`train → evaluate → fairness slices → docs check → human approval (high) → registry Production → monitor`

## تنفيذ بوابة مقاييس

```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class GateConfig:
    min_f1: float = 0.80
    min_auc: float = 0.85
    max_fairness_gap: float = 0.10
    min_slice_f1: float = 0.70
    require_human_for_high_risk: bool = True

@dataclass
class GateResult:
    ok: bool
    reasons: list

def compliance_gate(
    metrics: Dict[str, float],
    slice_f1: Dict[str, float],
    risk: str,
    human_approved: bool,
    cfg: GateConfig = GateConfig(),
) -> GateResult:
    reasons = []
    if metrics.get("f1", 0) < cfg.min_f1:
        reasons.append("f1_below_min")
    if metrics.get("auc", 0) < cfg.min_auc:
        reasons.append("auc_below_min")
    if slice_f1:
        gap = max(slice_f1.values()) - min(slice_f1.values())
        if gap > cfg.max_fairness_gap:
            reasons.append(f"fairness_gap={gap:.3f}")
        if min(slice_f1.values()) < cfg.min_slice_f1:
            reasons.append("slice_f1_below_min")
    if risk == "high" and cfg.require_human_for_high_risk and not human_approved:
        reasons.append("human_approval_missing")
    return GateResult(ok=not reasons, reasons=reasons)
```

## مراجعة بشرية (Human Review) — ليست خانة اختيار فارغة

```python
def record_human_review(
    reviewer: str,
    model_version: str,
    checklist: dict,
    decision: str,
    notes: str,
) -> dict:
    required = ["data_license_ok", "eval_reviewed", "redteam_smoke_ok", "rollback_plan"]
    missing = [k for k in required if not checklist.get(k)]
    if missing and decision == "approve":
        raise ValueError(f"cannot approve, missing {missing}")
    return {
        "reviewer": reviewer,
        "model_version": model_version,
        "decision": decision,
        "checklist": checklist,
        "notes": notes,
    }
```

## دمج في CI (يفشل البناء)

```python
# ci_gate.py
import json
from pathlib import Path

metrics = json.loads(Path("artifacts/metrics.json").read_text())
slices = json.loads(Path("artifacts/slice_f1.json").read_text())
meta = json.loads(Path("artifacts/release_meta.json").read_text())
human = Path("artifacts/HUMAN_APPROVED").exists()

result = compliance_gate(
    metrics, slices, risk=meta.get("risk", "limited"), human_approved=human
)
Path("artifacts/gate_result.json").write_text(
    json.dumps(result.__dict__, ensure_ascii=False, indent=2), encoding="utf-8"
)
if not result.ok:
    raise SystemExit("COMPLIANCE_GATE_FAIL: " + ", ".join(result.reasons))
print("COMPLIANCE_GATE_OK")
```

## ما بعد الإنتاج: الحوكمة لا تنتهي
- مراقبة أداء شرائحي أسبوعياً
- إعادة تقييم عند تغيّر البيانات أو الغرض
- Rollback سريع لـ champion السابق
- تحديث بطاقة النموذج عند كل ترقية

## قائمة إطلاق Responsible AI
- [ ] System card + مستوى الخطر
- [ ] مقاييس overall + slices
- [ ] بوابة CI مفعّلة
- [ ] موافقة بشرية إن لزم
- [ ] audit log + model_version
- [ ] إفصاح للمستخدم عند الحاجة
- [ ] خطة حادث (هلوسة ضارة، تمييز، تسريب)

## مشروع تخرج الدورة
اختر نظاماً عالي المخاطر محاكى (مثل ترتيب مرشحين). نفّذ: بيانات شرائح وهمية، `compliance_gate`، ملف موافقة، ورفض متعمد عند فجوة لهجات. اكتب runbook صفحة واحدة لفريقك بالعربية.
""" + res([
        ("docs", "NIST AI RMF — Govern / Map / Measure / Manage", "https://www.nist.gov/itl/ai-risk-management-framework"),
        ("paper", "Model Cards for Model Reporting", "https://arxiv.org/abs/1810.03993"),
        ("docs", "Datasheets for Datasets", "https://arxiv.org/abs/1803.09010"),
        ("blog", "MLOps meets Responsible AI", "https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning"),
        ("video", "Microsoft — Responsible AI dashboard walkthrough", "https://www.youtube.com/watch?v=f1oaG7Qb-vc"),
        ("podcast", "Data & Society — technology, society & AI", "https://listen.datasociety.net/"),
    ])

    return {
        "title": "حوكمة الذكاء الاصطناعي والأخلاقيات في العالم العربي",
        "description": "دورة تطبيقية للمهندسين وصنّاع القرار: تصنيف مخاطر، وعي تنظيمي عالمي/إقليمي عالي المستوى، تدقيق عدالة واللهجات العربية، تفسير وسجلات تدقيق، وبوابة امتثال داخل MLOps — بمحتوى عملي وليس شعارات. (ليست استشارة قانونية.)",
        "tags": ["AI Governance", "Ethics", "Compliance", "Responsible AI", "Fairness", "Arabic NLP"],
        "price": 49,
        "duration": "5 ساعات",
        "gradient": "from-cyan-500 to-blue-500",
        "modules": [
            {"title": "الوحدة 1: تصنيف المخاطر والسياق العربي", "content": m1},
            {"title": "الوحدة 2: المشهد التنظيمي العالمي والإقليمي", "content": m2},
            {"title": "الوحدة 3: عدالة البيانات وتمثيل اللهجات", "content": m3},
            {"title": "الوحدة 4: قابلية التفسير وسجلات التدقيق", "content": m4},
            {"title": "الوحدة 5: بوابة امتثال MLOps ومراجعة بشرية", "content": m5},
        ],
    }
