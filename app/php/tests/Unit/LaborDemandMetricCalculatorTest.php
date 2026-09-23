<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Services\LaborDemandMetricCalculator;
use PHPUnit\Framework\TestCase;

final class LaborDemandMetricCalculatorTest extends TestCase
{
    public function test_it_calculates_labor_demand_metrics(): void
    {
        $calculator = new LaborDemandMetricCalculator();

        $metrics = $calculator->calculate(
            currentWorkers: 341646,
            openings: 16408,
            unfilled: 2994,
            plannedHires: 11108,
        );

        $this->assertSame(
            18.25,
            $metrics->unfilledRate,
        );

        $this->assertSame(
            4.80,
            $metrics->openingIntensity,
        );

        $this->assertSame(
            3.25,
            $metrics->plannedHireRate,
        );
    }

    public function test_it_returns_null_when_denominator_is_zero(): void
    {
        $calculator = new LaborDemandMetricCalculator();

        $metrics = $calculator->calculate(
            currentWorkers: 0,
            openings: 0,
            unfilled: 0,
            plannedHires: 0,
        );

        $this->assertNull(
            $metrics->unfilledRate,
        );

        $this->assertNull(
            $metrics->openingIntensity,
        );

        $this->assertNull(
            $metrics->plannedHireRate,
        );
    }

    public function test_it_returns_null_when_source_value_is_missing(): void
    {
        $calculator = new LaborDemandMetricCalculator();

        $metrics = $calculator->calculate(
            currentWorkers: null,
            openings: 100,
            unfilled: 20,
            plannedHires: 10,
        );

        $this->assertSame(
            20.0,
            $metrics->unfilledRate,
        );

        $this->assertNull(
            $metrics->openingIntensity,
        );

        $this->assertNull(
            $metrics->plannedHireRate,
        );
    }
}