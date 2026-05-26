from pydantic import BaseModel
from typing import Optional
from models.pubchem import SubstanceOutput

class AdcList(BaseModel):
    adc_id: str
    adc_name: str
    adc_drug_name: str

class AdcOutput(BaseModel):
    adc_id: str
    adc_drug_name: str
    adc_name: str
    adc_brand_name: str
    adc_phase: str
    adc_drug_status: str
    adc_detail_url: str
    adc_synonyms: str
    adc_organization: str
    adc_drug_to_antibody_ratio: str
    adc_structure: str
    adc_therapeutic_target: str
    adc_conjugate_type: str
    adc_combination_type: str
    adc_special_approvals: str
    adc_pubchem_sid: Optional[int] = None
    adc_drugbank_id: str
    adc_chembl_id: str
    adc_absorption: str
    adc_distribution: str
    adc_metabolism: str
    adc_elimination: str
    adc_toxicity: str
    adc_drugmap_id: str
    adc_ttd_id: str
    adc_dresis_id: str

    antibody_id: str
    antibody_name: str
    antibody_organization: str
    antibody_indication: str
    antibody_synonyms: str
    antibody_type: str
    antibody_subtype: str
    antibody_antigen_name: str
    antibody_chembl_id: str
    antibody_heavy_chain_sequence: str
    antibody_heavy_chain_variable_domain: str
    antibody_heavy_chain_constant_domain_1: str
    antibody_heavy_chain_constant_domain_2: str
    antibody_heavy_chain_constant_domain_3: str
    antibody_heavy_chain_hinge_region: str
    antibody_heavy_chain_cdr_1: str
    antibody_heavy_chain_cdr_2: str
    antibody_heavy_chain_cdr_3: str
    antibody_light_chain_sequence: str
    antibody_light_chain_variable_domain: str
    antibody_light_chain_constant_domain: str
    antibody_light_chain_cdr_1: str
    antibody_light_chain_cdr_2: str
    antibody_light_chain_cdr_3: str

    payload_id: str
    payload_name: str
    payload_synonyms: str
    payload_targets: str
    payload_structure: str
    payload_formula: str
    payload_isosmiles: str
    payload_pubchem_cid: Optional[int] = None
    payload_inchi: str
    payload_inchikey: str
    payload_iupac_name: str
    payload_pharmaceutical_properties: str

    linker_id: str
    linker_name: str
    linker_type: str
    linker_antibody_linker_relation: str
    linker_structure: str
    linker_formula: str
    linker_isosmiles: str
    linker_pubchem_cid: Optional[int] = None
    linker_inchi: str
    linker_inchikey: str
    linker_iupac_name: str
    linker_pharmaceutical_properties: str

    # Joined property
    substance_data: Optional[SubstanceOutput] = None
    query_field: Optional[str] = None