from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.utils.auth import get_current_user, require_roles
from app.db.database import get_db
from app.schemas.user import UserCreate, UserUpdate, User, UserList
from app.schemas.reports import AdminRoleData, AdminAuditData
from app.functions.user_service import UserService
import requests
import json
from datetime import datetime, date

router = APIRouter()

class RoleAssignment(BaseModel):
    user_id: int
    role: str  # "agent", "adjuster", "operator", "manager", "admin"

class AuditLogEntry(BaseModel):
    id: int
    user_id: int
    username: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: str = None
    details: dict = {}

class AuditLogsResponse(BaseModel):
    logs: List[AuditLogEntry]
    total: int
    skip: int
    limit: int

class RoleInfo(BaseModel):
    role: str
    description: str
    permissions: List[str]
    user_count: int

class RolesResponse(BaseModel):
    roles: List[RoleInfo]

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str

class UserRoleUpdate(BaseModel):
    role: str

@router.get("/", response_model=UserList)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Get list of users (manager and admin only)"""
    user_service = UserService(db)
    users, total = user_service.get_users(
        skip=skip,
        limit=limit,
        role=role,
        active_only=active_only
    )
    
    return UserList(
        users=users,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Create new user (admin only)"""
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Get user by ID (admin only)"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Update user (admin only)"""
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Delete user (admin only)"""
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}

@router.get("/admin/roles", response_model=AdminRoleData)
async def get_roles_management(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Get roles management data (admin only)"""
    
    # Список всех доступных ролей
    available_roles = [
        {
            "role": "agent",
            "description": "Агент - продажа страховых полисов",
            "permissions": ["clients.create", "clients.read", "contracts.create", "contracts.read"]
        },
        {
            "role": "adjuster", 
            "description": "Урегулировщик - обработка страховых заявок",
            "permissions": ["claims.read", "claims.process", "claims.decision"]
        },
        {
            "role": "operator",
            "description": "Оператор - первичная обработка заявок",
            "permissions": ["claims.create", "claims.submit", "clients.read"]
        },
        {
            "role": "manager",
            "description": "Менеджер - аналитика и управление",
            "permissions": ["analytics.read", "reports.generate", "users.read"]
        },
        {
            "role": "admin",
            "description": "Администратор - полный доступ",
            "permissions": ["*"]
        }
    ]
    
    # Имитация статистики пользователей по ролям (в реальности нужно запрашивать из auth-service)
    users_by_role = {
        "agent": 8,
        "adjuster": 4,
        "operator": 6,
        "manager": 3,
        "admin": 4
    }
    
    # Имитация недавних изменений ролей
    recent_role_changes = [
        {
            "user_id": 15,
            "user_name": "Иван Петров",
            "old_role": "agent",
            "new_role": "manager",
            "changed_by": "Администратор",
            "changed_at": "2024-01-15T10:30:00",
            "reason": "Повышение по службе"
        },
        {
            "user_id": 23,
            "user_name": "Мария Сидорова", 
            "old_role": "operator",
            "new_role": "adjuster",
            "changed_by": "Администратор",
            "changed_at": "2024-01-10T14:15:00",
            "reason": "Перевод в другой отдел"
        }
    ]
    
    return AdminRoleData(
        roles=available_roles,
        users_by_role=users_by_role,
        recent_role_changes=recent_role_changes
    )

@router.post("/admin/roles/assign")
async def assign_user_role(
    user_id: int,
    new_role: str,
    reason: str = "",
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Assign role to user (admin only)"""
    
    # Проверяем корректность роли
    valid_roles = ["agent", "adjuster", "operator", "manager", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # В реальности здесь должен быть вызов auth-service для изменения роли
    # Пока что возвращаем успешный ответ
    
    return {
        "message": f"Role '{new_role}' assigned to user {user_id} successfully",
        "user_id": user_id,
        "new_role": new_role,
        "assigned_by": current_user.get("user_id"),
        "assigned_at": datetime.now().isoformat(),
        "reason": reason
    }

@router.get("/admin/audit", response_model=AdminAuditData)
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Get system audit logs (admin only)"""
    
    # Имитация логов системы (в реальности должны храниться в отдельной таблице)
    all_logs = [
        {
            "id": 1,
            "timestamp": "2024-01-15T10:30:00",
            "user_id": 15,
            "user_name": "Иван Петров",
            "action": "role_change",
            "details": "Role changed from agent to manager",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0..."
        },
        {
            "id": 2,
            "timestamp": "2024-01-15T09:15:00", 
            "user_id": 23,
            "user_name": "Мария Сидорова",
            "action": "login",
            "details": "Successful login",
            "ip_address": "192.168.1.101",
            "user_agent": "Mozilla/5.0..."
        },
        {
            "id": 3,
            "timestamp": "2024-01-14T16:45:00",
            "user_id": 8,
            "user_name": "Алексей Иванов",
            "action": "claim_decision",
            "details": "Claim CLM-2024-1234567 approved for 50000 RUB",
            "ip_address": "192.168.1.102",
            "user_agent": "Mozilla/5.0..."
        },
        {
            "id": 4,
            "timestamp": "2024-01-14T14:20:00",
            "user_id": 12,
            "user_name": "Ольга Смирнова",
            "action": "contract_create",
            "details": "New contract created for client ID 45",
            "ip_address": "192.168.1.103",
            "user_agent": "Mozilla/5.0..."
        },
        {
            "id": 5,
            "timestamp": "2024-01-14T11:30:00",
            "user_id": 19,
            "user_name": "Дмитрий Козлов",
            "action": "report_generate",
            "details": "Financial report generated for Q4 2023",
            "ip_address": "192.168.1.104",
            "user_agent": "Mozilla/5.0..."
        }
    ]
    
    # Применяем фильтры
    filtered_logs = all_logs
    
    if action_type:
        filtered_logs = [log for log in filtered_logs if log["action"] == action_type]
    
    if user_id:
        filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
    
    if start_date:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_date.isoformat()]
    
    if end_date:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_date.isoformat()]
    
    # Пагинация
    total_filtered = len(filtered_logs)
    paginated_logs = filtered_logs[skip:skip + limit]
    
    # Статистика
    summary = {
        "total_actions": len(all_logs),
        "filtered_actions": total_filtered,
        "unique_users": len(set(log["user_id"] for log in all_logs)),
        "action_types": {
            "login": len([log for log in all_logs if log["action"] == "login"]),
            "role_change": len([log for log in all_logs if log["action"] == "role_change"]),
            "claim_decision": len([log for log in all_logs if log["action"] == "claim_decision"]),
            "contract_create": len([log for log in all_logs if log["action"] == "contract_create"]),
            "report_generate": len([log for log in all_logs if log["action"] == "report_generate"])
        }
    }
    
    return AdminAuditData(
        logs=paginated_logs,
        total_logs=len(all_logs),
        filtered_count=total_filtered,
        summary=summary
    ) 