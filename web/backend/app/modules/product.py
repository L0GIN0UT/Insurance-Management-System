from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# Base Product schema
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_premium: float
    coverage_amount: Optional[float] = None
    is_active: bool = True

# Schema for creating a product
class ProductCreate(ProductBase):
    name: str
    base_premium: float
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @validator('base_premium')
    def validate_base_premium(cls, v):
        if v <= 0:
            raise ValueError('Base premium must be positive')
        return v
    
    @validator('coverage_amount')
    def validate_coverage_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Coverage amount must be positive')
        return v

# Schema for updating a product
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_premium: Optional[float] = None
    coverage_amount: Optional[float] = None
    is_active: Optional[bool] = None

# Schema for product response
class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for product list with pagination
class ProductList(BaseModel):
    products: List[Product]
    total: int
    skip: int
    limit: int

# Schema for product with contracts
class ProductWithContracts(Product):
    contracts: List['ContractBase'] = []
    
    class Config:
        from_attributes = True 