<?php

declare(strict_types=1);

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

final class LaborDemandQueryRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'region_code' => [
                'sometimes',
                'string',
                'max:50',
            ],

            'size_code' => [
                'sometimes',
                'string',
                'max:50',
            ],
        ];
    }
}