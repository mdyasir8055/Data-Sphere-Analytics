import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from schema_visualizer import SchemaVisualizer
    
    # Test initialization
    schema_visualizer = SchemaVisualizer()
    assert isinstance(schema_visualizer, SchemaVisualizer)

def test_generate_er_diagram(mock_schema_visualizer, mock_session_state, mock_db_manager):
    # Get schema for testing
    schema = mock_db_manager.get_database_schema()
    
    # Test ER diagram generation
    with patch('networkx.DiGraph'):
        with patch('matplotlib.pyplot.figure'):
            diagram = mock_schema_visualizer.generate_er_diagram(schema)
            assert diagram is not None

def test_visualize_schema_ui(mock_schema_visualizer):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_schema_visualizer, 'visualize_schema_ui')