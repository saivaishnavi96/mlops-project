CHATBOT INTENT A/B TESTING FRONTEND
==================================

This package contains a responsive HTML + CSS + JavaScript dashboard and a small Flask backend.
The backend connects the website to your actual scikit-learn models. It is not a mock prediction UI.

PROJECT FILES
-------------
app.py                  Flask backend/API
 templates/index.html   Main dashboard page
 static/style.css       Responsive styling
 static/app.js          UI interactions and API calls
 chatbot_models/        Create this folder and copy the three model files exported from Colab
 chatbot_ab_test_results.csv  Copy the metrics CSV exported from Colab

STEP 1 — EXPORT MODELS FROM GOOGLE COLAB
----------------------------------------
Run the model-save cell in your notebook. It should create:
  chatbot_models/model_a.pkl
  chatbot_models/model_b.pkl
  chatbot_models/vectorizer.pkl

Download chatbot_models.zip from Colab, unzip it, and copy the chatbot_models folder into this project folder.

STEP 2 — COPY THE METRICS CSV
-----------------------------
Download chatbot_ab_test_results.csv from the Colab session and place it next to app.py.
It should have columns: Model, Accuracy, Precision, Recall, F1 Score.

STEP 3 — INSTALL REQUIREMENTS
-----------------------------
Open a terminal in this project folder and run:
  python -m venv .venv

Windows:
  .venv\Scripts\activate
macOS/Linux:
  source .venv/bin/activate

Then run:
  pip install -r requirements.txt

STEP 4 — START THE WEBSITE
--------------------------
Run:
  python app.py

Open this address in your browser:
  http://127.0.0.1:5000

IMPORTANT NOTES
---------------
- The browser frontend calls the Flask backend; the model files must be available locally.
- The notebook currently has only 25 sample questions. Accuracy scores are preliminary.
- The model recommendation is based on overall test-set accuracy, not the correctness of an individual prediction.
- Only use trusted model files. Pickle/joblib files can execute code when loaded.
- For a public deployment, turn off Flask debug mode and use a production server.
