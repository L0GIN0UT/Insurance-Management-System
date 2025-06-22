from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ClaimStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(Date)
    identification_number = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)  # Reference to user from auth service
    
    # Relationships
    contracts = relationship("Contract", back_populates="client")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.first_name} {self.last_name}')>"

class InsuranceProduct(Base):
    __tablename__ = "insurance_products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    base_premium = Column(Float, nullable=False)
    coverage_amount = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contracts = relationship("Contract", back_populates="product")
    
    def __repr__(self):
        return f"<InsuranceProduct(id={self.id}, name='{self.name}')>"

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("insurance_products.id"), nullable=False)
    agent_id = Column(Integer, nullable=False)  # Reference to user from auth service
    premium_amount = Column(Float, nullable=False)
    coverage_amount = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    terms_conditions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="contracts")
    product = relationship("InsuranceProduct", back_populates="contracts")
    claims = relationship("Claim", back_populates="contract")
    
    def __repr__(self):
        return f"<Contract(id={self.id}, number='{self.contract_number}', status='{self.status}')>"

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    incident_date = Column(Date, nullable=False)
    reported_date = Column(Date, server_default=func.current_date())
    description = Column(Text, nullable=False)
    claimed_amount = Column(Float)
    approved_amount = Column(Float)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.SUBMITTED)
    adjuster_id = Column(Integer)  # Reference to user from auth service
    adjuster_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="claims")
    
    def __repr__(self):
        return f"<Claim(id={self.id}, number='{self.claim_number}', status='{self.status}')>" 