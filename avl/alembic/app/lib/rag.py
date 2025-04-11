import requests
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
#import pyodbc


from filelock import Timeout, FileLock

from typing import List, Dict, Tuple, Set, Callable, Any, Self
from dataclasses import dataclass, field
import datetime
import os
import math
import time
import io
import re
import tempfile 
import random
import copy
import sys
import json
import base64
import sqlite3

#Model stuff
sys.path.append(os.path.dirname(__file__))
from models import DenseEmbeddingsDispatcher, SparseEmbeddingsDispatcher
from models import RerankerDispatcher, TranscriberDispatcher, LLMDispatcher

RAG_RESERVED_METADATA = {
    "date", "docname", "docid", "index", "rangetype", "rangebegin", 
    "rangeend", "overlapbefore", "overlapafter", "numchunks", "collection"
}
TRANSCRIBER_SAMPLE_RATE = 16000 #Required by whisper
PYTHON_TYPES_TO_SQL_TYPES = {
    "<class 'float'>": "FLOAT",
    "<class 'decimal.Decimal'>": "FLOAT",
    "<class 'int'>": "INTEGER",
    "<class 'str'>": "TEXT",
    "<class 'datetime.datetime'>": "DATETIME",
    "<class 'bool'>": "BOOLEAN",
}

@dataclass
class Chunk:
    metadata : dict[str, any] = field(default_factory=lambda:{})
    content : str = ""
    score : float = 0
    collection : str = ""
    id : str = ""
    embeddings : dict[str, any] = field(default_factory=lambda:{"dense":[],"sparse":{"indices":[],"values":[]}})

    def to_dict(this):
        """Returns this object as a Python dict"""
        return {
            "metadata": this.metadata, 
            "content": this.content,
            "score": this.score,
            "collection": this.collection,
            "id": this.id,
            "embeddings": this.embeddings
        }
    
    def from_dict(dictionary: dict[str, Any]) -> Self:
        """Loads data from a Python dict. Not all fields need to be present."""
        return Chunk(**dictionary)

@dataclass
class Document:
    name : str = ""
    date : str = ""
    link : str = ""
    chunks : int = 0

def load_json_config_file(name : str):
    return json.load(open(
        os.path.dirname(__file__) + f"/../../resources/{name}.json", 
        "r", encoding = "utf-8"
    ))

def save_json_config_file(name : str, data):
    json.dump(
        data,
        open(
            os.path.dirname(__file__) + f"/../../resources/{name}.json", 
            "w", encoding = "utf-8"
        ),
        ensure_ascii = False, 
        indent = 4
    )

def get_filelock(name : str):
    return FileLock(os.path.dirname(__file__) + f"/../../resources/locks/{name}.lock")

class RAG:

    def __init__(this, parameters : Dict[str, Any]):

        this.history = ChatMessageHistory()
        this.retrievedChunks = [[]]
        this.param = {}
        this.reload_parameters(parameters)

    def reload_parameters(
            this,
            parameters : dict[str, Any]
        ):
        
        this.param = copy.deepcopy(parameters)
        this.llm = LLMDispatcher(
            this.param["models"]["llm"],
            this.param["rag"]["max_context"], 
            this.param["rag"]["llm_temperature"],
            ollama_host = os.getenv("OLLAMA_HOST"),
            google_api_key = this.param["credentials"]["google"],
            openai_api_key = this.param["credentials"]["openai"],
            together_api_key = this.param["credentials"]["together"],
        )
    
    def generate_context_header(this, metadata : Dict[str, str]) -> str:
        contextHeader = ""
        for key, value in metadata.items():
            if not key.startswith("[context]"):
                continue
            contextHeader += f"{key[len("[context]"):]}: {value}\n"
        return contextHeader
    
    def append_history(
            this, 
            author : str, 
            message : str
        ):

        if author == "human":
            this.history.add_user_message(message)
        else:
            this.history.add_ai_message(message)
            
        # Keep one more message if the message is from the user, 
        # so we can include in the history the N last Q/A pairs 
        # and the current user prompt.
        trimHistoryLen = this.param["rag"]["chat_history"]*2 + (author == "human")

        # This is a dumb way to clear the oldest message,
        # but the tutorials say to do this...
        storedMessages = this.history.messages
        if len(storedMessages) > this.param["rag"]["chat_history"] * 2:
            this.history.clear()
            if trimHistoryLen > 0:
                for oldMessage in storedMessages[-trimHistoryLen:]:
                    this.history.add_message(oldMessage)

    def load_history(this, messages : dict[str, str]):
        this.history.clear()
        for msg in messages:
            this.append_history(msg["author"], msg["content"]) 

    def clear_history(this):
        this.history.clear()

    def rollback_history(this):
        """
        Deletes the last Q/A pair from the history.
        """
        storedMessages = this.history.messages
        this.history.clear()
        for message in storedMessages[:len(storedMessages)-2]:
            this.history.add_message(message)

    def chunks_to_string(this, chunks: list[Chunk]) -> str:
        string = ""
        for doc in this.retrievedChunks[-1]:
            contextHeader = this.generate_context_header(doc.metadata)
            string += "\n\n-------------------------------------\n\n"
            string += f"Document source: {doc.metadata["docname"]}\n"
            string += f"{contextHeader}\n"
            string += f"\nContent: {doc.content}\n\n"
        return string
    
    def create_llm_response(
            this,
            userPrompt : str,
            chunks : list[Chunk],
            success : bool,
        ):

        obtainedContext = this.chunks_to_string(chunks)
        this.append_history("human", userPrompt)
        modelInput = ChatPromptTemplate([
            (
                "system", 
                # If no documents were found, tell user no info is available 
                # instead of hallucinating
                this.param["prompts"]["nodata"] if not success else this.param["prompts"]["rag"]
            ), 
            MessagesPlaceholder(variable_name = "chat_history"),
        ])

        return this.llm.stream(modelInput.invoke({
            "context" : obtainedContext,
            "chat_history" : this.history.messages
        }))
    
    def begin_sql_stream(
            this,
            userPrompt : str,
            database : dict[str, Any],
        ):
        """
        Creates a command for the SQL database, executes it, and uses the results to
        create a response to the user query.
        
        Args:
            userPrompt: the question asked by the user
            database: a dictionary containing information about the database, specifically
                - "type": can be "SQLite", "SQL Server" or "Microsoft Access"
                - "path": path to the database file, if needed
                - "tables": list of tables, each element is a dictionary containing:
                    - "name": name of the table
                    - "description": additional descriptions for the table
                    - "schema": column information of the table, usually as a
                        "CREATE TABLE" statement.
        """

        if database["type"] == "Microsoft Access":
            storagePath = database["path"]
            cursor = pyodbc.connect(
                driver="Microsoft Access Driver (*.mdb, *.accdb)", 
                dbq=storagePath,
            ).cursor()
        elif database["type"] == "SQLite":
            storagePath = database["path"]
            print(os.curdir)
            cursor = sqlite3.connect(storagePath).cursor()
        elif database["type"] == "SQL Server":
            host = database["host"]
            db = database["database"]
            user = database["user"]
            password = database["password"]
            cursor = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host};DATABASE={db};UID={user};PWD={password};TrustServerCertificate=yes;"
            ).cursor()

        cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
        print(cursor.fetchall())

        schema = ""
        for table in database["tables"]:
            schema += f"Table {table["name"]}: {table["description"]}\n"
            schema += f"{table["schema"]}\n\n"

        # Generated queries and obtained errors at each retry
        sqlQueries = []
        sqlErrors = []
        success = False
        this.retrievedChunks = [[]]

        for retry in range(this.param["rag"]["sql_tries"]):
            retryPrompt = this.param["prompts"]["sql_retry"].format(
                database_name = database["type"], 
                error = "" if len(sqlErrors) == 0 else sqlErrors[-1], 
                query = "" if len(sqlQueries) == 0 else sqlQueries[-1]
            )
            generatePrompt = this.param["prompts"]["sql_query"].format(
                database_name = database["type"],
                schema = schema, 
                question = userPrompt,
                retry_prompt = "" if len(sqlErrors) == 0 else retryPrompt
            )
            llmAnswer = this.llm.invoke(generatePrompt)
            
            try:
                sqlQuery = llmAnswer
                queryBegin = llmAnswer.find("```sql\n")+7
                sqlQuery = llmAnswer[queryBegin:llmAnswer.find("\n```",queryBegin)]
                sqlQueries.append(sqlQuery)
                
                # Common mistake: using double quotes for text. Let us try to fix it.
                # It can happen with a WHERE clause (check with =) or a LIKE clause
                while True:
                    match = re.search("(like|Like|LIKE|=)(.){0,1}\"", sqlQuery)
                    if match is None:
                        break
                    sqlQuery = sqlQuery[:match.span()[1]-1] + "'" + sqlQuery[match.span()[1]:]
                    nextDoubleQuote = sqlQuery.find("\"", match.span()[1])
                    sqlQuery = sqlQuery[:nextDoubleQuote] + "'" + sqlQuery[nextDoubleQuote+1:]
                # Common mistake: use * instead of % for wildcards in LIKE clause
                pos = 0
                while True:
                    match = re.search("(like|Like|LIKE)", sqlQuery[pos:])
                    if match is None:
                        break
                    pos += match.span()[1]
                    matchBeg = sqlQuery.find("'*", pos)
                    matchEnd = sqlQuery.find("*'", pos)
                    if matchBeg != -1:
                        sqlQuery = sqlQuery[:matchBeg+1] + "%" + sqlQuery[matchBeg+2:]
                    if matchEnd != -1:
                        sqlQuery = sqlQuery[:matchEnd] + "%" + sqlQuery[matchEnd+1:]

                sqlQueries[-1] = sqlQuery
                cursor.execute(sqlQueries[-1])
                rows = cursor.fetchall()
                if len(rows) == 0:
                    sqlErrors.append("No matching entries found, try to change the query a bit.")
                    continue
                maxTextLength = (this.param["rag"]["max_context"] - 512) * 3
                success = True
            
                # Create markdown style table with the output
                text = "|"
                for column in cursor.description:
                    text += f" {column[0]} |"

                for row in rows:
                    newLine = "\n|"
                    for idx in range(len(row)):
                        newLine += f" {row[idx]} |"
                    if len(text) + len(newLine) > maxTextLength:
                        break
                    text += newLine

                text = f"SQL query:\n{sqlQueries[-1]}\n\nResult:\n{text}"
                this.retrievedChunks = [[Chunk(
                    metadata = { "docname": database["name"] },
                    content = text
                )]]
                break
            except Exception as e:
                sqlErrors.append(repr(e))

        if not success:
            this.retrievedChunks = [[Chunk(
                metadata = { "docname": database["name"] },
                content = "\n\n".join(
                    [f"SQL query:\n{sqlQueries[idx]}\n\nResult:\n{sqlErrors[idx]}" for idx in range(len(sqlErrors))]
                )
            )]]

        return this.create_llm_response(userPrompt, this.retrievedChunks[-1], success)
    
    def end_stream(
            this, 
            AIresponse : str
        ) -> list[list[Chunk]]:
        """
        Adds the generated response back to the history,
        returns the documents used for context and generates
        new questions for use in the rag.
        Called after any begin_*_stream().

        Args:
            AIresponse: generated string by the AI
        Returns:
            A list of used documents for each processing stage. 
            Information is inside the metadata attribute, which is a dictionary. 
            Valid keys include "docname", "date", "link", and pages or lines 
            depending on file type.
        Example:
            llmResponse = tmpMessage.write_stream(st.session_state.llm.begin_search_stream(prompt))
            retrievedChunks = st.session_state.llm.end_stream(llmResponse)
            show_context(retrievedChunks)
        """
        this.llm.end_stream(AIresponse)
        this.append_history("ai", AIresponse)
        return this.retrievedChunks[-1]
    
    def delete_database(
            this,
            name : str,
        ):
        databases = load_json_config_file("databases")
        if name not in databases:
            return
        
        if databases[name]["type"] == "Microsoft Access":
            os.remove(os.path.dirname(__file__) + "/../../database/access/" + name)
        if databases[name]["type"] == "SQLite":
            os.remove(os.path.dirname(__file__) + "/../../database/sqlite/" + name)
        del databases[name]
        save_json_config_file("databases", databases)

    def get_database_info(
            this,
            name : str,
        ) -> dict[str, any] | None:
        databases = load_json_config_file("databases")
        return databases.get(name, None)
    
    def update_database_info(
            this,
            name : str,
            info : dict[str, any]
        ):
        databases = load_json_config_file("databases")
        databases[name] = info
        save_json_config_file("databases", databases)

    def add_database_common(
            this,
            dbname,
            cursor,
            provider: str,
            metadata : dict[str, any]
        ):
        """
        Common function to all database adders. Extracts table information and 
        stores the information in the json.
        """
        if provider == "SQLite":
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
            tables = [{
                "name": table[1],
                "description": "",
                "schema": table[4]
            } for table in cursor.fetchall()]
        
        elif provider == "SQL Server" or provider == "Microsoft Access": 
            if provider == "SQL Server": # User tables have the type "TABLE" and its second element as "dbo"
                tableNames = [table.table_name for table in cursor.tables() if table[3] == "TABLE" and table[1] == "dbo"]
            else: # User tables have the type "TABLE"
                tableNames = [table.table_name for table in cursor.tables() if table[3] == "TABLE"] 

            tables : list[dict[str, Any]] = []
            for tableName in tableNames:
                # This way of finding primary keys will only work if the table was created via GUI
                primaryKeyCols = { row[8] for row in cursor.statistics(tableName) if row[5]=='PrimaryKey' } 
                cursor.execute(f"SELECT TOP 1 * FROM [{tableName}]") # To have column info

                columns : list[dict[str, Any]] = []
                # Find all columns in the database
                for column in cursor.description:
                    columnType = PYTHON_TYPES_TO_SQL_TYPES.get(str(column[1]), str(column[1]))
                    columns.append({
                        "name": column[0],
                        "type": columnType,
                        "is_primary": column[0] in primaryKeyCols,
                        "references": []
                    })

                # Generate table schema with all columns
                schema = f"CREATE TABLE [{tableName}] ("
                for column in columns:
                    schema += f"\n    [{column["name"]}] {column["type"]}"
                    schema += ","
                for column in columns:
                    if column["is_primary"]:
                        schema += f"\n    PRIMARY KEY ({column["name"]}),"
                for column in columns:
                    if len(column["references"]) != 0:
                        schema += f"\n    FOREIGN KEY {column["name"]} REFERENCES {column["references"][0]},"
                schema = schema[:-1]
                schema += "\n)"

                tables.append({
                    "name": tableName,
                    "description": "",
                    "schema": schema
                })

        databases = load_json_config_file("databases")
        databases[dbname] = metadata | { "tables": tables }
        save_json_config_file("databases", databases)

    def add_sql_server(
            this,
            dbname : str,
            host : str,
            database : str,
            user : str,
            password : str
        ):

        cursor = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"
        ).cursor()
        this.add_database_common(
            dbname, cursor, "SQL Server", 
            { "type": "SQL Server", "host": host, "database": database, "user": user, "password": password }
        )

    def add_file_database(
            this,
            dbname : str,
            provider : str,
            file,
        ):
        
        if provider == "Microsoft Access":
            storagePath = os.path.dirname(__file__) + "/../../database/access/" + file.name
        elif provider == "SQLite":
            storagePath = os.path.dirname(__file__) + "/../../database/sqlite/" + file.name
        storage = open(storagePath, "wb")
        storage.write(file.read())
        storage.close()
        
        if provider == "Microsoft Access":
            cursor = pyodbc.connect(
                driver="Microsoft Access Driver (*.mdb, *.accdb)", 
                dbq=storagePath,
            ).cursor()
        elif provider == "SQLite":
            cursor = sqlite3.connect(storagePath).cursor()
        
        this.add_database_common(
            dbname, cursor, provider, { "type": provider, "filename": file.name }
        )

    def add_database(
            this,
            dbname : str,
            provider : str,
            **kwargs
        ):
        """
        Adds a new database to the system.

        Arguments: 
            type: can be "Microsoft Access", "SQLite" or "SQL Server"
        """
        if provider == "Microsoft Access" or provider == "SQLite":
            this.add_file_database(dbname, provider, kwargs["file"])
        elif provider == "SQL Server":
            this.add_sql_server(dbname, kwargs["host"], kwargs["database"], kwargs["user"], kwargs["password"])
        else:
            raise ValueError(f"Unknown database provider: {provider}")

