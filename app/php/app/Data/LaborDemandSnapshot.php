<?php

declare(strict_types=1);

namespace App\Data;

final readonly class LaborDemandSnapshot
{
    public function __construct(
        public string $occupationCode,
        public string $occupationName,

        public string $periodCode,
        public int $referenceYear,
        public int $referenceHalf,

        public string $regionCode,
        public string $regionName,

        public string $sizeCode,
        public string $sizeName,

        public ?int $currentWorkers,
        public ?int $openings,
        public ?int $hires,
        public ?int $unfilled,
        public ?int $shortage,
        public ?int $plannedHires,
        public ?float $shortageRate,

        public LaborDemandMetrics $derivedMetrics,
    ) {
    }
}