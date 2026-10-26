import os
from typing import List, Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Security
from sqlalchemy import select, or_, cast, func
from sqlalchemy.dialects.mysql import CHAR
from dotenv import load_dotenv

from models.atc import ATCCode, ATCCodesOutput
from models.tables import ATCCodes
from models.auth import get_api_key
from models.database import get_db_session

load_dotenv(override=True)

router = APIRouter(prefix="/atc", tags=["ATC Overlap"])


@router.get(
    "/overlap",
    summary="Get levels of overlap between two atc codes",
    response_model=ATCCodesOutput,
)
async def get_atcs(
    atc1: Annotated[str, Query(alias="atc code 1", example="A01AB04")],
    atc2: Annotated[str, Query(alias="atc code 2", example="A01AB10")],
    api_key: str = Security(get_api_key),
    session=Depends(get_db_session),
):

    # if atc1 or atc2 don't exist, return error
    if not atc1 or not atc2:
        raise HTTPException(
            status_code=400,
            detail="Need to include two atc codes to get overlap levels",
        )

    # count the number of overlapping characters
    total_chars = 0
    for i, char in enumerate(atc1):
        if i < len(atc2) and char == atc2[i]:
            total_chars += 1
        else:
            break

    # ATC level character lengths: Level 1 (1), Level 2 (3), Level 3 (4), Level 4 (5), Level 5 (7)
    level_lengths = [1, 3, 4, 5, 7]

    # Step 1: Collect overlapping prefix strings
    overlapping_prefixes = []
    for length in level_lengths:
        if total_chars >= length:
            prefix = atc1[:length]
            overlapping_prefixes.append(prefix)

    # Return early if there is no overlap
    if not overlapping_prefixes:
        return ATCCodesOutput(levels=[])

    # Step 2: Fetch matching ATC codes from DB in level order
    stmt = (
        select(ATCCodes)
        .where(ATCCodes.code.in_(overlapping_prefixes))
        .order_by(ATCCodes.code)
    )
    atc_codes = session.execute(stmt).scalars().all()

    return {"levels": atc_codes}


