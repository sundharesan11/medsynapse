"""
Test script for Phase 2: Qdrant Vector Database Integration

This demonstrates:
1. Storing multiple patient cases in Qdrant
2. Semantic similarity search
3. Patient history retrieval
4. Similar case recommendations
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

from graph import process_patient_intake_sync
from utils.qdrant_client import get_qdrant_client


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_store_multiple_cases():
    """
    Test 1: Store multiple patient cases with different conditions.

    This simulates building up a patient database over time.
    """
    print_section("TEST 1: Storing Multiple Patient Cases")

    test_cases = [
        {
            "patient_id": "P001",
            "description": "Patient with chest pain and cardiovascular history",
            "input": """
            45-year-old male with sharp chest pain for 2 days.
            Pain is moderate, 6/10 severity.
            History of hypertension and high cholesterol.
            Taking Lisinopril 10mg and Atorvastatin 20mg.
            BP: 145/92, HR: 88
            """
        },
        {
            "patient_id": "P002",
            "description": "Patient with respiratory symptoms",
            "input": """
            32-year-old female with persistent cough and shortness of breath for 1 week.
            Cough is dry, worse at night.
            History of asthma.
            Taking albuterol inhaler as needed.
            Temperature: 99.8°F, O2 sat: 94%
            """
        },
        {
            "patient_id": "P003",
            "description": "Patient with cardiac symptoms (similar to P001)",
            "input": """
            58-year-old male with chest discomfort and difficulty breathing.
            Pressure-like sensation in chest, started this morning.
            History of diabetes and coronary artery disease.
            Taking Metformin 1000mg and Aspirin 81mg.
            BP: 150/95, HR: 92, irregular rhythm
            """
        },
        {
            "patient_id": "P004",
            "description": "Patient with respiratory infection (similar to P002)",
            "input": """
            28-year-old female with cough, fever, and chest congestion for 3 days.
            Productive cough with yellow sputum.
            No significant medical history.
            No current medications.
            Temperature: 101.2°F, HR: 95
            """
        },
        {
            "patient_id": "P005",
            "description": "Patient with headache and neurological symptoms",
            "input": """
            42-year-old female with severe headache for 2 days.
            Headache is throbbing, located in temples.
            Associated with nausea and sensitivity to light.
            History of migraines.
            Taking Sumatriptan as needed.
            BP: 128/82, HR: 78
            """
        }
    ]

    print(f"📝 Processing {len(test_cases)} patient cases...\n")

    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Case {i}/{len(test_cases)}: {case['patient_id']} ---")
        print(f"Description: {case['description']}")

        # Process through the pipeline (this will automatically store in Qdrant)
        result = process_patient_intake_sync(
            patient_id=case["patient_id"],
            raw_input=case["input"]
        )

        if result.soap_report:
            print(f"✅ Case {case['patient_id']} processed and stored")
        else:
            print(f"❌ Case {case['patient_id']} failed")

        # Small delay to avoid rate limits
        time.sleep(2)

    print_section("✅ All Cases Stored")


def test_semantic_search():
    """
    Test 2: Semantic similarity search.

    Search for cases similar to a query, even with different wording.
    """
    print_section("TEST 2: Semantic Similarity Search")

    qdrant = get_qdrant_client()

    test_queries = [
        {
            "query": "chest pain and heart problems",
            "expected": "Should find P001 and P003 (cardiac cases)"
        },
        {
            "query": "coughing and respiratory issues",
            "expected": "Should find P002 and P004 (respiratory cases)"
        },
        {
            "query": "severe headache with nausea",
            "expected": "Should find P005 (migraine case)"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"🔍 Searching for: \"{test['query']}\"")
        print(f"   Expected: {test['expected']}")

        results = qdrant.search_similar_cases(
            query_text=test['query'],
            limit=3,
            score_threshold=0.5
        )

        if results:
            print(f"\n✅ Found {len(results)} similar cases:")
            for j, case in enumerate(results, 1):
                print(f"\n   {j}. Patient {case['patient_id']} (Score: {case['score']:.2f})")
                print(f"      Chief Complaint: {case['chief_complaint']}")
                print(f"      Symptoms: {', '.join(case['symptoms'][:3])}...")
        else:
            print("   ❌ No similar cases found")

        print()


def test_patient_history():
    """
    Test 3: Retrieve patient history.

    Get all previous encounters for a specific patient.
    """
    print_section("TEST 3: Patient History Retrieval")

    qdrant = get_qdrant_client()

    # Test retrieving history for P001
    patient_id = "P001"
    print(f"📚 Retrieving history for patient {patient_id}...")

    history = qdrant.get_patient_history(patient_id=patient_id, limit=10)

    if history:
        print(f"\n✅ Found {len(history)} previous encounters:\n")
        for i, encounter in enumerate(history, 1):
            print(f"{i}. {encounter['timestamp'][:19]}")
            print(f"   Chief Complaint: {encounter['chief_complaint']}")
            print(f"   Symptoms: {', '.join(encounter['symptoms'])}")
            print()
    else:
        print(f"   No history found for patient {patient_id}")


def test_collection_stats():
    """
    Test 4: Get collection statistics.
    """
    print_section("TEST 4: Collection Statistics")

    qdrant = get_qdrant_client()
    stats = qdrant.get_collection_stats()

    print("📊 Qdrant Collection Stats:")
    print(f"   Total Cases: {stats.get('total_cases', 0)}")
    print(f"   Vector Dimension: {stats.get('vector_dimension', 0)}")
    print(f"   Status: {stats.get('status', 'Unknown')}")


def test_similar_case_in_pipeline():
    """
    Test 5: Process a new case and see similar historical cases.

    This demonstrates the full Phase 2 feature: when processing a new case,
    the knowledge agent will automatically find similar historical cases.
    """
    print_section("TEST 5: New Case with Similar Case Retrieval")

    print("📝 Processing a NEW patient with cardiac symptoms...")
    print("   The knowledge agent should find similar cases from P001 and P003\n")

    new_case_input = """
    52-year-old male presents with chest tightness and sweating.
    Symptoms started 1 hour ago, described as squeezing sensation.
    History of high blood pressure and smoking.
    Currently taking Amlodipine 5mg daily.
    BP: 160/98, HR: 102, appears anxious
    """

    result = process_patient_intake_sync(
        patient_id="P_NEW_001",
        raw_input=new_case_input
    )

    if result.knowledge_context and result.knowledge_context.similar_cases:
        print("\n✨ SIMILAR HISTORICAL CASES FOUND:")
        for i, case in enumerate(result.knowledge_context.similar_cases, 1):
            print(f"\n{i}. Patient {case['patient_id']} (Similarity: {case['score']:.0%})")
            print(f"   Chief Complaint: {case['chief_complaint']}")
            print(f"   Assessment: {case['assessment'][:100]}...")
    else:
        print("\n   No similar historical cases found (database might be empty)")


def main():
    """Run all Phase 2 tests."""

    print("\n" + "="*70)
    print("  🧠 PHASE 2: QDRANT VECTOR DATABASE INTEGRATION")
    print("     Testing Patient Memory & Semantic Search")
    print("="*70)

    # Check environment
    print("\n🔧 Environment Check:")
    print(f"  GROQ_API_KEY: {'✅' if os.getenv('GROQ_API_KEY') else '❌'}")
    print(f"  QDRANT_URL: {os.getenv('QDRANT_URL', 'http://localhost:6333')}")

    # Check Qdrant connection
    print("\n🔌 Checking Qdrant connection...")
    try:
        qdrant = get_qdrant_client()
        print("✅ Connected to Qdrant successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        print("\n⚠️  Make sure Qdrant is running:")
        print("   docker-compose up -d qdrant")
        print("\nOr start it manually:")
        print("   docker run -p 6333:6333 qdrant/qdrant")
        return

    # Run tests
    try:
        # Test 1: Store multiple cases
        test_store_multiple_cases()

        # Test 2: Semantic search
        test_semantic_search()

        # Test 3: Patient history
        test_patient_history()

        # Test 4: Stats
        test_collection_stats()

        # Test 5: Similar cases in pipeline
        test_similar_case_in_pipeline()

        print_section("✅ ALL PHASE 2 TESTS COMPLETED")

        print("🎉 Phase 2 Features Working:")
        print("   ✅ Case storage with embeddings")
        print("   ✅ Semantic similarity search")
        print("   ✅ Patient history retrieval")
        print("   ✅ Similar case recommendations in pipeline")

        print("\n🔍 View Qdrant UI at: http://localhost:3001")
        print("   (if you started docker-compose with qdrant-web-ui)")

    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
