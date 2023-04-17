# Container Images

Several container images are provided as examples for running the ML Operator.

## ML Operator

This image contains the code that runs the ML Operator. It is based on kopf and uses the Python SDK to interact with the Kubernetes API.

## ML Model

This image contains a simple ML model that can be used for testing the ML Operator. It is based on the [Kaggle Titanic Tutorial](https://www.kaggle.com/code/alexisbcook/titanic-tutorial), but uses scikit-learn pipelines instead of pandas features engineering.

This allows for saving a model artifact that contains both the machine learning model (a Random Forest Classifier) and the feature engineering (OneHotEncoder).

The container provides to API endpoints available on port 8080:
- `/ping`: A simple ping endpoint that returns HTTP 200 if everything is ok.
- `/invocations`: A prediction endpoint that expects a JSON payload expecting columns `Pclass`, `Sex`, `SibSp` and `Parch`. It returns a JSON payload with the prediction 0 or 1 for the survival of the passenger.

## ML Model Initializer

This image contains a simple script that initializes a ML Model resource by downloading a model artifact from a URL and storing it in a Kubernetes Persistent Volume available for the ML Model.