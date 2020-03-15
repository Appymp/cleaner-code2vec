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

df.columns=['code','project']

#Filter only added lines which start with '+'
df1=df[df['code'].str.startswith('+')]
df1

#apply nuanced filter criteria
##remove 'import', '@', 'public'
rem_imp=df1[~df1['code'].str.contains('import|@|public')]


# Bracket normalization
rem_brac=rem_imp.copy() # create new object so can compare before and after
rem_brac=rem_brac.reset_index().set_index('project') # set new index while preserving old index
rem_brac.columns=['line','code']
rem_brac.reset_index(inplace=True)

#  Function to insert row at specific index location. Useful for testing. 
def ins_row(row_number,df,row_value):
    start_upper=0
    end_upper=row_number
    start_lower=row_number
    end_lower=df.shape[0]
    upper_half = [*range(start_upper, end_upper, 1)]
    lower_half = [*range(start_lower, end_lower, 1)] 
    lower_half = [x.__add__(1) for x in lower_half]
    index_ = upper_half + lower_half 
    df.index = index_
    df.loc[row_number] = row_value #insert after row_number
    df = df.sort_index()
    return df

#add row to test if closing bracket operation works
row_value=[1,'test','+ {']
rem_brac=ins_row(23,rem_brac,row_value)

#iterate over each project 
for proj,rem_brac_gp in rem_brac.groupby('project'):
    o=0
    c=0
    #iterate over each line of code within filtered project
    for ind,row in rem_brac_gp.iterrows():
        if '{' in row['code']:
            o+=1
            #print('open',ind,o)
            
        if '}' in row['code']:
            c+=1
            #print('close',ind,c)
        if c > o:
            rem_brac.drop(ind,inplace=True)
            o=0
            c=0 
      
    while o > c: # add close bracket if applicable so that it balances with open brackets
        row_value=pd.DataFrame({'project':[proj],'line':'added','code':'+ }'})
        rem_brac=pd.concat([rem_brac.loc[:ind],row_value,rem_brac.loc[ind+1:]]).reset_index(drop=True)
        ind+=1 #if required next close bracket applied at next index location
        c+=1  
        

