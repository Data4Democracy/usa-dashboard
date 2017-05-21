"""
This script processes San Diego crime data downloaded with `download_latest_data.py` and organized by year with `separate_data_by_year.py`.

It creates a dataframe (csv) with the following columns:
* year
* month
* day
* offense description
* count

The reports by the San Diego Police Department do not categorize all crimes into only a few categories, so we have limited the search to the following categories (followed by keywords used).
The order of these categories is important such that an ambiguous category will be put in the first relevant category (generally more specific)
* Murder: homicide, murder
* Arson: arson, fire (not firearm),
* Assault: assault, adw, threat
* Battery: battery, gbi
* Drugs: drug, narcotic, marij, cocaine, control + subs, cannabi
* Burglary: burglary, robbery
* Motor Vehicle theft: carjacking, theft + auto, theft + vehicle
* Theft: defraud + innkeeper, theft
* Disorderly conduct: disord + conduct
* Drinking and driving: drink + drive, driv + influence, dui
* Fraud: fraud, false, personate
* Concealed weapon: conceal
* Carrying weapon: carry
* Child-related crimes: child, under 18
* Sex crimes (non-child related): sex, rape, prostitution, pimp, copulation, sodomy
* Manufacturing, selling, or transporting of illegal goods (non-drug related): manufact, mfg, sell, transport
* Vandalism: vandal
* Other gun-related crimes: firearm, f/arm, gun
* Other weapons crimes: weapon
* Other

Notes
* No row is included in the dashboard if there were no reports for that crime for that day
* Crimes are not double-counted (i.e. cannot be both a rape an attempted murder and a murder)
"""

import pandas as pd
import numpy as np


def categorize_crime(s):
    if ('homicide' in s and 'attempt' in s) or ('murder' in s and 'attempt' in s):
        return 'attempted murder'
    elif ('sex' in s) or ('rape' in s) or ('prostitution' in s) or ('pimp' in s) or ('copulation' in s) or ('sodomy' in s):
        return 'sex crimes, not child-related'
    elif ('drunk' in s and 'public' in s):
        return 'drunk in public'
    elif ('homicide' in s) or ('murder' in s):
        return 'murder'
    elif ('arson' in s) or ('fire' in s and 'firearm' not in s):
        return 'arson'
    elif ('assault' in s) or ('adw' in s) or ('threat' in s):
        return 'assault'
    elif ('battery' in s) or ('gbi' in s):
        return 'battery'
    elif ('carjacking' in s) or ('theft' in s and 'auto' in s) or ('theft' in s and 'vehicle' in s) or ('burglar' in s and 'vehicle' in s) or ('robber' in s and 'vehicle' in s) or ('theft' in s and 'car' in s):
        return 'motor vehicle theft'
    elif ('burglar' in s) or ('robber' in s):
        if 'shoplift' not in s:
            return 'burglary'
        else:
            return 'theft'
    elif 'disord' in s and 'conduct' in s:
        return 'disorderly conduct'
    elif ('dui' in s) or ('drink' in s and 'driv' in s) or ('infleunce' in s and 'driv' in s):
        return 'driving under the influence'
    elif ('fraud' in s) or ('false' in s) or ('personate' in s):
        return 'fraud'
    elif ('conceal' in s) or ('carry' in s) or ('exhibit' in s):
        return 'illegal conceal or carry of weapon'
    elif ('child' in s) or ('under 18' in s):
        if 'marijuana' not in s:
            return 'child-related crimes'
        else:
            return 'drug possession'
    elif 'vandal' in s:
        return 'vandalism'
    elif ('sell' in s) or ('transport' in s) or ('manufact' in s) or ('mfg' in s):
        return 'illegal sales, manufacture, or transport'
    elif ('drug' in s) or ('narcotic' in s) or ('marij' in s) or ('cocaine' in s) or ('cont' in s and 'subs' in s) or ('cannabi' in s):
        return 'drug possession'
    elif ('theft' in s) or ('shoplift' in s) or ('defraud' in s and 'innkeeper' in s):
        return 'theft'
    elif ('firearm' in s) or ('f/arm' in s) or ('gun' in s) or ('weapon' in s):
        return 'weapon-related crime'
    else:
        return 'other'


years = [2016, 2017]
for year in years:

        # Import data
    df = pd.DataFrame.from_csv(
        'raw_data/' + str(year) + '_records.txt', encoding='cp1252')
    df['Charge_Description_Orig'] = df['Charge_Description_Orig'].astype(
        str).str.lower()

    # Extract day, month, and year for each record
    dates = df['activityDate'].values
    df['year'] = [d.split('/')[2].split(' ')[0] for d in dates]
    df['month'] = [d.split('/')[0] for d in dates]
    df['day'] = [d.split('/')[1] for d in dates]

    # # Categorize offenses
    crime_category = [''] * len(df)
    for i, crime_str in enumerate(df['Charge_Description_Orig'].values):
        crime_category[i] = categorize_crime(crime_str)
    df['category'] = crime_category

    # Count how many times each offense occurred on each day, and save this as
    # a new dataframe
    df['count'] = np.zeros(len(df))
    df2 = df[['year', 'month', 'day', 'category', 'count']].groupby(
        ['year', 'month', 'day', 'category']).agg('count')
    df2.reset_index(inplace=True)

    # Save count of crimes
    if year == 2016:
        df2.to_csv('data/2016_startSept8.csv')
    else:
        df2.to_csv('data/' + str(year) + '.csv')
