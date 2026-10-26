from fastapi import APIRouter

router = APIRouter(prefix="/gene", tags=["Genes"])




@router.get(
    "/annotation-files",
    summary="Get the available gene annotation files used in curation pipelines",
    response_model=dict,
)
async def get_gene_annotations():

    annotation_files = [
        {
            "name": "Gencode v50 Annotations",
            "download_url": "https://storage.googleapis.com/annotationdb_pipeline_outputs/annotation_assets/gencode.v50.annotation.gtf.gz",
            "description": "A Annotation file containing the coordinates and structure of genes, transcripts, exons, UTRs, and coding sequences across the genome. In layman terminology it is the map of where genes are and how they're structured."
        },
        {
            "name": "Gencode v50 Metadata",
            "download_url": "https://storage.googleapis.com/annotationdb_pipeline_outputs/annotation_assets/gencode.v50.metadata.EntrezGene.gz",
            "description": "A cross-reference file mapping GENCODE gene/transcript IDs to NCBI Entrez Gene IDs. Used to translate between GENCODE's own ID system and Entrez IDs. This is often needed when integrating data from different databases or tools that expect one ID system over another."
        },
        {
            "name": "Gene to Ensembl",
            "download_url": "https://storage.googleapis.com/annotationdb_pipeline_outputs/annotation_assets/gene2ensembl.gz",
            "description": "An NCBI-provided mapping file linking Entrez Gene IDs to Ensembl gene, transcript, and protein IDs."
        },
        {
            "name": "Gene History",
            "download_url": "https://storage.googleapis.com/annotationdb_pipeline_outputs/annotation_assets/gene_history.gz",
            "description": "Records of genes that have been discontinued, replaced, or merged into other IDs over time. Used to resolve 'stale' or outdated gene IDs in older datasets so they can be mapped to their current, valid identifiers."
        }
    ]
    

    return {"annotation_files": annotation_files}


