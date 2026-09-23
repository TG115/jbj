<?php

declare(strict_types=1);

namespace App\Services;

use App\Data\LaborDemandMetrics;

final class LaborDemandMetricCalculator
{
    public function calculate(
        ?int $currentWorkers,
        ?int $openings,
        ?int $unfilled,
        ?int $plannedHires,
    ): LaborDemandMetrics {
        return new LaborDemandMetrics(
            unfilledRate: $this->percentage(
                numerator: $unfilled,
                denominator: $openings,
            ),
            openingIntensity: $this->percentage(
                numerator: $openings,
                denominator: $currentWorkers,
            ),
            plannedHireRate: $this->percentage(
                numerator: $plannedHires,
                denominator: $currentWorkers,
            ),
        );
    }

    private function percentage(
        ?int $numerator,
        ?int $denominator,
    ): ?float {
        if (
            $numerator === null
            || $denominator === null
            || $denominator === 0
        ) {
            return null;
        }

        return round(
            ($numerator / $denominator) * 100,
            2,
        );
    }
}