import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

def generate_results():
    """
    Runs the Logistic Regression analysis on the PyLog output
    and returns text stats and the dataframe for visualization.
    """
    # Use the dynamic path from your project structure
    data_path = os.path.join("data", "output", "final_output.csv")
    
    if not os.path.exists(data_path):
        return "ERROR: final_output.csv not found.\nPlease run analysis first.", None

    try:
        # 1. Load dataset
        df = pd.read_csv(data_path)

        # 2. Define features and target (From your logic)
        X = df.drop(['predicted_label'], axis=1, errors='ignore')
        y = df['predicted_label']

        # 3. Preprocessing (From your logic)
        numerical_features = ['path_len']
        # Note: We filter binary features to ensure they exist in the CSV
        all_binary = ['method_enc', 'dos attack', 'malware attack', 'dns attack', 'fishing attack', 'bruteforce attack']
        binary_features = [col for col in all_binary if col in df.columns]

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('bin', 'passthrough', binary_features)
            ],
            remainder='drop'
        )

        # 4. Split and Train
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(random_state=42, solver='liblinear'))
        ])
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # 5. Format Text Output for the Right Panel
        report = classification_report(y_test, y_pred, output_dict=True)
        
        text_res = (
            f"--- MODEL II EVALUATION ---\n"
            f"Accuracy: {report['accuracy']:.2%}\n"
            f"Precision (Attack): {report['1']['precision']:.2%}\n"
            f"Recall (Attack): {report['1']['recall']:.2%}\n"
            f"---------------------------\n"
            f"LOG TOTALS:\n"
            f"Safe: {len(df[df['predicted_label']==0])}\n"
            f"Attack: {len(df[df['predicted_label']==1])}\n"
            f"==========================="
        )

        # We return the text and the DATAFRAME so the UI can draw it
        return text_res, df

    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}", None