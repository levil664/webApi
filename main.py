from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from crud import get_product_categories, get_products

from database import engine, get_db
from endpoints import router_websocket, router_products, router_product_categories

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="WebApi",
    summary="WebApi",
)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, dp: Session = Depends(get_db)):
    http_protocol = request.headers.get("x-forwarded-proto", "http")
    ws_protocol = "wss" if http_protocol == "https" else "ws"
    server_urn = request.url.netloc
    products = get_products(dp, skip=0, limit=10)
    product_categories = get_product_categories(dp, skip=0, limit=10)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "http_protocol": http_protocol,
                                       "ws_protocol": ws_protocol,
                                       "products": products,
                                       "product_categories": product_categories,
                                       "server_urn": server_urn})


app.include_router(router_websocket)
app.include_router(router_product_categories)
app.include_router(router_products)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
