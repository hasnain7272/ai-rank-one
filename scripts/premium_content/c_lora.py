# -*- coding: utf-8 -*-
from _res import res


def course():
    m1 = """# الضبط الكامل مقابل LoRA/QLoRA — الحدس الرياضي ومتى تضبط النموذج

## ماذا ستبني في هذه الدورة؟
مساراً هندسياً لـ **Fine-tuning** عملي: متى تضبط ومتى يكفي RAG/البرومبت، حدس LoRA وQLoRA، إعداد PEFT (rank/alpha/target modules)، تجهيز البيانات وحلقة التدريب، مشروع محوّل نطاق (domain adapter)، ثم الدمج والتصدير والتقييم والتكلفة.

هذه ليست «شغّل notebook وانسَ». الهدف: **قرارات إنتاج** + كود transformers/peft أسلوب حقيقي.

## متى لا تحتاج Fine-tuning؟
| الحاجة | الأنسب غالباً |
|--------|----------------|
| معرفة حديثة / مستندات خاصة | RAG |
| تنسيق إخراج بسيط | برومبت + few-shot / JSON schema |
| أسلوب أو اصطلاحات نطاق ثابتة | LoRA/QLoRA |
| سلوك أداة معقّد + بيانات وفيرة | SFT (+ تفضيلات لاحقاً) |
| تغيير قدرات أساسية للنموذج | Full FT أو نموذج أكبر — نادر ومكلف |

**قاعدة ذهبية:** إن كانت المشكلة «لا يجد المعلومة» → RAG أولاً. إن كانت «يعرف لكن لا يتكلم بلسان نطاقك» → adapter.

## Full Fine-Tuning: ماذا يتغيّر؟
لكل طبقة خطية تقريباً لدينا أوزان `W` بحجم ضخم. التحديث الكامل:

```
W' = W + ΔW
```

حيث `ΔW` بنفس رتبة `W` تقريباً → ذاكرة مُحسِّن (Adam states) ضخمة، تخزين نسخة كاملة لكل تجربة، وخطر **نسيان كارثي** لما تعلّمه النموذج الأساس.

## LoRA: تحديث منخفض الرتبة
الفرضية: التحديث المفيد أثناء التكييف يعيش في فضاء منخفض الرتبة. بدلاً من تعلّم `ΔW` كاملة:

```
ΔW ≈ B @ A
```

- `A` شكلها `(r, in)` و `B` شكلها `(out, r)` و **r << min(in, out)**
- عدد المعاملات ≈ `r * (in + out)` بدل `in * out`
- أثناء الاستدلال يمكن **دمج** `W + BA` فلا تكلفة إضافية للlatency بعد الدمج

```python
# حدس عددي — ليس تدريب حقيقي
import numpy as np

rng = np.random.default_rng(0)
in_f, out_f, r = 4096, 4096, 16
# عدد عناصر ΔW الكاملة
full = in_f * out_f
# LoRA
lora = r * (in_f + out_f)
print("full params", full)
print("lora params", lora)
print("ratio", round(lora / full, 6))
# مثال: ~0.0078 → أقل من 1% من معاملات الطبقة
```

### alpha والقياس
غالباً يُضرب التحديث بـ `alpha / r` (أو يُضبط عبر `lora_alpha` في PEFT) ليبقى تأثير الرتبة مستقراً عند تغيير `r`.

```
h = W x + scaling * (B (A x))
```

## QLoRA: LoRA + تكميم 4-bit للأساس
- يُحمَّل النموذج الأساس مكمّماً (مثل NF4) لتوفير VRAM
- تُدرَّب محوّلات LoRA بـ precision أعلى (غالباً BF16/FP16 للحسابات)
- النتيجة: ضبط 7B–70B على بطاقة واحدة أو قليلة — مع حذر من فقدان جودة التكميم

## مقارنة سريعة للقرار

```python
from dataclasses import dataclass


@dataclass
class FtDecision:
    use_rag: bool
    use_lora: bool
    use_full_ft: bool
    reason: str


def decide(need_private_knowledge: bool, need_style_or_format: bool,
           has_labeled_sft: bool, huge_budget: bool) -> FtDecision:
    if need_private_knowledge and not need_style_or_format:
        return FtDecision(True, False, False, "RAG أولاً للمحتوى المتغيّر")
    if need_style_or_format and has_labeled_sft:
        return FtDecision(need_private_knowledge, True, False, "LoRA/QLoRA للنمط + RAG إن لزم")
    if huge_budget and has_labeled_sft and not need_private_knowledge:
        return FtDecision(False, False, True, "Full FT نادر — تجربة كبيرة فقط")
    return FtDecision(True, False, False, "ابدأ برومبت/RAG — اجمع بيانات قبل الضبط")
```

## تكاليف خفية يتجاهلها المبتدئ
1. **جمع وتنظيف البيانات** أغلى من GPU.
2. **تقييم** قبل/بعد على مجموعة ثابتة — وإلا «صار أحلى» وهم.
3. **إصدار المحوّلات** (base model revision + rank + data hash).
4. **الامتثال**: بيانات تدريب قد تحتوي PII.

## قائمة تحقق الوحدة 1
- [ ] كتبت مشكلة منتج بجملة: RAG أم LoRA أم الاثنان؟
- [ ] فهمت أن LoRA ≈ BA منخفضة الرتبة
- [ ] حسبت نسبة المعاملات لطبقة 4096×4096 عند r=8 و r=64
- [ ] عرّفت مقياس نجاح قبل أي `trainer.train()`

## تمرين
اختر حالة عربية (دعم فني، عقود، طب عام تثقيفي). اكتب:
1) 20 مثالاً لـ SFT (input/output)
2) 10 أسئلة تقييم
3) قرار: LoRA فقط / RAG فقط / هجين — مع تبرير سطرين
""" + res([
        ("paper", "LoRA: Low-Rank Adaptation arXiv:2106.09685", "https://arxiv.org/abs/2106.09685"),
        ("paper", "QLoRA arXiv:2305.14314", "https://arxiv.org/abs/2305.14314"),
        ("docs", "Hugging Face PEFT overview", "https://huggingface.co/docs/peft/index"),
        ("blog", "Hugging Face — Parameter-Efficient Fine-Tuning using PEFT", "https://huggingface.co/blog/peft"),
        ("video", "Efficient Fine-Tuning — LoRA & QLoRA (Hugging Face)", "https://www.youtube.com/watch?v=Us5ZFp16PaU"),
        ("podcast", "Latent Space — fine-tuning era", "https://www.latent.space/"),
    ])

    m2 = """# إعداد PEFT/LoRA: target modules والرتبة وalpha

## الهدف
ضبط محوّل LoRA على نموذج Causal LM بأقل معاملات فعّالة، مع اختيار طبقات صحيحة وتوازن rank/alpha وdropout.

## تثبيت متوافق مع أسلوب الإنتاج

```bash
python -m venv .venv
pip install "torch" "transformers>=4.43" "peft>=0.11" "datasets>=2.20" "accelerate>=0.33" "bitsandbytes>=0.43" "trl>=0.9"
# bitsandbytes اختياري لـ QLoRA على CUDA
```

## تحميل النموذج + إعداد LoRA (FP16/BF16)

```python
from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType


BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"  # صغير للتجارب؛ غيّر حسب رخصتك وVRAM


def load_tokenizer(model_id: str = BASE_MODEL):
    tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    return tok


def build_lora_config(
    r: int = 16,
    alpha: int = 32,
    dropout: float = 0.05,
    target_modules: list[str] | None = None,
) -> LoraConfig:
    # شائع في LLaMA/Mistral/Qwen: إسقاطات الانتباه وأحياناً MLP
    if target_modules is None:
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        bias="none",
        target_modules=target_modules,
    )


def load_model_with_lora(model_id: str = BASE_MODEL, lora: LoraConfig | None = None):
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto",
    )
    model.config.use_cache = False  # للتدريب مع gradient checkpointing لاحقاً
    cfg = lora or build_lora_config()
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()
    return model
```

## QLoRA: BitsAndBytesConfig

```python
from transformers import BitsAndBytesConfig
from peft import prepare_model_for_kbit_training


def load_qlora_model(model_id: str = BASE_MODEL, lora: LoraConfig | None = None):
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb,
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)
    cfg = lora or build_lora_config(r=32, alpha=64)
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()
    return model
```

## كيف تختار target_modules؟
1. اطبع أسماء الوحدات: ابحث عن `Linear` داخل `model.named_modules()`.
2. ابدأ بـ attention projections (`q_proj`, `v_proj` كحد أدنى؛ غالباً الأربعة).
3. أضف `gate_proj` / `up_proj` / `down_proj` إن احتجت تكييف معرفة أسلوبية أعمق (VRAM أعلى قليلاً).
4. لا تستهدف كل شيء «احتياطاً» — راقب trainable% ومقاييس التقييم.

```python
def list_linear_suffixes(model, limit: int = 40) -> list[str]:
    names = []
    for name, mod in model.named_modules():
        if mod.__class__.__name__ in ("Linear", "Linear4bit", "Conv1D"):
            names.append(name)
    # أظهر آخر جزء من الاسم لتخمين target_modules
    suffixes = sorted({n.split(".")[-1] for n in names})
    return suffixes[:limit]
```

## rank و alpha — دليل عملي
| إعداد | متى |
|-------|-----|
| r=8, alpha=16 | أسلوب خفيف، بيانات قليلة |
| r=16, alpha=32 | نقطة بداية جيدة |
| r=64, alpha=128 | مهمة صعبة + بيانات أوفر + VRAM |
| dropout 0.05–0.1 | قلل الحفظ الحرفي للبيانات الصغيرة |

**ملاحظة:** رفع r بلا بيانات = overfitting أغلى. قِس دائماً على hold-out.

## أخطاء شائعة في الإعداد
- نسيان `pad_token` → أخطاء collator أو تحذيرات صامتة
- `use_cache=True` مع checkpointing → تعارض
- target_modules لا تطابق أسماء النموذج (Qwen vs LLaMA)
- خلط basemodel مختلف عند تحميل adapter لاحقاً

## تمرين
1. حمّل نموذجاً صغيراً واطبع `print_trainable_parameters()`.
2. قارن trainable% عند target=attention فقط vs attention+MLP.
3. ثبّت alpha = 2*r وجرّب r ∈ {8,16,32} على 50 خطوة — راقب loss فقط كإشارة أولية.
""" + res([
        ("docs", "PEFT LoRA guide", "https://huggingface.co/docs/peft/package_reference/lora"),
        ("docs", "Transformers quantization (bitsandbytes)", "https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes"),
        ("blog", "Hugging Face: Efficient Training on a Single GPU", "https://huggingface.co/docs/transformers/perf_train_gpu_one"),
        ("paper", "The Power of Scale for Parameter-Efficient Prompt Tuning arXiv:2104.08691", "https://arxiv.org/abs/2104.08691"),
        ("video", "QLoRA — fine-tuning LLMs on a single GPU", "https://www.youtube.com/watch?v=y9PHWGOa8HA"),
        ("podcast", "Latent Space — fine-tuning era", "https://www.latent.space/"),
    ])

    m3 = """# تجهيز البيانات وحلقة التدريب وإخفاقات شائعة

## شكل بيانات SFT pro-production
أفضل صيغة للInstruct: محادثة متعددة الأدوار أو `instruction / input / output` تُحوَّل لقالب الدردشة الخاص بالنموذج.

```python
from __future__ import annotations

from datasets import Dataset


RAW = [
    {
        "messages": [
            {"role": "system", "content": "أنت مساعد سياسات موارد بشرية. أجب بدقة واختصار."},
            {"role": "user", "content": "كم يوم إجازة سنوية للموظف الجديد؟"},
            {"role": "assistant", "content": "حسب السياسة الداخلية: 21 يوماً في السنة الأولى، تُحسب تناسباً بعد قضاء 3 أشهر."},
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "أنت مساعد سياسات موارد بشرية. أجب بدقة واختصار."},
            {"role": "user", "content": "هل تُرحَّل الإجازة للسنة التالية؟"},
            {"role": "assistant", "content": "يُسمح بترحيل حتى 5 أيام فقط بموافقة المدير، وتسقط بقية الأيام غير المستخدمة."},
        ]
    },
]


def assert_sft_quality(rows: list[dict]) -> None:
    assert len(rows) >= 1
    for i, row in enumerate(rows):
        msgs = row["messages"]
        assert msgs[-1]["role"] == "assistant", "آخر رسالة يجب أن تكون الإجابة"
        assert len(msgs[-1]["content"].strip()) > 0
        # تجنّب تسرّب تعليمات التدريب في user فقط بلا system موحّد إن لزم
        if i == 0:
            roles = [m["role"] for m in msgs]
            assert "user" in roles and "assistant" in roles
```

### تحويل لقالب الدردشة ثم توكنة

```python
def render_and_tokenize(tokenizer, rows: list[dict], max_len: int = 1024) -> Dataset:
    texts = []
    for row in rows:
        text = tokenizer.apply_chat_template(
            row["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )
        texts.append(text)

    def _tok(batch):
        out = tokenizer(
            batch["text"],
            max_length=max_len,
            truncation=True,
            padding=False,
        )
        out["labels"] = [ids[:] for ids in out["input_ids"]]
        return out

    ds = Dataset.from_dict({"text": texts})
    ds = ds.map(_tok, batched=True, remove_columns=["text"])
    return ds
```

**تحسين متقدم (مهم للجودة):** قنّع خسارة التوكنات الخاصة بـ user/system (loss on assistant only) عبر collator مخصص أو TRL `DataCollatorForCompletionOnlyLM`. بدون ذلك قد يحفظ النموذج صياغة الأسئلة أكثر من الأجوبة.

## حلقة تدريب بأسلوب transformers + peft

```python
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling


def train_lora(model, tokenizer, train_ds, eval_ds=None, out_dir: str = "out/lora-hr"):
    args = TrainingArguments(
        output_dir=out_dir,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch" if eval_ds is not None else "no",
        bf16=True,
        fp16=False,
        gradient_checkpointing=True,
        report_to=[],
        optim="adamw_torch",
    )
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
    )
    trainer.train()
    trainer.save_model(out_dir)
    tokenizer.save_pretrained(out_dir)
    return out_dir
```

### بديل TRL SFTTrainer (شائع في الإنتاج السريع)

```python
# from trl import SFTTrainer, SFTConfig
# trainer = SFTTrainer(model=model, args=sft_config, train_dataset=raw_ds, ...)
# يختصر collator وقوالب الدردشة — راجع توثيق إصدارك
```

## إخفاقات شائعة وحلولها
| عرض | سبب محتمل | علاج |
|-----|-----------|------|
| loss ينهار لـ 0 سريعاً | تسريب labels / بيانات مكررة | راقب عينات؛ قنّع الخسارة؛ زد تنوع البيانات |
| loss لا ينزل | LR صغير جداً أو target modules خاطئة | 1e-4–3e-4 لـ LoRA غالباً؛ تحقق الأسماء |
| نبرة جيدة ومحتوى خاطئ | بيانات ضحلة | ارفع جودة الأجوبة لا حجم الضجيج |
| OOM | batch/تسلسل طويل | grad accumulation، checkpointing، QLoRA، max_len |
| انحدار في المهام العامة | overfitting نطاق ضيق | قلل epochs، زد dropout، اخلط بيانات عامة قليلة |
| مخرجات مقطوعة | max_new_tokens / قالب خاطئ | وحّد chat template بين التدريب والاستدلال |

## صحة البيانات — قائمة لا تتخطّاها
- [ ] إزالة PII أو ترميزها
- [ ] توحيد اللغة والنبرة
- [ ] رفض أجوبة متناقضة لنفس السؤال
- [ ] تقسيم train/val حسب **سؤال** لا صف عشوائي يسرّب التسريب
- [ ] حفظ hash للبيانات مع إصدار المحوّل

## تمرين
1. أنشئ 40 مثالاً يدوياً لنطاقك (أفضل من 4000 صف ضعيف).
2. قسّم 80/20 بحذر.
3. درّب 1 epoch على نموذج صغير — احفظ loss و3 أجوبة qual.
4. وثّق فشلاً واحداً واجهته وكيف أصلحته.
""" + res([
        ("docs", "Transformers Trainer", "https://huggingface.co/docs/transformers/main_classes/trainer"),
        ("docs", "TRL SFTTrainer", "https://huggingface.co/docs/trl/sft_trainer"),
        ("blog", "HF: Fine-tune LLMs with PEFT", "https://huggingface.co/blog/peft"),
        ("paper", "Self-Instruct arXiv:2212.10560", "https://arxiv.org/abs/2212.10560"),
        ("video", "Fine-tuning with TRL SFTTrainer (Hugging Face)", "https://www.youtube.com/watch?v=OQdp-OeG1as"),
        ("podcast", "Latent Space — fine-tuning era", "https://www.latent.space/"),
    ])

    m4 = """# مشروع مصغّر: محوّل نطاق (Domain Adapter) من طرف لطرف

## سيناريو المشروع
تبني **محوّل موارد بشرية عربي** فوق نموذج Instruct صغير:
- مدخلات: أسئلة موظفين
- مخرجات: إجابات قصيرة مستندة لسياسة وهمية ثابتة (في الواقع اربطها لاحقاً بـ RAG)

الهدف التعليمي: خط أنابيب كامل يمكن استبداله بنطاقك (قانوني، دعم SaaS، مبيعات).

## هيكل المجلد

```
hr_adapter/
  data/train.jsonl
  data/val.jsonl
  train_qlora.py
  infer.py
  eval_qual.py
  out/
```

## 1) بيانات JSONL

```python
# كل سطر: كائن messages
# {"messages":[{"role":"system","content":"..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}]}

import json
from pathlib import Path


def write_jsonl(path: str, rows: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\\n")


SYSTEM = "أنت مساعد الموارد البشرية لشركة نموذجية. لا تختلق سياسات. إن جهلت، اطلب تصعيداً للموارد البشرية."


def make_row(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


# أمثلة بذرة — وسّعها إلى 100–500 يدوياً للجودة
SEED_TRAIN = [
    make_row("ما ساعات العمل الرسمية؟", "ساعات العمل من 9 صباحاً إلى 5 مساءً من الأحد إلى الخميس."),
    make_row("كيف أطلب إجازة؟", "قدّم الطلب عبر بوابة HR قبل 5 أيام عمل، مع موافقة المدير المباشر."),
    make_row("هل يوجد عمل عن بُعد؟", "يُسمح بيومين عن بُعد أسبوعياً بعد فترة التجربة وبموافقة المدير."),
]
SEED_VAL = [
    make_row("متى تنتهي فترة التجربة؟", "فترة التجربة 3 أشهر من تاريخ المباشرة ما لم يُنص على خلاف ذلك في العقد."),
]
```

## 2) سكربت تدريب مدمج (QLoRA إن توفر CUDA)

```python
# train_qlora.py — أسلوب إنتاج مختصر
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
import torch

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
OUT = "out/hr-lora"


def main():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    use_cuda = torch.cuda.is_available()
    if use_cuda:
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb, device_map="auto")
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32, device_map="cpu")

    lora = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, lora)

    raw = load_dataset("json", data_files={"train": "data/train.jsonl", "validation": "data/val.jsonl"})

    def to_text(ex):
        text = tok.apply_chat_template(ex["messages"], tokenize=False, add_generation_prompt=False)
        return {"text": text}

    raw = raw.map(to_text)

    def tokenize(batch):
        out = tok(batch["text"], truncation=True, max_length=768)
        out["labels"] = [x[:] for x in out["input_ids"]]
        return out

    ds = raw.map(tokenize, batched=True, remove_columns=raw["train"].column_names)

    args = TrainingArguments(
        output_dir=OUT,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        logging_steps=5,
        save_strategy="epoch",
        eval_strategy="epoch",
        bf16=use_cuda,
        gradient_checkpointing=use_cuda,
        report_to=[],
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        data_collator=DataCollatorForLanguageModeling(tok, mlm=False),
    )
    trainer.train()
    trainer.save_model(OUT)
    tok.save_pretrained(OUT)


if __name__ == "__main__":
    main()
```

## 3) استدلال سريع

```python
# infer.py
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

BASE = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER = "out/hr-lora"

tok = AutoTokenizer.from_pretrained(ADAPTER)
base = AutoModelForCausalLM.from_pretrained(BASE, device_map="auto")
model = PeftModel.from_pretrained(base, ADAPTER)
model.eval()

messages = [
    {"role": "system", "content": "أنت مساعد الموارد البشرية لشركة نموذجية."},
    {"role": "user", "content": "كيف أطلب إجازة؟"},
]
prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tok(prompt, return_tensors="pt").to(model.device)
with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=128, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True))
```

## 4) تقييم كيفي إلزامي
لا تكتفِ بـ loss. جهّز 15 سؤالاً:
- 5 داخل التوزيع (شبيهة بالتدريب)
- 5 إعادة صياغة
- 5 خارج النطاق (يجب أن يرفض أو يُصعّد)

سجّل: صحة، نبرة، هل اختلق سياسة؟

## مخرجات المشروع الناجح
- [ ] `out/hr-lora` يضم adapter weights + tokenizer config
- [ ] جدول مقارنة base vs adapter على 15 سؤالاً
- [ ] قرار مكتوب: هل يكفي LoRA أم نحتاج RAG فوقه؟

## تمرين توسعة
استبدل نطاق HR بدومينك. لا تزد epochs قبل أن تصل ~100 مثال عالي الجودة.
""" + res([
        ("docs", "PEFT loading adapters", "https://huggingface.co/docs/peft/developer_guides/model_merging"),
        ("docs", "Datasets load_dataset json", "https://huggingface.co/docs/datasets/loading"),
        ("blog", "QLoRA blog (HF)", "https://huggingface.co/blog/4bit-transformers-bitsandbytes"),
        ("paper", "Alpaca / instruction following arXiv:2303.16199", "https://arxiv.org/abs/2303.16199"),
        ("video", "End-to-end QLoRA fine-tuning walkthrough", "https://www.youtube.com/watch?v=XpoKB3usmKc"),
        ("podcast", "Latent Space — fine-tuning era", "https://www.latent.space/"),
    ])

    m5 = """# الدمج والتصدير والخدمة والتقييم والتكلفة

## دمج المحوّل مع الأساس (Merge)
بعد الرضا عن الجودة، ادمج LoRA في الأوزان لتقليل تعقيد الخدمة (لا حاجة لتحميل adapter منفصل) — على حساب مرونة «تبديل محوّلات».

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

BASE = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER = "out/hr-lora"
MERGED = "out/hr-merged"

tok = AutoTokenizer.from_pretrained(ADAPTER)
base = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float16, device_map="cpu")
model = PeftModel.from_pretrained(base, ADAPTER)
merged = model.merge_and_unload()
merged.save_pretrained(MERGED, safe_serialization=True)
tok.save_pretrained(MERGED)
```

**تحذير:** لا تدمج فوق نموذج مكمّم 4-bit ثم تفترض أن النتيجة صالحة لكل السيناريوهات دون اختبار. ادمج على دقة أعلى إن أمكن ثم كمّم للخدمة.

## تصدير وخيارات الخدمة
| خيار | ملاءمة |
|------|--------|
| transformers + FastAPI | بسيط، تحكم كامل، أبطأ دون تحسين |
| text-generation-inference / vLLM | إنتاج throughput عالٍ |
| llama.cpp / GGUF | طرفية وحدود موارد |
| محوّلات متعددة بدون دمج | منتج multi-tenant (عميل = adapter) |

## خدمة FastAPI بحد أدنى

```python
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

log = logging.getLogger("lora_svc")
api = FastAPI(title="Domain Adapter API")

MODEL_DIR = "out/hr-merged"  # أو الأساس + PeftModel
tok = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, device_map="auto")
model.eval()


class GenIn(BaseModel):
    user: str = Field(..., min_length=1, max_length=4000)
    system: str = Field("أنت مساعد مهني دقيق.")
    max_new_tokens: int = Field(256, ge=16, le=1024)


class GenOut(BaseModel):
    text: str
    latency_ms: int


@api.post("/v1/generate", response_model=GenOut)
def generate(body: GenIn):
    t0 = time.perf_counter()
    messages = [
        {"role": "system", "content": body.system},
        {"role": "user", "content": body.user},
    ]
    try:
        prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=body.max_new_tokens, do_sample=False)
        text = tok.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    except Exception:
        log.exception("gen_fail")
        raise HTTPException(status_code=500, detail="generation_error")
    ms = int((time.perf_counter() - t0) * 1000)
    log.info("ok ms=%s chars=%s", ms, len(text))
    return GenOut(text=text, latency_ms=ms)
```

## تقييم ما بعد النشر
1. **مجموعة ذهبية ثابتة** (لا تدرّب عليها): دقة وقائعية + نبرة.
2. **انحدار عام**: 20 سؤالاً عاماً — هل انهار النموذج؟
3. **أمان**: محاولات استخراج بيانات تدريب / سياسات سرية.
4. **A/B**: base vs adapter على نفس البرومبت.

```python
def exact_policy_score(pairs: list[tuple[str, str]], generate_fn) -> float:
    \"\"\"pairs: (question, must_contain_substring)\"\"\"
    if not pairs:
        return 0.0
    hits = 0
    for q, needle in pairs:
        ans = generate_fn(q)
        if needle in ans:
            hits += 1
    return hits / len(pairs)
```

## نموذج تكلفة تقريبي

```python
def estimate_cost(
    n_tokens_train: int,
    gpu_hour_price: float,
    hours: float,
    storage_gb: float,
    storage_price_per_gb_month: float,
) -> dict:
    train = hours * gpu_hour_price
    store = storage_gb * storage_price_per_gb_month
    return {
        "train_usd": round(train, 2),
        "storage_month_usd": round(store, 2),
        "tokens_seen": n_tokens_train,
        "note": "أضف تكلفة التسمية البشرية — غالباً الأكبر",
    }
```

قارن دائماً مع: **GPT API + RAG**. أحياناً LoRA أرخص عند حجم استعلامات ضخم ونمط ثابت؛ وأحياناً العكس.

## قائمة إطلاق الإنتاج
- [ ] إصدار: base commit + adapter hash + data hash + hyperparams
- [ ] اختبار merge على نفس مجموعة التقييم
- [ ] حد معدل + timeout + max_new_tokens
- [ ] لا تسجّل نصوص مستخدم حساسة بلا سياسة
- [ ] خطة rollback للنموذج السابق
- [ ] مراقبة: latency p95، أخطاء CUDA OOM، نسبة رفض
- [ ] وثّق الترخيص التجاري للنموذج الأساس

## مشروع تخرج الدورة
Adapter لنطاقك + تقرير صفحة: مقاييس قبل/بعد، تكلفة تدريب تقريبية، قرار الدمج من عدمه، وهل يبقى RAG ضرورياً.

> Fine-tuning الناجح ليس loss منخفضاً — بل **سلوك ثابت** يمر تقييمك ويتحمّل تكلفة التشغيل.
""" + res([
        ("docs", "PEFT merge_and_unload", "https://huggingface.co/docs/peft/developer_guides/model_merging"),
        ("docs", "vLLM documentation", "https://docs.vllm.ai/"),
        ("blog", "Hugging Face: deploying LLMs", "https://huggingface.co/docs/text-generation-inference/index"),
        ("paper", "Holistic Evaluation of Language Models arXiv:2211.09110", "https://arxiv.org/abs/2211.09110"),
        ("video", "vLLM — fast LLM serving (with LoRA adapters)", "https://www.youtube.com/watch?v=5ZlavKF_98U"),
        ("podcast", "Practical AI — deploying models", "https://changelog.com/practicalai"),
    ])

    return {
        "title": "ضبط نماذج اللغة الدقيقة مع LoRA وQLoRA للإنتاج",
        "description": "دورة هندسية مدفوعة: قرار Full FT مقابل LoRA/QLoRA، إعداد PEFT (rank/alpha/target modules)، بيانات SFT وحلقة transformers، مشروع محوّل نطاق عربي، ثم الدمج والتصدير والخدمة والتقييم وحساب التكلفة.",
        "tags": ["LoRA", "QLoRA", "PEFT", "Fine-tuning", "Transformers", "LLM", "Production"],
        "price": 39,
        "duration": "10 ساعات",
        "gradient": "from-violet-500 to-purple-500",
        "modules": [
            {"title": "الوحدة 1: Full FT مقابل LoRA/QLoRA ومتى تضبط النموذج", "content": m1},
            {"title": "الوحدة 2: إعداد PEFT/LoRA والـ target modules والرتبة", "content": m2},
            {"title": "الوحدة 3: تجهيز البيانات وحلقة التدريب والإخفاقات", "content": m3},
            {"title": "الوحدة 4: مشروع محوّل نطاق (Domain Adapter) متكامل", "content": m4},
            {"title": "الوحدة 5: الدمج والتصدير والخدمة والتقييم والتكلفة", "content": m5},
        ],
    }
