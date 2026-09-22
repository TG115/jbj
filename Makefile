.PHONY: up down ps build \
        migrate seed \
        normalize-ksco8 normalize-keco2025 \
        import-ksco8 import-keco2025 \
        etl-status \
				migrate migrate-status migrate-baseline

up:
	docker compose up -d

down:
	docker compose down

ps:
	docker compose ps

build:
	docker compose build

normalize-ksco8:
	docker compose exec python \
		python -m jbj_etl.cli.normalize_ksco8 \
		/data/raw/ksco8/ksco8_items.hwpx \
		/data/processed/taxonomies/ksco8.csv

normalize-keco2025:
	docker compose exec python \
		python -m jbj_etl.cli.normalize_keco2025 \
		/data/raw/keco2025/keco2025_table.pdf \
		/data/processed/taxonomies/keco2025.csv

import-ksco8:
	docker compose exec python \
		python -m jbj_etl.cli.import_taxonomy \
		--code KSCO \
		--version 8 \
		--name "한국표준직업분류" \
		--file /data/processed/taxonomies/ksco8.csv \
		--source-code KSCO8 \
		--source-file /data/raw/ksco8/ksco8_items.hwpx

import-keco2025:
	docker compose exec python \
		python -m jbj_etl.cli.import_taxonomy \
		--code KECO \
		--version 2025 \
		--name "한국고용직업분류" \
		--file /data/processed/taxonomies/keco2025.csv \
		--source-code KECO2025 \
		--source-file /data/raw/keco2025/keco2025_table.pdf

etl-status:
	docker compose exec mysql \
		sh -c 'mysql --default-character-set=utf8mb4 \
		-u"$$MYSQL_USER" -p"$$MYSQL_PASSWORD" "$$MYSQL_DATABASE" \
		-e "\
		SELECT \
			r.etl_run_id, \
			s.source_code, \
			r.job_name, \
			r.status_code, \
			r.processed_count, \
			r.started_at, \
			r.finished_at \
		FROM etl_run r \
		JOIN data_source s \
		  ON s.data_source_id = r.data_source_id \
		ORDER BY r.etl_run_id DESC \
		LIMIT 20;"'

migrate:
	docker compose exec python \
		python -m jbj_etl.cli.migrate \
		up /database/migrations

migrate-status:
	docker compose exec python \
		python -m jbj_etl.cli.migrate \
		status /database/migrations

migrate-baseline:
	docker compose exec python \
		python -m jbj_etl.cli.migrate \
		baseline /database/migrations \
		--through 5