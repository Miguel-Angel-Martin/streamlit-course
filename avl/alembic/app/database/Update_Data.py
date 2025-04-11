import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy import select
from Database_Model import Vendor, Warehouse, Project, engine

def determine_project_id_of_html(number: str) -> str:
    #if number.startswith("ES"):
        #return "GPN" + number[2:]
    if number.startswith("GPN") or number.startswith("SO") or number.startswith("IO"):
        return number
    elif len(number) == 6:
        return "GPN" + number
    elif number.startswith("3711"):
        return "SO" + number
    elif number.startswith("90") or number.startswith("107"):
        return "IO" + number
    else:
        return None

def update_data():
    vendors_df = pd.read_excel("20250212134310_Approved_suppliers.xlsx")
    projects_df = pd.read_excel("Projects.xlsx")
    vendors = []
    projects = []
    warehouses = []

    for index, row in vendors_df.iterrows():
        with Session(engine) as session:
            existing_vendor = session.execute(select(Vendor).where(Vendor.Number == row.iloc[0])).scalar_one_or_none()
            if existing_vendor:
                existing_vendor.Company = row.iloc[1]
                existing_vendor.Search_Term = row.iloc[2]
                existing_vendor.Street1 = row.iloc[3]
                existing_vendor.Street2 = row.iloc[4]
                existing_vendor.City = row.iloc[5]
                existing_vendor.State = row.iloc[6]
                existing_vendor.Postal_Code = row.iloc[7]
                existing_vendor.Country = row.iloc[8]
                existing_vendor.Phone = row.iloc[9]
                existing_vendor.Fax = row.iloc[10]
                existing_vendor.VAT_Reg_No = row.iloc[11]
                existing_vendor.Risk = row.iloc[12]
                existing_vendor.ABC_Rating = row.iloc[13]
                existing_vendor.Currency = row.iloc[14]
                existing_vendor.DateOfEntry = row.iloc[15]
                existing_vendor.ISO_9001 = row.iloc[16]
                existing_vendor.ISO_14001 = row.iloc[17]
                existing_vendor.ISO_27001 = row.iloc[18]
                existing_vendor.Title = row.iloc[19]
                existing_vendor.First_Name = row.iloc[20]
                existing_vendor.Last_Name = row.iloc[21]
                existing_vendor.Department = row.iloc[22]
                existing_vendor.Position = row.iloc[23]
                existing_vendor.Email = row.iloc[24]
                existing_vendor.Cell_Phone_Number = row.iloc[25]
                existing_vendor.Contact_Number = row.iloc[26]
                existing_vendor.Contact_City = row.iloc[27]
                existing_vendor.Contact_Country = row.iloc[28]
                session.commit()
            else:
                new_vendor = Vendor(
                    Number = row.iloc[0],
                    Company = row.iloc[1],
                    Search_Term = row.iloc[2],
                    Street1 = row.iloc[3],
                    Street2 = row.iloc[4],
                    City = row.iloc[5],
                    State = row.iloc[6],
                    Postal_Code = row.iloc[7],
                    Country = row.iloc[8],
                    Phone = row.iloc[9],
                    Fax = row.iloc[10],
                    VAT_Reg_No = row.iloc[11],
                    Risk = row.iloc[12],
                    ABC_Rating = row.iloc[13],
                    Currency = row.iloc[14],
                    DateOfEntry = row.iloc[15],
                    ISO_9001 = row.iloc[16],
                    ISO_14001 = row.iloc[17],
                    ISO_27001 = row.iloc[18],
                    Title = row.iloc[19],
                    First_Name = row.iloc[20],
                    Last_Name = row.iloc[21],
                    Department = row.iloc[22],
                    Position = row.iloc[23],
                    Email = row.iloc[24],
                    Cell_Phone_Number = row.iloc[25],
                    Contact_Number = row.iloc[26],
                    Contact_City = row.iloc[27],
                    Contact_Country = row.iloc[28]
                )
                vendors.append(new_vendor)

    for index, row in projects_df.iterrows():
        with Session(engine) as session:
            project_id = determine_project_id_of_html(row.iloc[0])
            if project_id:
                existing_project = session.execute(select(Project).where(Project.Id == project_id)).scalar_one_or_none()
                if existing_project:
                    existing_project.Name = row.iloc[1]
                    existing_project.Manager = row.iloc[2]
                    existing_project.Closed = row.iloc[3]
                    existing_project.Modified_DateTime = row.iloc[4]
                    existing_project.Modifier = row.iloc[5]
                    session.commit()
                else:
                    new_project = Project(
                        Id = project_id,
                        Name = row.iloc[1],
                        Manager = row.iloc[2],
                        Closed = row.iloc[3],
                        Modified_DateTime = row.iloc[4],
                        Modifier = row.iloc[5]
                    )
                    projects.append(new_project)

    with Session(engine) as session:
        existing_warehouse = session.execute(select(Warehouse).where(Warehouse.Id == 1)).scalar_one_or_none()
        if not existing_warehouse:
            global_warehouse = Warehouse(
                Id = 1,
                Name = "Global storage",
                Location = "Valladolid"
            )
            warehouses.append(global_warehouse)

    with Session(engine) as session:
        try:
            session.add_all(vendors)
            session.add_all(projects)
            session.add_all(warehouses)
            session.commit()
            
            print(f"Vendors insertados correctamente (Leidas {vendors_df.shape[0]} filas y {vendors_df.shape[1]} columnas para vendors)")
            print(f"Proyectos insertados correctamente (Leidas {projects_df.shape[0]} filas y {projects_df.shape[1]} columnas para proyectos.)")

        except Exception as e:
            session.rollback()
            print(f"No changes applied, error with the inserts: {e}")

update_data()