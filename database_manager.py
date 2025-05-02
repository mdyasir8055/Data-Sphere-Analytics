import streamlit as st
import pandas as pd
import os
import json
import re
import datetime
import sqlalchemy
from sqlalchemy import create_engine, inspect, text, MetaData, Table
import pymongo
import pymysql
import psycopg2
import sqlite3
from utils import save_session_state

class DatabaseManager:
    def __init__(self):
        # Initialize database connection settings
        if "db_connections" not in st.session_state:
            st.session_state.db_connections = {}
        
        if "connected_db" not in st.session_state:
            st.session_state.connected_db = None
        
        if "current_connection" not in st.session_state:
            st.session_state.current_connection = None
        
        if "query_results" not in st.session_state:
            st.session_state.query_results = None
        
        if "db_schema" not in st.session_state:
            st.session_state.db_schema = None
        
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
    
    def create_connection_ui(self):
        """Create UI for setting up database connections"""
        st.subheader("Create New Database Connection")
        
        # Connection name
        connection_name = st.text_input("Connection Name", key="new_conn_name")
        
        # Connection method selection
        connection_method = st.radio(
            "Connection Method",
            ["Connect to Server", "Upload Database File"],
            key="connection_method"
        )
        
        # Handle file upload method
        if connection_method == "Upload Database File":
            self._file_upload_ui(connection_name)
            return
        
        # Database type selection
        db_type = st.selectbox(
            "Database Type",
            ["PostgreSQL", "MySQL", "SQLite", "MongoDB"],
            key="new_conn_type"
        )
        
        # Connection details based on database type
        if db_type == "PostgreSQL":
            host = st.text_input("Host", value=os.getenv("PGHOST", "localhost"), key="pg_host")
            port = st.text_input("Port", value=os.getenv("PGPORT", "5432"), key="pg_port")
            database = st.text_input("Database", value=os.getenv("PGDATABASE", ""), key="pg_db")
            username = st.text_input("Username", value=os.getenv("PGUSER", ""), key="pg_user")
            password = st.text_input("Password", type="password", value=os.getenv("PGPASSWORD", ""), key="pg_pass")
            
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            
        elif db_type == "MySQL":
            host = st.text_input("Host", value="localhost", key="mysql_host")
            port = st.text_input("Port", value="3306", key="mysql_port")
            database = st.text_input("Database", key="mysql_db")
            username = st.text_input("Username", key="mysql_user")
            password = st.text_input("Password", type="password", key="mysql_pass")
            
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            
        elif db_type == "SQLite":
            database_path = st.text_input("Database File Path", key="sqlite_path")
            connection_string = f"sqlite:///{database_path}"
            
        elif db_type == "MongoDB":
            host = st.text_input("Host", value="localhost", key="mongo_host")
            port = st.text_input("Port", value="27017", key="mongo_port")
            database = st.text_input("Database", key="mongo_db")
            username = st.text_input("Username (optional)", key="mongo_user")
            password = st.text_input("Password (optional)", type="password", key="mongo_pass")
            
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                connection_string = f"mongodb://{host}:{port}/{database}"
        
        # Save connection button
        if st.button("Test and Save Connection", key="test_and_save_conn_btn"):
            if not connection_name:
                st.error("Please provide a connection name.")
                return
            
            # Test connection
            try:
                if db_type == "PostgreSQL":
                    engine = create_engine(connection_string)
                    conn = engine.connect()
                    conn.close()
                elif db_type == "MySQL":
                    engine = create_engine(connection_string)
                    conn = engine.connect()
                    conn.close()
                elif db_type == "SQLite":
                    engine = create_engine(connection_string)
                    conn = engine.connect()
                    conn.close()
                elif db_type == "MongoDB":
                    client = pymongo.MongoClient(connection_string)
                    client.server_info()
                    client.close()
                
                # Prepare connection parameters based on database type
                connection_params = {}
                if db_type == "PostgreSQL":
                    connection_params = {
                        "host": host,
                        "port": port,
                        "database": database,
                        "username": username,
                        "has_password": bool(password)
                    }
                elif db_type == "MySQL":
                    connection_params = {
                        "host": host,
                        "port": port,
                        "database": database,
                        "username": username,
                        "has_password": bool(password)
                    }
                elif db_type == "MongoDB":
                    connection_params = {
                        "host": host,
                        "port": port,
                        "database": database,
                        "username": username,
                        "has_password": bool(password)
                    }
                
                # Save connection details to session state
                st.session_state.db_connections[connection_name] = {
                    "type": db_type,
                    "connection_string": connection_string,
                    "display_string": self._mask_password_in_connection_string(connection_string),
                    "connection_params": connection_params
                }
                
                # Save session state
                save_session_state()
                
                # Activate the connection
                st.session_state.connected_db = connection_name
                st.session_state.current_connection = st.session_state.db_connections[connection_name]
                
                # Get database schema
                self.get_database_schema()
                
                st.success(f"Connection to {db_type} database successful! Connection saved as '{connection_name}' and activated.")
                
                # Refresh the page to update all components
                st.rerun()
            except Exception as e:
                st.error(f"Failed to connect to the database: {str(e)}")
    
    def manage_connections_ui(self):
        """UI for managing existing database connections"""
        st.subheader("Manage Database Connections")
        
        if not st.session_state.db_connections:
            st.info("No database connections saved. Create a new connection to get started.")
            return
        
        # Display saved connections
        st.write("Saved Connections:")
        
        for conn_name, conn_details in st.session_state.db_connections.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{conn_name}** ({conn_details['type']})")
            
            with col2:
                if st.button("Connect", key=f"connect_{conn_name}"):
                    try:
                        self.connect_to_db(conn_name)
                        st.session_state.connected_db = conn_name
                        st.session_state.current_connection = conn_details
                        
                        # Get database schema
                        self.get_database_schema()
                        
                        st.success(f"Connected to {conn_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to connect: {str(e)}")
            
            with col3:
                if st.button("Delete", key=f"delete_{conn_name}"):
                    if st.session_state.connected_db == conn_name:
                        st.session_state.connected_db = None
                        st.session_state.current_connection = None
                        st.session_state.db_schema = None
                    
                    del st.session_state.db_connections[conn_name]
                    save_session_state()
                    st.success(f"Connection '{conn_name}' deleted.")
                    st.rerun()
        
        # Display current connection status
        if st.session_state.connected_db:
            st.success(f"✅ Currently connected to: {st.session_state.connected_db}")
        else:
            st.warning("⚠️ No active database connection.")
    
    def connect_to_db(self, connection_name):
        """Connect to a specific database by connection name"""
        if connection_name not in st.session_state.db_connections:
            raise ValueError(f"Connection '{connection_name}' not found.")
        
        conn_details = st.session_state.db_connections[connection_name]
        db_type = conn_details["type"]
        connection_string = conn_details["connection_string"]
        
        try:
            if db_type in ["PostgreSQL", "MySQL", "SQLite"]:
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    # Test connection is successful if we get here
                    pass
            elif db_type == "MongoDB":
                with pymongo.MongoClient(connection_string) as client:
                    client.server_info()
            
            return True
        except Exception as e:
            raise Exception(f"Failed to connect: {str(e)}")
    
    def get_database_schema(self):
        """Get the schema of the currently connected database"""
        if not st.session_state.connected_db or not st.session_state.current_connection:
            return None
        
        db_type = st.session_state.current_connection["type"]
        connection_string = st.session_state.current_connection["connection_string"]
        
        try:
            schema = {}
            
            if db_type in ["PostgreSQL", "MySQL", "SQLite"]:
                engine = create_engine(connection_string)
                inspector = inspect(engine)
                
                schema["tables"] = {}
                for table_name in inspector.get_table_names():
                    columns = inspector.get_columns(table_name)
                    primary_keys = inspector.get_pk_constraint(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    schema["tables"][table_name] = {
                        "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns],
                        "primary_keys": primary_keys.get("constrained_columns", []),
                        "foreign_keys": [{
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"],
                            "constrained_columns": fk["constrained_columns"]
                        } for fk in foreign_keys]
                    }
            
            elif db_type == "MongoDB":
                client = pymongo.MongoClient(connection_string)
                db_name = connection_string.split("/")[-1]
                db = client[db_name]
                
                schema["collections"] = {}
                for collection_name in db.list_collection_names():
                    # Get a sample document to infer schema
                    sample = db[collection_name].find_one()
                    if sample:
                        schema["collections"][collection_name] = {
                            "fields": [{"name": k, "type": type(v).__name__} for k, v in sample.items()]
                        }
                    else:
                        schema["collections"][collection_name] = {"fields": []}
            
            st.session_state.db_schema = schema
            return schema
            
        except Exception as e:
            st.error(f"Failed to retrieve database schema: {str(e)}")
            return None
    
    def _file_upload_ui(self, connection_name):
        """UI for uploading database files"""
        st.subheader("Upload Database File")
        
        # Validate connection name
        if not connection_name:
            st.warning("Please provide a connection name before uploading a file.")
            return
        
        # File upload
        uploaded_file = st.file_uploader("Upload Database File", type=["db", "sqlite", "sqlite3", "csv", "xlsx", "json"])
        
        if uploaded_file is not None:
            # Determine file type
            file_type = self._get_file_type(uploaded_file)
            st.write(f"Detected file type: {file_type}")
            
            # Configuration based on file type
            if file_type in ["db", "sqlite", "sqlite3"]:
                # For SQLite databases
                db_type = "SQLite"
                db_path = self._save_uploaded_file(uploaded_file)
                connection_string = f"sqlite:///{db_path}"
                
                # Show path where the file was saved
                st.info(f"Database saved at: {db_path}")
                
            elif file_type == "csv":
                # For CSV files
                db_type = "SQLite"
                table_name = st.text_input("Table Name for the CSV Data", value="imported_data")
                
                # Create an in-memory SQLite database from the CSV
                db_path = self._csv_to_sqlite(uploaded_file, table_name)
                connection_string = f"sqlite:///{db_path}"
                
                # Show success message
                st.info(f"CSV data imported into SQLite database as table '{table_name}'")
                
            elif file_type == "xlsx":
                # For Excel files
                db_type = "SQLite"
                sheet_name = st.text_input("Sheet Name (leave blank for first sheet)", value="")
                table_name = st.text_input("Table Name for the Excel Data", value="imported_data")
                
                # Create an in-memory SQLite database from the Excel file
                db_path = self._excel_to_sqlite(uploaded_file, table_name, sheet_name)
                connection_string = f"sqlite:///{db_path}"
                
                # Show success message
                sheet_info = f"sheet '{sheet_name}'" if sheet_name else "first sheet"
                st.info(f"Excel data ({sheet_info}) imported into SQLite database as table '{table_name}'")
                
            elif file_type == "json":
                # For JSON files
                db_type = "SQLite"
                table_name = st.text_input("Table Name for the JSON Data", value="imported_data")
                
                # Create an in-memory SQLite database from the JSON
                db_path = self._json_to_sqlite(uploaded_file, table_name)
                connection_string = f"sqlite:///{db_path}"
                
                # Show success message
                st.info(f"JSON data imported into SQLite database as table '{table_name}'")
            
            # Test and save connection
            if st.button("Save Connection"):
                if not connection_name:
                    st.error("Please provide a connection name.")
                    return
                
                try:
                    # Test the connection
                    engine = create_engine(connection_string)
                    conn = engine.connect()
                    conn.close()
                    
                    # Save connection details
                    st.session_state.db_connections[connection_name] = {
                        "type": db_type,
                        "connection_string": connection_string,
                        "details": {
                            "database": db_path,
                            "file_type": file_type,
                            "original_filename": uploaded_file.name
                        }
                    }
                    
                    # Save session state
                    save_session_state()
                    
                    # Activate the connection
                    st.session_state.connected_db = connection_name
                    st.session_state.current_connection = st.session_state.db_connections[connection_name]
                    
                    # Get database schema
                    self.get_database_schema()
                    
                    st.success(f"Database '{connection_name}' successfully configured and connected!")
                    
                    # Refresh the page to update all components
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
    
    def _get_file_type(self, uploaded_file):
        """Determine the type of the uploaded file"""
        # Get file extension
        filename = uploaded_file.name
        file_extension = filename.split(".")[-1].lower()
        
        if file_extension in ["db", "sqlite", "sqlite3"]:
            return "sqlite"
        elif file_extension == "csv":
            return "csv"
        elif file_extension in ["xlsx", "xls"]:
            return "xlsx"
        elif file_extension == "json":
            return "json"
        else:
            return "unknown"
    
    def _save_uploaded_file(self, uploaded_file):
        """Save the uploaded file to disk"""
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp_db")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a unique filename
        file_extension = uploaded_file.name.split(".")[-1]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"db_{timestamp}.{file_extension}"
        file_path = os.path.join(temp_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    
    def _csv_to_sqlite(self, csv_file, table_name):
        """Convert a CSV file to a SQLite database"""
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp_db")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a unique filename for the SQLite database
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        db_filename = f"csv_import_{timestamp}.db"
        db_path = os.path.join(temp_dir, db_filename)
        
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Create a SQLite database and save the DataFrame to it
        engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql(table_name, engine, index=False, if_exists="replace")
        
        return db_path
    
    def _excel_to_sqlite(self, excel_file, table_name, sheet_name=None):
        """Convert an Excel file to a SQLite database"""
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp_db")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a unique filename for the SQLite database
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        db_filename = f"excel_import_{timestamp}.db"
        db_path = os.path.join(temp_dir, db_filename)
        
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_file)
        
        # Create a SQLite database and save the DataFrame to it
        engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql(table_name, engine, index=False, if_exists="replace")
        
        return db_path
    
    def _json_to_sqlite(self, json_file, table_name):
        """Convert a JSON file to a SQLite database"""
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp_db")
        os.makedirs(temp_dir, exist_ok=True)
    
        # Generate a unique filename for the SQLite database
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        db_filename = f"json_import_{timestamp}.db"
        db_path = os.path.join(temp_dir, db_filename)
    
        # Read the JSON file
        try:
            # First, try the simpler method
            df = pd.read_json(json_file)
        except Exception:
            try:
                # Reset file pointer to beginning
                json_file.seek(0)
                content = json_file.read().decode('utf-8')
                if content.strip():  # Check if content is not empty
                    json_data = json.loads(content)
                    if isinstance(json_data, list):
                        df = pd.json_normalize(json_data)
                    else:
                        df = pd.json_normalize([json_data])
                else:
                    st.error("The JSON file appears to be empty.")
                    df = pd.DataFrame()
            except Exception as e:
                st.error(f"Failed to parse JSON file: {str(e)}")
                df = pd.DataFrame({
                    "column1": ["Sample data 1", "Sample data 2"],
                    "column2": [123, 456],
                    "column3": [True, False]
                })
                st.info("Created a sample table since the JSON couldn't be parsed.")
        
        # Serialize list/dict columns to JSON strings
        for col in df.columns:
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

        # Create a SQLite database and save the DataFrame to it
        engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql(table_name, engine, index=False, if_exists="replace")
    
        return db_path

    
    def execute_query(self, query):
        """Execute a SQL query against the currently connected database"""
        if not st.session_state.connected_db or not st.session_state.current_connection:
            st.error("No active database connection.")
            return None
        
        db_type = st.session_state.current_connection["type"]
        connection_string = st.session_state.current_connection["connection_string"]
        
        try:
            # Log query to history
            query_item = {
                "query": query,
                "database": st.session_state.connected_db,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.session_state.query_history.insert(0, query_item)
            
            # Limit history to 20 items
            if len(st.session_state.query_history) > 20:
                st.session_state.query_history = st.session_state.query_history[:20]
            
            save_session_state()
            
            # Execute query based on database type
            if db_type in ["PostgreSQL", "MySQL", "SQLite"]:
                engine = create_engine(connection_string)
                
                # Handle SQLite-specific queries
                if db_type == "SQLite" and "INFORMATION_SCHEMA.TABLES" in query:
                    # For SQLite, we need to use sqlite_master instead of INFORMATION_SCHEMA.TABLES
                    if "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES" in query:
                        # Replace with SQLite equivalent
                        modified_query = "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                        with engine.connect() as conn:
                            result = pd.read_sql(modified_query, conn)
                            st.session_state.query_results = result
                            return result
                    else:
                        # For other INFORMATION_SCHEMA queries, adapt accordingly
                        modified_query = query.replace("INFORMATION_SCHEMA.TABLES", "sqlite_master WHERE type='table'")
                        with engine.connect() as conn:
                            result = pd.read_sql(modified_query, conn)
                            st.session_state.query_results = result
                            return result
                
                with engine.connect() as conn:
                    # Check if the query returns results
                    if query.strip().lower().startswith(("select", "show", "describe", "explain")):
                        result = pd.read_sql(query, conn)
                        st.session_state.query_results = result
                        return result
                    else:
                        # For non-select queries
                        conn.execute(text(query))
                        st.session_state.query_results = "Query executed successfully."
                        return "Query executed successfully."
            
            elif db_type == "MongoDB":
                # Parse MongoDB query from SQL-like syntax
                try:
                    with pymongo.MongoClient(connection_string) as client:
                        db_name = connection_string.split("/")[-1]
                        db = client[db_name]
                        
                        # Parse the query to determine operation type
                        query_parts = query.strip().split(" ", 2)
                        operation = query_parts[0].lower()
                        
                        if operation == "find":
                            # Handle find operation
                            collection_name = query_parts[1]
                            filter_json = "{}" if len(query_parts) < 3 else query_parts[2]
                            filter_dict = json.loads(filter_json)
                            result = list(db[collection_name].find(filter_dict))
                            
                        elif operation == "aggregate":
                            # Handle aggregate operation
                            collection_name = query_parts[1]
                            pipeline_json = query_parts[2]
                            pipeline = json.loads(pipeline_json)
                            result = list(db[collection_name].aggregate(pipeline))
                            
                        elif operation == "insert":
                            # Handle insert operation
                            collection_name = query_parts[1]
                            document_json = query_parts[2]
                            document = json.loads(document_json)
                            result = db[collection_name].insert_one(document)
                            return f"Document inserted with ID: {result.inserted_id}"
                            
                        elif operation == "update":
                            # Handle update operation
                            collection_name = query_parts[1]
                            update_parts = query_parts[2].split(" ", 2)
                            filter_json = update_parts[0]
                            update_json = update_parts[1]
                            filter_dict = json.loads(filter_json)
                            update_dict = json.loads(update_json)
                            result = db[collection_name].update_many(filter_dict, update_dict)
                            return f"Updated {result.modified_count} documents"
                            
                        elif operation == "delete":
                            # Handle delete operation
                            collection_name = query_parts[1]
                            filter_json = query_parts[2]
                            filter_dict = json.loads(filter_json)
                            result = db[collection_name].delete_many(filter_dict)
                            return f"Deleted {result.deleted_count} documents"
                            
                        else:
                            st.error(f"Unsupported MongoDB operation: {operation}")
                            return None
                            
                        # Convert MongoDB result to DataFrame for find and aggregate
                        if operation in ["find", "aggregate"]:
                            if result:
                                df = pd.DataFrame(result)
                                # Remove _id column which is not easily serializable
                                if "_id" in df.columns:
                                    df = df.drop("_id", axis=1)
                                st.session_state.query_results = df
                                return df
                            else:
                                st.session_state.query_results = pd.DataFrame()
                                return pd.DataFrame()
                except Exception as e:
                    st.error(f"MongoDB operation failed: {str(e)}")
                    return f"Error: {str(e)}"
        
        except Exception as e:
            error_message = f"Query execution failed: {str(e)}"
            st.session_state.query_results = error_message
            return error_message
            
    def _mask_password_in_connection_string(self, connection_string):
        """Replace actual password with placeholder in connection string for display"""
        # This is a simple implementation that works for most connection string formats
        return re.sub(r':(.*?)@', ':********@', connection_string)
