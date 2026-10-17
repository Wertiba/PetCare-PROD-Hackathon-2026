# Покрытие кода тестами

Снимок `coverage report` (строки и ветвления). Обновить: `sh scripts/coverage_report.sh`;
HTML-отчёт с подсветкой строк — `reports/coverage-html/index.html` и артефакт CI-задачи `test-backend`.

| Name                                                           |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/app/application/animals/di.py                              |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/animals/dto.py                             |       16 |        0 |        0 |        0 |    100% |           |
| src/app/application/animals/interactors.py                     |       57 |        0 |        4 |        1 |     98% |   60-\>62 |
| src/app/application/auth/di.py                                 |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/auth/dto.py                                |        9 |        0 |        0 |        0 |    100% |           |
| src/app/application/auth/interactors.py                        |      105 |        2 |       16 |        0 |     98% |     88-89 |
| src/app/application/breeds/di.py                               |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/breeds/dto.py                              |       19 |        0 |        0 |        0 |    100% |           |
| src/app/application/breeds/interactors.py                      |       73 |        1 |       10 |        3 |     95% |83, 84-\>87, 87-\>89 |
| src/app/application/categories/di.py                           |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/categories/dto.py                          |       24 |        0 |        0 |        0 |    100% |           |
| src/app/application/categories/interactors.py                  |       75 |        0 |       12 |        1 |     99% | 100-\>102 |
| src/app/application/changes.py                                 |        8 |        0 |        4 |        0 |    100% |           |
| src/app/application/events/di.py                               |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/events/dto.py                              |       39 |        0 |        0 |        0 |    100% |           |
| src/app/application/events/interactors.py                      |      102 |        0 |       14 |        0 |    100% |           |
| src/app/application/exceptions.py                              |        2 |        0 |        0 |        0 |    100% |           |
| src/app/application/foods/di.py                                |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/foods/dto.py                               |       34 |        0 |        0 |        0 |    100% |           |
| src/app/application/foods/interactors.py                       |       69 |        0 |        8 |        2 |     97% |104-\>106, 106-\>108 |
| src/app/application/notes/di.py                                |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/notes/dto.py                               |       18 |        0 |        0 |        0 |    100% |           |
| src/app/application/notes/interactors.py                       |       57 |        0 |        6 |        1 |     98% |   71-\>73 |
| src/app/application/notifications/di.py                        |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/notifications/dto.py                       |       25 |        0 |        0 |        0 |    100% |           |
| src/app/application/notifications/interactors.py               |       68 |        3 |        6 |        1 |     95% |   108-110 |
| src/app/application/pagination.py                              |       20 |        0 |        0 |        0 |    100% |           |
| src/app/application/pets/di.py                                 |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/pets/dto.py                                |       34 |        0 |        0 |        0 |    100% |           |
| src/app/application/pets/interactors.py                        |      114 |        2 |       28 |        4 |     96% |33-\>35, 96-\>98, 131, 134 |
| src/app/application/ports/animal\_gateway.py                   |        3 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/breed\_gateway.py                    |        4 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/category\_gateway.py                 |        4 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/database\_health.py                  |        1 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/event\_gateway.py                    |        6 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/food\_gateway.py                     |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/note\_gateway.py                     |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/notification\_gateway.py             |        7 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/pet\_gateway.py                      |        4 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/photos.py                            |        7 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/refresh\_token\_gateway.py           |        4 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/state\_gateway.py                    |        7 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/tokens.py                            |        3 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/unit\_of\_work.py                    |       13 |        0 |        0 |        0 |    100% |           |
| src/app/application/ports/user\_gateway.py                     |        3 |        0 |        0 |        0 |    100% |           |
| src/app/application/states/di.py                               |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/states/dto.py                              |       35 |        0 |        0 |        0 |    100% |           |
| src/app/application/states/interactors.py                      |       94 |        0 |       16 |        1 |     99% | 109-\>111 |
| src/app/application/users/access.py                            |       10 |        0 |        2 |        0 |    100% |           |
| src/app/application/users/di.py                                |        5 |        0 |        0 |        0 |    100% |           |
| src/app/application/users/dto.py                               |       41 |        0 |        0 |        0 |    100% |           |
| src/app/application/users/interactors.py                       |       30 |        2 |        4 |        2 |     88% |    35, 43 |
| src/app/bootstrap.py                                           |       18 |        0 |        0 |        0 |    100% |           |
| src/app/domain/animals/entity.py                               |       11 |        0 |        0 |        0 |    100% |           |
| src/app/domain/animals/errors.py                               |        4 |        0 |        0 |        0 |    100% |           |
| src/app/domain/animals/ids.py                                  |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/breeds/entity.py                                |       15 |        0 |        0 |        0 |    100% |           |
| src/app/domain/breeds/errors.py                                |        4 |        0 |        0 |        0 |    100% |           |
| src/app/domain/breeds/ids.py                                   |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/categories/entity.py                            |       15 |        0 |        0 |        0 |    100% |           |
| src/app/domain/categories/enums.py                             |       21 |        0 |        0 |        0 |    100% |           |
| src/app/domain/categories/errors.py                            |        7 |        0 |        0 |        0 |    100% |           |
| src/app/domain/categories/ids.py                               |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/errors.py                                       |        4 |        0 |        0 |        0 |    100% |           |
| src/app/domain/events/entity.py                                |       19 |        0 |        0 |        0 |    100% |           |
| src/app/domain/events/enums.py                                 |       21 |        0 |        0 |        0 |    100% |           |
| src/app/domain/events/errors.py                                |        6 |        0 |        0 |        0 |    100% |           |
| src/app/domain/events/ids.py                                   |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/events/periods.py                               |       16 |        0 |        6 |        0 |    100% |           |
| src/app/domain/events/rules.py                                 |        7 |        0 |        2 |        0 |    100% |           |
| src/app/domain/foods/entity.py                                 |       17 |        0 |        0 |        0 |    100% |           |
| src/app/domain/foods/errors.py                                 |        3 |        0 |        0 |        0 |    100% |           |
| src/app/domain/foods/ids.py                                    |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/foods/rules.py                                  |       16 |        0 |        4 |        0 |    100% |           |
| src/app/domain/notes/entity.py                                 |       12 |        0 |        0 |        0 |    100% |           |
| src/app/domain/notes/errors.py                                 |        3 |        0 |        0 |        0 |    100% |           |
| src/app/domain/notes/ids.py                                    |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/notifications/entity.py                         |       16 |        0 |        0 |        0 |    100% |           |
| src/app/domain/notifications/enums.py                          |       10 |        0 |        0 |        0 |    100% |           |
| src/app/domain/notifications/errors.py                         |        3 |        0 |        0 |        0 |    100% |           |
| src/app/domain/notifications/ids.py                            |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/pets/entity.py                                  |       18 |        0 |        0 |        0 |    100% |           |
| src/app/domain/pets/errors.py                                  |        8 |        0 |        0 |        0 |    100% |           |
| src/app/domain/pets/ids.py                                     |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/pets/rules.py                                   |       10 |        1 |        4 |        1 |     86% |        11 |
| src/app/domain/refresh\_tokens/entity.py                       |       14 |        0 |        0 |        0 |    100% |           |
| src/app/domain/refresh\_tokens/ids.py                          |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/states/entity.py                                |       15 |        0 |        0 |        0 |    100% |           |
| src/app/domain/states/errors.py                                |        8 |        0 |        0 |        0 |    100% |           |
| src/app/domain/states/ids.py                                   |        2 |        0 |        0 |        0 |    100% |           |
| src/app/domain/states/rules.py                                 |       11 |        0 |        6 |        0 |    100% |           |
| src/app/domain/users/entity.py                                 |       16 |        0 |        0 |        0 |    100% |           |
| src/app/domain/users/enums.py                                  |        4 |        0 |        0 |        0 |    100% |           |
| src/app/domain/users/errors.py                                 |       16 |        0 |        0 |        0 |    100% |           |
| src/app/domain/users/ids.py                                    |        2 |        0 |        0 |        0 |    100% |           |
| src/app/infra/config.py                                        |       18 |        4 |        4 |        1 |     68% |     40-43 |
| src/app/infra/database/db\_helper.py                           |        9 |        0 |        0 |        0 |    100% |           |
| src/app/infra/database/di.py                                   |       23 |        0 |        2 |        0 |    100% |           |
| src/app/infra/database/health.py                               |        8 |        0 |        0 |        0 |    100% |           |
| src/app/infra/database/mappings.py                             |       53 |        0 |        2 |        0 |    100% |           |
| src/app/infra/database/unit\_of\_work.py                       |       21 |        2 |        0 |        0 |     90% |     18-19 |
| src/app/infra/duration.py                                      |        9 |        0 |        2 |        0 |    100% |           |
| src/app/infra/gateways/animal.py                               |       37 |        5 |        2 |        1 |     85% |20-21, 38-39, 44 |
| src/app/infra/gateways/breed.py                                |       40 |        4 |        4 |        0 |     91% |21-22, 41-42 |
| src/app/infra/gateways/category.py                             |       40 |        4 |        4 |        0 |     91% |21-22, 40-41 |
| src/app/infra/gateways/di.py                                   |       36 |        0 |        0 |        0 |    100% |           |
| src/app/infra/gateways/event.py                                |       75 |        6 |       14 |        1 |     92% |21-\>23, 26-27, 72-73, 92-93 |
| src/app/infra/gateways/food.py                                 |       56 |        6 |        8 |        1 |     89% |20-\>22, 25-26, 68-69, 81-82 |
| src/app/infra/gateways/note.py                                 |       47 |        4 |        6 |        1 |     91% |20-\>22, 25-26, 46-47 |
| src/app/infra/gateways/notification.py                         |       54 |        5 |       10 |        2 |     89% |23-\>25, 28-29, 74-75, 98 |
| src/app/infra/gateways/pet.py                                  |       35 |        4 |        2 |        1 |     86% |19-\>21, 24-25, 47-48 |
| src/app/infra/gateways/refresh\_token.py                       |       31 |       10 |        0 |        0 |     68% |17-22, 29-30, 36-37 |
| src/app/infra/gateways/state.py                                |       79 |        8 |       16 |        1 |     91% |29-\>31, 34-35, 77-78, 103-104, 116-117 |
| src/app/infra/gateways/user.py                                 |       24 |        2 |        0 |        0 |     92% |     28-29 |
| src/app/infra/logger.py                                        |       37 |        6 |        8 |        3 |     80% |15-16, 20-21, 29, 32 |
| src/app/infra/metrics.py                                       |        7 |        0 |        0 |        0 |    100% |           |
| src/app/infra/photos/di.py                                     |        8 |        0 |        0 |        0 |    100% |           |
| src/app/infra/photos/storage.py                                |       22 |        1 |        4 |        1 |     92% |        27 |
| src/app/infra/security/di.py                                   |        5 |        0 |        0 |        0 |    100% |           |
| src/app/infra/security/jwt\_service.py                         |       45 |        0 |        4 |        1 |     98% |   26-\>28 |
| src/app/infra/singleton.py                                     |        6 |        0 |        2 |        1 |     88% |     5-\>7 |
| src/app/main.py                                                |       35 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/\_\_init\_\_.py                  |        3 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/endpoints/\_\_init\_\_.py        |        6 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/endpoints/health.py              |       19 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/endpoints/metrics.py             |        6 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/dependencies/\_\_init\_\_.py  |        3 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/dependencies/current\_user.py |       13 |        0 |        2 |        0 |    100% |           |
| src/app/presentation/http/api/v1/dependencies/pagination.py    |        6 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/\_\_init\_\_.py     |       24 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/animals.py          |       34 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/auth.py             |       42 |        0 |        4 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/breeds.py           |       36 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/categories.py       |       35 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/events.py           |       51 |        0 |        6 |        1 |     98% | 106-\>108 |
| src/app/presentation/http/api/v1/endpoints/foods.py            |       37 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/notes.py            |       34 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/notifications.py    |       35 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/pets.py             |       40 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/states.py           |       38 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/endpoints/users.py            |       13 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/exceptions/\_\_init\_\_.py    |        3 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/exceptions/api\_exs.py        |       82 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/exceptions/base.py            |       19 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/exceptions/exc\_map.py        |       13 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/exceptions/handlers.py        |       45 |        4 |        6 |        2 |     88% |30-\>35, 38-39, 58-59 |
| src/app/presentation/http/api/v1/utils/\_\_init\_\_.py         |        2 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/api/v1/utils/cookies.py              |        7 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/loc2field.py                         |       24 |        1 |       12 |        2 |     92% | 6-\>8, 12 |
| src/app/presentation/http/middleware/observability.py          |       36 |        1 |        6 |        1 |     95% |        23 |
| src/app/presentation/http/middleware/trace\_id.py              |       20 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/paginated.py                         |       20 |        5 |        2 |        0 |     68% |10, 14, 25-28 |
| src/app/presentation/http/password.py                          |        9 |        0 |        6 |        0 |    100% |           |
| src/app/presentation/http/schemas/animal.py                    |       19 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/schemas/base.py                      |       14 |        3 |        6 |        3 |     70% |  6, 9, 16 |
| src/app/presentation/http/schemas/breed.py                     |       29 |        0 |        2 |        0 |    100% |           |
| src/app/presentation/http/schemas/category.py                  |       30 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/schemas/event.py                     |       62 |        0 |        2 |        0 |    100% |           |
| src/app/presentation/http/schemas/food.py                      |       55 |        0 |        2 |        0 |    100% |           |
| src/app/presentation/http/schemas/note.py                      |       21 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/schemas/notification.py              |       30 |        0 |        2 |        0 |    100% |           |
| src/app/presentation/http/schemas/pet.py                       |       60 |        3 |       10 |        1 |     94% | 31, 47-48 |
| src/app/presentation/http/schemas/responses.py                 |       27 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/schemas/state.py                     |       45 |        0 |        2 |        0 |    100% |           |
| src/app/presentation/http/schemas/token.py                     |        7 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/schemas/user.py                      |       30 |        0 |        0 |        0 |    100% |           |
| src/app/presentation/http/uploads.py                           |       14 |        0 |        4 |        0 |    100% |           |
| **TOTAL**                                                      | **3757** |   **99** |  **320** |   **42** | **96%** |           |

36 empty files skipped.
