# Покрытие тестами

Обновить: `sh scripts/coverage_report.sh` из `backend/`. Тот же отчёт строит CI-задача `test-backend`.

## Требования

Покрыто требований: **33 из 35**. Отчёт генерирует `pytest --req-report=PATH` по маркерам `@pytest.mark.req`.


### Сценарии

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| S1 | Сценарий 1. Добавление питомца | 2 | ✅ покрыто |
| S2 | Сценарий 2. Ведение истории здоровья | 1 | ✅ покрыто |
| S3 | Сценарий 3. Учёт питания | 1 | ✅ покрыто |
| S4 | Сценарий 4. Контроль предстоящих процедур | 1 | ✅ покрыто |

### 5.1 Карточки питомцев

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.1.1 | Создание карточки питомца | 20 | ✅ покрыто |
| 5.1.2 | Имя, вид, порода и дата рождения | 7 | ✅ покрыто |
| 5.1.3 | Добавление фотографии | 19 | ✅ покрыто |
| 5.1.4 | Список питомцев пользователя | 3 | ✅ покрыто |

### 5.2 Карта здоровья

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.2.1 | История вакцинаций с датами | 6 | ✅ покрыто |
| 5.2.2 | История обработок от паразитов | 2 | ✅ покрыто |
| 5.2.3 | Записи о посещениях ветеринара | 3 | ✅ покрыто |
| 5.2.4 | Хранение заключений ветеринаров | 6 | ✅ покрыто |
| 5.2.5 | Учёт веса и других параметров | 21 | ✅ покрыто |

### 5.3 Учёт питания

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.3.1 | Записи о кормах | 8 | ✅ покрыто |
| 5.3.2 | Оценка «понравилось / не понравилось» | 4 | ✅ покрыто |
| 5.3.3 | Оценка «подошло / не подошло» | 6 | ✅ покрыто |
| 5.3.4 | Нежелательные реакции: ЖКТ, аллергия | 5 | ✅ покрыто |
| 5.3.5 | История питания и личная база предпочтений | 8 | ✅ покрыто |

### 5.4 Напоминания и назначения

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 5.4.1 | Расчёт даты следующей вакцинации | 18 | ✅ покрыто |
| 5.4.2 | Расчёт даты следующей обработки от паразитов | 8 | ✅ покрыто |
| 5.4.3 | Назначения препаратов из ветеринарных заключений | 0 | ⚪ нет тестов |
| 5.4.4 | Длительность и регулярность приёма препаратов | 0 | ⚪ нет тестов |
| 5.4.5 | Формирование напоминаний | 8 | ✅ покрыто |
| 5.4.6 | Список ближайших событий | 6 | ✅ покрыто |
| 5.4.7 | Уведомления через push или виджет | 16 | ✅ покрыто |

### 7–8 UX и ограничения

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| 7.1 | Понятные ошибки форм с указанием проблемного поля | 24 | ✅ покрыто |

### Дополнительные функции

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| P.REPORT | Экспорт истории питомца в PDF с графиками | 10 | ✅ покрыто |

### Платформа

| Id | Требование | Тестов | Статус |
|---|---|---|---|
| P.AUTH | Регистрация, вход, обновление токена, выход | 64 | ✅ покрыто |
| P.ACCESS | Изоляция данных пользователей и права ролей | 35 | ✅ покрыто |
| P.CATALOG | Справочник видов, пород и категорий | 18 | ✅ покрыто |
| P.TX | Транзакции: Unit of Work и откаты | 11 | ✅ покрыто |
| P.TIME | Единый формат времени (Unix seconds, UTC) | 27 | ✅ покрыто |
| P.OBS | Наблюдаемость: trace id, логи, метрики, health | 34 | ✅ покрыто |
| P.ARCH | Контракт API, схема БД, границы слоёв | 19 | ✅ покрыто |
| P.CHECK | Демо-данные жюри: разные питомцы и история | 3 | ✅ покрыто |

### Тесты по требованиям

<details><summary>S1 — Сценарий 1. Добавление питомца (2)</summary>

- `tests/scenarios/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_quick_form_highlights_the_missing_name` — passed

</details>

<details><summary>S2 — Сценарий 2. Ведение истории здоровья (1)</summary>

- `tests/scenarios/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>S3 — Сценарий 3. Учёт питания (1)</summary>

- `tests/scenarios/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>S4 — Сценарий 4. Контроль предстоящих процедур (1)</summary>

- `tests/scenarios/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.1.1 — Создание карточки питомца (20)</summary>

- `tests/api/test_pets_endpoints.py::test_avatar_generation_failure_and_unavailable` — passed
- `tests/api/test_pets_endpoints.py::test_blank_name_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_breed_is_required_and_must_exist` — passed
- `tests/api/test_pets_endpoints.py::test_create_minimal_pet` — passed
- `tests/api/test_pets_endpoints.py::test_delete_pet_removes_photo_and_avatar` — passed
- `tests/api/test_pets_endpoints.py::test_existing_nested_photo_keys_support_reads_generation_and_deletion` — passed
- `tests/api/test_pets_endpoints.py::test_future_birth_date_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_generate_avatar_requires_photo_then_keeps_photo_as_source` — passed
- `tests/api/test_pets_endpoints.py::test_list_returns_only_current_users_pets` — passed
- `tests/api/test_pets_endpoints.py::test_null_name_on_patch_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_other_users_pet_avatar_endpoints_are_not_found` — passed
- `tests/api/test_pets_endpoints.py::test_other_users_pet_is_not_found` — passed
- `tests/api/test_pets_endpoints.py::test_past_birth_date_returns_age_months` — passed
- `tests/api/test_pets_endpoints.py::test_patch_changes_breed_and_animal_and_clears_birth_date` — passed
- `tests/api/test_pets_endpoints.py::test_pet_keeps_living_after_its_breed_is_deleted` — passed
- `tests/api/test_pets_endpoints.py::test_photo_upload_wrong_type_and_too_large` — passed
- `tests/api/test_pets_endpoints.py::test_reupload_resets_generated_avatar_and_deletes_old_objects` — passed
- `tests/api/test_pets_endpoints.py::test_select_generated_avatar_and_reject_missing_one` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_quick_form_highlights_the_missing_name` — passed

</details>

<details><summary>5.1.2 — Имя, вид, порода и дата рождения (7)</summary>

- `tests/api/test_animals_breeds_endpoints.py::test_everyone_reads_seeded_animals_and_breeds` — passed
- `tests/api/test_pets_endpoints.py::test_breed_is_required_and_must_exist` — passed
- `tests/api/test_pets_endpoints.py::test_create_minimal_pet` — passed
- `tests/api/test_pets_endpoints.py::test_future_birth_date_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_past_birth_date_returns_age_months` — passed
- `tests/api/test_pets_endpoints.py::test_patch_changes_breed_and_animal_and_clears_birth_date` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed

</details>

<details><summary>5.1.3 — Добавление фотографии (19)</summary>

- `tests/api/test_pets_endpoints.py::test_avatar_generation_failure_and_unavailable` — passed
- `tests/api/test_pets_endpoints.py::test_delete_pet_removes_photo_and_avatar` — passed
- `tests/api/test_pets_endpoints.py::test_existing_nested_photo_keys_support_reads_generation_and_deletion` — passed
- `tests/api/test_pets_endpoints.py::test_generate_avatar_requires_photo_then_keeps_photo_as_source` — passed
- `tests/api/test_pets_endpoints.py::test_other_users_pet_avatar_endpoints_are_not_found` — passed
- `tests/api/test_pets_endpoints.py::test_photo_upload_wrong_type_and_too_large` — passed
- `tests/api/test_pets_endpoints.py::test_reupload_resets_generated_avatar_and_deletes_old_objects` — passed
- `tests/api/test_pets_endpoints.py::test_select_generated_avatar_and_reject_missing_one` — passed
- `tests/api/test_photo_direct_upload.py::test_confirm_rejects_missing_oversized_and_mismatched_objects` — passed
- `tests/api/test_photo_direct_upload.py::test_confirm_replaces_photo_and_rejects_foreign_or_avatar_keys` — passed
- `tests/api/test_photo_direct_upload.py::test_confirming_the_current_photo_key_is_idempotent` — passed
- `tests/api/test_photo_direct_upload.py::test_delete_generated_avatar_switches_the_source_back_to_the_photo` — passed
- `tests/api/test_photo_direct_upload.py::test_delete_photo_removes_both_objects_and_is_idempotent` — passed
- `tests/api/test_photo_direct_upload.py::test_direct_photo_endpoints_require_a_token` — passed
- `tests/api/test_photo_direct_upload.py::test_direct_upload_flow_can_skip_the_photo_and_then_use_it` — passed
- `tests/api/test_photo_direct_upload.py::test_upload_url_rejects_bad_input_and_a_foreign_pet` — passed
- `tests/api/test_photo_direct_upload.py::test_upload_url_returns_a_presigned_put` — passed
- `tests/infra/test_transactions.py::test_failed_photo_update_keeps_old_object_and_removes_new_object` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed

</details>

<details><summary>5.1.4 — Список питомцев пользователя (3)</summary>

- `tests/api/test_pets_endpoints.py::test_list_returns_only_current_users_pets` — passed
- `tests/report/test_pet_report.py::test_demo_history_reads_like_real_use` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed

</details>

<details><summary>5.2.1 — История вакцинаций с датами (6)</summary>

- `tests/api/test_events_endpoints.py::test_create_with_defaults_and_frontend_shape` — passed
- `tests/api/test_events_endpoints.py::test_deleting_pet_cascades_to_events` — passed
- `tests/api/test_events_endpoints.py::test_list_filters` — passed
- `tests/api/test_events_endpoints.py::test_update_validation_and_delete` — passed
- `tests/report/test_pet_report.py::test_report_is_a_downloadable_pdf` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.2 — История обработок от паразитов (2)</summary>

- `tests/api/test_events_endpoints.py::test_list_filters` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.3 — Записи о посещениях ветеринара (3)</summary>

- `tests/api/test_events_endpoints.py::test_list_filters` — passed
- `tests/api/test_events_endpoints.py::test_one_off_completion_has_no_next` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.4 — Хранение заключений ветеринаров (6)</summary>

- `tests/api/test_notes_endpoints.py::test_crud` — passed
- `tests/api/test_notes_endpoints.py::test_list_filters_by_pet_and_text_newest_first` — passed
- `tests/api/test_notes_endpoints.py::test_other_users_notes_are_invisible` — passed
- `tests/api/test_notes_endpoints.py::test_requires_auth` — passed
- `tests/api/test_notes_endpoints.py::test_validation_and_pet_cascade` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.2.5 — Учёт веса и других параметров (21)</summary>

- `tests/api/test_categories_endpoints.py::test_list_shows_system_first_then_own` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_state_patch_changes_only_the_given_fields` — passed
- `tests/api/test_states_endpoints.py::test_create_and_read_state` — passed
- `tests/api/test_states_endpoints.py::test_deleting_pet_cascades_to_states` — passed
- `tests/api/test_states_endpoints.py::test_foreign_pet_and_unknown_category` — passed
- `tests/api/test_states_endpoints.py::test_list_filters_and_isolation` — passed
- `tests/api/test_states_endpoints.py::test_summary_aggregates_by_kind[appetite-values2-3.0]` — passed
- `tests/api/test_states_endpoints.py::test_summary_aggregates_by_kind[food-values1-300.0]` — passed
- `tests/api/test_states_endpoints.py::test_summary_aggregates_by_kind[liked-values3-3.0]` — passed
- `tests/api/test_states_endpoints.py::test_summary_aggregates_by_kind[weight-values0-4300.0]` — passed
- `tests/api/test_states_endpoints.py::test_summary_with_period_and_empty` — passed
- `tests/api/test_states_endpoints.py::test_time_defaults_to_now` — passed
- `tests/api/test_states_endpoints.py::test_update_and_delete` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[appetite-0]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[appetite-6]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[liked--1]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[liked-2]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[weight--5]` — passed
- `tests/report/test_pet_report.py::test_measurements_and_food_become_series_and_verdicts` — passed
- `tests/report/test_pet_report.py::test_report_is_a_downloadable_pdf` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_2_owner_keeps_the_health_history` — passed

</details>

<details><summary>5.3.1 — Записи о кормах (8)</summary>

- `tests/api/test_foods_endpoints.py::test_crud` — passed
- `tests/api/test_foods_endpoints.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/api/test_foods_endpoints.py::test_list_filters` — passed
- `tests/api/test_foods_endpoints.py::test_other_users_food_is_invisible` — passed
- `tests/api/test_foods_endpoints.py::test_requires_auth` — passed
- `tests/api/test_foods_endpoints.py::test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food` — passed
- `tests/api/test_foods_endpoints.py::test_validation` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.2 — Оценка «понравилось / не понравилось» (4)</summary>

- `tests/api/test_foods_endpoints.py::test_crud` — passed
- `tests/api/test_foods_endpoints.py::test_list_filters` — passed
- `tests/report/test_pet_report.py::test_measurements_and_food_become_series_and_verdicts` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.3 — Оценка «подошло / не подошло» (6)</summary>

- `tests/api/test_foods_endpoints.py::test_crud` — passed
- `tests/api/test_foods_endpoints.py::test_list_filters` — passed
- `tests/report/test_pet_report.py::test_measurements_and_food_become_series_and_verdicts` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed
- `tests/unit/test_food_rules.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/unit/test_food_rules.py::test_suspects_ignore_case_and_spacing_and_keep_order` — passed

</details>

<details><summary>5.3.4 — Нежелательные реакции: ЖКТ, аллергия (5)</summary>

- `tests/api/test_categories_endpoints.py::test_list_shows_system_first_then_own` — passed
- `tests/api/test_foods_endpoints.py::test_crud` — passed
- `tests/api/test_foods_endpoints.py::test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food` — passed
- `tests/report/test_pet_report.py::test_measurements_and_food_become_series_and_verdicts` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed

</details>

<details><summary>5.3.5 — История питания и личная база предпочтений (8)</summary>

- `tests/api/test_foods_endpoints.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/api/test_foods_endpoints.py::test_list_filters` — passed
- `tests/api/test_foods_endpoints.py::test_suspects_are_ingredients_never_seen_in_earlier_tolerated_food` — passed
- `tests/report/test_pet_report.py::test_report_is_a_downloadable_pdf` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_3_owner_learns_which_food_suits_the_pet` — passed
- `tests/unit/test_food_rules.py::test_everything_is_suspect_without_tolerated_history` — passed
- `tests/unit/test_food_rules.py::test_normalize_trims_and_drops_blanks_and_case_insensitive_duplicates` — passed
- `tests/unit/test_food_rules.py::test_suspects_ignore_case_and_spacing_and_keep_order` — passed

</details>

<details><summary>5.4.1 — Расчёт даты следующей вакцинации (18)</summary>

- `tests/api/test_events_endpoints.py::test_complete_plans_next_occurrence` — passed
- `tests/api/test_events_endpoints.py::test_completion_date_cannot_be_in_the_future` — passed
- `tests/api/test_events_endpoints.py::test_late_completion_counts_from_done_date` — passed
- `tests/api/test_events_endpoints.py::test_next_schedule_is_calculated` — passed
- `tests/api/test_events_endpoints.py::test_patch_status_done_also_plans_next` — passed
- `tests/api/test_events_endpoints.py::test_recording_a_recent_done_event_plans_the_next_from_its_date` — passed
- `tests/api/test_events_endpoints.py::test_recording_old_history_does_not_plan_past_occurrences` — passed
- `tests/api/test_events_endpoints.py::test_reopening_and_completing_again_does_not_duplicate_the_next_event` — passed
- `tests/infra/test_transactions.py::test_failed_completion_rolls_back_both_events` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[daily-expected1]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[half_year-expected5]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[monthly-expected3]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[none-None]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[quarterly-expected4]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[weekly-expected2]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[yearly-expected6]` — passed
- `tests/report/test_pet_report.py::test_history_folds_into_procedures_and_monthly_activity` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.4.2 — Расчёт даты следующей обработки от паразитов (8)</summary>

- `tests/observability/test_users_and_observability.py::test_next_occurrence[daily-expected1]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[half_year-expected5]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[monthly-expected3]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[none-None]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[quarterly-expected4]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[weekly-expected2]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[yearly-expected6]` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.4.5 — Формирование напоминаний (8)</summary>

- `tests/api/test_events_endpoints.py::test_complete_plans_next_occurrence` — passed
- `tests/api/test_notifications_endpoints.py::test_create_defaults_to_event_schedule` — passed
- `tests/api/test_notifications_endpoints.py::test_delete_and_cascade_from_event` — passed
- `tests/api/test_notifications_endpoints.py::test_due_filter_and_mark_read` — passed
- `tests/api/test_notifications_endpoints.py::test_filter_by_event` — passed
- `tests/api/test_notifications_endpoints.py::test_invalid_values` — passed
- `tests/api/test_notifications_endpoints.py::test_isolation_and_unknown_event` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.4.6 — Список ближайших событий (6)</summary>

- `tests/api/test_events_endpoints.py::test_upcoming_includes_overdue_and_excludes_far_and_done` — passed
- `tests/api/test_notifications_endpoints.py::test_due_filter_and_mark_read` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_upcoming_can_be_narrowed_to_one_pet` — passed
- `tests/report/test_pet_report.py::test_demo_history_reads_like_real_use` — passed
- `tests/report/test_pet_report.py::test_history_folds_into_procedures_and_monthly_activity` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_4_owner_follows_upcoming_procedures` — passed

</details>

<details><summary>5.4.7 — Уведомления через push или виджет (16)</summary>

- `tests/infra/test_notification_channels.py::test_dispatcher_delivers_due_notification_once_and_leaves_status` — passed
- `tests/infra/test_notification_channels.py::test_dispatcher_waits_until_web_push_can_send` — passed
- `tests/infra/test_notification_channels.py::test_failed_subscription_does_not_block_the_other` — passed
- `tests/infra/test_notification_channels.py::test_revoked_subscriptions_stay_delivered` — passed
- `tests/infra/test_notification_channels.py::test_sender_drops_endpoint_outside_allowlist` — passed
- `tests/infra/test_notification_channels.py::test_settings_web_push_and_test_message` — passed
- `tests/infra/test_notification_channels.py::test_settings_when_web_push_is_not_configured` — passed
- `tests/infra/test_notification_channels.py::test_subscription_endpoint_is_https_and_allowlisted` — passed
- `tests/infra/test_notification_channels.py::test_total_push_failure_is_retried` — passed
- `tests/infra/test_notification_channels.py::test_unconfigured_web_push_does_not_claim` — passed
- `tests/infra/test_notification_channels.py::test_vapid_subject_must_be_mailto_or_https` — passed
- `tests/infra/test_notification_channels.py::test_web_push_keys_longer_than_255_are_rejected` — passed
- `tests/infra/test_notification_channels.py::test_web_push_sender_passes_timeout` — passed
- `tests/infra/test_notification_channels.py::test_web_push_sender_turns_410_into_gone` — passed
- `tests/infra/test_notification_channels.py::test_web_push_subscription_ownership` — passed
- `tests/infra/test_notification_channels.py::test_web_push_timeout_must_be_positive` — passed

</details>

<details><summary>7.1 — Понятные ошибки форм с указанием проблемного поля (24)</summary>

- `tests/api/test_animals_breeds_endpoints.py::test_catalog_validation_and_duplicates` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_names_differing_only_in_case_are_duplicates` — passed
- `tests/api/test_auth_endpoints.py::test_register_rejects_full_name_with_invalid_characters` — passed
- `tests/api/test_auth_endpoints.py::test_validation_error_message_is_english` — passed
- `tests/api/test_categories_endpoints.py::test_validation_errors` — passed
- `tests/api/test_events_endpoints.py::test_update_validation_and_delete` — passed
- `tests/api/test_foods_endpoints.py::test_validation` — passed
- `tests/api/test_notes_endpoints.py::test_validation_and_pet_cascade` — passed
- `tests/api/test_notifications_endpoints.py::test_invalid_values` — passed
- `tests/api/test_pets_endpoints.py::test_blank_name_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_breed_is_required_and_must_exist` — passed
- `tests/api/test_pets_endpoints.py::test_future_birth_date_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_null_name_on_patch_is_422` — passed
- `tests/api/test_pets_endpoints.py::test_photo_upload_wrong_type_and_too_large` — passed
- `tests/api/test_photo_direct_upload.py::test_upload_url_rejects_bad_input_and_a_foreign_pet` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[1234567890-at least one letter]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[onlyletters-at least one digit]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[short1-between 8 and 72]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[appetite-0]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[appetite-6]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[liked--1]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[liked-2]` — passed
- `tests/api/test_states_endpoints.py::test_value_must_fit_category_type[weight--5]` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_quick_form_highlights_the_missing_name` — passed

</details>

<details><summary>P.REPORT — Экспорт истории питомца в PDF с графиками (10)</summary>

- `tests/api/test_input_bounds.py::test_state_time_outside_date_range_is_rejected` — passed
- `tests/report/test_pet_report.py::test_demo_data_migration_seeds_every_jury_account_in_place` — passed
- `tests/report/test_pet_report.py::test_demo_history_reads_like_real_use` — passed
- `tests/report/test_pet_report.py::test_each_jury_account_gets_its_own_pets` — passed
- `tests/report/test_pet_report.py::test_empty_history_still_renders` — passed
- `tests/report/test_pet_report.py::test_history_folds_into_procedures_and_monthly_activity` — passed
- `tests/report/test_pet_report.py::test_measurements_and_food_become_series_and_verdicts` — passed
- `tests/report/test_pet_report.py::test_report_includes_the_pet_photo` — passed
- `tests/report/test_pet_report.py::test_report_is_a_downloadable_pdf` — passed
- `tests/report/test_pet_report.py::test_report_of_someone_elses_pet_is_not_found` — passed

</details>

<details><summary>P.AUTH — Регистрация, вход, обновление токена, выход (64)</summary>

- `tests/api/test_auth_endpoints.py::test_access_cookie_authenticates_without_authorization_header[login]` — passed
- `tests/api/test_auth_endpoints.py::test_access_cookie_authenticates_without_authorization_header[refresh]` — passed
- `tests/api/test_auth_endpoints.py::test_access_cookie_authenticates_without_authorization_header[register]` — passed
- `tests/api/test_auth_endpoints.py::test_access_token_body_field_is_deprecated_but_still_required[AccessTokenResponse]` — passed
- `tests/api/test_auth_endpoints.py::test_access_token_body_field_is_deprecated_but_still_required[UserAndAccessTokenResponse]` — passed
- `tests/api/test_auth_endpoints.py::test_bearer_authentication_still_works_without_cookies` — passed
- `tests/api/test_auth_endpoints.py::test_bearer_header_takes_precedence_over_access_cookie` — passed
- `tests/api/test_auth_endpoints.py::test_email_does_not_replace_login[login]` — passed
- `tests/api/test_auth_endpoints.py::test_email_does_not_replace_login[register]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_access_cookie_is_rejected` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_authorization_header_does_not_fall_back_to_cookie[Basic invalid]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_authorization_header_does_not_fall_back_to_cookie[Bearer ]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_authorization_header_does_not_fall_back_to_cookie[Bearer invalid]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_authorization_header_does_not_fall_back_to_cookie[]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_login_is_rejected[login-]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_login_is_rejected[login-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_login_is_rejected[register-]` — passed
- `tests/api/test_auth_endpoints.py::test_invalid_login_is_rejected[register-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]` — passed
- `tests/api/test_auth_endpoints.py::test_login_migration_renames_identifier_and_unique_constraint` — passed
- `tests/api/test_auth_endpoints.py::test_login_returns_200_and_sets_both_cookies` — passed
- `tests/api/test_auth_endpoints.py::test_login_with_wrong_password_returns_401` — passed
- `tests/api/test_auth_endpoints.py::test_logout_clears_both_cookies_and_revokes_refresh_token` — passed
- `tests/api/test_auth_endpoints.py::test_logout_without_cookie_returns_401` — passed
- `tests/api/test_auth_endpoints.py::test_refresh_rotates_cookie_and_invalidates_previous_refresh_token` — passed
- `tests/api/test_auth_endpoints.py::test_refresh_without_cookie_returns_401` — passed
- `tests/api/test_auth_endpoints.py::test_register_accepts_cyrillic_full_name` — passed
- `tests/api/test_auth_endpoints.py::test_register_accepts_full_name_with_yo` — passed
- `tests/api/test_auth_endpoints.py::test_register_rejects_duplicate_login` — passed
- `tests/api/test_auth_endpoints.py::test_register_rejects_full_name_with_invalid_characters` — passed
- `tests/api/test_auth_endpoints.py::test_register_returns_201_and_sets_cookie` — passed
- `tests/api/test_auth_endpoints.py::test_validation_error_message_is_english` — passed
- `tests/api/test_input_bounds.py::test_login_with_oversized_password_is_rejected` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_deactivated_user_cannot_log_in_refresh_or_use_tokens` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[1234567890-at least one letter]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[onlyletters-at least one digit]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_password_rules_point_at_the_password_field[short1-between 8 and 72]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_token_of_a_deleted_user_is_rejected` — passed
- `tests/observability/test_users_and_observability.py::test_me_returns_and_updates_profile` — passed
- `tests/scenarios/test_user_scenarios.py::test_scenario_1_owner_adds_a_pet_with_photo` — passed
- `tests/unit/test_auth_interactors.py::test_login_with_correct_credentials_returns_token_pair` — passed
- `tests/unit/test_auth_interactors.py::test_login_with_unknown_login_raises` — passed
- `tests/unit/test_auth_interactors.py::test_login_with_wrong_password_raises` — passed
- `tests/unit/test_auth_interactors.py::test_logout_deletes_refresh_token_and_is_idempotent` — passed
- `tests/unit/test_auth_interactors.py::test_refresh_rotates_token_and_invalidates_old_one` — passed
- `tests/unit/test_auth_interactors.py::test_refresh_with_unknown_token_raises` — passed
- `tests/unit/test_auth_interactors.py::test_register_creates_user_and_returns_token_pair` — passed
- `tests/unit/test_auth_interactors.py::test_register_rejects_duplicate_login` — passed
- `tests/unit/test_auth_interactors.py::test_verify_access_token_returns_current_user_data` — passed
- `tests/unit/test_cookies.py::test_access_cookie_attributes_and_expiration[False]` — passed
- `tests/unit/test_cookies.py::test_access_cookie_attributes_and_expiration[True]` — passed
- `tests/unit/test_cookies.py::test_delete_refresh_cookie_expires_it` — passed
- `tests/unit/test_cookies.py::test_set_refresh_cookie_sets_expected_attributes` — passed
- `tests/unit/test_duration.py::test_parses_days` — passed
- `tests/unit/test_duration.py::test_parses_minutes` — passed
- `tests/unit/test_duration.py::test_parses_seconds_and_hours` — passed
- `tests/unit/test_duration.py::test_rejects_bad_format` — passed
- `tests/unit/test_jwt_service.py::test_access_token_has_expected_claims` — passed
- `tests/unit/test_jwt_service.py::test_decode_token_accepts_matching_type` — passed
- `tests/unit/test_jwt_service.py::test_decode_token_rejects_garbage` — passed
- `tests/unit/test_jwt_service.py::test_decode_token_rejects_wrong_type` — passed
- `tests/unit/test_jwt_service.py::test_expire_seconds_come_from_env_vars` — passed
- `tests/unit/test_jwt_service.py::test_hash_token_is_deterministic_sha256` — passed
- `tests/unit/test_jwt_service.py::test_password_hash_roundtrip` — passed
- `tests/unit/test_jwt_service.py::test_refresh_token_has_refresh_type` — passed

</details>

<details><summary>P.ACCESS — Изоляция данных пользователей и права ролей (35)</summary>

- `tests/api/test_animals_breeds_endpoints.py::test_only_admin_writes_the_catalog` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_requires_auth` — passed
- `tests/api/test_categories_endpoints.py::test_admin_changes_any_category` — passed
- `tests/api/test_categories_endpoints.py::test_categories_are_shared_but_only_the_author_changes_them` — passed
- `tests/api/test_categories_endpoints.py::test_requires_auth` — passed
- `tests/api/test_categories_endpoints.py::test_system_category_is_read_only` — passed
- `tests/api/test_events_endpoints.py::test_isolation_and_unknown_pet` — passed
- `tests/api/test_foods_endpoints.py::test_other_users_food_is_invisible` — passed
- `tests/api/test_foods_endpoints.py::test_requires_auth` — passed
- `tests/api/test_notes_endpoints.py::test_other_users_notes_are_invisible` — passed
- `tests/api/test_notes_endpoints.py::test_requires_auth` — passed
- `tests/api/test_notifications_endpoints.py::test_isolation_and_unknown_event` — passed
- `tests/api/test_pets_endpoints.py::test_list_returns_only_current_users_pets` — passed
- `tests/api/test_pets_endpoints.py::test_other_users_pet_avatar_endpoints_are_not_found` — passed
- `tests/api/test_pets_endpoints.py::test_other_users_pet_is_not_found` — passed
- `tests/api/test_photo_direct_upload.py::test_delete_photo_removes_both_objects_and_is_idempotent` — passed
- `tests/api/test_photo_direct_upload.py::test_direct_photo_endpoints_require_a_token` — passed
- `tests/api/test_photo_direct_upload.py::test_upload_url_rejects_bad_input_and_a_foreign_pet` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/animals-animals]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/breeds-breeds]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/categories-categories]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events-events]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events/upcoming-events]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/foods-food]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notes-notes]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notifications-notifications]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/pets-pets]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/states-states]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/users/me-users]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_deactivated_user_cannot_log_in_refresh_or_use_tokens` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_upcoming_can_be_narrowed_to_one_pet` — passed
- `tests/api/test_states_endpoints.py::test_foreign_pet_and_unknown_category` — passed
- `tests/api/test_states_endpoints.py::test_list_filters_and_isolation` — passed
- `tests/report/test_pet_report.py::test_report_of_someone_elses_pet_is_not_found` — passed
- `tests/scenarios/test_user_scenarios.py::test_another_owner_sees_nothing_of_barsik` — passed

</details>

<details><summary>P.CATALOG — Справочник видов, пород и категорий (18)</summary>

- `tests/api/test_animals_breeds_endpoints.py::test_admin_manages_animals_and_breeds` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_breed_search_by_name` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_catalog_validation_and_duplicates` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_everyone_reads_seeded_animals_and_breeds` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_names_differing_only_in_case_are_duplicates` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_only_admin_writes_the_catalog` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_requires_auth` — passed
- `tests/api/test_animals_breeds_endpoints.py::test_search_treats_like_wildcards_literally` — passed
- `tests/api/test_categories_endpoints.py::test_admin_changes_any_category` — passed
- `tests/api/test_categories_endpoints.py::test_categories_are_shared_but_only_the_author_changes_them` — passed
- `tests/api/test_categories_endpoints.py::test_category_used_by_others_keeps_its_meaning` — passed
- `tests/api/test_categories_endpoints.py::test_filters_by_type_and_name` — passed
- `tests/api/test_categories_endpoints.py::test_list_shows_system_first_then_own` — passed
- `tests/api/test_categories_endpoints.py::test_requires_auth` — passed
- `tests/api/test_categories_endpoints.py::test_system_category_is_read_only` — passed
- `tests/api/test_categories_endpoints.py::test_update_and_delete_own` — passed
- `tests/api/test_categories_endpoints.py::test_validation_errors` — passed
- `tests/api/test_pets_endpoints.py::test_pet_keeps_living_after_its_breed_is_deleted` — passed

</details>

<details><summary>P.TX — Транзакции: Unit of Work и откаты (11)</summary>

- `tests/infra/test_transactions.py::test_authentication_gateway_and_uow_share_one_session` — passed
- `tests/infra/test_transactions.py::test_commit_time_duplicate_login_keeps_the_existing_error_contract` — passed
- `tests/infra/test_transactions.py::test_failed_avatar_update_keeps_the_existing_photo_and_avatar` — passed
- `tests/infra/test_transactions.py::test_failed_completion_rolls_back_both_events` — passed
- `tests/infra/test_transactions.py::test_failed_photo_update_keeps_old_object_and_removes_new_object` — passed
- `tests/infra/test_transactions.py::test_failed_registration_rolls_back_user_and_token` — passed
- `tests/infra/test_transactions.py::test_failed_rotation_preserves_original_refresh_token` — passed
- `tests/infra/test_transactions.py::test_read_only_request_never_commits` — passed
- `tests/infra/test_unit_of_work.py::test_add_query_tracked_update_and_delete` — passed
- `tests/infra/test_unit_of_work.py::test_failed_commit_rolls_back_the_entire_write` — passed
- `tests/infra/test_unit_of_work.py::test_uncommitted_changes_are_discarded` — passed

</details>

<details><summary>P.TIME — Единый формат времени (Unix seconds, UTC) (27)</summary>

- `tests/api/test_input_bounds.py::test_notification_time_outside_date_range_is_rejected` — passed
- `tests/api/test_input_bounds.py::test_state_time_outside_date_range_is_rejected` — passed
- `tests/architecture/test_timestamps.py::test_all_persistent_instant_columns_are_numeric` — passed
- `tests/architecture/test_timestamps.py::test_birth_timestamp_normalizes_to_utc_midnight` — passed
- `tests/architecture/test_timestamps.py::test_calendar_recurrence_preserves_fractional_seconds_and_clamps_leap_days` — passed
- `tests/architecture/test_timestamps.py::test_documented_timestamp_fields_are_numbers` — passed
- `tests/architecture/test_timestamps.py::test_fractional_timestamp_roundtrip_and_epoch_zero` — passed
- `tests/architecture/test_timestamps.py::test_iso_dates_are_rejected_and_error_timestamps_are_numeric` — passed
- `tests/architecture/test_timestamps.py::test_nonfinite_body_timestamps_return_validation_errors[-Infinity]` — passed
- `tests/architecture/test_timestamps.py::test_nonfinite_body_timestamps_return_validation_errors[Infinity]` — passed
- `tests/architecture/test_timestamps.py::test_nonfinite_body_timestamps_return_validation_errors[NaN]` — passed
- `tests/architecture/test_timestamps.py::test_nonfinite_query_timestamps_return_validation_errors[-Infinity]` — passed
- `tests/architecture/test_timestamps.py::test_nonfinite_query_timestamps_return_validation_errors[Infinity]` — passed
- `tests/architecture/test_timestamps.py::test_nonfinite_query_timestamps_return_validation_errors[NaN]` — passed
- `tests/architecture/test_timestamps.py::test_timestamp_migration_has_explicit_utc_and_reversible_conversions` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete--1e+100]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete--62135596801.0]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete-1e+100]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[complete-253402300800.0]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create--1e+100]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create--62135596801.0]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create-1e+100]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[create-253402300800.0]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update--1e+100]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update--62135596801.0]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update-1e+100]` — passed
- `tests/architecture/test_timestamps.py::test_unsupported_event_timestamps_return_422_without_writes[update-253402300800.0]` — passed

</details>

<details><summary>P.OBS — Наблюдаемость: trace id, логи, метрики, health (34)</summary>

- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/animals-animals]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/breeds-breeds]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/categories-categories]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events-events]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/events/upcoming-events]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/foods-food]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notes-notes]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/notifications-notifications]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/pets-pets]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/states-states]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_database_outage_returns_uniform_500[/api/v1/users/me-users]` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_readiness_reports_ready_database` — passed
- `tests/api/test_resilience_and_edge_cases.py::test_readiness_reports_unavailable_database` — passed
- `tests/observability/test_app_boot.py::test_app_imports_and_liveness_responds` — passed
- `tests/observability/test_app_boot.py::test_app_uses_injected_configs_for_title_cors_cookies_and_jwt` — passed
- `tests/observability/test_app_boot.py::test_avatar_provider_uses_injected_config` — passed
- `tests/observability/test_app_boot.py::test_database_is_lazy_uses_injected_config_and_closes_with_container` — passed
- `tests/observability/test_app_boot.py::test_user_role_has_no_typo` — passed
- `tests/observability/test_trace_id.py::test_cors_allows_configured_origin` — passed
- `tests/observability/test_trace_id.py::test_cors_rejects_unconfigured_origin` — passed
- `tests/observability/test_trace_id.py::test_error_response_trace_id_matches_request_header` — passed
- `tests/observability/test_trace_id.py::test_response_always_includes_trace_id_header` — passed
- `tests/observability/test_trace_id.py::test_trace_id_header_is_echoed_back_when_provided` — passed
- `tests/observability/test_users_and_observability.py::test_me_returns_and_updates_profile` — passed
- `tests/observability/test_users_and_observability.py::test_metrics_endpoint_exposes_request_and_domain_counters` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[daily-expected1]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[half_year-expected5]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[monthly-expected3]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[none-None]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[quarterly-expected4]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[weekly-expected2]` — passed
- `tests/observability/test_users_and_observability.py::test_next_occurrence[yearly-expected6]` — passed
- `tests/observability/test_users_and_observability.py::test_trace_id_is_echoed_and_used_in_errors` — passed
- `tests/observability/test_users_and_observability.py::test_validation_error_with_non_uuid_trace_id` — passed

</details>

<details><summary>P.ARCH — Контракт API, схема БД, границы слоёв (19)</summary>

- `tests/api/test_input_bounds.py::test_food_weight_beyond_int32_is_rejected` — passed
- `tests/api/test_input_bounds.py::test_huge_page_is_rejected` — passed
- `tests/api/test_input_bounds.py::test_search_with_nul_is_rejected` — passed
- `tests/api/test_input_bounds.py::test_state_value_beyond_int32_is_rejected` — passed
- `tests/api/test_input_bounds.py::test_text_with_nul_is_rejected[/api/v1/foods-body1]` — passed
- `tests/api/test_input_bounds.py::test_text_with_nul_is_rejected[/api/v1/notes-body0]` — passed
- `tests/architecture/test_architecture_and_contract.py::test_inner_layers_do_not_import_frameworks_or_outer_layers` — passed
- `tests/architecture/test_architecture_and_contract.py::test_openapi_matches_the_documented_api_contract` — passed
- `tests/architecture/test_architecture_and_contract.py::test_postgres_schema_matches_documented_tables_and_indexes` — passed
- `tests/architecture/test_models.py::test_alembic_revision_chain_has_a_single_head` — passed
- `tests/architecture/test_models.py::test_avatar_source_enum_values` — passed
- `tests/architecture/test_models.py::test_category_id_migration_renames_column_constraint_and_index_in_place` — passed
- `tests/architecture/test_models.py::test_notification_delivery_migration_adds_channel_storage_and_reverts` — passed
- `tests/architecture/test_models.py::test_pet_avatar_migration_converts_legacy_photo_url_and_reverts` — passed
- `tests/architecture/test_models.py::test_schemas_user_role_is_the_canonical_enum` — passed
- `tests/architecture/test_models.py::test_seed_admin_migration_creates_admin_and_owns_seeded_catalog` — passed
- `tests/architecture/test_models.py::test_tables_have_expected_columns` — passed
- `tests/architecture/test_models.py::test_user_role_enum_values` — passed
- `tests/report/test_pet_report.py::test_demo_data_migration_seeds_every_jury_account_in_place` — passed

</details>

<details><summary>P.CHECK — Демо-данные жюри: разные питомцы и история (3)</summary>

- `tests/report/test_pet_report.py::test_demo_data_migration_seeds_every_jury_account_in_place` — passed
- `tests/report/test_pet_report.py::test_demo_history_reads_like_real_use` — passed
- `tests/report/test_pet_report.py::test_each_jury_account_gets_its_own_pets` — passed

</details>


## Код

Строки и ветвления по модулям; файлы со 100 % покрытием не показаны.

| Name                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/app/application/animals/interactors.py              |       64 |        0 |        6 |        1 |     99% |   68-\>71 |
| src/app/application/auth/interactors.py                 |      105 |        2 |       16 |        0 |     98% |     88-89 |
| src/app/application/breeds/interactors.py               |       80 |        0 |       12 |        1 |     99% |  95-\>100 |
| src/app/application/categories/interactors.py           |       75 |        0 |       12 |        1 |     99% | 100-\>102 |
| src/app/application/foods/interactors.py                |       69 |        0 |        8 |        2 |     97% |104-\>106, 106-\>108 |
| src/app/application/notes/interactors.py                |       57 |        0 |        6 |        1 |     98% |   71-\>73 |
| src/app/application/notifications/delivery.py           |      110 |        5 |       36 |        8 |     91% |36, 64, 72, 114-\>112, 123, 126-\>128, 129, 163-\>165 |
| src/app/application/notifications/interactors.py        |       68 |        3 |        6 |        1 |     95% |   109-111 |
| src/app/application/notifications/settings.py           |       74 |        1 |       20 |        4 |     95% |26-\>28, 31-\>33, 45, 49-\>54 |
| src/app/application/pets/interactors.py                 |      233 |        2 |       54 |        5 |     98% |59, 84-\>86, 179-\>181, 202, 273-\>275 |
| src/app/application/reports/builder.py                  |       99 |        0 |       36 |        3 |     98% |105-\>104, 117-\>108, 119-\>108 |
| src/app/application/reports/interactors.py              |       44 |        0 |        6 |        1 |     98% |   43-\>41 |
| src/app/application/states/interactors.py               |       94 |        0 |       16 |        1 |     99% | 117-\>119 |
| src/app/application/users/interactors.py                |       30 |        2 |        4 |        2 |     88% |    35, 43 |
| src/app/infra/avatars/spirit.py                         |       67 |       10 |       14 |        3 |     84% |73-74, 92-94, 106-\>112, 117-119, 121-122 |
| src/app/infra/database/db\_helper.py                    |        8 |        3 |        0 |        0 |     62% | 19-26, 35 |
| src/app/infra/database/unit\_of\_work.py                |       21 |        2 |        0 |        0 |     90% |     18-19 |
| src/app/infra/di.py                                     |       40 |        3 |        0 |        0 |     92% |30, 54, 58 |
| src/app/infra/gateways/animal.py                        |       44 |        6 |        2 |        0 |     87% |20-21, 28-29, 46-47 |
| src/app/infra/gateways/breed.py                         |       47 |        6 |        4 |        0 |     88% |21-22, 29-30, 49-50 |
| src/app/infra/gateways/category.py                      |       40 |        4 |        4 |        0 |     91% |21-22, 40-41 |
| src/app/infra/gateways/event.py                         |       75 |        6 |       14 |        1 |     92% |21-\>23, 26-27, 72-73, 92-93 |
| src/app/infra/gateways/food.py                          |       56 |        6 |        8 |        1 |     89% |20-\>22, 25-26, 68-69, 81-82 |
| src/app/infra/gateways/note.py                          |       47 |        4 |        6 |        1 |     91% |20-\>22, 25-26, 46-47 |
| src/app/infra/gateways/notification.py                  |       80 |       11 |       10 |        2 |     86% |25-\>27, 30-31, 77-78, 94-95, 109-110, 133-134, 157 |
| src/app/infra/gateways/notification\_settings.py        |       17 |        2 |        0 |        0 |     88% |     20-21 |
| src/app/infra/gateways/pet.py                           |       45 |        7 |        4 |        2 |     82% |21-\>23, 26-27, 31, 36-37, 59-60 |
| src/app/infra/gateways/refresh\_token.py                |       31 |       10 |        0 |        0 |     68% |17-22, 29-30, 36-37 |
| src/app/infra/gateways/state.py                         |       79 |        8 |       16 |        1 |     91% |29-\>31, 34-35, 77-78, 105-106, 118-119 |
| src/app/infra/gateways/user.py                          |       24 |        2 |        0 |        0 |     92% |     28-29 |
| src/app/infra/gateways/web\_push\_subscription.py       |       24 |        4 |        0 |        0 |     83% |24-25, 32-33 |
| src/app/infra/logger.py                                 |       32 |        4 |        6 |        1 |     87% |14-15, 19-20 |
| src/app/infra/notifications/worker.py                   |       63 |       42 |       20 |        1 |     27% |20, 35-43, 52-74, 80-86, 94-96 |
| src/app/infra/photos/provision.py                       |       48 |       48 |       10 |        0 |      0% |      3-78 |
| src/app/infra/reports/pdf.py                            |      334 |        3 |       74 |        6 |     98% |115, 124-\>126, 167-\>169, 329, 382, 430-\>439 |
| src/app/infra/security/jwt\_service.py                  |       45 |        0 |        4 |        1 |     98% |   26-\>28 |
| src/app/infra/singleton.py                              |        6 |        6 |        2 |        0 |      0% |       1-7 |
| src/app/infra/webpush/sender.py                         |       53 |       11 |       16 |        4 |     75% |25-27, 34, 60-64, 69, 77 |
| src/app/main.py                                         |       50 |        2 |        6 |        2 |     93% |    34, 36 |
| src/app/presentation/http/api/v1/endpoints/events.py    |       74 |        1 |       12 |        2 |     97% |45, 169-\>171 |
| src/app/presentation/http/api/v1/exceptions/handlers.py |       45 |        2 |        6 |        2 |     92% |30-\>35, 38-39 |
| src/app/presentation/http/calendar.py                   |       52 |        3 |       18 |        1 |     91% |   104-106 |
| src/app/presentation/http/loc2field.py                  |       24 |        1 |       12 |        2 |     92% | 6-\>8, 12 |
| src/app/presentation/http/middleware/observability.py   |       36 |        1 |        6 |        1 |     95% |        23 |
| src/app/presentation/http/paginated.py                  |       20 |        5 |        2 |        0 |     68% |10, 14, 25-28 |
| src/app/presentation/http/schemas/base.py               |       30 |        3 |        8 |        3 |     84% |21, 24, 31 |
| src/app/presentation/http/schemas/notification.py       |       76 |        2 |        8 |        2 |     95% |    67, 80 |
| src/app/presentation/http/schemas/pet.py                |       78 |        3 |       10 |        1 |     95% | 32, 48-49 |
| **TOTAL**                                               | **5567** |  **246** |  **640** |   **71** | **94%** |           |

187 files skipped due to complete coverage.
