from db.db_manager import DBManager
from datetime import date

db = DBManager()

class CustomerModel:
    def __init__(self, customer_id:int=None, name="", surname:str = "", telephone:str = "", project:str = "", date:str = date.today()):
        self.customer_id = customer_id
        self.name = name
        self.surname = surname
        self.telephone = telephone
        self.project = project
        self.date = date

    @staticmethod
    def create_customer(name, surname, telephone, project, date):
        query = """
            INSERT INTO customer (name, surname, telephone, project, date)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (name, surname, telephone, project, date)
        db.run_action(query, params)

    @staticmethod
    def get_all_customers():
        query = """
            SELECT id AS customer_id, name, surname, telephone, project, date
            FROM customer
        """
        return db.run_query(query)

    @staticmethod
    def get_customer_by_id(customer_id):
        query = """
            SELECT id AS customer_id, name, surname, telephone, project, date
            FROM customer
            WHERE id = %s
        """
        params = (customer_id,)
        result = db.run_query(query, params)
        
        # Verificar que el DataFrame tenga al menos una fila
        if not result.empty and len(result) > 0:
            return result.iloc[0].to_dict()
        else:
            return None


    @staticmethod
    def update_customer(customer_id, name, surname, telephone, project, date):
        query = """
            UPDATE customer
            SET name = %s, surname = %s, telephone = %s, project = %s, date = %s
            WHERE id = %s
        """
        params = (name, surname, telephone, project, date, customer_id)
        db.run_action(query, params)

    @staticmethod
    def delete_customer(customer_id):
        query = "DELETE FROM customer WHERE id = %s"
        params = (customer_id,)
        db.run_action(query, params)

