### Import libraries and set working directory###
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime

os.chdir(os.path.dirname(os.path.realpath(__file__)))


### Combine data from splitwise ###
filepaths = [f for f in os.listdir("./rawdata") if f.endswith('.csv')]
my_name = 'Nicola Mori'

df = pd.DataFrame()

for i in filepaths:

    temp = pd.read_csv('rawdata/'+i)

    #Remove unnecesary rows
    temp = temp[:-1]
    temp = temp[temp['Categorie']!='Pagamento']

    #Unified criteria for ammount column
    temp['Costo'] = pd.to_numeric(temp['Costo'])
    temp['Costo']=np.select([temp[my_name]>0, abs(temp.iloc[:,5:]).sum(axis=1)==0, temp[my_name]<0],
                            [temp['Costo']+temp.iloc[:,5:].drop(columns=[my_name]).sum(axis=1), temp['Costo'], abs(temp[my_name])], 
                            default=0)

    #Keep relevant columns
    temp = temp.loc[:,:'Costo']

    #Append to df
    df = pd.concat([df, temp], ignore_index=True)

#Reformat df
df['Costo'] = df['Costo'].round(2)
df['Data'] = pd.to_datetime(df['Data']).dt.to_period('M') #We are interested only on the month
df = df[['Costo','Data','Descrizione','Categorie']].sort_values(['Data'])

#Keep data for the last 12 months
df = df[df['Data']>=(datetime.now().date() - pd.DateOffset(months=12)).to_period('M')]


### Add custom categories ###
categories = pd.read_csv('extras/custom_cat.csv', sep=';')

#Merge and drop irrelevant columns
df_cat = df.merge(categories, on='Categorie', how='left')
df_cat = df_cat.drop(['Categorie','Gruppi'], axis=1)


### Summarise data ###
#Top spenders by month
df_topn =(df_cat[(df_cat.Categoria!='Mangiare') & (~df_cat.Descrizione.isin(['Affitto','Crossfit']))]
    .sort_values(by=['Data','Costo'], ascending=[False,False])
    .groupby('Data')
    .head(5)
    .drop(columns=['Categoria'])
    )

today=str(datetime.now().date())

with open(f'top_spenders_{today}.txt', 'w') as f:
    
    for i in df_topn['Data'].unique():
        f.write(f'Top purchases {i}:\n')
        f.write(df_topn[df_topn['Data']==i].drop(columns=['Data']).to_string(index=False, header=False))
        f.write('\n\n')


#Group expenses by category and month
df_summ = df_cat.groupby([df_cat.Data, df_cat.Categoria])['Costo'].sum()
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
today=str(datetime.now().date())

plt.savefig(fname=f'expenses_summary_{today}.png', dpi=300, facecolor='white', bbox_inches='tight')
df_cat.to_csv(f'expenses_detail_{today}.csv', sep=';', index=False)



