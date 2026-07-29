from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.etl_service.charts import build_dashboard_payload

app = FastAPI(title="Finance Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dashboard")
def dashboard():
    payload = build_dashboard_payload()
    return payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api_service.dashboard_api:app", host="0.0.0.0", port=5000, reload=True)
