run-api:
	uvicorn apps.api.main:app --reload

test:
	pytest tests/
