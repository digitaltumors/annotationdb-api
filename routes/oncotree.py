import os
from pydantic import BaseModel, Field
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, or_
import pandas as pd
from dotenv import load_dotenv
from models.tables import CellLines
from models.database import get_db_session

load_dotenv(override=True)


router = APIRouter(prefix="/oncotree")


@router.get(
    "/many",
    summary="Extract cell line data by via cell line name",
)
async def get_cell_lines(
    cell_lines: str = Query(
        description="Cell line names or cellosaurus accession id's (comma seperated)",
        example="HL-60,HeLa,CVCL_0060,CVCL_2030",
    ),
    # format: OutputFormat = Query(
    #     OutputFormat.json, description="Output format: `json` or `csv`."
    # ),
    session=Depends(get_db_session),
):
    if not cell_lines:
        raise HTTPException(
            status_code=400, detail="Need to include at least one drug to get output"
        )

    cell_line_list = [drug for drug in cell_lines.split(",")]

    conditions = []
    for name in cell_line_list:
        conditions.append(CellLines.cell_line_name.ilike(name))
        conditions.append(CellLines.accession.ilike(name))
        conditions.append(CellLines.synonyms.ilike(name))

    rows = session.query(CellLines).filter(or_(*conditions)).distinct().all()

    return rows
