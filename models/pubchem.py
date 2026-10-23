from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class Toxicity(BaseModel):
    pubchem_cid: int
    tox_dataset: str
    dili_severity_grade: Optional[int] = None
    dili_annotation: Optional[str] = None
    tox_source_url: Optional[str] = None
    hepatotoxicity_likelihood_score: Optional[str] = None
    hepatotoxicity_likelihood_score_reasoning: Optional[str] = None


class DIRIL_Toxicity(BaseModel):
    pubchem_cid: int
    description: str
    product_name: str
    product_date: str
    product_country: str
    label_gong: str
    label_shi: str
    toxicity: str


class DICT_Rank_Toxicity(BaseModel):
    pubchem_cid: int
    trade_name: str
    active_ingredients: str
    cardiotoxicity: str
    label_section: str
    dic_severity_level: str
    dict_concern: str
    keywords: str


# One DailyMed Structured Product Label (SPL) per approved drug (ChEMBL max_phase == 4)
class DailyMedLabel(BaseModel):
    pubchem_cid: int
    molecule_chembl_id: Optional[str] = None
    # How the drug was matched to DailyMed
    unii: Optional[str] = None
    unii_source: str
    search_tier: str
    candidate_count: int
    # The chosen label (view it at https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=<setid>)
    setid: str
    spl_title: str
    spl_version: int
    published_date: Optional[date] = None
    document_type: str
    marketing_category: Optional[str] = None
    application_number: Optional[str] = None
    active_moiety_uniis: Optional[str] = None
    is_single_ingredient: bool
    label_format: str
    # Label data
    boxed_warning: Optional[str] = None
    warnings_and_precautions: Optional[str] = None
    adverse_reactions: Optional[str] = None


class Bioassay(BaseModel):
    aid: int
    version: Optional[int] = None
    assay_name: Optional[str] = None
    source_name: Optional[str] = None
    source_id: Optional[str] = None
    description_combined: Optional[str] = None
    protocol_combined: Optional[str] = None
    comment_combined: Optional[str] = None
    activity_outcome_method: Optional[int] = None
    target_name: Optional[str] = None
    target_protein_accession: Optional[str] = None


class Mechanism(BaseModel):
    molecule_chembl_id: str
    parent_molecule_chembl_id: Optional[str] = None
    child_molecule_chembl_id: Optional[str] = None
    action_type: str
    binding_site_comment: str
    mechanism_of_action: str
    mechanism_comment: str
    direct_interaction: int
    disease_efficacy: int
    max_phase: int
    mec_id: int
    mechanism_refs: str
    molecular_mechanism: int
    record_id: int
    selectivity_comment: str
    site_id: str
    target_chembl_id: str
    target_name: str

    # Fields below are extracted from the variant sequence object (if it exists [likely does not])
    variant_sequence_accession: str
    variant_sequence_isoform: int
    variant_sequence_mutation: str
    variant_sequence_organism: str
    variant_sequence_sequence: str
    variant_sequence_tax_id: int
    variant_sequence_version: int
    source: str
    inferred_from_parent: bool
    inferred_from_child: bool = False


class DrugIndication(BaseModel):
    molecule_chembl_id: str
    parent_molecule_chembl_id: Optional[str] = None
    child_molecule_chembl_id: Optional[str] = None
    drugind_id: int
    max_phase_for_ind: Optional[str] = None
    mesh_id: str
    mesh_heading: str
    efo_id: Optional[str] = None
    efo_term: Optional[str] = None
    clinical_trials_ref_ids: Optional[str] = None
    daily_med_ref_ids: Optional[str] = None
    ema_ref_ids: Optional[str] = None
    fda_ref_ids: Optional[str] = None
    usan_ref_ids: Optional[str] = None
    inn_ref_ids: Optional[str] = None
    inferred_from_parent: bool = False
    inferred_from_child: bool = False


class PubchemOutput(BaseModel):
    cid: int
    title: str
    mapped_name: str
    molecule_chembl_id: Optional[str] = None
    molecule_chembl_id_from_synonyms: Optional[bool] = False
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
    chembl_max_phase: int
    drug_like: bool
    fda_approval: bool
    date_added: datetime
    atc_code: Optional[str] = None

    # ORM relationship fields
    mechanisms: Optional[list[Mechanism] | None] = None
    drug_indications: Optional[list[DrugIndication] | None] = None
    bioassays: Optional[list[Bioassay] | None] = None
    toxicity: Optional[list[Toxicity]] = None
    diril_toxicity: Optional[DIRIL_Toxicity | None] = None
    dict_rank_toxicity: Optional[DICT_Rank_Toxicity | None] = None
    dailymed_label: Optional[DailyMedLabel | None] = None
    query_field: Optional[str] = None


class PubChemOutputWithBioassayIds(BaseModel):
    cid: int
    title: str
    mapped_name: str
    molecule_chembl_id: Optional[str] = None
    molecule_chembl_id_from_synonyms: Optional[bool] = False
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
    chembl_max_phase: int
    drug_like: bool
    fda_approval: bool
    date_added: datetime

    # ORM relationship fields
    mechanisms: Optional[list[Mechanism] | None] = None
    drug_indications: Optional[list[DrugIndication] | None] = None
    toxicity: Optional[list[Toxicity]] = None
    diril_toxicity: Optional[DIRIL_Toxicity | None] = None
    dict_rank_toxicity: Optional[DICT_Rank_Toxicity | None] = None
    dailymed_label: Optional[DailyMedLabel | None] = None
    bioassays: Optional[list[int]] = []
    query_field: Optional[str] = None


class CompoundManyNewResponse(BaseModel):
    compounds: list[PubChemOutputWithBioassayIds]
    bioassays: dict[int, Bioassay]


class CompoundList(BaseModel):
    name: str
    cid: int
    smiles: str
    inchikey: str
    mapped_name: str


class SubstanceToxicityOutput(BaseModel):
    sid: int
    tox_dataset: str
    dili_severity_grade: Optional[int] = None
    dili_annotation: Optional[str] = None
    tox_source_url: Optional[str] = None
    hepatotoxicity_likelihood_score: Optional[str] = None
    hepatotoxicity_likelihood_score_reasoning: Optional[str] = None


class SubstanceOutput(BaseModel):
    sid: int
    title: str
    mapped_name: str
    molecule_chembl_id: Optional[str] = None
    chembl_max_phase: int

    # ORM relationship fields
    mechanisms: Optional[list[Mechanism] | None] = None
    drug_indications: Optional[list[DrugIndication] | None] = None
    toxicity: Optional[list[SubstanceToxicityOutput]] = None
    query_field: Optional[str] = None


class SubstanceList(BaseModel):
    name: str
    sid: int
    mapped_name: str
