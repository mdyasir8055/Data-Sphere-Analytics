import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from semantic_layer import SemanticLayer
    
    # Test initialization
    semantic_layer = SemanticLayer()
    assert isinstance(semantic_layer, SemanticLayer)

def test_create_semantic_model(mock_semantic_layer, mock_session_state):
    # Initialize semantic models in session state
    if "semantic_models" not in st.session_state:
        st.session_state.semantic_models = {}
    
    # Test model creation
    model_name = "test_model"
    model_def = {
        "entities": {
            "customer": {
                "source_table": "customers",
                "attributes": [
                    {"name": "id", "source_column": "id"},
                    {"name": "name", "source_column": "name"}
                ]
            }
        },
        "relationships": [],
        "description": "Test model"
    }
    
    mock_semantic_layer.create_semantic_model(model_name, model_def)
    
    # Check if model was created
    assert model_name in st.session_state.semantic_models
    assert st.session_state.semantic_models[model_name] == model_def

def test_query_semantic_model(mock_semantic_layer, mock_session_state, mock_db_manager):
    # Initialize semantic models in session state
    if "semantic_models" not in st.session_state:
        st.session_state.semantic_models = {}
    
    # Create test model
    model_name = "test_model"
    model_def = {
        "entities": {
            "customer": {
                "source_table": "customers",
                "attributes": [
                    {"name": "id", "source_column": "id"},
                    {"name": "name", "source_column": "name"}
                ]
            }
        },
        "relationships": [],
        "description": "Test model"
    }
    
    st.session_state.semantic_models[model_name] = model_def
    
    # Test querying semantic model
    with patch.object(mock_db_manager, 'execute_query', return_value="query_result"):
        result = mock_semantic_layer.query_semantic_model(
            model_name, 
            "Show all customers", 
            mock_db_manager
        )
        assert result == "query_result"

def test_semantic_layer_ui(mock_semantic_layer):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_semantic_layer, 'semantic_layer_ui')