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
rem_brac=rem_imp.copy() # create new object so can compare before and after
o=0 # intialize count variable for open brackets
c=0
#rem_brac.code.str.contains('{')
rem_brac=rem_brac.reset_index().set_index('commit') # set new index while preserving old index
rem_brac.columns=['line','code']
rem_brac.reset_index(inplace=True)

rem_brac_grpd=rem_brac.groupby('commit')
for commit,rem_brac_gp in rem_brac_grpd:
    o=0  # intialize count variable for open brackets
    c=0  # intialize count variable for close brackets
    #print (commit)
    for ind,row in rem_brac_gp.iterrows():
        if '{' in row['code']:
            o=o+1
   
        if '}' in row['code']:
            c=c+1
        
        if c > o:
            rem_brac.drop(ind,inplace=True)






