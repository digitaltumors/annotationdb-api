import os
from dotenv import load_dotenv

load_dotenv(override=True)

DESCRIPTION = f"""
This API is developed and maintained by the <a href="https://bhklab.ca" target="_blank">Benjamin Haibe-Kains lab</a>

The AnnotationDB API serves as a tool to retrieve annotations for various compounds and cell lines. The stored compounds
and cell lines have either been used in datasets produced by the Haibe-Kains lab or have been requested by close
collaborators. Our annotations are timestamped and only updated annually (every 12 months). Once a full database update has concluded,
toggles to older versions will be available to ensure transparency and version control.

Note, AnnotationDB is made up of two major internal components
<ol>
	<li>A SQL database of compound and cell line annotations</li>
    <li>This Rest API that interfaces with the SQL database for annotation data</li>
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
    	Compound specific route: <a href="{os.getenv("URL_PREFIX")}/compound/many?compound=Aspirin&compound=59174488&format=json&bioassay=true&mechanism=true&toxicity=true&golden_bioassay=true" target="_blank"><code>{os.getenv("URL_PREFIX")}/compound/many?compound=Aspirin&compound=59174488&format=json&bioassay=true&mechanism=true&toxicity=true&golden_bioassay=true</code></a>
        <ul>
        	<li><strong>Mandatory</strong>: Compound identifiers are taken as a repeated/multi-value query parameter. To query multiple compounds, use the <code>compound=</code> parameter repeatedly.</li>
            <li><strong>Optional</strong>: Only json can be placed after <code>format=</code>. <i>The option for tabular output will be available soon</i> </li>
            <ul><li><strong>Default value</strong>: json</li></ul>
            <li><strong>Optional</strong>: true/false goes after <code>bioassay=</code> to toggle populating the array of homo sapien bioassays related to the compound(s)</li>
			<ul><li><strong>Default value</strong>: false</li></ul>
            <li><strong>Optional</strong>: true/false goes after <code>golden_bioassay=</code> to toggle populating the array of only golden specific homo sapien bioassays related to the compound(s). The <code>bioassay=</code> parameter must be set to true for golden bioassays to be retrieved. </li>
			<ul><li><strong>Default value</strong>: false</li></ul>
            <li><strong>Optional</strong>: true/false goes after <code>mechanism=</code> to toggle populating the mechanism(s) of action related to the compound(s)</li>
            <ul><li><strong>Default value</strong>: false</li></ul>
            <li><strong>Option</strong>: true/false goes after <code>toxicity=</code> to toggle populating the toxicity fields related to the compound(s)</li>
            <ul><li><strong>Default value</strong>: false</li></ul>
        </ul>
    </li>
    <li>
    	Cell line specific route: <a href="{os.getenv("URL_PREFIX")}/cell_line/many?cell_lines=HL-60,CVCL_2030&format=json" target="_blank"><code>{os.getenv("URL_PREFIX")}/cell_line/many?cell_lines=HL-60,CVCL_2030&format=json</code></a>
		<ul>
        	<li><strong>Mandatory</strong>: Cell line identifiers go after the <code>cell_lines=</code>. The cell line list must be comma separated without spaces between items</li>
            <li><strong>Optional</strong>: Only json can be placed after <code>format=</code>. <i>The option for tabular output will be available soon</i> </li>
            <ul><li><strong>Default value</strong>: json</li></ul>
        </ul>
    </li>
</ol>


    
Please forward any questions or concerns to <a href="mailto:annotationdb-help@bhklab.ca">annotationdb-help@bhklab.ca</a>
"""
