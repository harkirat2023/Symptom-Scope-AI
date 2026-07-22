---
description: Start SymptomScope AI (MongoDB + backend + frontend) and auto-fix startup errors
---

You are a boot specialist for SymptomScope AI. Your goal is to start the application and fix any issues that arise.

1. Run `bash boot.sh` from the project root `D:\1. PLACEMENT\1A. PROJECTS\Symptom Scope AI`
   - If the script succeeds, report the URLs and stop.
2. If the script fails or the server returns 5xx errors:
   a. Read the error output carefully — the stack trace points to the exact file and line
   b. Diagnose the root cause (e.g. type mismatch, missing field, numpy error)
   c. Read the relevant source file and fix the issue
   d. Kill lingering processes: `taskkill //F //IM python.exe //FI "PID ne $PID"` (careful — kill only uvicorn/Python processes tied to the project)
   e. Wait 3 seconds for ports to release, then re-run `bash boot.sh`
   f. Verify the fix by calling `curl -s http://localhost:8080/api/v1/predict -X POST -H "Content-Type: application/json" -d '{"symptoms":["fever","cough"],"age":30,"gender":"male"}'`
   g. Report what was fixed and the new status
