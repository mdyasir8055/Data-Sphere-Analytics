import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_end_to_end_workflow(mock_db_manager, mock_nlp_processor, mock_session_state):
    """Test the complete workflow from connecting to a database to executing a query"""
    
    # 1. Connect to database
    mock_db_manager.connect_to_db("test_sqlite")
    assert st.session_state.connected_db == "test_sqlite"
    
    # 2. Get database schema
    schema = mock_db_manager.get_database_schema()
    assert schema is not None
    assert "tables" in schema
    
    # 3. Generate SQL from natural language
    nl_query = "Show me all customers"
    sql_query = mock_nlp_processor.generate_sql_with_groq(nl_query, schema)
    assert sql_query == "SELECT * FROM customers"
    
    # 4. Execute the query
    result = mock_db_manager.execute_query(sql_query)
    assert result is not None
    
    # 5. Check if query is added to history
    assert len(st.session_state.query_history) > 0
    
    # This test verifies that the core workflow of the application works correctly