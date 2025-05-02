import pytest
import pandas as pd
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from data_exporter import DataExporter
    
    # Test initialization
    data_exporter = DataExporter()
    assert isinstance(data_exporter, DataExporter)

def test_export_to_csv(mock_data_exporter):
    # Create test dataframe
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['John', 'Jane', 'Bob']
    })
    
    # Test CSV export
    csv_data = mock_data_exporter.export_to_csv(df)
    assert isinstance(csv_data, str)
    assert "id,name" in csv_data
    assert "1,John" in csv_data

def test_export_to_excel(mock_data_exporter):
    # Create test dataframe
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['John', 'Jane', 'Bob']
    })
    
    # Test Excel export
    excel_data = mock_data_exporter.export_to_excel(df)
    assert isinstance(excel_data, bytes)
    assert len(excel_data) > 0

def test_export_to_json(mock_data_exporter):
    # Create test dataframe
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['John', 'Jane', 'Bob']
    })
    
    # Test JSON export
    json_data = mock_data_exporter.export_to_json(df)
    assert isinstance(json_data, str)
    assert '"id":1' in json_data
    assert '"name":"John"' in json_data

def test_export_ui(mock_data_exporter):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_data_exporter, 'export_ui')