import pytest
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from database_manager import DatabaseManager
    
    # Test initialization
    db_manager = DatabaseManager()
    
    # Check if session state variables are initialized
    assert "db_connections" in st.session_state
    assert "connected_db" in st.session_state
    assert "current_connection" in st.session_state
    assert "query_results" in st.session_state
    assert "db_schema" in st.session_state
    assert "query_history" in st.session_state

def test_connect_to_db(mock_db_manager, mock_session_state):
    # Test connecting to an existing database
    result = mock_db_manager.connect_to_db("test_sqlite")
    assert result is True
    
    # Test connecting to a non-existent database
    with pytest.raises(ValueError):
        mock_db_manager.connect_to_db("non_existent_db")

def test_get_database_schema(mock_db_manager, mock_session_state):
    # Test schema extraction
    schema = mock_db_manager.get_database_schema()
    
    # Verify schema structure
    assert "tables" in schema
    assert "customers" in schema["tables"]
    assert "orders" in schema["tables"]
    
    # Verify columns in customers table
    customer_columns = [col["name"] for col in schema["tables"]["customers"]["columns"]]
    assert "id" in customer_columns
    assert "name" in customer_columns
    assert "email" in customer_columns
    assert "signup_date" in customer_columns
    
    # Verify foreign key relationship
    orders_fks = schema["tables"]["orders"]["foreign_keys"]
    assert len(orders_fks) == 1
    assert orders_fks[0]["referred_table"] == "customers"
    assert orders_fks[0]["referred_columns"] == ["id"]
    assert orders_fks[0]["constrained_columns"] == ["customer_id"]

def test_execute_query(mock_db_manager, mock_session_state):
    # Test SELECT query
    result = mock_db_manager.execute_query("SELECT * FROM customers")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3  # 3 customers in test data
    assert "name" in result.columns
    
    # Test query with parameters
    result = mock_db_manager.execute_query("SELECT * FROM customers WHERE id = 1")
    assert len(result) == 1
    assert result.iloc[0]["name"] == "John Doe"
    
    # Test JOIN query
    result = mock_db_manager.execute_query("""
        SELECT c.name, o.order_date, o.total_amount 
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
    """)
    assert len(result) == 4  # 4 orders in test data
    
    # Test non-SELECT query (should return success message)
    with patch('sqlalchemy.engine.Connection.execute'):
        result = mock_db_manager.execute_query("UPDATE customers SET name = 'Test' WHERE id = 1")
        assert result == "Query executed successfully."

def test_file_upload_ui(mock_db_manager):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_db_manager, '_file_upload_ui')

def test_create_connection_ui(mock_db_manager):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_db_manager, 'create_connection_ui')

def test_manage_connections_ui(mock_db_manager):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_db_manager, 'manage_connections_ui')