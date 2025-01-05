import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import shap
import matplotlib.pyplot as plt

# Load the dataset
file_path = '/content/credit_risk_dataset.csv'
data = pd.read_csv(file_path)

# Handle missing values
data['person_emp_length'] = data['person_emp_length'].fillna(data['person_emp_length'].median())
data['loan_int_rate'] = data['loan_int_rate'].fillna(data['loan_int_rate'].median())

# Separate features and target
X = data.drop(columns=['loan_status'])
y = data['loan_status']

# Define categorical and numerical features
categorical_features = ['person_home_ownership', 'loan_intent', 'loan_grade', 'cb_person_default_on_file']
numerical_features = ['person_age', 'person_income', 'person_emp_length', 'loan_amnt', 'loan_int_rate',
                      'loan_percent_income', 'cb_person_cred_hist_length']

# Preprocessing for numerical and categorical features
numerical_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Define the model
model = RandomForestClassifier(random_state=42)

# Create a pipeline
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('classifier', model)])

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
pipeline.fit(X_train, y_train)

# Evaluate the model
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# Explainability using SHAP
explainer = shap.TreeExplainer(pipeline.named_steps['classifier'])

# Preprocess test data for SHAP
preprocessed_data = pipeline.named_steps['preprocessor'].transform(X_test)

# Convert to dense format if sparse
if hasattr(preprocessed_data, "toarray"):
    preprocessed_data = preprocessed_data.toarray()

# Get SHAP values
shap_values = explainer.shap_values(preprocessed_data)

# Retrieve feature names after preprocessing
feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()

# Plot SHAP summary
shap.summary_plot(shap_values[1], preprocessed_data, feature_names=feature_names)
