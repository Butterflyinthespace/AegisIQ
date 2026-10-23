"""Read-only AegisIQ portfolio demonstration using fictional records."""
from pathlib import Path
import json
import streamlit as st

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "demo_data" / "synthetic_evidence"
OBSERVATIONS = ROOT / "demo_data" / "observations.json"
NAVY, TEAL = "#0B2639", "#328F96"

st.set_page_config(page_title="AegisIQ | Public Demonstration", page_icon="🛡️", layout="wide")
st.markdown("""<style>
.stApp {background:#F7FAFB;color:#173548}
.block-container {max-width:1250px;padding-top:2rem}
[data-testid="stSidebar"] {background:white}
[data-testid="stMain"] p, [data-testid="stMain"] li {font-size:17px;line-height:1.7}
[data-testid="stMain"] h1 {font-size:38px;color:#0B2639}
[data-testid="stMain"] h2 {font-size:28px;color:#0B2639}
[data-testid="stMain"] h3 {font-size:22px;color:#0B2639}
button[data-baseweb="tab"] {font-size:17px}
.hero {background:linear-gradient(110deg,#0B2639,#22646B);padding:32px 38px;border-radius:18px;color:white}
.hero h1 {color:white!important;margin:0 0 12px 0}
.hero p {color:#D6E8EA!important;margin:0}
.note {background:#EAF5F4;border-left:4px solid #328F96;padding:14px 18px;border-radius:8px}
</style>""",unsafe_allow_html=True)

with st.sidebar:
    logo = ROOT / "logo.png"
    if logo.exists(): st.image(str(logo), use_container_width=True)
    else: st.title("AegisIQ")
    st.caption("PUBLIC DEMONSTRATION")
    st.success("Read-only visitor mode")
    st.write("Synthetic evidence only. No uploads, editing, accounts, or live systems.")
    st.caption("Independent educational portfolio project.")

st.markdown('<div class="hero"><h1>AegisIQ</h1><p>Cybersecurity evidence assessment · NCA ECC pilot<br>Fictional OB/GYN department · Noura Valley Hospital</p></div>',unsafe_allow_html=True)
st.write("")
st.info("Educational proof of concept. All hospital data is fictional. Observations are illustrative and require human review; this is not an NCA compliance certification or a production hospital system.")

records = sorted(p for p in EVIDENCE.iterdir() if p.is_file())
findings = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
a,b,c=st.columns(3)
a.metric("Synthetic evidence files",len(records))
b.metric("Illustrative observations",len(findings))
c.metric("Visitor permissions","Read-only")

t1,t2,t3,t4,t5=st.tabs(["Overview","Evidence Library","Assessment Findings","Risk Acceptance Case","Methodology & Limitations"])
with t1:
    st.subheader("What this demonstration shows")
    st.write("AegisIQ explores how cybersecurity evidence from multiple documents can be organized, cross-referenced, and reviewed against selected NCA Essential Cybersecurity Controls (ECC) topics. The public website presents a precomputed, inspectable scenario rather than executing assessments on visitor input.")
    st.markdown("**Workflow:** Document intake → extraction → rule-based comparison → proposed observation → human review → risk-treatment case study → reporting.")
    st.markdown("**Scenario:** One fictional hospital's Obstetrics and Gynecology department. No real patients, employees, or organizational systems are represented.")
    st.caption("Open Evidence Library to inspect all 14 original simulated documents and Assessment Findings to see the example cross-document observations.")
with t2:
    st.subheader("Original simulated evidence")
    st.write("All 14 scenario documents are included as read-only resources. Text formats can be previewed below; all files can be downloaded for independent inspection.")
    for i,p in enumerate(records):
        with st.expander(f"{p.name} · {p.stat().st_size/1024:.1f} KB"):
            if p.suffix.lower() in {'.csv','.json','.txt'}:
                raw=p.read_text(encoding='utf-8-sig',errors='replace')
                st.code(raw[:18000],language='json' if p.suffix=='.json' else None)
                if len(raw)>18000: st.caption('Preview truncated; download for the complete file.')
            else: st.caption("Download this original document to inspect its contents.")
            st.download_button("Download evidence file",data=p.read_bytes(),file_name=p.name,mime='application/octet-stream',key=f'dl_{i}')
with t3:
    st.subheader("Precomputed assessment observations")
    st.write("These five observations are examples derived from the fictional evidence pack. They are not live results or confirmed compliance failures.")
    for f in findings:
        with st.expander(f"{f['id']} · {f['title']}",expanded=False):
            st.markdown(f"**Subject:** {f['subject']}  \n**Selected ECC reference:** {f['ecc']}")
            st.write(f['summary'])
            st.markdown('**Source documents:**')
            for name in f['sources']: st.write('• '+name)
            st.warning('Review status: illustrative observation — independent analyst validation required.')
    st.download_button('Download example findings (JSON)',data=OBSERVATIONS.read_bytes(),file_name='AegisIQ_demo_observations.json',mime='application/json')
with t5:
    st.subheader("Methodology")
    st.write("The local prototype processes uploaded PDF, Word, Excel, CSV, JSON, and text evidence, maps selected ECC control topics, and uses deterministic rules to flag specific inconsistencies across structured records. This public version displays the synthetic source documents and illustrative results without running the processing pipeline.")
    st.subheader("Limitations")
    st.markdown("- The Risk Acceptance Case tab adds hypothetical business context not supported by the original evidence.\n- No risk acceptance has been authorized or recorded.\n- One fictional OB/GYN department; not hospital-wide coverage.\n- Selected ECC topics only; not a complete compliance audit.\n- Rule-based checks, not a validated large-language-model assessment.\n- No real hospital integration, patient data, authentication, or persistent analyst decisions.\n- Visitors cannot upload, edit, or execute assessment code through this interface.\n- Hosting uptime and wake-up behavior depend on the deployment provider.")
    st.markdown("Official framework: [NCA Essential Cybersecurity Controls](https://nca.gov.sa/en/regulatory-documents/controls-list/ecc/).")
with t4:
    st.subheader("Risk Acceptance Case Study")
    st.caption("Fictional training scenario linked to OBS-003. This is not a real approval, and the proposed exception is not established by the source evidence.")
    st.info("Case status: Proposed for management review — no risk acceptance has been approved.")
    st.markdown("### 1. Starting observation")
    st.markdown("**OBS-003 · Privileged remote account lacks multi-factor authentication (MFA)**")
    st.write("The simulated privileged-access register marks `k.alzahrani-admin` as remotely accessible without enforced MFA. This is a potential identity and access management gap under selected ECC reference 2-2-3.")
    st.markdown("**Evidence:** `08_MFA_and_Privileged_Access.csv` and `10_Security_Events.csv`.")
    st.markdown("### 2. Business context — hypothetical assumption")
    st.write("For this teaching exercise, assume a legacy clinical administration system cannot currently support MFA. The fictional IT team requests a short, documented exception while a compatible authentication method is tested. This explanation is invented for the case study; it is not verified by the evidence pack.")
    st.markdown("### 3. Risk assessment")
    left, right = st.columns(2)
    with left:
        st.markdown("**Threat scenario**")
        st.write("Stolen administrator credentials could permit unauthorized remote access because a second authentication factor is absent.")
        st.markdown("**Inherent likelihood (illustrative)**")
        st.write("High — privileged remote access with a single authentication factor.")
    with right:
        st.markdown("**Potential impact**")
        st.write("High — possible compromise of clinical-system administration, service availability, and sensitive operational data.")
        st.markdown("**Inherent risk (illustrative)**")
        st.error("High · qualitative training estimate, not a measured score")
    st.markdown("### 4. Proposed treatment and compensating controls")
    st.markdown("""- **Preferred treatment:** Enable supported MFA or migrate the account to a secure privileged-access method as soon as feasible.
- **Temporary access restriction:** Permit administration only through a controlled jump host or approved network path.
- **Privilege reduction:** Remove unnecessary permissions and limit the account to authorized administrators.
- **Monitoring:** Alert on every use of this account and review privileged sessions.
- **Credential protection:** Use a strong unique credential stored in an approved privileged-access vault, with rotation and emergency revocation procedures.
- **Time limit:** Set an exception expiry date and require evidence of remediation or a fresh decision.""")
    st.markdown("### 5. Residual risk and management decision")
    st.warning("**Residual risk: potentially still significant.** These safeguards may reduce exposure, but they do not provide MFA. Effectiveness must be verified before any residual-risk rating can be finalized.")
    st.markdown("**Proposed analyst recommendation:** Do not grant open-ended acceptance. Escalate a time-limited exception request for review by the authorized risk owner, subject to verified compensating controls, a remediation plan, and periodic reassessment.")
    st.markdown("**Simulated decision record:** Pending — no approval or rejection is asserted.")
    st.markdown("### 6. Required decision evidence")
    st.markdown("Business justification · affected systems and account owner · technical constraint evidence · control test results · likelihood/impact rationale · remediation owner and deadline · authorized approver and decision date.")
    case = {
        "case_id": "RA-001", "linked_observation": "OBS-003",
        "classification": "fictional training case / proposed exception",
        "evidence": ["08_MFA_and_Privileged_Access.csv", "10_Security_Events.csv"],
        "assumption": "Hypothetical legacy-system MFA compatibility constraint; not supported by uploaded evidence",
        "risk_scenario": "Unauthorized remote privileged access following credential compromise",
        "inherent_risk": "High (illustrative qualitative estimate)",
        "proposed_treatment": ["Enable MFA or supported privileged-access alternative", "Restrict administration path", "Least privilege", "Session monitoring", "Credential vault and rotation", "Time-limited exception with remediation deadline"],
        "residual_risk": "Not finalized; verify compensating control effectiveness",
        "analyst_recommendation": "Escalate a time-limited request only after control verification",
        "decision": "Pending authorized management review",
        "note": "No real hospital, risk acceptance, or regulatory determination"
    }
    st.download_button("Download case study (JSON)", data=json.dumps(case, indent=2).encode("utf-8"), file_name="AegisIQ_risk_acceptance_case.json", mime="application/json")
st.divider()
st.caption("AegisIQ · Independent educational portfolio demonstration · Synthetic data · Not affiliated with or endorsed by the NCA.")
