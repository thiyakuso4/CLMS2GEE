import streamlit as st
import datetime as dt
from terracatalogueclient import Catalogue
from terracatalogueclient.config import CatalogueConfig, CatalogueEnvironment
import time

# --- Page setup ---
st.set_page_config(page_title="CLMS2GEE", page_icon="🌍", layout="centered")

st.title("🌍 CLMS2GEE")
st.markdown("""
### Copernicus Land Monitoring Service ➜ Google Earth Engine
**CLMS2GEE** lets you discover, download, and upload Copernicus products (e.g., DMP, NDVI)
directly to your Google Earth Engine account.
""")

# --- Session state for stopping downloads ---
if "stop_download" not in st.session_state:
    st.session_state.stop_download = False

def stop_download():
    st.session_state.stop_download = True

# --- User inputs ---
start_date = st.date_input("Start Date", dt.date(2014, 1, 1))
end_date = st.date_input("End Date", dt.date(2014, 1, 5))
version = st.selectbox("Product Version", ["RT5", "RT6"])
output_dir = st.text_input("Output Folder", "DMP_data")

col1, col2 = st.columns(2)
download_btn = col1.button("⬇️ Download Data")
stop_btn = col2.button("🛑 Stop Download", on_click=stop_download)

if download_btn:
    st.session_state.stop_download = False
    st.write("🔍 Connecting to CLMS catalogue...")
    try:
        config = CatalogueConfig.from_environment(CatalogueEnvironment.CGLS)
        catalogue = Catalogue(config)

        # Retrieve product list
        st.write("📦 Fetching product metadata...")
        products = list(
            catalogue.get_products(
                "clms_global_dmp_300m_v1_10daily_geotiff",
                start=start_date,
                end=end_date,
            )
        )

        # Filter based on RT version
        selected_products = [p for p in products if version in str(p)]

        if not selected_products:
            st.warning(f"No {version} products found for the selected date range.")
        else:
            st.success(f"Found {len(selected_products)} {version} products.")
            progress = st.progress(0, text="Starting download...")

            total = len(selected_products)
            for i, product in enumerate(selected_products, 1):
                # Check stop flag
                if st.session_state.stop_download:
                    st.warning("🛑 Download stopped by user.")
                    break

                # Download product one by one
                catalogue.download_products([product], output_dir, raise_on_failure=False)
                progress.progress(i / total, text=f"Downloading {i}/{total} products...")
                time.sleep(0.2)  # To allow UI updates

            if not st.session_state.stop_download:
                st.success("✅ All downloads completed successfully!")

    except Exception as e:
        st.error(f"❌ Error: {e}")
