import streamlit as st

# === Load Valid Indian Cities ===
with open("indian_cities.txt", "r") as file:
    valid_cities = set(line.strip().lower() for line in file if line.strip())

# === City Tier & Base Price Logic ===
def detect_city_tier(city):
    tier1 = ['mumbai', 'delhi', 'bengaluru', 'chennai', 'kolkata', 'hyderabad']
    tier2 = ['ahmedabad', 'pune', 'jaipur', 'lucknow', 'surat', 'kanpur']
    if city in tier1:
        return 2.5e7, "Tier 1 - Metro"
    elif city in tier2 or city.endswith("pur") or city.endswith("nagar") or len(city) >= 7:
        return 1.4e7, "Tier 2"
    else:
        return 0.6e7, "Tier 3"

# === Price Estimation Function ===
def estimate_price(base_price, size, bedrooms, bathrooms, floors, year_built, parking, garden, facilities):
    price = base_price
    size_diff = size - 1500
    price += (size_diff // 100) * 0.05 * base_price
    if bedrooms == 1:
        price -= 0.10 * base_price
    elif bedrooms >= 3:
        price += 0.10 * base_price
    if bathrooms > 2:
        price += 0.05 * (bathrooms - 2) * base_price
    elif bathrooms < 2:
        price -= 0.05 * (2 - bathrooms) * base_price
    if floors == 2:
        price += 0.10 * base_price
    elif floors >= 3:
        price += 0.20 * base_price
    age = max(0, 2025 - year_built)
    price *= max(1 - 0.01 * age, 0.7)
    if parking:
        price += 0.05 * base_price
    if garden:
        price += 0.05 * base_price
    facilities = [f.strip().lower() for f in facilities.split(",") if f.strip().lower() not in ("", "no", "none")]
    price += len(facilities) * 0.03 * base_price
    return price

# === Default Values ===
defaults = {
    "city": "",
    "size": "",
    "bedrooms": "",
    "bathrooms": "",
    "floors": "",
    "year_built": "",
    "parking": "-- Select --",
    "garden": "-- Select --",
    "facilities": "",
    "confirm_reset": False,
    "reset_trigger": False,
    "reset_message_shown": False
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# === Streamlit UI ===
st.set_page_config(page_title="Indian House Price Estimator", layout="centered")
st.title("Smart Indian House Price Estimator")
st.caption("Estimate realistic house prices based on city, size, features, and facilities.")

# Inputs
st.session_state.city = st.text_input("Enter your City (India):", value=st.session_state.city).strip().lower()

if st.session_state.city:
    if st.session_state.city not in valid_cities:
        st.error("Invalid city. Please enter a valid Indian city.")
    else:
        base_price, tier = detect_city_tier(st.session_state.city)

        st.session_state.size = st.text_input("Size (in sqft):", value=st.session_state.size)
        st.session_state.bedrooms = st.text_input("Bedrooms (1–9):", value=st.session_state.bedrooms)
        st.session_state.bathrooms = st.text_input("Bathrooms (1–9):", value=st.session_state.bathrooms)
        st.session_state.floors = st.text_input("Floors (1–9):", value=st.session_state.floors)
        st.session_state.year_built = st.text_input("Year Built (1900–2025):", value=st.session_state.year_built)
        st.session_state.parking = st.selectbox("Parking Available?", ["-- Select --", "Yes", "No"],
                                                index=["-- Select --", "Yes", "No"].index(st.session_state.parking))
        st.session_state.garden = st.selectbox("Garden/Lawn?", ["-- Select --", "Yes", "No"],
                                               index=["-- Select --", "Yes", "No"].index(st.session_state.garden))
        st.session_state.facilities = st.text_input("Extra facilities (e.g. lift, balcony, gym, pool):",
                                                    value=st.session_state.facilities)

        # Buttons
        col1, col2 = st.columns([5, 1])
        with col1:
            estimate = st.button("Estimate Price")
        with col2:
            reset = st.button("🔄", help="Reset form")

        # === Handle Reset Trigger ===
        if reset:
            st.session_state.confirm_reset = True
            st.session_state.reset_message_shown = False

        if st.session_state.confirm_reset:
            st.warning("Are you sure you want to reset all fields?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, Reset", key="yes_reset"):
                    for key in defaults:
                        st.session_state[key] = defaults[key]
                    st.session_state.reset_message_shown = True
                    st.session_state.confirm_reset = False
            with c2:
                if st.button("No, Cancel", key="no_reset"):
                    st.session_state.confirm_reset = False
                    st.session_state.reset_message_shown = False

        # Show reset message only after successful reset
        if st.session_state.reset_message_shown:
            st.success("✅ All fields have been reset.")
            st.session_state.reset_message_shown = False

        # === Handle Estimate ===
        if estimate:
            try:
                size = float(st.session_state.size)
                bedrooms = int(st.session_state.bedrooms)
                bathrooms = int(st.session_state.bathrooms)
                floors = int(st.session_state.floors)
                year = int(st.session_state.year_built)

                if not (99 <= size <= 99999):
                    st.warning("Size must be between 99 and 99,999 sqft."); st.stop()
                if not (1 <= bedrooms <= 9):
                    st.warning("Bedrooms must be between 1 and 9."); st.stop()
                if not (1 <= bathrooms <= 9):
                    st.warning("Bathrooms must be between 1 and 9."); st.stop()
                if not (1 <= floors <= 9):
                    st.warning("Floors must be between 1 and 9."); st.stop()
                if not (1900 <= year <= 2025):
                    st.warning("Year must be between 1900 and 2025."); st.stop()
                if st.session_state.parking == "-- Select --" or st.session_state.garden == "-- Select --":
                    st.warning("Please select Parking and Garden options."); st.stop()

                parking = st.session_state.parking == "Yes"
                garden = st.session_state.garden == "Yes"

                final_price = estimate_price(base_price, size, bedrooms, bathrooms, floors, year, parking, garden,
                                             st.session_state.facilities)
                final_price = min(max(final_price, 5e6), 5e8)

                st.success(f"City Tier: {tier}")
                st.success(f"Estimated House Price: ₹{final_price / 1e7:.2f} crore")
                st.caption("Goodbye! Have a great day and may your dream home find you soon!")

            except:
                st.warning("Please fill all fields correctly to continue.")
