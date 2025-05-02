import pytest
import os
import pandas as pd
import sqlite3
import tempfile
import streamlit as st
from unittest.mock import MagicMock, patch

# Mock session state for testing
@pytest.fixture
def mock_session_state():
    with patch.object(st, 'session_state', {
        "db_connections": {},
        "connected_db": None,
        "current_connection": None,
        "query_results": None,
        "db_schema": None,
        "query_history": [],
        "groq_api_key": "mock_groq_key",
        "gemini_api_key": "mock_gemini_key",
        "api_endpoints": {},
        "data_lineage": {}
    }):
        yield st.session_state

# Create a test SQLite database
@pytest.fixture
def test_db_path():
    # Create a temporary SQLite database for testing
    fd, path = tempfile.mkstemp(suffix='.db')
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        signup_date DATE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')
    
    # Insert test data
    cursor.execute('''
    INSERT INTO customers (name, email, signup_date)
    VALUES 
        ('John Doe', 'john@example.com', '2023-01-15'),
        ('Jane Smith', 'jane@example.com', '2023-02-20'),
        ('Bob Johnson', 'bob@example.com', '2023-03-10')
    ''')
    
    cursor.execute('''
    INSERT INTO orders (customer_id, order_date, total_amount)
    VALUES 
        (1, '2023-04-05', 125.99),
        (1, '2023-05-10', 89.50),
        (2, '2023-04-15', 45.25),
        (3, '2023-05-20', 210.75)
    ''')
    
    conn.commit()
    conn.close()
    os.close(fd)
    
    yield path
    
    # Cleanup
    os.unlink(path)

# Mock database manager
@pytest.fixture
def mock_db_manager(test_db_path, mock_session_state):
    from database_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    
    # Add test connection
    st.session_state.db_connections["test_sqlite"] = {
        "type": "SQLite",
        "connection_string": f"sqlite:///{test_db_path}"
    }
    
    # Set as current connection
    st.session_state.connected_db = "test_sqlite"
    st.session_state.current_connection = st.session_state.db_connections["test_sqlite"]
    
    # Get schema
    db_manager.get_database_schema()
    
    return db_manager

# Mock NLP processor
@pytest.fixture
def mock_nlp_processor():
    from nlp_processor import NLPProcessor
    
    nlp_processor = NLPProcessor()
    
    # Mock the AI response
    nlp_processor.generate_sql_with_groq = MagicMock(return_value="SELECT * FROM customers")
    nlp_processor.generate_sql_with_gemini = MagicMock(return_value="SELECT * FROM customers")
    
    return nlp_processor

# Mock other components
@pytest.fixture
def mock_schema_visualizer():
    from schema_visualizer import SchemaVisualizer
    return SchemaVisualizer()

@pytest.fixture
def mock_data_exporter():
    from data_exporter import DataExporter
    return DataExporter()

@pytest.fixture
def mock_query_optimizer():
    from query_optimizer import QueryOptimizer
    return QueryOptimizer()

@pytest.fixture
def mock_schema_advisor():
    from schema_advisor import SchemaAdvisor
    return SchemaAdvisor()

@pytest.fixture
def mock_semantic_layer():
    from semantic_layer import SemanticLayer
    return SemanticLayer()

@pytest.fixture
def mock_advanced_visualization():
    from advanced_visualization import AdvancedVisualization
    return AdvancedVisualization()

@pytest.fixture
def mock_enterprise_integration():
    from enterprise_integration import EnterpriseIntegration
    return EnterpriseIntegration()