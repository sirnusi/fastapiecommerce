from fastapi import FastAPI, Depends

from routers import products, auth, orders, categories, rating
import models


from database import engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API", version="1.0")
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(rating.router)

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}

