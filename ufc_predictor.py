import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score

# ---------- SETTINGS ----------
FILTER_OLD_EVENTS = True   # Set to True to drop UFC 1–39 fights

# ---------- STEP 1: Load Dataset ----------
print("🔄 Loading dataset...")
df = pd.read_csv("large_dataset.csv")
print(f"✅ Original dataset shape: {df.shape}")

# ---------- STEP 2: Optionally Drop Early Events ----------
if FILTER_OLD_EVENTS:
    print("🧹 Dropping early UFC events (UFC 1–39)...")
    df = df[~df['event_name'].str.contains(r'UFC\s([1-9]$|[1-3][0-9]($|\D))', na=False)]
    print(f"✅ After filtering: {df.shape}")
else:
    print("📂 Keeping all UFC events (no filtering).")

# ---------- STEP 3: Create Target Column ----------
print("🎯 Creating target variable...")
df['target'] = df['winner'].apply(lambda x: 1 if x == 'Red' else 0)

# ---------- STEP 4: Select Feature Columns ----------
print("📊 Selecting feature columns (only '_diff')...")
features = [col for col in df.columns if '_diff' in col]
X = df[features]
y = df['target']

# ---------- STEP 5: Drop Rows with Missing Values ----------
print("🚫 Dropping rows with missing values...")
mask = X.notna().all(axis=1) & y.notna()
X = X[mask]
y = y[mask]
print(f"✅ Shape after cleaning: {X.shape}")

# ---------- STEP 6: Train/Test Split ----------
print("🔀 Splitting into train/test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📦 Train size: {X_train.shape[0]} | 🧪 Test size: {X_test.shape[0]}")

# ---------- STEP 7: Train Logistic Regression ----------
print("🤖 Training Logistic Regression model...")
model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)

# ---------- STEP 8: Evaluate Model ----------
print("📈 Evaluating model...")
preds = model.predict(X_test)
accuracy = accuracy_score(y_test, preds)

print("\n--- 📊 Final Results ---")
print(f"✅ Accuracy: {accuracy:.4f}")
print("\n🧾 Classification Report:")
print(classification_report(y_test, preds, target_names=["Blue Win", "Red Win"]))

import joblib
joblib.dump(model, 'ufc_logistic_model.pkl')
