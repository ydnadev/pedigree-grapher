""" UI helper """
import pandas as pd
import streamlit as st

from .models import Pedigree


def show_pedigree_table(pedigree: Pedigree):
    """ Show pedigree dataframe """
    df = pd.DataFrame(
        [
            {
                "Individual ID": ind.individual_id,
                "Father ID": ind.father_id,
                "Mother ID": ind.mother_id,
                "Sex": ind.sex,
                "USGS Band ID": ind.usgs_band_id,
                "Hatch Year": ind.hatch_year,
                "Aux ID": ind.aux_id,
            }
            for ind in pedigree.relationships.values()
        ]
    )
    st.subheader("Parsed Pedigree Data")
    st.dataframe(df, use_container_width=True, height=600)

