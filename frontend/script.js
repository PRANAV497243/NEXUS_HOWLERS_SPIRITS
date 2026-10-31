/**
 * PROJECT NEXUS — Frontend Logic Controller
 * Developed by Pranav, AI & DE Branch
 */

document.addEventListener("DOMContentLoaded", () => {
  const solveBtn = document.getElementById("solve-btn");
  const queryInput = document.getElementById("query-input");
  const autoApproveToggle = document.getElementById("auto-approve-toggle");
  const voiceBtn = document.getElementById("voice-btn");
  const streamLog = document.getElementById("stream-log");
  const resultBody = document.getElementById("result-body");
  const downloadDocxBtn = document.getElementById("download-docx-btn");
  const activityCounter = document.getElementById("activity-counter");
  const systemStatus = document.getElementById("system-status");

  const agentNodes = {
    planner: document.getElementById("node-planner"),
    researcher: document.getElementById("node-researcher"),
    analyst: document.getElementById("node-analyst"),
    critic: document.getElementById("node-critic"),
    writer: document.getElementById("node-writer"),
  };

  const statusLabels = {
    planner: document.getElementById("status-planner"),
    researcher: document.getElementById("status-researcher"),
    analyst: document.getElementById("status-analyst"),
    critic: document.getElementById("status-critic"),
    writer: document.getElementById("status-writer"),
  };

  let eventCount = 0;

  function updateAgentFleet(activeAgent) {
    Object.keys(agentNodes).forEach((agent) => {
      if (agent === activeAgent) {
        agentNodes[agent].classList.add("active");
        if (statusLabels[agent]) statusLabels[agent].innerText = "Executing...";
      } else {
        agentNodes[agent].classList.remove("active");
        if (statusLabels[agent] && statusLabels[agent].innerText === "Executing...") {
          statusLabels[agent].innerText = "Done";
        }
      }
    });
  }

  function appendLogMessage(msg) {
    eventCount++;
    activityCounter.innerText = `${eventCount} events`;
    if (streamLog.querySelector(".empty-state")) {
      streamLog.innerHTML = "";
    }

    const entry = document.createElement("div");
    entry.className = "log-entry";
    entry.innerHTML = `
      <div class="log-meta">
        <strong>${msg.agent.toUpperCase()}</strong>
        <span>${msg.timestamp ? msg.timestamp.slice(11, 19) : ""}</span>
      </div>
      <div>${msg.message}</div>
    `;
    streamLog.appendChild(entry);
    streamLog.scrollTop = streamLog.scrollHeight;
  }

  async function startWorkflow() {
    const query = queryInput.value.trim();
    if (!query) {
      alert("Please enter a problem statement or inquiry.");
      return;
    }

    solveBtn.disabled = true;
    solveBtn.innerHTML = `<span>Synthesizing Fleet...</span>`;
    systemStatus.innerHTML = `<span class="dot" style="background:#f59e0b; box-shadow:0 0 8px #f59e0b;"></span> Solving Task`;
    resultBody.innerHTML = `<div class="empty-state">Agents collaborating... Please wait while multi-agent synthesis executes.</div>`;
    downloadDocxBtn.classList.add("hidden");

    try {
      const response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          auto_approve: autoApproveToggle.checked,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update UI with logs
      if (data.agent_messages) {
        streamLog.innerHTML = "";
        data.agent_messages.forEach((m) => appendLogMessage(m));
      }

      // Render Final Report
      if (data.final_report) {
        resultBody.innerText = data.final_report.markdown || data.final_report.executive_summary;
      }

      // Handle Docx Download
      if (data.docx_path) {
        const parts = data.docx_path.split(/[\\/]/);
        const filename = parts[parts.length - 1];
        downloadDocxBtn.href = `/api/download/${filename}`;
        downloadDocxBtn.classList.remove("hidden");
      }

      systemStatus.innerHTML = `<span class="dot" style="background:#10b981; box-shadow:0 0 8px #10b981;"></span> Problem Solved`;
      Object.keys(statusLabels).forEach((k) => (statusLabels[k].innerText = "Completed"));
    } catch (err) {
      alert("Workflow execution failed: " + err.message);
      systemStatus.innerHTML = `<span class="dot" style="background:#ef4444; box-shadow:0 0 8px #ef4444;"></span> Failed`;
    } finally {
      solveBtn.disabled = false;
      solveBtn.innerHTML = `<span>Execute Multi-Agent Workflow</span><span class="btn-arrow">→</span>`;
    }
  }

  solveBtn.addEventListener("click", startWorkflow);

  // Web Speech API Voice Recognition
  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    voiceBtn.addEventListener("click", () => {
      voiceBtn.innerText = "Listening...";
      recognition.start();
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      queryInput.value = transcript;
      voiceBtn.innerText = "🎙️ Voice";
    };

    recognition.onerror = () => {
      voiceBtn.innerText = "🎙️ Voice";
    };
  } else {
    voiceBtn.addEventListener("click", () => {
      alert("Speech recognition is not natively supported in this browser. Please type your prompt.");
    });
  }
});
