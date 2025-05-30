const API_BASE_URL = "http://localhost:8000";

export async function scanMemory(pattern: string, process: string, pid?: number) {
  const params = new URLSearchParams();
  if (pattern) params.append("pattern", pattern);
  if (process) params.append("process", process);
  if (pid) params.append("pid", pid.toString());

  const response = await fetch(`${API_BASE_URL}/scan?${params.toString()}`, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error("Failed to scan memory");
  }

  return response.json();
}

export async function getLogs() {
  const response = await fetch(`${API_BASE_URL}/logs`, { method: "GET" });
  if (!response.ok) {
    throw new Error("Failed to fetch logs");
  }
  return response.json();
}
