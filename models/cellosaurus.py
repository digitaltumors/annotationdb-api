from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Disease(BaseModel):
    id: str
    source: str
    cellosaurus_accession: str
    description: str


class CellosaurusOutput(BaseModel):
    accession: str
    cell_line_name: str = None
    category: str
    date: str
    age_at_sampling: str
    sex_of_cell: str
    hierarchy: str

    # Comment fields
    cell_type: str
    derived_from_site: str
    donor_information: str
    doubling_time: str
    genome_ancestry: str
    hla_typing: str
    microsatellite_instability: str
    omics: str
    part_of: str
    population: str
    sequence_variation: str
    anecdotal: str
    biotechnology: str
    discontinued: str
    group_col: str
    misspelling: str
    registration: str
    virology: str
    caution: str
    characteristics: str
    karyotypic_information: str
    problematic_cell_line: str
    transformant: str
    miscellaneous: str
    from_col: str
    genetic_integration: str
    knockout_cell: str
    selected_for_resistance_to: str

    # ORM relationship fields
    diseases: Optional[list[Disease]] = None
