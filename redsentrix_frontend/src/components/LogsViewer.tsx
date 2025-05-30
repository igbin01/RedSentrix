import React, { useState, useEffect } from "react";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export const LogsViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState("");
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch logs from backend API
  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/logs"); // adjust if needed
      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      const data: LogEntry[] = await res.json();
      setLogs(data);
      setFilteredLogs(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch logs");
    } finally {
      setLoading(false);
    }
  };

  // Effect: fetch logs on component mount
  useEffect(() => {
    fetchLogs();
  }, []);

  // Effect: filter logs when `filter` or `logs` change
  useEffect(() => {
    if (!filter) {
      setFilteredLogs(logs);
      return;
    }
    const lowerFilter = filter.toLowerCase();
    setFilteredLogs(
      logs.filter(
        (log) =>
          log.message.toLowerCase().includes(lowerFilter) ||
          log.level.toLowerCase().includes(lowerFilter) ||
          log.timestamp.toLowerCase().includes(lowerFilter)
      )
    );
  }, [filter, logs]);

  return (
    <div style={{ padding: 20 }}>
      <h2>RedSentrix Logs Viewer</h2>

      <input
        type="text"
        placeholder="Filter logs by keyword..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        style={{ padding: 8, width: "100%", marginBottom: 10, fontSize: 16 }}
      />

      {loading && <p>Loading logs...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div
        style={{
          maxHeight: "400px",
          overflowY: "scroll",
          backgroundColor: "#222",
          color: "#eee",
          padding: 10,
          borderRadius: 4,
          fontFamily: "monospace",
          fontSize: 14,
        }}
      >
        {filteredLogs.length === 0 && !loading && <p>No logs found.</p>}

        {filteredLogs.map((log, idx) => (
          <div key={idx} style={{ marginBottom: 6 }}>
            <span style={{ color: "#888" }}>[{log.timestamp}] </span>
            <span
              style={{
                color:
                  log.level.toLowerCase() === "error"
                    ? "red"
                    : log.level.toLowerCase() === "warn"
                    ? "orange"
                    : "lightgreen",
                fontWeight: "bold",
              }}
            >
              {log.level.toUpperCase()}
            </span>
            <span>: {log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogsViewer;
