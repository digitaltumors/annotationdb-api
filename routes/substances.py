import os
from pydantic import Field
from typing import List, Annotated
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_, cast, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import sessionmaker, selectinload
from dotenv import load_dotenv
from models.pubchem import SubstanceOutput, SubstanceList
from models.tables import Substances, SubstanceSynonyms, SubstanceToxicity
from models.output import OutputFormat

load_dotenv(override=True)

router = APIRouter(prefix="/substance", tags=["Substances"])

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
    summary="Extract substance data for list of unique identifiers",
    response_model=List[SubstanceOutput],
)
async def get_substances(
    substances: Annotated[
        list[str],
        Query(
            alias="substance",
            description="Unique substance identifiers such as: substance name or pubchem sid (&substance= separated))",
        ),
    ],
    format: OutputFormat = Query(
        OutputFormat.json,
        description="Output format: json",
        # description="Output format: `json` or `csv`."
    ),
    mechanism: bool = Query(
        False, description="Toggle to include ChEMBL mechanism for queried substance(s)"
    ),
    toxicity: bool = Query(
        False, description="Toggle to include toxicity for queried substance(s)"
    ),
    session=Depends(get_db_session),
):
    if not substances:
        raise HTTPException(
            status_code=400,
            detail="Need to include at least one substance to get output",
        )

    raw_terms = [c.strip() for c in substances if c.strip()]

    if not raw_terms:
        raise HTTPException(status_code=400, detail="No valid substance names found.")

    if len(raw_terms) > 250:
        raise HTTPException(
            status_code=413,
            detail="substance list is too large, please batch identifiers into a list of 250 or less",
        )

    sid_terms: list[int] = []
    other_terms: list[str] = []

    for term in raw_terms:
        if term.isdigit():
            sid_terms.append(int(term))
            continue

        other_terms.append(term.lower())

    sid_terms = list(dict.fromkeys(sid_terms))
    other_terms = list(dict.fromkeys(other_terms))

    # functional indexes
    other_terms_255 = [term[:255] for term in other_terms]

    options = []
    if mechanism:
        options.append(selectinload(Substances.mechanisms))
   
    if toxicity:
        options.append(selectinload(Substances.toxicity))

    # match indexed expressions on pubchem_substances exactly
    title_idx_expr = cast(func.lower(Substances.title), CHAR(255, charset="utf8mb4"))
    mapped_name_idx_expr = cast(
        func.lower(Substances.mapped_name), CHAR(255, charset="utf8mb4")
    )

    # resolve all term types to sids
    resolved_sids: set[int] = set(sid_terms)

    try:
        if other_terms_255:
            rows_other = (
                session.query(Substances.sid)
                .filter(
                    or_(
                        title_idx_expr.in_(other_terms_255),
                        mapped_name_idx_expr.in_(other_terms_255),
                    )
                )
                .all()
            )
            resolved_sids.update(r[0] for r in rows_other)

            # Batch synonym lookup
            rows_syn = (
                session.query(SubstanceSynonyms.sid)
                .filter(SubstanceSynonyms.synonym.in_(other_terms))
                .all()
            )
            resolved_sids.update(r[0] for r in rows_syn)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Data retrieval error: {error}")

    if not resolved_sids:
        return []

    # single PK lookup for all resolved sids with eager-load
    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(Substances)
                .options(*options)
                .filter(Substances.sid.in_(resolved_sids))
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

    # Match each substance back to the original query term using already-loaded fields
    term_lower_to_orig = {t.lower(): t for t in raw_terms}
    for c in rows:
        c.query_field = (
            term_lower_to_orig.get(str(c.sid))
            or term_lower_to_orig.get((c.title or "").lower()[:255])
            or term_lower_to_orig.get((c.mapped_name or "").lower()[:255])
        )

    # Synonym fallback — only query for substances that didn't match above
    unresolved = [c for c in rows if c.query_field is None]
    if other_terms and unresolved:
        syn_rows = (
            session.query(SubstanceSynonyms.sid, SubstanceSynonyms.synonym)
            .filter(
                SubstanceSynonyms.sid.in_([c.sid for c in unresolved]),
                SubstanceSynonyms.synonym.in_(other_terms),
            )
            .all()
        )
        sid_to_syn = {sid: term_lower_to_orig.get(syn.lower()) for sid, syn in syn_rows}
        for c in unresolved:
            c.query_field = sid_to_syn.get(c.sid)

    return rows

@router.get(
    "/all",
    summary="Get names, pubchem sids, and the initial mapped names for all substances in AnnotationDB",
    response_model=List[SubstanceList],
)
async def get_substance_identifiers(
    session=Depends(get_db_session),
):
    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(
                    Substances.title,
                    Substances.sid,
                    Substances.mapped_name,
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
                "name": row[0],
                "sid": row[1],
                "mapped_name": row[2],
            }
        )

    return result