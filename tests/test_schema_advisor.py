import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from schema_advisor import SchemaAdvisor
    
    # Test initialization
    schema_advisor = SchemaAdvisor()
    assert isinstance(schema_advisor, SchemaAdvisor)

def test_analyze_schema(mock_schema_advisor, mock_db_manager):
    # Get schema for testing
    schema = mock_db_manager.get_database_schema()
    
    # Test schema analysis
    analysis = mock_schema_advisor.analyze_schema(schema)
    
    # Check if analysis contains expected keys
    assert "table_count" in analysis
    assert "column_count" in analysis
    assert "primary_keys" in analysis
    assert "foreign_keys" in analysis
    assert "normalization_score" in analysis
    
    # Check specific analysis results
    assert analysis["table_count"] == 2
    assert analysis["primary_keys"] == 2
    assert analysis["foreign_keys"] == 1

def test_suggest_improvements(mock_schema_advisor, mock_db_manager):
    # Get schema for testing
    schema = mock_db_manager.get_database_schema()
    
    # Test improvement suggestions
    suggestions = mock_schema_advisor.suggest_improvements(schema)
    
    # Check if suggestions is a list
    assert isinstance(suggestions, list)

def test_advisor_ui(mock_schema_advisor):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_schema_advisor, 'advisor_ui')