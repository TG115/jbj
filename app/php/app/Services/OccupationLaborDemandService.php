<?php

declare(strict_types=1);

namespace App\Services;

use App\Data\LaborDemandAbsence;
use App\Data\LaborDemandSnapshot;
use Illuminate\Support\Facades\DB;

final class OccupationLaborDemandService
{
    public function __construct(
        private readonly LaborDemandMetricCalculator $metricCalculator,
    ) {
    }

    private const NATIONWIDE_REGION_CODE = '15118REG2012_00';

    private const ALL_SIZE_CODE = '13102110322SIZES.00';

    public function findLatest(
        string $occupationCode,
        ?string $regionCode = null,
        ?string $sizeCode = null,
    ): ?LaborDemandSnapshot {
        $regionCode = $regionCode ?? self::NATIONWIDE_REGION_CODE;
        $sizeCode = $sizeCode ?? self::ALL_SIZE_CODE;

        $row = DB::table('fact_labor_demand as f')
            ->join(
                'occupation_taxonomy_node as n',
                'n.occupation_taxonomy_node_id',
                '=',
                'f.occupation_taxonomy_node_id',
            )
            ->join(
                'occupation_taxonomy as t',
                't.occupation_taxonomy_id',
                '=',
                'n.occupation_taxonomy_id',
            )
            ->join(
                'data_source as s',
                's.data_source_id',
                '=',
                'f.data_source_id',
            )
            ->where('t.code', 'KECO')
            ->where('t.version', '2025')
            ->where('n.code', $occupationCode)
            ->where(
                's.source_code',
                'KOSIS_LABOR_DEMAND',
            )
            ->where(
                'f.region_member_code',
                $regionCode,
            )
            ->where(
                'f.establishment_size_member_code',
                $sizeCode,
            )
            ->orderByDesc('f.period_code')
            ->select([
                'n.code as occupation_code',
                'n.name_ko as occupation_name',

                'f.period_code',
                'f.reference_year',
                'f.reference_half',

                'f.region_member_code',
                'f.region_name',

                'f.establishment_size_member_code',
                'f.establishment_size_name',

                'f.current_workers_count',
                'f.openings_count',
                'f.hires_count',
                'f.unfilled_count',
                'f.shortage_count',
                'f.planned_hires_count',
                'f.shortage_rate',
            ])
            ->first();

        if ($row === null) {
            return null;
        }

        return $this->toSnapshot($row);
    }

    /**
     * Exact grain 행이 없을 때 missing≠0 이유를 구분한다.
     *
     * - not_found: 직종 미존재, 또는 비교 가능한 다른 grain fact도 없음
     * - source_unavailable: 동일 직종의 다른 grain(예: 전국×동일 규모) fact는 있으나
     *   요청한 region×size 조합에는 원천/적재 행이 없음
     */
    public function resolveAbsence(
        string $occupationCode,
        ?string $regionCode = null,
        ?string $sizeCode = null,
    ): LaborDemandAbsence {
        $regionCode = $regionCode ?? self::NATIONWIDE_REGION_CODE;
        $sizeCode = $sizeCode ?? self::ALL_SIZE_CODE;

        if (! $this->occupationExists($occupationCode)) {
            return new LaborDemandAbsence(
                code: LaborDemandAbsence::CODE_NOT_FOUND,
                message: '노동수요 데이터를 찾을 수 없습니다.',
            );
        }

        if ($this->hasOtherGrainFact(
            occupationCode: $occupationCode,
            regionCode: $regionCode,
            sizeCode: $sizeCode,
        )) {
            return new LaborDemandAbsence(
                code: LaborDemandAbsence::CODE_SOURCE_UNAVAILABLE,
                message: '요청한 지역·규모 조합의 노동수요 원천 데이터가 없습니다.',
            );
        }

        return new LaborDemandAbsence(
            code: LaborDemandAbsence::CODE_NOT_FOUND,
            message: '노동수요 데이터를 찾을 수 없습니다.',
        );
    }

    private function occupationExists(
        string $occupationCode,
    ): bool {
        return DB::table('occupation_taxonomy_node as n')
            ->join(
                'occupation_taxonomy as t',
                't.occupation_taxonomy_id',
                '=',
                'n.occupation_taxonomy_id',
            )
            ->where('t.code', 'KECO')
            ->where('t.version', '2025')
            ->where('n.code', $occupationCode)
            ->exists();
    }

    /**
     * 요청 grain이 아닌 다른 region(동일 size)에 해당 직종 fact가 있는지.
     * 전형적 예: 전국 L3는 있고 시도 L3는 없는 KOSIS 지역 grain 공백.
     */
    private function hasOtherGrainFact(
        string $occupationCode,
        string $regionCode,
        string $sizeCode,
    ): bool {
        return DB::table('fact_labor_demand as f')
            ->join(
                'occupation_taxonomy_node as n',
                'n.occupation_taxonomy_node_id',
                '=',
                'f.occupation_taxonomy_node_id',
            )
            ->join(
                'occupation_taxonomy as t',
                't.occupation_taxonomy_id',
                '=',
                'n.occupation_taxonomy_id',
            )
            ->join(
                'data_source as s',
                's.data_source_id',
                '=',
                'f.data_source_id',
            )
            ->where('t.code', 'KECO')
            ->where('t.version', '2025')
            ->where('n.code', $occupationCode)
            ->where(
                's.source_code',
                'KOSIS_LABOR_DEMAND',
            )
            ->where(
                'f.establishment_size_member_code',
                $sizeCode,
            )
            ->where(
                'f.region_member_code',
                '!=',
                $regionCode,
            )
            ->exists();
    }

    /**
     * @return list<LaborDemandSnapshot>
     */
    public function findHistory(
        string $occupationCode,
        ?string $regionCode = null,
        ?string $sizeCode = null,
    ): array {
        $regionCode = $regionCode ?? self::NATIONWIDE_REGION_CODE;
        $sizeCode = $sizeCode ?? self::ALL_SIZE_CODE;

        $rows = DB::table('fact_labor_demand as f')
            ->join(
                'occupation_taxonomy_node as n',
                'n.occupation_taxonomy_node_id',
                '=',
                'f.occupation_taxonomy_node_id',
            )
            ->join(
                'occupation_taxonomy as t',
                't.occupation_taxonomy_id',
                '=',
                'n.occupation_taxonomy_id',
            )
            ->join(
                'data_source as ds',
                'ds.data_source_id',
                '=',
                'f.data_source_id',
            )
            ->where('t.code', 'KECO')
            ->where('t.version', '2025')
            ->where('n.code', $occupationCode)
            ->where(
                'ds.source_code',
                'KOSIS_LABOR_DEMAND',
            )
            ->where(
                'f.region_member_code',
                $regionCode,
            )
            ->where(
                'f.establishment_size_member_code',
                $sizeCode,
            )
            ->orderBy('f.period_code')
            ->select([
                'n.code as occupation_code',
                'n.name_ko as occupation_name',

                'f.period_code',
                'f.reference_year',
                'f.reference_half',

                'f.region_member_code',
                'f.region_name',

                'f.establishment_size_member_code',
                'f.establishment_size_name',

                'f.current_workers_count',
                'f.openings_count',
                'f.hires_count',
                'f.unfilled_count',
                'f.shortage_count',
                'f.planned_hires_count',
                'f.shortage_rate',
            ])
            ->get();

        $history = [];

        foreach ($rows as $row) {
            $history[] = $this->toSnapshot($row);
        }

        return $history;
    }

    private function toSnapshot(
        object $row,
    ): LaborDemandSnapshot {
        $currentWorkers =
            $row->current_workers_count !== null
                ? (int) $row->current_workers_count
                : null;

        $openings =
            $row->openings_count !== null
                ? (int) $row->openings_count
                : null;

        $hires =
            $row->hires_count !== null
                ? (int) $row->hires_count
                : null;

        $unfilled =
            $row->unfilled_count !== null
                ? (int) $row->unfilled_count
                : null;

        $shortage =
            $row->shortage_count !== null
                ? (int) $row->shortage_count
                : null;

        $plannedHires =
            $row->planned_hires_count !== null
                ? (int) $row->planned_hires_count
                : null;

        $shortageRate =
            $row->shortage_rate !== null
                ? (float) $row->shortage_rate
                : null;

        $derivedMetrics =
            $this->metricCalculator->calculate(
                currentWorkers: $currentWorkers,
                openings: $openings,
                unfilled: $unfilled,
                plannedHires: $plannedHires,
            );

        return new LaborDemandSnapshot(
            occupationCode:
                $row->occupation_code,

            occupationName:
                $row->occupation_name,

            periodCode:
                $row->period_code,

            referenceYear:
                (int) $row->reference_year,

            referenceHalf:
                (int) $row->reference_half,

            regionCode:
                (string) $row->region_member_code,
            
            regionName:
                (string) $row->region_name,
            
            sizeCode:
                (string) $row->establishment_size_member_code,
            
            sizeName:
                (string) $row->establishment_size_name,

            currentWorkers:
                $currentWorkers,

            openings:
                $openings,

            hires:
                $hires,

            unfilled:
                $unfilled,

            shortage:
                $shortage,

            plannedHires:
                $plannedHires,

            shortageRate:
                $shortageRate,

            derivedMetrics:
                $derivedMetrics,
        );
    }
}