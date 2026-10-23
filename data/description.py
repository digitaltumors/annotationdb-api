import os
from dotenv import load_dotenv

load_dotenv(override=True)

DESCRIPTION = f"""
This API is developed and maintained by the <a href="https://bhklab.ca" target="_blank">Benjamin Haibe-Kains lab</a>

<h2>Overview</h2>
<p>The AnnotationDB API serves as a tool to retrieve annotations for various compounds, substances, antibody-drug conjugates, and cell lines
pivotal for clear and reproducible cancer research. Our annotations are timestamped and only updated annually (every 12 months).
Once a full database update has concluded, toggles to older versions will be available to ensure transparency and version control.</p>

<p>AnnotationDB is made up of two major internal components:</p>
<ol>
	<li>A MySQL database focused primarily on compound, substance, antibody-drug conjugate (ADC), and cell line annotations</li>
    <li><strong>This REST API</strong> that interfaces with the MySQL database for annotation data</li>
</ol>

<strong>Compound annotations</strong> along with accompanying bioassay, toxicity, and Anatomical Therapeutic Classification codes (ATCs)
fields are retrieved directly from
<a href="https://pubchem.ncbi.nlm.nih.gov/docs/programmatic-access" target="_blank" rel="noopener noreferrer">Pubchem's REST/View API</a>.
<strong>Compound mechanisms of actions (MOAs)</strong> are retrieved directly from
<a href="https://www.ebi.ac.uk/chembl/api/data/docs" target="_blank" rel="noopener noreferrer">ChEMBL's REST API</a>.
<strong>Antibody-drug conjugates (ADCs)</strong> have been programatically scraped from
<a href="https://adcdb.idrblab.net/" target="_blank" rel="noopener noreferrer">ADCdb</a>.
<strong>Cell line annotations</strong> are retrieved directly from
<a href="https://api.cellosaurus.org/api-methods" target="_blank" rel="noopener noreferrer">Cellosaurus' REST API</a>.


<h2>Technical Details</h2>
<p>There are seven subsets of GET routes in AnnotationDB. The <strong>Compounds</strong>, <strong>Substances</strong>, <strong>Chemicals</strong>, and <strong>Cell Lines</strong> routes work almost identically.
They all accept an unique idenifier for the respective annotation, then return the metadata associated (if it exists) in JSON.

<h3>/all Routes</h3>
<p>
	These routes provide all available identifiers for the various compounds, substances, cell lines, and antibody-drug
	conjugates in our database.
</p>

<ol>
	<li>
		Compound route: <a href="{os.getenv("URL_PREFIX")}/compound/all" target="_blank"><code>{os.getenv("URL_PREFIX")}/compound/all</code></a>
    </li>
	<li>
		Substance route: <a href="{os.getenv("URL_PREFIX")}/substance/all" target="_blank"><code>{os.getenv("URL_PREFIX")}/substance/all</code></a>
    </li>
    <li>
    	Antibody-drug conjugate route: <a href="{os.getenv("URL_PREFIX")}/adc/all" target="_blank" ><code>{os.getenv("URL_PREFIX")}/adc/all</code></a>
    </li>
	<li>
    	Cell line route: <a href="{os.getenv("URL_PREFIX")}/cell_line/all" target="_blank" ><code>{os.getenv("URL_PREFIX")}/cell_line/all</code></a>
    </li>
</ol>

<h3>/many Routes</h3>
<p>
	These routes provide full annotation data for compounds, substances, cell lines, and antibody-drug conjugates via identifiers
	retrieved from respective <code>/all</code> routes. Some of these routes accept additional paramaters which will include
	or disclude additional annotation data for mechanisms, toxicity, and bioassays.
	
</p>
<ol>
	<li>
		Compound route example (Acetaminophen): <a href="{os.getenv("URL_PREFIX")}/compound/many?compound=Acetaminophen&bioassay=true&mechanism=true&toxicity=true&golden_bioassay=true" target="_blank"><code>{os.getenv("URL_PREFIX")}/compound/many?compound=Acetaminophen&bioassay=true&mechanism=true&toxicity=true&golden_bioassay=true</code></a>
    </li>
	<li>
		Substance route example (Bevacizumab): <a href="{os.getenv("URL_PREFIX")}/substance/many?substance=Bevacizumab&mechanism=true&toxicity=true" target="_blank"><code>{os.getenv("URL_PREFIX")}/substance/many?substance=Bevacizumab&mechanism=true&toxicity=true</code></a>
    </li>
    <li>
    	Antibody-drug conjugate route example (DRG0AAJTS): <a href="{os.getenv("URL_PREFIX")}/adc/many?adc=DRG0AAJTS" target="_blank" ><code>{os.getenv("URL_PREFIX")}/adc/many?adc=DRG0AAJTS</code></a>
    </li>
	<li>
    	Cell line route example (HL-60): <a href="{os.getenv("URL_PREFIX")}/cell_line/many?cell_lines=HL-60" target="_blank" ><code>{os.getenv("URL_PREFIX")}/cell_line/many?cell_lines=HL-60</code></a>
    </li>
</ol>

<h3>/atc/overlap Route</h3>

<p>
	This route takes two atc code parameters and produces the levels of overlap. Read WHO's
	<a href="https://www.who.int/tools/atc-ddd-toolkit/atc-classification" target="_blank" rel="noopener noreferrer">classification toolkit</a>
	to get an understanding of the provided results. <strong>Due to the WHO's policy, you must request a key through our contact email
	to access the response data.</strong>
</p>
<p>
	
</p>
<ol>
	<li>
		ATC overlap route example (A01AB04 and A01AB10): <a href="{os.getenv("URL_PREFIX")}/atc/overlap?atc%20code%201=A01AB04&atc%20code%202=A01AB10" target="_blank"><code>{os.getenv("URL_PREFIX")}/atc/overlap?atc%20code%201=A01AB04&atc%20code%202=A01AB10</code></a>
    </li>
</ol>


<h3>/gene/annotation-files Route</h3>

<p>
	This route produces download links for the Gencode and Ensembl gene annotations our team uses in curated datasets.
</p>
<ol>
	<li>
		Gene annotation files route: <a href="{os.getenv("URL_PREFIX")}/gene/annotation-files" target="_blank"><code>{os.getenv("URL_PREFIX")}/gene/annotation-files</code></a>
    </li>
</ol>


<h2>Additional Parameter Dictionary</h2>

For the compound, substance, and chemical <code>/many</code> routes, the following parameters can be toggled
on or off (off by default) to include additional annotation data, as show in the Technical Details section above.

<ul>
    <li><code>mechanism=</code>: true/false field which decides whether to include the mechanism(s) of action related to the compound(s) queried for</li>
    <ul><li><strong>Default value</strong>: false</li></ul>
    <li><code>indication=</code>: true/false field which decides whether to include the indication(s) related to the compound(s)/substance(s)/ADC(s) queried for</li>
    <ul><li><strong>Default value</strong>: false</li></ul>
    <li><code>toxicity=</code>: true/false field which decides whether to include the toxicity fields related to the compound(s) queried for</li>
    <ul><li><strong>Default value</strong>: false</li></ul>
    <li><code>label=</code>: true/false field which decides whether to include the DailyMed drug label (boxed warning, warnings and precautions, adverse reactions) of the FDA approved compound(s) queried for</li>
    <ul><li><strong>Default value</strong>: false</li></ul>
	<li><code>bioassay=</code>: true/false field which decides whether to include the list of homo sapien bioassays related to the compound(s) queried for</li>
    <ul><li><strong>Default value</strong>: false</li></ul>
    <li><code>golden_bioassay=</code>: true/false field which decides whether to include the list of only our internal
	<a href="https://github.com/bhklab/pcba_qc" target="_blank" rel="noopener noreferrer">gold standard homo sapien bioassays</a>
	related to the compound(s) queried for</li>
    <ul><li><strong>Default value</strong>: false</li></ul>
</ul>


<h2>Annotation References</h2>
<ul>
<li>Compound/Substance Annotations</li>
	<ul>
	<li>Pubchem</li>
	<ul>
		<li>
			<a href="https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest-tutorial#section=How-PUG-REST-Works" target="_blank" rel="noopener noreferrer">REST (Compounds/Substances/Bioassays)</a>
		</li>
		<li>
			<a href="https://pubchem.ncbi.nlm.nih.gov/docs/pug-view" target="_blank" rel="noopener noreferrer">View (Toxicity)</a>
		</li>
		<li>
			<a href="https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/ltkb-benchmark-dataset" target="_blank" rel="noopener noreferrer">Liver Toxicity Knowledge Database (LTKB)</a>
		</li>
		<li>
			<a href="https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/drug-induced-liver-injury-rank-dilirank-20-dataset" target="_blank" rel="noopener noreferrer">Drug Induced Liver Injury Rank (DILIrank 2.0)</a>
		</li>
		<li>
			<a href="https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb/drug-induced-liver-injury-severity-and-toxicity-dilist-dataset" target="_blank" rel="noopener noreferrer">Drug-Induced Liver Injury Severity and Toxicity (DILIst)</a>
		</li>
		<li>
			<a href="https://www.who.int/tools/atc-ddd-toolkit/atc-classification" target="_blank" rel="noopener noreferrer">Anatomical Therapeutic Classification codes (ATCs)</a>
		</li>
	</ul>
		<li>DailyMed</li>
		<ul>
			<li>
				<a href="https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm" target="_blank" rel="noopener noreferrer">DailyMed Drug Labels (Structured Product Labels)</a>
			</li>
		</ul>
		<li>ChEMBL</li>
		<ul>
			<li>
				<a href="https://www.ebi.ac.uk/chembl/explore/drug_mechanisms/" target="_blank" rel="noopener noreferrer">ChEMBL Drug Mechanism of Action (MOA)</a>
			</li>
			<li>
				<a href="https://www.ebi.ac.uk/chembl/explore/drug_indications/" target="_blank" rel="noopener noreferrer">ChEMBL Drug Indications</a>
			</li>
		</ul>
	</ul>
	<li>Antibody-Drug Conjugates</li>
	<ul>
		<li>
			<a href="https://adcdb.idrblab.net/" target="_blank" rel="noopener noreferrer">ADCdb</a>
		</li>
	</ul>
	<li>Cell Lines</li>
	<ul>
		<li>
			<a href="https://api.cellosaurus.org/api-methods" target="_blank" rel="noopener noreferrer">Cellosaurus' REST API</a>
		</li>
	</ul>

</ul>


<!-- <h2>Data Dictionary</h2> -->



<h2>Contact</h2>

Please forward any questions or concerns to <a href="mailto:annotationdb-help@bhklab.ca">annotationdb-help@bhklab.ca</a>
"""
