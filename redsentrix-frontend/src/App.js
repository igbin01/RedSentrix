import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [logs, setLogs] = useState([]);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("");
  const [module, setModule] = useState("");
  const [theme, setTheme] = useState("dark");
  const [scanTarget, setScanTarget] = useState("");

  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/api/logs", {
        params: {
          search: search || undefined,
          level: level || undefined,
          module: module || undefined,
          limit: 100,
        },
      });
      setLogs(res.data);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    }
  };

  const startScan = async () => {
    try {
      await axios.post("http://localhost:8000/api/scan", {
        process_name: scanTarget,
      });
      alert("Scan started for " + scanTarget);
    } catch (err) {
      console.error("Scan failed:", err);
      alert("Scan failed.");
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className={`min-h-screen ${theme === "dark" ? "bg-gray-900 text-white" : "bg-white text-black"} p-4`}>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">🛡️ RedSentrix Dashboard</h1>
        <button
          onClick={toggleTheme}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Toggle {theme === "dark" ? "Light" : "Dark"} Mode
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <input
          className="p-2 border rounded"
          placeholder="Search keyword"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <input
          className="p-2 border rounded"
          placeholder="Module (e.g. StealthMemoryScanner)"
          value={module}
          onChange={(e) => setModule(e.target.value)}
        />
        <select className="p-2 border rounded" value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="">All Levels</option>
          <option value="info">Info</option>
          <option value="debug">Debug</option>
          <option value="error">Error</option>
        </select>
        <button
          className="bg-blue-600 text-white rounded p-2 hover:bg-blue-700"
          onClick={fetchLogs}
        >
          Refresh Logs
        </button>
      </div>

      <div className="mb-6 flex gap-2">
        <input
          className="p-2 border rounded w-full"
          placeholder="Process name to scan"
          value={scanTarget}
          onChange={(e) => setScanTarget(e.target.value)}
        />
        <button
          className="bg-green-600 text-white rounded px-4 hover:bg-green-700"
          onClick={startScan}
        >
          Start Scan
        </button>
      </div>

      <div className="overflow-auto border rounded shadow-md">
        <table className="w-full text-left">
          <thead className="bg-gray-800 text-white">
            <tr>
              <th className="p-2">Time</th>
              <th className="p-2">Module</th>
              <th className="p-2">Level</th>
              <th className="p-2">Message</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 && (
              <tr>
                <td className="p-2 text-center" colSpan="4">
                  No logs available.
                </td>
              </tr>
            )}
            {logs.map((log, index) => (
              <tr key={index} className="border-t border-gray-700">
                <td className="p-2 text-sm">
                  {new Date(log.timestamp * 1000).toLocaleTimeString()}
                </td>
                <td className="p-2 text-sm">{log.module}</td>
                <td className="p-2 text-sm font-semibold">{log.level.toUpperCase()}</td>
                <td className="p-2 text-sm">{log.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;

