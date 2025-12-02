import os
from pydantic import BaseModel, Field
from typing import List
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker, selectinload
import pandas as pd
from dotenv import load_dotenv
from models.tables import CellLines, CellLineSynonyms, CellLineDisease
from models.output import OutputFormat
from models.cellosaurus import CellosaurusOutput

load_dotenv(override=True)


router = APIRouter(prefix="/cell_lines")


# Creating database connection/session
password_cleaned = quote_plus(os.getenv("DATABASE_PASS"))
engine = create_engine(
    f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{password_cleaned}"
    f"@{os.getenv('DATABASE_IP')}:{os.getenv('PORT')}/{os.getenv('SELECTED_DB')}",
    echo=True,
)
session_maker = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session():
    session = session_maker()
    yield session  # Use 'yields' instead of 'return' to ensure we can close the session, avoiding leaks
    session.close()


@router.get(
    "/many",
    summary="Extract cell line data from list of cell line names and/or cellosaurus accession ids",
    response_model=List[CellosaurusOutput],
)
async def get_cell_lines(
    cell_lines: str = Query(
        description="Unique cell line identifiers such as: cell line name or cellosaurus accession id (comma seperated)",
        example="HL-60,HeLa,CVCL_0060,CVCL_2030",
    ),
    format: OutputFormat = Query(
        OutputFormat.json, description="Output format: `json` or `csv`."
    ),
    session=Depends(get_db_session),
):
    if not cell_lines:
        raise HTTPException(
            status_code=400, detail="Need to include at least one drug to get output"
        )

    cell_line_list = [cell_line for cell_line in cell_lines.split(",")]

    conditions = []
    for identifier in cell_line_list:
        conditions.append(CellLines.cell_line_name.ilike(identifier))
        conditions.append(CellLines.accession.ilike(identifier))
        conditions.append(CellLineSynonyms.synonym.ilike(identifier))

    rows = (
        session.query(CellLines)
        .options(selectinload(CellLines.diseases))
        .outerjoin(
            CellLineSynonyms,
            CellLines.accession == CellLineSynonyms.cellosaurus_accession,
        )
        .filter(or_(*conditions))
        .distinct()
        .all()
    )

    return rows


@router.get(
    "/all",
    summary="Get all cell line names and cellosaurus accession ids for all cell lines that exist in AnnotationDB",
)
async def get_cell_line_names(
    session=Depends(get_db_session),
):
    rows = (
        session.query(
            CellLines.cell_line_name,
            CellLines.accession,
        )
        .distinct()
        .all()
    )

    result = []
    for row in rows:
        result.append({"name": row[0], "accession": row[1]})

    return result
