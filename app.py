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

        # === Buttons ===
        col1, col2 = st.columns([5, 1])
        with col1:
            estimate = st.button("Estimate Price")
        with col2:
            reset_clicked = st.button("🔄", key="reset")

        # === Handle Reset
        if reset_clicked:
            confirm = st.radio("Are you sure you want to reset?", ["Cancel", "Yes"], horizontal=True, key="confirm_reset_choice")
            if confirm == "Yes":
                for key in defaults:
                    st.session_state[key] = defaults[key]
                st.success("All fields have been reset.")
                st.stop()

        # === Handle Estimate
        if estimate:
            try:
                size = float(st.session_state.size)
                bedrooms = int(st.session_state.bedrooms)
                bathrooms = int(st.session_state.bathrooms)
                floors = int(st.session_state.floors)
                year = int(st.session_state.year_built)

                if not (99 <= size <= 99999): st.warning("Size must be between 99 and 99,999 sqft."); st.stop()
                if not (1 <= bedrooms <= 9): st.warning("Bedrooms must be between 1 and 9."); st.stop()
                if not (1 <= bathrooms <= 9): st.warning("Bathrooms must be between 1 and 9."); st.stop()
                if not (1 <= floors <= 9): st.warning("Floors must be between 1 and 9."); st.stop()
                if not (1900 <= year <= 2025): st.warning("Year must be between 1900 and 2025."); st.stop()
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
