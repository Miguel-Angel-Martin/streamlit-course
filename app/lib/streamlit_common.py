import asyncio
import os
import streamlit as st

from bs4 import BeautifulSoup

from lib.db import transaction
from lib.logging import logger
from lib.notifications import send_request_notification
from lib.types import TransactionType, RequestStatus, RequestType, UserRole, EmailType

# Pandas
import pandas as pd
from pandas.api.types import ( # filter_dataframe
    is_categorical_dtype,
    is_numeric_dtype
)

# SQLAlchemy
from sqlalchemy.orm import Session
from sqlalchemy import Date, select, delete

from database.Database_Model import User, Request, RequestLine, Material, Transaction, Warehouse, Project, Keyword, Vendor, GR_File
from database.Database_Model import engine

from datetime import datetime

from .auth import get_user_auth, get_user_groups_and_account

PAGE_TITLE = "Material Tracker"
PAGE_ICON = "resources/AvlLogo.png"
PAGE_LOGO = "resources/AvlGreenLogo.png"

MANAGER_LANDING_PAGE = "pages/Request_1_AllPendingRequests.py"
REQUESTER_LANDING_PAGE = "pages/Request_3_Make_Request.py"

# Devuelve el rol de la sesion
def get_session_role():
    return  st.session_state.user.get('role', UserRole.REQUESTER.value)

# Oculta el menu de streamlit
def streamlit_remove_hamburguer():
    hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Inicializacion de la sidebar comun de todas las paginas
def common_page_initialization(currentPage: str) -> bool:

    # Configuracion de la pagina: debe ejecutarse primero
    st.set_page_config(
        page_title = PAGE_TITLE,
        page_icon = PAGE_ICON,
        layout = "wide"
    )

    st.logo(PAGE_LOGO, size="large")

    streamlit_remove_hamburguer()

    if 'user' not in st.session_state:

        if "FORCE_AUTH" in os.environ:
            auth_data = os.environ["FORCE_AUTH"].split(":")
            st.session_state.user = {
                'id': auth_data[0],
                'email': auth_data[1]
            }
        else:
            avl_auth_process(
                os.getenv("OAUTH_REDIRECT_URL"),
                os.getenv("THIS_WEB_URL"),
                os.getenv("OAUTH_CLIENT_ID"),
                os.getenv("OAUTH_CLIENT_SECRET"),
                os.getenv("LDAP_ACCOUNT"),
                os.getenv("LDAP_PASS")
            )

        with transaction() as tx:
            user = tx.query(User).filter(User.UserKey == st.session_state.user['id']).first()
            if not user:
                user = User(UserKey=st.session_state.user['id'], Email=st.session_state.user['email'], Role=UserRole.REQUESTER.value, Password='')
                tx.add(user)
                logger.info(f"User {st.session_state.user['id']} created")
            st.session_state.user['role'] = user.Role or UserRole.REQUESTER.value

        logger.debug(f"User logged in: {st.session_state.user}")
        

    # Mostrar el rol del usuario en la barra lateral
    st.sidebar.header(f"{st.session_state['user']['id']}: Logged in as {get_session_role()}", divider="gray")

    # Dependiendo del rol las paginas disponibles seran unas u otras
    if get_session_role() == UserRole.MANAGER.value or get_session_role() == UserRole.ADMIN.value:
        st.sidebar.write
        st.sidebar.header("Requests")
        st.sidebar.page_link("pages/Request_1_AllPendingRequests.py", label = "📝 Pending Requests")
        st.sidebar.page_link("pages/Request_2_AllRequestHistory.py", label = "📚 Request History")
        st.sidebar.subheader("", divider = "gray")
        st.sidebar.page_link("pages/Request_4_OwnPendingRequests.py", label = "📬 My Pending Requests")
        st.sidebar.page_link("pages/Request_5_OwnRequestsHistory.py", label = "🛍️ My Request History")
        st.sidebar.page_link("pages/Request_3_Make_Request.py", label = "🛒 Make Request")
        st.sidebar.subheader("", divider = "gray")
        st.sidebar.header("Transactions")
        st.sidebar.page_link("pages/Transactions_1_TransactionsHistory.py", label = "📜 Transactions History") 
        st.sidebar.page_link("pages/Transactions_2_ImportTransactions.py", label = "🚚 Import Transactions")
        st.sidebar.page_link("pages/Transactions_3_TransferIn.py", label = "🚛 Transfer In")
        st.sidebar.page_link("pages/Transactions_4_TransferOut.py", label = "📦 Transfer Out")
        st.sidebar.subheader("", divider = "gray")
        st.sidebar.header("Inventory")
        st.sidebar.page_link("pages/Inventory_1_Materials.py", label = "🗂️ Materials")
        st.sidebar.page_link("pages/Inventory_2_Update_Materials.py", label = "🔄 Update Materials")
        st.sidebar.subheader("", divider = "gray")
        st.sidebar.header("Settings")
        st.sidebar.page_link("pages/Settings.py", label = "🧰 Settings")
        st.sidebar.page_link("pages/ChatBot.py", label = "ChatBot")
        
    else:
        st.sidebar.header("Requests")
        st.sidebar.page_link("pages/Request_3_Make_Request.py", label = "🛒 Make Request")
        st.sidebar.page_link("pages/Request_4_OwnPendingRequests.py", label = "📬 My Pending Requests")
        st.sidebar.page_link("pages/Request_5_OwnRequestsHistory.py", label = "🛍️ My Request History")
        st.sidebar.subheader("", divider = "gray")

    

    # Dependiendo del rol la pagina de landing sera una u otra
    if currentPage == "app.py":
        match get_session_role():
            case UserRole.MANAGER.value:
                st.switch_page(MANAGER_LANDING_PAGE)
            case _:
                st.switch_page(REQUESTER_LANDING_PAGE)

    if "successmsg" in st.session_state:
        st.toast(st.session_state["successmsg"])
        del st.session_state["successmsg"]
    if "errormsg" in st.session_state:
        st.toast(st.session_state["errormsg"])
        del st.session_state["errormsg"]

# ------------------------------ Filtros para ficheros ------------------------------ #

# Devuelve la fecha y un dataframe con todas las lineas validas de un gr file
def clean_GR_html(html_content: str, filter_: bool):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Obtener la fecha (de la primera tabla, 4º fila, 2º columna)
    tables = soup.find_all('table')
    
    fecha = None
    if len(tables) > 0:
        table = tables[0]
        fecha = table.find_all('tr')[3].find_all('td')[1].get_text(strip=True)
    
    # 2. Crear un DataFrame con todas las lineas de las demas tablas
    all_data = []
    headers = None  # Inicializar encabezado como None
    for table in tables[1:]: # Empezar desde la segunda tabla
        rows = table.find_all('tr')
        headers = [col.get_text(strip=True) for col in rows[0].find_all('td')]
        # Procesar las filas restantes (sin la primera)
        for row in rows[1:]:
            # Extraer todas las celdas de la fila
            cols = row.find_all(['td', 'th'])
            cols = [col.get_text(strip=True) for col in cols]
            
            if cols:
                all_data.append(cols)
    
    # Si el dataframe no esta vacio   
    if len(all_data[0]) > 1:
        # Crear un DataFrame con los datos extraídos
        df = pd.DataFrame(all_data)
        
        # 3. Filtrar los datos según las condiciones
        # Filtrar filas donde la primera columna comienza con '*'
        df = df[~df[0].str.startswith('*', na=False)]
        
        # Filtrar filas donde la tercera columna no está vacia y no contiene un punto '.'
        df = df[~((df[2].notna()) & (df[2] != '') & ~df[2].str.contains(r'\.', na=False))]

        # Filtrar filas donde la columna 16 tiene alguna subcadena de GR_FILES_KEYWORDS
        if filter_:
            keywords_df = pd.read_sql(
                select(Keyword.Value)
            , engine)
            keyword_list = keywords_df['Value'].tolist()

            print(f'filtro: keyword_list')
            print('df sin filtro')
            print(df)
            df = df[df[16].str.contains('|'.join(keyword_list), na=False)]
            print('df filtrado')
            print(df)

        # Filtrar filas donde las columnas 8, 9 y 10 contienen números decimales
        def es_decimal(valor):
            try:
                float(valor)
                return True
            except ValueError:
                return False
        
        df = df[df[7].apply(es_decimal)]
        df = df[df[8].apply(es_decimal)]
        df = df[df[9].apply(es_decimal)]
        
        if headers:
            df.columns = headers
            
    # Si no hay nada devolver dataframe vacio
    else:
        df = pd.DataFrame()
        
    
    return fecha, df

# Obtiene una lista con todas las filas de los dataframes del fichero que pertenecen a materiales registrados
def get_all_PO_quantities_to_update(dataframes: list[pd.DataFrame]) -> pd.DataFrame:

    materials_po_items_df = pd.read_sql(
        select(Material.PO_PO_Item)
    , engine)

    materials_po_items = set(materials_po_items_df.iloc[:, 0].astype(str))
    filtered_data = []
    
    for df in dataframes:
        cleaned_df = clean_PO_dataframe(df)  # Limpiar el DataFrame
        
        # Filtrar solo las filas que tienen PO.PO_Item en materials_po_items sin crear la columna
        filtered_df = cleaned_df[
            cleaned_df.apply(lambda row: f"{row.iloc[0]}.{row.iloc[1]}", axis=1).isin(materials_po_items)
        ]

        # Agregar las filas filtradas a la lista de datos
        filtered_data.extend(filtered_df.values.tolist())

    # Convertir la lista de datos filtrados en un DataFrame
    filtered_dataframe = pd.DataFrame(filtered_data, columns=cleaned_df.columns)

    return filtered_dataframe

# Transformar la primera fila del dataframe en los nombres de la columna, y filas especificas de un PO file
def clean_PO_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    # El campo de Short Text a veces viene con un colspan de 3, triplicando la columna al leerla con el pandas
    # Borrar las columnas triplicadas ya que solo interesa el campo de cantidad
    if len(df.columns) > 18:
        df = df.drop(columns=[8,9])

    # Establecer la primera fila como nombres de las columnas
    df.columns = df.iloc[0]
    
    # Eliminar la primera fila y resetear el índice
    df = df.drop(0).reset_index(drop=True)  

    # Filtrar las filas donde la primera columna no empieza con '*'
    df = df[~df.iloc[:, 0].astype(str).str.startswith("*")]

    return df

# ------------------------------ Base de datos ------------------------------ #

# Consulta si la fecha de un gr esta registrada
def is_gr_file_registered(gr_date: Date) -> bool:
    existing_gr_file = pd.read_sql(
        select(GR_File)
        .where(GR_File.Date == gr_date)
    , engine)

    return not existing_gr_file.empty

# Determina el id del proyecto de un material mediante su wbs element
def determine_project_id(wbs_element: str, so: str, order: str) -> str:
    if wbs_element:
        return f"GPN{wbs_element.split('.')[1]}"
    elif so:
        return f"SO{so[-4:]}"
    elif order:
        return f"IO{order[-4:]}"
    else:
        return None

# ----- Adds ----- #

# Guarda una fecha de un gr si no esta registrado
def add_gr_file(gr_date: Date, session: Session) -> bool:
    try:
        if not is_gr_file_registered(gr_date):
            # Registrar la fecha del GR file
            new_GR_File = GR_File(
                Date = gr_date
            )
            session.add(new_GR_File)
        return True
        
    except Exception as e:
        print(f"There was an error processing the GR date: {e}")
        return False

# Guarda transaccion, material y proyecto del material en la session
def add_transaction_and_material_data(transaction_data: dict, material_data: dict, session: Session) -> bool:
    # Guardar el proyecto si no existe
    project_id = material_data["Project_Id"]
    if not add_new_project_if_not_exists(project_id, session):
        return False

    # Crear y guardar la transaccion
    if not add_transaction(transaction_data, session):
        return False

    # Crear y guardar el material
    if not add_material(material_data, session):
        return False
    
    return True

# Guarda una transaccion en la session
def add_transaction(transaction_data: dict, session: Session) -> bool:
    try:
        new_transaction = Transaction(**transaction_data)
        session.add(new_transaction)
        return True

    except Exception as e:
        print(f"There was an error saving the transaction: {e}")
        return False

# Guarda un material en la session
def add_material(material_data: dict, session) -> bool:
    try:
        # Verificar si el material ya existe en la base de datos
        po_po_item = material_data["PO_PO_Item"]
        existing_material = session.query(Material).filter(Material.PO_PO_Item == po_po_item).first()

        if existing_material:
            # Si el material existe, actualizamos el stock sumando la cantidad
            existing_material.Stock += material_data["Stock"]
        else:
            # Si el material no existe, creamos uno nuevo
            new_material = Material(**material_data)
            session.add(new_material)

        return True  # Si todo va bien, devolvemos True

    except Exception as e:
        print(f"There was an error saving the material: {e}")
        return False
 
# Guarda un proyecto si no existe
def add_new_project_if_not_exists(project_id: str, session: Session) -> bool:
    try:
        # Verificar si el proyecto ya existe
        project = session.query(Project).filter(Project.Id == project_id).first()
        
        if not project:
            # Si no existe, creamos un nuevo proyecto
            new_project = Project(Id=project_id)
            session.add(new_project)
        return True
    except Exception as e:
        print(f"There was an error saving the project: {e}")
        return False

# Lee la informacion de una transaccion de una gr line y lo devuelve en forma de diccionario
def process_transaction_data_from_gr_line(gr_line_df: pd.DataFrame) -> dict:
    po = str(gr_line_df.iloc[0])
    po_item = str(gr_line_df.iloc[1])
    po_po_item = f"{po}.{po_item}"
    so = str(gr_line_df.iloc[3]) if str(gr_line_df.iloc[3]) != "nan" else None
    so_item = str(gr_line_df.iloc[4]) if str(gr_line_df.iloc[4]) != "nan" else None
    so_so_item = f"{so}.{so_item}" if so and so_item else None
    transaccion_qty = int(gr_line_df.iloc[7])
    # Convertir posting_date a datetime.date
    posting_date_str = str(gr_line_df.iloc[12])
    posting_date = datetime.strptime(posting_date_str, '%d.%m.%Y').date() if posting_date_str != 'nan' else None
    user = str(gr_line_df.iloc[14])
    # Convertir time a datetime.time
    time_str = str(gr_line_df.iloc[15])
    time = datetime.strptime(time_str, '%H:%M:%S').time() if time_str != 'nan' else None

    return {
        "Type": "Delivery",
        "PO_PO_Item": po_po_item,
        "SO_SO_Item": so_so_item,
        "User": user,
        "Posting_date": posting_date,
        "Time": time,
        "Transact_QTY": transaccion_qty
    }

# Lee la informacion de un material de una gr line y lo devuelve en forma de diccionario
def process_material_data_from_gr_line(gr_line_df: pd.DataFrame) -> dict:
    po = str(gr_line_df.iloc[0])
    po_item = str(gr_line_df.iloc[1])
    po_po_item = f"{po}.{po_item}"
    wbs_element = str(gr_line_df.iloc[2]) if str(gr_line_df.iloc[2]) != "nan" else None
    so = str(gr_line_df.iloc[3]) if str(gr_line_df.iloc[3]) != "nan" else None
    material = str(gr_line_df.iloc[5]) if str(gr_line_df.iloc[5]) != "nan" else None
    material_description = str(gr_line_df.iloc[6]) if str(gr_line_df.iloc[6]) != "nan" else None
    transaccion_qty = int(gr_line_df.iloc[7])
    vendor_number = str(gr_line_df.iloc[17])
    order = str(gr_line_df.iloc[20])
    
    # Determinar el project_id
    project_id = determine_project_id(wbs_element, so, order)
    if not project_id:
        return None
    
    return {
        "PO_PO_Item": po_po_item,
        "Stock": transaccion_qty,
        "Warehouse_Id": 1,  # TODO de momento guardarlo todo en un almacen general
        "Vendor_Number": vendor_number,
        "Short_Description": material,
        "Long_Text": material_description,
        "Project_Id": project_id,
        "WBS": wbs_element
    }

# ----- Saves ----- #

# Registra las lineas de un gr file, creando transacciones, materiales
def save_gr_lines_data(selected_gr_lines_df: pd.DataFrame, gr_date: Date) -> bool:
    with Session(engine) as session:
        try:
            for index, gr_line_df in selected_gr_lines_df.iterrows():
                transaction_data = process_transaction_data_from_gr_line(gr_line_df)
                material_data = process_material_data_from_gr_line(gr_line_df)

                # Ignorar linea si no se puede determinar toda la informacion de un material
                if not material_data:
                    continue

                if not add_transaction_and_material_data(transaction_data, material_data, session):
                    session.rollback(); return False
            
            if not add_gr_file(gr_date, session):
                session.rollback(); return False
                
            # Registrar informacion
            session.commit(); return True

        except Exception as e:
            print(f"There was an error processing the GR data: {e}")
            session.rollback(); return False

def save_transfer_in(transaction_data: dict, material_data: dict) -> bool:
    with Session(engine) as session:

        transaction_data["Posting_date"] = datetime.now().date()
        transaction_data["Time"] = datetime.now().time()

        try:
            if not add_transaction_and_material_data(transaction_data, material_data, session):
                session.rollback(); return False

            # Registrar informacion
            session.commit(); return True

        except Exception as e:
            print(f"There was an error processing the GR data: {e}")
            session.rollback(); return False

# Descarta un material registrado
def save_transfer_out(material_po_po_item: str, transaccion_qty: int, notes: str) -> bool:
    with Session(engine) as session:
        try:
            # Fecha de la transaccion
            posting_date = datetime.now().date()
            posting_time = datetime.now().time()
            
            new_transaction_data = {
                "Type": TransactionType.DISCARD.value,
                "PO_PO_Item": material_po_po_item,
                "SO_SO_Item": None,
                "User": "UxxAxx",  # TODO cambiar cuando se tenga autenticacion
                "Posting_date": posting_date,
                "Time": posting_time,
                "Transact_QTY": transaccion_qty,
                "Notes": notes
            }
            
            if not add_transaction(new_transaction_data, session):
                session.rollback()
                return False

            material_data = {
                "PO_PO_Item": material_po_po_item,
                "Stock": -int(transaccion_qty)
            }
            
            # Actualizar stock del material
            if not add_material(material_data, session):
                session.rollback()
                return False
            
            # Registrar informacion
            session.commit()
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

def add_keyword(keyword: str) -> bool:
    new_keyword = Keyword(Value=keyword)
    with Session(engine) as session:
        try:
            session.add(new_keyword)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error: La palabra clave '{keyword}' ya existe.")
            return False

def remove_keyword(keyword: str) -> bool:
    with Session(engine) as session:
        keyword_to_remove = session.query(Keyword).filter(Keyword.Value == keyword).first()
        if keyword_to_remove:
            try:
                session.delete(keyword_to_remove)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(f"Error al eliminar la palabra clave: {e}")
                return False
        else:
            print(f"No se encontró la palabra clave '{keyword}' para eliminar.")
            return False

# ----- Updates ----- #

def update_user_role(user_key: str, new_role: str) -> bool:
    """Actualiza el rol del usuario dado su UserKey y nuevo rol"""
    with Session(engine) as session:
        try:
            user = session.query(User).filter_by(UserKey = user_key).first()
            user.Role = new_role
            session.commit(); return True
        except Exception as e:
            print(f"Error: There was a problem trying to update the user role. {e}")
            session.rollback(); return False

# Actualiza las cantidades pendientes a recibir de un material dado el dataframe de un PO file
def update_quantities_to_receive(materials_to_update: pd.DataFrame) -> bool:
    with Session(engine) as session:
        try:
            # Para cada material, le sumamos la cantidad de la actualización a su cantidad pendiente a recibir
            for index in materials_to_update.index:
                po_po_item = f"{materials_to_update.at[index, materials_to_update.columns[0]]}.{materials_to_update.at[index, materials_to_update.columns[1]]}"
                quantity_to_add = int(materials_to_update.at[index, materials_to_update.columns[10]])

                # Buscar el material correspondiente
                material = session.query(Material).filter_by(PO_PO_Item = po_po_item).first()

                # Actualizar la cantidad pendiente a recibir
                if material:
                    material.Pending_QTY_To_Receive = quantity_to_add
                    session.add(material)

            # Actualizar la informacion de los materiales
            session.commit(); return True
    
        except Exception as e:
            print(f"Error: There was a problem trying to update quantities. {e}")
            session.rollback(); return False

# Logica para denegar una request por id
def deny_request_by_id(request_id: int, feedback_to_requester: str) -> bool:
    with Session(engine) as session:
        try:
            request = session.get(Request, request_id)

            # Cambiar de estado la request e introducir nueva informacion
            request.Status = RequestStatus.DENIED.value
            request.Feedback_To_Requester = feedback_to_requester

            # Obtener todas las request lines asociadas a la request
            request_lines = session.query(RequestLine).filter(RequestLine.Request_Id == request_id).all()
            # Fecha en la que se realiza la request
            posting_date = datetime.now().date()
            time = datetime.now().time()

            # Denegar todas las lineas de request y crear una transaccion por cada una de ellas
            for line in request_lines:
                line.Status = RequestStatus.DENIED.value
                new_transaction = Transaction(
                    Type = TransactionType.DENY_REQUEST.value,
                    PO_PO_Item = line.PO_PO_Item,
                    User = st.session_state.user['id'],
                    Posting_date = posting_date,
                    Time = time,
                    Transact_QTY = 0
                )

                # Guardar transaccion para asignarle a la linea de request el id de la transaccion sin problemas
                session.add(new_transaction)
                session.commit()
                line.Transaction_Id = new_transaction.Id
                session.add(line)
                
            session.commit()
            send_request_notification(request, EmailType.DENIED.value)
            return True
                
        except Exception as e:
            print(f"There was an error denying the request: {e}")
            session.rollback(); return False

# Logica para aceptar una request por id
def accept_request_by_id(request_id: int, feedback_to_requester: str, receiver: str, manufacturing_destination: str) -> bool:
    with Session(engine) as session:
        try:
            request = session.get(Request, request_id)
            request_lines = session.query(RequestLine).filter(RequestLine.Request_Id == request_id).all()
            request_type = request.Type

            # Fecha de la request
            posting_date = datetime.now().date()
            time = datetime.now().time()

            for line in request_lines:
                material = session.query(Material).filter(Material.PO_PO_Item == line.PO_PO_Item and line.Id == request_id).first()
                requested_qty = int(line.Requested_Qty)
                stock = int(material.Stock)
                
                new_transaction = Transaction(
                    PO_PO_Item = line.PO_PO_Item,
                    User = st.session_state.user['id'],
                    Posting_date = posting_date,
                    Time = time,
                    Transact_QTY = requested_qty
                )
                
                # Si la request es total, comprobar que se pueden aceptar todas las request lines, si no, se cancela el proceso de aceptar la request
                if request_type == RequestType.TOTAL.value:
                    if not stock >= requested_qty:
                        print(f"Not enough stock")
                        return False
                    else:
                        new_transaction.Type = TransactionType.ATTEND_REQUEST.value
                        line.Status = RequestStatus.ATTENDED.value
                        material.Stock -= requested_qty

                if request_type == RequestType.PARTIAL.value:
                    if not stock >= requested_qty:
                        if stock == 0:
                            new_transaction.Type = TransactionType.DENY_REQUEST.value
                            new_transaction.Notes = "Denied due to insufficient stock"
                            line.Status = RequestStatus.DENIED.value
                        else:
                            new_transaction.Type = TransactionType.ATTEND_REQUEST.value
                            new_transaction.Notes = f"Only {stock} of {requested_qty} delivered due to insufficient stock"
                            new_transaction.Transact_QTY = stock
                            line.Status = RequestStatus.ATTENDED.value
                            material.Stock = 0
                    else:
                        new_transaction.Type = TransactionType.ATTEND_REQUEST.value
                        line.Status = RequestStatus.ATTENDED.value
                        material.Stock -= requested_qty

                session.add(line)
                session.add(new_transaction)
                session.commit()

                line.Transaction_Id = new_transaction.Id
                session.add(line)

            # Cambiar de estado la request e introducir nueva informacion
            request.Status = RequestStatus.ATTENDED.value
            request.Feedback_To_Requester = feedback_to_requester
            request.Receiver = receiver
            request.Manufacturing_Destination = manufacturing_destination

            session.commit()
            send_request_notification(request, EmailType.ACCEPTED.value)
            return True

        except Exception as e:
            print(f"There was an error processing the transaction: {e}")
            session.rollback(); return False

# Logica para crear una request dado un diccionario con la informacion de la interfaz desde la que se crea
def save_request(request_data: dict) -> bool:
    selected_project_id = request_data['selected_project_id']
    selected_warehouse_id = request_data['selected_warehouse_id']
    selected_type_of_request = request_data['selected_type_of_request']
    available_materials_df = request_data['available_materials_df']
    selected_materials_df = request_data['selected_materials_df']
    materials_quantities = request_data['materials_quantities']
    end_user = request_data['end_user']
    warehouse_notes = request_data['warehouse_notes']

    with Session(engine) as session:
        try:
            # Crear nueva request
            new_request = Request(
                UserRequester = st.session_state.user['email'],
                Status = RequestStatus.REQUESTED.value,
                Type = selected_type_of_request,
                Posting_date = datetime.now().date(),
                Time = datetime.now().time(),
                WarehouseNotes = warehouse_notes,
                EndUser = end_user,
                Warehouse_Id = selected_warehouse_id,
                Project_Id = selected_project_id
            )

            # Registrar request
            session.add(new_request)
            session.commit()  # Realizar el commit para que la request tenga un Id asignado
            request_id = new_request.Id

            # Crear las request lines para cada material seleccionado
            for index in range(len(selected_materials_df.selection.rows)):
                selected_index = selected_materials_df.selection.rows[index]
                cantidad = materials_quantities[index]
                
                material_df = available_materials_df.iloc[selected_index]
                material_po_item = material_df["PO.PO Item"]
                
                new_request_line = RequestLine(
                    Request_Id = request_id,
                    PO_PO_Item = material_po_item,
                    Requested_Qty = cantidad,
                    Status = RequestStatus.REQUESTED.value
                )

                session.add(new_request_line)

            session.commit()
            send_request_notification(new_request, EmailType.PENDING_APROVAL.value)
            return True

        except Exception as e:
            print(f"Error: There was a problem trying to make the request. {e}")
            session.rollback(); return False

# ------------------------------ Reruns ------------------------------ #

# Rerun con mensaje de exitoS
def rerun_with_success(message: str):
    st.session_state["successmsg"] = f"✅ {message}"
    st.rerun()

# Rerun con mensaje de error
def rerun_with_error(message: str):
    st.session_state["errormsg"] = f"❌ {message}"
    st.rerun()

# ------------------------------ Interfazes ------------------------------ #

# Despliega un mensaje central propio para cuando no hay resultados al consultar informacion
def no_results_message(message: str):
    st.markdown(f"<h3 style='text-align: center; color: grey;'>{message}</h3>", unsafe_allow_html=True)

# ------------------------------ Otros ------------------------------ #

# Guarda automaticamente transacciones dado el contenido del fichero de un gr
def process_gr_file_auto(html_content: str):
    try:
        gr_file_data = clean_GR_html(html_content, True)
        new_transactions_date = datetime.strptime(gr_file_data[0], '%d.%m.%Y').date()
        gr_file_lines_df = gr_file_data[1]
        save_gr_lines_data(gr_file_lines_df, new_transactions_date)
    except Exception as e:
        st.error(f"GR file processing error: {e}")

def process_po_file_auto(html_content: str):
    try:
        dataframes = pd.read_html(html_content)
        materials_to_update = get_all_PO_quantities_to_update(dataframes)
        update_quantities_to_receive(materials_to_update)
    except Exception as e:
        st.error(f"PO file processing error: {e}")

# Cambia los numeros del vendor por el nombre del vendor que esta asociado a ese numero
# (La columna no debe haber sido renombrada)
def change_id_of_vendors_by_name(df: pd.DataFrame) -> pd.DataFrame:
    for index, value in enumerate(df["Vendor_Number"]):
        with Session(engine) as session:
            vendor_name = session.execute(
                select(Vendor.Company)
                .where(Vendor.Number == value)).fetchone() # Devuelve una tupla con los resultados
            
            if vendor_name:
                df.at[index, "Vendor_Number"] = vendor_name[0]

    return df

# Devuelve las lineas de una request con la informacion de sus respectivos materiales
# (La columna no debe haber sido renombrada)
def merge_materials_data_to_request_lines_df(request_lines_df: pd.DataFrame) -> pd.DataFrame:
    # Elegir orden y columnas a mostrar
    columns_to_show = ["Id", "Transaction_Id", "PO_PO_Item", "Status", "Requested_Qty"]
    request_lines_df = request_lines_df[columns_to_show]

    # Renombrar las columnas que se quiera
    request_lines_df = request_lines_df.rename(columns = {
        "Id": "Request line id",
        "Transaction_Id": "Transaction id",
        "PO_PO_Item": "PO.PO Item",
        "Requested_Qty": "Requested quantity"
    })

    # Dataframe de materiales con la informacion que queremos
    materials_df = pd.read_sql(
        select(Material)
    , engine)

    # Elegir columnas a mostrar
    columns_to_show = ["PO_PO_Item", "Vendor_Number", "Short_Description", "Long_Text", "Project_Id", "WBS", "Stock"]
    materials_df = materials_df[columns_to_show]

    # En vez de los numeros del vendor, se muestran los nombres asociados a ese numero 
    materials_df = change_id_of_vendors_by_name(materials_df)

    # Renombrar las columnas que se quiera
    materials_df = materials_df.rename(columns = {
        "PO_PO_Item": "PO.PO Item",
        "Vendor_Number": "Vendor",
        "Short_Description": "Short description",
        "Long_Text": "Long description",
        "Project_Id": "Project Id"
    })

    # Por cada request line mergear la informacion de su material
    merged_df = pd.merge(request_lines_df, materials_df, how='left', on='PO.PO Item')

    return merged_df

# Dataframe con filtros, necesita una key como parametro para evitar error de filtros duplicados
# Valdria el dataframe como key pero cabe la posibilidad de que 2 dataframes esten vacios y cuenten como igual
def filter_dataframe(df: pd.DataFrame, key: str) -> pd.DataFrame:

    if key not in st.session_state:
        st.session_state[key] = {'columns': [], 'filters': {}, 'state': False}
        
    modify = st.checkbox(
        label = "Add filters",
        value = st.session_state[key]['state'],
        key = f"add_filters_{key}" # Clave para poder crear un filtro para cada dataframe distinto
    )
    
    # Recarga para que la interfaz refleje el estado actual del filtro
    if st.session_state[key]['state'] != modify:
        st.session_state[key]['state'] = modify
        st.rerun()

    if not modify:
        return df
    else:
        selected_columns = st.session_state[key]['columns']
        column_filters = st.session_state[key]['filters']

    df = df.copy()

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on ", df.columns, default = selected_columns)
        
        # Recarga para que la interfaz refleje el estado actual del filtro
        if to_filter_columns != selected_columns:
            st.session_state[key]['columns'] = to_filter_columns
            st.session_state[key]['filters'] = {}
            st.rerun()

        for column in to_filter_columns:
            left, right = st.columns((1, 20))

            if column not in column_filters:
                column_filters[column] = None
                
            if is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=column_filters[column] if column_filters[column] else (_min, _max),
                    step=step,
                )

                # Recarga para que la interfaz refleje el estado actual del filtro
                if user_num_input != column_filters[column]:
                    column_filters[column] = user_num_input
                    st.rerun()

                df = df[df[column].between(*user_num_input)]

            elif is_categorical_dtype(df[column]) or df[column].nunique() < 6:

                unique_values = df[column].unique()
                valid_defaults = [val for val in (column_filters[column] if column_filters[column] else []) if val in unique_values]

                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default = valid_defaults if valid_defaults else list(unique_values),
                )

                # Recarga para que la interfaz refleje el estado actual del filtro
                if user_cat_input != column_filters[column]:
                    column_filters[column] = user_cat_input
                    st.rerun()

                df = df[df[column].isin(user_cat_input)]

            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                    value=column_filters[column] if column_filters[column] else ''
                )

                # Recarga para que la interfaz refleje el estado actual del filtro
                if user_text_input != column_filters[column]:
                    column_filters[column] = user_text_input
                    st.rerun()

                if user_text_input:

                    def custom_strip(text):
                        chars = [" ", "-", "_", " "] # ඞ this character looks kinda sus ඞ
                        for char in chars:
                            text = text.replace(char, "")
                        return text

                    # Aplica el TRIM personalizado al texto del usuario y a la columna de datos
                    trimmed_user_input = custom_strip(user_text_input)
                    df[column] = df[column].astype(str).apply(custom_strip)

                    df = df[df[column].str.contains(trimmed_user_input, case=False)]

        # Save the updated filters back into session_state
        st.session_state[key]['filters'] = column_filters

    return df

# ------------------------------ Autentificacion ------------------------------ #

def simple_error_page(
        title : str,
        errorInfo : str,
        retryURL : str,
    ):
    """
    Shows a rather simple error page with a retry button.
    Stops execution once called.

    Arguments:
        title: error title
        errorInfo: what happened
        retryURL: where to redirect the user to retry

    Returns:
        Nothing.

    Examples:
        try:
            do_something()
        except Exception as e:
            logger.error("Something went wrong")
            simple_error_page(
                "Something went wrong!",
                repr(e),
                "http://localhost:8501/"
            )
    """

    st.markdown(f"**{title}**")
    st.write(f"Error info: {errorInfo}")
    st.write(f'''<h2><a target="_self"
        href="{retryURL}">Retry</a></h2>''',
                unsafe_allow_html=True)
    st.stop()

def streamlit_auth_callback(authorizationURL : str):
    # If we are accessing this page for the first time
    # there will be no parameters inside the url.
    # But when we are redirected back after sending the
    # user to the page for authorization the code will be present
    if "code" not in st.query_params:
        #st.session_state["logger"].info(f"Auth URL: {authorizationURL}")
        st.write("You are not logged in; redirecting to login page...")
        st.markdown(
            f"<meta style=\"color:white;\" http-equiv=\"refresh\" content=\"0; url='{authorizationURL}'\">",
            unsafe_allow_html = True
        )
        st.stop()

    code = st.query_params["code"]
    #Once we have the code clear the parameters from the url
    st.query_params.clear()
    return code

def avl_auth_process(
        redirectURL : str,
        errorURL : str,
        clientID : str,
        clientSecret : str,
        ldapAccount : str,
        ldapPass : str
    ):
    """
    Runs the entire authentication process, storing data inside
    st.session_state["user"] (keys are "account_name" and "groups").
    Requires the logger to be initialized,
    so you have to call init_logger() before this.
    If an error occurs or the user is not correctly authenticated the function
    automatically stops execution and shows a simple error screen.

    Arguments:
        redirectURL: where to send the user back after oauth authorization.
            You want this to be the same url you gave the oauth server when registering the app.
        errorURL: in case of error, where the retry button should send the user.

    Returns:
        Nothing.
    """
    #First get which user is trying to access
    try:
        user, givenName, familyName, email = \
            asyncio.run(get_user_auth(
                streamlit_auth_callback,
                redirectURL,
                clientID,
                clientSecret
            ))
    except Exception as e:
        #st.session_state["logger"].error(f"Auth Error: {repr(e)}")
        simple_error_page(
            "An error occurred during authentication",
            repr(e),
            errorURL
        )

    #st.session_state["logger"].info(f"User {user} has logged in")

    #Now to the get permissions
    # try:
    #     userGroups, accountName = \
    #         get_user_groups_and_account((givenName, familyName), ldapAccount, ldapPass)
    # except Exception as e:
    #     #st.session_state["logger"].error(f"LDAP Error: {repr(e)}, from user {user}")
    #     simple_error_page(
    #         "An error occurred trying to access ldap",
    #         repr(e),
    #         errorURL
    #     )

    st.session_state["user"] = {
        "id" : user,
        "email": email
    }
