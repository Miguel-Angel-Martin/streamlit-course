import functools
import os
from pathlib import Path
from redmail import EmailSender
import streamlit as st
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.Database_Model import engine, Request, User, Vendor
from lib.db import connection

from lib.queries import get_request_by_id
from lib.queries import get_request_lines_with_material_data_by_request_id
from lib.types import EmailType

__all__ = ["send"]

SUBJECT = "[AVL Material Tracker]"

@functools.cache
def sender():
    templates = (Path(__file__).parent.parent / "templates").resolve()
    sender = EmailSender(
        host=os.getenv("AVL_SMTP_HOST"),
        port=os.getenv("AVL_SMTP_PORT"),
        username=os.getenv("AVL_SMTP_USERNAME"),
        password=os.getenv("AVL_SMTP_PASSWORD"))
    sender.set_template_paths(
        html=templates,
        text=templates,
    )
    return sender


def send(**kwargs):
    if not kwargs.get("sender"):
        kwargs["sender"] = os.getenv("AVL_SMTP_EMAIL")
    return sender().send(**kwargs)


def send_request_notification(request: Request, subject: str):
    try:
        request_df = get_request_by_id(request.Id)
        lines_df = get_request_lines_with_material_data_by_request_id(request.Id)

        # Obtenemos el curpo del mensaje dependiendo del contexto del mensaje
        email_content = email_html(request, subject, request_df, lines_df)

        # Se renombran y ocultan campos de los dataframes del request y sus lineas, dependiendo del contexto del mensaje
        columns_to_show = ["Id", "Type", "Posting_date", "Time", "WarehouseNotes", "Project_Id"]
        request_df = request_df[columns_to_show]
        
        if EmailType.PENDING_APROVAL.value:
            columns_to_show = ["Id", "PO_PO_Item", "Requested_Qty", "Stock", "Status", "Vendor_Number", "Short_Description", "Long_Text", "WBS"]
        else:    
            columns_to_show = ["Id", "Transaction_Id", "PO_PO_Item", "Requested_Qty", "Stock", "Status", "Vendor_Number", "Short_Description", "Long_Text", "WBS"]
        lines_df = change_id_of_vendors_by_name(lines_df)
        lines_df = lines_df[columns_to_show]

        request_df = request_df.rename(columns={
            "Posting_date": "Posting Date",
            "Time": "Posting Time",
            "Project_Id": "Project Id"
        })

        lines_df = lines_df.rename(columns={
            "Transaction_Id": "Transaction Id",
            "Requested_Qty": "Requested Quantity",
            "Vendor_Number": "Vendor",
            "Short_Description": "Short Description",
            "Long_Text": "Long Text"
        })
        
        with connection().session as session:
            cc = [user[0].Email for user in session.execute(select(User).filter(User.Role == 'Manager')).all()]

        return send(
            subject=f"{SUBJECT} Request {request.Id}: {subject}",
            receivers=[request.UserRequester],
            #cc=cc,
            html=email_content,
            body_tables={"request": request_df, "lines": lines_df}
        )
    
    except Exception as e:
        print(f"Error: There was a problem sending the mail: {e}")


def email_html(request: Request, subject: str, request_df: pd.DataFrame, lines_df: pd.DataFrame) -> str:
    logistics_user = st.session_state.user['email']
    html = f"""
        <p>Dear <strong>{request.UserRequester}</strong>,</p>
    """
    # Dependiendo del subject, cambian las condiciones del mensaje
    match subject:
        case EmailType.PENDING_APROVAL.value:
            html += f"""
                <p>Your Request with ID <strong>{request.Id}</strong> has been processed and is currently <strong>pending approval</strong>.</p>
            """
        case EmailType.ACCEPTED.value:
            html += f"""
                <p>Your request with ID <strong>{request.Id}</strong> has been <strong style="color: green;">Accepted</strong> by <strong>{logistics_user}</strong>.</p>
                <p>The materials have been picked up by <strong>{request.Receiver}</strong> and will be delivered in <strong>{request.Manufacturing_Destination}</strong>.</p>
                <p>Logistics notes: {request.Feedback_To_Requester}</p>
            """
        case EmailType.DENIED.value:
            html += f"""
                <p>Your request with ID <strong>{request.Id}</strong> has been <strong style="color: red;">Denied</strong> by <strong>{logistics_user}</strong>.</p>
                <p>Reason for denial: {request.Feedback_To_Requester}</p>
            """

    # Agregar las tablas al final del mensaje
    html += """
        <h2>Request Details</h2>
        {{ request }}

        <h3>Lines</h3>
        {{ lines }}
        <br>
        <p>This message was generated automatically. Please do not reply.</p>
    """

    return html


def change_id_of_vendors_by_name(df: pd.DataFrame) -> pd.DataFrame:
    with Session(engine) as session:
        for index, value in enumerate(df["Vendor_Number"]):
            vendor_name = session.execute(
                select(Vendor.Company)
                .where(Vendor.Number == value)).fetchone() # Devuelve una tupla con los resultados
            
            if vendor_name:
                df.at[index, "Vendor_Number"] = vendor_name[0]

    return df