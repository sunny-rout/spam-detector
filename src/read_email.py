import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import clean_text

df = pd.read_csv('spam.csv')
# Display the first few rows of the DataFrame to verify the contents
print(df.head())
# Display the summary information of the DataFrame to understand its structure)
print(df.info()) 
# Display the column names to understand the structure of the DataFrame
print(df.columns)

# Apply the cleaning function to the 'text' column
df['CleanedMessage'] = df['Message'].apply(clean_text.clean_text)
# Display the first few rows of the DataFrame after cleaning
print(df[['Message', 'CleanedMessage']].head())

vectorizer = CountVectorizer()
# Fit the vectorizer on the cleaned text data
X = vectorizer.fit_transform(df['CleanedMessage'])
# Display the shape of the resulting feature matrix
print("Shape of the feature matrix:", X.shape)
# Display the feature names to understand the vocabulary
print("Feature names:", vectorizer.get_feature_names_out()[:5])  # Display first 5 feature names

# Prepare the target variable
y = df['Category'].map({'ham': 0, 'spam': 1})
# Display the unique values in the target variable
print("Unique values in target variable:", y.unique())
# Train a Naive Bayes classifier
model = MultinomialNB()
model.fit(X, y)
# Display the model's class prior probabilities
print("Class prior probabilities:", model.class_prior)
# Function to predict if an email is spam or ham
def predict_email(text):
    cleaned_text = clean_text(text)
    text_vector = vectorizer.transform([cleaned_text])
    prediction = model.predict(text_vector)
    return 'spam' if prediction[0] == 1 else 'ham'
# Example usage of the predict_email function
example_email = "Congratulations! You've won a lottery of $1000!"
print("Prediction for example email:", predict_email(example_email))
# Save the model and vectorizer for future use
joblib.dump(model, 'spam_classifier.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
# Display a message indicating that the model and vectorizer have been saved
print("Model and vectorizer saved successfully.")
# ...existing code...