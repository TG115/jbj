<?php

declare(strict_types=1);

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

final class OccupationLaborDemandResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'occupation' => [
                'code' => $this->resource->occupationCode,
                'name' => $this->resource->occupationName,
            ],

            'period' => [
                'code' => $this->resource->periodCode,
                'year' => $this->resource->referenceYear,
                'half' => $this->resource->referenceHalf,
            ],

            'scope' => [
                'region' => [
                    'code' => $this->resource->regionCode,
                    'name' => $this->resource->regionName,
                ],

                'establishment_size' => [
                    'code' => $this->resource->sizeCode,
                    'name' => $this->resource->sizeName,
                ],
            ],

            'metrics' => [
                'official' => [
                    'current_workers' => $this->resource->currentWorkers,
                    'openings' => $this->resource->openings,
                    'hires' => $this->resource->hires,
                    'unfilled' => $this->resource->unfilled,
                    'shortage' => $this->resource->shortage,
                    'planned_hires' => $this->resource->plannedHires,
                    'shortage_rate' => $this->resource->shortageRate,
                ],

                'derived' => [
                    'unfilled_rate' => $this->resource->derivedMetrics->unfilledRate,
                    'opening_intensity' => $this->resource->derivedMetrics->openingIntensity,
                    'planned_hire_rate' =>$this->resource->derivedMetrics->plannedHireRate,
                ],
            ],
        ];
    }
}