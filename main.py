from fastapi import FastAPI, UploadFile, File, HTTPException
from supabase_client import supabase
import uuid

app = FastAPI(title="Product API")

# Temporary in-memory storage
products = []

# -----------------------------
# Upload image to Supabase
# -----------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = f"{uuid.uuid4()}-{file.filename}"

        # Upload to Supabase storage
        supabase.storage.from_("products").upload(
            filename,
            content,
            {"content-type": file.content_type}
        )

        # Get public URL
        public_url = supabase.storage.from_("products").get_public_url(filename)

        return {"url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Create product
# -----------------------------
@app.post("/products")
def create_product(product: dict):
    product_id = len(products) + 1
    product["id"] = product_id
    products.append(product)
    return product

# -----------------------------
# Get all products
# -----------------------------
@app.get("/products")
def get_products():
    return {"products": products}

# -----------------------------
# Get product by ID
# -----------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
