from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SAEnum,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker, joinedload
import uvicorn

DATABASE_URL = "sqlite:///./pigeon.db"
SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class UserRole(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    CASHIER = "cashier"

class ColumnType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.CASHIER)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    managed_users = relationship("User", backref="manager", remote_side=[id], foreign_keys=[manager_id])
    managed_points = relationship("Point", back_populates="manager", foreign_keys="[Point.manager_id]")

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    manager = relationship("User", back_populates="managed_points", foreign_keys=[manager_id])
    tables = relationship("TableMeta", back_populates="point", cascade="all, delete-orphan")
    cashiers = relationship("User", secondary="point_cashiers", backref="cashier_points")

class PointCashier(Base):
    __tablename__ = "point_cashiers"
    point_id = Column(Integer, ForeignKey("points.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

class TableMeta(Base):
    __tablename__ = "table_meta"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    point_id = Column(Integer, ForeignKey("points.id"), nullable=False)

    point = relationship("Point", back_populates="tables")
    columns = relationship("ColumnMeta", back_populates="table", cascade="all, delete-orphan")
    rows = relationship("Row", back_populates="table", cascade="all, delete-orphan")

class ColumnMeta(Base):
    __tablename__ = "column_meta"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_meta.id"), nullable=False)
    name = Column(String, nullable=False)
    col_type = Column(SAEnum(ColumnType), nullable=False)
    options = Column(JSON, nullable=True)

    table = relationship("TableMeta", back_populates="columns")

class Row(Base):
    __tablename__ = "rows"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_meta.id"), nullable=False)
    data = Column(JSON, nullable=False, default=dict)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    table = relationship("TableMeta", back_populates="rows")
    creator = relationship("User")

def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        owner = db.query(User).filter(User.role == UserRole.OWNER).first()
        if not owner:
            owner = User(
                username="owner",
                hashed_password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash("123456"),
                role=UserRole.OWNER
            )
            db.add(owner)
            db.commit()
            print("Default owner created (username: owner, password: 123456)")
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"--- DEBUG JWT ERROR: {e} ---") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    role = payload.get("role")
    if user_id is None or role is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole
    manager_id: Optional[int] = None
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole

class PointCreate(BaseModel):
    name: str
    address: Optional[str] = None
    manager_id: int

class ColumnOut(BaseModel):
    id: int
    name: str
    col_type: ColumnType
    options: Optional[List[str]] = None
    class Config:
        from_attributes = True

class TableOut(BaseModel):
    id: int
    name: str
    point_id: int
    columns: List[ColumnOut] = []
    class Config:
        from_attributes = True

class PointOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    manager_id: int
    cashiers: List[UserOut] = []
    tables: List[TableOut] = []
    class Config:
        from_attributes = True

class TableCreate(BaseModel):
    name: str

class ColumnCreate(BaseModel):
    name: str
    col_type: ColumnType
    options: Optional[List[str]] = None

class RowCreate(BaseModel):
    data: Dict[str, Any]

class RowOut(BaseModel):
    id: int
    table_id: int
    data: Dict[str, Any]
    created_by: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

app = FastAPI(title="Pigeon CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_router = __import__("fastapi").APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }

@auth_router.post("/token")
def login_for_swagger(form_data: OAuth2PasswordRequestForm = Depends(),
                      db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }

@auth_router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@auth_router.post("/impersonate/{manager_id}")
def impersonate(manager_id: int,
                current_user: User = Depends(require_role(UserRole.OWNER)),
                db: Session = Depends(get_db)):
    manager = db.query(User).filter(User.id == manager_id, User.role == UserRole.MANAGER).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    access_token = create_access_token(data={"sub": str(manager.id), "role": manager.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": manager.id,
            "username": manager.username,
            "role": manager.role
        }
    }

@auth_router.post("/impersonate-cashier/{cashier_id}")
def impersonate_cashier(cashier_id: int,
                        current_user: User = Depends(require_role(UserRole.MANAGER)),
                        db: Session = Depends(get_db)):
    cashier = db.query(User).filter(
        User.id == cashier_id,
        User.role == UserRole.CASHIER,
        User.manager_id == current_user.id
    ).first()
    if not cashier:
        raise HTTPException(status_code=404, detail="Cashier not found or not yours")
    access_token = create_access_token(data={"sub": str(cashier.id), "role": cashier.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": cashier.id,
            "username": cashier.username,
            "role": cashier.role
        }
    }

users_router = __import__("fastapi").APIRouter(prefix="/users", tags=["users"])

@users_router.post("/managers", response_model=UserOut)
def create_manager(user_data: UserCreate,
                   current_user: User = Depends(require_role(UserRole.OWNER)),
                   db: Session = Depends(get_db)):
    if user_data.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="Role must be manager")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    manager = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.MANAGER
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager

@users_router.get("/managers", response_model=List[UserOut])
def list_managers(current_user: User = Depends(require_role(UserRole.OWNER)),
                  db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == UserRole.MANAGER).all()

@users_router.post("/cashiers", response_model=UserOut)
def create_cashier(user_data: UserCreate,
                   current_user: User = Depends(require_role(UserRole.MANAGER)),
                   db: Session = Depends(get_db)):
    if user_data.role != UserRole.CASHIER:
        raise HTTPException(status_code=400, detail="Role must be cashier")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    cashier = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.CASHIER,
        manager_id=current_user.id
    )
    db.add(cashier)
    db.commit()
    db.refresh(cashier)
    return cashier

@users_router.get("/cashiers", response_model=List[UserOut])
def list_cashiers(current_user: User = Depends(require_role(UserRole.MANAGER)),
                  db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == UserRole.CASHIER, User.manager_id == current_user.id).all()

points_router = __import__("fastapi").APIRouter(prefix="/points", tags=["points"])

@points_router.post("/", response_model=PointOut)
def create_point(point_data: PointCreate,
                 current_user: User = Depends(require_role(UserRole.OWNER)),
                 db: Session = Depends(get_db)):
    manager = db.query(User).filter(User.id == point_data.manager_id, User.role == UserRole.MANAGER).first()
    if not manager:
        raise HTTPException(status_code=400, detail="Manager not found")
    point = Point(**point_data.dict())
    db.add(point)
    db.commit()
    db.refresh(point)
    return point

@points_router.get("/", response_model=List[PointOut])
def list_points(current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if current_user.role == UserRole.OWNER:
        return db.query(Point).all()
    elif current_user.role == UserRole.MANAGER:
        return db.query(Point).filter(Point.manager_id == current_user.id).all()
    else:
        return current_user.cashier_points

@points_router.get("/{point_id}", response_model=PointOut)
def get_point(point_id: int,
              current_user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    point = db.query(Point).filter(Point.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    if current_user.role == UserRole.OWNER:
        return point
    elif current_user.role == UserRole.MANAGER and point.manager_id == current_user.id:
        return point
    elif current_user.role == UserRole.CASHIER and point in current_user.cashier_points:
        return point
    raise HTTPException(status_code=403, detail="Access denied")

@points_router.post("/{point_id}/cashiers/{cashier_id}")
def assign_cashier_to_point(point_id: int, cashier_id: int,
                            current_user: User = Depends(require_role(UserRole.MANAGER)),
                            db: Session = Depends(get_db)):
    point = db.query(Point).filter(Point.id == point_id, Point.manager_id == current_user.id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found or not yours")
    cashier = db.query(User).filter(User.id == cashier_id, User.role == UserRole.CASHIER,
                                    User.manager_id == current_user.id).first()
    if not cashier:
        raise HTTPException(status_code=404, detail="Cashier not found or not yours")
    if db.query(PointCashier).filter(PointCashier.point_id == point_id,
                                     PointCashier.user_id == cashier_id).first():
        raise HTTPException(status_code=400, detail="Cashier already assigned")
    db.add(PointCashier(point_id=point_id, user_id=cashier_id))
    db.commit()
    return {"ok": True}

@points_router.delete("/{point_id}/cashiers/{cashier_id}")
def remove_cashier_from_point(point_id: int, cashier_id: int,
                              current_user: User = Depends(require_role(UserRole.MANAGER)),
                              db: Session = Depends(get_db)):
    point = db.query(Point).filter(Point.id == point_id, Point.manager_id == current_user.id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found or not yours")
    entry = db.query(PointCashier).filter(PointCashier.point_id == point_id,
                                          PointCashier.user_id == cashier_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Cashier not assigned to this point")
    db.delete(entry)
    db.commit()
    return {"ok": True}

@users_router.delete("/cashiers/{cashier_id}")
def delete_cashier(cashier_id: int,
                   current_user: User = Depends(require_role(UserRole.MANAGER)),
                   db: Session = Depends(get_db)):
    cashier = db.query(User).filter(
        User.id == cashier_id,
        User.role == UserRole.CASHIER,
        User.manager_id == current_user.id
    ).first()
    if not cashier:
        raise HTTPException(status_code=404, detail="Cashier not found or not yours")
    db.delete(cashier)
    db.commit()
    return {"ok": True}

tables_router = __import__("fastapi").APIRouter(prefix="/tables", tags=["tables"])

@tables_router.post("/points/{point_id}", response_model=TableOut)
def create_table(point_id: int, table_data: TableCreate,
                 current_user: User = Depends(require_role(UserRole.MANAGER)),
                 db: Session = Depends(get_db)):
    point = db.query(Point).filter(Point.id == point_id, Point.manager_id == current_user.id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found or not yours")
    table = TableMeta(name=table_data.name, point_id=point_id)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table

@tables_router.get("/points/{point_id}", response_model=List[TableOut])
def list_tables(point_id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    point = db.query(Point).filter(Point.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    if current_user.role == UserRole.OWNER:
        return point.tables
    elif current_user.role == UserRole.MANAGER and point.manager_id == current_user.id:
        return point.tables
    elif current_user.role == UserRole.CASHIER and point in current_user.cashier_points:
        return point.tables
    raise HTTPException(status_code=403, detail="Access denied")

@tables_router.post("/{table_id}/columns", response_model=ColumnOut)
def add_column(table_id: int, col_data: ColumnCreate,
               current_user: User = Depends(require_role(UserRole.MANAGER)),
               db: Session = Depends(get_db)):
    table = db.query(TableMeta).filter(TableMeta.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    point = db.query(Point).filter(Point.id == table.point_id, Point.manager_id == current_user.id).first()
    if not point:
        raise HTTPException(status_code=403, detail="Not your table")
    if col_data.col_type == ColumnType.SELECT and not col_data.options:
        raise HTTPException(status_code=400, detail="Options required for select column")
    column = ColumnMeta(
        table_id=table_id,
        name=col_data.name,
        col_type=col_data.col_type,
        options=col_data.options
    )
    db.add(column)
    db.commit()
    db.refresh(column)
    return column

@tables_router.delete("/columns/{column_id}")
def delete_column(column_id: int,
                  current_user: User = Depends(require_role(UserRole.MANAGER)),
                  db: Session = Depends(get_db)):
    column = db.query(ColumnMeta).filter(ColumnMeta.id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    table = db.query(TableMeta).filter(TableMeta.id == column.table_id).first()
    point = db.query(Point).filter(Point.id == table.point_id, Point.manager_id == current_user.id).first()
    if not point:
        raise HTTPException(status_code=403, detail="Not your column")
    db.delete(column)
    db.commit()
    return {"ok": True}

@tables_router.delete("/{table_id}")
def delete_table(table_id: int,
                 current_user: User = Depends(require_role(UserRole.MANAGER)),
                 db: Session = Depends(get_db)):
    table = db.query(TableMeta).filter(TableMeta.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    point = db.query(Point).filter(Point.id == table.point_id, Point.manager_id == current_user.id).first()
    if not point:
        raise HTTPException(status_code=403, detail="Not your table")
    db.delete(table)
    db.commit()
    return {"ok": True}

cash_router = __import__("fastapi").APIRouter(prefix="/cash-register", tags=["cash-register"])

def validate_row_data(table_id: int, data: Dict[str, Any], db: Session):
    columns = db.query(ColumnMeta).filter(ColumnMeta.table_id == table_id).all()
    col_dict = {c.name: c for c in columns}
    for col_name, value in data.items():
        if col_name not in col_dict:
            raise HTTPException(status_code=400, detail=f"Unknown column '{col_name}'")
        col = col_dict[col_name]
        if col.col_type == ColumnType.NUMBER:
            try:
                float(value)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail=f"Column '{col_name}' must be a number")
        elif col.col_type == ColumnType.DATE:
            try:
                datetime.fromisoformat(str(value))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Column '{col_name}' must be a date (YYYY-MM-DD)")
        elif col.col_type == ColumnType.SELECT:
            if value not in (col.options or []):
                raise HTTPException(status_code=400, detail=f"Value for '{col_name}' must be one of {col.options}")

@cash_router.get("/tables", response_model=List[TableOut])
def get_cashier_tables(current_user: User = Depends(require_role(UserRole.CASHIER)),
                       db: Session = Depends(get_db)):
    tables = []
    for point in current_user.cashier_points:
        tables.extend(point.tables)
    return tables

@cash_router.get("/tables/{table_id}", response_model=TableOut)
def get_cashier_table(table_id: int,
                      current_user: User = Depends(require_role(UserRole.CASHIER)),
                      db: Session = Depends(get_db)):
    table = db.query(TableMeta).options(joinedload(TableMeta.columns)).filter(TableMeta.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    point = table.point
    if point not in current_user.cashier_points:
        raise HTTPException(status_code=403, detail="Access denied")
    return table

@tables_router.get("/{table_id}", response_model=TableOut)
def get_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(TableMeta).options(joinedload(TableMeta.columns)).filter(TableMeta.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@cash_router.get("/tables/{table_id}/rows", response_model=List[RowOut])
def list_rows(table_id: int,
              current_user: User = Depends(require_role(UserRole.CASHIER)),
              db: Session = Depends(get_db)):
    table = db.query(TableMeta).filter(TableMeta.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    point = table.point
    if point not in current_user.cashier_points:
        raise HTTPException(status_code=403, detail="Access denied")
    return table.rows

@cash_router.post("/tables/{table_id}/rows", response_model=RowOut)
def create_row(table_id: int, row_data: RowCreate,
               current_user: User = Depends(require_role(UserRole.CASHIER)),
               db: Session = Depends(get_db)):
    table = db.query(TableMeta).filter(TableMeta.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    point = table.point
    if point not in current_user.cashier_points:
        raise HTTPException(status_code=403, detail="Access denied")

    validate_row_data(table_id, row_data.data, db)

    row = Row(
        table_id=table_id,
        data=row_data.data,
        created_by=current_user.id
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@cash_router.put("/rows/{row_id}", response_model=RowOut)
def update_row(row_id: int, row_data: RowCreate,
               current_user: User = Depends(require_role(UserRole.CASHIER)),
               db: Session = Depends(get_db)):
    row = db.query(Row).filter(Row.id == row_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    table = row.table
    point = table.point
    if point not in current_user.cashier_points:
        raise HTTPException(status_code=403, detail="Access denied")

    validate_row_data(table.id, row_data.data, db)
    row.data = row_data.data
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row

@cash_router.delete("/rows/{row_id}")
def delete_row(row_id: int,
               current_user: User = Depends(require_role(UserRole.CASHIER)),
               db: Session = Depends(get_db)):
    row = db.query(Row).filter(Row.id == row_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    table = row.table
    point = table.point
    if point not in current_user.cashier_points:
        raise HTTPException(status_code=403, detail="Access denied")
    db.delete(row)
    db.commit()
    return {"ok": True}

dashboard_router = __import__("fastapi").APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/owner")
def owner_dashboard(current_user: User = Depends(require_role(UserRole.OWNER)),
                    db: Session = Depends(get_db)):
    total_managers = db.query(User).filter(User.role == UserRole.MANAGER).count()
    total_points = db.query(Point).count()
    total_cashiers = db.query(User).filter(User.role == UserRole.CASHIER).count()
    today = datetime.utcnow().date()
    rows_today = db.query(Row).filter(
        Row.created_at >= today,
        Row.created_at < today + timedelta(days=1)
    ).count()
    return {
        "total_managers": total_managers,
        "total_points": total_points,
        "total_cashiers": total_cashiers,
        "rows_today": rows_today
    }

@dashboard_router.get("/manager")
def manager_dashboard(current_user: User = Depends(require_role(UserRole.MANAGER)),
                      db: Session = Depends(get_db)):
    my_points = db.query(Point).filter(Point.manager_id == current_user.id).all()
    point_ids = [p.id for p in my_points]
    total_tables = db.query(TableMeta).filter(TableMeta.point_id.in_(point_ids)).count()
    total_cashiers = db.query(PointCashier).filter(PointCashier.point_id.in_(point_ids)).count()
    today = datetime.utcnow().date()
    rows_today = db.query(Row).join(TableMeta).filter(
        TableMeta.point_id.in_(point_ids),
        Row.created_at >= today,
        Row.created_at < today + timedelta(days=1)
    ).count()
    return {
        "my_points": len(my_points),
        "total_tables": total_tables,
        "total_cashiers": total_cashiers,
        "rows_today": rows_today
    }

@dashboard_router.get("/cashier")
def cashier_dashboard(current_user: User = Depends(require_role(UserRole.CASHIER)),
                      db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    point_ids = [p.id for p in current_user.cashier_points]
    rows_today = db.query(Row).join(TableMeta).filter(
        TableMeta.point_id.in_(point_ids),
        Row.created_by == current_user.id,
        Row.created_at >= today,
        Row.created_at < today + timedelta(days=1)
    ).count()
    total_rows = db.query(Row).join(TableMeta).filter(
        TableMeta.point_id.in_(point_ids),
        Row.created_by == current_user.id
    ).count()
    return {
        "rows_today": rows_today,
        "total_rows": total_rows
    }

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(points_router)
app.include_router(tables_router)
app.include_router(cash_router)
app.include_router(dashboard_router)

@app.on_event("startup")
def startup_event():
    init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)