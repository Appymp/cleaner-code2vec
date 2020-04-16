#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:48:26 2020

@author: appanna
"""

import pandas as pd
import ast
import wrapper

def getfcommitcode(i, commit):
    """
    input : commit row
    output : df with java code 
    Check if java files are modified in the commit and if yes, extarct the commit code form it. 
     return a dataframe with commit number, file name and code lines. Each row is a line of code.
    """
    df = pd.DataFrame()    
    """Need to check if it is java file"""
    try:
        for file, file_code in zip(ast.literal_eval(commit['OPEN_ISSUES']),ast.literal_eval(commit['LICENCE_NAME'])):
            if file.split('.')[-1].lower() == 'java':
    #                df_temp=pd.concat([df_temp, pd.Series(file_code.split('\n'))], axis=0, ignore_index=True)
                df_temp = pd.DataFrame()
                df_temp= df_temp.assign(code= pd.Series(file_code.split('\n')))
                df_temp= df_temp.assign(file= file)
                df_temp= df_temp.assign(commit= i)
                df=pd.concat([df, df_temp], axis=0, ignore_index=True,sort=False)    
    except: 
        print("Error parsing the commint info. Likely EOF encountered")        
    return df         
#Split code string into multiple rows of a dataframe
#df=pd.concat([pd.Series(row['SI'], row['LICENCE_NAME'].split('\\n'))              
#                for _, row in repo.iterrows()]).reset_index()


def preparedata(df):
    #Filter only added lines which start with '+'
    df1=df[df['code'].str.startswith('+')]
    df1['code']=df1['code'].str[1:] #Remove the '+' from the rows
    
    #apply nuanced filter criteria
    ##remove 'import', '@', 'public', 'private'
    rem_brac=df1[~df1['code'].str.contains('import|@|public|private|package')]
        
    # Bracket normalization
    rem_brac=rem_brac.reset_index()
    #iterate over each project
    df2 = pd.DataFrame()
    for i_commit,rem_brac_cgp in rem_brac.groupby('commit'):
        file_no = 0
        for i_file,rem_brac_fgp in rem_brac_cgp.groupby('file'):

            o=0
            c=0
            os = 0 
            cs = 0
            comment_o = 0
            if_flag = 0
            file_no += 1
        #iterate over each line of code within filtered project
            for ind,row in rem_brac_fgp.iterrows():
                if '//' in row['code']: # Eliminate comments
                    row['code'] = row['code'].split('//')[0]
                if '/*' in row['code']:
                    comment_o = 1
                
                if 'else if' in row['code'] and comment_o == 0 :
                    pass
                elif 'if' in row['code'] and comment_o == 0:
                    if_flag = 1
                    
                if 'else' in row['code'] and comment_o == 0 :
                    if if_flag == 0 :
                        rem_brac_fgp.drop(ind,inplace=True)
                        continue
                    
                if '{' in row['code'] and comment_o == 0 :
                    o+=row['code'].count('{') #count the number of open brackects ??
                # small brackets 
                if '(' in row['code'] and comment_o == 0 :
                    os+= row['code'].count('(') #count the number of open brackects ??                    
                    
                if '}' in row['code'] and comment_o == 0 :
                    c+=row['code'].count('}')

                if ')' in row['code'] and comment_o == 0 :
                    cs+=row['code'].count(')') #count the number of open brackects ??                   

                if '*/' in row['code']:
                    comment_o = 0        
        
                if c > o:
                    rem_brac_fgp.drop(ind,inplace=True)
                    o=0
                    c=0 
                    
                if cs > os:
                    rem_brac_fgp.drop(ind,inplace=True)
                    os=0
                    cs=0   
                    
            while o > c: # add close bracket if applicable so that it balances with open brackets
#                print("***************more***************", o , " ", c)
                row_value=pd.DataFrame({'index':[-1], 'commit':[i_commit],'file':[row['file']],'code':['}']})
#                rem_brac=pd.concat([rem_brac.loc[:ind],row_value,rem_brac.loc[ind+1:]]).reset_index(drop=True)
                print(row_value.shape)
                rem_brac_fgp=rem_brac_fgp.append(row_value).reset_index(drop=True)
                c+=1

            # create function start
            funct_def = "static int f"+str(i_commit)+str(file_no)+"(){ "
            func_start =pd.DataFrame({'commit':[i_commit],'file':row['file'],'code':[funct_def]})
            # close the function bracket
            row_value=pd.DataFrame({'index':[-1], 'commit':[i_commit],'file':[row['file']],'code':['}']})
            rem_brac_fgp=rem_brac_fgp.append(row_value).reset_index(drop=True)

            df2 = pd.concat([df2,func_start,rem_brac_fgp], axis=0, ignore_index=True,sort=False)
        # add '\n' for every code row of rem_brac so that looks similar to working text output
        #rem_brac['code']='\n' + rem_brac['code'].astype(str) 
        
    df2['code']='\n' + df2['code']        

    return df2

def getvectors(str_code, predictor):
    """
    run the wrapper to code2vec and retrun vectors
    """
    output_filename = 'input\output.txt'
    str_code = str_code.encode('utf-8').decode('unicode_escape')
    vec = predictor.predict(str_code)
    with open(output_filename, 'at') as f:
        f.write(str_code)
        f.write('\n')
    return vec

def main():
    pd.options.display.max_colwidth = 1000 #so that the long lines of code are displayed

    repo=pd.read_excel('input\RepoCommit1_TESTSMALL.xlsx')#Read in the table
    predictor = wrapper.InteractivePredictorWrapper()
    df_out = pd.DataFrame()

    for i,row in repo.iterrows(): 
        nrow = pd.DataFrame()
        write_row = pd.DataFrame()

        if pd.isna(row['SI']):  # check if row is a repo or a commit          
            df = getfcommitcode(i,row)    
            if not df.empty: # if ast.literal_eval works on code, proceed        
                df2 = preparedata(df)
                df2.to_excel('input\cleancode.xlsx')            
                for j, cf_code in df2.groupby(['commit','file']):
                    print(i)
                    vec = getvectors(cf_code.code.to_string(index=False), predictor)
                    write_row = row[['REPO_ID','NAME','OWNER','OWNER_TYPE','SIZE','CREATE_DATE','PUSHED_DATE','MAIN_LANGUAGE','NO_LANGUAGES','SCRIPT_SIZE','STARS','SUBSCRIPTIONS']]
                    temp_ser = pd.Series([j, vec], index=['FILE_NO', 'VECTORS'])
                    write_row = write_row.append(temp_ser)
                    nrow = nrow.append( write_row, ignore_index=True)
            else:
                write_row = row[['REPO_ID','NAME','OWNER','OWNER_TYPE','SIZE','CREATE_DATE','PUSHED_DATE','MAIN_LANGUAGE','NO_LANGUAGES','SCRIPT_SIZE','STARS','SUBSCRIPTIONS']]
                temp_ser = pd.Series(["", ""], index=['FILE_NO', 'VECTORS'])
                write_row = write_row.append(temp_ser)
                nrow = nrow.append( write_row, ignore_index=True)
        else:
            nrow = nrow.append(row, ignore_index=True)
        df_out = pd.concat([df_out, nrow])
    df_out.to_excel('input/ccode.xlsx')
if __name__ == '__main__':
  main()