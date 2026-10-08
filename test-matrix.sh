#!/bin/bash
set -e

PYTHON_VERSIONS=(3.11 3.12 3.13 3.14)
TEST_ENV=_venv

echo "Running test matrix across Python ${PYTHON_VERSIONS[*]}"

for pyver in "${PYTHON_VERSIONS[@]}"; do
    echo "━━━ Python $pyver ━━━"
    UV_PROJECT_ENVIRONMENT="$TEST_ENV" uv run --python $pyver -- pytest --cov=rudi_node_read --cov-report=term -q -p no:cacheprovider
    echo
done

rm -fr "$TEST_ENV"
