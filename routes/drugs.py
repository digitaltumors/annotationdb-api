import os
from pydantic import BaseModel, Field
from typing import List
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker, selectinload
import pandas as pd
from dotenv import load_dotenv
from models.pubchem import PubchemOutput, PubchemList
from models.tables import Compounds, CompoundSynonyms
from models.output import OutputFormat

load_dotenv(override=True)


router = APIRouter(prefix="/compound")


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
    summary="Extract compound data for list of unique identifiers",
    response_model=List[PubchemOutput],
)
async def get_compounds(
    compounds: str = Query(
        description="Unique compound identifiers such as: compound name, SMILE, inchikey, or pubchem CID (comma separated)",
        example="Aspirin,C1=CC=C2C(=C1)C=CC(=O)O2,AQIXAKUUQRKLND-UHFFFAOYSA-N,59174488",
    ),
    format: OutputFormat = Query(
        OutputFormat.json, description="Output format: `json` or `csv`."
    ),
    bioassay: bool = Query(
        False,
        description="Toggle to include homo sapien relevant bioassays for queried drugs",
    ),
    mechanism: bool = Query(
        False,
        description="Toggle to include ChEMBL mechanisms for queried drugs",
    ),
    toxicity: bool = Query(
        False,
        description="Toggle to include toxicity for queried drugs",
    ),
    session=Depends(get_db_session),
):
    if not compounds:
        raise HTTPException(
            status_code=400, detail="Need to include at least one drug to get output"
        )

    compound_list = [compound for compound in compounds.split(",")]

    if not compound_list:
        raise HTTPException(status_code=400, detail="No valid compound names found.")

    if len(compound_list) > 50:
        raise HTTPException(
            status_code=413,
            detail="Compound list is too large, please batch identifiers into list of 50 or less",
        )

    conditions = []
    for name in compound_list:
        conditions.append(Compounds.title.ilike(name))
        conditions.append(Compounds.cid.ilike(name))
        conditions.append(Compounds.smiles.ilike(name))
        conditions.append(Compounds.inchikey.ilike(name))
        conditions.append(CompoundSynonyms.synonym.ilike(name))

    options = []
    if mechanism:
        options.append(selectinload(Compounds.mechanisms))
    if bioassay:
        options.append(selectinload(Compounds.bioassays))
    if toxicity:
        options.append(selectinload(Compounds.toxicity))

    rows = (
        session.query(Compounds)
        .options(*options)
        .outerjoin(
            CompoundSynonyms,
            Compounds.cid == CompoundSynonyms.pubchem_cid,
        )
        .filter(or_(*conditions))
        .distinct()
        .all()
    )

    return rows


@router.get(
    "/all",
    summary="Get names, pubchem cids, smiles, and inchikeys for all compounds in AnnotationDB",
    response_model=List[PubchemList],
)
async def get_compound_identifiers(
    session=Depends(get_db_session),
):
    rows = (
        session.query(
            Compounds.title, Compounds.cid, Compounds.smiles, Compounds.inchikey
        )
        .distinct()
        .all()
    )

    result = []
    for row in rows:
        result.append(
            {"name": row[0], "cid": row[1], "smiles": row[2], "inchikey": row[3]}
        )

    return result
