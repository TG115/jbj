CREATE TABLE fact_labor_demand (
    fact_labor_demand_id BIGINT UNSIGNED
        AUTO_INCREMENT PRIMARY KEY,

    data_source_id BIGINT UNSIGNED NOT NULL,
    etl_run_id BIGINT UNSIGNED NOT NULL,

    occupation_taxonomy_node_id
        BIGINT UNSIGNED NOT NULL,

    period_code CHAR(6) NOT NULL,
    reference_year SMALLINT UNSIGNED NOT NULL,
    reference_half TINYINT UNSIGNED NOT NULL,

    region_member_code VARCHAR(100) NOT NULL,
    region_name VARCHAR(255) NOT NULL,

    establishment_size_member_code
        VARCHAR(100) NOT NULL,

    establishment_size_name
        VARCHAR(255) NOT NULL,

    source_occupation_member_code
        VARCHAR(100) NOT NULL,

    source_occupation_name
        VARCHAR(255) NOT NULL,

    current_workers_count BIGINT UNSIGNED NULL,
    openings_count BIGINT UNSIGNED NULL,
    hires_count BIGINT UNSIGNED NULL,
    unfilled_count BIGINT UNSIGNED NULL,
    shortage_count BIGINT UNSIGNED NULL,
    planned_hires_count BIGINT UNSIGNED NULL,

    shortage_rate DECIMAL(7, 3) NULL,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_labor_demand_data_source
        FOREIGN KEY (data_source_id)
        REFERENCES data_source(data_source_id),

    CONSTRAINT fk_fact_labor_demand_etl_run
        FOREIGN KEY (etl_run_id)
        REFERENCES etl_run(etl_run_id),

    CONSTRAINT fk_fact_labor_demand_occupation
        FOREIGN KEY (occupation_taxonomy_node_id)
        REFERENCES occupation_taxonomy_node(
            occupation_taxonomy_node_id
        ),

    CONSTRAINT uq_fact_labor_demand_grain
        UNIQUE (
            data_source_id,
            period_code,
            region_member_code,
            establishment_size_member_code,
            occupation_taxonomy_node_id
        ),

    CONSTRAINT chk_fact_labor_demand_half
        CHECK (
            reference_half IN (1, 2)
        ),

    CONSTRAINT chk_fact_labor_demand_shortage_rate
        CHECK (
            shortage_rate IS NULL
            OR (
                shortage_rate >= 0
                AND shortage_rate <= 100
            )
        ),

    INDEX idx_fact_labor_demand_occupation_period (
        occupation_taxonomy_node_id,
        period_code
    ),

    INDEX idx_fact_labor_demand_region_period (
        region_member_code,
        period_code
    ),

    INDEX idx_fact_labor_demand_size_period (
        establishment_size_member_code,
        period_code
    )
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;