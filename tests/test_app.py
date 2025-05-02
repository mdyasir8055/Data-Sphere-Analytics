import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_app_initialization():
    # This test would require complex mocking of streamlit
    # For now, we'll just import the app and check if it runs without errors
    with patch('streamlit.set_page_config'):
        with patch('streamlit.sidebar.selectbox', return_value="Home"):
            with patch('streamlit.title'):
                with patch('streamlit.subheader'):
                    with patch('streamlit.markdown'):
                        try:
                            import app
                            print("App imported successfully!")
                            assert True  # If we got here without errors, the test passes
                        except Exception as e:
                            print(f"App initialization failed: {str(e)}")
                            pytest.fail(f"App initialization failed: {str(e)}")

# This allows the file to be run directly for debugging
if __name__ == "__main__":
    print("Running test_app_initialization directly...")
    test_app_initialization()
    print("Test completed!")
