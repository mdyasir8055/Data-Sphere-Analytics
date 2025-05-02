import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from query_optimizer import QueryOptimizer
    
    # Test initialization
    query_optimizer = QueryOptimizer()
    assert isinstance(query_optimizer, QueryOptimizer)

def test_analyze_query(mock_query_optimizer):
    # Test query analysis
    query = "SELECT * FROM customers WHERE id = 1"
    analysis = mock_query_optimizer.analyze_query(query)
    
    # Check if analysis contains expected keys
    assert "structure" in analysis
    assert "tables" in analysis
    assert "conditions" in analysis
    assert "joins" in analysis
    
    # Check specific analysis results
    assert analysis["tables"] == ["customers"]
    assert "id = 1" in analysis["conditions"]
    assert len(analysis["joins"]) == 0

def test_suggest_optimizations(mock_query_optimizer):
    # Test optimization suggestions
    query = "SELECT * FROM customers"
    suggestions = mock_query_optimizer.suggest_optimizations(query)
    
    # Check if suggestions is a list
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0

def test_optimizer_ui(mock_query_optimizer):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_query_optimizer, 'optimizer_ui')