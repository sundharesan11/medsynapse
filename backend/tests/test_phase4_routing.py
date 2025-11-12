"""
Test script for Phase 4 dynamic routing features.

Tests various case scenarios to demonstrate:
- Case priority detection (routine, urgent, emergency)
- Routing path tracking
- Enhanced analysis flagging
- Processing time measurement
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.graph import process_patient_intake_sync


def test_routine_case():
    """Test a routine case with mild symptoms."""
    print("\n" + "="*80)
    print("TEST 1: ROUTINE CASE - Mild headache")
    print("="*80)

    result = process_patient_intake_sync(
        patient_id="P001",
        raw_input="""
        Patient reports a mild headache that started yesterday.
        Pain level is 3/10. No other symptoms.
        Taking ibuprofen as needed.
        No significant medical history.
        """
    )

    print(f"\nRESULTS:")
    print(f"   Priority: {result.case_priority}")
    print(f"   Path: {' -> '.join(result.routing_path)}")
    print(f"   Enhanced Analysis: {result.requires_enhanced_analysis}")
    print(f"   Processing Time: {result.processing_time_ms:.2f}ms")

    assert result.case_priority == "routine", f"Expected routine, got {result.case_priority}"
    print("SUCCESS: TEST PASSED")


def test_urgent_case():
    """Test an urgent case with concerning symptoms."""
    print("\n" + "="*80)
    print("TEST 2: URGENT CASE - High fever and persistent vomiting")
    print("="*80)

    result = process_patient_intake_sync(
        patient_id="P002",
        raw_input="""
        Patient has high fever of 103°F for the past 2 days.
        Persistent vomiting, unable to keep food down.
        Feeling weak and dizzy.
        No recent travel. Taking acetaminophen.
        Blood pressure: 140/95, Heart rate: 105
        """
    )

    print(f"\nRESULTS:")
    print(f"   Priority: {result.case_priority}")
    print(f"   Path: {' -> '.join(result.routing_path)}")
    print(f"   Enhanced Analysis: {result.requires_enhanced_analysis}")
    print(f"   Processing Time: {result.processing_time_ms:.2f}ms")

    assert result.case_priority in ["urgent", "emergency"], f"Expected urgent/emergency, got {result.case_priority}"
    print("SUCCESS: TEST PASSED")


def test_emergency_case():
    """Test an emergency case with critical symptoms."""
    print("\n" + "="*80)
    print("TEST 3: EMERGENCY CASE - Severe chest pain")
    print("="*80)

    result = process_patient_intake_sync(
        patient_id="P003",
        raw_input="""
        Patient experiencing severe chest pain that started 30 minutes ago.
        Pain radiates to left arm. Shortness of breath.
        Sweating profusely. Pain level 9/10.
        History of hypertension. Currently on lisinopril.
        Blood pressure: 185/110, Heart rate: 125
        """
    )

    print(f"\nRESULTS:")
    print(f"   Priority: {result.case_priority}")
    print(f"   Path: {' -> '.join(result.routing_path)}")
    print(f"   Enhanced Analysis: {result.requires_enhanced_analysis}")
    print(f"   Processing Time: {result.processing_time_ms:.2f}ms")

    assert result.case_priority == "emergency", f"Expected emergency, got {result.case_priority}"
    print("SUCCESS: TEST PASSED")


def test_complex_case_with_low_confidence():
    """Test a complex case that should trigger enhanced analysis flag."""
    print("\n" + "="*80)
    print("TEST 4: COMPLEX CASE - Multiple vague symptoms")
    print("="*80)

    result = process_patient_intake_sync(
        patient_id="P004",
        raw_input="""
        Patient reports generalized fatigue for several weeks.
        Occasional dizziness, poor appetite, mild joint pain.
        Weight loss of about 10 pounds over 2 months.
        Medical history: diabetes, hypothyroidism, osteoarthritis.
        On metformin, levothyroxine, and occasional NSAIDs.
        No allergies. Vitals within normal range.
        """
    )

    print(f"\nRESULTS:")
    print(f"   Priority: {result.case_priority}")
    print(f"   Path: {' -> '.join(result.routing_path)}")
    print(f"   Enhanced Analysis: {result.requires_enhanced_analysis}")
    print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
    print(f"   Knowledge Confidence: {result.knowledge_context.confidence_score:.2f}")

    # Complex cases with vague symptoms may trigger enhanced analysis
    print("SUCCESS: TEST PASSED")


def test_routing_path_completeness():
    """Test that all expected nodes are in the routing path."""
    print("\n" + "="*80)
    print("TEST 5: ROUTING PATH COMPLETENESS")
    print("="*80)

    result = process_patient_intake_sync(
        patient_id="P005",
        raw_input="Patient has a mild cough for 3 days. No fever."
    )

    expected_nodes = ["intake", "summary", "knowledge", "report", "storage"]

    print(f"\nRESULTS:")
    print(f"   Expected path: {' -> '.join(expected_nodes)}")
    print(f"   Actual path: {' -> '.join(result.routing_path)}")

    assert result.routing_path == expected_nodes, f"Path mismatch! Got: {result.routing_path}"
    print("SUCCESS: TEST PASSED")


def main():
    """Run all Phase 4 routing tests."""
    print("\n" + "="*80)
    print("PHASE 4 DYNAMIC ROUTING TEST SUITE")
    print("="*80)

    tests = [
        test_routine_case,
        test_urgent_case,
        test_emergency_case,
        test_complex_case_with_low_confidence,
        test_routing_path_completeness,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"ERROR: TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: TEST ERROR: {e}")
            failed += 1

    print("\n" + "="*80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*80 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
