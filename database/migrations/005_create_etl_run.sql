CREATE TABLE etl_run (
    etl_run_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    data_source_id BIGINT UNSIGNED NOT NULL,

    job_name VARCHAR(150) NOT NULL,

    status_code VARCHAR(20) NOT NULL,

    source_file_name VARCHAR(255) NULL,

    source_checksum_sha256 CHAR(64) NULL,

    parameters_json JSON NULL,

    processed_count BIGINT UNSIGNED NOT NULL
        DEFAULT 0,

    inserted_count BIGINT UNSIGNED NOT NULL
        DEFAULT 0,

    updated_count BIGINT UNSIGNED NOT NULL
        DEFAULT 0,

    rejected_count BIGINT UNSIGNED NOT NULL
        DEFAULT 0,

    error_message TEXT NULL,

    started_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    finished_at TIMESTAMP NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_etl_run_data_source
        FOREIGN KEY (data_source_id)
        REFERENCES data_source(data_source_id),

    CONSTRAINT chk_etl_run_status_code
        CHECK (
            status_code IN (
                'RUNNING',
                'SUCCESS',
                'FAILED'
            )
        ),

    INDEX idx_etl_run_data_source (
        data_source_id
    ),

    INDEX idx_etl_run_status_started_at (
        status_code,
        started_at
    ),

    INDEX idx_etl_run_source_started_at (
        data_source_id,
        started_at
    )
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;