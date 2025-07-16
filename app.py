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

# === Streamlit App ===
st.set_page_config(page_title="Indian House Price Estimator", layout="centered")
st.title("Smart Indian House Price Estimator")
st.caption("Estimate realistic house prices based on city, size, features, and facilities.")

# Init
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False
if "reset_now" not in st.session_state:
    st.session_state.reset_now = False

# Reset trigger
if st.session_state.reset_now:
    for key in list(st.session_state.keys()):
        if key not in ["confirm_reset", "reset_now"]:
            del st.session_state[key]
    st.session_state.reset_now = False
    st.stop()

# Input: City
city = st.text_input("Enter your City (India):", key="city_input").strip().lower()

if city:
    if city not in valid_cities:
        st.error("Invalid city. Please enter a valid Indian city.")
    else:
        base_price, tier = detect_city_tier(city)

        size = st.text_input("Size (in sqft):", key="size")
        bedrooms = st.text_input("Bedrooms (1–9):", key="bedrooms")
        bathrooms = st.text_input("Bathrooms (1–9):", key="bathrooms")
        floors = st.text_input("Floors (1–9):", key="floors")
        year_built = st.text_input("Year Built (1900–2025):", key="year")
        parking_input = st.selectbox("Parking Available?", ["-- Select --", "Yes", "No"], key="parking")
        garden_input = st.selectbox("Garden/Lawn?", ["-- Select --", "Yes", "No"], key="garden")
        facilities = st.text_input("Extra facilities (e.g. lift, balcony, gym, pool):", key="facilities")

        col1, col2 = st.columns([5, 1])
        with col1:
            estimate_clicked = st.button("Estimate Price")
        with col2:
            reset_clicked = st.button("🔄", help="Reset all fields")

        if reset_clicked:
            st.session_state.confirm_reset = True

        if st.session_state.confirm_reset:
            st.warning("Are you sure you want to reset all fields?")
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("Yes, Reset"):
                    st.session_state.reset_now = True
            with confirm_col2:
                if st.button("No"):
                    st.session_state.confirm_reset = False

        if estimate_clicked:
            try:
                s = float(size)
                b = int(bedrooms)
                ba = int(bathrooms)
                f = int(floors)
                y = int(year_built)

                if not (99 <= s <= 99999): st.warning("Size must be 99–99999."); st.stop()
                if not (1 <= b <= 9): st.warning("Bedrooms must be 1–9."); st.stop()
                if not (1 <= ba <= 9): st.warning("Bathrooms must be 1–9."); st.stop()
                if not (1 <= f <= 9): st.warning("Floors must be 1–9."); st.stop()
                if not (1900 <= y <= 2025): st.warning("Year must be 1900–2025."); st.stop()
                if parking_input == "-- Select --" or garden_input == "-- Select --":
                    st.warning("Please select both Parking and Garden options."); st.stop()

                parking = parking_input == "Yes"
                garden = garden_input == "Yes"

                estimated = estimate_price(base_price, s, b, ba, f, y, parking, garden, facilities)
                estimated = min(max(estimated, 5e6), 5e8)

                st.success(f"City Tier: {tier}")
                st.success(f"Estimated House Price: ₹{estimated / 1e7:.2f} crore")
                st.caption("Goodbye! Have a great day and may your dream home find you soon!")

            except ValueError:
                st.warning("Please fill all fields correctly to continue.")
