INSERT INTO data_source (
    source_code,
    name,
    provider_name,
    source_type,
    source_url,
    update_cycle,
    is_active
)
VALUES
(
    'KSCO8',
    '제8차 한국표준직업분류',
    '국가데이터처',
    'OFFICIAL_FILE',
    'https://mods.go.kr/board.es?act=view&bid=107&list_no=431582&mid=a10403040000',
    '비정기',
    TRUE
),
(
    'KECO2025',
    '한국고용직업분류 2025',
    '한국고용정보원',
    'OFFICIAL_FILE',
    'https://www.keis.or.kr/keis/ko/proj/114/pblc/detail.do?categoryIdx=125&pubIdx=11172',
    '비정기',
    TRUE
),
(
    'KOSIS_LABOR_DEMAND',
    '직종별·규모별(2026년 이후) / DT_118N_DEN062',
    '고용노동부',
    'API',
    'https://kosis.kr/openapi/Param/statisticsParameterData.do',
    '반기',
    TRUE
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    provider_name = VALUES(provider_name),
    source_type = VALUES(source_type),
    source_url = VALUES(source_url),
    update_cycle = VALUES(update_cycle),
    is_active = VALUES(is_active),
    updated_at = CURRENT_TIMESTAMP;