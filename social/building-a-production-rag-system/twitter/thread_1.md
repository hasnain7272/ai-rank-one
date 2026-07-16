🚀 دورة جديدة: بناء نظام RAG للإنتاج مع البحث الهجين وإعادة الترتيب.

هل تعاني من ضعف إجابات نظام الـ RAG الخاص بك عند التعامل مع مستندات حقيقية وصعبة؟

في هذه الدورة، سنتعلم الحلول الهندسية التي تستخدمها كبرى الشركات لحل هذه المشكلة.

تابع الثريد 👇 #الذكاء_الاصطناعي #RAG

---

1/4 البحث المتجهي (Vector Search) وحده لا يكفي في الإنتاج. إذا بحث المستخدم عن رقم تسلسلي دقيق، قد يفشل المتجه الدلالي.

الحل هو البحث الهجين (Hybrid Search) الذي يدمج بين البحث النصي التقليدي (BM25) والبحث المتجهي الكثيف.

---

2/4 لدمج النتائج نستخدم خوارزمية Reciprocal Rank Fusion (RRF):

```python
def rrf(dense_results, sparse_results, k=60):
    score = {}
    for rank, doc in enumerate(dense_results):
        score[doc] = score.get(doc, 0) + 1.0 / (k + rank + 1)
    return sorted(score.items(), key=lambda x: x[1], reverse=True)
```

---

3/4 افتح الوحدة الأولى مجاناً الآن وتعلم تقنيات تقسيم المستندات وتطبيق إعادة الترتيب (Reranking) لتقليل زمن الاستجابة والهلوسة.

🔗 ابدأ الآن: https://ai-rank-one.hasnainrazalakhani7272.workers.dev/courses/building-a-production-rag-system