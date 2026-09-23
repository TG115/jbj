<?php

declare(strict_types=1);

namespace Tests\Feature;

use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

final class OccupationLaborDemandTest extends TestCase
{
    use DatabaseTransactions;

    public function test_it_returns_labor_demand_for_occupation(): void
    {
        $context = $this->createOccupationContext();

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202601',
            currentWorkers: 341646,
            openings: 16408,
        );

        $response = $this->getJson(
            '/api/occupations/133/labor-demand'
        );

        $response
            ->assertOk()
            ->assertJsonPath(
                'data.occupation.code',
                '133',
            )
            ->assertJsonPath(
                'data.occupation.name',
                '소프트웨어 개발자',
            )
            ->assertJsonPath(
                'data.period.code',
                '202601',
            )
            ->assertJsonPath(
                'data.metrics.official.current_workers',
                341646,
            )
            ->assertJsonPath(
                'data.metrics.official.openings',
                16408,
            )
            ->assertJsonPath(
                'data.metrics.official.shortage_rate',
                3.2,
            )
            ->assertJsonPath(
                'data.metrics.derived.unfilled_rate',
                18.25,
            )
            ->assertJsonPath(
                'data.metrics.derived.opening_intensity',
                4.8,
            )
            ->assertJsonPath(
                'data.metrics.derived.planned_hire_rate',
                3.25,
            );
    }

    public function test_it_returns_latest_labor_demand(): void
    {
        $context = $this->createOccupationContext();

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202501',
            currentWorkers: 300000,
            openings: 12000,
        );

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202601',
            currentWorkers: 341646,
            openings: 16408,
        );

        $response = $this->getJson(
            '/api/occupations/133/labor-demand'
        );

        $response
            ->assertOk()
            ->assertJsonPath(
                'data.period.code',
                '202601',
            )
            ->assertJsonPath(
                'data.metrics.official.current_workers',
                341646,
            )
            ->assertJsonPath(
                'data.metrics.official.openings',
                16408,
            );
    }

    public function test_it_returns_404_when_labor_demand_does_not_exist(): void
    {
        $response = $this->getJson(
            '/api/occupations/999/labor-demand'
        );

        $response
            ->assertNotFound()
            ->assertJsonPath(
                'message',
                '노동수요 데이터를 찾을 수 없습니다.',
            );
    }

    public function test_it_returns_labor_demand_history(): void
    {
        $context = $this->createOccupationContext();

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202501',
            currentWorkers: 300000,
            openings: 12000,
        );

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202601',
            currentWorkers: 341646,
            openings: 16408,
        );

        $response = $this->getJson(
            '/api/occupations/133/labor-demand/history'
        );

        $response
            ->assertOk()
            ->assertJsonCount(2, 'data')
            ->assertJsonPath(
                'data.0.period.code',
                '202501',
            )
            ->assertJsonPath(
                'data.1.period.code',
                '202601',
            )
            ->assertJsonPath(
                'data.1.metrics.official.current_workers',
                341646,
            );
    }

    public function test_it_filters_labor_demand_by_region_and_size(): void
    {
        $context = $this->createOccupationContext();

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202601',
            currentWorkers: 341646,
            openings: 16408,
        );

        $this->insertLaborDemand(
            context: $context,
            periodCode: '202601',
            currentWorkers: 50000,
            openings: 5000,
            regionCode: 'TEST_REGION_01',
            regionName: '테스트 지역',
            sizeCode: 'TEST_SIZE_01',
            sizeName: '테스트 규모',
        );

        $response = $this->getJson(
            '/api/occupations/133/labor-demand'
            . '?region_code=TEST_REGION_01'
            . '&size_code=TEST_SIZE_01'
        );

        $response
            ->assertOk()
            ->assertJsonPath(
                'data.scope.region.code',
                'TEST_REGION_01',
            )
            ->assertJsonPath(
                'data.scope.region.name',
                '테스트 지역',
            )
            ->assertJsonPath(
                'data.scope.establishment_size.code',
                'TEST_SIZE_01',
            )
            ->assertJsonPath(
                'data.metrics.official.current_workers',
                50000,
            );
    }

    public function test_it_rejects_invalid_labor_demand_query(): void
    {
        $response = $this->getJson(
            '/api/occupations/133/labor-demand'
            . '?region_code='
            . str_repeat('A', 51)
        );

        $response
            ->assertUnprocessable()
            ->assertJsonValidationErrors([
                'region_code',
            ]);
    }

    /**
     * 테스트에 필요한 공통 기준 데이터를 만든다.
     *
     * @return array{
     *     occupation_node_id: int,
     *     data_source_id: int,
     *     etl_run_id: int
     * }
     */
    private function createOccupationContext(): array
    {
        $taxonomyId = DB::table(
            'occupation_taxonomy'
        )->insertGetId([
            'code' => 'KECO',
            'name' => '한국고용직업분류',
            'version' => '2025',
            'country_code' => 'KR',
        ]);

        $occupationNodeId = DB::table(
            'occupation_taxonomy_node'
        )->insertGetId([
            'occupation_taxonomy_id' => $taxonomyId,
            'code' => '133',
            'name_ko' => '소프트웨어 개발자',
            'level' => 3,
            'is_active' => true,
        ]);

        $dataSourceId = DB::table(
            'data_source'
        )->insertGetId([
            'source_code' => 'KOSIS_LABOR_DEMAND',
            'name' => 'KOSIS 노동수요 테스트',
            'provider_name' => '고용노동부',
            'source_type' => 'API',
            'update_cycle' => '반기',
            'is_active' => true,
        ]);

        $etlRunId = DB::table(
            'etl_run'
        )->insertGetId([
            'data_source_id' => $dataSourceId,
            'job_name' => 'test_labor_demand',
            'status_code' => 'SUCCESS',
            'processed_count' => 1,
            'finished_at' => now(),
        ]);

        return [
            'occupation_node_id' => $occupationNodeId,
            'data_source_id' => $dataSourceId,
            'etl_run_id' => $etlRunId,
        ];
    }

    /**
     * 노동수요 Fact 테스트 데이터를 만든다.
     *
     * @param array{
     *     occupation_node_id: int,
     *     data_source_id: int,
     *     etl_run_id: int
     * } $context
     */
    private function insertLaborDemand(
        array $context,
        string $periodCode,
        int $currentWorkers,
        int $openings,
        string $regionCode = '15118REG2012_00',
        string $regionName = '전국',
        string $sizeCode = '13102110322SIZES.00',
        string $sizeName = '전규모(1인이상)',
    ): void {
        $year = (int) substr(
            $periodCode,
            0,
            4,
        );

        $half = (int) substr(
            $periodCode,
            4,
            2,
        );

        DB::table(
            'fact_labor_demand'
        )->insert([
            'data_source_id' =>
                $context['data_source_id'],

            'etl_run_id' =>
                $context['etl_run_id'],

            'occupation_taxonomy_node_id' =>
                $context['occupation_node_id'],

            'period_code' => $periodCode,
            'reference_year' => $year,
            'reference_half' => $half,

            'region_member_code' => $regionCode,
            'region_name' => $regionName,

            'establishment_size_member_code' => $sizeCode,
            'establishment_size_name' => $sizeName,

            'source_occupation_member_code' => 'keco2026_133',
            'source_occupation_name' => '133 소프트웨어 개발자',

            'current_workers_count' => $currentWorkers,
            'openings_count' => $openings,

            'hires_count' => 13414,
            'unfilled_count' => 2994,
            'shortage_count' => 11293,
            'planned_hires_count' => 11108,
            'shortage_rate' => 3.2,
        ]);
    }
}