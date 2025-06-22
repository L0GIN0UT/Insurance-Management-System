from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
from ..db.models import Contract, Client, InsuranceProduct, ContractStatus
from ..modules.contract import ContractCreate, ContractUpdate, PremiumCalculationParams, PremiumCalculationResult
import secrets
import string

class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def create_contract(self, contract_data: ContractCreate) -> Contract:
        """Create a new contract"""
        # Generate unique contract number
        contract_number = self.generate_contract_number()
        
        contract = Contract(
            **contract_data.dict(exclude={'contract_number'}),
            contract_number=contract_number
        )
        
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get contract by ID"""
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

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
    ) -> tuple[List[Contract], int]:
        """Get list of contracts with pagination and filters"""
        query = self.db.query(Contract)
        
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
        
        return contracts, total

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

    def activate_contract(self, contract_id: int) -> Optional[Contract]:
        """Activate contract"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        if contract.status != ContractStatus.DRAFT:
            raise ValueError("Only draft contracts can be activated")
        
        contract.status = ContractStatus.ACTIVE
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def suspend_contract(self, contract_id: int, reason: str = None) -> Optional[Contract]:
        """Suspend contract"""
        contract = self.get_contract(contract_id)
        if not contract:
            return None
        
        if contract.status != ContractStatus.ACTIVE:
            raise ValueError("Only active contracts can be suspended")
        
        contract.status = ContractStatus.SUSPENDED
        # Could add reason to terms_conditions or separate field
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

    def check_expired_contracts(self) -> List[Contract]:
        """Check and update expired contracts"""
        today = date.today()
        expired_contracts = self.db.query(Contract).filter(
            and_(
                Contract.end_date < today,
                Contract.status == ContractStatus.ACTIVE
            )
        ).all()
        
        for contract in expired_contracts:
            contract.status = ContractStatus.EXPIRED
        
        if expired_contracts:
            self.db.commit()
        
        return expired_contracts

    def calculate_premium(self, params: PremiumCalculationParams) -> PremiumCalculationResult:
        """Calculate premium based on parameters"""
        base_premium = params.base_premium
        coverage_amount = params.coverage_amount
        risk_factors = params.risk_factors
        discounts = params.discounts
        
        # Risk factor calculations
        risk_multiplier = 1.0
        risk_adjustments = {}
        
        # Age factor
        if 'age' in risk_factors:
            age = risk_factors['age']
            if age < 25:
                risk_multiplier *= 1.2
                risk_adjustments['young_driver'] = 0.2
            elif age > 65:
                risk_multiplier *= 1.1
                risk_adjustments['senior_driver'] = 0.1
        
        # Coverage amount factor
        if coverage_amount > 100000:
            risk_multiplier *= 1.05
            risk_adjustments['high_coverage'] = 0.05
        
        # Location factor
        if 'location_risk' in risk_factors:
            location_risk = risk_factors['location_risk']
            if location_risk == 'high':
                risk_multiplier *= 1.15
                risk_adjustments['high_risk_location'] = 0.15
            elif location_risk == 'low':
                risk_multiplier *= 0.95
                risk_adjustments['low_risk_location'] = -0.05
        
        # Apply risk adjustments
        adjusted_premium = base_premium * risk_multiplier
        
        # Apply discounts
        discount_multiplier = 1.0
        discounts_applied = {}
        
        if 'loyalty_discount' in discounts:
            discount_rate = discounts['loyalty_discount']
            discount_multiplier *= (1 - discount_rate)
            discounts_applied['loyalty'] = discount_rate
        
        if 'multi_policy_discount' in discounts:
            discount_rate = discounts['multi_policy_discount']
            discount_multiplier *= (1 - discount_rate)
            discounts_applied['multi_policy'] = discount_rate
        
        total_premium = adjusted_premium * discount_multiplier
        
        return PremiumCalculationResult(
            base_premium=base_premium,
            total_premium=total_premium,
            risk_adjustments=risk_adjustments,
            discounts_applied=discounts_applied,
            calculation_details={
                'risk_multiplier': risk_multiplier,
                'discount_multiplier': discount_multiplier,
                'adjusted_premium': adjusted_premium
            }
        )

    def generate_contract_number(self) -> str:
        """Generate unique contract number"""
        while True:
            # Format: CON-YYYY-XXXXXX
            year = datetime.now().year
            random_part = ''.join(secrets.choice(string.digits) for _ in range(6))
            contract_number = f"CON-{year}-{random_part}"
            
            # Check if it's unique
            existing = self.db.query(Contract).filter(
                Contract.contract_number == contract_number
            ).first()
            
            if not existing:
                return contract_number

    def get_contracts_expiring_soon(self, days: int = 30) -> List[Contract]:
        """Get contracts expiring within specified days"""
        expiry_date = date.today() + timedelta(days=days)
        
        return self.db.query(Contract).filter(
            and_(
                Contract.end_date <= expiry_date,
                Contract.status == ContractStatus.ACTIVE
            )
        ).all()

    def get_contract_statistics(self, agent_id: Optional[int] = None) -> dict:
        """Get contract statistics"""
        query = self.db.query(Contract)
        
        if agent_id:
            query = query.filter(Contract.agent_id == agent_id)
        
        contracts = query.all()
        
        stats = {
            "total_contracts": len(contracts),
            "active_contracts": len([c for c in contracts if c.status == ContractStatus.ACTIVE]),
            "draft_contracts": len([c for c in contracts if c.status == ContractStatus.DRAFT]),
            "suspended_contracts": len([c for c in contracts if c.status == ContractStatus.SUSPENDED]),
            "expired_contracts": len([c for c in contracts if c.status == ContractStatus.EXPIRED]),
            "cancelled_contracts": len([c for c in contracts if c.status == ContractStatus.CANCELLED]),
            "total_premium": sum(c.premium_amount for c in contracts),
            "average_premium": sum(c.premium_amount for c in contracts) / len(contracts) if contracts else 0,
            "total_coverage": sum(c.coverage_amount for c in contracts)
        }
        
        return stats 