import os
from pydantic import BaseModel, Field
from typing import List
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_, cast, func, select
from sqlalchemy.dialects.mysql import CHAR
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
        OutputFormat.json,
        description="Output format: json",
        # description="Output format: `json` or `csv`."
    ),
    bioassay: bool = Query(
        False,
        description="Toggle to include homo sapien relevant bioassays for queried drug(s)",
    ),
    mechanism: bool = Query(
        False, description="Toggle to include ChEMBL mechanism for queried drug(s)"
    ),
    toxicity: bool = Query(
        False, description="Toggle to include toxicity for queried drug(s)"
    ),
    session=Depends(get_db_session),
):
    if not compounds:
        raise HTTPException(
            status_code=400, detail="Need to include at least one drug to get output"
        )

    raw_terms = [term.strip() for term in compounds.split(",") if term.strip()]

    if not raw_terms:
        raise HTTPException(status_code=400, detail="No valid compound names found.")

    if len(raw_terms) > 50:
        raise HTTPException(
            status_code=413,
            detail="Compound list is too large, please batch identifiers into a list of 50 or less",
        )

    cid_terms: list[int] = []
    inchikey_terms: list[str] = []
    other_terms: list[str] = []

    for term in raw_terms:
        if term.isdigit():
            cid_terms.append(int(term))
            continue

        # InChIKey: 27 chars, second-last char is '-'
        if len(term) == 27 and term[-2] == "-":
            inchikey_terms.append(term.lower())
            continue

        other_terms.append(term.lower())

    cid_terms = list(dict.fromkeys(cid_terms))
    inchikey_terms = list(dict.fromkeys(inchikey_terms))
    other_terms = list(dict.fromkeys(other_terms))

    # Your functional indexes on pubchem_compounds are CHAR(255) / CHAR(27)
    other_terms_255 = [term[:255] for term in other_terms]
    inchikey_terms_27 = [term[:27] for term in inchikey_terms]

    options = []
    if mechanism:
        options.append(selectinload(Compounds.mechanisms))
    if bioassay:
        options.append(selectinload(Compounds.bioassays))
    if toxicity:
        options.append(selectinload(Compounds.toxicity))

    # Match the indexed expressions on pubchem_compounds exactly
    title_idx_expr = cast(func.lower(Compounds.title), CHAR(255, charset="utf8mb4"))
    smiles_idx_expr = cast(func.lower(Compounds.smiles), CHAR(255, charset="utf8mb4"))
    mapped_name_idx_expr = cast(
        func.lower(Compounds.mapped_name), CHAR(255, charset="utf8mb4")
    )
    inchikey_idx_expr = cast(
        func.lower(Compounds.inchikey), CHAR(27, charset="utf8mb4")
    )

    filters = []

    if cid_terms:
        filters.append(Compounds.cid.in_(cid_terms))

    if inchikey_terms_27:
        filters.append(inchikey_idx_expr.in_(inchikey_terms_27))

    if other_terms_255:
        filters.append(title_idx_expr.in_(other_terms_255))
        filters.append(smiles_idx_expr.in_(other_terms_255))
        filters.append(mapped_name_idx_expr.in_(other_terms_255))

        # Uses compound_synonyms PRIMARY(synonym, pubchem_cid)
        # Best if synonym column collation is case-insensitive.
        synonym_exists = (
            select(1)
            .select_from(CompoundSynonyms)
            .where(
                CompoundSynonyms.pubchem_cid == Compounds.cid,
                CompoundSynonyms.synonym.in_(other_terms),
            )
            .exists()
        )
        filters.append(synonym_exists)

    if not filters:
        raise HTTPException(status_code=400, detail="No valid compound identifiers found.")

    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(Compounds)
                .options(*options)
                .filter(or_(*filters))
                .all()
            )
            break
        except Exception as error:
            if retry >= 2:
                raise HTTPException(
                    status_code=500, detail=f"Data retrieval error: {error}"
                )
            print(f"retry {retry}: {error}")
            retry += 1

    return rows


@router.get(
    "/all",
    summary="Get names, pubchem cids, smiles, and inchikeys for all compounds in AnnotationDB",
    response_model=List[PubchemList],
)
async def get_compound_identifiers(
    session=Depends(get_db_session),
):
    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(
                    Compounds.title, Compounds.cid, Compounds.smiles, Compounds.inchikey
                )
                .distinct()
                .all()
            )
            break
        except Exception as error:
            if retry >= 2:
                raise HTTPException(
                    status_code=500, detail=f"Data retrieval error: {error}"
                )
            else:
                print(f"retry {retry}: {error}")
                retry += 1

    result = []
    for row in rows:
        result.append(
            {"name": row[0], "cid": row[1], "smiles": row[2], "inchikey": row[3]}
        )

    return result
