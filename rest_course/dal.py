from .types import BDB, UID
import redis
import dataclasses
import typing

_connection = None

BDB_ID_COUNTER = "counter"
BDB_UIDS = "bdb_uids"

class MissingUidException(Exception):
    pass

def get_next_id() -> int:
    client = connect()
    return client.incr(BDB_ID_COUNTER)


def connect() -> redis.Redis:
    global _connection
    if _connection is None:
        _connection = redis.Redis(decode_responses=True)
    return _connection


def save_bdb(bdb: BDB) -> None:
    client = connect()
    bdb_as_dict = dataclasses.asdict(bdb)
    uid = bdb_as_dict.get("uid")
    client.sadd(BDB_UIDS, uid)
    client.hmset(f"bdb:{uid}", bdb_as_dict)


def load_bdb(uid: UID) -> typing.Optional[BDB]:
    client = connect()
    bdb_as_dict = client.hgetall(f"bdb:{uid}")
    if not bdb_as_dict:
        return None
    return BDB(**bdb_as_dict)


def bdb_keys() -> typing.Iterable[UID]:
    client = connect()
    return [UID(uid) for uid in client.smembers(BDB_UIDS)]

def delete_bdb(uid: UID):
    client = connect()
    if client.delete(f"bdb:{uid}") == 0:
        raise MissingUidException(f"missing bdb:{uid}")
    client.srem(BDB_UIDS, uid)

def delete_all_bdbs():
    for uid in bdb_keys():
        delete_bdb(uid)
