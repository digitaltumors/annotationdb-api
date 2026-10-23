from pydantic import BaseModel
from typing import Optional
from models.pubchem import SubstanceOutput


class AdcList(BaseModel):
    adc_id: str
    adc_name: str
    adc_drug_name: str


class AdcIndication(BaseModel):
    id: int
    adc_id: str
    disease_name: str
    status: str
    trial_ids: Optional[str] = None
    approval_year: Optional[str] = None
    document: Optional[str] = None
    link: Optional[str] = None


# Fields shared by every ADCdb activity level.
class AdcActivityBase(BaseModel):
    activity_id: str
    adc_id: str
    standard_type: Optional[str] = None
    value: Optional[str] = None
    expression: Optional[str] = None


class AdcCellLineActivity(AdcActivityBase):
    method_description: Optional[str] = None
    in_vitro_disease: Optional[str] = None
    in_vitro_cell_line: Optional[str] = None
    cellosaurus_id: Optional[str] = None
    cellosaurus_link: Optional[str] = None


class AdcHumanClinicalActivity(AdcActivityBase):
    patients_enrolled: Optional[str] = None
    administration_dosage: Optional[str] = None
    nct_number: Optional[str] = None
    nct_link: Optional[str] = None
    clinical_status: Optional[str] = None
    clinical_description: Optional[str] = None
    primary_endpoint: Optional[str] = None
    other_endpoint: Optional[str] = None


class AdcPatientDerivedXenograftModelActivity(AdcActivityBase):
    method_description: Optional[str] = None
    in_vivo_model: Optional[str] = None


class AdcCellLineDerivedXenograftModelActivity(AdcActivityBase):
    method_description: Optional[str] = None
    in_vivo_model: Optional[str] = None
    in_vitro_disease: Optional[str] = None
    in_vitro_cell_line: Optional[str] = None
    cellosaurus_id: Optional[str] = None
    cellosaurus_link: Optional[str] = None


class AdcModelOrganismActivity(AdcActivityBase):
    method_description: Optional[str] = None
    in_vivo_model: Optional[str] = None


class AdcOutput(BaseModel):
    adc_id: str
    adc_drug_name: str
    adc_name: str
    adc_phase: str
    adc_drug_status: str
    adc_detail_url: str

    adc_brand_name: Optional[str] = None
    adc_synonyms: Optional[str] = None
    adc_organization: Optional[str] = None
    adc_drug_to_antibody_ratio: Optional[str] = None
    adc_structure: Optional[str] = None
    adc_therapeutic_target: Optional[str] = None
    adc_conjugate_type: Optional[str] = None
    adc_combination_type: Optional[str] = None
    adc_special_approvals: Optional[str] = None
    adc_pubchem_sid: Optional[int] = None
    adc_drugbank_id: Optional[str] = None
    adc_chembl_id: Optional[str] = None
    adc_drugmap_id: Optional[str] = None
    adc_ttd_id: Optional[str] = None
    adc_dresis_id: Optional[str] = None
    adc_chebi_id: Optional[str] = None
    adc_absorption: Optional[str] = None
    adc_distribution: Optional[str] = None
    adc_metabolism: Optional[str] = None
    adc_elimination: Optional[str] = None
    adc_toxicity: Optional[str] = None

    antibody_name: str
    antibody_id: Optional[str] = None
    antibody_organization: Optional[str] = None
    antibody_indication: Optional[str] = None
    antibody_synonyms: Optional[str] = None
    antibody_type: Optional[str] = None
    antibody_subtype: Optional[str] = None
    antibody_antigen_name: Optional[str] = None
    antibody_chembl_id: Optional[str] = None
    antibody_drugbank_id: Optional[str] = None
    antibody_drug_central_id: Optional[str] = None
    antibody_pdb_id: Optional[str] = None
    antibody_approval_date: Optional[str] = None
    antibody_brand_name: Optional[str] = None
    antibody_heavy_chain_sequence: Optional[str] = None
    antibody_heavy_chain_variable_domain: Optional[str] = None
    antibody_heavy_chain_constant_domain_1: Optional[str] = None
    antibody_heavy_chain_constant_domain_2: Optional[str] = None
    antibody_heavy_chain_constant_domain_3: Optional[str] = None
    antibody_heavy_chain_hinge_region: Optional[str] = None
    antibody_heavy_chain_cdr_1: Optional[str] = None
    antibody_heavy_chain_cdr_2: Optional[str] = None
    antibody_heavy_chain_cdr_3: Optional[str] = None
    antibody_light_chain_sequence: Optional[str] = None
    antibody_light_chain_variable_domain: Optional[str] = None
    antibody_light_chain_constant_domain: Optional[str] = None
    antibody_light_chain_cdr_1: Optional[str] = None
    antibody_light_chain_cdr_2: Optional[str] = None
    antibody_light_chain_cdr_3: Optional[str] = None

    payload_name: str
    payload_id: Optional[str] = None
    payload_synonyms: Optional[str] = None
    payload_targets: Optional[str] = None
    payload_structure: Optional[str] = None
    payload_formula: Optional[str] = None
    payload_isosmiles: Optional[str] = None
    payload_pubchem_cid: Optional[int] = None
    payload_inchi: Optional[str] = None
    payload_inchikey: Optional[str] = None
    payload_iupac_name: Optional[str] = None
    payload_pharmaceutical_properties: Optional[str] = None

    linker_name: str
    linker_id: Optional[str] = None
    linker_type: Optional[str] = None
    linker_antibody_linker_relation: Optional[str] = None
    linker_structure: Optional[str] = None
    linker_formula: Optional[str] = None
    linker_isosmiles: Optional[str] = None
    linker_pubchem_cid: Optional[int] = None
    linker_inchi: Optional[str] = None
    linker_inchikey: Optional[str] = None
    linker_iupac_name: Optional[str] = None
    linker_pharmaceutical_properties: Optional[str] = None

    antigen_id: Optional[str] = None
    antigen_name: Optional[str] = None
    antigen_gene_name: Optional[str] = None
    antigen_gene_id: Optional[str] = None
    antigen_uniprot_entry: Optional[str] = None
    antigen_hgnc_id: Optional[str] = None
    antigen_kegg_id: Optional[str] = None
    antigen_family: Optional[str] = None
    antigen_function: Optional[str] = None
    antigen_sequence: Optional[str] = None
    antigen_synonym: Optional[str] = None

    target_id: Optional[str] = None
    target_name: Optional[str] = None
    target_gene_name: Optional[str] = None
    target_gene_id: Optional[str] = None
    target_uniprot_entry: Optional[str] = None
    target_hgnc_id: Optional[str] = None
    target_kegg_id: Optional[str] = None
    target_family: Optional[str] = None
    target_function: Optional[str] = None
    target_sequence: Optional[str] = None
    target_synonym: Optional[str] = None

    # Joined property
    indications: Optional[list[AdcIndication] | None] = None
    cell_line_activity_data: Optional[list[AdcCellLineActivity] | None] = None
    human_clinical_activity_data: Optional[list[AdcHumanClinicalActivity] | None] = None
    patient_derived_xenograft_model_activity_data: Optional[
        list[AdcPatientDerivedXenograftModelActivity] | None
    ] = None
    cell_line_derived_xenograft_model_activity_data: Optional[
        list[AdcCellLineDerivedXenograftModelActivity] | None
    ] = None
    model_organism_activity_data: Optional[list[AdcModelOrganismActivity] | None] = None
    substance_data: Optional[SubstanceOutput] = None
    query_field: Optional[str] = None
