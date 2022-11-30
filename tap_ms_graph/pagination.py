from singer_sdk.pagination import BaseAPIPaginator
from typing import Optional, Any
from requests import Response

NEXT_LINK_KEY = '@odata.nextLink'

class MSGraphPaginator(BaseAPIPaginator):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(None, *args, **kwargs)

    def get_next(self, response: Response) -> Optional[str]:
        return response.json().get(NEXT_LINK_KEY)
