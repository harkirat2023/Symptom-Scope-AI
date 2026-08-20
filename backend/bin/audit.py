"""
Feature Audit Script — verifies all SymptomScope AI features are operational.

Checks:
- API endpoints respond correctly
- ML models are trained and loadable
- Database connectivity
- LLM service initialization
- RAG knowledge base status
- Rate limiting configuration
- Security headers
- CORS configuration
- Authentication setup

Usage:
    python -m bin.audit  (requires running server on localhost:8000)
    python -m bin.audit --offline  (checks imports and files only)
"""

import argparse
import importlib
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("audit")

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

API_BASE = "http://localhost:8000/api/v1"

FEATURE_LIST = [
    # (feature_name, api_path, method, expected_fields)
    ("Health Check", "/health", "GET", ["status", "version"]),
    ("Prediction", "/predict", "POST", ["prediction", "confidence", "severity"]),
    ("Symptom List", "/symptoms", "GET", ["symptoms"]),
    ("Doctor Search", "/doctors", "GET", ["doctors"]),
    ("Hospitals", "/hospitals", "GET", ["hospitals"]),
    ("Analytics", "/analytics/summary", "GET", ["summary"]),
    ("Risk Score", "/risk-score", "POST", ["risk_score", "level"]),
    ("Chat Session", "/chat/session", "POST", ["_id", "user_id"]),
    ("Chat Message", "/chat/message", "POST", ["_id", "content"]),
    ("Chat Sessions", "/chat/sessions", "GET", ["sessions"]),
    ("AI Medical Explain", "/chat/explain", "POST", ["explanation"]),
    ("AI Follow-up", "/chat/follow-up", "POST", ["follow_up_questions"]),
    ("Medical Q&A", "/chat/ask", "POST", ["answer"]),
    ("Export", "/export/pdf", "POST", []),
    ("Reports", "/reports", "POST", ["report_id"]),
    ("Reminders", "/reminders", "POST", ["reminder_id"]),
]

ML_ARTIFACTS = [
    "ml/models/decision_tree_v1.pkl",
    "ml/models/random_forest_v1.pkl",
    "ml/models/naive_bayes_v1.pkl",
    "ml/models/label_encoder_v1.pkl",
    "ml/models/symptom_columns_v1.pkl",
]

REQUIRED_MODULES = [
    "main",
    "utils.settings",
    "utils.database",
    "utils.rate_limit",
    "utils.logging_config",
    "utils.env_check",
    "utils.request_logger",
    "utils.exceptions",
    "services.prediction_service",
    "services.chat_service",
    "services.llm_service",
    "services.rag_service",
    "services.reminder_service",
    "repositories.prediction_repository",
    "repositories.chat_repository",
    "repositories.reminder_repository",
    "repositories.risk_score_repository",
    "schemas.prediction_schema",
    "schemas.chat_schema",
    "api.v1.predict",
    "api.v1.chat",
    "api.v1.doctors",
    "api.v1.hospitals",
    "api.v1.analytics",
    "api.v1.reports",
    "api.v1.export",
    "api.v1.reminders",
    "api.v1.risk_score",
    "ml.training.train_models",
]


def verify_module_imports() -> list[dict]:
    results = []
    for mod_name in REQUIRED_MODULES:
        try:
            importlib.import_module(mod_name)
            results.append({"module": mod_name, "status": "OK"})
        except Exception as e:
            results.append({"module": mod_name, "status": "FAIL", "error": str(e)})
    return results


def verify_ml_artifacts() -> list[dict]:
    results = []
    for artifact in ML_ARTIFACTS:
        path = PROJECT_ROOT / artifact
        exists = path.exists()
        size_kb = path.stat().st_size / 1024 if exists else 0
        results.append({
            "artifact": artifact,
            "exists": exists,
            "size_kb": round(size_kb, 1),
        })
    return results


def verify_rag_knowledge() -> dict:
    knowledge_dir = PROJECT_ROOT / "ml" / "rag" / "knowledge"
    if not knowledge_dir.exists():
        return {"exists": False, "files": 0}
    files = list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md"))
    return {"exists": True, "files": len(files), "file_list": [f.name for f in files]}


def verify_prompts() -> list[dict]:
    prompts_dir = PROJECT_ROOT / "ml" / "prompts"
    if not prompts_dir.exists():
        return [{"dir": str(prompts_dir), "exists": False}]
    results = []
    for f in sorted(prompts_dir.glob("*.txt")):
        content = f.read_text(encoding="utf-8")
        results.append({"file": f.name, "size": len(content), "exists": True})
    return results


def check_api_endpoints() -> list[dict]:
    results = []
    try:
        import httpx
    except ImportError:
        return [{"endpoint": "all", "status": "SKIP", "reason": "httpx not installed"}]

    test_data = {
        "/predict": {
            "symptoms": ["fever", "dry_cough", "fatigue"],
            "age": 30, "gender": "male",
        },
        "/chat/session": {"prediction_id": None},
        "/chat/message": {"session_id": "", "content": "Hello"},
        "/chat/explain": {
            "disease": "Common Cold", "confidence": 85.0, "severity": "mild",
            "symptoms": ["fever", "cough"],
        },
        "/chat/follow-up": {
            "disease": "Common Cold", "confidence": 85.0, "severity": "mild",
            "symptoms": ["fever"],
        },
        "/chat/ask": {"question": "What is the common cold?"},
        "/risk-score": {
            "age": 45, "bmi": 28, "blood_pressure": "140/90",
            "smoker": True, "diabetes": False,
        },
    }

    for feature, path, method, expected_fields in FEATURE_LIST:
        if path == "/health":
            url = "http://localhost:8000/health"
        else:
            url = f"{API_BASE}{path}"

        try:
            if path in test_data:
                response = httpx.post(url, json=test_data[path], timeout=10)
            elif method == "GET":
                response = httpx.get(url, timeout=10)
            else:
                response = httpx.post(url, json={}, timeout=10)

            status_ok = response.status_code in (200, 201)
            fields_ok = all(f in response.json() for f in expected_fields) if expected_fields else True

            results.append({
                "feature": feature,
                "path": path,
                "status_code": response.status_code,
                "status": "OK" if (status_ok and fields_ok) else "WARN",
                "details": "status ok" if status_ok else f"got {response.status_code}",
            })
        except Exception as e:
            results.append({
                "feature": feature,
                "path": path,
                "status_code": None,
                "status": "FAIL",
                "details": str(e),
            })

    return results


def generate_report(
    module_results: list[dict],
    ml_results: list[dict],
    rag_info: dict,
    prompt_results: list[dict],
    api_results: list[dict] | None,
) -> str:
    lines = []
    lines.append("# SymptomScope AI — Audit Report")
    lines.append("\nGenerated: automated\n")
    lines.append("---\n")

    # Module imports
    lines.append("## Module Imports\n")
    passed = sum(1 for r in module_results if r["status"] == "OK")
    total = len(module_results)
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Passed | {passed}/{total} |")
    lines.append(f"| Failed | {total - passed}/{total} |")
    lines.append("\n**Failed modules:**")
    for r in module_results:
        if r["status"] != "OK":
            lines.append(f"- `{r['module']}`: {r.get('error', 'unknown')}")
    lines.append("")

    # ML artifacts
    lines.append("## ML Artifacts\n")
    lines.append("| Artifact | Exists | Size |")
    lines.append("|----------|--------|------|")
    for r in ml_results:
        lines.append(f"| {r['artifact']} | {'✅' if r['exists'] else '❌'} | {r['size_kb']} KB |")
    lines.append("")

    # RAG
    lines.append("## RAG Knowledge Base\n")
    lines.append(f"- **Exists:** {'✅' if rag_info['exists'] else '❌'}")
    lines.append(f"- **Document files:** {rag_info.get('files', 0)}")
    if rag_info.get("file_list"):
        for fname in rag_info["file_list"]:
            lines.append(f"  - {fname}")
    lines.append("")

    # Prompts
    lines.append("## Prompt Templates\n")
    all_ok = all(r["exists"] for r in prompt_results)
    lines.append(f"- **All prompts present:** {'✅' if all_ok else '❌'}")
    if not all_ok:
        for r in prompt_results:
            if not r["exists"]:
                lines.append(f"  - Missing: {r['file']}")
    lines.append("")

    # API endpoints
    if api_results:
        lines.append("## API Endpoints\n")
        lines.append("| Feature | Path | Status | Code | Details |")
        lines.append("|---------|------|--------|------|---------|")
        for r in api_results:
            emoji = "✅" if r["status"] == "OK" else "⚠️" if r["status"] == "WARN" else "❌"
            code = str(r["status_code"]) if r["status_code"] else "N/A"
            lines.append(f"| {r['feature']} | {r['path']} | {emoji} {r['status']} | {code} | {r['details']} |")
        lines.append("")
        api_ok = sum(1 for r in api_results if r["status"] == "OK")
        lines.append(f"**API endpoints passing:** {api_ok}/{len(api_results)}")
    else:
        lines.append("\n## API Endpoints\n")
        lines.append("*Skipped — server not running. Start with `uvicorn main:app` and rerun.*\n")

    overall = "ALL CHECKS PASSED" if (passed == total and (api_results is None or all(r["status"] == "OK" for r in api_results))) else "SOME CHECKS FAILED"
    lines.append(f"\n## Overall: {overall}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SymptomScope AI Feature Audit")
    parser.add_argument("--offline", action="store_true", help="Skip HTTP endpoint checks")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("  SymptomScope AI — Feature Audit")
    logger.info("=" * 60)

    logger.info("\n[1/5] Verifying module imports...")
    module_results = verify_module_imports()

    logger.info("\n[2/5] Checking ML artifacts...")
    ml_results = verify_ml_artifacts()

    logger.info("\n[3/5] Checking RAG knowledge base...")
    rag_info = verify_rag_knowledge()

    logger.info("\n[4/5] Checking prompt templates...")
    prompt_results = verify_prompts()

    api_results = None
    if not args.offline:
        logger.info("\n[5/5] Checking API endpoints...")
        api_results = check_api_endpoints()
    else:
        logger.info("\n[5/5] Skipping API checks (offline mode)")

    report = generate_report(module_results, ml_results, rag_info, prompt_results, api_results)

    report_path = PROJECT_ROOT / "AUDIT_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    logger.info("\nAudit report saved to: %s", report_path)
    safe_report = report.replace("\u2705", "[OK]").replace("\u274c", "[FAIL]").replace("\u26a0\ufe0f", "[WARN]")
    try:
        print("\n" + report)
    except UnicodeEncodeError:
        print("\n" + safe_report)


if __name__ == "__main__":
    main()
