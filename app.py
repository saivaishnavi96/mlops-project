from flask import Flask, render_template, request, jsonify
from pathlib import Path
import joblib
import pandas as pd
import time

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / 'chatbot_models'
app = Flask(__name__)

RESPONSES = {
    'order_status': 'I can help you check your order status.',
    'refund': 'I can help you with your refund request.',
    'return': 'I can help you return or exchange your product.',
    'password_reset': 'I can help you reset your password.',
    'product_info': 'I can help you with product information.'
}

model_a = model_b = vectorizer = None
model_load_error = None
try:
    model_a = joblib.load(MODEL_DIR / 'model_a.pkl')
    model_b = joblib.load(MODEL_DIR / 'model_b.pkl')
    vectorizer = joblib.load(MODEL_DIR / 'vectorizer.pkl')
except Exception as exc:
    model_load_error = str(exc)


def load_metrics():
    path = BASE_DIR / 'chatbot_ab_test_results.csv'
    if path.exists():
        try:
            df = pd.read_csv(path)
            metrics = {}
            for _, row in df.iterrows():
                name = str(row.get('Model', '')).strip()
                key = 'model_a' if name.lower() == 'model a' else 'model_b' if name.lower() == 'model b' else None
                if key:
                    metrics[key] = {
                        'accuracy': float(row['Accuracy']),
                        'precision': float(row['Precision']),
                        'recall': float(row['Recall']),
                        'f1_score': float(row['F1 Score'])
                    }
            if 'model_a' in metrics and 'model_b' in metrics:
                return metrics
        except Exception:
            pass
    # Fallback: calculate metrics only if the original labelled test split is exported.
    return None

@app.get('/')
def index():
    return render_template('index.html')

@app.get('/api/metrics')
def metrics():
    if model_load_error:
        return jsonify(error='Model files not found. Export the trained models from Colab and place them in the chatbot_models folder.'), 503
    results = load_metrics()
    if results is None:
        return jsonify(error='chatbot_ab_test_results.csv is missing or does not contain Model, Accuracy, Precision, Recall and F1 Score columns.'), 503
    return jsonify(results)

@app.post('/api/predict')
def predict():
    if model_load_error:
        return jsonify(error='Model files not found. Export model_a.pkl, model_b.pkl and vectorizer.pkl from your Colab notebook.'), 503
    body = request.get_json(silent=True) or {}
    question = str(body.get('question', '')).strip()
    selected_model = body.get('selected_model', 'Show Both')
    if not question:
        return jsonify(error='Please enter a customer question.'), 400
    try:
        vector = vectorizer.transform([question])
        start = time.perf_counter(); intent_a = str(model_a.predict(vector)[0]); latency_a = (time.perf_counter() - start) * 1000
        start = time.perf_counter(); intent_b = str(model_b.predict(vector)[0]); latency_b = (time.perf_counter() - start) * 1000
        metrics_data = load_metrics() or {}
        accuracy_a = (metrics_data.get('model_a') or {}).get('accuracy')
        accuracy_b = (metrics_data.get('model_b') or {}).get('accuracy')
        if accuracy_a is not None and accuracy_b is not None and accuracy_a > accuracy_b:
            recommended = 'Model A · Naive Bayes'
        elif accuracy_a is not None and accuracy_b is not None and accuracy_b > accuracy_a:
            recommended = 'Model B · Logistic Regression'
        else:
            recommended = 'Accuracy tied or metrics unavailable'
        result = {
            'model_a': {'intent': intent_a, 'latency_ms': latency_a, 'response': RESPONSES.get(intent_a, 'No predefined response for this intent.')},
            'model_b': {'intent': intent_b, 'latency_ms': latency_b, 'response': RESPONSES.get(intent_b, 'No predefined response for this intent.')},
            'accuracy_a': accuracy_a, 'accuracy_b': accuracy_b, 'recommended_model': recommended,
            'selected_model': selected_model
        }
        # Append a lightweight prediction log for later review.
        log_path = BASE_DIR / 'ab_test_results.csv'
        log_row = pd.DataFrame([{'timestamp': pd.Timestamp.now().isoformat(), 'question': question,
                                 'selected_model': selected_model, 'model_a_intent': intent_a,
                                 'model_b_intent': intent_b, 'model_a_latency_ms': latency_a,
                                 'model_b_latency_ms': latency_b, 'recommended_model': recommended}])
        log_row.to_csv(log_path, mode='a', header=not log_path.exists(), index=False)
        return jsonify(result)
    except Exception as exc:
        return jsonify(error=f'Prediction failed: {exc}'), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
