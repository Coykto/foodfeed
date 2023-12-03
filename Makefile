
poetry:
	poetry lock && \
	poetry export --with=dev --with=layer --without-hashes --without-urls --output backend/requirements-dev.txt && \
	poetry export --without=dev --with=layer --without-hashes --without-urls --output backend/requirements.txt && \
	poetry export --only=layer --without-hashes --without-urls --output backend/python/lambdas/requirements.txt