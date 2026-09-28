<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\OccupationLaborDemandResource;
use App\Services\OccupationLaborDemandService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;
use App\Http\Requests\LaborDemandQueryRequest;

final class OccupationLaborDemandController extends Controller
{
    public function __construct(
        private readonly OccupationLaborDemandService $service,
    ) {
    }

    public function show(
        LaborDemandQueryRequest $request,
        string $occupationCode,
    ): OccupationLaborDemandResource|JsonResponse {
        $validated = $request->validated();

        $snapshot = $this->service->findLatest(
            occupationCode: $occupationCode,
            regionCode: $validated['region_code'] ?? null,
            sizeCode: $validated['size_code'] ?? null,
        );

        if ($snapshot === null) {
            $absence = $this->service->resolveAbsence(
                occupationCode: $occupationCode,
                regionCode: $validated['region_code'] ?? null,
                sizeCode: $validated['size_code'] ?? null,
            );

            return response()->json(
                [
                    'message' => $absence->message,
                    'code' => $absence->code,
                ],
                404,
            );
        }

        return new OccupationLaborDemandResource(
            $snapshot,
        );
    }

    public function history(
        LaborDemandQueryRequest $request,
        string $occupationCode,
    ): AnonymousResourceCollection {
        $validated = $request->validated();

        $snapshots = $this->service->findHistory(
            occupationCode: $occupationCode,
            regionCode: $validated['region_code'] ?? null,
            sizeCode: $validated['size_code'] ?? null,
        );

        return OccupationLaborDemandResource::collection(
            $snapshots,
        );
    }
}