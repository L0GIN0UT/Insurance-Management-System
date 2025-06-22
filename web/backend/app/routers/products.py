from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils.auth import get_current_user, require_roles
from app.db.database import get_db
from app.db.models import InsuranceProduct
from pydantic import BaseModel

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: str
    base_premium: float
    coverage_amount: float

class Product(BaseModel):
    id: int
    name: str
    description: str
    base_premium: float
    coverage_amount: float
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[Product])
async def get_products(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all insurance products"""
    products = db.query(InsuranceProduct).filter(InsuranceProduct.is_active == True).all()
    return products

@router.post("/", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Create new insurance product (manager/admin only)"""
    product = InsuranceProduct(
        **product_data.dict(),
        is_active=True
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Update insurance product (manager/admin only)"""
    product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    for field, value in product_data.dict().items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Delete insurance product (admin only)"""
    product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete - mark as inactive instead of deleting
    product.is_active = False
    db.commit()
    return {"message": "Product deleted successfully"} 