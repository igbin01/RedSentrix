from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import threading
import time
import re

app = FastAPI(title="RedSentrix Backend API")

# CORS setup for frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models

class LogEntry(BaseModel):
    timestamp: float
    module: Optional[str] = None
    message: str
    level: str

class ScanRequest(BaseModel):
    pattern: Optional[str] = None
    process_name: Optional[str] = None
    pid: Optional[int] = None
    encoding: Optional[str] = None
    key: Optional[str] = None
    entropy_mode: bool = False
    yara_path: Optional[str] = None
    output_path: Optional[str] = None

# Logger class that stores logs in-memory with filtering and pagination

class StealthLogger:
    def __init__(self):
        self.logs_store: List[dict] = []

    def add_log_entry(self, module: str, message: str, level: str = "info"):
        self.logs_store.append({
            "timestamp": time.time(),
            "module": module,
            "message": message,
            "level": level,
        })

    def get_logs(
        self,
        module: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        filtered_logs = self.logs_store

        if module:
            filtered_logs = [log for log in filtered_logs if log["module"].lower() == module.lower()]
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"].lower() == level.lower()]
        if search:
            filtered_logs = [log for log in filtered_logs if search.lower() in log["message"].lower()]
        if start_time or end_time:
            def in_range(log):
                ts = datetime.fromtimestamp(log["timestamp"])
                if start_time and ts < start_time:
                    return False
                if end_time and ts > end_time:
                    return False
                return True
            filtered_logs = [log for log in filtered_logs if in_range(log)]

        # Sort newest first
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)

        total = len(filtered_logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_logs = filtered_logs[start_idx:end_idx]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "logs": paged_logs,
        }

logger = StealthLogger()

# Helper to parse ISO datetime string, returns None if invalid
def parse_iso(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

# Simulated stealth scan worker running in a background thread
def stealth_scan_worker(scan_params: ScanRequest):
    logger.add_log_entry("StealthMemoryScanner", "Stealth memory scan started.", "info")
    time.sleep(5)  # Simulate scanning delay
    target = scan_params.process_name or str(scan_params.pid) or "unknown"
    logger.add_log_entry("StealthMemoryScanner", f"Stealth memory scan finished for target: {target}", "info")

# API endpoints

@app.post("/api/scan")
def start_stealth_scan(scan_params: ScanRequest):
    threading.Thread(target=stealth_scan_worker, args=(scan_params,), daemon=True).start()
    return {"status": "started", "detail": "Stealth memory scan initiated."}

@app.get("/api/logs", response_model=dict)
def get_logs(
    module: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None, description="ISO datetime start filter"),
    end_time: Optional[str] = Query(None, description="ISO datetime end filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    start_dt = parse_iso(start_time)
    end_dt = parse_iso(end_time)

    return logger.get_logs(module, level, search, start_dt, end_dt, page, page_size)

@app.post("/api/persistence/start")
def start_persistence_module():
    logger.add_log_entry("PersistenceModule", "Persistence module started.", "info")
    # TODO: Implement actual persistence logic here
    return {"status": "started", "detail": "Persistence module started."}

@app.post("/api/malware_behavior/start")
def start_malware_behavior_module():
    logger.add_log_entry("MalwareBehaviorGenerator", "Malware behavior module started.", "info")
    # TODO: Implement actual malware behavior logic here
    return {"status": "started", "detail": "Malware behavior module started."}
