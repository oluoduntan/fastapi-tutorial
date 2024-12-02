from fastapi import FastAPI, status
from .routers import auth, todos, admin, user
from .models import Base
from .database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

@app.get("/healthy", status_code=status.HTTP_200_OK)
def healthy():
    return {"status": "Healthy"}