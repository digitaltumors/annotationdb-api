import os
from pydantic import BaseModel
from typing import List, Annotated
from fastapi import APIRouter, HTTPException, Depends, Query
from dotenv import load_dotenv

from models.pubchem import PubchemOutput, SubstanceOutput
from models.output import OutputFormat
from models.database import get_db_session
from routes.drugs import get_compounds
from routes.substances import get_substances

load_dotenv(override=True)

router = APIRouter(prefix="/chemical", tags=["Chemicals"])


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
    indication: bool = Query(
        False,
        description="Toggle to include ChEMBL drug indications for queried chemical(s)",
    ),
    toxicity: bool = Query(
        False, description="Toggle to include toxicity for queried chemical(s)"
    ),
    label: bool = Query(
        False,
        description="Toggle to include the DailyMed drug label (boxed warning, warnings and precautions, adverse reactions) for queried chemical(s) (compounds only)",
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
        indication=indication,
        toxicity=toxicity,
        label=label,
        golden_bioassay=golden_bioassay,
        session=session,
    )

    substances_result = await get_substances(
        substances=chemicals,
        format=format,
        mechanism=mechanism,
        indication=indication,
        toxicity=toxicity,
        session=session,
    )

    return {"compounds": compounds_result, "substances": substances_result}
