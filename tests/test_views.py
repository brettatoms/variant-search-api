from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from variant_search.app import app
import variant_search.db as db

data = [
    ("gene", "other_data"),
    ("abcd", "some other data"),
    ("abcd", "same gene different data"),
    ("test", "a different gene"),
    ("texas", "the biggest gene"),
]

columns = data[0]


def make_result(rows):
    return {"columns": columns, "data": rows}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def csv_data():
    def _encode_row(row):
        return "\t".join(row).encode("utf8")

    return BytesIO(b"\n".join(_encode_row(row) for row in data))


@pytest.fixture(autouse=True, scope="session")
def init_db(csv_data):
    db.populate_db(csv_data)


@pytest.mark.parametrize(
    "query,result", [["te", {"test", "texas"}], ["test", {"test"}], ["a", {"abcd"}]]
)
def test_list_view(client, query, result):
    resp = client.get(f"/v1/genes?q={query}")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert set(data) == result


@pytest.mark.parametrize(
    "gene,result",
    [
        ["test", make_result([["test", "a different gene"]])],
        [
            "abcd",
            make_result(
                [["abcd", "some other data"], ["abcd", "same gene different data"]]
            ),
        ],
    ],
)
def test_detail_view(client, gene, result):
    resp = client.get(f"/v1/genes/{gene}")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["columns"] == list(result["columns"])
    assert data["data"] == result["data"]
