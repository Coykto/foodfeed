
poetry:
	poetry export --with dev --without-hashes --without-urls --ansi --output backend/requirements-dev.txt && \
	poetry export --without dev --without-hashes --without-urls --ansi --output backend/requirements-dev.txt