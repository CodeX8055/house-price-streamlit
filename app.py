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

# === Price Estimation Logic ===
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

# === Streamlit UI ===
st.set_page_config(page_title="Indian House Price Estimator", layout="centered")
st.title("Smart Indian House Price Estimator")
st.caption("Estimate realistic house prices based on city tier, home features, and facilities.")

# === City Input ===
city = st.text_input("Enter your City (India):").strip().lower()

if city:
    if city not in valid_cities:
        st.error("Invalid city. Please enter a valid Indian city.")
    else:
        base_price, tier = detect_city_tier(city)

        # === Form Begins ===
        with st.form("estimate_form"):
            size = st.number_input("Size (in sqft):", min_value=99, max_value=99999, step=1, key="size")
            bedrooms = st.number_input("Bedrooms (1–9):", min_value=1, max_value=9, step=1, key="bedrooms")
            bathrooms = st.number_input("Bathrooms (1–9):", min_value=1, max_value=9, step=1, key="bathrooms")
            floors = st.number_input("Floors (1–9):", min_value=1, max_value=9, step=1, key="floors")
            year_built = st.number_input("Year Built (1900–2025):", min_value=1900, max_value=2025, step=1, key="year")
            parking = st.radio("Parking Available?", ["Yes", "No"], key="parking")
            garden = st.radio("Garden/Lawn Available?", ["Yes", "No"], key="garden")
            facilities = st.text_input("Extra facilities (e.g. lift, balcony, gym, pool):", key="facilities")
            
            submitted = st.form_submit_button("Estimate Price")

        # === If form is submitted ===
        if submitted:
            parking_bool = True if st.session_state.parking == "Yes" else False
            garden_bool = True if st.session_state.garden == "Yes" else False

            estimated = estimate_price(
                base_price,
                st.session_state.size,
                st.session_state.bedrooms,
                st.session_state.bathrooms,
                st.session_state.floors,
                st.session_state.year,
                parking_bool,
                garden_bool,
                st.session_state.facilities
            )
            estimated = min(max(estimated, 5e6), 5e8)

            st.success(f"City Tier: {tier}")
            st.success(f"Estimated House Price: ₹{estimated / 1e7:.2f} crore")
            st.caption("Goodbye! Have a great day and may your dream home find you soon!")
