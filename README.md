# NetWatch AI — Real-Time Network Anomaly Detection

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0-black)
![scikit--learn](https://img.shields.io/badge/scikit--learn-IsolationForest-orange)
![License](https://img.shields.io/badge/license-MIT-green)

> A live monitoring dashboard that watches network telemetry (latency, packet loss, bandwidth) and uses machine learning to automatically flag anomalies — instead of just plotting graphs and leaving a human to spot the problem.

## Live Demo

🚧 Coming Soon

The application will be deployed on AWS EC2 with continuous monitoring and real-time anomaly visualization.

**[Add your demo GIF or screenshot here once you run it locally]**

---

## Why I built this ?

During my networking internship, I spent time monitoring latency and packet-loss dashboards to identify potential issues. This project automates that workflow by learning normal network behavior and flagging unusual patterns in real time using machine learning.

## How it works ?

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌───────────┐
│  Data source │ --> │  SQLite store │ --> │ Anomaly Engine  │ --> │ Dashboard │
│ (simulated / │     │  (metrics log)│     │ (IsolationForest│     │ (Flask +  │
│  live probes)│     │               │     │  + rolling stats)     │  Chart.js)│
└─────────────┘     └──────────────┘     └────────────────┘     └───────────┘
```

1. **Data collection** — a background thread generates network metrics every few seconds    (swap this for real ICMP pings / SNMP polling / router logs in production).

2. **Storage** — every reading is logged to SQLite with a timestamp.

3. **Detection** — each new point is scored two ways:

   - **Rolling statistics** (z-score against recent mean/std) — used on cold start, fully explainable.

   - **Isolation Forest** (`scikit-learn`) — once enough history exists, this unsupervised model learns the normal multi-dimensional pattern across latency + packet loss + bandwidth together, and flags points that don't fit — catching subtler, combined anomalies a single-metric threshold would miss.

4. **Dashboard** — a live-updating web UI shows real-time charts with anomalies highlighted, plus a scrolling event feed.


## Tech stack

- **Backend:** Python, Flask
- **ML:** scikit-learn (`IsolationForest`)
- **Storage:** SQLite
- **Frontend:** HTML/CSS/JS, Chart.js

## Features

- 📡 Real-time network telemetry monitoring
- 🤖 Machine Learning-based anomaly detection using Isolation Forest
- 📊 Live interactive charts with Chart.js
- 📈 Continuous background data simulation
- 🚨 Automatic anomaly event feed
- 🗄️ SQLite database for historical metrics
- 🌐 REST API built with Flask

## Getting started

```bash
git clone https://github.com/thaparekha9868-png/NETWATCH-by-REKHA.git
cd NETWATCH-by-REKHA
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:8000** — the dashboard seeds itself with historical data and starts streaming live anomaly-scored metrics automatically.

## Project structure

```
network-anomaly-ai/
├── app.py                 # Flask app + background data loop
├── core/
│   ├── database.py         # SQLite schema & queries
│   ├── simulator.py        # Synthetic network telemetry generator
│   └── detector.py         # RollingStats + IsolationForest anomaly engine
├── templates/
│   └── dashboard.html      # Live monitoring UI
├── requirements.txt
└── README.md
```

## Roadmap

- [ ] Swap simulator for real ICMP/SNMP polling
- [ ] Slack/email webhook alerts on anomaly detection
- [ ] Deploy to AWS EC2 (free tier) with S3 for historical log archiving
- [ ] Configurable sensitivity per network segment

## Built by
 **Rekha Thapa** — BSc CSIT graduate with a background in **computer networking, Python development, and cloud technologies**.

Interested in building intelligent systems using **AI, automation, and network security concepts**.

🔗 [LinkedIn](https://www.linkedin.com/in/rekhaa-thapa-657aa3369) · 
🔗 [GitHub](https://github.com/thaparekha9868-png)