# DataSphere Testing Suite

This directory contains tests for the DataSphere Analytics Platform.

## Test Structure

The tests are organized by component:

- `conftest.py`: Contains fixtures and setup for all tests
- `test_database_manager.py`: Tests for database connection and management
- `test_nlp_processor.py`: Tests for natural language to SQL conversion
- `test_schema_visualizer.py`: Tests for schema visualization
- `test_data_exporter.py`: Tests for data export functionality
- `test_query_optimizer.py`: Tests for query optimization
- `test_schema_advisor.py`: Tests for schema analysis and recommendations
- `test_semantic_layer.py`: Tests for semantic modeling
- `test_advanced_visualization.py`: Tests for data visualization
- `test_enterprise_integration.py`: Tests for enterprise integrations
- `test_app.py`: Tests for the main application
- `test_utils.py`: Tests for utility functions
- `test_integration.py`: End-to-end integration tests

## Running Tests

To run all tests:

```bash
python run_tests.py
```

To run a specific test file:

```bash
pytest -v tests/test_database_manager.py
```

## Test Coverage

The tests cover:

1. Unit tests for individual components
2. Integration tests for component interactions
3. UI component existence tests
4. End-to-end workflow tests

## Adding New Tests

When adding new features to DataSphere, please add corresponding tests in the appropriate test file.