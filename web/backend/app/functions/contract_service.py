from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from datetime import date, datetime, timedelta
from ..db.models import Contract, Client, InsuranceProduct, ContractStatus
from ..schemas.contract import (
    ContractCreate, ContractUpdate, PremiumCalculationParams, 
    PremiumCalculationResult, ContractWithDetails
)
import secrets
import string

class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def create_contract(self, contract_data: ContractCreate, agent_id: int) -> Contract:
        """Create a new contract"""
        # Generate unique contract number
        contract_number = self.generate_contract_number()
        
        contract = Contract(
            **contract_data.dict(),
            contract_number=contract_number,
            agent_id=agent_id
        )
        
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get contract by ID"""
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

    def get_contract_with_details(self, contract_id: int) -> Optional[ContractWithDetails]:
        """Get contract with related details"""
        contract_query = self.db.query(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.product)
        ).filter(Contract.id == contract_id).first()
        
        if not contract_query:
            return None
        
        # Create contract with details
        contract_dict = {
            **contract_query.__dict__,
            "client_name": f"{contract_query.client.first_name} {contract_query.client.last_name}",
            "product_name": contract_query.product.name,
            "agent_name": None  # Would need to fetch from auth service
        }
        
        return ContractWithDetails(**contract_dict)

    def get_contract_by_number(self, contract_number: str) -> Optional[Contract]:
        """Get contract by contract number"""
        return self.db.query(Contract).filter(Contract.contract_number == contract_number).first()

    def get_contracts(
        self, 
        skip: int = 0, 
        limit: int = 100,
        client_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        status: Optional[ContractStatus] = None,
        product_id: Optional[int] = None
    ) -> Tuple[List[ContractWithDetails], int]:
        """Get list of contracts with pagination and filters"""
        query = self.db.query(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.product)
        )
        
        # Apply filters
        if client_id:
            query = query.filter(Contract.client_id == client_id)
        
        if agent_id:
            query = query.filter(Contract.agent_id == agent_id)
        
        if status:
            query = query.filter(Contract.status == status)
        
        if product_id:
            query = query.filter(Contract.product_id == product_id)
        
        total = query.count()
        contracts = query.offset(skip).limit(limit).all()
        
        # Convert to ContractWithDetails
        contracts_with_details = []
        for contract in contracts:
            contract_dict = {
                **contract.__dict__,
                "client_name": f"{contract.client.first_name} {contract.client.last_name}",
                "product_name": contract.product.name,
                "agent_name": None  # Would need to fetch from auth service
            }
            contracts_with_details.append(ContractWithDetails(**contract_dict))
        
        return contracts_with_details, total

    def update_contract(self, contract_id: int, contract_data: ContractUpdate) -> Optional[Contract]:
        """Update contract"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        update_data = contract_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contract, field, value)
        
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def activate_contract(self, contract_id: int) -> bool:
        """Activate contract"""
        contract = self.get_contract(contract_id)
        if not contract:
            return False
        
        if contract.status != ContractStatus.DRAFT:
            return False
        
        contract.status = ContractStatus.ACTIVE
        self.db.commit()
        return True

    def suspend_contract(self, contract_id: int, reason: str = None) -> Optional[Contract]:
        """Suspend contract"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        if contract.status != ContractStatus.ACTIVE:
            raise ValueError("Only active contracts can be suspended")
        
        contract.status = ContractStatus.SUSPENDED
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def cancel_contract(self, contract_id: int, reason: str = None) -> Optional[Contract]:
        """Cancel contract"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        if contract.status in [ContractStatus.EXPIRED, ContractStatus.CANCELLED]:
            raise ValueError("Contract is already cancelled or expired")
        
        contract.status = ContractStatus.CANCELLED
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def calculate_premium(self, params: PremiumCalculationParams, product: InsuranceProduct) -> PremiumCalculationResult:
        """Calculate premium based on parameters and product"""
        base_premium = product.base_premium * (params.coverage_amount / 100000)  # Base rate per 100k coverage
        risk_factors = params.risk_factors
        
        # Risk factor calculations
        risk_multiplier = 1.0
        calculation_details = {
            "product_name": product.name,
            "base_coverage": product.coverage_amount,
            "requested_coverage": params.coverage_amount,
            "risk_factors_applied": {}
        }
        
        # Age factor
        if params.client_age:
            age = params.client_age
            if age < 25:
                risk_multiplier *= 1.2
                calculation_details["risk_factors_applied"]["young_age"] = 0.2
            elif age > 65:
                risk_multiplier *= 1.1
                calculation_details["risk_factors_applied"]["senior_age"] = 0.1
        
        # Coverage amount factor
        if params.coverage_amount > 500000:
            risk_multiplier *= 1.1
            calculation_details["risk_factors_applied"]["high_coverage"] = 0.1
        
        # Custom risk factors
        for factor, value in risk_factors.items():
            if factor == "high_risk_area" and value:
                risk_multiplier *= 1.15
                calculation_details["risk_factors_applied"]["high_risk_area"] = 0.15
            elif factor == "previous_claims" and isinstance(value, (int, float)):
                risk_multiplier *= (1 + value * 0.1)
                calculation_details["risk_factors_applied"]["previous_claims"] = value * 0.1
            elif factor == "security_systems" and value:
                risk_multiplier *= 0.9
                calculation_details["risk_factors_applied"]["security_systems"] = -0.1
        
        final_premium = base_premium * risk_multiplier
        monthly_premium = final_premium / params.duration_months
        
        return PremiumCalculationResult(
            base_premium=round(base_premium, 2),
            risk_multiplier=round(risk_multiplier, 2),
            final_premium=round(final_premium, 2),
            monthly_premium=round(monthly_premium, 2),
            calculation_details=calculation_details
        )

    def generate_contract_number(self) -> str:
        """Generate unique contract number"""
        while True:
            # Generate format: CON-YYYY-XXXXXX
            year = datetime.now().year
            random_part = ''.join(secrets.choice(string.digits) for _ in range(6))
            contract_number = f"CON-{year}-{random_part}"
            
            # Check if it's unique
            existing = self.get_contract_by_number(contract_number)
            if not existing:
                return contract_number

    def get_contracts_expiring_soon(self, days: int = 30) -> List[Contract]:
        """Get contracts expiring within specified days"""
        future_date = date.today() + timedelta(days=days)
        
        return self.db.query(Contract).filter(
            and_(
                Contract.end_date <= future_date,
                Contract.end_date >= date.today(),
                Contract.status == ContractStatus.ACTIVE
            )
        ).all()

    def get_contract_statistics(self, agent_id: Optional[int] = None) -> dict:
        """Get contract statistics"""
        query = self.db.query(Contract)
        
        if agent_id:
            query = query.filter(Contract.agent_id == agent_id)
        
        all_contracts = query.all()
        
        stats = {
            "total_contracts": len(all_contracts),
            "active_contracts": len([c for c in all_contracts if c.status == ContractStatus.ACTIVE]),
            "draft_contracts": len([c for c in all_contracts if c.status == ContractStatus.DRAFT]),
            "expired_contracts": len([c for c in all_contracts if c.status == ContractStatus.EXPIRED]),
            "cancelled_contracts": len([c for c in all_contracts if c.status == ContractStatus.CANCELLED]),
            "total_premium_volume": sum(c.premium_amount for c in all_contracts),
            "total_coverage_volume": sum(c.coverage_amount for c in all_contracts)
        }
        
        return stats 