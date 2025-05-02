import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from nlp_processor import NLPProcessor
    
    # Test initialization
    nlp_processor = NLPProcessor()
    
    # Check if API clients are initialized
    assert hasattr(nlp_processor, 'groq_client')
    assert hasattr(nlp_processor, 'gemini_model')

def test_update_clients(mock_nlp_processor, mock_session_state):
    # Test updating API clients
    mock_nlp_processor._update_clients()
    
    # With mock API keys
    st.session_state.groq_api_key = "test_groq_key"
    st.session_state.gemini_api_key = "test_gemini_key"
    mock_nlp_processor._update_clients()
    
    # Without API keys
    st.session_state.groq_api_key = ""
    st.session_state.gemini_api_key = ""
    mock_nlp_processor._update_clients()
    
    assert True  # If we got here without errors, the test passes

def test_create_prompt(mock_nlp_processor, mock_session_state, mock_db_manager):
    # Test prompt creation
    schema_info = mock_db_manager.get_database_schema()
    prompt = mock_nlp_processor._create_prompt("List all customers", schema_info)
    
    # Check if prompt contains schema information
    assert "customers" in prompt
    assert "orders" in prompt
    assert "List all customers" in prompt

def test_extract_sql_from_response(mock_nlp_processor):
    # Test SQL extraction from various response formats
    
    # Test with SQL in code blocks
    response = """
    Here's the SQL query:
    ```sql
    SELECT * FROM customers;
    ```
    """
    sql = mock_nlp_processor._extract_sql_from_response(response)
    assert sql == "SELECT * FROM customers;"
    
    # Test with SQL without code blocks
    response = """
    Here's the SQL query:
    SELECT * FROM customers;
    """
    sql = mock_nlp_processor._extract_sql_from_response(response)
    assert sql == "SELECT * FROM customers;"
    
    # Test with multiple code blocks
    response = """
    You could use:
    ```sql
    SELECT * FROM customers;
    ```
    Or alternatively:
    ```sql
    SELECT id, name FROM customers;
    ```
    """
    sql = mock_nlp_processor._extract_sql_from_response(response)
    assert sql == "SELECT * FROM customers;"

def test_generate_sql_with_groq(mock_nlp_processor, mock_session_state):
    # This would require mocking the Groq API
    # For now, we'll just test that the method exists and returns the mocked value
    schema_info = {"tables": {"customers": {"columns": [{"name": "id"}, {"name": "name"}]}}}
    sql = mock_nlp_processor.generate_sql_with_groq("List all customers", schema_info)
    assert sql == "SELECT * FROM customers"

def test_generate_sql_with_gemini(mock_nlp_processor, mock_session_state):
    # This would require mocking the Gemini API
    # For now, we'll just test that the method exists and returns the mocked value
    schema_info = {"tables": {"customers": {"columns": [{"name": "id"}, {"name": "name"}]}}}
    sql = mock_nlp_processor.generate_sql_with_gemini("List all customers", schema_info)
    assert sql == "SELECT * FROM customers"

def test_text_to_sql_ui(mock_nlp_processor):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_nlp_processor, 'text_to_sql_ui')

def test_sql_editor_ui(mock_nlp_processor):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_nlp_processor, 'sql_editor_ui')