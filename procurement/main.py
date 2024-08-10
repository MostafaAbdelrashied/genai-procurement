import uvicorn
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from procurement.api.api_router import api_router
from procurement.utils.config import get_settings


def custom_generate_unique_id(route: APIRouter):
    return route.name


app = FastAPI(
    title="ubs-sc-genai chatbot",
    docs_url="/docs",
    generate_unique_id_function=custom_generate_unique_id,
)

templates = Jinja2Templates(directory="server/templates")
# Mount the static directory
app.mount("/static", StaticFiles(directory="server/static"), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """
    Expose static template

    @param request:
    @return:
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_root": get_settings().app_config.app_root},
    )


# Include application routers
app.include_router(api_router)

# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8089,
        reload=True,
        reload_includes=["*.js", "*.html", "*.css"],
    )


if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8089,
        reload=True,
        reload_includes=["*.js", "*.html", "*.css"],
    )
