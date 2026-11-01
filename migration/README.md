# Stage 1 migration records

Produced by `scripts/migrate.py` from the legacy `polities.csv`, `phases.csv` and `rulers.csv` on `main`, and checked by `scripts/verify_migration.py`. See session report S06.

- `legacy_crosswalk.csv`: every legacy row → its v2 ID (`legacy_row` is the line number in the legacy file, header = 1).
- `issues.csv`: changes made during migration and items left for review.
- `title_roles_review.csv`: ruler role assigned to each title, by rule or by default.

These files are historical records. Do not edit them; corrections go into `data/`.
