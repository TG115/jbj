CREATE TABLE occupation_taxonomy (
    occupation_taxonomy_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    code VARCHAR(32) NOT NULL,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(32) NOT NULL,

    country_code CHAR(2) NOT NULL DEFAULT 'KR',

    valid_from DATE NULL,
    valid_to DATE NULL,

    source_url VARCHAR(500) NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_occupation_taxonomy_code_version
        UNIQUE (code, version, country_code)
);

CREATE TABLE occupation_taxonomy_node (
    occupation_taxonomy_node_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    occupation_taxonomy_id BIGINT UNSIGNED NOT NULL,

    code VARCHAR(32) NOT NULL,
    name_ko VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NULL,

    level TINYINT UNSIGNED NOT NULL,

    parent_occupation_taxonomy_node_id BIGINT UNSIGNED NULL,

    description TEXT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_occupation_taxonomy_node_taxonomy
        FOREIGN KEY (occupation_taxonomy_id)
        REFERENCES occupation_taxonomy(occupation_taxonomy_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_occupation_taxonomy_node_parent
        FOREIGN KEY (parent_occupation_taxonomy_node_id)
        REFERENCES occupation_taxonomy_node(occupation_taxonomy_node_id)
        ON DELETE SET NULL,

    CONSTRAINT uq_occupation_taxonomy_node_code
        UNIQUE (occupation_taxonomy_id, code),

    INDEX idx_occupation_taxonomy_node_taxonomy
        (occupation_taxonomy_id),

    INDEX idx_occupation_taxonomy_node_parent
        (parent_occupation_taxonomy_node_id),

    INDEX idx_occupation_taxonomy_node_level
        (level)
);

