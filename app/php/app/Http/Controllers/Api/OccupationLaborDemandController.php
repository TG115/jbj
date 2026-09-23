<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\OccupationLaborDemandResource;
use App\Services\OccupationLaborDemandService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

final class OccupationLaborDemandController extends Controller
{
    public function __construct(
        private readonly OccupationLaborDemandService $service,
    ) {
    }

    public function show(
        string $occupationCode,
    ): OccupationLaborDemandResource|JsonResponse {
        $snapshot = $this->service->findLatest(
            $occupationCode,
        );

        if ($snapshot === null) {
            return response()->json(
                [
                    'message' => '노동수요 데이터를 찾을 수 없습니다.',
                ],
                404,
            );
        }

        return new OccupationLaborDemandResource(
            $snapshot,
        );
    }

    public function history(
        string $occupationCode,
    ): AnonymousResourceCollection {
        $snapshots = $this->service->findHistory(
            $occupationCode,
        );

        return OccupationLaborDemandResource::collection(
            $snapshots,
        );
    }
}