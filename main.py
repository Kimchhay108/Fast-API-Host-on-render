from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from pydantic import BaseModel
from typing import List
from supabase_client import supabase
import uuid

app = FastAPI(title="Product API")

# -----------------------------
# Pydantic models
# -----------------------------
class Variant(BaseModel):
    memory: str
    price: int

class ImageURLs(BaseModel):
    front: str
    back: str
    side: str

class Product(BaseModel):
    category: str
    name: str
    color: str
    variants: List[Variant]
    img: ImageURLs

# -----------------------------
# In-memory storage
# -----------------------------
products = []

# -----------------------------
# Upload image to Supabase
# -----------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = f"{uuid.uuid4()}-{file.filename}"

        supabase.storage.from_("products").upload(
            filename,
            content,
            {"content-type": file.content_type}
        )

        public_url = supabase.storage.from_("products").get_public_url(filename)

        return {"url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Create product
# -----------------------------
@app.post("/products", response_model=Product)
def create_product(product: Product):
    product_dict = product.dict()
    product_id = len(products) + 1
    product_dict["id"] = product_id
    products.append(product_dict)
    return product_dict

# -----------------------------
# Get all products
# -----------------------------
@app.get("/products", response_model=List[Product])
def get_products():
    return products

# -----------------------------
# Get product by ID
# -----------------------------
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int = Path(..., description="ID of the product to retrieve")):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# -----------------------------
# Update product by ID
# -----------------------------
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: Product):
    for i, p in enumerate(products):
        if p["id"] == product_id:
            updated_product = product.dict()
            updated_product["id"] = product_id
            products[i] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")

# -----------------------------
# Delete product by ID
# -----------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for i, p in enumerate(products):
        if p["id"] == product_id:
            products.pop(i)
            return {"detail": f"Product {product_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")
