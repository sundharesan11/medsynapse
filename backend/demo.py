"""
Interactive Demo for Doctor's Intelligent Assistant

Run this to demo the system interactively from the terminal.
Perfect for presentations and showcasing to colleagues!
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from graph import process_patient_intake_sync
from utils.qdrant_client import get_qdrant_client


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*70)
    print("  DOCTOR'S INTELLIGENT ASSISTANT - LIVE DEMO")
    print("  Multi-Agent System with Patient Memory")
    print("="*70 + "\n")


def print_section(title: str, char: str = "─"):
    """Print a section header."""
    print(f"\n{char*70}")
    print(f"  {title}")
    print(f"{char*70}\n")


def demo_quick_case():
    """Demo 1: Quick case with pre-filled data."""
    print_section("DEMO 1: Quick Case (Pre-filled)", "=")

    print("Demonstrating cardiac case processing...\n")

    patient_input = """
    58-year-old male presents with chest tightness and sweating.
    Pain started 2 hours ago, described as pressure-like sensation.
    Patient has history of hypertension and diabetes.
    Currently taking Metformin 1000mg and Lisinopril 10mg.
    Blood pressure: 160/95, Heart rate: 98, appears anxious
    """

    print("PATIENT INPUT:")
    print(patient_input)

    input("\nPress ENTER to start processing...")

    # Process the case
    result = process_patient_intake_sync(
        patient_id="DEMO_001",
        raw_input=patient_input
    )

    # Display results
    display_results(result)


def demo_custom_input():
    """Demo 2: Custom patient input from user."""
    print_section("DEMO 2: Custom Patient Case", "=")

    print("Now YOU enter the patient information!\n")
    print("TIP: Include chief complaint, symptoms, history, vitals\n")

    # Get patient ID
    patient_id = input("Enter Patient ID (e.g., P12345): ").strip()
    if not patient_id:
        patient_id = "DEMO_CUSTOM"

    print("\nEnter patient information (type END on a new line when done):")
    print("-" * 70)

    # Collect multi-line input
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    patient_input = "\n".join(lines)

    if not patient_input.strip():
        print("\n[ERROR] No input provided. Skipping this demo.\n")
        return

    print("\nProcessing your case...")

    # Process the case
    result = process_patient_intake_sync(
        patient_id=patient_id,
        raw_input=patient_input
    )

    # Display results
    display_results(result)


def demo_similar_cases():
    """Demo 3: Show similar case retrieval."""
    print_section("DEMO 3: Similar Case Detection", "=")

    print("This patient has SIMILAR symptoms to a previous case...")
    print("Watch how the system finds matching historical cases!\n")

    patient_input = """
    62-year-old male with chest pain radiating to left arm.
    Pain started during physical activity, relieved with rest.
    History of high cholesterol and smoking.
    Taking Atorvastatin 40mg.
    BP: 155/92, HR: 95, appears uncomfortable
    """

    print("PATIENT INPUT:")
    print(patient_input)

    input("\nPress ENTER to start processing...")

    result = process_patient_intake_sync(
        patient_id="DEMO_SIMILAR",
        raw_input=patient_input
    )

    # Highlight similar cases
    display_results(result, highlight_similar=True)


def display_results(result, highlight_similar=False):
    """Display the SOAP report and similar cases."""

    if not result.soap_report:
        print("\n[ERROR] Report generation failed!")
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        return

    soap = result.soap_report

    print_section("PROCESSING COMPLETE", "=")

    # Show similar cases if found
    if highlight_similar and result.knowledge_context and result.knowledge_context.similar_cases:
        print_section("SIMILAR HISTORICAL CASES FOUND", "-")

        for i, case in enumerate(result.knowledge_context.similar_cases, 1):
            print(f"\n{i}. Patient {case['patient_id']} - Similarity: {case['score']:.0%}")
            print(f"   Chief Complaint: {case['chief_complaint']}")
            print(f"   Symptoms: {', '.join(case['symptoms'][:3])}")
            if case.get('assessment'):
                print(f"   Previous Assessment: {case['assessment'][:100]}...")
        print()

    # Display SOAP report
    print_section("📄 SOAP REPORT", "─")

    print(f"Patient ID: {soap.patient_id}")
    print(f"Generated: {soap.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Confidence: {soap.confidence_level or 'N/A'}")

    print("\n" + "─"*70)
    print("S - SUBJECTIVE")
    print("─"*70)
    print(soap.subjective)

    print("\n" + "─"*70)
    print("O - OBJECTIVE")
    print("─"*70)
    print(soap.objective)

    print("\n" + "─"*70)
    print("A - ASSESSMENT")
    print("─"*70)
    print(soap.assessment)

    print("\n" + "─"*70)
    print("P - PLAN")
    print("─"*70)
    print(soap.plan)

    if soap.flags:
        print("\n" + "-"*70)
        print("CLINICAL FLAGS")
        print("-"*70)
        for flag in soap.flags:
            print(f"  [!] {flag}")

    print("\n" + "="*70 + "\n")


def show_database_stats():
    """Show current database statistics."""
    print_section("DATABASE STATISTICS", "-")

    try:
        qdrant = get_qdrant_client()
        stats = qdrant.get_collection_stats()

        print(f"Total Cases Stored: {stats.get('total_cases', 0)}")
        print(f"Vector Dimension: {stats.get('vector_dimension', 0)}")
        print(f"Database Status: {stats.get('status', 'Unknown')}")
        print()

    except Exception as e:
        print(f"[WARNING] Could not retrieve stats: {e}\n")


def interactive_menu():
    """Show interactive menu."""
    while True:
        print("\n" + "="*70)
        print("  DEMO OPTIONS")
        print("="*70)
        print()
        print("  1. Quick Demo (pre-filled cardiac case)")
        print("  2. Enter Your Own Patient Case")
        print("  3. Demo Similar Case Detection")
        print("  4. View Database Statistics")
        print("  5. Search for Similar Cases")
        print("  Q. Quit")
        print()

        choice = input("Select option (1-5 or Q): ").strip().upper()

        if choice == "1":
            demo_quick_case()
        elif choice == "2":
            demo_custom_input()
        elif choice == "3":
            demo_similar_cases()
        elif choice == "4":
            show_database_stats()
        elif choice == "5":
            search_demo()
        elif choice == "Q":
            print("\nThank you for watching the demo!\n")
            print("View cases in Qdrant Dashboard: http://localhost:6333/dashboard")
            print("View LangSmith traces: https://smith.langchain.com\n")
            break
        else:
            print("\n[ERROR] Invalid choice. Please try again.")


def search_demo():
    """Demo searching for similar cases."""
    print_section("SEARCH FOR SIMILAR CASES", "=")

    query = input("Enter symptoms to search for (e.g., 'chest pain and breathing difficulty'): ").strip()

    if not query:
        print("[ERROR] No search query provided.\n")
        return

    # Ask if they want to see all results (debug mode)
    show_all = input("Show ALL results including low scores? (y/n, default=n): ").strip().lower()

    try:
        qdrant = get_qdrant_client()

        if show_all == 'y':
            # Debug mode: Show ALL matches with no threshold
            results = qdrant.search_similar_cases(
                query_text=query,
                limit=10,
                score_threshold=0.0  # Show everything!
            )
            print(f"\nDEBUG MODE: Showing all {len(results)} matches (no threshold):\n")
        else:
            # Normal mode: Use reasonable threshold
            results = qdrant.search_similar_cases(
                query_text=query,
                limit=5,
                score_threshold=0.5  # 50% similarity minimum
            )
            print(f"\nFound {len(results)} similar cases (>50% threshold):\n")

        if results:
            for i, case in enumerate(results, 1):
                # Indicate similarity level
                score = case['score']
                if score >= 0.75:
                    indicator = "[HIGH]"
                elif score >= 0.60:
                    indicator = "[MED] "
                else:
                    indicator = "[LOW] "

                print(f"{indicator} {i}. Patient {case['patient_id']} - Similarity: {score:.1%} ({score:.3f})")
                print(f"   Chief Complaint: {case['chief_complaint']}")
                print(f"   Symptoms: {', '.join(case['symptoms'][:3])}")
                print()

            if show_all != 'y':
                print("TIP: Run again with 'y' to see ALL matches including filtered ones\n")
        else:
            print("\n[INFO] No cases in database. Run test_qdrant.py to populate.\n")

    except Exception as e:
        print(f"\n[ERROR] Search failed: {e}\n")


def check_environment():
    """Check if environment is properly configured."""
    print("Checking environment...\n")

    checks_passed = True

    # Check Groq API
    if os.getenv("GROQ_API_KEY"):
        print("[OK] Groq API Key configured")
    else:
        print("[ERROR] GROQ_API_KEY not found in .env")
        checks_passed = False

    # Check LangSmith
    if os.getenv("LANGCHAIN_API_KEY"):
        print("[OK] LangSmith API Key configured")
    else:
        print("[WARNING] LangSmith not configured (optional)")

    # Check Qdrant
    try:
        import requests
        # Try root endpoint instead of /health (which returns 404 in some versions)
        response = requests.get("http://localhost:6333/", timeout=2)
        if response.status_code == 200:
            print("[OK] Qdrant database is running")
        else:
            print("[ERROR] Qdrant is not responding properly")
            checks_passed = False
    except Exception:
        print("[ERROR] Qdrant is not running")
        print("   Run: docker-compose up -d qdrant")
        checks_passed = False

    print()
    return checks_passed


def main():
    """Main demo function."""
    print_banner()

    # Check environment
    if not check_environment():
        print("[ERROR] Environment not properly configured. Please fix issues above.\n")
        sys.exit(1)

    print("System ready. Starting demo.\n")
    print("NOTE: Each case is automatically stored with embeddings")
    print("      and can be retrieved using semantic search.\n")

    input("Press ENTER to start the demo...")

    # Start interactive menu
    interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Exiting.\n")
        sys.exit(0)
