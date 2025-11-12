"""
Test script for the multi-agent medical assistant graph.

This demonstrates the system working end-to-end without requiring
the FastAPI server. Perfect for development and debugging.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load environment variables
load_dotenv()

from backend.graph import process_patient_intake_sync


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_simple_case():
    """Test with a simple patient case."""

    print_section("TEST CASE 1: Simple Chest Pain")

    patient_input = """
    Patient is a 45-year-old male presenting with chest pain.
    The pain started 2 days ago and is described as sharp and stabbing.
    Pain is moderate in severity, rated 6/10.
    Patient has a history of hypertension and high cholesterol.
    Currently taking Lisinopril 10mg daily and Atorvastatin 20mg daily.
    No known drug allergies.
    Blood pressure today: 145/92, Heart rate: 88 bpm, Temperature: 98.6°F
    """

    result = process_patient_intake_sync(
        patient_id="P12345",
        raw_input=patient_input
    )

    # Display results
    if result.soap_report:
        print_section("SOAP REPORT GENERATED")

        soap = result.soap_report
        print(f"Patient ID: {soap.patient_id}")
        print(f"Generated: {soap.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Confidence: {soap.confidence_level}")

        print("\n" + "─"*60)
        print("S - SUBJECTIVE")
        print("─"*60)
        print(soap.subjective)

        print("\n" + "─"*60)
        print("O - OBJECTIVE")
        print("─"*60)
        print(soap.objective)

        print("\n" + "─"*60)
        print("A - ASSESSMENT")
        print("─"*60)
        print(soap.assessment)

        print("\n" + "─"*60)
        print("P - PLAN")
        print("─"*60)
        print(soap.plan)

        if soap.flags:
            print("\n" + "─"*60)
            print("FLAGS")
            print("─"*60)
            for flag in soap.flags:
                print(f"  - {flag}")

        # Save to file
        output_file = "test_soap_report.json"
        with open(output_file, "w") as f:
            json.dump(soap.model_dump(mode='json'), f, indent=2, default=str)
        print(f"\nFull report saved to: {output_file}")

    else:
        print("ERROR: SOAP report generation failed")
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

    return result


def test_complex_case():
    """Test with a more complex patient case."""

    print_section("TEST CASE 2: Complex Multi-System Case")

    patient_input = """
    67-year-old female patient presents with fatigue, shortness of breath, and leg swelling.
    Symptoms have been progressively worsening over the past 3 weeks.
    Fatigue is severe, limiting daily activities.
    Shortness of breath occurs with minimal exertion and when lying flat.
    Bilateral leg swelling, worse at end of day.

    Medical history:
    - Type 2 Diabetes (diagnosed 15 years ago)
    - Coronary artery disease (stent placed 5 years ago)
    - Chronic kidney disease stage 3
    - Atrial fibrillation

    Current medications:
    - Metformin 1000mg twice daily
    - Aspirin 81mg daily
    - Warfarin 5mg daily
    - Metoprolol 50mg twice daily
    - Furosemide 40mg daily

    Allergies: Penicillin (rash)

    Vital signs:
    - Blood pressure: 168/96
    - Heart rate: 102 irregular
    - Respiratory rate: 22
    - O2 saturation: 91% on room air
    - Weight: 185 lbs (up 12 lbs from last visit 3 weeks ago)
    """

    result = process_patient_intake_sync(
        patient_id="P67890",
        raw_input=patient_input
    )

    if result.soap_report:
        print_section("SOAP REPORT - COMPLEX CASE")
        soap = result.soap_report

        print(f"Patient ID: {soap.patient_id}")
        print(f"Confidence: {soap.confidence_level}")

        print("\nASSESSMENT (excerpt):")
        print(soap.assessment[:300] + "...")

        print("\nPLAN (excerpt):")
        print(soap.plan[:300] + "...")

        if soap.flags:
            print("\nCLINICAL FLAGS:")
            for flag in soap.flags:
                print(f"  WARNING: {flag}")

    return result


def main():
    """Run all test cases."""

    print("\n" + "="*60)
    print("  DOCTOR'S INTELLIGENT ASSISTANT - TEST SUITE")
    print("="*60)

    # Check environment
    print("\nEnvironment Check:")
    print(f"  GROQ_API_KEY: {'SUCCESS: Set' if os.getenv('GROQ_API_KEY') else 'ERROR: Missing'}")
    print(f"  LANGCHAIN_API_KEY: {'SUCCESS: Set' if os.getenv('LANGCHAIN_API_KEY') else 'ERROR: Missing'}")
    print(f"  LangSmith Tracing: {'SUCCESS: Enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else 'WARNING: Disabled'}")

    if not os.getenv('GROQ_API_KEY'):
        print("\nERROR: GROQ_API_KEY not found in environment")
        print("Please create a .env file with your Groq API key")
        print("Get your key from: https://console.groq.com/keys")
        return

    # Run test cases
    try:
        test_simple_case()

        # Uncomment to run complex case
        # test_complex_case()

        print_section("SUCCESS: ALL TESTS COMPLETED")

        if os.getenv('LANGCHAIN_TRACING_V2') == 'true':
            print("View detailed traces at: https://smith.langchain.com")
            print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")

    except Exception as e:
        print(f"\nERROR: Test failed with error:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
