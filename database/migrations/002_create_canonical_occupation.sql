CREATE TABLE canonical_occupation (
    canonical_occupation_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    slug VARCHAR(100) NOT NULL,

    name_ko VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NULL,

    description TEXT NULL,

    is_public BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_canonical_occupation_slug
        UNIQUE (slug),

    INDEX idx_canonical_occupation_name_ko (name_ko),
    INDEX idx_canonical_occupation_is_public (is_public)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;