import pandas as pd
import joblib
from ufc_helpers import get_next_event_fighters, get_fighter_stats, calculate_diff

# ---------- Load Trained Model ----------
print("📦 Loading trained model...")
model = joblib.load("ufc_logistic_model.pkl")
print("✅ Model loaded.")

# ---------- Get Next UFC Card ----------
print("\n🔍 Getting next UFC event fight list...")
fight_list = get_next_event_fighters()
print(f"✅ Found {len(fight_list)} fights.\n")

# ---------- Predict Each Fight ----------
for i, (red_url, blue_url) in enumerate(fight_list):
    print(f"⚔️  Fight {i+1}/{len(fight_list)}")

    red = get_fighter_stats(red_url)
    blue = get_fighter_stats(blue_url)

    if not red or not blue:
        print("❌ Could not retrieve both fighters' stats. Skipping...\n")
        continue

    diff_dict = calculate_diff(red, blue)
    input_df = pd.DataFrame([diff_dict])

    prediction = model.predict(input_df)[0]
    confidence = model.predict_proba(input_df)[0][prediction]

    red_name = red.get('name', 'Red Fighter')
    blue_name = blue.get('name', 'Blue Fighter')
    winner = red_name if prediction == 1 else blue_name

    print(f"🥋 {red_name} vs {blue_name}")
    print(f"🧠 Predicted Winner: {winner}")
    print(f"📊 Confidence: {confidence:.2%}\n")

print("✅ All predictions complete.")
