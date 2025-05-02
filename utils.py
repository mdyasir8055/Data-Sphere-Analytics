import streamlit as st
import json
import os

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "db_connections" not in st.session_state:
        st.session_state.db_connections = {}
    
    if "connected_db" not in st.session_state:
        st.session_state.connected_db = None
    
    if "current_connection" not in st.session_state:
        st.session_state.current_connection = None
    
    if "db_schema" not in st.session_state:
        st.session_state.db_schema = None
    
    if "query_results" not in st.session_state:
        st.session_state.query_results = None
    
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""
    
    if "natural_language_query" not in st.session_state:
        st.session_state.natural_language_query = ""
    
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

def save_session_state():
    """Save relevant session state variables to storage"""
    # Create a dictionary with the data to save
    save_data = {
        "db_connections": st.session_state.db_connections,
        "query_history": st.session_state.query_history
    }
    
    # Convert to JSON and store in session state
    st.session_state.saved_data = json.dumps(save_data)

def load_session_state():
    """Load session state variables from storage"""
    if "saved_data" in st.session_state:
        try:
            # Load data from session state
            saved_data = json.loads(st.session_state.saved_data)
            
            # Update session state with loaded data
            for key, value in saved_data.items():
                if key in ["db_connections", "query_history"]:
                    st.session_state[key] = value
        except Exception as e:
            st.error(f"Error loading saved data: {str(e)}")
