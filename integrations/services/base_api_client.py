
import requests


class BaseAPIClient:
    """Reusable client for communicating with external APIs."""

    def __init__(self, base_url, headers=None, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def _initiate_request(self, endpoint, payload=None, method="POST", params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=payload if method.upper() != "GET" else None,
                params=params if method.upper() == "GET" else None,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": data.get("ok", True),
                "data": data,
                "status_code": response.status_code,
            }

        except requests.exceptions.RequestException as exc:
            error_data = None
            status_code = None

            if exc.response is not None:
                status_code = exc.response.status_code

                try:
                    error_data = exc.response.json()
                except ValueError:
                    error_data = exc.response.text

            return {
                "success": False,
                "error": str(exc),
                "error_response": error_data,
                "status_code": status_code,
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }
