### Import libraries and set working directory###
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.realpath(__file__)))


### Combine data from splitwise ###
filepaths = [f for f in os.listdir("./rawdata") if f.endswith('.csv')]
my_name = 'Nicola Mori'

df = pd.DataFrame()

for i in filepaths:

    temp = pd.read_csv('rawdata/'+i)

    #Remove last row
    temp = temp[:-1]

    #Unified criteria for ammount column
    temp['Costo'] = pd.to_numeric(temp['Costo'])
    temp['Costo']=np.where(temp[my_name]==0, temp['Costo'], temp['Costo']/(len(temp.loc[:,'Valuta':].columns)-1))

    #Keep relevant columns
    temp = temp.loc[:,:'Costo']

    #Append to df
    df = pd.concat([df, temp], ignore_index=True)

#Reformat df
df['Costo'] = df['Costo'].round(2)
df['Data'] = pd.to_datetime(df['Data'])
df = df[['Costo','Data','Descrizione','Categorie']]


### Add custom categories ###
categories = pd.read_csv('splitwise_cat.csv', sep=';')

#Merge and drop irrelevant columns
df_cat = df.merge(categories, on='Categorie', how='left')
df_cat = df_cat.drop(['Categorie','Gruppi'], axis=1)


### Summarise data ###
#Group expenses by category and month
df_summ = df_cat.groupby([df_cat.Data.dt.month, df_cat.Categoria])['Costo'].sum()
df_summ = df_summ.unstack('Categoria')

df_summ = df_summ.fillna(0)

#Add total column and row
df_summ['Totale'] = df_summ.sum(axis=1)
df_summ.loc['Totale'] = df_summ.sum(axis=0)

#Generate plot
fig, ax = plt.subplots(1, 1)
ax.xaxis.tick_top() 

df_summ.iloc[:-1,:-1].plot.barh(stacked=True, figsize=(12,8), table=np.round(df_summ, 2), ax=ax)

#Save graph and categorized expenses
plt.savefig(fname='expenses_summary.png', dpi=300, facecolor='white', bbox_inches='tight')
df_cat.to_excel('expenses_detail.xlsx', index=False)



