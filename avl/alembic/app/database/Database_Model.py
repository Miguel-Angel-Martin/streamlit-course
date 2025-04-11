from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
import os

# Crear el motor
engine = create_engine(os.environ['DATABASE_URL'])

class Base(DeclarativeBase):
    pass

# Definición de las clases (tablas)
class User(Base):
    __tablename__ = 'User'
    UserKey = Column(String, primary_key=True)
    Email = Column(String, unique=True, nullable=False)
    Password = Column(String, nullable=False)
    Role = Column(String, nullable=False)

class Request(Base):
    __tablename__ = 'Request'
    Id = Column(Integer, primary_key=True)
    UserRequester = Column(String, ForeignKey('User.Email'), nullable=False)
    Status = Column(String, nullable=False)
    Type = Column(String, nullable=False)
    Posting_date = Column(Date, nullable=True)
    Time = Column(Time, nullable=True)
    WarehouseNotes = Column(String)
    EndUser = Column(String)
    Warehouse_Id = Column(Integer, ForeignKey('Warehouse.Id'), nullable=False)
    Project_Id = Column(String, ForeignKey('Project.Id'), nullable=False)
    Feedback_To_Requester = Column(String)
    Receiver = Column(String)
    Manufacturing_Destination = Column(String)

class RequestLine(Base):
    __tablename__ = 'RequestLine'
    Id = Column(Integer, primary_key=True)
    Request_Id = Column(Integer, ForeignKey('Request.Id'), nullable=False)
    Transaction_Id = Column(Integer, ForeignKey('Transaction.Id'))
    PO_PO_Item = Column(String, nullable=False)
    Requested_Qty = Column(Integer, nullable=False)
    Status = Column(String, nullable=False)

class Material(Base):
    __tablename__ = 'Material'
    PO_PO_Item = Column(String, primary_key=True)
    Stock = Column(Integer, nullable=False)
    Warehouse_Id = Column(Integer, ForeignKey('Warehouse.Id'), nullable=False)
    Vendor_Number = Column(String, nullable=False)
    Short_Description = Column(String)
    Long_Text = Column(String, nullable=False)
    Project_Id = Column(String, ForeignKey('Project.Id'), nullable=True)
    WBS = Column(String)
    Pending_QTY_To_Receive = Column(Integer)

class Transaction(Base):
    __tablename__ = 'Transaction'
    Id = Column(Integer, primary_key=True)
    Type = Column(String, nullable=False)
    PO_PO_Item = Column(String, ForeignKey('Material.PO_PO_Item'), nullable=False)
    SO_SO_Item = Column(String, nullable=True)
    User = Column(String, ForeignKey('User.UserKey'), nullable=False)
    Posting_date = Column(Date, nullable=True)
    Time = Column(Time, nullable=True)
    Transact_QTY = Column(Integer, nullable=False)
    Notes = Column(String, nullable=True)

class Warehouse(Base):
    __tablename__ = 'Warehouse'
    Id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    Location = Column(String, nullable=True)

class Project(Base):
    __tablename__ = 'Project'
    Id = Column(String, primary_key=True)
    Name = Column(String, nullable=True)
    Manager = Column(String, nullable=True)
    Closed = Column(Boolean, nullable=True)
    Modified_DateTime = Column(DateTime, nullable=True)
    Modifier = Column(String, nullable=True)

class Keyword(Base):
    __tablename__ = 'Keyword'
    Id = Column(Integer, primary_key=True)
    Value = Column(String, unique=True, nullable=False)
    
 # Todos los campos son opcionales
class Vendor(Base):
    __tablename__ = 'Vendor'
    Number = Column(String, primary_key=True)
    Company = Column(String, nullable=True)
    Search_Term = Column(String, nullable=True)
    Street1 = Column(String, nullable=True)
    Street2 = Column(String, nullable=True)
    City = Column(String, nullable=True)
    State = Column(String, nullable=True)
    Postal_Code = Column(String, nullable=True)
    Country = Column(String, nullable=True)
    Phone = Column(String, nullable=True)
    Fax = Column(String, nullable=True)
    VAT_Reg_No = Column(String, nullable=True)
    Risk = Column(String, nullable=True)
    ABC_Rating = Column(String, nullable=True)
    Currency = Column(String, nullable=True)
    DateOfEntry = Column(String, nullable=True)
    ISO_9001 = Column(String, nullable=True)
    ISO_14001 = Column(String, nullable=True)
    ISO_27001 = Column(String, nullable=True)
    Title = Column(String, nullable=True)
    First_Name = Column(String, nullable=True)
    Last_Name = Column(String, nullable=True)
    Department = Column(String, nullable=True)
    Position = Column(String, nullable=True)
    Email = Column(String, nullable=True)
    Cell_Phone_Number = Column(String, nullable=True)
    Contact_Number = Column(String, nullable=True)
    Contact_City = Column(String, nullable=True)
    Contact_Country = Column(String, nullable=True)

class GR_File(Base):
    __tablename__ = 'GR_File'
    Date = Column(Date, primary_key=True)

# Crear todas las tablas
Base.metadata.create_all(engine)
