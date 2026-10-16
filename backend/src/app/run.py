import uvicorn

from app.core.config import settings
from app.main import app

if __name__ == "__main__":
    # Access lines come from ObservabilityMiddleware (with trace id), so uvicorn's own are off.
    uvicorn.run(app, host=settings.run.host, port=settings.run.port, access_log=False, log_config=None)
