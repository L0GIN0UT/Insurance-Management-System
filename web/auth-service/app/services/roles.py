from enum import Enum
from typing import List
from ..models.user import UserRole

class Permission(str, Enum):
    # Client permissions
    VIEW_CLIENTS = "view_clients"
    CREATE_CLIENTS = "create_clients"
    EDIT_CLIENTS = "edit_clients"
    DELETE_CLIENTS = "delete_clients"
    
    # Contract permissions
    VIEW_CONTRACTS = "view_contracts"
    CREATE_CONTRACTS = "create_contracts"
    EDIT_CONTRACTS = "edit_contracts"
    APPROVE_CONTRACTS = "approve_contracts"
    
    # Claim permissions
    VIEW_CLAIMS = "view_claims"
    CREATE_CLAIMS = "create_claims"
    PROCESS_CLAIMS = "process_claims"
    APPROVE_CLAIMS = "approve_claims"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    VIEW_REPORTS = "view_reports"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIG = "system_config"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.AGENT: [
        Permission.VIEW_CLIENTS,
        Permission.CREATE_CLIENTS,
        Permission.EDIT_CLIENTS,
        Permission.VIEW_CONTRACTS,
        Permission.CREATE_CONTRACTS,
        Permission.EDIT_CONTRACTS,
        Permission.VIEW_CLAIMS,
        Permission.CREATE_CLAIMS,
    ],
    UserRole.ADJUSTER: [
        Permission.VIEW_CLIENTS,
        Permission.VIEW_CONTRACTS,
        Permission.VIEW_CLAIMS,
        Permission.PROCESS_CLAIMS,
        Permission.APPROVE_CLAIMS,
    ],
    UserRole.OPERATOR: [
        Permission.VIEW_CLIENTS,
        Permission.EDIT_CLIENTS,
        Permission.VIEW_CONTRACTS,
        Permission.EDIT_CONTRACTS,
        Permission.VIEW_CLAIMS,
    ],
    UserRole.MANAGER: [
        Permission.VIEW_CLIENTS,
        Permission.CREATE_CLIENTS,
        Permission.EDIT_CLIENTS,
        Permission.DELETE_CLIENTS,
        Permission.VIEW_CONTRACTS,
        Permission.CREATE_CONTRACTS,
        Permission.EDIT_CONTRACTS,
        Permission.APPROVE_CONTRACTS,
        Permission.VIEW_CLAIMS,
        Permission.CREATE_CLAIMS,
        Permission.PROCESS_CLAIMS,
        Permission.APPROVE_CLAIMS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_REPORTS,
    ],
    UserRole.ADMIN: [permission for permission in Permission],  # All permissions
}

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    """Get all permissions for a user role"""
    return ROLE_PERMISSIONS.get(user_role, [])

def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if a user role has a specific permission"""
    user_permissions = get_user_permissions(user_role)
    return permission in user_permissions 