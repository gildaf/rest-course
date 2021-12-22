# PEP 585
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException, Request, Response

from . import bdb_manager
from .params import BDBParams, BDBResponse
from .types import UID

app = FastAPI()


@app.post("/bdbs", operation_id="create_bdb", response_model=BDBResponse)
def create_bdb(req: BDBParams, request: Request, response: Response) -> BDBResponse:
    bdb = bdb_manager.create_bdb(req)

    # TODO: Add fields: created_at
    url = request.url_for("get_bdb", uid=str(bdb.uid))
    response.headers["location"] = url
    return BDBResponse(bdb=bdb, url=url)


@app.get("/bdbs/{uid}", operation_id="get_bdb", response_model=BDBResponse)
def get_bdb(uid: UID, request: Request) -> BDBResponse:
    try:
        bdb = bdb_manager.get_bdb(uid)
        url = request.url_for("get_bdb", uid=str(bdb.uid))
        return BDBResponse(bdb=bdb, url=url)
    except LookupError:
        raise HTTPException(status_code=404)


@app.get("/bdbs", operation_id="get_all_bdbs", response_model=Iterable[BDBResponse])
def get_all_bdbs(request: Request) -> Iterable[BDBResponse]:
    for bdb in bdb_manager.get_all_bdbs():
        url = request.url_for("get_bdb", uid=str(bdb.uid))
        yield BDBResponse(bdb=bdb, url=url)
