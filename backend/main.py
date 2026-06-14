from api.v1.routers import router_neurotest
from fastapi import FastAPI
from uvicorn import run

app = FastAPI(title="NeuroTest")
app.include_router(router_neurotest)

if __name__ == "__main__":
    run(app=app, host="0.0.0.0", port=8000)
