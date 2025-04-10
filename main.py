from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# База даних (SQLite)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
@app.get("/")
def root():
    return {"message": "Система управління студентськими гуртожитками працює!"}

# Моделі БД
class RoomDB(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    capacity = Column(Integer)
    occupied = Column(Boolean, default=False)
    condition = Column(String)


class StudentDB(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    has_booking = Column(Boolean, default=False)


class UtilityBillDB(Base):
    __tablename__ = "utility_bills"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    amount = Column(Float)
    due_date = Column(String)


class InventoryItemDB(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    quantity = Column(Integer)
    condition = Column(String)


# Створення таблиць у БД
Base.metadata.create_all(bind=engine)


# Pydantic моделі для API
class Room(BaseModel):
    id: int
    name: str
    capacity: int
    occupied: bool
    condition: str


class Student(BaseModel):
    id: int
    name: str
    room_id: int | None = None
    has_booking: bool = False


class UtilityBill(BaseModel):
    student_id: int
    amount: float
    due_date: str


class InventoryItem(BaseModel):
    id: int
    name: str
    quantity: int
    condition: str


# Функція для отримання сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD операції для кімнат
@app.post("/rooms/", response_model=Room)
def create_room(room: Room, db: Session = Depends(get_db)):
    db_room = RoomDB(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@app.get("/rooms/", response_model=list[Room])
def get_rooms(db: Session = Depends(get_db)):
    return db.query(RoomDB).all()


@app.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(RoomDB).filter(RoomDB.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


# CRUD операції для студентів
@app.post("/students/", response_model=Student)
def create_student(student: Student, db: Session = Depends(get_db)):
    db_student = StudentDB(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students/", response_model=list[Student])
def get_students(db: Session = Depends(get_db)):
    return db.query(StudentDB).all()


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# CRUD операції для комунальних платежів
@app.post("/utility_bills/", response_model=UtilityBill)
def create_utility_bill(bill: UtilityBill, db: Session = Depends(get_db)):
    db_bill = UtilityBillDB(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@app.get("/utility_bills/", response_model=list[UtilityBill])
def get_utility_bills(db: Session = Depends(get_db)):
    return db.query(UtilityBillDB).all()


# CRUD операції для інвентаризації
@app.post("/inventory/", response_model=InventoryItem)
def create_inventory_item(item: InventoryItem, db: Session = Depends(get_db)):
    db_item = InventoryItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/inventory/", response_model=list[InventoryItem])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(InventoryItemDB).all()


# Звіти про стан приміщень
@app.get("/rooms/{room_id}/condition")
def get_room_condition(room_id: int, db: Session = Depends(get_db)):
    room = db.query(RoomDB).filter(RoomDB.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"room_id": room.id, "condition": room.condition}


# Бронювання кімнати для студента
@app.post("/students/{student_id}/book_room/{room_id}")
def book_room(student_id: int, room_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    room = db.query(RoomDB).filter(RoomDB.id == room_id).first()

    if not student or not room:
        raise HTTPException(status_code=404, detail="Student or Room not found")

    if room.occupied:
        raise HTTPException(status_code=400, detail="Room is already occupied")

    student.room_id = room_id
    student.has_booking = True
    room.occupied = True

    db.commit()
    return {"message": f"Room {room_id} booked for student {student_id}"}
