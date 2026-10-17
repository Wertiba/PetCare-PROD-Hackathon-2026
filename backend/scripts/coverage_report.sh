#!/usr/bin/env sh
# Refresh the committed test reports in docs/: requirement coverage and code coverage by module.
# Run from backend/: sh scripts/coverage_report.sh
set -eu
uv run python -m pytest -q --cov --cov-report=html:reports/coverage-html --req-report=docs/requirements-coverage.md
{
  echo "# Покрытие кода тестами"
  echo
  echo "Снимок \`coverage report\` (строки и ветвления). Обновить: \`sh scripts/coverage_report.sh\`;"
  echo "HTML-отчёт с подсветкой строк — \`reports/coverage-html/index.html\` и артефакт CI-задачи \`test-backend\`."
  echo
  uv run coverage report --format=markdown
} > docs/code-coverage.md
