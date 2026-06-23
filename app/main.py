from fastapi import FastAPI
from app.database import engine, Base
from app.routers import customers, pets, orders, billing

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="宠物寄养小店管理系统",
    description="客户管理、宠物档案、寄养订单、收费结算 API",
    version="1.0.0",
)

app.include_router(customers.router)
app.include_router(pets.router)
app.include_router(orders.router)
app.include_router(billing.router)


@app.get("/")
def root():
    return {"message": "宠物寄养小店管理系统 API 已启动"}
