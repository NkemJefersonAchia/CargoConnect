Unit Tests

All unit tests for this project are stored in this directory.

How to run tests

1. Open a terminal in the project root:

	C:\Users\LENOVO\CargoConnect

2. Run the full unit test suite:

	python.exe -m pytest -q "Unit tests"

3. Run individual test files:

	python.exe -m pytest -q "Unit tests/test_auth_utils.py"
	python.exe -m pytest -q "Unit tests/test_config.py"
	python.exe -m pytest -q "Unit tests/test_user_model.py"
	python.exe -m pytest -q "Unit tests/test_payment_routes.py"
	python.exe -m pytest -q "Unit tests/test_app.py"

Notes

- The eventlet deprecation warning may appear when running app-related tests.
- The warning does not mean test failure.
