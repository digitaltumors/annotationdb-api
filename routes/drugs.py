import os
from pydantic import BaseModel, Field
from typing import List
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker, selectinload
import pandas as pd
from dotenv import load_dotenv
from models.pubchem import PubchemOutput
from models.tables import Compounds, CompoundSynonyms
from models.output import OutputFormat

load_dotenv(override=True)


router = APIRouter(prefix="/drug")


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
async def get_drugs(
    drugs: str = Query(
        description="Drug names (comma seperated)",
        example="Erlotinib,Gemcitabine,Afatinib",
    ),
    format: OutputFormat = Query(
        OutputFormat.json, description="Output format: `json` or `csv`."
    ),
    session=Depends(get_db_session),
):
    if not drugs:
        raise HTTPException(
            status_code=400, detail="Need to include at least one drug to get output"
        )

    drug_list = [drug for drug in drugs.split(",")]

    if not drug_list:
        raise HTTPException(status_code=400, detail="No valid drug names found.")

    conditions = []
    for name in drug_list:
        conditions.append(Compounds.title.ilike(name))
        conditions.append(Compounds.cid.ilike(name))
        conditions.append(Compounds.smiles.ilike(name))
        conditions.append(CompoundSynonyms.synonym.ilike(name))

    query = (
        session.query(Compounds)
        .options(
            selectinload(Compounds.mechanisms),
        )
        .outerjoin(CompoundSynonyms, Compounds.cid == CompoundSynonyms.pubchem_cid)
        .filter(or_(*conditions))
        .distinct()
    )

    rows = query.all()

    return rows
