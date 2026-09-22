<?php

declare(strict_types=1);

use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\OccupationLaborDemandController;

Route::get('/health', function (): JsonResponse {
    try {
        DB::selectOne('SELECT 1');

        $database = 'connected';
        $statusCode = 200;
    } catch (\Throwable) {
        $database = 'disconnected';
        $statusCode = 503;
    }

    return response()->json(
        [
            'service' => 'jbj-api',
            'status' => $database === 'connected'
                ? 'ok'
                : 'error',
            'database' => $database,
        ],
        $statusCode,
    );
});

Route::get(
    '/occupations/{occupationCode}/labor-demand',
    [
        OccupationLaborDemandController::class,
        'show',
    ],
)->where(
    'occupationCode',
    '\d{1,3}',
);