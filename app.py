import streamlit as st
import datetime as dt
from terracatalogueclient import Catalogue
from terracatalogueclient.config import CatalogueConfig, CatalogueEnvironment

# --- Page setup ---
st.set_page_config(page_title="CLMS2GEE", page_icon="🌍", layout="centered")

st.title("🌍 CLMS2GEE")
st.markdown("""
### Copernicus Land Monitoring Service ➜ Google Earth Engine
**CLMS2GEE** lets you discover, download, and upload Copernicus products (e.g., DMP, NDVI)
directly to your Google Earth Engine account.
""")

# --- User inputs ---
start_date = st.date_input("Start Date", dt.date(2014, 1, 1))
end_date = st.date_input("End Date", dt.date(2025, 4, 24))
version = st.selectbox("Product Version", ["RT5", "RT6"])
output_dir = st.text_input("Output Folder", "/mnt/d/Projects/kevin/DMP/data")

if st.button("Download Data"):
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
            st.write("⬇️ Starting download...")

            catalogue.download_products(selected_products, output_dir, raise_on_failure=False)
            st.success("✅ Download completed successfully!")

    except Exception as e:
        st.error(f"❌ Error: {e}")
