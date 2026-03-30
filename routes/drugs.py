import os
from pydantic import BaseModel, Field
from typing import List, Annotated
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import create_engine, select, or_, cast, func, select
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import sessionmaker, selectinload
import pandas as pd
from dotenv import load_dotenv
from models.pubchem import PubchemOutput, PubchemList, CompoundManyNewResponse
from models.tables import CompoundBioAssays, Compounds, CompoundSynonyms, BioAssays
from models.output import OutputFormat

GOLDEN_BIOASSAYS = [
    2060322,
    624171,
    624246,
    743035,
    743036,
    743040,
    743042,
    743069,
    624287,
    624288,
    743075,
    743079,
    743080,
    743094,
    1645877,
    652025,
    1963823,
    1963824,
    1645876,
    651631,
    504706,
    686970,
    902,
    903,
    904,
    914,
    915,
    924,
    1454,
    2528,
    995,
    485349,
    1347055,
]

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
    compounds: Annotated[
        list[str],
        Query(
            alias="compound",
            description="Unique compound identifiers such as: compound name, SMILE, inchikey, or pubchem CID (&compound= separated))",
        ),
    ],
    format: OutputFormat = Query(
        OutputFormat.json,
        description="Output format: json",
        # description="Output format: `json` or `csv`."
    ),
    bioassay: bool = Query(
        False,
        description="Toggle to include homo sapien relevant bioassays for queried compound(s)",
    ),
    mechanism: bool = Query(
        False, description="Toggle to include ChEMBL mechanism for queried compound(s)"
    ),
    toxicity: bool = Query(
        False, description="Toggle to include toxicity for queried compound(s)"
    ),
    golden_bioassay: bool = Query(
        False,
        description="Toggle to include gold standard bioassays for queried compound(s)",
    ),
    session=Depends(get_db_session),
):
    if not compounds:
        raise HTTPException(
            status_code=400,
            detail="Need to include at least one compound to get output",
        )

    raw_terms = [c.strip() for c in compounds if c.strip()]

    if not raw_terms:
        raise HTTPException(status_code=400, detail="No valid compound names found.")

    if len(raw_terms) > 250:
        raise HTTPException(
            status_code=413,
            detail="Compound list is too large, please batch identifiers into a list of 250 or less",
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

    # functional indexes
    other_terms_255 = [term[:255] for term in other_terms]
    inchikey_terms_27 = [term[:27] for term in inchikey_terms]

    options = []
    if mechanism:
        options.append(selectinload(Compounds.mechanisms))
    if bioassay:
        if golden_bioassay:
            options.append(
                selectinload(
                    Compounds.bioassays.and_(BioAssays.aid.in_(GOLDEN_BIOASSAYS))
                )
            )
        else:
            options.append(selectinload(Compounds.bioassays))
    if toxicity:
        options.append(selectinload(Compounds.toxicity))

    # match indexed expressions on pubchem_compounds exactly
    title_idx_expr = cast(func.lower(Compounds.title), CHAR(255, charset="utf8mb4"))
    smiles_idx_expr = cast(func.lower(Compounds.smiles), CHAR(255, charset="utf8mb4"))
    mapped_name_idx_expr = cast(
        func.lower(Compounds.mapped_name), CHAR(255, charset="utf8mb4")
    )
    inchikey_idx_expr = cast(
        func.lower(Compounds.inchikey), CHAR(27, charset="utf8mb4")
    )

    # resolve all term types to CIDs using separate index queries.
    resolved_cids: set[int] = set(cid_terms)

    try:
        if inchikey_terms_27:
            rows_ik = (
                session.query(Compounds.cid)
                .filter(inchikey_idx_expr.in_(inchikey_terms_27))
                .all()
            )
            resolved_cids.update(r[0] for r in rows_ik)

        if other_terms_255:
            rows_other = (
                session.query(Compounds.cid)
                .filter(
                    or_(
                        title_idx_expr.in_(other_terms_255),
                        smiles_idx_expr.in_(other_terms_255),
                        mapped_name_idx_expr.in_(other_terms_255),
                    )
                )
                .all()
            )
            resolved_cids.update(r[0] for r in rows_other)

            # Batch synonym lookup
            rows_syn = (
                session.query(CompoundSynonyms.pubchem_cid)
                .filter(CompoundSynonyms.synonym.in_(other_terms))
                .all()
            )
            resolved_cids.update(r[0] for r in rows_syn)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Data retrieval error: {error}")

    if not resolved_cids:
        return []

    # single PK lookup for all resolved CIDs with eager-load
    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(Compounds)
                .options(*options)
                .filter(Compounds.cid.in_(resolved_cids))
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
    "/many/streamline",
    summary="New endpoint to extract compound data for list of unique identifiers with improved query performance",
    response_model=CompoundManyNewResponse,
)
async def get_compounds_new(
    compounds: Annotated[
        list[str],
        Query(
            alias="compound",
            description="Unique compound identifiers such as: compound name, SMILE, inchikey, or pubchem CID (&compound= separated))",
        ),
    ],
    format: OutputFormat = Query(
        OutputFormat.json,
        description="Output format: json",
        # description="Output format: `json` or `csv`."
    ),
    bioassay: bool = Query(
        False,
        description="Toggle to include homo sapien relevant bioassays for queried compound(s)",
    ),
    mechanism: bool = Query(
        False, description="Toggle to include ChEMBL mechanism for queried compound(s)"
    ),
    toxicity: bool = Query(
        False, description="Toggle to include toxicity for queried compound(s)"
    ),
    golden_bioassay: bool = Query(
        False,
        description="Toggle to include gold standard bioassays for queried compound(s)",
    ),
    session=Depends(get_db_session),
):

    if not compounds:
        raise HTTPException(
            status_code=400,
            detail="Need to include at least one compound to get output",
        )

    raw_terms = [c.strip() for c in compounds if c.strip()]

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
        if golden_bioassay:
            options.append(
                selectinload(
                    Compounds.compound_bioassays.and_(
                        CompoundBioAssays.bioassay_aid.in_(GOLDEN_BIOASSAYS)
                    )
                ).load_only(
                    CompoundBioAssays.pubchem_cid, CompoundBioAssays.bioassay_aid
                )
            )
        else:
            options.append(
                selectinload(Compounds.compound_bioassays).load_only(
                    CompoundBioAssays.pubchem_cid, CompoundBioAssays.bioassay_aid
                )
            )
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
        raise HTTPException(
            status_code=400, detail="No valid compound identifiers found."
        )

    retry = 0
    while retry < 3:
        try:
            rows = (
                session.query(Compounds).options(*options).filter(or_(*filters)).all()
            )
            break
        except Exception as error:
            if retry >= 2:
                raise HTTPException(
                    status_code=500, detail=f"Data retrieval error: {error}"
                )
            print(f"retry {retry}: {error}")
            retry += 1

    compound_aid_map: dict[int, list[int]] = {}
    all_aids: set[int] = set()

    if bioassay:
        for compound in rows:
            aids = [link.bioassay_aid for link in compound.compound_bioassays]
            aids = list(dict.fromkeys(aids))
            compound_aid_map[compound.cid] = aids
            all_aids.update(aids)

    bioassay_lookup: dict[int, dict] = {}

    if bioassay and all_aids:
        bioassay_rows = (
            session.query(BioAssays).filter(BioAssays.aid.in_(all_aids)).all()
        )

        for b in bioassay_rows:
            bioassay_lookup[b.aid] = {
                "aid": b.aid,
                "version": b.version,
                "assay_name": b.assay_name,
                "source_name": b.source_name,
                "source_id": b.source_id,
                "description_combined": b.description_combined,
                "protocol_combined": b.protocol_combined,
                "comment_combined": b.comment_combined,
                "activity_outcome_method": b.activity_outcome_method,
                "target_name": b.target_name,
                "target_protein_accession": b.target_protein_accession,
            }

    compounds_payload = []
    for c in rows:
        compounds_payload.append(
            {
                "cid": c.cid,
                "title": c.title,
                "mapped_name": c.mapped_name,
                "molecule_chembl_id": c.molecule_chembl_id,
                "molecular_formula": c.molecular_formula,
                "molecular_weight": c.molecular_weight,
                "smiles": c.smiles,
                "connectivity_smiles": c.connectivity_smiles,
                "inchi": c.inchi,
                "inchikey": c.inchikey,
                "iupac_name": c.iupac_name,
                "xlogp": c.xlogp,
                "exact_mass": c.exact_mass,
                "monoisotopic_mass": c.monoisotopic_mass,
                "tpsa": c.tpsa,
                "complexity": c.complexity,
                "charge": c.charge,
                "h_bond_donor_count": c.h_bond_donor_count,
                "h_bond_acceptor_count": c.h_bond_acceptor_count,
                "rotatable_bond_count": c.rotatable_bond_count,
                "heavy_atom_count": c.heavy_atom_count,
                "isotope_atom_count": c.isotope_atom_count,
                "atom_stereo_count": c.atom_stereo_count,
                "defined_atom_stereo_count": c.defined_atom_stereo_count,
                "undefined_atom_stereo_count": c.undefined_atom_stereo_count,
                "bond_stereo_count": c.bond_stereo_count,
                "defined_bond_stereo_count": c.defined_bond_stereo_count,
                "undefined_bond_stereo_count": c.undefined_bond_stereo_count,
                "covalent_unit_count": c.covalent_unit_count,
                "volume_3d": c.volume_3d,
                "x_steric_quadrupole_3d": c.x_steric_quadrupole_3d,
                "y_steric_quadrupole_3d": c.y_steric_quadrupole_3d,
                "z_steric_quadrupole_3d": c.z_steric_quadrupole_3d,
                "feature_count_3d": c.feature_count_3d,
                "feature_acceptor_count_3d": c.feature_acceptor_count_3d,
                "feature_donor_count_3d": c.feature_donor_count_3d,
                "feature_anion_count_3d": c.feature_anion_count_3d,
                "feature_cation_count_3d": c.feature_cation_count_3d,
                "feature_ring_count_3d": c.feature_ring_count_3d,
                "feature_hydrophobe_count_3d": c.feature_hydrophobe_count_3d,
                "conformer_model_rmsd_3d": c.conformer_model_rmsd_3d,
                "effective_rotor_count_3d": c.effective_rotor_count_3d,
                "conformer_count_3d": c.conformer_count_3d,
                "fingerprint_2d": c.fingerprint_2d,
                "patent_count": c.patent_count,
                "patent_family_count": c.patent_family_count,
                "literature_count": c.literature_count,
                "annotation_types": c.annotation_types,
                "annotation_type_count": c.annotation_type_count,
                "fda_approval": c.fda_approval,
                "date_added": c.date_added,
                "mechanisms": c.mechanisms if mechanism else None,
                "toxicity": c.toxicity if toxicity else None,
                "bioassays": compound_aid_map.get(c.cid, []),
            }
        )

    return {
        "compounds": compounds_payload,
        "bioassays": bioassay_lookup,
    }


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
                    Compounds.title,
                    Compounds.cid,
                    Compounds.smiles,
                    Compounds.inchikey,
                    Compounds.mapped_name,
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
                "cid": row[1],
                "smiles": row[2],
                "inchikey": row[3],
                "mapped_name": row[4],
            }
        )

    return result
