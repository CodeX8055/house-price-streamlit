import streamlit as st
from datetime import datetime, timedelta

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

# === Estimation Function ===
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

# Session init for reset confirmation
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

# Input: City
city = st.text_input("Enter your City (India):").strip().lower()

# After city is entered
if city:
    if city not in valid_cities:
        st.error("Invalid city. Please enter a valid Indian city.")
    else:
        base_price, tier = detect_city_tier(city)

        # Inputs - all blank initially
        size_input = st.text_input("Size (in sqft):")
        bedrooms_input = st.text_input("Bedrooms (1–9):")
        bathrooms_input = st.text_input("Bathrooms (1–9):")
        floors_input = st.text_input("Floors (1–9):")
        year_input = st.text_input("Year Built (1900–2025):")
        parking_input = st.selectbox("Parking Available?", ["-- Select --", "Yes", "No"])
        garden_input = st.selectbox("Garden/Lawn?", ["-- Select --", "Yes", "No"])
        facilities = st.text_input("Extra facilities (e.g. lift, balcony, gym, pool):")

        # Two buttons side-by-side
        col1, col2 = st.columns([5, 1])
        with col1:
            estimate_clicked = st.button("Estimate Price")
        with col2:
            reset_clicked = st.button("🔄", help="Reset all fields")

        # Handle Reset
        if reset_clicked:
            st.session_state.confirm_reset = True

        if st.session_state.confirm_reset:
            st.warning("Are you sure you want to reset all fields?")
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("Yes, Reset"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state["just_reset"] = True
                    st.experimental_rerun()
            with confirm_col2:
                if st.button("No"):
                    st.session_state.confirm_reset = False

        # Optional cleanup after rerun
        if "just_reset" in st.session_state:
            del st.session_state["just_reset"]

        # Handle Estimate
        if estimate_clicked:
            try:
                size = float(size_input)
                bedrooms = int(bedrooms_input)
                bathrooms = int(bathrooms_input)
                floors = int(floors_input)
                year_built = int(year_input)

                if not (99 <= size <= 99999):
                    st.warning("Size must be between 99 and 99,999 sqft.")
                    st.stop()
                if not (1 <= bedrooms <= 9):
                    st.warning("Bedrooms must be between 1 and 9.")
                    st.stop()
                if not (1 <= bathrooms <= 9):
                    st.warning("Bathrooms must be between 1 and 9.")
                    st.stop()
                if not (1 <= floors <= 9):
                    st.warning("Floors must be between 1 and 9.")
                    st.stop()
                if not (1900 <= year_built <= 2025):
                    st.warning("Year must be between 1900 and 2025.")
                    st.stop()
                if parking_input == "-- Select --" or garden_input == "-- Select --":
                    st.warning("Please select both Parking and Garden options.")
                    st.stop()

                parking = parking_input == "Yes"
                garden = garden_input == "Yes"

                estimated = estimate_price(
                    base_price, size, bedrooms, bathrooms, floors, year_built, parking, garden, facilities
                )
                estimated = min(max(estimated, 5e6), 5e8)

                st.success(f"City Tier: {tier}")
                st.success(f"Estimated House Price: ₹{estimated / 1e7:.2f} crore")
                st.caption("Goodbye! Have a great day and may your dream home find you soon!")

            except ValueError:
                st.warning("Please fill all fields correctly to continue.")
