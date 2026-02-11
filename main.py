from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from routes.drugs import router as drugs_router
from routes.cell_lines import router as cell_lines_router
from fastapi.staticfiles import StaticFiles
from data.description import DESCRIPTION

app = FastAPI(
    title="AnnotationDB API",
    description=DESCRIPTION,
    version="0.1.0",
    docs_url=None,
)

app.include_router(drugs_router)
app.include_router(cell_lines_router)

app.mount("/styling", StaticFiles(directory="styling"), name="styling")


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="AnnotationDB API",
        swagger_favicon_url="/assets/favicon.ico",
        swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
        swagger_js_url="/styling/swagger.js",
        swagger_css_url="/styling/swagger.css",
    )


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
