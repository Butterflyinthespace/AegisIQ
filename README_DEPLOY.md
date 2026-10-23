# AegisIQ — public demo deployment

This package provides a **read-only Streamlit demonstration** of AegisIQ. It includes 14 synthetic evidence documents from fictional Noura Valley Hospital and five illustrative observations. The private assessor answer key is deliberately excluded.

## Add to your existing repository

Copy `demo_app.py`, `demo_data/`, and `requirements-demo.txt` into the repository root. Copy your existing `logo.png` if not already present. Keep `app.py` as the local, full-function prototype.

## Deploy

1. Commit and push these files to GitHub (the repository can remain private if the hosting provider supports private repository access).
2. On Streamlit Community Cloud, select the repository, branch `main`, and main file `demo_app.py`.
3. For dependency discovery, Streamlit normally uses `requirements.txt` in the repository. Ensure it contains `streamlit` and all dependencies required by the local app, or configure the demo to use an isolated deployment environment. `requirements-demo.txt` is a minimal reference, not automatically selected by Streamlit.
4. Verify all tabs, 14 downloads, and findings in a private deployment before sharing the public URL.

## Security and accuracy

This interface has no upload, edit, login, or server-side user-write functions. Evidence files are static assets included in the app repository and **are downloadable by visitors**. Do not replace them with real patient data or confidential documents. A read-only interface is not a substitute for reviewing repository permissions, dependency security, and hosting settings.

Free Streamlit hosting may put idle apps to sleep; cloud hosting works without the developer's laptop but does not guarantee instant 24/7 availability.
