# Restaurant Recommendation UI (Next.js)

## Run the app

You need **two processes**:

### 1. Start the API (Terminal 1)

From the **project root** (parent of `web/`):

```bash
./start-api.sh
```

Or:

```bash
PYTHONPATH=. python phase2/api/main.py
```

Leave this running. The API will be at **http://localhost:8000**.

### 2. Start the Next.js UI (Terminal 2)

From the **project root**:

```bash
cd web
npm install
npm run dev
```

Then open in your browser:

**http://localhost:3000**

That’s your **working URL** for the UI. The UI will call the API at `http://localhost:8000` (set in `web/.env.local`).

If you see “API not reachable”, make sure the API is running in Terminal 1 and refresh the page.
