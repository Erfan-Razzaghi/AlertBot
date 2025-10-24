from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from alertbot import env, startup
from alertbot.prometheus_endpoint import prom
from alertbot.splunk_endpoint import splunk
from alertbot.test_endpoint import tests
from utils.logger import setup_logging
import uvicorn


app = FastAPI(
    lifespan=startup.lifespan,
    title="Alertbot",
    description="Sending Alerts to Proper Destinations.",
    version="2.0.0",
    docs_url="/docs" if env.ENVIRONMENT == "STAGING" else None,
    redoc_url="/redoc" if env.ENVIRONMENT == "STAGING" else None
) 

Instrumentator().instrument(app).expose(app)

app.include_router(prom.router)
app.include_router(splunk.router)
if env.ENVIRONMENT == "STAGING":
    app.include_router(tests.router)

@app.get("/")
async def root():
    return {"message": "Hello World From Alertbot"}

if __name__ == "__main__":
    logger = setup_logging()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)