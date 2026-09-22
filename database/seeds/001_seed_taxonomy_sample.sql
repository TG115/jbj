SET NAMES utf8mb4;

INSERT INTO occupation_taxonomy (
    code,
    name,
    version,
    country_code
) VALUES (
    'KSCO',
    '한국표준직업분류',
    '8',
    'KR'
);

SET @ksco8_id = LAST_INSERT_ID();


INSERT INTO occupation_taxonomy_node (
    occupation_taxonomy_id,
    code,
    name_ko,
    level,
    parent_occupation_taxonomy_node_id
) VALUES (
    @ksco8_id,
    '2',
    '전문가 및 관련 종사자',
    1,
    NULL
);

SET @ksco8_level1_id = LAST_INSERT_ID();


INSERT INTO occupation_taxonomy_node (
    occupation_taxonomy_id,
    code,
    name_ko,
    level,
    parent_occupation_taxonomy_node_id
) VALUES (
    @ksco8_id,
    '22',
    '정보 통신 전문가 및 기술직',
    2,
    @ksco8_level1_id
);

SET @ksco8_level2_id = LAST_INSERT_ID();


INSERT INTO occupation_taxonomy_node (
    occupation_taxonomy_id,
    code,
    name_ko,
    level,
    parent_occupation_taxonomy_node_id
) VALUES (
    @ksco8_id,
    '222',
    '컴퓨터 시스템 및 소프트웨어 전문가',
    3,
    @ksco8_level2_id
);


-- KECO 2025
INSERT INTO occupation_taxonomy (
    code,
    name,
    version,
    country_code
) VALUES (
    'KECO',
    '한국고용직업분류',
    '2025',
    'KR'
);

SET @keco2025_id = LAST_INSERT_ID();


-- 대분류
INSERT INTO occupation_taxonomy_node (
    occupation_taxonomy_id,
    code,
    name_ko,
    level,
    parent_occupation_taxonomy_node_id
) VALUES (
    @keco2025_id,
    '1',
    '연구직 및 공학 기술직',
    1,
    NULL
);

SET @keco2025_level1_id = LAST_INSERT_ID();


-- 중분류
INSERT INTO occupation_taxonomy_node (
    occupation_taxonomy_id,
    code,
    name_ko,
    level,
    parent_occupation_taxonomy_node_id
) VALUES (
    @keco2025_id,
    '13',
    '정보통신 연구개발직 및 공학 기술직',
    2,
    @keco2025_level1_id
);

SET @keco2025_level2_id = LAST_INSERT_ID();


-- 소분류
INSERT INTO occupation_taxonomy_node (
    occupation_taxonomy_id,
    code,
    name_ko,
    level,
    parent_occupation_taxonomy_node_id
) VALUES (
    @keco2025_id,
    '133',
    '소프트웨어 개발자',
    3,
    @keco2025_level2_id
);