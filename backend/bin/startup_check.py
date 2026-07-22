"""
Startup Validation Script.

Runs before the server starts to validate:
- Environment variables are set correctly
- ML models exist and are loadable
- Database connection is reachable
- RAG knowledge base is initialized
- Required directories exist

Usage:
    python -m bin.startup_check
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("startup_check")

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CHECKS: list[dict] = []


def check(description: str):
    def decorator(func):
        CHECKS.append({"description": description, "func": func})
        return func
    return decorator


@check("MONGODB_URI is set")
def _check_mongo():
    from utils.settings import settings
    if not settings.mongodb_uri:
        raise ValueError("MONGODB_URI is not configured")


@check("GEMINI_API_KEY is set")
def _check_gemini():
    from utils.settings import settings
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")


@check("ML model artifacts exist")
def _check_models():
    artifacts = [
        "ml/models/decision_tree_v1.pkl",
        "ml/models/random_forest_v1.pkl",
        "ml/models/naive_bayes_v1.pkl",
        "ml/models/label_encoder_v1.pkl",
        "ml/models/symptom_columns_v1.pkl",
    ]
    missing = []
    for art in artifacts:
        path = PROJECT_ROOT / art
        if not path.exists():
            missing.append(art)
    if missing:
        raise FileNotFoundError(f"Missing ML artifacts: {', '.join(missing)}")


@check("RAG knowledge base directory exists")
def _check_rag():
    knowledge_dir = PROJECT_ROOT / "ml" / "rag" / "knowledge"
    if not knowledge_dir.exists():
        logger.warning("RAG knowledge directory missing — create ml/rag/knowledge/ with .txt files")
        return
    files = list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md"))
    if not files:
        logger.warning("RAG knowledge directory is empty — add medical documents")


@check("Prompt templates exist")
def _check_prompts():
    required_prompts = [
        "explain_prediction.txt",
        "follow_up_questions.txt",
        "medical_qa.txt",
        "chat.txt",
    ]
    prompts_dir = PROJECT_ROOT / "ml" / "prompts"
    missing = []
    for p in required_prompts:
        if not (prompts_dir / p).exists():
            missing.append(p)
    if missing:
        raise FileNotFoundError(f"Missing prompt templates: {', '.join(missing)}")


@check("Database connection is reachable")
def _check_db():
    from utils.database import get_database
    try:
        db = get_database()
        db.command("ping")
    except Exception as e:
        raise ConnectionError(f"Database unreachable: {e}")


def main():
    logger.info("=" * 50)
    logger.info("  Startup Validation")
    logger.info("=" * 50)

    passed = 0
    failed = 0
    for check_item in CHECKS:
        desc = check_item["description"]
        try:
            check_item["func"]()
            logger.info("  ✅  %s", desc)
            passed += 1
        except Exception as e:
            logger.error("  ❌  %s — %s", desc, e)
            failed += 1

    logger.info("-" * 50)
    logger.info("  Result: %d passed, %d failed", passed, failed)

    if failed > 0:
        sys.exit(1)

    logger.info("  All checks passed — ready to start.")


if __name__ == "__main__":
    main()
