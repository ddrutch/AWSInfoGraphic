Flask demo for the ContentAnalyzer agent

Usage

1. Install dependencies (recommended to use a virtualenv):

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Run the demo app:

   python web/app.py

3. Open http://127.0.0.1:5000 in your browser.

Notes
- Toggle Demo Mode on the page to use local deterministic fallbacks (no Bedrock required).
- The demo app calls `create_content_analyzer_agent().process(...)` synchronously for simplicity.
