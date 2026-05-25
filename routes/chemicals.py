import os
from pydantic import BaseModel
from typing import List, Annotated
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from models.pubchem import PubchemOutput, SubstanceOutput
from models.output import OutputFormat
from routes.drugs import get_compounds
from routes.substances import get_substances

load_dotenv(override=True)

router = APIRouter(prefix="/chemical", tags=["Chemicals"])

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

class ChemicalsOutput(BaseModel):
    compounds: List[PubchemOutput]
    substances: List[SubstanceOutput]

@router.get(
    "/many",
    summary="Extract chemical data (compounds and substances) for list of unique identifiers",
    response_model=ChemicalsOutput,
)
async def get_chemicals(
    chemicals: Annotated[
        list[str],
        Query(
            alias="chemical",
            description="Unique chemical identifiers such as: name, SMILE, inchikey, or pubchem CID/SID (&chemical= separated))",
        ),
    ],
    format: OutputFormat = Query(
        OutputFormat.json,
        description="Output format: json",
    ),
    bioassay: bool = Query(
        False,
        description="Toggle to include homo sapien relevant bioassays for queried chemical(s) (compounds only)",
    ),
    mechanism: bool = Query(
        False, description="Toggle to include ChEMBL mechanism for queried chemical(s)"
    ),
    toxicity: bool = Query(
        False, description="Toggle to include toxicity for queried chemical(s)"
    ),
    golden_bioassay: bool = Query(
        False,
        description="Toggle to include gold standard bioassays for queried chemical(s) (compounds only)",
    ),
    session=Depends(get_db_session),
):
    if not chemicals:
        raise HTTPException(
            status_code=400,
            detail="Need to include at least one chemical to get output",
        )

    # Call the original functions
    compounds_result = await get_compounds(
        compounds=chemicals,
        format=format,
        bioassay=bioassay,
        mechanism=mechanism,
        toxicity=toxicity,
        golden_bioassay=golden_bioassay,
        session=session
    )

    substances_result = await get_substances(
        substances=chemicals,
        format=format,
        mechanism=mechanism,
        toxicity=toxicity,
        session=session
    )

    return {
        "compounds": compounds_result,
        "substances": substances_result
    }