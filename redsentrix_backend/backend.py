from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import threading
import time

app = FastAPI(title="RedSentrix Backend API")

# Allow CORS from your frontend origin (adjust this URL to your actual frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React/TSX frontend default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory log store (replace with DB or file system in production)
logs_store = []

# Thread-safe log appending helper
def add_log_entry(module: str, message: str, level: str = "info"):
    logs_store.append({
        "timestamp": time.time(),
        "module": module,
        "message": message,
        "level": level,
    })

# Pydantic models for request validation and response
class ScanRequest(BaseModel):
    pattern: Optional[str] = None
    process_name: Optional[str] = None
    pid: Optional[int] = None
    encoding: Optional[str] = None
    key: Optional[str] = None
    entropy_mode: bool = False
    yara_path: Optional[str] = None
    output_path: Optional[str] = None

class LogEntry(BaseModel):
    timestamp: float
    module: str
    message: str
    level: str

# Dummy scanning function simulating the stealth memory scan
def stealth_scan_worker(scan_params: ScanRequest):
    add_log_entry("StealthMemoryScanner", "Stealth memory scan started.", "info")
    # Simulate some scanning activity (replace with actual scanner call)
    time.sleep(5)
    target = scan_params.process_name or str(scan_params.pid) or "unknown"
    add_log_entry("StealthMemoryScanner", f"Stealth memory scan finished for target: {target}", "info")

@app.post("/api/scan")
def start_stealth_scan(scan_params: ScanRequest):
    # Start scan in a background thread
    threading.Thread(target=stealth_scan_worker, args=(scan_params,), daemon=True).start()
    return {"status": "started", "detail": "Stealth memory scan initiated."}

@app.get("/api/logs", response_model=List[LogEntry])
def get_logs(
    module: Optional[str] = Query(None, description="Filter logs by module"),
    level: Optional[str] = Query(None, description="Filter logs by level"),
    search: Optional[str] = Query(None, description="Search text in log messages"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return")
):
    filtered_logs = logs_store

    if module:
        filtered_logs = [log for log in filtered_logs if log["module"].lower() == module.lower()]

    if level:
        filtered_logs = [log for log in filtered_logs if log["level"].lower() == level.lower()]

    if search:
        filtered_logs = [log for log in filtered_logs if search.lower() in log["message"].lower()]

    # Return newest logs first
    filtered_logs = sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True)

    return filtered_logs[:limit]

# Persistence module stub endpoint
@app.post("/api/persistence/start")
def start_persistence_module():
    add_log_entry("PersistenceModule", "Persistence module started.", "info")
    # TODO: Implement actual persistence logic here
    return {"status": "started", "detail": "Persistence module started."}

# Malware behavior module stub endpoint
@app.post("/api/malware_behavior/start")
def start_malware_behavior_module():
    add_log_entry("MalwareBehaviorGenerator", "Malware behavior module started.", "info")
    # TODO: Implement actual malware behavior logic here
    return {"status": "started", "detail": "Malware behavior module started."}

# Optionally add a simple GET endpoint to serve sample logs if needed
@app.get("/logs")
async def get_sample_logs():
    sample_logs = [
        {"timestamp": "2025-05-27T12:00:00Z", "level": "info", "message": "Started scan."},
        {"timestamp": "2025-05-27T12:00:01Z", "level": "warn", "message": "Low entropy detected."},
        {"timestamp": "2025-05-27T12:00:02Z", "level": "error", "message": "Process not found."},
    ]
    return sample_logs
