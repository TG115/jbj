CREATE TABLE data_source (
    data_source_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    source_code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,

    provider_name VARCHAR(255) NOT NULL,

    source_type VARCHAR(30) NOT NULL,

    source_url VARCHAR(500) NULL,

    license_name VARCHAR(255) NULL,
    license_url VARCHAR(500) NULL,

    update_cycle VARCHAR(100) NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_data_source_source_code
        UNIQUE (source_code),

    CONSTRAINT chk_data_source_source_type
        CHECK (
            source_type IN (
                'OFFICIAL_FILE',
                'API',
                'WEB',
                'MANUAL'
            )
        ),

    INDEX idx_data_source_provider_name (
        provider_name
    ),

    INDEX idx_data_source_is_active (
        is_active
    )
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;