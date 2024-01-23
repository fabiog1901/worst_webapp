from fastapi import APIRouter, Security, Body
from typing import Annotated, Any
import apiserver.dependencies as dep
import apiserver.service as svc
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

NAME = __name__.split(".", 2)[-1]

router = APIRouter(
    prefix="/search",
    tags=[NAME],
    dependencies=[Security(dep.get_current_user, scopes=["worst_read"])],
)


@router.post("")
async def execute_search(
    search_queries: Annotated[dict, Body()],
) -> dict | None:
    # {"queries":
    #   [
    #    {"indexUid":"worst",
    #     "q":"fa",
    #     "facets":[],
    #     "attributesToHighlight":["*"],"highlightPreTag":"__ais-highlight__",
    #     "highlightPostTag":"__/ais-highlight__","limit":21,"offset":0}
    #   ]
    # }
    
    print(search_queries)
    return {}
    return svc.execute_search(search_queries)

# rwq {"requests":[{"indexName":"worst",
#                   "params":{"attributes-to-snippet":["text"],"facets":[],"query":"","tagFilters":""}}
#                 ]
#     }
