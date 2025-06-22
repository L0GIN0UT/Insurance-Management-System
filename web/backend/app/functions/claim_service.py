from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime
from ..db.models import Claim, Contract, ClaimStatus
from ..modules.claim import ClaimCreate, ClaimUpdate, ClaimProcessingData, ClaimApproval, ClaimRejection
import secrets
import string

class ClaimService:
    def __init__(self, db: Session):
        self.db = db

    def create_claim(self, claim_data: ClaimCreate) -> Claim:
        """Create a new claim"""
        # Generate unique claim number
        claim_number = self.generate_claim_number()
        
        # Set reported date to today if not provided
        reported_date = claim_data.reported_date or date.today()
        
        claim = Claim(
            **claim_data.dict(exclude={'claim_number', 'reported_date'}),
            claim_number=claim_number,
            reported_date=reported_date
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
        search: Optional[str] = None
    ) -> tuple[List[Claim], int]:
        """Get list of claims with pagination and filters"""
        query = self.db.query(Claim)
        
        # Apply filters
        if contract_id:
            query = query.filter(Claim.contract_id == contract_id)
        
        if adjuster_id:
            query = query.filter(Claim.adjuster_id == adjuster_id)
        
        if status:
            query = query.filter(Claim.status == status)
        
        if search:
            search_filter = or_(
                Claim.claim_number.ilike(f"%{search}%"),
                Claim.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        claims = query.offset(skip).limit(limit).all()
        
        return claims, total

    def update_claim(self, claim_id: int, claim_data: ClaimUpdate) -> Optional[Claim]:
        """Update claim"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        update_data = claim_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(claim, field, value)
        
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

    def process_claim(self, claim_id: int, processing_data: ClaimProcessingData) -> Optional[Claim]:
        """Process claim with adjuster decision"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        if claim.status not in [ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW]:
            raise ValueError("Claim is not in a processable status")
        
        claim.adjuster_notes = processing_data.adjuster_notes
        claim.approved_amount = processing_data.approved_amount
        claim.status = processing_data.status
        
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def approve_claim(self, claim_id: int, approval_data: ClaimApproval) -> Optional[Claim]:
        """Approve claim"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        if claim.status != ClaimStatus.UNDER_REVIEW:
            raise ValueError("Only claims under review can be approved")
        
        # Validate approved amount doesn't exceed claimed amount
        if claim.claimed_amount and approval_data.approved_amount > claim.claimed_amount:
            raise ValueError("Approved amount cannot exceed claimed amount")
        
        # Validate approved amount doesn't exceed contract coverage
        if claim.contract and approval_data.approved_amount > claim.contract.coverage_amount:
            raise ValueError("Approved amount cannot exceed contract coverage")
        
        claim.approved_amount = approval_data.approved_amount
        claim.status = ClaimStatus.APPROVED
        if approval_data.approval_notes:
            claim.adjuster_notes = (claim.adjuster_notes or "") + f"\nApproval: {approval_data.approval_notes}"
        
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def reject_claim(self, claim_id: int, rejection_data: ClaimRejection) -> Optional[Claim]:
        """Reject claim"""
        claim = self.get_claim(claim_id)
        if not claim:
            return None
        
        if claim.status != ClaimStatus.UNDER_REVIEW:
            raise ValueError("Only claims under review can be rejected")
        
        claim.status = ClaimStatus.REJECTED
        claim.approved_amount = 0
        rejection_note = f"REJECTED: {rejection_data.rejection_reason}"
        if rejection_data.rejection_notes:
            rejection_note += f"\nNotes: {rejection_data.rejection_notes}"
        
        claim.adjuster_notes = (claim.adjuster_notes or "") + f"\n{rejection_note}"
        
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

    def get_pending_claims(self, adjuster_id: Optional[int] = None) -> List[Claim]:
        """Get pending claims (submitted or under review)"""
        query = self.db.query(Claim).filter(
            Claim.status.in_([ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW])
        )
        
        if adjuster_id:
            query = query.filter(Claim.adjuster_id == adjuster_id)
        
        return query.all()

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
        
        total_claimed = sum(c.claimed_amount or 0 for c in claims)
        total_approved = sum(c.approved_amount or 0 for c in claims if c.approved_amount)
        
        stats = {
            "total_claims": total_claims,
            "submitted_claims": submitted_claims,
            "under_review_claims": under_review_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "paid_claims": paid_claims,
            "total_claimed_amount": total_claimed,
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