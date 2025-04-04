import pandas as pd

from sqlalchemy import select, func, or_

from database.Database_Model import User, Request, RequestLine, Material, Transaction, Warehouse, Project, Vendor, Keyword
from database.Database_Model import engine

from lib.types import TransactionType
from lib.types import RequestStatus
from lib.types import UserRole

# -------------------- Transaction -------------------- #

def get_all_transactions() -> pd.DataFrame:
    """
    Devuelve todas las transacciones
    
    Columnas: | Id | Type | PO_PO_Item | SO_SO_Item | User | Posting_date | Time | Transact_QTY | Notes |
    """
    df = pd.read_sql(
        select(Transaction)
    , engine)

    return df

def get_transactions_notes() -> pd.DataFrame:
    """
    Devuelve todas las notas de las transacciones

    Columnas: | Transaction id | Notes |
    """
    df = pd.read_sql(
        select(
            Transaction.Id.label("Transaction id"),
            Transaction.Notes
        )
    , engine)

    return df

def get_transactions_with_material_descriptions() -> pd.DataFrame:
    """
    Devuelve todas las transacciones con la informacion del material de la transaccion
    
    Columnas Transaccion: | Id | Type | PO_PO_Item | SO_SO_Item | User | Posting_date | Time | Transact_QTY | Notes |
    
    Columnas Material (PO_PO_Item): | Stock | Warehouse_Id | Vendor_Number | Short_Description | Long_Text | Project_Id | WBS | Pending_QTY_To_Receive |
    """
    df = pd.read_sql(
        select(Transaction, Material)
        .join(Material, Transaction.PO_PO_Item == Material.PO_PO_Item)
    , engine)

    return df

# -------------------- Request -------------------- #

def get_all_pending_requests() -> pd.DataFrame:
    """
    Devuelve todas las requests pendiented por atender

    Columnas: | Id | UserRequester | Status | Type | Posting_date | Time | WarehouseNotes | EndUser | Warehouse_Id | Project_Id |
    """
    df = pd.read_sql(
        select(Request)
        .where(Request.Status == "Requested")
    , engine)

    return df

def get_request_by_id(request_id: int) -> pd.DataFrame:
    """
    Devuelve una request por su id

    Columnas: | Id | UserRequester | Status | Type | Posting_date | Time | WarehouseNotes | EndUser | Warehouse_Id | Project_Id |
    """
    df = pd.read_sql(
        select(Request)
        .where(Request.Id == request_id)
    , engine)

    return df

def get_request_by_id_with_transaction_date_and_time() -> pd.DataFrame:
    """
    Devuelve una request con su fecha y hora de transaccion si ha sido atendida

    Columnas Request: | Id | UserRequester | Status | Type | Posting_date | Time | WarehouseNotes | EndUser | Warehouse_Id | Project_Id | 
    
    Columnas Transaction: | Transaction_Posting_Date | Transaction_Time |
    """
    df = pd.read_sql(
        select(
            Request,
            Transaction.Posting_date.label('Transaction_Posting_Date'),
            Transaction.Time.label('Transaction_Time')
        )
        .join(RequestLine, RequestLine.Request_Id == Request.Id)
        .join(Transaction, Transaction.Id == RequestLine.Transaction_Id)
        .where(or_(Request.Status == RequestStatus.ATTENDED.value, Request.Status == RequestStatus.DENIED.value))
        .group_by(Request.Id)
    , engine)

    return df

def get_request_by_id_with_transaction_date_and_time_by_requester(requester: str) -> pd.DataFrame:
    """
    Devuelve una request con su fecha y hora de transaccion si ha sido atendida

    Columnas Request: | Id | UserRequester | Status | Type | Posting_date | Time | WarehouseNotes | EndUser | Warehouse_Id | Project_Id | 
    Columnas Transaction: | Transaction_Posting_Date | Transaction_Time |
    """
    df = pd.read_sql(
        select(
            Request,
            Transaction.Posting_date.label('Transaction_Posting_Date'),
            Transaction.Time.label('Transaction_Time')
        )
        .join(RequestLine, RequestLine.Request_Id == Request.Id)
        .join(Transaction, Transaction.Id == RequestLine.Transaction_Id)
        .where(or_(Request.Status == RequestStatus.ATTENDED.value, Request.Status == RequestStatus.DENIED.value))
        .where(Request.UserRequester == requester)
        .group_by(Request.Id)
    , engine)

    return df

def get_pendig_request_by_requester(requester: str) -> pd.DataFrame:
    """
    Devuelve todas las request sin atender dado el requester

    Columnas: | Id | UserRequester | Status | Type | Posting_date | Time | WarehouseNotes | EndUser | Warehouse_Id | Project_Id |
    """
    df = pd.read_sql(
        select(Request)
        .where(Request.Status == "Requested")
        .where(Request.UserRequester == requester)
    , engine)

    return df

# -------------------- Request Line -------------------- #

def get_request_lines_by_request_id(request_id: int) -> pd.DataFrame:
    """
    Devuelve todas request lines de una request, dado el id de la request

    Columnas: | Id | Request_Id | Transaction_Id | PO_PO_Item | Requested_Qty | Status |
    """
    df = pd.read_sql(
        select(RequestLine)
        .where(RequestLine.Request_Id == request_id)
    , engine)

    return df

def get_request_lines_with_material_data_by_request_id(request_id: int) -> pd.DataFrame:
    """
    Devuelve todas las request lines junto con la información de Material, dado el id de la request.

    Columnas Request Line: | Id | Request_Id | Transaction_Id | PO_PO_Item | Requested_Qty | Status | 
    
    Columnas Material: | PO_PO_Item	| Stock	| Warehouse_Id | Vendor_Number | Short_Description | Long_Text | Project_Id | WBS | Pending_QTY_To_Receive |
    """
    # Realizamos un join entre RequestLine y Material
    df = pd.read_sql(
        select(RequestLine, Material)
        .join(Material, RequestLine.PO_PO_Item == Material.PO_PO_Item)
        .where(RequestLine.Request_Id == request_id)
    , engine)

    columns_to_show = ["Id", "Request_Id", "Transaction_Id", "PO_PO_Item", "Stock", "Requested_Qty", "Status", 
                       "Warehouse_Id", "Vendor_Number", "Short_Description", "Long_Text", "Project_Id", "WBS", "Pending_QTY_To_Receive"]
    
    df = df[columns_to_show]

    return df

# -------------------- Project -------------------- #

def get_all_projects() -> pd.DataFrame: 
    """
    Devuelve todos los proyectos

    Columnas: | Project_Id | Name | Manager | Closed | Modified_DateTime | Modifier |
    """

    df = pd.read_sql(
        select(Project)
    , engine)
    
    return df

def get_project_by_name(name: str) -> pd.DataFrame:
    """
    Devuelve un proyecto dado su nombre

    Columnas: | Id | Name | Manager | Closed | Modified_DateTime | Modifier |
    """
    df = pd.read_sql(
        select(Project)
        .where(Project.Name == name)
    , engine)

    return df

def get_project_by_manager(manager: str) -> pd.DataFrame:
    """
    Devuelve un proyecto dado su manager

    Columnas: | Id | Name | Manager | Closed | Modified_DateTime | Modifier |
    """
    df = pd.read_sql(
        select(Project.Id)
        .where(Project.Manager == manager)
    , engine)

    return df

def get_all_projects_with_available_materials() -> pd.DataFrame:
    """
    Devuelve todos los proyectos con materiales disponibles

    Columnas: | Project_Id | Name | Manager | Closed | Modified_DateTime | Modifier |
    """

    all_projects_df = pd.read_sql(
        select(Project)
    , engine)

    projects_with_available_materials = pd.read_sql(
        select(Material.Project_Id)
        .where(Material.Stock > 0).distinct()
    , engine)

    all_projects_df = all_projects_df.rename(columns={
        "Id": "Project_Id"
    })

    merged_df = pd.merge(projects_with_available_materials, all_projects_df, how='left', on='Project_Id')
    
    return merged_df

# -------------------- Material -------------------- #

def get_all_materials() -> pd.DataFrame:
    """
    Devuelve todos los materiales registrados
    
    Columnas: | PO_PO_Item | Stock | Warehouse_Id | Vendor_Number | Short_Description | Long_Text | Project_Id | WBS | Pending_QTY_To_Receive |
    """
    df = pd.read_sql(
        select(Material)
    , engine)

    return df

def get_all_available_materials() -> pd.DataFrame:
    """
    Devuelve todos los materiales disponibles
    
    Columnas: | PO_PO_Item | Stock | Warehouse_Id | Vendor_Number | Short_Description | Long_Text | Project_Id | WBS | Pending_QTY_To_Receive |
    """
    df = pd.read_sql(
        select(Material)
        .where(Material.Stock >= 1)
    , engine)

    return df

def get_material_by_id(po_po_item: str) -> pd.DataFrame:
    """
    Devuelve un material dado su id

    Columnas: | PO_PO_Item | Stock | Warehouse_Id | Vendor_Number | Short_Description | Long_Text | Project_Id | WBS | Pending_QTY_To_Receive |
    """
    df = pd.read_sql(
        select(Material)
        .where(Material.PO_PO_Item == po_po_item)
    , engine)

    return df

def get_available_materials_from_project_id(project_id: int) -> pd.DataFrame:
    """
    Devuelve los materiales disponibles de un proyecto dado el id del proyecto

    Columnas: | PO_PO_Item | Stock | Warehouse_Id | Vendor_Number | Short_Description | Long_Text | Project_Id | WBS | Pending_QTY_To_Receive |
    """
    df = pd.read_sql(
        select(Material)
        .where(Material.Project_Id == project_id, Material.Stock >= 1)
    , engine)

    return df

def get_materials_total_received_quantity() -> pd.DataFrame:
    """
    Devuelve un dataframe con todos los materiales y sus cantidad total recibida
    
    Columnas: | PO_PO_Item | TotalReceivedQuantity |
    """

    df = pd.read_sql(
        select(
            Material.PO_PO_Item,
            func.sum(Transaction.Transact_QTY).label('TotalReceivedQuantity')
        )
        .join(Transaction, Transaction.PO_PO_Item == Material.PO_PO_Item)
        .filter(Transaction.Type == TransactionType.DELIVERY.value)
        .group_by(Material.PO_PO_Item)
    , engine)

    return df

def get_materials_pending_requests() -> pd.DataFrame:
    """
    Devuelve un dataframe con todos los materiales y las request pendientes por atender de dicho material
    
    Columnas: | PO_PO_Item | PendingRequestsCount |
    """
    df = pd.read_sql(
        select(
            Material.PO_PO_Item,
            func.count(Request.Id).label('PendingRequestsCount')
        )
        .join(RequestLine, RequestLine.PO_PO_Item == Material.PO_PO_Item)
        .join(Request, Request.Id == RequestLine.Request_Id)
        .filter(Request.Status == 'Requested')
        .group_by(Material.PO_PO_Item)
    , engine)

    return df

# -------------------- Warehouse -------------------- #

def get_all_warehouses() -> pd.DataFrame:
    """
    Devuelve todos los almacenes
    
    Columnas: | Id | Name | Location |
    """
    df = pd.read_sql(
        select(Warehouse)
    , engine)

    return df

def get_warehouse_by_id(warehouse_id: int) -> pd.DataFrame:
    """
    Devuelve un almacen dado su id
    
    Columnas: | Id | Name | Location |
    """
    df = pd.read_sql(
        select(Warehouse)
        .where(Warehouse.Id == warehouse_id)
    , engine)

    return df

# -------------------- User -------------------- #
def get_all_users() -> pd.DataFrame:
    """
    Devuelve todos los usarios
    
    Columnas: | UserKey | Email | Password | Role |
    """
    df = pd.read_sql(
        select(User)
    , engine)

    return df


def get_admin_users() -> pd.DataFrame:
    """
    Devuelve todos los usarios con el rol de Admin
    
    Columnas: | UserKey | Email | Password | Role |
    """
    df = pd.read_sql(
        select(User)
        .where(User.Role == UserRole.ADMIN.value)
    , engine)

    return df

def get_manager_users() -> pd.DataFrame:
    """
    Devuelve todos los usarios con el rol de Manager
    
    Columnas: | UserKey | Email | Password | Role |
    """
    df = pd.read_sql(
        select(User)
        .where(User.Role == UserRole.MANAGER.value)
    , engine)

    return df

def get_requesters_users() -> pd.DataFrame:
    """
    Devuelve todos los usarios con el rol de Requester
    
    Columnas: | UserKey | Email | Password | Role |
    """
    df = pd.read_sql(
        select(User)
        .where(User.Role == UserRole.REQUESTER.value)
    , engine)

    return df

# -------------------- Vendors -------------------- #

def get_all_vendors() -> pd.DataFrame:
    """
    Devuelve todos los vendors
    
    Columnas: | Number | Company | ... |
    """
    df = pd.read_sql(
        select(Vendor)
    , engine)

    return df

def get_vendor_by_name(name: str) -> pd.DataFrame:
    """
    Devuelve un vendor dado su nombre

    Columnas: | Number | Company | ... |
    """
    df = pd.read_sql(
        select(Vendor)
        .where(Vendor.Company == name)
    , engine)

    return df

# -------------------- Keyword -------------------- #

def get_keywords_values() -> pd.DataFrame:
    """
    Devuelve las palabras claves registradas
    
    Columnas: | Value |
    """
    df = pd.read_sql(
        select(Keyword.Value)
    , engine)

    return df


