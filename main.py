from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from crud import get_product_categories, get_products
from database import engine, get_db
from endpoints import router_websocket, router_products, router_product_categories
from fastapi import applications
from fastapi.openapi.docs import get_swagger_ui_html
import httpx
from jinja2 import Template

def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css"
    )

applications.get_swagger_ui_html = swagger_monkey_patch

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WebApi",
    summary="WebApi",
)

async def fetch_template(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, dp: Session = Depends(get_db)):
    http_protocol = request.headers.get("x-forwarded-proto", "http")
    ws_protocol = "wss" if http_protocol == "https" else "ws"
    server_urn = request.url.netloc
    products = get_products(dp, skip=0, limit=10)
    product_categories = get_product_categories(dp, skip=0, limit=10)

    template_url = "https://storage.yandexcloud.net/template-fastapi/index.html"
    template_content = await fetch_template(template_url)

    template = Template(template_content)
    rendered_template = template.render(
        request=request,
        http_protocol=http_protocol,
        ws_protocol=ws_protocol,
        products=products,
        product_categories=product_categories,
        server_urn=server_urn
    )

    return HTMLResponse(content=rendered_template)

app.include_router(router_websocket)
app.include_router(router_product_categories)
app.include_router(router_products)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
