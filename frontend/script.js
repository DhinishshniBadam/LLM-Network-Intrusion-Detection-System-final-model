const SAMPLE = {
    "url": "/login.php?id=' OR 1=1 --",
    "payload": "username=admin' --&password=test",
    "headers": {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    "network_features": {
        "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "SF",
        "src_bytes": 512, "dst_bytes": 124, "land": 0, "wrong_fragment": 0,
        "urgent": 0, "hot": 1, "num_failed_logins": 3, "logged_in": 0,
        "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0,
        "num_file_creations": 0, "num_shells": 0, "num_access_files": 0,
        "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0,
        "count": 15, "srv_count": 12, "serror_rate": 0.4, "srv_serror_rate": 0.3,
        "rerror_rate": 0.2, "srv_rerror_rate": 0.1, "same_srv_rate": 0.9,
        "diff_srv_rate": 0.1, "srv_diff_host_rate": 0.2, "dst_host_count": 120,
        "dst_host_srv_count": 100, "dst_host_same_srv_rate": 0.85,
        "dst_host_diff_srv_rate": 0.15, "dst_host_same_src_port_rate": 0.7,
        "dst_host_srv_diff_host_rate": 0.2, "dst_host_serror_rate": 0.3,
        "dst_host_srv_serror_rate": 0.2, "dst_host_rerror_rate": 0.1,
        "dst_host_srv_rerror_rate": 0.1
    }
};

let history = [];
let counter = 1;

function loadSample() {
    document.getElementById("inputData").value = JSON.stringify(SAMPLE, null, 2);
}

async function checkAPI() {
    try {
        const res = await fetch("http://127.0.0.1:8000/");
        const data = await res.json();
        document.getElementById("apiStatus").textContent = data.status === "running" ? "Online ✓" : "Error";
        document.getElementById("apiStatus").style.color = "var(--success)";
    } catch {
        document.getElementById("apiStatus").textContent = "Offline ✗";
        document.getElementById("apiStatus").style.color = "var(--danger)";
    }
}

async function predict() {
    const input = document.getElementById("inputData").value;
    let data;

    try {
        data = JSON.parse(input);
    } catch {
        alert("Invalid JSON. Use the 'Load Sample' button to see the expected format.");
        return;
    }

    const btn = document.getElementById("analyzeBtn");
    const btnText = document.getElementById("btnText");
    btn.disabled = true;
    btnText.textContent = "Analyzing...";

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        showResult(result);
        addHistory(result);
    } catch (e) {
        alert("Could not reach the API. Make sure the server is running.");
    } finally {
        btn.disabled = false;
        btnText.textContent = "Analyze Traffic";
    }
}

function showResult(result) {
    document.getElementById("placeholder").classList.add("hidden");
    document.getElementById("resultContent").classList.remove("hidden");

    const banner = document.getElementById("alertBanner");
    banner.className = "alert-banner";
    if (result.prediction === "anomaly" && result.confidence >= 0.75) {
        banner.classList.add("alert-anomaly");
    } else if (result.confidence < 0.75) {
        banner.classList.add("alert-suspicious");
    } else {
        banner.classList.add("alert-normal");
    }

    document.getElementById("alertText").textContent = result.alert + "  " + result.action;
    document.getElementById("resPrediction").textContent = result.prediction.toUpperCase();
    document.getElementById("resConfidence").textContent = (result.confidence * 100).toFixed(2) + "%";
    document.getElementById("resRisk").textContent = result.risk_score;

    // show attack type and detection method if present
    const extraInfo = document.getElementById("resExtra");
    if (result.attack_type || result.detection) {
        extraInfo.classList.remove("hidden");
        extraInfo.innerHTML =
            (result.attack_type ? `<span class="tag tag-anomaly">${result.attack_type}</span>` : "") +
            (result.detection   ? `<span class="tag tag-suspicious" style="margin-left:8px">${result.detection}</span>` : "");
    } else {
        extraInfo.classList.add("hidden");
    }

    const bar = document.getElementById("riskBar");
    bar.style.width = result.risk_score + "%";
    bar.style.background = result.risk_score > 75 ? "var(--danger)" :
                           result.risk_score > 50 ? "var(--warning)" : "var(--success)";
}

function addHistory(result) {
    const tbody = document.getElementById("historyBody");
    if (counter === 1) tbody.innerHTML = "";

    const tagClass = result.prediction === "anomaly" ? "tag-anomaly" :
                     result.confidence < 0.75 ? "tag-suspicious" : "tag-normal";

    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${counter++}</td>
        <td>${new Date().toLocaleTimeString()}</td>
        <td>${result.prediction.toUpperCase()}</td>
        <td>${(result.confidence * 100).toFixed(2)}%</td>
        <td>${result.risk_score}/100</td>
        <td><span class="tag ${tagClass}">${result.alert}</span></td>
        <td>${result.attack_type ? `<span class="tag tag-anomaly">${result.attack_type}</span>` : "—"}</td>
    `;
    tbody.prepend(row);
}

function clearHistory() {
    counter = 1;
    document.getElementById("historyBody").innerHTML = '<tr><td colspan="6" class="empty-row">No analyses yet</td></tr>';
}

checkAPI();
