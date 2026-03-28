from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Toxicity(BaseModel):
    pubchem_cid: int
    dili_severity_grade: int
    dili_annotation: str
    hepatotoxicity_likelihood_score: str


class Bioassay(BaseModel):
    aid: int
    version: int
    assay_name: str
    source_name: str
    source_id: str
    description_combined: str
    protocol_combined: str
    comment_combined: str
    activity_outcome_method: int
    target_name: str
    target_protein_accession: str


class Mechanism(BaseModel):
    molecule_chembl_id: str
    parent_molecule_chembl_id: str
    action_type: str
    binding_site_comment: str
    mechanism_of_action: str
    mechanism_comment: str
    direct_interaction: int
    disease_efficacy: int
    max_phase: int
    mec_id: int
    molecular_mechanism: int
    record_id: int
    selectivity_comment: str
    site_id: str
    target_chembl_id: str

    # Fields below are extracted from the variant sequence object (if it exists [likely does not])
    variant_sequence_accession: str
    variant_sequence_isoform: int
    variant_sequence_mutation: str
    variant_sequence_organism: str
    variant_sequence_sequence: str
    variant_sequence_tax_id: int
    variant_sequence_version: int


class PubchemOutput(BaseModel):
    cid: int
    title: str
    mapped_name: str
    molecule_chembl_id: Optional[str] = None
    molecular_formula: str
    molecular_weight: str
    smiles: str
    connectivity_smiles: str
    inchi: str
    inchikey: str
    iupac_name: str
    xlogp: float
    exact_mass: str
    monoisotopic_mass: str
    tpsa: float
    complexity: int
    charge: int
    h_bond_donor_count: int
    h_bond_acceptor_count: int
    rotatable_bond_count: int
    heavy_atom_count: int
    isotope_atom_count: int
    atom_stereo_count: int
    defined_atom_stereo_count: int
    undefined_atom_stereo_count: int
    bond_stereo_count: int
    defined_bond_stereo_count: int
    undefined_bond_stereo_count: int
    covalent_unit_count: int
    volume_3d: float
    x_steric_quadrupole_3d: float
    y_steric_quadrupole_3d: float
    z_steric_quadrupole_3d: float
    feature_count_3d: int
    feature_acceptor_count_3d: int
    feature_donor_count_3d: int
    feature_anion_count_3d: int
    feature_cation_count_3d: int
    feature_ring_count_3d: int
    feature_hydrophobe_count_3d: int
    conformer_model_rmsd_3d: float
    effective_rotor_count_3d: int
    conformer_count_3d: int
    fingerprint_2d: str
    patent_count: int
    patent_family_count: int
    literature_count: int
    annotation_types: str
    annotation_type_count: int
    fda_approval: bool
    date_added: datetime

    # ORM relationship fields
    mechanisms: Optional[list[Mechanism] | None] = None
    bioassays: Optional[list[Bioassay] | None] = None
    toxicity: Optional[Toxicity | None] = None


class PubChemOutputWithBioassayIds(BaseModel):
    cid: int
    title: str
    mapped_name: str
    molecule_chembl_id: Optional[str] = None
    molecular_formula: str
    molecular_weight: str
    smiles: str
    connectivity_smiles: str
    inchi: str
    inchikey: str
    iupac_name: str
    xlogp: float
    exact_mass: str
    monoisotopic_mass: str
    tpsa: float
    complexity: int
    charge: int
    h_bond_donor_count: int
    h_bond_acceptor_count: int
    rotatable_bond_count: int
    heavy_atom_count: int
    isotope_atom_count: int
    atom_stereo_count: int
    defined_atom_stereo_count: int
    undefined_atom_stereo_count: int
    bond_stereo_count: int
    defined_bond_stereo_count: int
    undefined_bond_stereo_count: int
    covalent_unit_count: int
    volume_3d: float
    x_steric_quadrupole_3d: float
    y_steric_quadrupole_3d: float
    z_steric_quadrupole_3d: float
    feature_count_3d: int
    feature_acceptor_count_3d: int
    feature_donor_count_3d: int
    feature_anion_count_3d: int
    feature_cation_count_3d: int
    feature_ring_count_3d: int
    feature_hydrophobe_count_3d: int
    conformer_model_rmsd_3d: float
    effective_rotor_count_3d: int
    conformer_count_3d: int
    fingerprint_2d: str
    patent_count: int
    patent_family_count: int
    literature_count: int
    annotation_types: str
    annotation_type_count: int
    fda_approval: bool
    date_added: datetime

    # ORM relationship fields
    mechanisms: Optional[list[Mechanism] | None] = None
    toxicity: Optional[Toxicity | None] = None
    bioassays: Optional[list[int]] = []


class CompoundManyNewResponse(BaseModel):
    compounds: list[PubChemOutputWithBioassayIds]
    bioassays: dict[int, Bioassay]

class PubchemList(BaseModel):
    name: str
    cid: int
    smiles: str
    inchikey: str
    mapped_name: str
