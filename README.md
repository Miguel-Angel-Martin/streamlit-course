# Devops 

AVL [test machine](http://10.23.147.88/)

AVL [production machine](http://10.23.138.23/)

# AVL Order Tracker Setup and Execution

## Clone the repository

To get started, clone the repository with the following command:

```
git clone https://devops.avl.com/004/AVL%20Iberica/_git/avl-order-tracker
```

## Create and set up the virtual environment

Make sure you have Python 3 installed. Then, create and activate a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```
pip install -r requirements.txt
```

## Configure the `.env` file

Set up the necessary environment variables in the .env file. At a minimum, include the following:

 - DATABASE_URL
 - [Other configuration parameters]

To be sure the DATABASE_URL does set properly, run the following command:

```
export DATABASE_URL="sqlite://<database path>/AvlMaterialTracker.db"
```

## Update the database

Update the model with alembic if it has changed, or to be sure is up to the date (At the end of the guide, its explained how to use alembic)

```
alembic upgrade head
```

> If it generates a new database file, it means there was a problem setting the enviroment variable DATABASE_URL, delete the new file and run the following comands:
> ```
> export DATABASE_URL=<database path>
> alembic upgrade head
> ```

Update the database content inside the app folder by running:

```
cd app
python3 database/Update_Data.py
```
This will update the tables with the xlsx inside of app.

## Run the application

Run the application using Streamlit:

> For the application to work correctly, you must run in the /app directory.

 - Locally:
 ```
 streamlit run app.py
 ```
 - Specifying a port:
 ```
 streamlit run app.py --server.port <port_number>
 ```
 - Running in the background using `nohup`:
 ```
 nohup streamlit run app.py --server.port <port_number>
 ```

 For the test machine run in port 3000 for example, port 8501 is blocked by the firewall.


## Terminate the background process
To stop the application running in the background, follow these steps:

1. Check for processes using the port with the following command:

```
lsof -i :<port_number>
```

2. Kill the process using the corresponding PID:

```
kill -9 <PID>
```

## Use of Alembic
If you want, or you have update the database model, you need to create a migration patch using Alembic after changind the model:

> Any command with Alembic should be run from the root directory with the virtual environment activated.

1. Create a new migration patch:
```
alembic revision -m "Name of the patch"
```

2. Modify the `upgrade()` method using Alembic’s functionality to reflect the changes made to the database model, and `downgrade()` to revert the changes.

3. Apply the patch (this will use the `upgrade()` function)

´´´
alembic upgrade head
´´´

Finally, if you want to revert the changes (use the `downgrade()` function) of a migration patch:

´´´
alembic downgrade <revision id>
´´´

To revert the las upgrade you can use:

´´´
alembic downgrade -1
´´´