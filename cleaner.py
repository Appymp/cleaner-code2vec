#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:48:26 2020

@author: appanna
"""

import pandas as pd

#Read in the table
repo=pd.read_csv('RepoCommit1_cleaner.csv')



#Split code string into multiple rows of a dataframe
df=pd.concat([pd.Series(row['SI'], row['LICENCE_NAME'].split('\\n'))              
                    for _, row in repo.iterrows()]).reset_index()

df.columns=['code','commit']

#Filter only added lines which start with '+'
df1=df[df['code'].str.startswith('+')]
df1

#apply nuanced filter criteria
##remove 'import', '@', 'public'
rem_imp=df1[~df1['code'].str.contains('import|@|public')]
rem_imp.set_index()
rem_imp.to_csv('rem_imp',index=True)


# Bracket normalization
for i, row in rem_imp.iterrows():
    if rem_imp.commit.str.contains('{'):
        return rem_imp[i]
    
    elif rem_imp.commit.str.contains('}'):
        rem_imp.drop(i)


#package this into a function






