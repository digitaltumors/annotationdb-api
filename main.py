from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from routes.drugs import router as drugs_router
from routes.cell_lines import router as cell_lines_router
from fastapi.staticfiles import StaticFiles

DESCRIPTION = """
This API is developed and maintained by the <a href="https://bhklab.ca" target="_blank">Benjamin Haibe-Kains lab</a> \n

The AnnotationDB API serves as a tool to retrieve annotations for various compounds and cell lines. The stored compounds
and cell lines have either been used in datasets produced by the Haibe-Kains lab or have been requested by close
collaborators. Our annotations are timestamped and are only updated after every 6-8 months. Once a full database update has concluded,
toggles to older versions will be available to ensure transparency and version control.

Note, AnnotationDB is made up of two major internal components
<ol>
	<li>A SQL database of compound and cell line annotations</li>
    <li>This Rest API that interfances with the SQL database for annotation data</li>
</ol>

<strong>Compound annotations</strong> along with accompanying bioassay and toxicity fields are stored directly from
<a href="https://pubchem.ncbi.nlm.nih.gov/" target="_blank">Pubchem</a>. Compound mechnanism/MOA fields are stored directly from
<a href="https://www.ebi.ac.uk/chembl/" target="_blank">ChEMBL</a>. All <strong>cell line annotation</strong>
fields are stored directly from cellosaurus.

There are two sets of compound and cell line GET routes that work almost identically. The first routes are the
<strong><i>/all</i></strong> routes which simply list out all the compounds or cell lines stored in the database.

<ol>
	<li>
		Compound specific route: <a href='https://annotationdb.bhklab.ca/compound/all' target="_blank"><code>https://annotationdb.bhklab.ca/compound/all</code></a>
    </li>
    <li>
    	Cell line specific route: <a href='https://annotationdb.bhklab.ca/cell_line/all' target="_blank" class="code-block"><code>https://annotationdb.bhklab.ca/cell_line/all</code></a>
    </li>
</ol>

The second pair of routes are the <strong><i>/many</i></strong> routes which retrieve the full annotation data for either compounds
or cell lines stored in the database. These routes require one or more additional parameters in the GET request. Specifically, you must
pass identifier(s) for the compounds or cell lines you want to search the database for.

Note: in the queries below, compound identifiers comes after the compounds= and the cell line identifiers come after cell_line=

<ol>
	<li>
    	Compound specific route: <a href='https://annotationdb.bhklab.ca/compound/many?compounds=Aspirin,59174488&format=json&bioassay=false&mechanism=false&toxicity=false' target="_blank"><code>https://annotationdb.bhklab.ca/compound/many?compounds=Aspirin,59174488&format=json&bioassay=false&mechanism=false&toxicity=false</code></a>
    </li>
    <li>
    	Cell line specific route: <a href='https://annotationdb.bhklab.ca/cell_line/many?cell_lines=HL-60,CVCL_2030&format=json' target="_blank"><code>https://annotationdb.bhklab.ca/cell_line/many?cell_lines=HL-60,CVCL_2030&format=json</code></a>
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
