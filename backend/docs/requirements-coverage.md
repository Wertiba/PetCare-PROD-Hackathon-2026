# Покрытие требований тестами

Покрыто требований: **30 из 33**. Отчёт генерирует `pytest --req-report=PATH` по маркерам `@pytest.mark.req`.


## Сценарии

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| S1 | Сценарий 1. Добавление питомца | 2 | ✅ покрыто |
| S2 | Сценарий 2. Ведение истории здоровья | 1 | ✅ покрыто |
| S3 | Сценарий 3. Учёт питания | 1 | ✅ покрыто |
| S4 | Сценарий 4. Контроль предстоящих процедур | 1 | ✅ покрыто |

## 5.1 Карточки питомцев

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.1.1 | Создание карточки питомца | 14 | ✅ покрыто |
| 5.1.2 | Имя, вид, порода и дата рождения | 7 | ✅ покрыто |
| 5.1.3 | Добавление фотографии | 4 | ✅ покрыто |
| 5.1.4 | Список питомцев пользователя | 2 | ✅ покрыто |

## 5.2 Карта здоровья

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.2.1 | История вакцинаций с датами | 5 | ✅ покрыто |
| 5.2.2 | История обработок от паразитов | 2 | ✅ покрыто |
| 5.2.3 | Записи о посещениях ветеринара | 3 | ✅ покрыто |
| 5.2.4 | Хранение заключений ветеринаров | 6 | ✅ покрыто |
| 5.2.5 | Учёт веса и других параметров | 19 | ✅ покрыто |

## 5.3 Учёт питания

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.3.1 | Записи о кормах | 8 | ✅ покрыто |
| 5.3.2 | Оценка «понравилось / не понравилось» | 3 | ✅ покрыто |
| 5.3.3 | Оценка «подошло / не подошло» | 5 | ✅ покрыто |
| 5.3.4 | Нежелательные реакции: ЖКТ, аллергия | 4 | ✅ покрыто |
| 5.3.5 | История питания и личная база предпочтений | 7 | ✅ покрыто |

## 5.4 Напоминания и назначения

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.4.1 | Расчёт даты следующей вакцинации | 13 | ✅ покрыто |
| 5.4.2 | Расчёт даты следующей обработки от паразитов | 8 | ✅ покрыто |
| 5.4.3 | Назначения препаратов из ветеринарных заключений | 0 | ⚪ нет тестов |
| 5.4.4 | Длительность и регулярность приёма препаратов | 0 | ⚪ нет тестов |
| 5.4.5 | Формирование напоминаний | 8 | ✅ покрыто |
| 5.4.6 | Список ближайших событий | 4 | ✅ покрыто |
| 5.4.7 | Уведомления через push или виджет | 0 | ⚪ нет тестов |

## 7–8 UX и ограничения

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 7.1 | Понятные ошибки форм с указанием проблемного поля | 22 | ✅ покрыто |

## Платформа

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| P.AUTH | Регистрация, вход, обновление токена, выход | 48 | ✅ покрыто |
| P.ACCESS | Изоляция данных пользователей и права ролей | 30 | ✅ покрыто |
| P.CATALOG | Справочник видов, пород и категорий | 16 | ✅ покрыто |
| P.TX | Транзакции: Unit of Work и откаты | 10 | ✅ покрыто |
| P.TIME | Единый формат времени (Unix seconds, UTC) | 25 | ✅ покрыто |
| P.OBS | Наблюдаемость: trace id, логи, метрики, health | 31 | ✅ покрыто |
| P.ARCH | Контракт API, схема БД, границы слоёв | 7 | ✅ покрыто |

## Тесты по требованиям

<details><summary>S1 — Сценарий 1. Добавление питомца (2)</summary>

- `tests/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed
- `tests/test_user_scenarios.py::test_scenario_1_quick_form_highlights_the_missing_name` — passed

</details>

<details><summary>S2 — Сценарий 2. Ведение истории здоровья (1)</summary>

- `tests/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>S3 — Сценарий 3. Учёт питания (1)</summary>

- `tests/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>S4 — Сценарий 4. Контроль предстоящих процедур (1)</summary>

- `tests/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.1.1 — Создание карточки питомца (14)</summary>

- `tests/test_pets_endpoints.py::test_blank_name_is_422` — passed
- `tests/test_pets_endpoints.py::test_breed_is_required_and_must_exist` — passed
- `tests/test_pets_endpoints.py::test_create_minimal_pet` — passed
- `tests/test_pets_endpoints.py::test_delete_pet_removes_photo_file` — passed
- `tests/test_pets_endpoints.py::test_future_birth_date_is_422` — passed
- `tests/test_pets_endpoints.py::test_list_returns_only_current_users_pets` — passed
- `tests/test_pets_endpoints.py::test_null_name_on_patch_is_422` — passed
- `tests/test_pets_endpoints.py::test_other_users_pet_is_not_found` — passed
- `tests/test_pets_endpoints.py::test_past_birth_date_returns_age_months` — passed
- `tests/test_pets_endpoints.py::test_patch_changes_breed_and_animal_and_clears_birth_date` — passed
- `tests/test_pets_endpoints.py::test_pet_keeps_living_after_its_breed_is_deleted` — passed
- `tests/test_pets_endpoints.py::test_photo_upload_wrong_type_and_too_large` — passed
- `tests/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed
- `tests/test_user_scenarios.py::test_scenario_1_quick_form_highlights_the_missing_name` — passed

</details>

<details><summary>5.1.2 — Имя, вид, порода и дата рождения (7)</summary>

- `tests/test_animals_breeds_endpoints.py::test_everyone_reads_seeded_animals_and_breeds` — passed
- `tests/test_pets_endpoints.py::test_breed_is_required_and_must_exist` — passed
- `tests/test_pets_endpoints.py::test_create_minimal_pet` — passed
- `tests/test_pets_endpoints.py::test_future_birth_date_is_422` — passed
- `tests/test_pets_endpoints.py::test_past_birth_date_returns_age_months` — passed
- `tests/test_pets_endpoints.py::test_patch_changes_breed_and_animal_and_clears_birth_date` — passed
- `tests/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed

</details>

<details><summary>5.1.3 — Добавление фотографии (4)</summary>

- `tests/test_pets_endpoints.py::test_delete_pet_removes_photo_file` — passed
- `tests/test_pets_endpoints.py::test_photo_upload_wrong_type_and_too_large` — passed
- `tests/test_transactions.py::test_failed_photo_update_keeps_old_file_and_removes_new_file` — passed
- `tests/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed

</details>

<details><summary>5.1.4 — Список питомцев пользователя (2)</summary>

- `tests/test_pets_endpoints.py::test_list_returns_only_current_users_pets` — passed
- `tests/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed

</details>

<details><summary>5.2.1 — История вакцинаций с датами (5)</summary>

- `tests/test_events_endpoints.py::test_create_with_defaults_and_frontend_shape` — passed
- `tests/test_events_endpoints.py::test_deleting_pet_cascades_to_events` — passed
- `tests/test_events_endpoints.py::test_list_filters` — passed
- `tests/test_events_endpoints.py::test_update_validation_and_delete` — passed
- `tests/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.2 — История обработок от паразитов (2)</summary>

- `tests/test_events_endpoints.py::test_list_filters` — passed
- `tests/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.3 — Записи о посещениях ветеринара (3)</summary>

- `tests/test_events_endpoints.py::test_list_filters` — passed
- `tests/test_events_endpoints.py::test_one_off_completion_has_no_next` — passed
- `tests/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.4 — Хранение заключений ветеринаров (6)</summary>

- `tests/test_notes_endpoints.py::test_crud` — passed
- `tests/test_notes_endpoints.py::test_list_filters_by_pet_and_text_newest_first` — passed
- `tests/test_notes_endpoints.py::test_other_users_notes_are_invisible` — passed
- `tests/test_notes_endpoints.py::test_requires_auth` — passed
- `tests/test_notes_endpoints.py::test_validation_and_pet_cascade` — passed
- `tests/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.5 — Учёт веса и других параметров (19)</summary>

- `tests/test_categories_endpoints.py::test_list_shows_system_first_then_own` — passed
- `tests/test_resilience_and_edge_cases.py::test_state_patch_changes_only_the_given_fields` — passed
- `tests/test_states_endpoints.py::test_create_and_read_state` — passed
- `tests/test_states_endpoints.py::test_deleting_pet_cascades_to_states` — passed
- `tests/test_states_endpoints.py::test_foreign_pet_and_unknown_category` — passed
- `tests/test_states_endpoints.py::test_list_filters_and_isolation` — passed
- `tests/test_states_endpoints.py::test_summary_aggregates_by_kind[appetite-values2-3.0]` — passed
- `tests/test_states_endpoints.py::test_summary_aggregates_by_kind[food-values1-300.0]` — passed
- `tests/test_states_endpoints.py::test_summary_aggregates_by_kind[liked-values3-3.0]` — passed
- `tests/test_states_endpoints.py::test_summary_aggregates_by_kind[weight-values0-4300.0]` — passed
- `tests/test_states_endpoints.py::test_summary_with_period_and_empty` — passed
- `tests/test_states_endpoints.py::test_time_defaults_to_now` — passed
- `tests/test_states_endpoints.py::test_update_and_delete` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[appetite-0]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[appetite-6]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[liked--1]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[liked-2]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[weight--5]` — passed
- `tests/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.3.1 — Записи о кормах (8)</summary>

- `tests/test_foods_endpoints.py::test_crud` — passed
- `tests/test_foods_endpoints.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/test_foods_endpoints.py::test_list_filters` — passed
- `tests/test_foods_endpoints.py::test_other_users_food_is_invisible` — passed
- `tests/test_foods_endpoints.py::test_requires_auth` — passed
- `tests/test_foods_endpoints.py::test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food` — passed
- `tests/test_foods_endpoints.py::test_validation` — passed
- `tests/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.2 — Оценка «понравилось / не понравилось» (3)</summary>

- `tests/test_foods_endpoints.py::test_crud` — passed
- `tests/test_foods_endpoints.py::test_list_filters` — passed
- `tests/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.3 — Оценка «подошло / не подошло» (5)</summary>

- `tests/test_food_rules.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/test_food_rules.py::test_suspects_ignore_case_and_spacing_and_keep_order` — passed
- `tests/test_foods_endpoints.py::test_crud` — passed
- `tests/test_foods_endpoints.py::test_list_filters` — passed
- `tests/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.4 — Нежелательные реакции: ЖКТ, аллергия (4)</summary>

- `tests/test_categories_endpoints.py::test_list_shows_system_first_then_own` — passed
- `tests/test_foods_endpoints.py::test_crud` — passed
- `tests/test_foods_endpoints.py::test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food` — passed
- `tests/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.5 — История питания и личная база предпочтений (7)</summary>

- `tests/test_food_rules.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/test_food_rules.py::test_normalize_trims_and_drops_blanks_and_case_insensitive_duplicates` — passed
- `tests/test_food_rules.py::test_suspects_ignore_case_and_spacing_and_keep_order` — passed
- `tests/test_foods_endpoints.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/test_foods_endpoints.py::test_list_filters` — passed
- `tests/test_foods_endpoints.py::test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food` — passed
- `tests/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.4.1 — Расчёт даты следующей вакцинации (13)</summary>

- `tests/test_events_endpoints.py::test_complete_plans_next_occurrence` — passed
- `tests/test_events_endpoints.py::test_late_completion_counts_from_done_date` — passed
- `tests/test_events_endpoints.py::test_next_schedule_is_calculated` — passed
- `tests/test_events_endpoints.py::test_patch_status_done_also_plans_next` — passed
- `tests/test_transactions.py::test_failed_completion_rolls_back_both_events` — passed
- `tests/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[daily-expected1]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[half_year-expected5]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[monthly-expected3]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[none-None]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[quarterly-expected4]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[weekly-expected2]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[yearly-expected6]` — passed

</details>

<details><summary>5.4.2 — Расчёт даты следующей обработки от паразитов (8)</summary>

- `tests/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[daily-expected1]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[half_year-expected5]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[monthly-expected3]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[none-None]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[quarterly-expected4]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[weekly-expected2]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[yearly-expected6]` — passed

</details>

<details><summary>5.4.5 — Формирование напоминаний (8)</summary>

- `tests/test_events_endpoints.py::test_complete_plans_next_occurrence` — passed
- `tests/test_notifications_endpoints.py::test_create_defaults_to_event_schedule` — passed
- `tests/test_notifications_endpoints.py::test_delete_and_cascade_from_event` — passed
- `tests/test_notifications_endpoints.py::test_due_filter_and_mark_read` — passed
- `tests/test_notifications_endpoints.py::test_filter_by_event` — passed
- `tests/test_notifications_endpoints.py::test_invalid_values` — passed
- `tests/test_notifications_endpoints.py::test_isolation_and_unknown_event` — passed
- `tests/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.4.6 — Список ближайших событий (4)</summary>

- `tests/test_events_endpoints.py::test_upcoming_includes_overdue_and_excludes_far_and_done` — passed
- `tests/test_notifications_endpoints.py::test_due_filter_and_mark_read` — passed
- `tests/test_resilience_and_edge_cases.py::test_upcoming_can_be_narrowed_to_one_pet` — passed
- `tests/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>7.1 — Понятные ошибки форм с указанием проблемного поля (22)</summary>

- `tests/test_animals_breeds_endpoints.py::test_catalog_validation_and_duplicates` — passed
- `tests/test_auth_endpoints.py::test_register_rejects_full_name_with_invalid_characters` — passed
- `tests/test_auth_endpoints.py::test_validation_error_message_is_english` — passed
- `tests/test_categories_endpoints.py::test_validation_errors` — passed
- `tests/test_events_endpoints.py::test_update_validation_and_delete` — passed
- `tests/test_foods_endpoints.py::test_validation` — passed
- `tests/test_notes_endpoints.py::test_validation_and_pet_cascade` — passed
- `tests/test_notifications_endpoints.py::test_invalid_values` — passed
- `tests/test_pets_endpoints.py::test_blank_name_is_422` — passed
- `tests/test_pets_endpoints.py::test_breed_is_required_and_must_exist` — passed
- `tests/test_pets_endpoints.py::test_future_birth_date_is_422` — passed
- `tests/test_pets_endpoints.py::test_null_name_on_patch_is_422` — passed
- `tests/test_pets_endpoints.py::test_photo_upload_wrong_type_and_too_large` — passed
- `tests/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[1234567890-at least one letter]` — passed
- `tests/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[onlyletters-at least one digit]` — passed
- `tests/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[short1-between 8 and 72]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[appetite-0]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[appetite-6]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[liked--1]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[liked-2]` — passed
- `tests/test_states_endpoints.py::test_value_must_fit_category_type[weight--5]` — passed
- `tests/test_user_scenarios.py::test_scenario_1_quick_form_highlights_the_missing_name` — passed

</details>

<details><summary>P.AUTH — Регистрация, вход, обновление токена, выход (48)</summary>

- `tests/test_auth_endpoints.py::test_email_does_not_replace_login[login]` — passed
- `tests/test_auth_endpoints.py::test_email_does_not_replace_login[register]` — passed
- `tests/test_auth_endpoints.py::test_invalid_login_is_rejected[login-]` — passed
- `tests/test_auth_endpoints.py::test_invalid_login_is_rejected[login-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` — passed
- `tests/test_auth_endpoints.py::test_invalid_login_is_rejected[register-]` — passed
- `tests/test_auth_endpoints.py::test_invalid_login_is_rejected[register-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` — passed
- `tests/test_auth_endpoints.py::test_login_migration_renames_identifier_and_unique_constraint` — passed
- `tests/test_auth_endpoints.py::test_login_returns_200_and_sets_refresh_cookie` — passed
- `tests/test_auth_endpoints.py::test_login_with_wrong_password_returns_401` — passed
- `tests/test_auth_endpoints.py::test_logout_clears_cookie_and_revokes_refresh_token` — passed
- `tests/test_auth_endpoints.py::test_logout_without_cookie_returns_401` — passed
- `tests/test_auth_endpoints.py::test_refresh_rotates_cookie_and_invalidates_previous_refresh_token` — passed
- `tests/test_auth_endpoints.py::test_refresh_without_cookie_returns_401` — passed
- `tests/test_auth_endpoints.py::test_register_accepts_cyrillic_full_name` — passed
- `tests/test_auth_endpoints.py::test_register_rejects_duplicate_login` — passed
- `tests/test_auth_endpoints.py::test_register_rejects_full_name_with_invalid_characters` — passed
- `tests/test_auth_endpoints.py::test_register_returns_201_and_sets_cookie` — passed
- `tests/test_auth_endpoints.py::test_validation_error_message_is_english` — passed
- `tests/test_auth_interactors.py::test_login_with_correct_credentials_returns_token_pair` — passed
- `tests/test_auth_interactors.py::test_login_with_unknown_login_raises` — passed
- `tests/test_auth_interactors.py::test_login_with_wrong_password_raises` — passed
- `tests/test_auth_interactors.py::test_logout_deletes_refresh_token_and_is_idempotent` — passed
- `tests/test_auth_interactors.py::test_refresh_rotates_token_and_invalidates_old_one` — passed
- `tests/test_auth_interactors.py::test_refresh_with_unknown_token_raises` — passed
- `tests/test_auth_interactors.py::test_register_creates_user_and_returns_token_pair` — passed
- `tests/test_auth_interactors.py::test_register_rejects_duplicate_login` — passed
- `tests/test_auth_interactors.py::test_verify_access_token_returns_current_user_data` — passed
- `tests/test_cookies.py::test_delete_refresh_cookie_expires_it` — passed
- `tests/test_cookies.py::test_set_refresh_cookie_sets_expected_attributes` — passed
- `tests/test_duration.py::test_parses_days` — passed
- `tests/test_duration.py::test_parses_minutes` — passed
- `tests/test_duration.py::test_parses_seconds_and_hours` — passed
- `tests/test_duration.py::test_rejects_bad_format` — passed
- `tests/test_jwt_service.py::test_access_token_has_expected_claims` — passed
- `tests/test_jwt_service.py::test_decode_token_accepts_matching_type` — passed
- `tests/test_jwt_service.py::test_decode_token_rejects_garbage` — passed
- `tests/test_jwt_service.py::test_decode_token_rejects_wrong_type` — passed
- `tests/test_jwt_service.py::test_expire_seconds_come_from_env_vars` — passed
- `tests/test_jwt_service.py::test_hash_token_is_deterministic_sha256` — passed
- `tests/test_jwt_service.py::test_password_hash_roundtrip` — passed
- `tests/test_jwt_service.py::test_refresh_token_has_refresh_type` — passed
- `tests/test_resilience_and_edge_cases.py::test_deactivated_user_cannot_log_in_refresh_or_use_tokens` — passed
- `tests/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[1234567890-at least one letter]` — passed
- `tests/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[onlyletters-at least one digit]` — passed
- `tests/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[short1-between 8 and 72]` — passed
- `tests/test_resilience_and_edge_cases.py::test_token_of_a_deleted_user_is_rejected` — passed
- `tests/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed
- `tests/test_users_and_observability.py::test_me_returns_and_updates_profile` — passed

</details>

<details><summary>P.ACCESS — Изоляция данных пользователей и права ролей (30)</summary>

- `tests/test_animals_breeds_endpoints.py::test_only_admin_writes_the_catalog` — passed
- `tests/test_animals_breeds_endpoints.py::test_requires_auth` — passed
- `tests/test_categories_endpoints.py::test_admin_changes_any_category` — passed
- `tests/test_categories_endpoints.py::test_categories_are_shared_but_only_the_author_changes_them` — passed
- `tests/test_categories_endpoints.py::test_requires_auth` — passed
- `tests/test_categories_endpoints.py::test_system_category_is_read_only` — passed
- `tests/test_events_endpoints.py::test_isolation_and_unknown_pet` — passed
- `tests/test_foods_endpoints.py::test_other_users_food_is_invisible` — passed
- `tests/test_foods_endpoints.py::test_requires_auth` — passed
- `tests/test_notes_endpoints.py::test_other_users_notes_are_invisible` — passed
- `tests/test_notes_endpoints.py::test_requires_auth` — passed
- `tests/test_notifications_endpoints.py::test_isolation_and_unknown_event` — passed
- `tests/test_pets_endpoints.py::test_list_returns_only_current_users_pets` — passed
- `tests/test_pets_endpoints.py::test_other_users_pet_is_not_found` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/animals-animals]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/breeds-breeds]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/categories-categories]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events-events]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events/upcoming-events]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/foods-food]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notes-notes]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notifications-notifications]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/pets-pets]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/states-states]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/users/me-users]` — passed
- `tests/test_resilience_and_edge_cases.py::test_deactivated_user_cannot_log_in_refresh_or_use_tokens` — passed
- `tests/test_resilience_and_edge_cases.py::test_upcoming_can_be_narrowed_to_one_pet` — passed
- `tests/test_states_endpoints.py::test_foreign_pet_and_unknown_category` — passed
- `tests/test_states_endpoints.py::test_list_filters_and_isolation` — passed
- `tests/test_user_scenarios.py::test_another_owner_sees_nothing_of_barsik` — passed

</details>

<details><summary>P.CATALOG — Справочник видов, пород и категорий (16)</summary>

- `tests/test_animals_breeds_endpoints.py::test_admin_manages_animals_and_breeds` — passed
- `tests/test_animals_breeds_endpoints.py::test_breed_search_by_name` — passed
- `tests/test_animals_breeds_endpoints.py::test_catalog_validation_and_duplicates` — passed
- `tests/test_animals_breeds_endpoints.py::test_everyone_reads_seeded_animals_and_breeds` — passed
- `tests/test_animals_breeds_endpoints.py::test_only_admin_writes_the_catalog` — passed
- `tests/test_animals_breeds_endpoints.py::test_requires_auth` — passed
- `tests/test_categories_endpoints.py::test_admin_changes_any_category` — passed
- `tests/test_categories_endpoints.py::test_categories_are_shared_but_only_the_author_changes_them` — passed
- `tests/test_categories_endpoints.py::test_category_used_by_others_keeps_its_meaning` — passed
- `tests/test_categories_endpoints.py::test_filters_by_type_and_name` — passed
- `tests/test_categories_endpoints.py::test_list_shows_system_first_then_own` — passed
- `tests/test_categories_endpoints.py::test_requires_auth` — passed
- `tests/test_categories_endpoints.py::test_system_category_is_read_only` — passed
- `tests/test_categories_endpoints.py::test_update_and_delete_own` — passed
- `tests/test_categories_endpoints.py::test_validation_errors` — passed
- `tests/test_pets_endpoints.py::test_pet_keeps_living_after_its_breed_is_deleted` — passed

</details>

<details><summary>P.TX — Транзакции: Unit of Work и откаты (10)</summary>

- `tests/test_transactions.py::test_authentication_gateway_and_uow_share_one_session` — passed
- `tests/test_transactions.py::test_commit_time_duplicate_login_keeps_the_existing_error_contract` — passed
- `tests/test_transactions.py::test_failed_completion_rolls_back_both_events` — passed
- `tests/test_transactions.py::test_failed_photo_update_keeps_old_file_and_removes_new_file` — passed
- `tests/test_transactions.py::test_failed_registration_rolls_back_user_and_token` — passed
- `tests/test_transactions.py::test_failed_rotation_preserves_original_refresh_token` — passed
- `tests/test_transactions.py::test_read_only_request_never_commits` — passed
- `tests/test_unit_of_work.py::test_add_query_tracked_update_and_delete` — passed
- `tests/test_unit_of_work.py::test_failed_commit_rolls_back_the_entire_write` — passed
- `tests/test_unit_of_work.py::test_uncommitted_changes_are_discarded` — passed

</details>

<details><summary>P.TIME — Единый формат времени (Unix seconds, UTC) (25)</summary>

- `tests/test_timestamps.py::test_all_persistent_instant_columns_are_numeric` — passed
- `tests/test_timestamps.py::test_birth_timestamp_normalizes_to_utc_midnight` — passed
- `tests/test_timestamps.py::test_calendar_recurrence_preserves_fractional_seconds_and_clamps_leap_days` — passed
- `tests/test_timestamps.py::test_documented_timestamp_fields_are_numbers` — passed
- `tests/test_timestamps.py::test_fractional_timestamp_roundtrip_and_epoch_zero` — passed
- `tests/test_timestamps.py::test_iso_dates_are_rejected_and_error_timestamps_are_numeric` — passed
- `tests/test_timestamps.py::test_nonfinite_body_timestamps_return_validation_errors[-Infinity]` — passed
- `tests/test_timestamps.py::test_nonfinite_body_timestamps_return_validation_errors[Infinity]` — passed
- `tests/test_timestamps.py::test_nonfinite_body_timestamps_return_validation_errors[NaN]` — passed
- `tests/test_timestamps.py::test_nonfinite_query_timestamps_return_validation_errors[-Infinity]` — passed
- `tests/test_timestamps.py::test_nonfinite_query_timestamps_return_validation_errors[Infinity]` — passed
- `tests/test_timestamps.py::test_nonfinite_query_timestamps_return_validation_errors[NaN]` — passed
- `tests/test_timestamps.py::test_timestamp_migration_has_explicit_utc_and_reversible_conversions` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete--1e+100]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete--62135596801.0]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete-1e+100]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete-253402300800.0]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create--1e+100]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create--62135596801.0]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create-1e+100]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create-253402300800.0]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update--1e+100]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update--62135596801.0]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update-1e+100]` — passed
- `tests/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update-253402300800.0]` — passed

</details>

<details><summary>P.OBS — Наблюдаемость: trace id, логи, метрики, health (31)</summary>

- `tests/test_app_boot.py::test_app_imports_and_liveness_responds` — passed
- `tests/test_app_boot.py::test_user_role_has_no_typo` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/animals-animals]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/breeds-breeds]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/categories-categories]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events-events]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events/upcoming-events]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/foods-food]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notes-notes]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notifications-notifications]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/pets-pets]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/states-states]` — passed
- `tests/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/users/me-users]` — passed
- `tests/test_resilience_and_edge_cases.py::test_readiness_reports_ready_database` — passed
- `tests/test_resilience_and_edge_cases.py::test_readiness_reports_unavailable_database` — passed
- `tests/test_trace_id.py::test_cors_allows_configured_origin` — passed
- `tests/test_trace_id.py::test_cors_rejects_unconfigured_origin` — passed
- `tests/test_trace_id.py::test_error_response_trace_id_matches_request_header` — passed
- `tests/test_trace_id.py::test_response_always_includes_trace_id_header` — passed
- `tests/test_trace_id.py::test_trace_id_header_is_echoed_back_when_provided` — passed
- `tests/test_users_and_observability.py::test_me_returns_and_updates_profile` — passed
- `tests/test_users_and_observability.py::test_metrics_endpoint_exposes_request_and_domain_counters` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[daily-expected1]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[half_year-expected5]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[monthly-expected3]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[none-None]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[quarterly-expected4]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[weekly-expected2]` — passed
- `tests/test_users_and_observability.py::test_next_occurrence[yearly-expected6]` — passed
- `tests/test_users_and_observability.py::test_trace_id_is_echoed_and_used_in_errors` — passed
- `tests/test_users_and_observability.py::test_validation_error_with_non_uuid_trace_id` — passed

</details>

<details><summary>P.ARCH — Контракт API, схема БД, границы слоёв (7)</summary>

- `tests/test_architecture_and_contract.py::test_inner_layers_do_not_import_frameworks_or_outer_layers` — passed
- `tests/test_architecture_and_contract.py::test_openapi_matches_the_documented_api_contract` — passed
- `tests/test_architecture_and_contract.py::test_postgres_schema_matches_documented_tables_and_indexes` — passed
- `tests/test_models.py::test_category_id_migration_renames_column_constraint_and_index_in_place` — passed
- `tests/test_models.py::test_schemas_user_role_is_the_canonical_enum` — passed
- `tests/test_models.py::test_tables_have_expected_columns` — passed
- `tests/test_models.py::test_user_role_enum_values` — passed

</details>

