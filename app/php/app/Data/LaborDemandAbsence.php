<?php

declare(strict_types=1);

namespace App\Data;

final readonly class LaborDemandAbsence
{
    public const CODE_NOT_FOUND = 'not_found';

    public const CODE_SOURCE_UNAVAILABLE = 'source_unavailable';

    public function __construct(
        public string $code,
        public string $message,
    ) {
    }
}
