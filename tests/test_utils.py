import pytest
import streamlit as st
import os
import json
from unittest.mock import patch, mock_open

def test_initialize_session_state():
    from utils import initialize_session_state
    
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Test initialization
    initialize_session_state()
    
    # Check if session state variables are initialized
    assert "db_connections" in st.session_state
    assert "connected_db" in st.session_state
    assert "current_connection" in st.session_state
    assert "db_schema" in st.session_state
    assert "query_results" in st.session_state
    assert "current_query" in st.session_state
    assert "natural_language_query" in st.session_state

def test_save_session_state():
    from utils import save_session_state
    
    # Set up test session state
    st.session_state.db_connections = {"test_db": {"type": "SQLite", "connection_string": "sqlite:///test.db"}}
    
    # Mock open function
    with patch("builtins.open", mock_open()) as mock_file:
        save_session_state()
        mock_file.assert_called_once()
        # Check if json.dump was called with the correct data
        call_args = mock_file.return_value.__enter__.return_value.write.call_args[0][0]
        assert "db_connections" in call_args
        assert "test_db" in call_args

def test_load_session_state():
    from utils import load_session_state
    
    # Mock session state data
    session_data = {
        "db_connections": {"test_db": {"type": "SQLite", "connection_string": "sqlite:///test.db"}},
        "api_keys": {"groq": "test_key"}
    }
    
    # Mock open function
    with patch("builtins.open", mock_open(read_data=json.dumps(session_data))):
        with patch("os.path.exists", return_value=True):
            load_session_state()
            
            # Check if session state was loaded correctly
            assert "db_connections" in st.session_state
            assert "test_db" in st.session_state.db_connections
            assert "api_keys" in st.session_state