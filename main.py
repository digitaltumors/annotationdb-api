import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from routes.drugs import router as drugs_router
from routes.cell_lines import router as cell_lines_router
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv(override=True)

DESCRIPTION = f"""
This API is developed and maintained by the <a href="https://bhklab.ca" target="_blank">Benjamin Haibe-Kains lab</a> \n

The AnnotationDB API serves as a tool to retrieve annotations for various compounds and cell lines. The stored compounds
and cell lines have either been used in datasets produced by the Haibe-Kains lab or have been requested by close
collaborators. Our annotations are timestamped and only updated after every 6-8 months. Once a full database update has concluded,
toggles to older versions will be available to ensure transparency and version control.

Note, AnnotationDB is made up of two major internal components
<ol>
	<li>A SQL database of compound and cell line annotations</li>
    <li>This Rest API that interfances with the SQL database for annotation data</li>
</ol>

<strong>Compound annotations</strong> along with accompanying bioassay and toxicity fields are stored directly from
<a href="https://pubchem.ncbi.nlm.nih.gov/docs/programmatic-access" target="_blank">Pubchem</a>.
Compound mechnanism/MOA fields are stored directly from
<a href="https://www.ebi.ac.uk/chembl/api/data/docs" target="_blank">ChEMBL</a>.
All <strong>cell line annotation</strong> fields are stored directly from
<a href="https://api.cellosaurus.org/api-methods" target="_blank"> cellosaurus</a>.

There are two sets of compound and cell line GET routes that work almost identically. The first routes are the
<strong>/all</strong> routes which simply list out all the compounds or cell lines stored in the database.

<ol>
	<li>
		Compound specific route: <a href="{os.getenv("URL_PREFIX")}/compound/all" target="_blank"><code>{os.getenv("URL_PREFIX")}/compound/all</code></a>
    </li>
    <li>
    	Cell line specific route: <a href="{os.getenv("URL_PREFIX")}/cell_line/all" target="_blank" class="code-block"><code>{os.getenv("URL_PREFIX")}/cell_line/all</code></a>
    </li>
</ol>

The second pair of routes are the <strong>/many</strong> routes which retrieve the full annotation data for either compounds
or cell lines stored in the database. These routes require one or more additional parameters in the GET request.

<ol>
	<li>
    	Compound specific route: <a href="{os.getenv("URL_PREFIX")}/compound/many?compounds=Aspirin,59174488&format=json&bioassay=false&mechanism=false&toxicity=false" target="_blank"><code>{os.getenv("URL_PREFIX")}/compound/many?compounds=Aspirin,59174488&format=json&bioassay=false&mechanism=false&toxicity=false</code></a>
        <ul>
        	<li><strong>Mandatory</strong>: Compound identifiers go after the <span><code>compounds=</code></span> comma separated without spaces</li>
            <li><strong>Optional</strong>: Only json can be placed after <span><code>format=</code></span> but the option for tabular output will be <i>available soon</i> </li>
            <ul><li><strong>Default value</strong>: json</li></ul>
            <li><strong>Optional</strong>: true/false goes after <span><code>bioassay=</code></span> to toggle populating the array of homo sapien bioassays related to the compound(s)</li>
			<ul><li><strong>Default value</strong>: false</li></ul>
            <li><strong>Optional</strong>: true/false goes after <span><code>mechanism=</code></span> to toggle populating the mechanism(s) of action related to the compound(s)</li>
            <ul><li><strong>Default value</strong>: false</li></ul>
            <li><strong>Option</strong>: true/false goes after <span><code>toxicity=</code></span> to toggle populating the toxicity fields related to the compound(s) (this defaults to false)</li>
            <ul><li><strong>Default value</strong>: false</li></ul>
        </ul>
    </li>
    <li>
    	Cell line specific route: <a href="{os.getenv("URL_PREFIX")}/cell_line/many?cell_lines=HL-60,CVCL_2030&format=json" target="_blank"><code>{os.getenv("URL_PREFIX")}/cell_line/many?cell_lines=HL-60,CVCL_2030&format=json</code></a>
		<ul>
        	<li><strong>Mandatory</strong>: Cell line identifiers go after the <span><code>cell_lines=</code></span> comma separated without spaces</li>
            <li><strong>Optional</strong>: Only json can be placed after <span><code>format=</code></span> but the option for tabular output will be <i>available soon</i> </li>
            <ul><li><strong>Default value</strong>: json</li></ul>
        </ul>
    </li>
</ol>


    
Please forward any questions or concerns to <a href="mailto:annotationdb-help@bhklab.ca">annotationdb-help@bhklab.ca</a>
"""

app = FastAPI(
    title="AnnotationDB API",
    description=DESCRIPTION,
    version="0.1.0",
    docs_url=None,
)

app.include_router(drugs_router)
app.include_router(cell_lines_router)

app.mount("/styling", StaticFiles(directory="styling"), name="styling")


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="AnnotationDB Docs",
        swagger_favicon_url="/assets/favicon.ico",
        swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
        swagger_js_url="/styling/swagger.js",
        swagger_css_url="/styling/swagger.css",
    )


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
