from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from ..db.models import Client, Contract, ContractStatus
from ..schemas.client import ClientCreate, ClientUpdate
import secrets
import string

class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def create_client(self, client_data: ClientCreate, created_by: int) -> Client:
        """Create a new client"""
        client_dict = client_data.dict()
        
        # Generate identification_number if not provided
        if not client_dict.get('identification_number'):
            client_dict['identification_number'] = self.generate_client_id()
        
        client = Client(
            **client_dict,
            created_by=created_by
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_client(self, client_id: int) -> Optional[Client]:
        """Get client by ID"""
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_client_by_email(self, email: str) -> Optional[Client]:
        """Get client by email"""
        return self.db.query(Client).filter(Client.email == email).first()

    def get_clients(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Tuple[List[Client], int]:
        """Get list of clients with pagination and search"""
        query = self.db.query(Client)
        
        # Apply filters
        if search:
            search_filter = or_(
                Client.first_name.ilike(f"%{search}%"),
                Client.last_name.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if created_by:
            query = query.filter(Client.created_by == created_by)
        
        total = query.count()
        clients = query.offset(skip).limit(limit).all()
        
        return clients, total

    def update_client(self, client_id: int, client_data: ClientUpdate) -> Optional[Client]:
        """Update client"""
        client = self.get_client(client_id)
        if not client:
            return None
        
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, client_id: int) -> bool:
        """Delete client"""
        client = self.get_client(client_id)
        if not client:
            return False
        
        # Check if client has active contracts
        if self.has_active_contracts(client_id):
            raise ValueError("Cannot delete client with active contracts")
        
        self.db.delete(client)
        self.db.commit()
        return True

    def has_active_contracts(self, client_id: int) -> bool:
        """Check if client has active contracts"""
        active_contracts = self.db.query(Contract).filter(
            and_(
                Contract.client_id == client_id,
                Contract.status.in_([ContractStatus.ACTIVE, ContractStatus.DRAFT])
            )
        ).count()
        return active_contracts > 0

    def search_clients(self, query: str, limit: int = 10) -> List[Client]:
        """Search clients by name, email or phone"""
        search_filter = or_(
            Client.first_name.ilike(f"%{query}%"),
            Client.last_name.ilike(f"%{query}%"),
            Client.email.ilike(f"%{query}%"),
            Client.phone.ilike(f"%{query}%")
        )
        
        return self.db.query(Client).filter(search_filter).limit(limit).all()

    def generate_client_id(self) -> str:
        """Generate unique client identification number"""
        while True:
            # Generate 8-character alphanumeric ID
            client_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Check if it's unique
            existing = self.db.query(Client).filter(
                Client.identification_number == client_id
            ).first()
            
            if not existing:
                return client_id

    def get_client_statistics(self, client_id: int) -> dict:
        """Get client statistics"""
        client = self.get_client(client_id)
        if not client:
            return {}
        
        stats = {
            "total_contracts": len(client.contracts),
            "active_contracts": len([c for c in client.contracts if c.status == ContractStatus.ACTIVE]),
            "total_premium": sum(c.premium_amount for c in client.contracts),
            "total_claims": sum(len(c.claims) for c in client.contracts),
            "total_claim_amount": sum(
                sum(claim.claim_amount or 0 for claim in contract.claims)
                for contract in client.contracts
            )
        }
        
        return stats 