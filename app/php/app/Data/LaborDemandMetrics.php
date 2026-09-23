<?php

declare(strict_types=1);

namespace App\Data;

final readonly class LaborDemandMetrics
{
    public function __construct(
        public ?float $unfilledRate,
        public ?float $openingIntensity,
        public ?float $plannedHireRate,
    ) {
    }
}