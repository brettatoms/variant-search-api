import csv
import io
import os
import sqlite3
from urllib import request
from typing import IO
from zipfile import ZipFile

from variant_search.settings import settings

__conn = None


def connect(db: str = ":memory:"):
    """Return a connection to the database."""
    global __conn
    if __conn is None:
        __conn = sqlite3.connect(
            db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
    return __conn


def load_local_data(path: str) -> IO[bytes]:
    """Load the variants data from a local file."""
    return ZipFile(path).open("variants.tsv")


def load_remote_data(data_url: str) -> IO[bytes]:
    """Load the variants data from a remote url."""
    resp = request.urlopen(data_url)
    if resp.status != 200:
        raise Exception("Could not download data file")
    # TODO: Since HTTPResponse implements io.BufferedIOBase I would have expected I
    # could pass resp directly to ZipFile but it always raises a BadZipFile
    # error.  Unfortunately that means we have to read all of the data into memory.
    buffer = resp.read()
    return ZipFile(io.BytesIO(buffer)).open("variants.tsv")


def populate_db(data: IO[bytes]) -> None:
    """Populate the database with data."""
    reader = csv.DictReader(
        (row.decode("utf-8") for row in data), dialect=csv.excel_tab
    )
    if reader.fieldnames is None:
        raise Exception("Could not get field names from data")

    colnames = [fieldname.replace(" ", "_").lower() for fieldname in reader.fieldnames]

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("create table variants ({0})".format(",".join(colnames)))
    cursor.executemany(
        "insert into variants({0}) values ({1})".format(
            ",".join(colnames), ",".join(["?"] * len(colnames))
        ),
        (list(row.values()) for row in reader),
    )


data = None
if os.path.exists(settings.data_path):
    # If we have a local file then load the data from disk
    data = load_local_data(settings.data_path)
else:
    # Load the data from the data url
    data = load_remote_data(settings.data_url)


# Load the fetched data into the database. This should only run the first time
# that db.py is imported.
if os.environ.get("TEST", None) != "true":
    populate_db(data)
