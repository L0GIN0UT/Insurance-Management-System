from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app.schemas.user import UserCreate, UserUpdate, User

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[User], int]:
        """Get list of users with pagination and filters"""
        # Имитация пользователей (в реальности должно читаться из auth-service или локальной таблицы)
        all_users = [
            {
                "id": 1,
                "username": "admin1",
                "email": "admin@company.com",
                "full_name": "Администратор Системы",
                "role": "admin",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00",
                "last_login": "2024-01-15T09:30:00"
            },
            {
                "id": 2,
                "username": "agent1",
                "email": "agent1@company.com",
                "full_name": "Иван Агентов",
                "role": "agent",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-02T00:00:00",
                "last_login": "2024-01-15T08:45:00"
            },
            {
                "id": 3,
                "username": "adjuster1",
                "email": "adjuster1@company.com",
                "full_name": "Мария Урегулировщикова",
                "role": "adjuster",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-03T00:00:00",
                "last_login": "2024-01-15T10:15:00"
            },
            {
                "id": 4,
                "username": "operator1",
                "email": "operator1@company.com",
                "full_name": "Петр Операторов",
                "role": "operator",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-04T00:00:00",
                "last_login": "2024-01-15T07:30:00"
            },
            {
                "id": 5,
                "username": "manager1",
                "email": "manager1@company.com",
                "full_name": "Анна Менеджерова",
                "role": "manager",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-05T00:00:00",
                "last_login": "2024-01-15T09:00:00"
            }
        ]
        
        # Применяем фильтры
        filtered_users = all_users
        
        if role:
            filtered_users = [user for user in filtered_users if user["role"] == role]
            
        if active_only:
            filtered_users = [user for user in filtered_users if user["is_active"]]
        
        total = len(filtered_users)
        paginated_users = filtered_users[skip:skip + limit]
        
        # Конвертируем в User объекты
        users = [User(**user_data) for user_data in paginated_users]
        
        return users, total

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        # В реальности должно обращаться к auth-service
        users, _ = self.get_users(limit=1000)  # Получаем всех пользователей
        for user in users:
            if user.id == user_id:
                return user
        return None

    def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        # В реальности должно обращаться к auth-service
        new_user = User(
            id=999,  # Временный ID
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=True,
            is_verified=True,
            created_at="2024-01-15T12:00:00",
            updated_at="2024-01-15T12:00:00",
            last_login=None
        )
        return new_user

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        # В реальности должно обращаться к auth-service
        user = self.get_user(user_id)
        if not user:
            return None
            
        # Обновляем поля
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
            
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        # В реальности должно обращаться к auth-service
        user = self.get_user(user_id)
        return user is not None 