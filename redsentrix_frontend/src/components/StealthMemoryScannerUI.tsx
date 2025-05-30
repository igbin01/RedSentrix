<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RedSentrix Stealth Scanner</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    // Load PIDs from backend and populate dropdown
    function fetchPIDs() {
      fetch("/get-pids")
        .then((res) => res.json())
        .then((data) => {
          const pidSelect = document.getElementById("pid");
          pidSelect.innerHTML = "";
          data.pids.forEach((pid) => {
            const option = document.createElement("option");
            option.value = pid;
            option.textContent = pid;
            pidSelect.appendChild(option);
          });
        });
    }

    function toggleDarkMode() {
      document.documentElement.classList.toggle("dark");
    }

    // State variables to hold UI state and data
    let scanResults = [];
    let logs = [];
    let filteredLogs = [];
    let error = null;

    // Utility to display error message
    function showError(msg) {
      const errorElem = document.getElementById("error-message");
      if (msg) {
        errorElem.textContent = msg;
        errorElem.style.display = "block";
      } else {
        errorElem.textContent = "";
        errorElem.style.display = "none";
      }
    }

    // Update scan results UI
    function updateScanResults() {
      const ul = document.getElementById("scan-results");
      ul.innerHTML = "";
      scanResults.forEach((result, i) => {
        const li = document.createElement("li");
        li.textContent = typeof result === "string" ? result : JSON.stringify(result);
        ul.appendChild(li);
      });
    }

    // Update logs UI (all logs)
    function updateLogs() {
      filteredLogs = logs; // reset filtered logs to all logs
      renderFilteredLogs();
    }

    // Render filtered logs to the logs list
    function renderFilteredLogs() {
      const ul = document.getElementById("logs-list");
      ul.innerHTML = "";
      if (filteredLogs.length > 0) {
        filteredLogs.forEach((log, i) => {
          const li = document.createElement("li");
          li.textContent = typeof log === "string" ? log : JSON.stringify(log);
          ul.appendChild(li);
        });
      } else {
        const li = document.createElement("li");
        li.textContent = "No logs match your filter.";
        ul.appendChild(li);
      }
    }

    // Filter logs based on input value
    function filterLogs() {
      const filterKeyword = document.getElementById("filter-logs-input").value.toLowerCase();
      filteredLogs = logs.filter(log => log.toLowerCase().includes(filterKeyword));
      renderFilteredLogs();
    }

    // Call API to start scan
    async function startScan() {
      showError(null);

      const pattern = document.getElementById("pattern").value.trim();
      const process = document.getElementById("process").value.trim();
      const pidVal = document.getElementById("pid").value;
      const pid = pidVal ? Number(pidVal) : undefined;

      try {
        const response = await fetch("/api/scan-memory", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pattern, process, pid }),
        });
        if (!response.ok) throw new Error(`Scan failed: ${response.statusText}`);

        const results = await response.json();
        scanResults = results;
        updateScanResults();
      } catch (e) {
        showError(e.message);
      }
    }

    // Call API to load logs
    async function loadLogs() {
      try {
        const response = await fetch("/api/get-logs");
        if (!response.ok) throw new Error("Failed to load logs");

        const logsData = await response.json();
        logs = logsData;
        updateLogs();
      } catch (e) {
        showError(e.message);
      }
    }

    window.onload = () => {
      fetchPIDs();
      // Attach filter input event listener
      document.getElementById("filter-logs-input").addEventListener("input", filterLogs);
    };
  </script>
</head>
<body class="bg-white dark:bg-gray-900 text-black dark:text-white font-sans p-6">
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-4">RedSentrix Stealth Memory Scanner</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block mb-1" for="pid">PID</label>
        <select id="pid" class="w-full p-2 border dark:bg-gray-700 dark:border-gray-600"></select>
      </div>
      <div>
        <label class="block mb-1" for="pattern">Pattern</label>
        <input
          type="text"
          id="pattern"
          placeholder="Pattern string"
          class="w-full p-2 border dark:bg-gray-700 dark:border-gray-600"
        />
      </div>
      <div>
        <label class="block mb-1" for="process">Process Name</label>
        <input
          type="text"
          id="process"
          placeholder="Process name"
          class="w-full p-2 border dark:bg-gray-700 dark:border-gray-600"
        />
      </div>
    </div>

    <div class="mt-4 flex gap-2">
      <button
        onclick="startScan()"
        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
      >
        Start Scan
      </button>
      <button
        onclick="loadLogs()"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
      >
        Load Logs
      </button>
      <button
        onclick="toggleDarkMode()"
        class="ml-auto bg-gray-800 hover:bg-gray-900 text-white px-4 py-2 rounded"
      >
        Toggle Dark Mode
      </button>
    </div>

    <p
      id="error-message"
      style="color: red; margin-top: 0.5rem; display: none;"
    ></p>

    <h3 class="mt-6 font-semibold text-lg">Scan Results</h3>
    <ul id="scan-results" class="list-disc list-inside mb-6"></ul>

    <h3 class="font-semibold text-lg">Logs</h3>
    <input
      type="text"
      id="filter-logs-input"
      placeholder="Filter logs..."
      class="w-full p-2 mb-2 border dark:bg-gray-700 dark:border-gray-600 dark:text-white"
      style="max-width: 400px;"
    />
    <ul
      id="logs-list"
      class="list-disc list-inside border p-4 max-h-72 overflow-y-auto dark:bg-gray-800 dark:text-green-400"
    ></ul>
  </div>
</body>
</html>
