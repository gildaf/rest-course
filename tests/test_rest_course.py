import random

import httpx
import pytest

BASE_URL = "http://localhost:8000"
BDBS_URL = f"{BASE_URL}/bdbs"


@pytest.fixture(scope="module")
def client():
    return httpx.Client(event_hooks={"response": [lambda r: r.raise_for_status()]})


@pytest.fixture(scope="module", autouse=True)
def setup(client):
    # Create some BDBs
    bdbs = []
    for _ in range(5):
        i = random.randint(1000, 10000)
        params = {"name": f"foo{i}", "memory_size": i}
        resp = client.post(BDBS_URL, json=params)
        bdbs.append(resp.json()['uid'])
    yield

    #for uid in bdbs:
    #    url = f'{BDBS_URL}/{uid}'
    #    client.delete(url)
    client.delete(BDBS_URL)


def test_nothing(client):
    pass


def test_create_bdb(client):
    """
    Assumptions:
     - We do not rely on any preexisting server-side objects
     - Other requests may create and modify such objects while we run
     - Objects created by us belong to us, others should not touch them
    """

    # Get current list of BDBs
    r = client.get(BDBS_URL)
    bdb_uids_before = set(bdb["uid"] for bdb in r.json())

    # Create a BDB
    params = {"name": "foo", "memory_size": 2}
    r = client.post(BDBS_URL, json=params)
    bdb = r.json()

    assert bdb["uid"] is not None
    assert bdb["name"] == params["name"]
    assert bdb["memory_size"] == params["memory_size"]

    uid = bdb["uid"]
    assert uid not in bdb_uids_before, "UID was unexpectedly reused"

    # Get the BDB
    bdb_url = f"{BDBS_URL}/{uid}"  # Ugly: manual composition of URL
    r = client.get(bdb_url)
    assert r.json() == bdb, "BDB has changed since creation"

    # Check that new BDB is in list
    r = client.get(BDBS_URL)
    bdb_uids = set(bdb["uid"] for bdb in r.json())

    assert uid in bdb_uids

    # Clean up
    # TODO: Not implemented yet on the server side
    client.delete(bdb_url)

    with pytest.raises(httpx.HTTPStatusError) as e:
        client.get(bdb_url)
    #import pdb; pdb.set_trace()
    assert e.value.response.status_code==404
