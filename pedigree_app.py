"""Pedigree Grapher"""
from datetime import datetime

import streamlit as st

from src.models import Pedigree
from src.graph import PedigreeGraphBuilder
from src.ui import show_pedigree_table


st.set_page_config(layout="wide")
st.title("🐦 BurrowD Pedigree Grapher")

st.markdown(
    """
Upload a CSV of individuals and parents to visualize pedigrees and
filter by individual or band ID.
"""
)

uploaded_file = st.file_uploader("Upload CSV file")

if uploaded_file:
    pedigree = Pedigree.from_file(uploaded_file)
    show_pedigree_table(pedigree)

    st.write("### Focus Filters")
    individual_id = st.text_input("Enter an Individual ID (leave blank to skip)")
    band_id = st.text_input("Enter a USGS Band ID (leave blank to skip)")

    focus_id = None

    if individual_id.strip():
        if individual_id in pedigree.relationships:
            focus_id = individual_id
        else:
            st.warning(f"No match found for Individual ID: {individual_id}")
    elif band_id.strip():
        found_ids = [
            iid
            for iid, ind in pedigree.relationships.items()
            if ind.usgs_band_id == band_id
        ]
        if len(found_ids) == 1:
            focus_id = found_ids[0]
            st.info(f"Found Individual ID {focus_id} for Band {band_id}")
        elif len(found_ids) > 1:
            st.warning(
                f"Multiple Individuals found with band {band_id}: {found_ids}. "
                "Using the first one."
            )
            focus_id = found_ids[0]
        else:
            st.warning(f"No individual found with Band ID: {band_id}")

    filter_year = st.text_input(
        "Enter a Hatch Year to Filter Children (optional):"
    ).strip()
    filter_year = filter_year if filter_year else None

    subset = (
        pedigree.filter_family(focus_id, filter_year)
        if focus_id
        else pedigree.relationships
    )

    builder = PedigreeGraphBuilder(pedigree)
    png_bytes = builder.build_png(subset, focus_id=focus_id)

    if png_bytes:
        st.image(png_bytes, caption="Pedigree Graph", use_container_width=True)

        prefix = (
            focus_id
            if focus_id
            else ("band_" + band_id if band_id else "all_individuals")
        )
        SUFFIX = f"_{filter_year}" if filter_year else ""
        file_name = f"{prefix}_pedigree{SUFFIX}.png"

        st.download_button(
            label="Download PNG",
            data=png_bytes,
            file_name=file_name,
            mime="image/png",
        )
    else:
        st.error("No valid data to generate a PNG graph.")
else:
    st.info("Please upload a CSV file to begin.")

current_year = datetime.now().year
CR_STATEMENT = (
    f"Copyright (c) {current_year} "
    "Conservation Tech Lab at the San Diego Zoo Wildlife Alliance"
)
st.write(CR_STATEMENT)
