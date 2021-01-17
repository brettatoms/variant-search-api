from fastapi import APIRouter

import variant_search.db as db

router = APIRouter()


@router.get("/genes")
async def list(q: str):
    """Get a list of genes that matches q."""
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        "select distinct gene from variants where gene like ? order by gene",
        (q + "%",),
    )
    return [row[0] for row in cursor]


@router.get("/genes/{id}")
async def details(id: str):
    """Get the details data for a gene."""
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        "select * from variants where gene = ?",
        (id,),
    )

    return {
        "columns": [d[0] for d in cursor.description],
        "data": [row for row in cursor],
    }
