#!/usr/bin/env sh
# Write reports/coverage.md: which requirements the tests cover and how much code they run.
# Run from backend/: sh scripts/coverage_report.sh
set -eu
mkdir -p reports
requirements=$(mktemp)
trap 'rm -f "$requirements"' EXIT
uv run python -m pytest -q --cov --req-report="$requirements"
{
  echo "# Покрытие тестами"
  echo
  echo "Обновить: \`sh scripts/coverage_report.sh\` из \`backend/\`. Тот же отчёт строит CI-задача \`test-backend\`."
  echo
  # The requirement report's own headings move one level down under this document's title.
  echo "## Требования"
  sed -e '1d' -e 's/^## /### /' "$requirements"
  echo
  echo "## Код"
  echo
  echo "Строки и ветвления по модулям; файлы со 100 % покрытием не показаны."
  echo
  uv run coverage report --format=markdown --skip-covered
} > reports/coverage.md
