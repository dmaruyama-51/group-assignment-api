from fastapi import FastAPI
from api.routers import assign

app = FastAPI()

app.include_router(assign.router)


@app.get("/hello")
async def hello():
    return {"message": "hello world!"}
