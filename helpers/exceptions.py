from typing import Dict, List, Optional, Union

from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = (
        "We are unable to handle your request at this time. Please try again later."
    )

    def __init__(
        self,
        detail: Optional[Union[List, Dict, str]],
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.status_code = status_code
        message = detail if detail is not None else self.default_message
        if isinstance(detail, dict):
            self.detail = detail
        else:
            self.detail = {"message": force_str(message)}
