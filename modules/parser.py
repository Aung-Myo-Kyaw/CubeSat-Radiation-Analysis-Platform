import pandas as pd


def load_csv(file):
    return pd.read_csv(file)


def get_max_dose(df):
    return df["Dose_Gy"].max()


def get_min_dose(df):
    return df["Dose_Gy"].min()


def get_max_let(df):
    return df["LET_keV_um"].max()