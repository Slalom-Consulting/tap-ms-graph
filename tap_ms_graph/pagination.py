from singer_sdk.pagination import BaseAPIPaginator
from typing import Optional, Any
from requests import Response


class MSGraphPaginator(BaseAPIPaginator):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(None, *args, **kwargs)

    def get_next(self, response: Response) -> Optional[str]:
        return response.json().get('@odata.nextLink')
