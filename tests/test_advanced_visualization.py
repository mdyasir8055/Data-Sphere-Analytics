import pytest
import pandas as pd
import streamlit as st
from unittest.mock import patch, MagicMock

def test_init(mock_session_state):
    from advanced_visualization import AdvancedVisualization
    
    # Test initialization
    advanced_viz = AdvancedVisualization()
    assert isinstance(advanced_viz, AdvancedVisualization)

def test_create_chart(mock_advanced_visualization):
    # Create test dataframe
    df = pd.DataFrame({
        'category': ['A', 'B', 'C', 'A', 'B'],
        'value': [10, 20, 15, 25, 30]
    })
    
    # Test bar chart creation
    with patch('plotly.express.bar') as mock_bar:
        mock_bar.return_value = "bar_chart"
        chart = mock_advanced_visualization.create_chart(df, 'bar', 'category', 'value')
        assert chart == "bar_chart"
        mock_bar.assert_called_once()
    
    # Test line chart creation
    with patch('plotly.express.line') as mock_line:
        mock_line.return_value = "line_chart"
        chart = mock_advanced_visualization.create_chart(df, 'line', 'category', 'value')
        assert chart == "line_chart"
        mock_line.assert_called_once()
    
    # Test scatter chart creation
    with patch('plotly.express.scatter') as mock_scatter:
        mock_scatter.return_value = "scatter_chart"
        chart = mock_advanced_visualization.create_chart(df, 'scatter', 'category', 'value')
        assert chart == "scatter_chart"
        mock_scatter.assert_called_once()
    
    # Test pie chart creation
    with patch('plotly.express.pie') as mock_pie:
        mock_pie.return_value = "pie_chart"
        chart = mock_advanced_visualization.create_chart(df, 'pie', 'category', 'value')
        assert chart == "pie_chart"
        mock_pie.assert_called_once()

def test_forecast_data(mock_advanced_visualization):
    # Create test time series dataframe
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=10),
        'value': [10, 12, 15, 14, 16, 18, 17, 20, 22, 25]
    })
    
    # Test forecasting
    with patch('pandas.DataFrame.copy', return_value=df.copy()):
        forecast_df = mock_advanced_visualization.forecast_data(df, 'date', 'value', 5)
        assert len(forecast_df) == 15  # Original 10 + 5 forecast points

def test_visualization_ui(mock_advanced_visualization):
    # This would require more complex mocking of streamlit components
    # For now, we'll just test that the method exists
    assert hasattr(mock_advanced_visualization, 'visualization_ui')