# PEP 585
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException, status, Response

from .params import BDBParams
from .types import BDB, UID
from . import dal

app = FastAPI(title="REST Course", description="REST API Course")


@app.post(
    "/bdbs",
    tags=["bdb"],
    operation_id="create_bdb",
    status_code=status.HTTP_201_CREATED,
    response_model=BDB,
)
def create_bdb(req: BDBParams):
    bdb_last_uid = dal.get_next_id()
    uid = UID(bdb_last_uid)

    bdb = BDB(
        uid=uid,
        name=req.name,
        type=req.type,
        memory_size=req.memory_size,
    )
    dal.save_bdb(bdb)
    return bdb


@app.get("/bdbs/{uid}", tags=["bdb"], operation_id="get_bdb", response_model=BDB)
def get_bdb(uid: UID):
    bdb = dal.load_bdb(uid)
    if bdb is None:
        raise HTTPException(status_code=404)
    return bdb


@app.get(
    "/bdbs",
    tags=["bdb"],
    operation_id="get_all_bdbs",
    response_model=Iterable[BDB],
)
def get_all_bdbs():
    for uid in dal.bdb_keys():
        bdb = dal.load_bdb(UID(uid))
        yield bdb



@app.delete("/bdbs/{uid}", tags=["bdb"], operation_id="delete_bdb",
    status_code=status.HTTP_204_NO_CONTENT)
def delete_bdb(uid: UID):
    try:
        dal.delete_bdb(uid)
    except dal.MissingUidException:
        raise HTTPException(status_code=404)

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.delete("/bdbs", tags=["bdb"], operation_id="delete_all_bdbs")
def delete_all_bdbs():
    try:
        dal.delete_all_bdbs()
    except Exception:
        raise  HTTPException(status_code=500)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

