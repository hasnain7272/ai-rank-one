# -*- coding: utf-8 -*-
from _res import res


def course():
    m1 = """# الفجوة بين دفتر الملاحظات والإنتاج

## ماذا ستبني في هذه الدورة؟
نظام **MLOps** كامل: من سكربت تدريب قابل لإعادة الإنتاج، إلى تتبّع تجارب، CI/CD، خدمة FastAPI/Docker، ومراقبة انجراف تُشغّل إعادة تدريب. الهدف ليس «نموذج بدقة عالية في Notebook» بل **منتج يُشغَّل ويُراقَب ويُباع**.

## لماذا يفشل 80٪ من النماذج بعد التجربة؟
| سبب | في Notebook | في الإنتاج |
|-----|-------------|------------|
| البيانات | CSV ثابت محلي | تدفق حي + مخطط يتغيّر |
| البيئة | حزم عشوائية | صورة Docker + أقفال إصدارات |
| الإصدار | «آخر خلية شغّالة» | Git + hash بيانات + model version |
| التقييم | accuracy مرة واحدة | بوابة مقاييس + shadow deploy |
| المراقبة | لا شيء | latency + drift + business KPIs |

## ركائز MLOps (احفظها)
1. **Version everything**: كود + بيانات + بيئة + نموذج.
2. **Reproduce**: أي تشغيل قديم يمكن إعادته بنفس النتائج تقريباً.
3. **Automate**: تدريب/تقييم/نشر عبر خطوط أنابيب.
4. **Observe**: مقاييس تقنية + عمل + تنبيهات.
5. **Govern**: من وافق على النشر؟ أي إصدار في الإنتاج؟

## أول خطوة هندسية: أخرج التدريب من Jupyter

```python
# train.py — سكربت مستقل، لا يعتمد على حالة الخلايا
from pathlib import Path
import json
import hashlib
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report

DATA = Path("data/train.csv")
OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)

def data_fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]

def main():
    df = pd.read_csv(DATA)
    y = df.pop("label")
    X = df
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=200, max_depth=12, random_state=42, n_jobs=-1
    )
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    f1 = float(f1_score(y_te, pred, average="weighted"))
    meta = {
        "f1_weighted": f1,
        "data_sha": data_fingerprint(DATA),
        "n_train": len(X_tr),
        "n_test": len(X_te),
        "features": list(X.columns),
    }
    joblib.dump(model, OUT / "model.joblib")
    (OUT / "metrics.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(classification_report(y_te, pred))
    print("metrics:", meta)
    if f1 < 0.75:
        raise SystemExit("GATE_FAIL: F1 below threshold")

if __name__ == "__main__":
    main()
```

## متطلبات.txt وأقفال البيئة
لا تقل «يعمل عندي». ثبّت:

```text
# requirements.txt (مثال)
scikit-learn==1.5.2
pandas==2.2.3
joblib==1.4.2
mlflow==2.17.2
fastapi==0.115.0
uvicorn==0.32.0
```

وللتطوير استخدم `pip freeze > requirements.lock` أو Poetry/uv.

## هيكل مشروع إنتاجي مقترح
```
ml-service/
  data/           # لا ترفع بيانات حساسة — استخدم DVC/S3
  src/
    features.py
    train.py
    evaluate.py
    serve.py
  tests/
  artifacts/      # models + metrics (gitignore أو registry)
  Dockerfile
  .github/workflows/
```

## قائمة تحقق — هل خرجت من وضع «تجربة»؟
- [ ] `python train.py` يعمل من جذر المشروع بلا Jupyter
- [ ] metrics تُحفظ كملف JSON قابل للمقارنة
- [ ] بصمة بيانات (hash) مربوطة بالنموذج
- [ ] عتبة جودة تفشل التشغيل إن انخفض الأداء
- [ ] README يشرح أمر التدريب والتقييم فقط

## تمرين مدفوع القيمة
حوّل آخر Notebook لديك إلى `train.py` + `evaluate.py`. شغّل مرتين بنفس البذرة: يجب أن تطابق المقاييس تقريباً. إن اختلفت جوهرياً — ابحث عن عشوائية غير مضبوطة (shuffle, GPU nondeterminism, تسريب بيانات).

## أخطاء مكلفة
- تسريب من test إلى train عبر feature engineering في الدفتر
- حفظ pickle لنموذج مرتبط بمسارات مطلقة على جهازك
- عدم فصل preprocessing عن inference → اختلاف توزيع عند الخدمة
""" + res([
        ("docs", "Google — MLOps: Continuous delivery and automation", "https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning"),
        ("paper", "Hidden Technical Debt in Machine Learning Systems (Sculley et al.)", "https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems"),
        ("blog", "Made With ML — MLOps guide", "https://madewithml.com/"),
        ("video", "Full Stack Deep Learning — MLOps lectures", "https://fullstackdeeplearning.com/"),
        ("podcast", "Practical AI — ML in production episodes", "https://changelog.com/practicalai"),
    ])

    m2 = """# تتبّع التجارب وسجل النماذج (Experiment Tracking + Model Registry)

## المشكلة
بعد 30 تجربة: «أي hyperparameters أعطت أفضل F1؟ وأي ملف بيانات؟ وأي commit؟» بدون MLflow-style tracking أنت تخمّن.

## مفاهيم يجب أن تميّزها
| مفهوم | المعنى |
|-------|--------|
| Experiment | مشروع/مشكلة (مثلاً churn-v2) |
| Run | تشغيل تدريب واحد بمعاملات ومقاييس |
| Artifact | ملفات (نموذج، plots، تقارير) |
| Model Registry | كتالوج إصدارات + مراحل (Staging/Production) |
| Alias/Stage | أي إصدار «حي» في الخدمة |

## MLflow Tracking — الحد الأدنى الإنتاجي

```python
# train_tracked.py
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score, roc_auc_score

mlflow.set_tracking_uri("http://127.0.0.1:5000")  # أو file:./mlruns
mlflow.set_experiment("churn-prediction")

params = {
    "n_estimators": 300,
    "learning_rate": 0.05,
    "max_depth": 3,
}

with mlflow.start_run(run_name="gbm-baseline") as run:
    mlflow.log_params(params)
    mlflow.set_tags({
        "data_sha": "a1b2c3d4",
        "git_commit": "deadbeef",
        "owner": "ml-team",
    })
    model = GradientBoostingClassifier(**params)
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_valid)[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "f1": float(f1_score(y_valid, pred)),
        "auc": float(roc_auc_score(y_valid, proba)),
    }
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="churn-clf",  # يدخل الـ Registry
    )
    print("run_id:", run.info.run_id, metrics)
```

تشغيل الواجهة:

```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

## تسجيل مرحلة الإنتاج (Promotion)

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
# مثال: ترقية الإصدار 3 إلى Production بعد مراجعة
client.transition_model_version_stage(
    name="churn-clf",
    version=3,
    stage="Production",
    archive_existing_versions=True,
)

# أو aliases (أحدث MLflow):
# client.set_registered_model_alias("churn-clf", "champion", "3")
```

## ماذا تسجّل دائماً؟ (Checklist)
- [ ] hyperparameters الأساسية
- [ ] مقاييس validation **و** test (منفصلة)
- [ ] data_sha / dataset version
- [ ] git commit hash
- [ ] feature list / schema
- [ ] زمن التدريب + حجم العينة
- [ ] عتبة القرار (threshold) إن كانت جزءًا من المنتج

## مقارنة التجارب برمجياً

```python
import mlflow
from mlflow.entities import ViewType

runs = mlflow.search_runs(
    experiment_names=["churn-prediction"],
    filter_string="metrics.f1 > 0.80",
    order_by=["metrics.auc DESC"],
    max_results=10,
    run_view_type=ViewType.ACTIVE_ONLY,
)
print(runs[["run_id", "metrics.f1", "metrics.auc", "params.learning_rate"]])
```

## Anti-patterns
- Run بلا tags: لا تعرف من درّب ماذا
- تسجيل train accuracy فقط: خداع ذاتي
- Registry بدون gate: أي شخص يضع Production
- تخزين أسرار (API keys) داخل artifacts

## تمرين
1. شغّل 5 runs بمعاملات مختلفة.
2. اختر الأفضل بـ AUC مع قيد F1 ≥ عتبة.
3. سجّله Staging ثم Production يدوياً بعد مراجعة `metrics.json`.
4. حمّل النموذج بـ URI: `models:/churn-clf/Production`.
""" + res([
        ("docs", "MLflow Tracking documentation", "https://mlflow.org/docs/latest/tracking.html"),
        ("docs", "MLflow Model Registry", "https://mlflow.org/docs/latest/model-registry.html"),
        ("blog", "Neptune.ai — experiment tracking comparison", "https://neptune.ai/blog/ml-experiment-tracking"),
        ("paper", "Towards ML Engineering (Meta/FB engineering culture paper trail)", "https://arxiv.org/abs/1212.5701"),
        ("video", "MLflow — experiment tracking & model registry", "https://www.youtube.com/watch?v=6ngxBkx05Fs"),
        ("podcast", "Practical AI — ML in production episodes", "https://changelog.com/practicalai"),
    ])

    m3 = """# CI/CD لتدريب وتقييم النماذج

## الفكرة
كل push يمسّ `src/**` أو `data/**` (أو جدول مجدول) يطلق: اختبار وحدات → تدريب/تقييم على عينة → بوابة مقاييس → تسجيل artifacts. النشر للإنتاج **مشروط** بنجاح البوابة — لا «merge وأمل».

## طبقات الفحص (لا تخلطها)
1. **Unit tests**: preprocessing، مخطط الأعمدة، حدود القيم.
2. **Training job**: قد يكون على runner GPU أو workflow منفصل ثقيل.
3. **Eval gate**: قارن بالمتخطّي (champion) — لا تنشر إن خسرت.
4. **Smoke serve**: ارفع الحاوية واستدعِ `/health` و`/predict` بعينة.

## GitHub Actions — تدريب خفيف + بوابة

```yaml
# .github/workflows/train-eval.yml
name: train-eval
on:
  push:
    branches: [main]
    paths: ['src/**', 'data/**', 'requirements.txt']
  workflow_dispatch:

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
      - name: Install
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
      - name: Unit tests
        run: pytest -q tests/
      - name: Train + evaluate
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python src/train.py --config configs/ci.yaml
          python src/evaluate.py --min-f1 0.78 --min-auc 0.82
      - name: Upload metrics
        uses: actions/upload-artifact@v4
        with:
          name: metrics
          path: artifacts/metrics.json
```

## evaluate.py — بوابة صريحة

```python
# src/evaluate.py
import argparse
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--min-f1", type=float, required=True)
    p.add_argument("--min-auc", type=float, required=True)
    p.add_argument("--champion-metrics", default="artifacts/champion_metrics.json")
    args = p.parse_args()

    model = joblib.load("artifacts/model.joblib")
    df = pd.read_csv("data/valid.csv")
    y = df.pop("label")
    proba = model.predict_proba(df)[:, 1]
    pred = (proba >= 0.5).astype(int)
    f1 = float(f1_score(y, pred, average="weighted"))
    auc = float(roc_auc_score(y, proba))
    metrics = {"f1": f1, "auc": auc}
    Path("artifacts/metrics.json").write_text(json.dumps(metrics, indent=2))

    if f1 < args.min_f1 or auc < args.min_auc:
        raise SystemExit(f"GATE_FAIL absolute: {metrics}")

    champ_path = Path(args.champion_metrics)
    if champ_path.exists():
        champ = json.loads(champ_path.read_text())
        # لا تنشر إن خسرت الـ champion بأكثر من هامش صغير
        if auc + 1e-6 < float(champ.get("auc", 0)):
            raise SystemExit(f"GATE_FAIL vs champion: {metrics} < {champ}")

    print("GATE_OK", metrics)

if __name__ == "__main__":
    main()
```

## استراتيجيات إطلاق (بعد نجاح CI)
| استراتيجية | متى |
|------------|-----|
| Replace مباشر | نماذج منخفضة المخاطر |
| Shadow | النموذج الجديد يرى الحركة دون التأثير |
| Canary % | تدريجياً 5% → 25% → 100% |
| A/B | قياس KPI عمل (تحويل، شكاوى) |

## اختبارات بيانات (Data tests) — لا تهملها

```python
# tests/test_schema.py
import pandas as pd

REQUIRED = {"age", "tenure", "monthly_charges", "label"}

def test_columns_present():
    df = pd.read_csv("data/valid.csv")
    missing = REQUIRED - set(df.columns)
    assert not missing, missing

def test_no_all_null_features():
    df = pd.read_csv("data/valid.csv")
    null_ratio = df.drop(columns=["label"]).isna().mean()
    assert (null_ratio < 0.3).all(), null_ratio.to_dict()
```

## تمرين
أضف workflow يفشل إن نقص عمود أو انخفض F1. اربط badge في README. اكتب في PR template: «metrics الجديدة vs champion».

## قائمة تحقق CI/CD ML
- [ ] اختبارات وحدات للـ features
- [ ] بذرة عشوائية ثابتة في CI
- [ ] أسرار عبر secrets لا في YAML
- [ ] artifacts محفوظة لكل run
- [ ] فشل واضح برسالة GATE_FAIL
- [ ] لا GPU إلزامي لكل PR — افصل heavy train
""" + res([
        ("docs", "GitHub Actions — workflow syntax", "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions"),
        ("blog", "Continuous Delivery for Machine Learning (CD4ML) — Thoughtworks", "https://www.thoughtworks.com/insights/articles/intelligent-enterprise-series-cd4ml"),
        ("paper", "Software Engineering for Machine Learning: A Case Study (Microsoft)", "https://ieeexplore.ieee.org/document/8804457"),
        ("video", "CI/CD for machine learning with GitHub Actions", "https://www.youtube.com/watch?v=9BgIDqAzfuA"),
        ("podcast", "Software Engineering Daily — ML infrastructure", "https://softwareengineeringdaily.com/"),
    ])

    m4 = """# خدمة النموذج: FastAPI + Docker

## الهدف
تحويل artifact مسجّل إلى **HTTP API** بزمن استجابة معروف، صحة (`/health`)، مخطط طلب/رد صارم، وجاهزية للحاويات.

## لماذا FastAPI؟
- تحقق Pydantic من المدخلات (يرفض schema خاطئ مبكراً)
- توثيق OpenAPI تلقائي (`/docs`)
- أداء async مناسب I/O؛ للاستدلال الثقيل استخدم batch/worker

## serve.py إنتاجي مبسّط

```python
# src/serve.py
from __future__ import annotations
import os
import time
import logging
from typing import List
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("model-serve")

MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")
FEATURE_ORDER = os.getenv(
    "FEATURE_ORDER", "age,tenure,monthly_charges"
).split(",")

app = FastAPI(title="Churn Model API", version="1.0.0")
_model = None

class PredictIn(BaseModel):
    features: dict = Field(..., description="خريطة اسم_ميزة → قيمة")
    request_id: str | None = None

    @field_validator("features")
    @classmethod
    def non_empty(cls, v: dict) -> dict:
        if not v:
            raise ValueError("features empty")
        return v

class PredictOut(BaseModel):
    prediction: int
    probability: float
    model_version: str
    latency_ms: int

@app.on_event("startup")
def load_model():
    global _model
    _model = joblib.load(MODEL_PATH)
    log.info("loaded model from %s", MODEL_PATH)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model is not None}

def vectorize(features: dict) -> np.ndarray:
    missing = [c for c in FEATURE_ORDER if c not in features]
    if missing:
        raise HTTPException(400, f"missing features: {missing}")
    return np.array([[float(features[c]) for c in FEATURE_ORDER]])

@app.post("/v1/predict", response_model=PredictOut)
def predict(body: PredictIn):
    if _model is None:
        raise HTTPException(503, "model not loaded")
    t0 = time.time()
    X = vectorize(body.features)
    try:
        proba = float(_model.predict_proba(X)[0, 1])
    except Exception:
        log.exception("infer_fail rid=%s", body.request_id)
        raise HTTPException(500, "inference_error")
    pred = int(proba >= 0.5)
    ms = int((time.time() - t0) * 1000)
    log.info("ok rid=%s pred=%s p=%.4f ms=%s", body.request_id, pred, proba, ms)
    return PredictOut(
        prediction=pred,
        probability=proba,
        model_version=os.getenv("MODEL_VERSION", "local"),
        latency_ms=ms,
    )
```

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY artifacts/model.joblib ./artifacts/model.joblib
ENV MODEL_PATH=/app/artifacts/model.joblib
ENV MODEL_VERSION=1.0.0
ENV FEATURE_ORDER=age,tenure,monthly_charges
EXPOSE 8000
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t churn-api:1.0.0 .
docker run --rm -p 8000:8000 churn-api:1.0.0
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/v1/predict \\
  -H "Content-Type: application/json" \\
  -d '{"features":{"age":42,"tenure":12,"monthly_charges":70.5},"request_id":"t1"}'
```

## ممارسات خدمة لا تتخطّاها
- **نفس preprocessing** في التدريب والخدمة (شارك وحدة `features.py`)
- حدود حجم الطلب + timeout
- لا تُرجع stack traces للمستخدم
- `MODEL_VERSION` من Registry/CI
- جاهزية: `/health` يفحص تحميل النموذج لا مجرد «العملية حيّة»

## تحميل من MLflow مباشرة (اختياري)

```python
import mlflow.pyfunc
model = mlflow.pyfunc.load_model("models:/churn-clf/Production")
# pred = model.predict(pdf)
```

## تمرين
انشر محلياً بـ Docker، أرسل 100 طلباً متتابعاً، احسب p50/p95 للـ latency. أضف اختبار تكامل في CI يبني الصورة ويستدعي `/health`.
""" + res([
        ("docs", "FastAPI deployment", "https://fastapi.tiangolo.com/deployment/"),
        ("docs", "MLflow Models — pyfunc", "https://mlflow.org/docs/latest/models.html"),
        ("blog", "Docker best practices for Python", "https://docs.docker.com/language/python/"),
        ("paper", "Machine Learning Model Serving: a survey (arXiv)", "https://arxiv.org/abs/2011.09926"),
        ("video", "Serving ML models with FastAPI + Docker", "https://www.youtube.com/watch?v=h5wLuVDr0oc"),
        ("podcast", "Kubernetes Podcast / cloud-native serving episodes", "https://kubernetespodcast.com/"),
    ])

    m5 = """# مراقبة الانجراف ومحفّزات إعادة التدريب

## الحقيقة بعد الإطلاق
الدقة في يوم النشر **ليست** ضماناً بعد 30 يوماً. يتغيّر سلوك المستخدم، الموسمية، تعريفات المنتج، وحتى أعمدة ناقصة من المصدر. MLOps الناضج = **detect → alert → retrain/review → redeploy**.

## أنواع الانجراف
| نوع | السؤال | إشارة |
|-----|--------|-------|
| Data drift | هل تغيّر توزيع X؟ | KS, PSI, distance على الميزات |
| Concept drift | هل تغيّرت علاقة X→y؟ | انخفاض أداء عند توفّر labels |
| Prediction drift | هل تغيّر توزيع ŷ؟ | انزياح متوسط الاحتمال |
| Performance | هل KPI انهار؟ | F1/AUC على نافذة حديثة |
| Ops | هل الخدمة مريضة؟ | latency, 5xx, queue depth |

## PSI (Population Stability Index) — عملي

```python
import numpy as np

def psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    # PSI تقريبي: >0.2 غالباً يستدعي تحقيقاً (عتبات حسب المجال).
    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(reference, quantiles))
    if len(edges) < 3:
        return 0.0
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    ref_perc = ref_counts / max(ref_counts.sum(), 1)
    cur_perc = cur_counts / max(cur_counts.sum(), 1)
    # تجنّب أصفار
    ref_perc = np.clip(ref_perc, 1e-6, None)
    cur_perc = np.clip(cur_perc, 1e-6, None)
    return float(np.sum((cur_perc - ref_perc) * np.log(cur_perc / ref_perc)))
```

## KS test للميزة العددية

```python
from scipy.stats import ks_2samp

def feature_drift(ref, cur, p_threshold=0.01) -> bool:
    stat, p = ks_2samp(ref, cur)
    return bool(p < p_threshold)
```

## خط مراقبة يومي (سكربت + Cron / Airflow)

```python
# monitor.py
import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path("monitoring")
ref = pd.read_parquet(BASE / "reference.parquet")
live = pd.read_parquet(BASE / "live_yesterday.parquet")

report = {"features": {}, "alerts": []}
for col in ["age", "tenure", "monthly_charges"]:
    score = psi(ref[col].to_numpy(), live[col].to_numpy())
    report["features"][col] = {"psi": score}
    if score > 0.2:
        report["alerts"].append(f"PSI high on {col}: {score:.3f}")

# انجراف تنبؤ إن وُجدت احتمالات محفوظة
if "proba" in live.columns and "proba" in ref.columns:
    delta = float(live["proba"].mean() - ref["proba"].mean())
    report["pred_mean_delta"] = delta
    if abs(delta) > 0.05:
        report["alerts"].append(f"prediction mean shift {delta:.3f}")

Path("artifacts/drift_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
if report["alerts"]:
    # في الإنتاج: PagerDuty / Slack webhook
    raise SystemExit("DRIFT_ALERT: " + "; ".join(report["alerts"]))
print("drift ok", report)
```

## متى تعيد التدريب؟ (سياسة واضحة)
لا «كل أسبوع لأننا نستطيع». اربط محفّزاً:

1. **أداء**: labels متأخرة متاحة وانخفض AUC تحت عتبة لمدة N أيام.
2. **انجراف بيانات**: PSI > عتبة على ميزات حرجة + موافقة بشرية.
3. **تغيير منتج**: عمود جديد، شريحة مستخدمين جديدة.
4. **أمني/امتثال**: نموذج قديم بلا توثيق.

```python
def should_retrain(perf_auc: float, psi_max: float, days_since: int) -> str:
    if perf_auc < 0.80:
        return "retrain_now_performance"
    if psi_max > 0.25 and days_since >= 7:
        return "retrain_review_drift"
    if days_since >= 90:
        return "scheduled_refresh"
    return "hold"
```

## حلقة الإغلاق
`monitor` يفشل → workflow `retrain` → `evaluate` vs champion → Staging → مراجعة بشرية → Production → تحديث reference dataset.

## قائمة مراقبة أسبوع أول بعد الإطلاق
- [ ] لوحة: QPS, p95 latency, error rate
- [ ] توزيع prediction يومياً
- [ ] PSI لأهم 5 ميزات
- [ ] عيّنة مراجعة بشرية للأخطاء
- [ ] تنبيه Slack عند DRIFT_ALERT
- [ ] runbook: من يستدعى؟ كيف rollback؟

## مشروع تخرج الدورة
1. `train.py` + MLflow run  
2. CI gate  
3. Docker API  
4. `monitor.py` على بيانات مرجعية vs «حية» اصطناعية بمحاكاة انجراف  
5. وثّق في صفحة واحدة: عتباتك ولماذا
""" + res([
        ("docs", "Evidently AI — data drift docs", "https://docs.evidentlyai.com/"),
        ("paper", "Dataset Shift in Machine Learning (overview literature)", "https://arxiv.org/abs/2004.06493"),
        ("blog", "Why ML models degrade in production", "https://www.nannyml.com/blog"),
        ("video", "Monitoring ML models & data drift with Evidently", "https://www.youtube.com/watch?v=L4Pv6ExBQPM"),
        ("podcast", "TWIML AI — MLOps & monitoring", "https://twimlai.com/podcast/twimlai/"),
    ])

    return {
        "title": "هندسة التعلّم الآلي للإنتاج (MLOps) من التجربة إلى الإنتاج",
        "description": "دورة هندسية مدفوعة: حوّل نماذجك من Jupyter إلى نظام إنتاجي — تتبّع تجارب MLflow، بوابات CI/CD، خدمة FastAPI/Docker، ومراقبة انجراف مع محفّزات إعادة تدريب. للكود العربي والفرق التي تبيع ML كمنتج.",
        "tags": ["MLOps", "CI/CD", "Model Registry", "Monitoring", "FastAPI", "Docker"],
        "price": 49,
        "duration": "6 ساعات",
        "gradient": "from-rose-500 to-orange-500",
        "modules": [
            {"title": "الوحدة 1: الفجوة بين دفتر الملاحظات والإنتاج", "content": m1},
            {"title": "الوحدة 2: تتبّع التجارب وسجل النماذج", "content": m2},
            {"title": "الوحدة 3: CI/CD لتدريب وتقييم النماذج", "content": m3},
            {"title": "الوحدة 4: خدمة النموذج FastAPI وDocker", "content": m4},
            {"title": "الوحدة 5: مراقبة الانجراف ومحفّزات إعادة التدريب", "content": m5},
        ],
    }
