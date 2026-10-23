# NCA ECC Compliance Assistant — MVP

A local prototype for simulated healthcare cybersecurity evidence.

## Run on Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If activation is blocked by your PowerShell execution policy, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

No real patient data should be uploaded. This initial milestone only accepts PDF uploads; it does not analyze compliance or use AI yet.
