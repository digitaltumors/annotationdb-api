from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routes.drugs import router as drugs_router
from routes.cell_lines import router as cell_lines_router

app = FastAPI()
app.include_router(drugs_router)
app.include_router(cell_lines_router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
