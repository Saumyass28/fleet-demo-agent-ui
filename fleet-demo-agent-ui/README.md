# Fleet Agent Demo (UI + Mock Agent)

This demo shows your custom **UI** wired with a mock `FleetAgent` backend.  
No LLMs or APIs required.

## Steps to Run Locally
```bash
pip install -r requirements.txt
streamlit run fleetagents.py
```

## Deploy to Streamlit Cloud
1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io and connect your GitHub.
3. Select this repo and set `fleetagents.py` as the main file.
4. Deploy.

## Workflow (Mock Agent)
- User enters location & specs
- Agent looks up OEMs (mock data)
- Shows vehicles & filters shortlist
- Displays reviews & document comparisons
