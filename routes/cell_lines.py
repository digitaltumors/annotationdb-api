import os
from pydantic import BaseModel, Field
from typing import List
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker
import pandas as pd
from dotenv import load_dotenv
from models.pubchem import PubchemOutput
from models.tables import Pubchem
from models.output import OutputFormat

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
    summary="Extract drug data by utilizing drug names",
    # response_model=List[PubchemOutput],
)
async def get_cell_lines(
    cell_lines: str = Query(
        description="Cell line names or cellosaurus accession id's (comma seperated)",
        example="CJM,COLO_005,HeLa OR CVCL_0013,CVCL_053,CVCL_4965",
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

    cell_line_list = [drug for drug in cell_lines.split(",")]

    conditions = []
    for name in cell_line_list:
        if not isinstance(name, str):
            raise HTTPException(
                status_code=400,
                detail="Cell line list must only include strings",
            )
        cleaned = name.strip()
        conditions.append(Cell_line.cell_line_name == cleaned)
        conditions.append(Cell_line.synonyms.like(f"%{cleaned}%"))

    query = select(Cell_line).where(or_(*conditions))
    rows = session.scalars(query).all()

    return rows
