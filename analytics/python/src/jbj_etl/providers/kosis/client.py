from __future__ import annotations

from typing import Any

import requests

from jbj_etl.config import (
    get_kosis_config,
)


class KosisClient:
    META_URL = (
        "https://kosis.kr/openapi/"
        "statisticsData.do"
    )

    PARAM_DATA_URL = (
        "https://kosis.kr/openapi/Param/"
        "statisticsParameterData.do"
    )

    def __init__(self) -> None:
        config = get_kosis_config()

        self.api_key = config.api_key

        self.session = requests.Session()

    def _get(
        self,
        url: str,
        params: dict[str, Any],
    ) -> Any:

        response = self.session.get(
            url,
            params={
                "apiKey": self.api_key,
                "format": "json",
                "jsonVD": "Y",
                **params,
            },
            timeout=30,
        )

        response.raise_for_status()

        try:
            payload = response.json()

        except requests.exceptions.JSONDecodeError as exc:
            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            preview = response.text[:500]

            raise RuntimeError(
                "KOSIS 응답을 JSON으로 해석하지 못했습니다.\n"
                f"Content-Type: {content_type}\n"
                f"Response preview: {preview}"
            ) from exc

        self._raise_api_error(
            payload
        )

        return payload

    @staticmethod
    def _raise_api_error(
        payload: Any,
    ) -> None:

        rows = (
            payload
            if isinstance(payload, list)
            else [payload]
        )

        for row in rows:
            if not isinstance(row, dict):
                continue

            error_code = (
                row.get("ERR")
                or row.get("err")
                or row.get("ERROR")
                or row.get("errorCode")
            )

            if error_code:
                raise RuntimeError(
                    "KOSIS API error: "
                    f"{row}"
                )

    def get_table(
        self,
        *,
        org_id: str,
        table_id: str,
    ) -> Any:

        return self._get(
            self.META_URL,
            {
                "method": "getMeta",
                "type": "TBL",
                "orgId": org_id,
                "tblId": table_id,
            }
        )

    def get_items(
        self,
        *,
        org_id: str,
        table_id: str,
    ) -> Any:

        return self._get(
            self.META_URL,
            {
                "method": "getMeta",
                "type": "ITM",
                "orgId": org_id,
                "tblId": table_id,
            }
        )

    def get_periods(
        self,
        *,
        org_id: str,
        table_id: str,
    ) -> Any:

        return self._get(
            self.META_URL,
            {
                "method": "getMeta",
                "type": "PRD",
                "orgId": org_id,
                "tblId": table_id,
                "detail": "Y",
            }
        )

    def get_parameter_data(
        self,
        *,
        org_id: str,
        table_id: str,
        obj_l1: str,
        obj_l2: str,
        obj_l3: str,
        item_id: str,
        period_type: str,
        start_period: str,
        end_period: str,
    ) -> Any:

        return self._get(
            self.PARAM_DATA_URL,
            {
                "method": "getList",
                "orgId": org_id,
                "tblId": table_id,
                "objL1": obj_l1,
                "objL2": obj_l2,
                "objL3": obj_l3,
                "itmId": item_id,
                "prdSe": period_type,
                "startPrdDe": start_period,
                "endPrdDe": end_period,
            },
        )