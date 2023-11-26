
poetry_export:
	poetry export --with dev --output backend/requirements-dev.txt && \
	poetry export -f requirements.txt --without=dev --output backend/requirements.txt