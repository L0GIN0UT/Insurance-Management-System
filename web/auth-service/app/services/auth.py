from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from ..config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
def get_db_session():
    """Get database session"""
    # TODO: Implement proper database session management
    # For now, return None - we'll implement this when we add database setup
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None



class AuthService:
    """Authentication service class"""
    
    def __init__(self):
        self.db = get_db_session()
        # Временное хранилище пользователей в памяти
        self.users = {}
        self.user_id_counter = 1
    
    def create_user(self, username: str, email: str, full_name: str, password: str, role: UserRole) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(password)
        user = User(
            id=self.user_id_counter,
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Сохраняем в временное хранилище
        self.users[username] = user
        self.user_id_counter += 1
        
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user by username/email and password"""
        # Проверяем тестового админа
        if username_or_email == "admin" and password == "admin":
            return User(
                id=999,
                username="admin",
                email="admin@example.com",
                full_name="Administrator",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("admin"),
                created_at=datetime.utcnow(),
                is_active=True
            )
        
        # Проверяем зарегистрированных пользователей - сначала по username
        user = self.get_user_by_username(username_or_email)
        if user and verify_password(password, user.hashed_password):
            return user
        
        # Если не найден по username, ищем по email
        user = self.get_user_by_email(username_or_email)
        if user and verify_password(password, user.hashed_password):
            return user
        
        return None

# Legacy functions for backward compatibility
def create_user(db: Session, user_data) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 