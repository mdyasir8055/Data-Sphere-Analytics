import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
import json

def test_init(mock_session_state):
    from enterprise_integration import EnterpriseIntegration
    
    # Test initialization
    enterprise_integration = EnterpriseIntegration()
    assert isinstance(enterprise_integration, EnterpriseIntegration)

def test_create_api_endpoint(mock_enterprise_integration, mock_session_state):
    # Initialize API endpoints in session state
    if "api_endpoints" not in st.session_state:
        st.session_state.api_endpoints = {}
    
    # Test endpoint creation
    endpoint_name = "test_endpoint"
    endpoint_def = {
        "name": endpoint_name,
        "method": "GET",
        "query": "SELECT * FROM customers",
        "parameters": [{"name": "id", "type": "integer"}],
        "auth_required": True,
        "auth_type": "API Key",
        "rate_limit": 100,
        "path": f"/api/{endpoint_name}"
    }
    
    mock_enterprise_integration.create_api_endpoint(endpoint_name, endpoint_def)
    
    # Check if endpoint was created
    assert endpoint_name in st.session_state.api_endpoints
    assert st.session_state.api_endpoints[endpoint_name] == endpoint_def

def test_generate_powerbi_template(mock_enterprise_integration, mock_db_manager):
    # Get schema for testing
    schema = mock_db_manager.get_database_schema()
    
    # Test Power BI template generation
    template = mock_enterprise_integration._generate_powerbi_template(schema, ["customers", "orders"])
    
    # Check if template is a dictionary with expected structure
    assert isinstance(template, dict)
    assert "name" in template
    assert "tables" in template
    assert len(template["tables"]) == 2

def test_generate_lookml(mock_enterprise_integration, mock_db_manager):
    # Get schema for testing
    schema = mock_db_manager.get_database_schema()
    
    # Test LookML generation
    lookml = mock_enterprise_integration._generate_lookml(schema, ["customers", "orders"])
    
    # Check if lookml is a string with expected content
    assert isinstance(lookml, str)
    assert "view: customers" in lookml
    assert "view: orders" in lookml

def test_enterprise_integration_ui(mock_enterprise_integration):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_enterprise_integration, 'enterprise_integration_ui')