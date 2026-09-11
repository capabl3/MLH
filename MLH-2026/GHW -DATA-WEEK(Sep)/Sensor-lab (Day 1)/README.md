# Sensor Lab

A fast, lightweight API and dashboard for time-series sensor data, built with [FastAPI](https://fastapi.tiangolo.com/), [Tiger Data](https://www.tigerdata.com/), and managed using [uv](https://github.com/astral-sh/uv).

## 🚀 Quick Start

### 1. Project Initialization & Dependencies
This project is managed using the `uv` package manager. 

**Important Note on Initialization:** To prevent `uv` from attempting to build the project as a standard Python wheel (which causes a `src/<module>/__init__.py` build error), the project must be initialized with the `--no-package` flag.

```bash
# Initialize without building as a package
uv init --no-package sensor-lab
cd sensor-lab

# Install dependencies
uv add "timescaledb[fastapi]" "psycopg[binary]" python-dotenv

```

### 2. Environment Configuration

Create a `.env` file in the root directory of your project to store your Tiger Data database credentials.

**Important Note on the Connection String:**
When you copy your connection string from the Tiger Data cloud console, it will likely start with `postgres://` or `postgresql://`. Because this project uses the newer `psycopg` (v3) driver with SQLAlchemy, you **must** change the prefix to `postgresql+psycopg://` to avoid module errors.

```ini
# .env
# Replace with your actual Tiger Data credentials
DATABASE_URL="postgresql+psycopg://<username>:<password>@<your-host-id>.cloud.tigerdata.com:<port>/<dbname>"

```

### 3. Running the Server

Start the FastAPI application using `uvicorn`:

```bash
uv run uvicorn main:app --reload

```

## 🌐 Application Endpoints

Once the server is running locally, you can access the following web interfaces:

* **Dashboard:** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to view the live sensor chart and use the database seed button.
* **API Documentation:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to view the automatically generated, interactive API documentation (Swagger UI).

## 🧪 Then try it (Linux / macOS / Git Bash)

You can test the API endpoints using standard `curl` commands:

```bash
curl -X POST [http://127.0.0.1:8000/seed](http://127.0.0.1:8000/seed)                 # 500 readings across the last week

curl -X POST [http://127.0.0.1:8000/readings](http://127.0.0.1:8000/readings) \
  -H 'content-type: application/json' \
  -d '{"machine_id":2,"vibration":1.8,"power":3.7}'

curl '[http://127.0.0.1:8000/readings?machine_id=2](http://127.0.0.1:8000/readings?machine_id=2)'

curl '[http://127.0.0.1:8000/readings/trend?machine_id=2](http://127.0.0.1:8000/readings/trend?machine_id=2)'

```

## 🪟 Testing via Windows PowerShell

If you are using Windows PowerShell to test `POST` requests, standard Linux `curl` commands with `-X` or JSON bodies containing escaped quotes (`\"`) will throw errors. It is recommended to use PowerShell's native `Invoke-RestMethod` to handle JSON cleanly.

**Seed the database:**

```powershell
Invoke-RestMethod -Method POST -Uri [http://127.0.0.1:8000/seed](http://127.0.0.1:8000/seed)

```

**Post a new reading:**

```powershell
Invoke-RestMethod -Method POST -Uri [http://127.0.0.1:8000/readings](http://127.0.0.1:8000/readings) -ContentType "application/json" -Body '{"machine_id":2,"vibration":1.8,"power":3.7}'

```

**Get readings for a machine:**

```powershell
Invoke-RestMethod -Uri [http://127.0.0.1:8000/readings?machine_id=2](http://127.0.0.1:8000/readings?machine_id=2)

```

**Get the trend for a machine:**

```powershell
Invoke-RestMethod -Uri [http://127.0.0.1:8000/readings/trend?machine_id=2](http://127.0.0.1:8000/readings/trend?machine_id=2)

```

```