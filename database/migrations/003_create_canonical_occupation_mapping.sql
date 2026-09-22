CREATE TABLE canonical_occupation_mapping (
    canonical_occupation_mapping_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    canonical_occupation_id BIGINT UNSIGNED NOT NULL,
    occupation_taxonomy_node_id BIGINT UNSIGNED NOT NULL,

    usage_code VARCHAR(32) NOT NULL,

    mapping_type VARCHAR(20) NOT NULL,
    mapping_source VARCHAR(20) NOT NULL,

    confidence DECIMAL(5,4) NULL,

    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    note VARCHAR(500) NULL,

    verified_at TIMESTAMP NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_canonical_occupation_mapping_canonical
        FOREIGN KEY (canonical_occupation_id)
        REFERENCES canonical_occupation(canonical_occupation_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_canonical_occupation_mapping_taxonomy_node
        FOREIGN KEY (occupation_taxonomy_node_id)
        REFERENCES occupation_taxonomy_node(occupation_taxonomy_node_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_canonical_occupation_mapping_usage
        UNIQUE (
            canonical_occupation_id,
            occupation_taxonomy_node_id,
            usage_code
        ),

    CONSTRAINT chk_canonical_occupation_mapping_type
        CHECK (
            mapping_type IN (
                'EXACT',
                'BROADER',
                'NARROWER',
                'RELATED',
                'PARTIAL'
            )
        ),

    CONSTRAINT chk_canonical_occupation_mapping_source
        CHECK (
            mapping_source IN (
                'OFFICIAL',
                'MANUAL',
                'INFERRED'
            )
        ),

    CONSTRAINT chk_canonical_occupation_mapping_confidence
        CHECK (
            confidence IS NULL
            OR (confidence >= 0 AND confidence <= 1)
        ),

    INDEX idx_canonical_occupation_mapping_canonical
        (canonical_occupation_id),

    INDEX idx_canonical_occupation_mapping_taxonomy_node
        (occupation_taxonomy_node_id),

    INDEX idx_canonical_occupation_mapping_usage
        (usage_code)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;