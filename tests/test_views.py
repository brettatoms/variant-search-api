from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from variant_search.app import app
import variant_search.db as db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def data():
    return BytesIO(
        b"\n".join(
            [
                b"gene\tother_data",
                b"abcd\tsome other data",
                b"abcd\tsame gene different data",
                b"test\ta different gene",
                b"texas\tthe biggest gene",
            ]
        )
    )


@pytest.fixture(autouse=True, scope="session")
def init_db(data):
    db.populate_db(data)


@pytest.mark.parametrize(
    "query,result", [["te", {"test", "texas"}], ["test", {"test"}], ["a", {"abcd"}]]
)
def test_list_view(client, query, result):
    resp = client.get(f"/v1/genes?q={query}")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert set(data) == result


columns = ["gene", "other_data"]


@pytest.mark.parametrize(
    "gene,result",
    [
        ["test", {"columns": columns, "data": [["test", "a different gene"]]}],
        [
            "abcd",
            {
                "columns": columns,
                "data": [
                    ["abcd", "some other data"],
                    ["abcd", "same gene different data"],
                ],
            },
        ],
    ],
)
def test_detail_view(client, gene, result):
    resp = client.get(f"/v1/genes/{gene}")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["columns"] == result["columns"]
    assert data["data"] == result["data"]
