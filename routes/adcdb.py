import os
from typing import List, Annotated
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_, cast, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from models.adc import AdcList, AdcOutput
from models.tables import AntibodyDrugConjugates
from models.output import OutputFormat
from routes.substances import get_substances

load_dotenv(override=True)

router = APIRouter(prefix="/adc", tags=["Antibody-drug Conjugates"])

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
    summary="Extract ADC data for list of unique identifiers",
    response_model=List[AdcOutput],
)
async def get_adcs(
    adcs: Annotated[
        list[str],
        Query(
            alias="adc",
            description="Unique ADC identifiers such as: adc_id, adc_name, or adc_drug_name (&adc= separated))",
        ),
    ],
    session=Depends(get_db_session),
):
    if not adcs:
        raise HTTPException(
            status_code=400,
            detail="Need to include at least one ADC to get output",
        )

    raw_terms = [c.strip() for c in adcs if c.strip()]
    if not raw_terms:
        raise HTTPException(status_code=400, detail="No valid ADC names found.")

    if len(raw_terms) > 250:
        raise HTTPException(
            status_code=413,
            detail="ADC list is too large, please batch identifiers into a list of 250 or less",
        )

    other_terms = list(dict.fromkeys(term.lower() for term in raw_terms))
    other_terms_255 = [term[:255] for term in other_terms]

    # match indexed expressions
    name_idx_expr = cast(func.lower(AntibodyDrugConjugates.adc_name), CHAR(255, charset="utf8mb4"))
    drug_name_idx_expr = cast(func.lower(AntibodyDrugConjugates.adc_drug_name), CHAR(255, charset="utf8mb4"))
    id_idx_expr = cast(func.lower(AntibodyDrugConjugates.adc_id), CHAR(255, charset="utf8mb4"))

    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(AntibodyDrugConjugates)
                .filter(
                    or_(
                        name_idx_expr.in_(other_terms_255),
                        drug_name_idx_expr.in_(other_terms_255),
                        id_idx_expr.in_(other_terms_255),
                    )
                )
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

    if not rows:
        return []

    # Gather search terms for each ADC to query the substances table
    search_terms = []
    adc_to_terms = {}
    for r in rows:
        terms = []
        if r.adc_pubchem_sid:
            terms.append(str(r.adc_pubchem_sid))
        if r.adc_drug_name:
            terms.append(r.adc_drug_name)
        
        search_terms.extend(terms)
        adc_to_terms[r.adc_id] = terms

    search_terms = list(dict.fromkeys(search_terms))

    substances_results = []
    if search_terms:
        substances_results = await get_substances(
            substances=search_terms,
            format=OutputFormat.json,
            mechanism=True,
            toxicity=True,
            session=session
        )

    # get_substances sets query_field on the returned ORM objects
    term_lower_to_substance = {}
    for res in substances_results:
        if hasattr(res, "query_field") and res.query_field:
            term_lower_to_substance[res.query_field.lower()] = res

    term_lower_to_orig = {t.lower(): t for t in raw_terms}
    for c in rows:
        # Resolve query_field for the ADC itself
        c.query_field = (
            term_lower_to_orig.get((c.adc_id or "").lower()[:255])
            or term_lower_to_orig.get((c.adc_name or "").lower()[:255])
            or term_lower_to_orig.get((c.adc_drug_name or "").lower()[:255])
        )
        
        # Attach substance_data using either SID or drug name
        subst = None
        terms_to_check = adc_to_terms.get(c.adc_id, [])
        for term in terms_to_check:
            term_lower = str(term).lower()
            if term_lower in term_lower_to_substance:
                subst = term_lower_to_substance[term_lower]
                break
                
        c.substance_data = subst

    return rows


@router.get(
    "/all",
    summary="Get ADC IDs, names, and drug names for all ADCs in AnnotationDB",
    response_model=List[AdcList],
)
async def get_adc_identifiers(
    session=Depends(get_db_session),
):
    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(
                    AntibodyDrugConjugates.adc_id,
                    AntibodyDrugConjugates.adc_name,
                    AntibodyDrugConjugates.adc_drug_name,
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
            {
                "adc_id": row[0],
                "adc_name": row[1],
                "adc_drug_name": row[2],
            }
        )

    return result