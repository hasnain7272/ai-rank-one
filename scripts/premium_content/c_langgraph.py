# -*- coding: utf-8 -*-
from _res import res


def course():
    m1 = """# المفاهيم الأساسية وهندسة الوكلاء

## ماذا ستبني في هذه الدورة؟
نظام **وكلاء متعددين** يتعاونون: باحث يجمع معلومات، مبرمج يكتب كوداً، مراجع يتحقق — عبر **LangGraph** برسم بياني واضح قابل للتتبع.

هذه ليست دورة «شات مع GPT». الهدف: **هندسة أنظمة** تُشغَّل وتُباع.

## لماذا Multi-Agent وليس نموذجاً واحداً؟
| معيار | نموذج واحد | وكلاء متخصصون |
|--------|------------|----------------|
| التخصص | برومبت ضخم هش | كل وكيل يبرع في دور |
| التصحيح | صندوق أسود | تتبّع عقدة بعقدة |
| التكلفة | سياق طويل دائماً | سياق مختصر لكل دور |
| الأمان | كل الأدوات متاحة | أدوات محدودة لكل وكيل |

## LangGraph في جملة
- **State**: حالة مشتركة (رسائل، نتائج، أعلام)
- **Nodes**: دوال بايثون = وكلاء أو خطوات
- **Edges**: انتقالات ثابتة أو شرطية

```
        ┌────────────┐
 START →│ researcher │──→ coder ──→ reviewer ──→ END
        └────────────┘         ↑         │
              └────────────────┘ (إعادة عند الرفض)
```

## إعداد بيئة احترافية

```bash
python -m venv .venv
pip install "langgraph>=0.2" "langchain-openai>=0.2" "langchain-core>=0.3"
```

## الحالة المشتركة — أساس كل شيء

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    research_notes: str
    code_draft: str
    review_ok: bool
    iteration: int
```

`add_messages` يمنع استبدال السجل بالكامل في كل خطوة.

## مبادئ تصميم قبل كتابة سطر
1. مسؤولية واحدة لكل عقدة
2. مخرج واضح في الـ State
3. شرط توقف صريح (حد حلقات)
4. أدوات بأقل صلاحية

## تمرين
عرّف `AgentState` محلياً. حدّد 3 أدوار لوكلاء من مشكلة في عملك قبل الوحدة 2.
""" + res([
        ("docs", "LangGraph Concepts", "https://langchain-ai.github.io/langgraph/concepts/low_level/"),
        ("blog", "LangGraph multi-agent workflows", "https://blog.langchain.dev/langgraph-multi-agent-workflows/"),
        ("paper", "AutoGen (Microsoft) arXiv:2308.08155", "https://arxiv.org/abs/2308.08155"),
        ("video", "LangChain — Introduction to LangGraph", "https://www.youtube.com/watch?v=5h-JBkySK34"),
        ("podcast", "Latent Space — agents", "https://www.latent.space/"),
    ])

    m2 = """# بناء الرسم البياني وهيكلة العقد

## الهدف
رسم: researcher → coder → reviewer مع حلقة إعادة و**حد أمان** للحلقات.

```python
from typing import Literal
from langgraph.graph import StateGraph, START, END

def researcher(state: AgentState) -> dict:
    notes = f"ملاحظات حول: {state['task']}"
    return {
        "research_notes": notes,
        "messages": [("assistant", f"[researcher] {notes}")],
        "iteration": state.get("iteration", 0) + 1,
    }

def coder(state: AgentState) -> dict:
    draft = f"# {state['task']}\\ndef solve():\\n    return 42\\n"
    return {"code_draft": draft, "messages": [("assistant", "[coder] مسودة")]}

def reviewer(state: AgentState) -> dict:
    ok = "def solve" in state.get("code_draft", "")
    return {"review_ok": ok, "messages": [("assistant", "[reviewer] " + ("قبول" if ok else "رفض"))]}

def route(state: AgentState) -> Literal["researcher", "__end__"]:
    if state.get("review_ok") or state.get("iteration", 0) >= 3:
        return "__end__"
    return "researcher"

g = StateGraph(AgentState)
g.add_node("researcher", researcher)
g.add_node("coder", coder)
g.add_node("reviewer", reviewer)
g.add_edge(START, "researcher")
g.add_edge("researcher", "coder")
g.add_edge("coder", "reviewer")
g.add_conditional_edges("reviewer", route, {"researcher": "researcher", "__end__": END})
app = g.compile()
```

## أنماط شائعة
1. Pipeline A→B→C  
2. Supervisor يوزّع المهام  
3. Map-Reduce  
4. Reflection (مولّد + ناقد)

## نمط المشرف (Supervisor) — توجيه ديناميكي
في الأنظمة الأكبر لا تثبّت المسار A→B→C. دع **مشرفاً** يقرر أي وكيل يعمل تالياً بناءً على الحالة.

```python
from typing import Literal

def supervisor(state: AgentState) -> dict:
    # في الإنتاج: استدعِ LLM ليختار الوكيل التالي أو FINISH.
    if not state.get("research_notes"):
        nxt = "researcher"
    elif not state.get("code_draft"):
        nxt = "coder"
    elif not state.get("review_ok"):
        nxt = "reviewer"
    else:
        nxt = "FINISH"
    return {"next": nxt}

def route_supervisor(state: AgentState) -> Literal["researcher", "coder", "reviewer", "__end__"]:
    nxt = state.get("next", "FINISH")
    return END if nxt == "FINISH" or state.get("iteration", 0) >= 6 else nxt

sg = StateGraph(AgentState)
sg.add_node("supervisor", supervisor)
for w in ("researcher", "coder", "reviewer"):
    sg.add_node(w, globals()[w])
    sg.add_edge(w, "supervisor")  # كل عامل يعود للمشرف
sg.add_edge(START, "supervisor")
sg.add_conditional_edges("supervisor", route_supervisor,
    {"researcher": "researcher", "coder": "coder", "reviewer": "reviewer", "__end__": END})
supervised = sg.compile()
```

**متى تختار أي نمط؟**
| النمط | الأنسب | المخاطر |
|-------|--------|---------|
| Pipeline ثابت | مهام متسلسلة متوقعة | جمود أمام الحالات الشاذة |
| Supervisor | توجيه مرن حسب الحالة | تكلفة LLM لكل قرار |
| Map-Reduce | مهام متوازية مستقلة | تجميع النتائج معقّد |

## أخطاء مكلفة
- نسيان حد الحلقات → فاتورة API  
- عقدة واحدة عملاقة → صندوق أسود  
- عدم تسجيل messages → تصحيح مستحيل
- مشرف بلا شرط FINISH واضح → حلقة لا نهائية

## تمرين
حوّل تذكرة دعم (تلخيص → رد → مراجعة نبرة) إلى 3 عقد، ثم أعد بناءها بنمط المشرف وقارن عدد استدعاءات LLM.
""" + res([
        ("docs", "Multi-agent collaboration tutorial", "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/"),
        ("blog", "Anthropic: Building effective agents", "https://www.anthropic.com/research/building-effective-agents"),
        ("paper", "ReAct arXiv:2210.03629", "https://arxiv.org/abs/2210.03629"),
        ("video", "DeepLearning.AI agent courses", "https://www.deeplearning.ai/"),
        ("podcast", "Practical AI podcast", "https://changelog.com/practicalai"),
    ])

    m3 = """# الذاكرة المستمرة وتبادل الرسائل

## المشكلة
بدون checkpointer كل طلب يبدأ من الصفر — تجربة سيئة وتكلفة إعادة سياق.

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = g.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "user-42-session-1"}}

app.invoke({
    "task": "اكتب دالة تحقق بريد",
    "messages": [], "iteration": 0,
    "research_notes": "", "code_draft": "", "review_ok": False,
}, config)
```

**قاعدة إنتاج:** `thread_id` = جلسة مستخدم واحدة. لا تخلط المستخدمين.

## أنواع الذاكرة
| نوع | الاستخدام |
|-----|-----------|
| Short-term (state) | خطوات الرسم الحالية |
| Thread | جلسة متعددة الرسائل |
| Long-term | تفضيلات عبر الجلسات (DB/Vector) |

للإنتاج استخدم checkpointer على Postgres/SQLite بدل MemorySaver فقط.

## checkpointer إنتاجي على Postgres
`MemorySaver` يضيع كل شيء عند إعادة تشغيل الخادم. للإنتاج ثبّت الحالة في قاعدة بيانات.

```python
# pip install "langgraph-checkpoint-postgres>=1.0" psycopg
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:pass@localhost:5432/agents?sslmode=disable"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # ينشئ الجداول أول مرة فقط
    app = g.compile(checkpointer=checkpointer)
    cfg = {"configurable": {"thread_id": "user-42-session-1"}}
    app.invoke({"task": "...", "messages": [], "iteration": 0,
                "research_notes": "", "code_draft": "", "review_ok": False}, cfg)

    # استعادة أحدث نقطة حفظ لنفس الجلسة (مثلاً بعد إعادة تشغيل)
    snapshot = app.get_state(cfg)
    print("آخر تكرار محفوظ:", snapshot.values.get("iteration"))
```

**قائمة تحقق للذاكرة الإنتاجية:**
- [ ] `thread_id` مشتق من هوية المستخدم الموثّقة (لا من المدخلات)
- [ ] سياسة انتهاء صلاحية/أرشفة للجلسات القديمة
- [ ] عدم تخزين أسرار أو PII خام في الحالة
- [ ] نسخ احتياطي لقاعدة نقاط الحفظ

## تمرين
استدعاءان بنفس thread_id وآخر مختلف — قارن السلوك واكتب متى تحتاج ذاكرة طويلة المدى.
""" + res([
        ("docs", "LangGraph persistence", "https://langchain-ai.github.io/langgraph/concepts/persistence/"),
        ("blog", "Memory for agents", "https://blog.langchain.dev/memory-for-agents/"),
        ("paper", "Generative Agents arXiv:2304.03442", "https://arxiv.org/abs/2304.03442"),
        ("video", "LangGraph — persistence & memory", "https://www.youtube.com/watch?v=hE8C2M8GRLo"),
        ("podcast", "TWIML AI Podcast", "https://twimlai.com/podcast/twimlai/"),
    ])

    m4 = """# دمج الأدوات (Tools) وحلقات التكرار

القيمة التجارية تظهر عندما يستدعي الوكيل أدوات حقيقية.

```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def search_docs(query: str) -> str:
    \"\"\"بحث في قاعدة معرفة داخلية.\"\"\"
    kb = {
        "auth": "JWT + انتهاء 15 دقيقة + refresh",
        "rag": "Hybrid BM25+dense ثم RRF ثم rerank",
    }
    for k, v in kb.items():
        if k in query.lower():
            return v
    return "لا نتيجة — اطلب توضيحاً"

@tool
def run_tests(snippet: str) -> str:
    \"\"\"محاكاة اختبارات.\"\"\"
    return "PASS" if "def " in snippet else "FAIL"

tools = [search_docs, run_tests]
tool_node = ToolNode(tools)
```

## حلقة ReAct داخل الرسم
وكيل يقرر → أداة تُنفَّذ → نتيجة تعود → حتى END أو حد أقصى.

## أمان (إلزامي إن بِعت منتجاً)
- لا eval بلا sandbox
- rate limit لكل thread_id
- سجّل كل tool call (من، ماذا، المدة)

## مشروع الوحدة
وكيل DevOps: سؤال → search_docs → إجابة → run_tests إن وُجد كود.
""" + res([
        ("docs", "LangChain Tools", "https://python.langchain.com/docs/concepts/tools/"),
        ("paper", "Toolformer arXiv:2302.04761", "https://arxiv.org/abs/2302.04761"),
        ("blog", "OpenAI function calling", "https://platform.openai.com/docs/guides/function-calling"),
        ("video", "LangChain — tool calling with agents", "https://www.youtube.com/watch?v=zCwuAlpQKTM"),
        ("podcast", "Latent Space tool use", "https://www.latent.space/"),
    ])

    m5 = """# النشر والمراقبة في الإنتاج

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time, logging

log = logging.getLogger("agents")
api = FastAPI(title="Multi-Agent API")

class ChatIn(BaseModel):
    session: str = Field(..., min_length=3)
    task: str = Field(..., min_length=3)

@api.post("/v1/agent")
def run_agent(body: ChatIn):
    t0 = time.time()
    cfg = {"configurable": {"thread_id": body.session}}
    try:
        out = app.invoke({
            "task": body.task, "messages": [], "iteration": 0,
            "research_notes": "", "code_draft": "", "review_ok": False,
        }, cfg)
    except Exception as e:
        log.exception("fail")
        raise HTTPException(500, "agent_error") from e
    ms = int((time.time() - t0) * 1000)
    log.info("ok session=%s ms=%s", body.session, ms)
    return {"code": out.get("code_draft"), "review_ok": out.get("review_ok"), "latency_ms": ms}
```

## قائمة إطلاق
- [ ] حد حلقات + timeout
- [ ] Checkpointer إنتاج + نسخ احتياطي
- [ ] أسرار في secret manager
- [ ] مقاييس: latency, tokens, tool errors, loops
- [ ] تنبيهات فشل
- [ ] لا تسجّل بيانات حساسة خاماً

## مشروع تخرج
Docker + 10 طلبات متزامنة + تقرير صفحة: اختناقات ومراقبة الأسبوع الأول.
""" + res([
        ("docs", "LangGraph how-tos", "https://langchain-ai.github.io/langgraph/how-tos/"),
        ("blog", "OpenTelemetry blog", "https://opentelemetry.io/blog/"),
        ("paper", "LLM evaluation reliability arXiv:2404.12272", "https://arxiv.org/abs/2404.12272"),
        ("video", "Deploying LangGraph apps to production", "https://www.youtube.com/watch?v=pfAQxBS5z8o"),
        ("podcast", "Software Engineering Daily", "https://softwareengineeringdaily.com/"),
    ])

    return {
        "title": "بناء أنظمة الوكلاء المتعددة (Multi-Agents) باستخدام LangGraph",
        "description": "دورة هندسية: وكلاء متخصصون، ذاكرة جلسات، أدوات آمنة، ونشر قابل للمراقبة — بكود بايثون جاهز للإنتاج وللسوق العربي.",
        "tags": ["LangGraph", "Python", "Multi-Agent", "LLM Orchestration", "Production"],
        "price": 39,
        "duration": "8 ساعات",
        "gradient": "from-brand-500 to-indigo-500",
        "modules": [
            {"title": "الوحدة 1: المفاهيم الأساسية وهندسة الوكلاء", "content": m1},
            {"title": "الوحدة 2: بناء الرسم البياني وهيكلة العقد", "content": m2},
            {"title": "الوحدة 3: الذاكرة المستمرة وتبادل الرسائل", "content": m3},
            {"title": "الوحدة 4: دمج الأدوات (Tools) وحلقات التكرار", "content": m4},
            {"title": "الوحدة 5: النشر والمراقبة في الإنتاج", "content": m5},
        ],
    }
