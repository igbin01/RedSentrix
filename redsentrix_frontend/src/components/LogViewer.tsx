import React, { useState, useEffect } from "react";

type LogEntry = {
  timestamp: string;
  level: string;
  message: string;
};

const LogViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [level, setLevel] = useState<string>("");
  const [keyword, setKeyword] = useState<string>("");
  const [startTime, setStartTime] = useState<string>("");
  const [endTime, setEndTime] = useState<string>("");

  const fetchLogs = async () => {
    const params = new URLSearchParams();
    if (level) params.append("level", level);
    if (keyword) params.append("keyword", keyword);
    if (startTime) params.append("start_time", startTime);
    if (endTime) params.append("end_time", endTime);
    params.append("page", page.toString());
    params.append("page_size", pageSize.toString());

    const resp = await fetch(`http://localhost:8000/logs?${params.toString()}`);
    const data = await resp.json();
    setLogs(data.logs);
    setTotal(data.total);
  };

  useEffect(() => {
    fetchLogs();
  }, [page, level, keyword, startTime, endTime]);

  return (
    <div>
      <h2>Log Viewer</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          Level:{" "}
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="">All</option>
            <option value="info">Info</option>
            <option value="warn">Warn</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>
        </label>

        <label style={{ marginLeft: "1rem" }}>
          Keyword:{" "}
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Search message"
          />
        </label>

        <label style={{ marginLeft: "1rem" }}>
          Start Time:{" "}
          <input
            type="datetime-local"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
          />
        </label>

        <label style={{ marginLeft: "1rem" }}>
          End Time:{" "}
          <input
            type="datetime-local"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
          />
        </label>
      </div>

      <table border={1} cellPadding={5} style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Level</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 && (
            <tr>
              <td colSpan={3} style={{ textAlign: "center" }}>
                No logs found.
              </td>
            </tr>
          )}
          {logs.map((log, idx) => (
            <tr key={idx}>
              <td>{log.timestamp}</td>
              <td>{log.level}</td>
              <td>{log.message}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "1rem" }}>
        <button onClick={() => setPage(p => Math.max(p - 1, 1))} disabled={page === 1}>
          Previous
        </button>
        <span style={{ margin: "0 1rem" }}>
          Page {page} / {Math.ceil(total / pageSize)}
        </span>
        <button
          onClick={() => setPage(p => (p * pageSize < total ? p + 1 : p))}
          disabled={page * pageSize >= total}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default LogViewer;
