#!make

.PHONY : tests

# Main test target
tests: setup-test-containers run-tests teardown-test-containers

# Test runner
# NB: `pytest-alembic` requires the DB engine to point an empty database. Thus, alembic
# tests should be run first.
run-tests:
	@set -a && source ./tests/api/test.env && set +a && \
	python -m pytest -rPQ tests

## Helper targets
setup-test-containers: setup-test-db
teardown-test-containers: teardown-test-db

setup-test-db:
	-@docker stop testdb
	-@docker rm testdb
	@docker system prune -f
	@sleep 2
	@set -a && source ./tests/api/test.env && set +a && \
	docker run --name testdb \
		-p 5433:5432 \
		-e POSTGRES_PASSWORD \
		-e POSTGRES_USER \
		-e POSTGRES_DB \
		-d pgvector/pgvector:pg16
	@set -a && source ./tests/api/test.env && set +a && \
	python -m alembic upgrade head

teardown-test-db:
	@docker stop testdb
	@docker rm testdb
