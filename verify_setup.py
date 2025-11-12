"""
Quick setup verification script.

Run this to check if your environment is configured correctly.
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment variables are set correctly."""

    print("\n" + "="*60)
    print("  🔧 ENVIRONMENT VERIFICATION")
    print("="*60 + "\n")

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your API keys\n")
        return False

    print("✅ .env file exists")

    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv loaded\n")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("   Run: pip install -r requirements.txt\n")
        return False

    # Check required variables
    checks = {
        "GROQ_API_KEY": {
            "required": True,
            "description": "Groq API Key (get from https://console.groq.com/keys)",
            "starts_with": "gsk_"
        },
        "LANGCHAIN_API_KEY": {
            "required": False,
            "description": "LangSmith API Key (get from https://smith.langchain.com)",
            "starts_with": "ls__"
        },
        "LANGCHAIN_TRACING_V2": {
            "required": False,
            "description": "Enable LangSmith tracing",
            "expected": "true"
        },
        "LANGCHAIN_PROJECT": {
            "required": False,
            "description": "LangSmith project name",
            "expected": None
        }
    }

    all_good = True

    for var, config in checks.items():
        value = os.getenv(var)

        if not value:
            if config["required"]:
                print(f"❌ {var} not set")
                print(f"   {config['description']}\n")
                all_good = False
            else:
                print(f"⚠️  {var} not set (optional)")
                print(f"   {config['description']}\n")
        else:
            # Check format if specified
            if "starts_with" in config and not value.startswith(config["starts_with"]):
                print(f"⚠️  {var} might be invalid")
                print(f"   Should start with '{config['starts_with']}'\n")
            else:
                print(f"✅ {var} is set")

    return all_good


def check_dependencies():
    """Check if required packages are installed."""

    print("\n" + "="*60)
    print("  📦 DEPENDENCY CHECK")
    print("="*60 + "\n")

    packages = [
        "fastapi",
        "uvicorn",
        "langgraph",
        "langchain",
        "langchain_groq",
        "pydantic"
    ]

    all_installed = True

    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            all_installed = False

    if not all_installed:
        print("\n❌ Missing dependencies")
        print("   Run: pip install -r requirements.txt\n")
        return False

    print("\n✅ All dependencies installed")
    return True


def test_groq_connection():
    """Test if Groq API is accessible."""

    print("\n" + "="*60)
    print("  🤖 GROQ API TEST")
    print("="*60 + "\n")

    try:
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not set\n")
            return False

        print("Testing Groq connection...")
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )

        response = llm.invoke("Say 'hello' in exactly one word")
        print(f"✅ Groq API working!")
        print(f"   Response: {response.content}\n")
        return True

    except Exception as e:
        print(f"❌ Groq API test failed")
        print(f"   Error: {str(e)}\n")
        return False


def main():
    """Run all checks."""

    print("\n" + "="*60)
    print("  🩺 DOCTOR'S INTELLIGENT ASSISTANT")
    print("     Setup Verification")
    print("="*60)

    # Check Python version
    if sys.version_info < (3, 11):
        print("\n⚠️  Python 3.11+ recommended")
        print(f"   Current version: {sys.version}")
    else:
        print(f"\n✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")

    # Run checks
    env_ok = check_environment()
    deps_ok = check_dependencies()

    # Only test Groq if environment and deps are OK
    groq_ok = False
    if env_ok and deps_ok:
        groq_ok = test_groq_connection()

    # Summary
    print("\n" + "="*60)
    print("  📊 SUMMARY")
    print("="*60 + "\n")

    if env_ok and deps_ok and groq_ok:
        print("✅ All checks passed! You're ready to go!")
        print("\n🚀 Next steps:")
        print("   1. cd backend")
        print("   2. python tests/test_graph.py")
        print("   3. View traces at https://smith.langchain.com\n")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n📚 Help:")
        print("   See docs/SETUP.md for detailed instructions")
        print("   See docs/README.md for troubleshooting\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
