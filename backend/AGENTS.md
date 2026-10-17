## Commands
- Install: 'uv sync'
- Add dependency: 'uv add'
- Run tests: 'uv run pytest'
- Lint: 'uv run ruff check .'
- Format: 'uv run ruff check . --fix; uv run ruff format .'
- Docker: enter nix develop shell via 'nix develop', it provides docker, docker-compose and colima

## Architecture
Clean Architecture as defined by Robert Martin

- 'src/app/domain': domain entities, value objects, domain services
everything is grouped by entity, e.g., src/app/domain/<entity_name>/{entity.py,vo.py,}
- 'src/app/application': use-case interactors: each under src/application/<entity_name>; ports
- 'src/app/infra': adapters (port implementations)
- 'src/app/presentation': app presentation: src/app/presentation/http/api - fastapi api

dependencies must point inward: presentation -> infra -> application -> domain, ie no code in domain can import code from application or other layers
domain/application must not contain details or concrete implementations

## Code conventions
- use dishka for dependency injection: providers must stay close to what they provide, e.g., user interactors provider is under 'src/app/application/users/di'
- use gateways for reading
- use unit of work for writing as defined by Martin Fowler [UoW](https://martinfowler.com/eaaCatalog/unitOfWork.html)
