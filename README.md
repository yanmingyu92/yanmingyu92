<div align="center">

<img alt="Jaime Yan, PhD — Clinical Data Science · Statistical Programming Leader. Kaplan-Meier curves and a DNA helix of data points." src="./dist/banner.svg" width="100%">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./dist/neofetch-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./dist/neofetch-light.svg">
  <img alt="Neofetch-style terminal card: Jaime Yan, PhD — Associate Director, Statistical Programming. R, Python, SQL, SAS; CDISC, GxP, LLM/RAG." src="./dist/neofetch-dark.svg" width="100%">
</picture>

<br/>

[![Website](https://img.shields.io/badge/jaimeyan.com-0A66C2?style=flat-square&logo=googlechrome&logoColor=white)](https://jaimeyan.com) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jaime-y-66312a133/) [![Google Scholar](https://img.shields.io/badge/Google_Scholar-4285F4?style=flat-square&logo=googlescholar&logoColor=white)](https://scholar.google.com/citations?user=vo1hv04AAAAJ&hl=en) [![py4csr on PyPI](https://img.shields.io/pypi/v/py4csr?style=flat-square&label=py4csr&logo=pypi&logoColor=white&color=3775A9)](https://pypi.org/project/py4csr/) [![r-universe](https://img.shields.io/badge/r--universe-yanmingyu92-276DC3?style=flat-square&logo=r&logoColor=white)](https://yanmingyu92.r-universe.dev)

</div>

### Hi, I'm Jaime 👋

I lead statistical programming for clinical trials and build **open, validated tooling for clinical data science**. I care most about analytics that regulators and reviewers can trust: reproducible R and Python pipelines, CDISC-native data, and AI that runs inside the GxP boundary rather than around it.

- 🏛️ **Associate Director, Statistical Programming @ Kardigan.** I lead programming for the tonlamarsen cardiovascular program and run a 21-service governed clinical analytics platform.
- 💊 **At Merck,** I was NDA statistical programming lead for **LIPFENDRA® (enlicitide)** from Phase 2b through the pivotal CORALreef program. It was FDA-approved in July 2026.
- 🤖 I architected an enterprise **GenAI (LLM/RAG) platform**; its SAS-to-R conversion tooling was adopted organization-wide.
- 🎓 **PhD in Data Science (2026)** on AI/ML governance in clinical development. I am sole author of 4 journal papers and author of 13 PhUSE/PharmaSUG papers.
- 🔭 **Currently exploring** digital protocols with CDISC **USDM** and ICH M11 ([usdm-toolkit](https://github.com/yanmingyu92/usdm-toolkit)).

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./dist/impact-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./dist/impact-light.svg">
  <img alt="By the numbers: 9+ years in Phase 1–3; 1 FDA approval as NDA lead; 4 sole-author journal papers; 13 PhUSE/PharmaSUG papers; 85+ technical articles." src="./dist/impact-dark.svg" width="100%">
</picture>
</p>

---

### 🧭 How I work: protocol to submission

```mermaid
flowchart LR
    P["Protocol & SAP<br/>USDM · ICH M11"] --> S["SDTM"]
    S --> A["ADaM<br/>admiral · admiralagent"]
    A --> T["TLFs<br/>tlfstack · py4csr"]
    T --> E["eSubmission<br/>Define-XML · eCTD · ADRG"]
    AI(["🤖 LLM agents + validation gates"]) -.-> A
    AI -.-> T
    G(["🛡️ GxP: validation · audit trail · Part 11"]) -.-> S
    G -.-> E
    classDef core fill:#0f766e,stroke:#2dd4bf,color:#ffffff
    classDef layer fill:#4c1d95,stroke:#a78bfa,color:#ffffff
    class P,S,A,T,E core
    class AI,G layer
```

---

### 🔬 Featured work

<table>
<tr>
<td width="33%" valign="top">

**[py4csr](https://github.com/yanmingyu92/py4csr)**
<sub>Python · MIT · on PyPI</sub>

A Python framework for clinical study reporting: CDISC-aware tables, listings and figures for CSRs.

`pip install py4csr`

</td>
<td width="33%" valign="top">

**[shiny-gxp-governance](https://github.com/yanmingyu92/shiny-gxp-governance)**
<sub>R/Shiny · MIT</sub>

A governance and validation template for R/Shiny in GxP settings: roles, control gates, risk-tiered validation, QC procedures and a 21 CFR Part 11 mapping.

</td>
<td width="33%" valign="top">

**[clinical-figure-library](https://github.com/yanmingyu92/clinical-figure-library)**
<sub>R + Python · source-available</sub>

Reproducible clinical trial figure templates (forest, waterfall, KM and more) with synthetic data and independent numerical QC. [Live gallery →](https://jaimeyan.com/lab/figures.html)

</td>
</tr>
<tr>
<td valign="top">

**[clinical-r-in-practice](https://yanmingyu92.github.io/clinical-r-in-practice/)**
<sub>Quarto book · CC BY-SA 4.0</sub>

A free 15-chapter book on the open-source R stack in regulated drug development: pharmaverse, ADaM, ARD, validation and LLM agents.

</td>
<td valign="top">

**[admiralagent](https://github.com/yanmingyu92/admiralagent)** · **[tlfstack](https://github.com/yanmingyu92/tlfstack)**
<sub>R packages · r-universe</sub>

Spec-driven ADaM code generation with LLM-translated layers, and convention-driven RTF TLFs with one code path for batch and interactive use.

</td>
<td valign="top">

**[clinprog-bench](https://github.com/yanmingyu92/clinprog-bench)** · **[CAVE-Onc](https://github.com/yanmingyu92/CAVE-Onc-Benchmark)**
<sub>Benchmarks · Python</sub>

Public benchmarks for clinical statistical-programming automation, plus graph-constrained agentic validation of CDISC oncology submissions.

</td>
</tr>
</table>

<details>
<summary><b>More open-source work</b></summary>
<br/>

| Project | What it does |
|---|---|
| [rval-gateway](https://github.com/yanmingyu92/rval-gateway) | R package validation gateway: riskmetric screening, decision engine and audit chain |
| [gxp-sce](https://github.com/yanmingyu92/gxp-sce) | *The GxP Statistical Computing Environment*: a review and practitioner's guide (CC BY-SA 4.0) |
| [eSubmission-Benchmark](https://github.com/yanmingyu92/eSubmission-Benchmark) | Public benchmark submission package (SDTM, ADaM, Define-XML, TLFs) cited at PharmaSUG 2026 |
| [clinical-reporting-ir](https://github.com/yanmingyu92/clinical-reporting-ir) | Typed IR schema and parity-validation harness for the Frontiers in Pharmacology paper |
| [sop-knowledge-graph](https://github.com/yanmingyu92/sop-knowledge-graph) | Six-stage pipeline turning pharmaceutical SOPs into a knowledge graph and web explorer |
| [posit-conf-2026-bilingual](https://github.com/yanmingyu92/posit-conf-2026-bilingual) | *Modern R in Practice / 现代 R 进阶*: a 28-chapter bilingual book with companion labs |
| [usdm-toolkit](https://github.com/yanmingyu92/usdm-toolkit) | Toolchain for CDISC USDM / ICH M11 digital protocols |
| [ragql-nav](https://github.com/yanmingyu92/ragql-nav) | Multi-agent framework routing natural-language clinical data questions to SQL or Neo4j |

</details>

---

### 📄 Selected publications (sole author, 2026)

- *Workflow topology–guided skill loading for agentic AI in clinical trial data pipelines: sequential exploratory evaluation.* **JMIR Formative Research**, 2026. [doi:10.2196/100769](https://doi.org/10.2196/100769)
- *A non-destructive methodological framework for modernizing legacy clinical reporting systems for AI-driven pharmacoinformatics: a SAS case study.* **Frontiers in Pharmacology**, 2026. [doi:10.3389/fphar.2026.1876207](https://doi.org/10.3389/fphar.2026.1876207) · [code](https://github.com/yanmingyu92/clinical-reporting-ir)
- *CAVE-Onc: graph-constrained agentic validation for cross-domain contradictions in CDISC oncology submissions.* **PLOS ONE**, 2026. [doi:10.1371/journal.pone.0350376](https://doi.org/10.1371/journal.pone.0350376) · [code](https://github.com/yanmingyu92/CAVE-Onc-Benchmark)
- *ClinAgent: AI-assisted methodology for clinical trial data processing and statistical programming.* **Biology Methods and Protocols** (Oxford University Press), 2026. [doi:10.1093/biomethods/bpag032](https://doi.org/10.1093/biomethods/bpag032)

<sub>Plus 13 PhUSE / PharmaSUG conference papers (2023–2026). Full list on <a href="https://scholar.google.com/citations?user=vo1hv04AAAAJ&hl=en">Google Scholar</a>.</sub>

---

### ✍️ Latest writing

<!-- FEED:START -->
- [AI in Validated Environments: LLMs Inside the GxP Boundary](https://jaimeyan.com/blog/ai-in-validated-environments.html) <sub>· Nov 04, 2026</sub>
- [Visit Windowing, Baseline, and LOCF: The Rules That Decide BDS](https://jaimeyan.com/blog/visit-windowing-baseline-locf-guide.html) <sub>· Nov 04, 2026</sub>
- [Define-XML and the Reviewer's Guide, Explained for Programmers](https://jaimeyan.com/blog/define-xml-reviewers-guide-tutorial.html) <sub>· Oct 26, 2026</sub>
- [How to Read a Protocol and SAP as a Statistical Programmer](https://jaimeyan.com/blog/protocol-sap-reading-guide.html) <sub>· Oct 26, 2026</sub>
- [Git for SAS Programmers: Version Control in a GxP World](https://jaimeyan.com/blog/git-for-clinical-programmers.html) <sub>· Oct 06, 2026</sub>
<!-- FEED:END -->

<sub>From <a href="https://jaimeyan.com">jaimeyan.com</a>: 85+ practical articles on CDISC, R in pharma, GxP and LLM automation. <a href="https://jaimeyan.com/rss.xml">RSS</a></sub>

---

### 🧰 Toolbox

<a href="https://skillicons.dev"><img alt="Skills: R, Python, PostgreSQL, Docker, Linux, Git, GitHub Actions, FastAPI, LaTeX, VS Code" src="https://skillicons.dev/icons?i=r,py,postgres,docker,linux,git,githubactions,fastapi,latex,vscode&perline=10"></a>

![Shiny](https://img.shields.io/badge/Shiny-1A162D?style=flat-square&logo=rstudioide&logoColor=75AADB) ![Quarto](https://img.shields.io/badge/Quarto-39729E?style=flat-square&logo=quarto&logoColor=white) ![SAS](https://img.shields.io/badge/SAS_(certified)-0766D1?style=flat-square&logoColor=white) ![LLM / RAG](https://img.shields.io/badge/LLM%20%2F%20RAG-412991?style=flat-square&logo=openai&logoColor=white) ![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?style=flat-square&logo=neo4j&logoColor=white)

![CDISC](https://img.shields.io/badge/CDISC-SDTM%20%C2%B7%20ADaM%20%C2%B7%20Define--XML-005A9C?style=flat-square) ![pharmaverse](https://img.shields.io/badge/pharmaverse-admiral%20%C2%B7%20rtables-E35B2F?style=flat-square) ![GxP](https://img.shields.io/badge/GxP-21%20CFR%20Part%2011%20%C2%B7%20GAMP%205-2E7D32?style=flat-square) ![Submissions](https://img.shields.io/badge/Submissions-NDA%20%C2%B7%20eCTD%20%C2%B7%20ISS%2FISE-6A1B9A?style=flat-square)

<img alt="" src="./dist/footer.svg" width="100%">

<sub>All demos and benchmarks use synthetic or public test data (e.g. the CDISC Pilot). Views are my own and not those of any employer.</sub>
