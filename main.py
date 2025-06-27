from app.api.endpoins import taskRouter
from fastapi import FastAPI, APIRouter


app = FastAPI()
apiRouter = APIRouter(prefix='/api')
apiRouter.include_router(taskRouter)
app.include_router(apiRouter)