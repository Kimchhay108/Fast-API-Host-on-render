from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional
import uuid
from supabase_client import supabase  # Your supabase client

app = FastAPI(title="iPhone Product API")

# -----------------------------
# Pydantic Models
# -----------------------------
class StorageOption(BaseModel):
    capacity: str
    price: int

class Images(BaseModel):
    front: str
    back: str
    side: str

class Specifications(BaseModel):
    screen_size: str
    cpu: str
    cpu_cores: int
    main_camera: str
    front_camera: str
    battery_capacity: str

class Product(BaseModel):
    id: Optional[str] = None
    name: str
    price: int
    currency: str
    brand: str
    category: str
    colors: List[str]
    storage_options: List[StorageOption]
    images: Images
    specifications: Specifications
    description: str
    in_stock: bool
    release_status: str

# -----------------------------
# In-memory storage
# -----------------------------
products: List[Product] = []

# -----------------------------
# Upload image to Supabase
# -----------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = f"{uuid.uuid4()}-{file.filename}"

        supabase.storage.from_("products").upload(
            path=filename,
            file=content,
            file_options={"content-type": file.content_type}
        )

        public_url = supabase.storage.from_("products").get_public_url(filename)
        return {"filename": filename, "url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Create a product
# -----------------------------
@app.post("/products", response_model=Product)
def create_product(product: Product):
    # If no ID provided, generate one
    if not product.id:
        product.id = str(uuid.uuid4())
    products.append(product)
    return product

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
def get_product(product_id: str = Path(..., description="ID of the product to retrieve")):
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# -----------------------------
# Update product by ID
# -----------------------------
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, product: Product):
    for i, p in enumerate(products):
        if p.id == product_id:
            product.id = product_id
            products[i] = product
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# -----------------------------
# Delete product by ID
# -----------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    for i, p in enumerate(products):
        if p.id == product_id:
            products.pop(i)
            return {"message": f"Product '{product_id}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")
