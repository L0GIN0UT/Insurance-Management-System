from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.db.models import Claim, Contract, ClaimStatus
from app.schemas.claim import ClaimCreate, ClaimUpdate, ClaimDecisionRequest, ClaimWithDetails
import secrets
import string

class ClaimService:
    def __init__(self, db: Session):
        self.db = db

    def create_claim(self, claim_data: ClaimCreate, created_by: Optional[int] = None) -> Claim:
        """Create new claim"""
        claim_number = self.generate_claim_number()
        
        claim = Claim(
            claim_number=claim_number,
            contract_id=claim_data.contract_id,
            incident_date=claim_data.incident_date,
            description=claim_data.description,
            claim_amount=claim_data.claim_amount,
            status=ClaimStatus.SUBMITTED,
            reported_date=date.today(),
            created_at=datetime.now()
        )
        
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def get_claim(self, claim_id: int) -> Optional[Claim]:
        """Get claim by ID"""
        return self.db.query(Claim).filter(Claim.id == claim_id).first()

    def get_claim_by_number(self, claim_number: str) -> Optional[Claim]:
        """Get claim by claim number"""
        return self.db.query(Claim).filter(Claim.claim_number == claim_number).first()

    def get_claims(
        self, 
        skip: int = 0, 
        limit: int = 100,
        contract_id: Optional[int] = None,
        adjuster_id: Optional[int] = None,
        status: Optional[ClaimStatus] = None,
        search: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> tuple[List[ClaimWithDetails], int]:
        """Get list of claims with pagination and filters"""
        from app.db.models import Client, Contract
        
        query = self.db.query(
            Claim,
            Contract.contract_number,
            (Client.first_name + ' ' + Client.last_name).label('client_name')
        ).join(Contract, Claim.contract_id == Contract.id)\
         .join(Client, Contract.client_id == Client.id)
        
        # Apply filters
        if contract_id:
            query = query.filter(Claim.contract_id == contract_id)
        
        if adjuster_id:
            query = query.filter(Claim.adjuster_id == adjuster_id)
        
        if status:
            query = query.filter(Claim.status == status)
            
        if status_filter:
            query = query.filter(Claim.status == status_filter)
        
        if search:
            search_filter = or_(
                Claim.claim_number.ilike(f"%{search}%"),
                Claim.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        results = query.offset(skip).limit(limit).all()
        
        # Convert to ClaimWithDetails
        claims_with_details = []
        for claim, contract_number, client_name in results:
            claim_dict = {
                "id": claim.id,
                "claim_number": claim.claim_number,
                "contract_id": claim.contract_id,
                "incident_date": claim.incident_date,
                "reported_date": claim.reported_date,
                "description": claim.description,
                "claim_amount": claim.claim_amount,
                "approved_amount": claim.approved_amount,
                "status": claim.status,
                "adjuster_id": claim.adjuster_id,
                "adjuster_notes": claim.adjuster_notes,
                "created_at": claim.created_at,
                "updated_at": claim.updated_at,
                "contract_number": contract_number,
                "client_name": client_name,
                "adjuster_name": f"Урегулировщик {claim.adjuster_id}" if claim.adjuster_id else None
            }
            claims_with_details.append(ClaimWithDetails(**claim_dict))
        
        return claims_with_details, total

    def get_claim_with_details(self, claim_id: int) -> Optional[ClaimWithDetails]:
        """Get claim with full details"""
        from app.db.models import Client, Contract
        
        result = self.db.query(
            Claim,
            Contract.contract_number,
            (Client.first_name + ' ' + Client.last_name).label('client_name')
        ).join(Contract, Claim.contract_id == Contract.id)\
         .join(Client, Contract.client_id == Client.id)\
         .filter(Claim.id == claim_id).first()
        
        if not result:
            return None
            
        claim, contract_number, client_name = result
        
        return ClaimWithDetails(
            id=claim.id,
            claim_number=claim.claim_number,
            contract_id=claim.contract_id,
            incident_date=claim.incident_date,
            reported_date=claim.reported_date,
            description=claim.description,
            claim_amount=claim.claim_amount,
            approved_amount=claim.approved_amount,
            status=claim.status,
            adjuster_id=claim.adjuster_id,
            adjuster_notes=claim.adjuster_notes,
            created_at=claim.created_at,
            updated_at=claim.updated_at,
            contract_number=contract_number,
            client_name=client_name,
            adjuster_name=f"Урегулировщик {claim.adjuster_id}" if claim.adjuster_id else None
        )

    def get_pending_claims(self, skip: int = 0, limit: int = 100, adjuster_id: Optional[int] = None) -> tuple[List[ClaimWithDetails], int]:
        """Get pending claims for adjustment"""
        from app.db.models import Client, Contract
        
        query = self.db.query(
            Claim,
            Contract.contract_number,
            (Client.first_name + ' ' + Client.last_name).label('client_name')
        ).join(Contract, Claim.contract_id == Contract.id)\
         .join(Client, Contract.client_id == Client.id)\
         .filter(Claim.status.in_([ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW]))
        
        if adjuster_id:
            query = query.filter(Claim.adjuster_id == adjuster_id)
        
        total = query.count()
        results = query.offset(skip).limit(limit).all()
        
        # Convert to ClaimWithDetails
        pending_claims = []
        for claim, contract_number, client_name in results:
            claim_dict = {
                "id": claim.id,
                "claim_number": claim.claim_number,
                "contract_id": claim.contract_id,
                "incident_date": claim.incident_date,
                "reported_date": claim.reported_date,
                "description": claim.description,
                "claim_amount": claim.claim_amount,
                "approved_amount": claim.approved_amount,
                "status": claim.status,
                "adjuster_id": claim.adjuster_id,
                "adjuster_notes": claim.adjuster_notes,
                "created_at": claim.created_at,
                "updated_at": claim.updated_at,
                "contract_number": contract_number,
                "client_name": client_name,
                "adjuster_name": f"Урегулировщик {claim.adjuster_id}" if claim.adjuster_id else None
            }
            pending_claims.append(ClaimWithDetails(**claim_dict))
        
        return pending_claims, total

    def make_decision(self, claim_id: int, decision_data: ClaimDecisionRequest, adjuster_id: int) -> Optional[Claim]:
        """Make decision on claim (adjuster only)"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        # Update claim based on decision
        if decision_data.decision == "approved":
            claim.status = ClaimStatus.APPROVED
            claim.approved_amount = decision_data.approved_amount or claim.claim_amount
        elif decision_data.decision == "rejected":
            claim.status = ClaimStatus.REJECTED
            claim.approved_amount = 0
        else:  # requires_investigation
            claim.status = ClaimStatus.UNDER_REVIEW
        
        # Update notes
        decision_note = f"Решение: {decision_data.decision}"
        if decision_data.notes:
            decision_note += f" - {decision_data.notes}"
        if decision_data.rejection_reason:
            decision_note += f" (Причина отказа: {decision_data.rejection_reason})"
            
        claim.adjuster_notes = (claim.adjuster_notes or "") + f"\n{decision_note}"
        claim.adjuster_id = adjuster_id
        claim.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def update_claim(self, claim_id: int, claim_data: ClaimUpdate) -> Optional[Claim]:
        """Update claim"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        update_data = claim_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(claim, field, value)
        
        claim.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def assign_adjuster(self, claim_id: int, adjuster_id: int) -> Optional[Claim]:
        """Assign adjuster to claim"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        if claim.status not in [ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW]:
            raise ValueError("Cannot assign adjuster to processed claim")
        
        claim.adjuster_id = adjuster_id
        claim.status = ClaimStatus.UNDER_REVIEW
        
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def mark_as_paid(self, claim_id: int) -> Optional[Claim]:
        """Mark claim as paid"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        if claim.status != ClaimStatus.APPROVED:
            raise ValueError("Only approved claims can be marked as paid")
        
        claim.status = ClaimStatus.PAID
        
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def generate_claim_number(self) -> str:
        """Generate unique claim number"""
        while True:
            # Format: CLM-YYYY-XXXXXXX
            year = datetime.now().year
            random_part = ''.join(secrets.choice(string.digits) for _ in range(7))
            claim_number = f"CLM-{year}-{random_part}"
            
            # Check if it's unique
            existing = self.db.query(Claim).filter(
                Claim.claim_number == claim_number
            ).first()
            
            if not existing:
                return claim_number

    def get_claim_statistics(self, adjuster_id: Optional[int] = None, contract_id: Optional[int] = None) -> dict:
        """Get claim statistics"""
        query = self.db.query(Claim)
        
        if adjuster_id:
            query = query.filter(Claim.adjuster_id == adjuster_id)
        
        if contract_id:
            query = query.filter(Claim.contract_id == contract_id)
        
        claims = query.all()
        
        # Calculate statistics
        total_claims = len(claims)
        submitted_claims = len([c for c in claims if c.status == ClaimStatus.SUBMITTED])
        under_review_claims = len([c for c in claims if c.status == ClaimStatus.UNDER_REVIEW])
        approved_claims = len([c for c in claims if c.status == ClaimStatus.APPROVED])
        rejected_claims = len([c for c in claims if c.status == ClaimStatus.REJECTED])
        paid_claims = len([c for c in claims if c.status == ClaimStatus.PAID])
        
        total_claimed = sum(c.claim_amount or 0 for c in claims)
        total_approved = sum(c.approved_amount or 0 for c in claims if c.approved_amount)
        
        stats = {
            "total_claims": total_claims,
            "submitted_claims": submitted_claims,
            "under_review_claims": under_review_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "paid_claims": paid_claims,
            "total_claim_amount": total_claimed,
            "total_approved_amount": total_approved,
            "average_claim_amount": total_claimed / total_claims if total_claims > 0 else 0,
            "approval_rate": approved_claims / total_claims if total_claims > 0 else 0,
            "payment_rate": paid_claims / approved_claims if approved_claims > 0 else 0
        }
        
        return stats

    def get_claims_by_contract(self, contract_id: int) -> List[Claim]:
        """Get all claims for a specific contract"""
        return self.db.query(Claim).filter(Claim.contract_id == contract_id).all()

    def validate_claim_eligibility(self, contract_id: int, incident_date: date) -> dict:
        """Validate if a claim is eligible based on contract terms"""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        
        if not contract:
            return {"eligible": False, "reason": "Contract not found"}
        
        if contract.status != "active":
            return {"eligible": False, "reason": "Contract is not active"}
        
        if incident_date < contract.start_date:
            return {"eligible": False, "reason": "Incident occurred before contract start date"}
        
        if incident_date > contract.end_date:
            return {"eligible": False, "reason": "Incident occurred after contract end date"}
        
        # Check if incident is within coverage period
        if incident_date > date.today():
            return {"eligible": False, "reason": "Incident date cannot be in the future"}
        
        # Additional eligibility checks can be added here
        # e.g., waiting periods, exclusions, etc.
        
        return {"eligible": True, "reason": "Claim is eligible for processing"} 