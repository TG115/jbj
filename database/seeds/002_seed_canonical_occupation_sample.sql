SET NAMES utf8mb4;

INSERT INTO canonical_occupation (
    slug,
    name_ko,
    name_en,
    description,
    is_public
) VALUES (
    'software-developer',
    '소프트웨어 개발자',
    'Software Developer',
    '소프트웨어를 설계, 개발, 테스트하고 유지보수하는 직업',
    FALSE
);

SET @software_developer_id = LAST_INSERT_ID();


-- KSCO8 222
-- 고용 통계용
INSERT INTO canonical_occupation_mapping (
    canonical_occupation_id,
    occupation_taxonomy_node_id,
    usage_code,
    mapping_type,
    mapping_source,
    is_primary,
    note
)
SELECT
    @software_developer_id,
    n.occupation_taxonomy_node_id,
    'EMPLOYMENT',
    'BROADER',
    'MANUAL',
    TRUE,
    'KSCO8 222는 소프트웨어 개발자보다 넓은 분류이므로 BROADER'
FROM occupation_taxonomy_node n
JOIN occupation_taxonomy t
    ON t.occupation_taxonomy_id = n.occupation_taxonomy_id
WHERE t.code = 'KSCO'
  AND t.version = '8'
  AND n.code = '222';


-- KECO2025 133
-- 노동수요 통계용
INSERT INTO canonical_occupation_mapping (
    canonical_occupation_id,
    occupation_taxonomy_node_id,
    usage_code,
    mapping_type,
    mapping_source,
    is_primary,
    note
)
SELECT
    @software_developer_id,
    n.occupation_taxonomy_node_id,
    'DEMAND',
    'EXACT',
    'MANUAL',
    TRUE,
    'KECO2025 133 소프트웨어 개발자'
FROM occupation_taxonomy_node n
JOIN occupation_taxonomy t
    ON t.occupation_taxonomy_id = n.occupation_taxonomy_id
WHERE t.code = 'KECO'
  AND t.version = '2025'
  AND n.code = '133';