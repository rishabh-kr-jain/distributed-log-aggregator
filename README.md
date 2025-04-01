# Django Log Aggregator

A high-performance, memory-efficient **Log Aggregator** built using **Django**, supporting:

- In-memory log storage
- Time-based log queries
- Auto-purging logs older than 1 hour
- Efficient sorted insertion and retrieval using `bisect`
- Full thread safety and concurrency handling

---

## Project Structure
<pre> 
logservice/ # Django project (global settings) 
├── logservice/ # Project config: settings, URLs 
│ ├── settings.py 
│ ├── urls.py 
│ └── wsgi.py 
├── logs/ # Logs app (main business logic) 
│ ├── init.py # Registers app config 
│ ├── apps.py # Starts auto-purge background thread 
│ ├── urls.py # App-level routing (POST/GET /logs) 
│ └── views.py # GET/POST endpoints and in-memory storage 
└── README.md # You are here
</pre> 



## Features

| Feature                          | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| **Efficient Storage**         | Logs are inserted using `bisect.insort()` for sorted order                  |
| **Binary Search Retrieval**   | Uses `bisect.bisect_left/right` for fast time-range log queries             |
| **Thread Safe**               | Shared state protected using `threading.RLock`                              |
| **Auto Purging**              | Background thread removes logs older than 1 hour (runs every 60s)           |
| **Out-of-Order Support**      | Logs can arrive in any order — inserted into correct spot automatically     |
| **Custom GET Validations**    | Ensures `end >= start` and missing parameters are handled                   |


---

## Getting Started

### 1. Clone and Install

```bash
git clone [<your-repo-url>](https://github.com/rishabh-kr-jain/distributed-log-aggregator.git)
cd logservice
pip install django requests
2. Start the Django Server
python manage.py runserver
Server will be available at http://localhost:8000
```

##API Endpoints

POST Service
curl --location 'http://localhost:8000/logs' \
--header 'Content-Type: application/json' \
--data '{"service": "auth", "timestamp": "2025-03-31T22:00:00", "message": "User logged out"}'

GET Service
curl --location 'http://localhost:8000/logs?service=auth&start=2025-03-31T21%3A50%3A00&end=2025-03-30T23%3A00%3A00'

Dependencies
 Python 3.6+
 Django
