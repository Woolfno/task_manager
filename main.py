from fastapi import APIRouter, FastAPI

from app.api.endpoins import authRouter, taskRouter

app = FastAPI()
apiRouter = APIRouter(prefix='/api')
apiRouter.include_router(taskRouter)
apiRouter.include_router(authRouter)
app.include_router(apiRouter)
