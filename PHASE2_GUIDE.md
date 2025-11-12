# 🧠 Phase 2: Qdrant Vector Database Integration - Quick Start

This guide walks you through setting up and testing the patient memory features.

---

## 🎯 What's New in Phase 2?

Phase 2 adds **intelligent patient memory** to your system:

✅ **Semantic Search** - Find similar cases even with different wording
✅ **Patient History** - Track all encounters for each patient
✅ **Similar Case Recommendations** - Automatically suggest relevant historical cases
✅ **Embeddings** - Convert cases to vectors for fast similarity search

---

## 🚀 Setup Steps

### 1. Start Qdrant Database

```bash
# Option A: Using docker-compose (recommended)
docker-compose up -d qdrant

# Option B: Docker directly
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant
```

Verify Qdrant is running:
```bash
curl http://localhost:6333/health
# Should return: {"title":"qdrant - vector search engine","version":"..."}
```

### 2. Install Additional Dependencies

The Phase 2 Qdrant client uses `sentence-transformers` for embeddings:

```bash
pip install -r requirements.txt
```

This installs:
- `qdrant-client` - Vector database client
- `sentence-transformers` - Embedding model (all-MiniLM-L6-v2)

### 3. Run Phase 2 Tests

```bash
cd backend
python3 test_qdrant.py
```

This will:
1. Store 5 different patient cases in Qdrant
2. Demonstrate semantic search
3. Retrieve patient history
4. Show similar case recommendations

---

## 📘 How It Works

### Architecture Update

```
OLD (Phase 1):
START → intake → summary → knowledge → report → END

NEW (Phase 2):
START → intake → summary → knowledge* → report → storage → END
                              ↑ Now searches Qdrant for similar cases
                                                         ↑ Stores case in Qdrant
```

### Embedding Process

```python
# 1. Patient case data
case = "chest pain, shortness of breath, hypertension"

# 2. Convert to embedding (384-dimensional vector)
embedding = [0.23, 0.81, -0.45, ..., 0.17]  # 384 numbers

# 3. Store in Qdrant with metadata
qdrant.store(embedding, payload={
    "patient_id": "P001",
    "chief_complaint": "chest pain",
    "symptoms": ["chest pain", "shortness of breath"],
    ...
})

# 4. Later: Search for similar cases
query = "cardiac symptoms and breathing difficulty"
query_embedding = embed(query)
similar_cases = qdrant.search(query_embedding)
# Returns cases with similar embeddings!
```

---

## 🧪 Testing Semantic Search

Try these examples:

### Example 1: Find Cardiac Cases
```python
from utils.qdrant_client import get_qdrant_client

qdrant = get_qdrant_client()

# Search with natural language
results = qdrant.search_similar_cases(
    query_text="heart problems and chest discomfort",
    limit=3,
    score_threshold=0.7
)

for case in results:
    print(f"Score: {case['score']:.2f}")
    print(f"Patient: {case['patient_id']}")
    print(f"Complaint: {case['chief_complaint']}")
```

### Example 2: Get Patient History
```python
# Retrieve all encounters for a patient
history = qdrant.get_patient_history(
    patient_id="P001",
    limit=10
)

print(f"Found {len(history)} previous encounters")
for encounter in history:
    print(encounter['chief_complaint'])
```

---

## 🔍 View Data in Qdrant UI

If you started with `docker-compose`, you can browse your data:

1. Go to: **http://localhost:3001**
2. You'll see the Qdrant Web UI
3. Browse collections → `patient_cases`
4. View stored vectors and metadata

---

## 💡 Real-World Usage

### Scenario: Recurring Patient

```python
# Patient P001 returns with similar symptoms
result = process_patient_intake_sync(
    patient_id="P001",
    raw_input="Chest pain again, similar to last time..."
)

# The knowledge agent automatically:
# 1. Searches Qdrant for P001's history
# 2. Finds similar past cases
# 3. Includes them in the context
# 4. Report agent considers past assessments

print(result.knowledge_context.similar_cases)
# Shows previous encounters with similarity scores!
```

### Scenario: Pattern Recognition

```python
# Find all cases similar to a symptom pattern
results = qdrant.search_similar_cases(
    query_text="chest pain with elevated blood pressure",
    limit=10,
    score_threshold=0.75
)

print(f"Found {len(results)} cases with this pattern")
# Useful for identifying trends, outbreaks, etc.
```

---

## 🎓 Key Concepts

### Embeddings
- **What**: Numerical representation of text (vectors)
- **Why**: Captures semantic meaning, not just keywords
- **Example**: "heart attack" and "myocardial infarction" have similar embeddings

### Cosine Similarity
- **What**: Measures how similar two vectors are
- **Range**: 0.0 (completely different) to 1.0 (identical)
- **Threshold**: We use 0.75 = pretty similar

### Sentence Transformers
- **Model**: all-MiniLM-L6-v2
- **Dimension**: 384 (each text → 384 numbers)
- **Speed**: Fast! ~1ms per embedding
- **Size**: ~80MB download (happens once)

---

## 🐛 Troubleshooting

### "Failed to connect to Qdrant"
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not, start it
docker-compose up -d qdrant

# Check logs
docker logs medsynapse-qdrant
```

### "No similar cases found"
- Database might be empty → run `test_qdrant.py` to populate
- Threshold too high → try `score_threshold=0.5`
- Query too generic → be more specific

### Slow embedding generation (first time)
- First run downloads the model (~80MB)
- Subsequent runs are fast
- Model cached in `~/.cache/torch/sentence_transformers/`

---

## 📊 Performance

With Qdrant + sentence-transformers:

- **Storage**: ~1KB per case (metadata + vector)
- **Search speed**: <10ms for 1000s of cases
- **Embedding speed**: ~1-2ms per case
- **Scalability**: Millions of cases supported

---

## 🎯 Next Steps

Now that Phase 2 is working, you can:

1. **Phase 3**: Build React frontend to visualize similar cases
2. **Phase 4**: Add dynamic routing based on case similarity
3. **Phase 5**: Deploy with Docker Compose

---

## 🆘 Need Help?

- **Qdrant docs**: https://qdrant.tech/documentation/
- **Sentence Transformers**: https://www.sbert.net/
- **Check logs**: All operations print status messages

---

**🎉 Enjoy Phase 2! Your system now has memory!**
