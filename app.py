
"""AegisIQ — AI-Assisted Evidence Assessment · NCA ECC.

Educational proof of concept using fictional hospital evidence.
Rule-based analysis; no automated compliance determinations.
"""

from html import escape
import csv
import hashlib
import io
import json
from pathlib import Path

import streamlit as st

from assessment_pipeline import run_assessment
from security_analyzer import analyze_security


st.set_page_config(
    page_title="AegisIQ | Compliance Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0B2639"
TEAL = "#328F96"
BACKGROUND = "#F7FAFB"

ALLOWED_EXTENSIONS = [
    "pdf", "docx", "xlsx", "csv", "json", "txt"
]
MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# DESIGN AND TYPOGRAPHY
# All CSS braces are doubled because this is a Python f-string.
# ============================================================

st.markdown(
    f"""
<style>

.stApp {{
    background: {BACKGROUND};
    color: #173548;
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1300px;
}}

[data-testid="stSidebar"] {{
    background: #FFFFFF;
    border-right: 1px solid #E2EBEF;
}}

h1, h2, h3 {{
    color: {NAVY} !important;
    letter-spacing: -0.5px;
}}

/* Hero */

.hero {{
    background: linear-gradient(
        120deg,
        #0B2639 0%,
        #173E50 72%,
        #22646B 100%
    );
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 25px;
    box-shadow: 0 12px 32px rgba(11,38,57,.10);
}}

.hero-label {{
    color: #8DDEDA;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 13px;
}}

.hero-title {{
    color: white;
    font-size: clamp(32px, 3vw, 42px);
    font-weight: 750;
    letter-spacing: -1px;
    line-height: 1.2;
    margin-bottom: 12px;
}}

.hero-description {{
    color: #D2E4E9;
    font-size: 17px;
    line-height: 1.8;
    max-width: 780px;
}}

.scope-badge {{
    display: inline-block;
    background: #E0F2F0;
    color: #155B61;
    border: 1px solid #B5DEDB;
    border-radius: 999px;
    padding: 9px 15px;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 13px;
}}

/* Section headings */

.section-label {{
    color: {TEAL};
    font-size: 14px;
    letter-spacing: 1.6px;
    font-weight: 750;
    text-transform: uppercase;
    margin-bottom: 12px;
}}

/* Feature cards */

.feature-card {{
    background: white;
    border: 1px solid #E1EAEE;
    border-radius: 16px;
    padding: 25px;
    min-height: 175px;
    margin-bottom: 15px;
}}

.feature-card h4 {{
    color: {NAVY};
    font-size: 20px;
    margin: 10px 0;
    font-weight: 700;
}}

.feature-card p {{
    color: #526D7B;
    font-size: 16px;
    line-height: 1.7;
    margin: 0;
}}

.step-number {{
    color: {TEAL};
    font-weight: 750;
    font-size: 14px;
}}

.status-ready {{
    color: #207C73;
    font-size: 14px;
    font-weight: 700;
}}

.status-planned {{
    color: #637B87;
    font-size: 14px;
    font-weight: 600;
}}

/* Upload area */

div[data-testid="stFileUploader"] {{
    background: white;
    border: 1px solid #D9E7EB;
    border-radius: 15px;
    padding: 12px;
}}

/* Tabs */

.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    border-bottom: 1px solid #DFE9ED;
}}

.stTabs [data-baseweb="tab"] {{
    color: #526D7B;
    font-weight: 600;
    font-size: 17px;
    padding: 12px 18px;
}}

.stTabs [aria-selected="true"] {{
    color: {NAVY} !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    background-color: {TEAL};
}}

/* Buttons */

.stButton button[kind="primary"] {{
    background: {NAVY};
    color: white;
    border-color: {NAVY};
    border-radius: 10px;
}}

/* Main body text */

[data-testid="stMain"] p,
[data-testid="stMain"] li {{
    font-size: 17px !important;
    line-height: 1.7 !important;
}}

/* Main headings */

[data-testid="stMain"] h1 {{
    font-size: 38px !important;
}}

[data-testid="stMain"] h2 {{
    font-size: 29px !important;
}}

[data-testid="stMain"] h3 {{
    font-size: 23px !important;
}}

/* Sidebar readability */

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {{
    font-size: 16px !important;
    line-height: 1.6 !important;
}}

/* Widgets and forms */

[data-testid="stWidgetLabel"] p,
[data-testid="stFileUploader"] p,
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {{
    font-size: 16px !important;
}}

/* Captions */

[data-testid="stCaptionContainer"] p,
[data-testid="stMain"] small {{
    font-size: 15px !important;
    line-height: 1.6 !important;
}}

/* Tables */

[data-testid="stTable"] {{
    font-size: 16px !important;
}}

/* Footer */

.footer {{
    color: #637B87;
    font-size: 15px;
    text-align: center;
    padding: 24px;
    line-height: 1.9;
}}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# REUSABLE COMPONENTS
# ============================================================

def card(number, title, description, status=None):
    status_html = ""

    if status:
        cls = (
            "status-ready"
            if status == "Available"
            else "status-planned"
        )

        status_html = (
            f'<div class="{cls}">'
            f'{escape(status)}'
            f'</div>'
        )

    st.markdown(
        f"""
<div class="feature-card">
    <div class="step-number">{escape(number)}</div>
    <h4>{escape(title)}</h4>
    <p>{escape(description)}</p>
    <div style="margin-top:12px">{status_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None

if "assessment_signature" not in st.session_state:
    st.session_state.assessment_signature = None

if "review_decisions" not in st.session_state:
    st.session_state.review_decisions = {}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    logo_path = Path(__file__).parent / "logo.png"

    if logo_path.is_file():
        st.image(
            str(logo_path),
            use_container_width=True,
        )
    else:
        st.title("AegisIQ")
        st.warning(
            "Save your logo as logo.png beside app.py."
        )

    st.caption("COMPLIANCE INTELLIGENCE")

    st.divider()

    st.markdown("### Workspace")

    st.write("Evidence Assessment")
    st.caption("Control Mapping — Pilot available")
    st.caption("Analyst Validation — Available")
    st.caption("Reporting — Available")

    st.divider()

    st.markdown("**Project status**")

    st.progress(6 / 7)

    st.caption(
        "6 of 7 development milestones implemented; "
        "deployment pending"
    )

    st.info(
        "DEMONSTRATION ENVIRONMENT\n\n"
        "Use simulated or sanitized documents only."
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="hero">
    <div class="hero-label">
        AEGISIQ / COMPLIANCE INTELLIGENCE
    </div>

    <div class="scope-badge">
        EDUCATIONAL PROOF OF CONCEPT ·
        SYNTHETIC DATA ·
        DEPARTMENT-SCOPED PILOT
    </div>

    <div class="hero-title">
        Evidence Assessment Workspace
    </div>

    <div class="hero-description">
        AI-Assisted Evidence Assessment · NCA ECC
        <br>
        A structured approach to cybersecurity compliance,
        evidence analysis, and human-validated risk findings.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SCOPE AND LIMITATIONS
# ============================================================

with st.expander(
    "Scope & Limitations — Read before interpreting findings",
    expanded=False,
):

    st.markdown(
        """
**Project scope**

AegisIQ is an independent educational proof of concept.

It uses entirely fictional hospital records modeled around
one Obstetrics and Gynecology (OB/GYN) department.

It is not connected to any real hospital or clinical
information system.

**What this pilot demonstrates**

- Local document extraction.
- Rule-based comparison of selected structured evidence.
- Preliminary observations mapped to selected NCA Essential
  Cybersecurity Controls (ECC).
- Analyst review and justification.
- Structured report exports.

**What it does not demonstrate**

- Enterprise-wide hospital coverage.
- Complete ECC compliance assessment.
- Integration with live hospital systems.
- Validated large-language-model reasoning.
- Automated regulatory compliance decisions.

An observation is not proof of a compliance violation.

**Real-world deployment considerations**

A hospital-wide implementation would require organizational
ownership and access models, secure system integrations,
broader validated control coverage, privacy protections,
comprehensive testing, and appropriate approvals.

**Use restrictions**

Do not upload real patient information, credentials, or
confidential organizational evidence.

This pilot is for demonstration and learning only.
"""
    )


# ============================================================
# FEATURE CARDS
# ============================================================

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    card(
        "01 / EVIDENCE",
        "Document Intake",
        "Collect simulated policies, procedures, and "
        "supporting compliance documents.",
        "Available",
    )

with c2:
    card(
        "02 / ASSESSMENT",
        "Intelligent Analysis",
        "Map evidence to verified control requirements "
        "and propose findings.",
        "Pilot available",
    )

with c3:
    card(
        "03 / OVERSIGHT",
        "Human Validation",
        "Review proposed observations and record "
        "analyst decisions with justifications.",
        "Available",
    )


# ============================================================
# MAIN NAVIGATION
# ============================================================

tab_evidence, tab_analysis, tab_workflow = st.tabs(
    [
        "Evidence Workspace",
        "Assessment Engine",
        "Workflow & Reporting",
    ]
)


# ============================================================
# TAB 1 — EVIDENCE WORKSPACE
# ============================================================

with tab_evidence:

    st.write("")

    st.markdown(
        '<div class="section-label">Layer 01 / Input</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Evidence Management")

    st.caption(
        "Upload fictional organizational documents to prepare "
        "a cybersecurity compliance assessment."
    )

    main_col, info_col = st.columns(
        [2.1, 1],
        gap="large",
    )

    with main_col:

        st.markdown("#### Upload documents")

        uploaded_files = st.file_uploader(
            "Choose one or more evidence files",
            type=ALLOWED_EXTENSIONS,
            accept_multiple_files=True,
            help=(
                "Maximum 10 MB per file "
                "(validated by the application)."
            ),
        )

        accepted_files = []

        for f in uploaded_files or []:

            extension = Path(f.name).suffix.lower()

            valid_extensions = {
                "." + ext
                for ext in ALLOWED_EXTENSIONS
            }

            if extension not in valid_extensions:
                st.error(
                    f"Unsupported format: {f.name}"
                )

            elif not f.size or f.size > MAX_FILE_SIZE:
                st.error(
                    "File must be non-empty and no larger "
                    f"than 10 MB: {f.name}"
                )

            else:
                accepted_files.append(f)

        signature = tuple(
            (
                f.name,
                hashlib.sha256(
                    f.getvalue()
                ).hexdigest(),
            )
            for f in accepted_files
        )

        if (
            signature
            != st.session_state.assessment_signature
        ):
            st.session_state.assessment_result = None
            st.session_state.assessment_signature = signature
            st.session_state.review_decisions = {}

        if not uploaded_files:

            st.info(
                "Your evidence inventory is empty. "
                "Upload a simulated document to begin."
            )

        elif accepted_files:

            st.success(
                f"{len(accepted_files)} document(s) "
                "accepted for this session."
            )

            st.markdown("#### Evidence inventory")

            inventory = [
                {
                    "Document": f.name,
                    "Format": (
                        Path(f.name).suffix[1:].upper()
                    ),
                    "Size (KB)": round(
                        f.size / 1024, 1
                    ),
                    "Status": "Received",
                }
                for f in accepted_files
            ]

            st.dataframe(
                inventory,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown(
                "#### Document Processing Layer"
            )

            st.caption(
                "Inspect the extracted evidence and "
                "its original section references."
            )

            if st.button(
                "Process evidence & find potential matches",
                type="primary",
            ):

                with st.spinner(
                    "Extracting evidence and mapping "
                    "pilot controls..."
                ):

                    st.session_state.assessment_result = (
                        run_assessment(accepted_files)
                    )

            assessment = (
                st.session_state.assessment_result
            )

            if assessment is not None:

                for error in assessment[
                    "extraction_errors"
                ]:

                    st.error(
                        "Unable to process "
                        f"{error['filename']}: "
                        f"{error['error']}"
                    )

                for file_index, document in enumerate(
                    assessment["documents"]
                ):

                    with st.expander(
                        "Extracted content — "
                        f"{document['filename']}",
                        expanded=False,
                    ):

                        st.success(
                            "Text extraction successful"
                        )

                        m1, m2 = st.columns(2)

                        m1.metric(
                            "Characters extracted",
                            f"{document['characters']:,}",
                        )

                        m2.metric(
                            "Sections identified",
                            len(document["sections"]),
                        )

                        if document["truncated"]:

                            st.warning(
                                "Content exceeded 150,000 "
                                "characters and was truncated."
                            )

                        for section_index, section in enumerate(
                            document["sections"]
                        ):

                            source_name = escape(
                                str(
                                    section.get(
                                        "source",
                                        "Unknown",
                                    )
                                )
                            )

                            st.markdown(
                                f"**Source: {source_name}**"
                            )

                            full_text = str(
                                section.get(
                                    "text",
                                    "",
                                )
                            )

                            preview = full_text[:10000]

                            st.text_area(
                                "Extracted text preview",
                                value=preview,
                                height=180,
                                disabled=True,
                                key=(
                                    f"extract_{file_index}_"
                                    f"{section_index}"
                                ),
                            )

                            if len(full_text) > len(preview):

                                st.caption(
                                    "Preview limited to the "
                                    "first 10,000 characters."
                                )

                        st.caption(
                            "Extraction only — no compliance "
                            "decision has been made."
                        )

            else:

                st.info(
                    "Select the processing button above "
                    "to extract and assess your evidence."
                )

    with info_col:

        card(
            "SUPPORTED FORMATS",
            "Flexible Evidence Intake",
            "PDF · DOCX · XLSX · CSV · JSON · TXT",
        )

        card(
            "DATA PROTECTION",
            "Privacy First",
            "Use fictional or sanitized evidence. "
            "Never upload real patient information, "
            "passwords, or confidential hospital data.",
        )

        card(
            "ASSESSMENT POLICY",
            "Analyst in Control",
            "Potential evidence matches require "
            "human validation before any "
            "compliance conclusion.",
        )


# ============================================================
# TAB 2 — ASSESSMENT ENGINE
# ============================================================

with tab_analysis:

    st.write("")

    st.markdown(
        '<div class="section-label">'
        'Layer 03 / Pilot mapping'
        '</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Assessment Engine")

    st.caption(
        "Pilot ECC evidence mapping and structured, "
        "cross-document security observations."
    )

    st.info(
        "Pilot scope: four verified ECC parent controls. "
        "Keyword mapping and rule-based cross-document "
        "observations; neither constitutes an organizational "
        "compliance determination."
    )

    assessment = (
        st.session_state.assessment_result
    )

    if assessment is None:

        st.warning(
            "Upload simulated evidence in the Evidence "
            "Workspace and select "
            "'Process evidence & find potential matches'."
        )

    else:

        mappings = assessment["mappings"]

        match_count = sum(
            len(item["potential_evidence"])
            for item in mappings
        )

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Documents processed",
            assessment["documents_processed"],
        )

        m2.metric(
            "Potential matches",
            match_count,
        )

        m3.metric(
            "Extraction errors",
            len(
                assessment["extraction_errors"]
            ),
        )

        if assessment["extraction_errors"]:

            st.warning(
                "Some evidence files could not be "
                "processed. Review the errors in "
                "the Evidence Workspace."
            )

        st.markdown(
            "#### Control-to-evidence mapping"
        )

        for mapping in mappings:

            st.markdown(
                "### ECC "
                + escape(
                    mapping["control_id"]
                )
            )

            st.write(
                mapping["requirement"]
            )

            st.caption(
                "Official framework source: "
                "ECC-2:2024, PDF page "
                f"{mapping['pdf_page']}"
            )

            st.write(
                "**Assessment status:** "
                "Requires human review"
            )

            matches = mapping[
                "potential_evidence"
            ]

            if not matches:

                st.warning(
                    "No keyword-matched evidence found "
                    "in the processed documents. "
                    "This does not establish noncompliance."
                )

            else:

                st.success(
                    f"{len(matches)} potential supporting "
                    "document(s) identified"
                )

                for match_index, match in enumerate(
                    matches
                ):

                    with st.expander(
                        f"{match['filename']} — potential match",
                        expanded=(match_index == 0),
                    ):

                        st.write(
                            "**Matched terms:** "
                            + ", ".join(
                                match["matched_keywords"]
                            )
                        )

                        st.write(
                            "**Extracted evidence excerpt:**"
                        )

                        st.code(
                            match["evidence_excerpt"],
                            language=None,
                        )

                        st.caption(
                            "Excerpt is an initial preview, "
                            "not proof that the control is "
                            "fulfilled. Review the full "
                            "source document."
                        )

        st.markdown("---")

        st.markdown(
            "#### Structured security observations"
        )

        st.caption(
            "Rule-based analysis of extracted tables. "
            "Findings are preliminary and require "
            "human validation."
        )

        result = analyze_security(
            assessment["documents"]
        )

        x1, x2 = st.columns(2)

        x1.metric(
            "Structured tables",
            result["tables_detected"],
        )

        x2.metric(
            "Proposed observations",
            result["observation_count"],
        )

        if not result["observations"]:

            st.info(
                "No observations triggered by the "
                "current structured checks. "
                "This does not prove compliance."
            )

        for observation in result[
            "observations"
        ]:

            heading = (
                f"{observation['observation_id']} · "
                f"{observation['title']} · "
                f"{observation['subject']}"
            )

            with st.expander(heading):

                st.markdown(
                    "**ECC reference:** "
                    + observation["ecc_control"]
                )

                st.markdown(
                    "**Status:** Requires human review"
                )

                st.write(
                    observation["explanation"]
                )

                st.markdown(
                    "**Source evidence**"
                )

                for source in observation[
                    "evidence"
                ]:

                    st.caption(
                        f"{source['filename']} · "
                        f"{source['source']} · "
                        f"extracted row {source['row']}"
                    )

                    st.code(
                        source["excerpt"],
                        language=None,
                    )

        st.caption(
            "These observations are preliminary. "
            "Open Workflow & Reporting to record "
            "analyst decisions."
        )


# ============================================================
# TAB 3 — HUMAN VALIDATION AND REPORTING
# ============================================================

with tab_workflow:

    st.write("")

    st.markdown(
        '<div class="section-label">'
        'Layer 04 / Human oversight'
        '</div>',
        unsafe_allow_html=True,
    )

    st.subheader(
        "Analyst Validation & Reporting"
    )

    st.caption(
        "Decisions apply to proposed observations, "
        "not to organizational ECC compliance status."
    )

    assessment = (
        st.session_state.assessment_result
    )

    if assessment is None:

        st.info(
            "Process simulated evidence in the "
            "Evidence Workspace to begin "
            "analyst validation."
        )

    else:

        analysis = analyze_security(
            assessment["documents"]
        )

        observations = analysis[
            "observations"
        ]

        choices = [
            "Pending review",
            "Accepted as finding",
            "Rejected",
            "Needs more evidence",
        ]

        if not observations:

            st.info(
                "No structured observations were "
                "triggered. This is not proof "
                "of compliance."
            )

        for observation in observations:

            oid = observation[
                "observation_id"
            ]

            current = (
                st.session_state.review_decisions.get(
                    oid,
                    {},
                )
            )

            heading = (
                f"{oid} · "
                f"{observation['title']} · "
                f"{observation['subject']}"
            )

            with st.expander(
                heading,
                expanded=False,
            ):

                st.markdown(
                    "**ECC reference:** "
                    + observation["ecc_control"]
                )

                st.write(
                    observation["explanation"]
                )

                for source in observation[
                    "evidence"
                ]:

                    st.caption(
                        f"{source['filename']} · "
                        f"{source['source']} · "
                        f"extracted row {source['row']}"
                    )

                    st.code(
                        source["excerpt"],
                        language=None,
                    )

                current_decision = current.get(
                    "decision",
                    "Pending review",
                )

                selection = st.selectbox(
                    "Analyst decision",
                    choices,
                    index=choices.index(
                        current_decision
                    ),
                    key=f"review_status_{oid}",
                )

                rationale = st.text_area(
                    "Review justification / required follow-up",
                    value=current.get(
                        "rationale",
                        "",
                    ),
                    key=f"review_note_{oid}",
                    help=(
                        "Required for a decision other "
                        "than Pending review."
                    ),
                )

                if st.button(
                    "Save review",
                    key=f"save_review_{oid}",
                ):

                    if (
                        selection != "Pending review"
                        and not rationale.strip()
                    ):

                        st.error(
                            "Please provide a justification "
                            "before saving this decision."
                        )

                    else:

                        st.session_state.review_decisions[
                            oid
                        ] = {
                            "decision": selection,
                            "rationale": rationale.strip(),
                        }

                        st.success(
                            "Review saved for this session."
                        )

        reviewed = sum(
            1
            for observation in observations
            if (
                st.session_state.review_decisions.get(
                    observation["observation_id"],
                    {},
                ).get(
                    "decision",
                    "Pending review",
                )
                != "Pending review"
            )
        )

        accepted = sum(
            1
            for observation in observations
            if (
                st.session_state.review_decisions.get(
                    observation["observation_id"],
                    {},
                ).get("decision")
                == "Accepted as finding"
            )
        )

        a, b, c = st.columns(3)

        a.metric(
            "Proposed observations",
            len(observations),
        )

        b.metric(
            "Decisions recorded",
            reviewed,
        )

        c.metric(
            "Accepted findings",
            accepted,
        )

        st.divider()

        # ----------------------------------------------------
        # REPORTING
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-label">'
            'Layer 05 / Export'
            '</div>',
            unsafe_allow_html=True,
        )

        st.subheader(
            "Assessment Report"
        )

        st.caption(
            "Exports include source references and "
            "analyst decisions. They do not certify "
            "ECC compliance."
        )

        report_rows = []

        for observation in observations:

            review = (
                st.session_state.review_decisions.get(
                    observation["observation_id"],
                    {},
                )
            )

            report_rows.append(
                {
                    "observation_id": observation[
                        "observation_id"
                    ],
                    "rule_id": observation[
                        "rule_id"
                    ],
                    "title": observation[
                        "title"
                    ],
                    "subject": observation[
                        "subject"
                    ],
                    "ecc_reference": observation[
                        "ecc_control"
                    ],
                    "explanation": observation[
                        "explanation"
                    ],
                    "analyst_decision": review.get(
                        "decision",
                        "Pending review",
                    ),
                    "analyst_justification": review.get(
                        "rationale",
                        "",
                    ),
                    "source_evidence": observation[
                        "evidence"
                    ],
                }
            )

        report = {
            "application": "AegisIQ",
            "assessment_type": (
                "Fictional evidence / NCA ECC pilot"
            ),
            "method": (
                "Rule-based structured evidence "
                "analysis; human review"
            ),
            "disclaimer": (
                "Not an ECC compliance certification "
                "or comprehensive assessment."
            ),
            "documents_processed": assessment[
                "documents_processed"
            ],
            "extraction_errors": assessment[
                "extraction_errors"
            ],
            "structured_tables": analysis[
                "tables_detected"
            ],
            "observations": report_rows,
        }

        table_rows = [
            {
                "ID": row[
                    "observation_id"
                ],
                "Subject": row[
                    "subject"
                ],
                "ECC": row[
                    "ecc_reference"
                ],
                "Decision": row[
                    "analyst_decision"
                ],
            }
            for row in report_rows
        ]

        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True,
        )

        left, right = st.columns(2)

        with left:

            st.download_button(
                "Download detailed JSON report",
                data=json.dumps(
                    report,
                    ensure_ascii=False,
                    indent=2,
                ).encode("utf-8"),
                file_name=(
                    "AegisIQ_assessment_report.json"
                ),
                mime="application/json",
                use_container_width=True,
            )

        with right:

            output = io.StringIO()

            fieldnames = [
                "observation_id",
                "rule_id",
                "title",
                "subject",
                "ecc_reference",
                "explanation",
                "analyst_decision",
                "analyst_justification",
                "source_evidence",
            ]

            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for record in report_rows:

                writer.writerow(
                    {
                        **record,
                        "source_evidence": json.dumps(
                            record["source_evidence"],
                            ensure_ascii=False,
                        ),
                    }
                )

            st.download_button(
                "Download review matrix (CSV)",
                data=output.getvalue().encode(
                    "utf-8-sig"
                ),
                file_name=(
                    "AegisIQ_review_matrix.csv"
                ),
                mime="text/csv",
                use_container_width=True,
            )

        st.warning(
            "Reviews exist only in this browser session "
            "and reset when the evidence changes. "
            "Download a report to retain them."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
<div class="footer">
    AegisIQ — AI-Assisted Evidence Assessment · NCA ECC
    <br>
    Educational, department-scoped proof of concept
    using synthetic data.
    Not a compliance certification.
    <br>
    Independent cybersecurity portfolio project.
    Not affiliated with or endorsed by the
    National Cybersecurity Authority.
</div>
""",
    unsafe_allow_html=True,
)
