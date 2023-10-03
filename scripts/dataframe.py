from sqlalchemy import create_engine
import pandas as pd

# engine = create_engine(r"postgresql://bpms:bpms@localhost:5432/bpms")
engine = create_engine(r"postgresql://jbpm:jbpm@localhost:5432/jbpm")
conn = engine.connect()

q1_start = "2023-10-01 00:00:00"
q1_end = "2023-10-01 24:00:00"

q2_start = "2023-10-02 00:00:00"
q2_end = "2023-10-02 24:00:00"

q1_query = f"SELECT lastmodificationdate, name, processinstanceid FROM ( SELECT lastmodificationdate, name, processinstanceid, ROW_NUMBER() OVER ( PARTITION BY processinstanceid ORDER BY lastmodificationdate DESC ) AS row_num FROM audittaskimpl WHERE lastmodificationdate >= '{q1_start}' AND lastmodificationdate <= '{q1_end}' AND status In ('InProgress', 'Reserved') ) AS ranked_rows WHERE row_num = 1;"  # noqa: E501
q2_query = f"SELECT lastmodificationdate, name, processinstanceid FROM ( SELECT lastmodificationdate, name, processinstanceid, ROW_NUMBER() OVER ( PARTITION BY processinstanceid ORDER BY lastmodificationdate DESC ) AS row_num FROM audittaskimpl WHERE lastmodificationdate >= '{q2_start}' AND lastmodificationdate <= '{q2_end}' AND status In ('InProgress', 'Reserved') ) AS ranked_rows WHERE row_num = 1;"  # noqa: E501

dfq1 = pd.read_sql_query(q1_query, conn)
dfq2 = pd.read_sql_query(q2_query, conn)

conn.close()

frames = [dfq1, dfq2]
result = pd.concat(frames)

print("-------------------------------------")
print(dfq1)
print("-------------------------------------")

print("-------------------------------------")
print(dfq2)
print("-------------------------------------")

active_instance_names = result['name'].drop_duplicates().reset_index(drop=True).values

balances_df = pd.DataFrame(index=list(active_instance_names), columns=['Saldo inicial', 'Nuevos', 'Terminados', 'Entradas', 'Salidas', 'Saldo Final'])

for index, row in balances_df.iterrows():
    saldo_inicial = (dfq1['name'] == index).sum()
    balances_df.at[index, "Saldo inicial"] = saldo_inicial

    filter = (dfq2['name'] == index) & (~dfq2['processinstanceid'].isin(dfq1['processinstanceid']))
    nuevos = dfq2[filter]['name'].count()
    balances_df.at[index, "Nuevos"] = nuevos

    filter = (dfq1['name'] == index) & (~dfq1['processinstanceid'].isin(dfq2['processinstanceid']))
    terminados = dfq1[filter]['name'].count()
    balances_df.at[index, "Terminados"] = terminados

    filter = (dfq2['name'] == index) & (dfq2['processinstanceid'].isin(dfq1['processinstanceid']))
    entradas = dfq2[filter]['name'].count()
    balances_df.at[index, "Entradas"] = entradas

    filter_1 = (dfq1['name'] == index) & (dfq1['processinstanceid'].isin(dfq2['processinstanceid']))
    filter_2 = (dfq2['name'] != index) & (dfq2['processinstanceid'].isin(dfq1['processinstanceid']))
    result = pd.merge(dfq1[filter_1], dfq2[filter_2], on='processinstanceid', how='inner')
    salidas = len(result)
    balances_df.at[index, "Salidas"] = salidas

    balances_df.at[index, "Saldo Final"] = saldo_inicial + nuevos - terminados + entradas - salidas

balances_df.insert(0, 'Nombre', balances_df.index)

print("-------------------------------------")
print(balances_df)
print("-------------------------------------")

indexes = dfq1['name'].drop_duplicates().reset_index(drop=True).values
columns = dfq2['name'].drop_duplicates().reset_index(drop=True).values

reclassifications_df = pd.DataFrame(index=list(active_instance_names), columns=list(active_instance_names))

for index, row in reclassifications_df.iterrows():
    for column in reclassifications_df.columns:

        dfq2_filter = (dfq2["name"] == column) & (dfq2['processinstanceid'].isin(dfq1['processinstanceid']))
        dfq1_filter = (dfq1["name"] == index) & (dfq1['processinstanceid'].isin(dfq2['processinstanceid']))

        result_1 = dfq1[dfq1_filter]
        result_2 = dfq2[dfq2_filter]

        result = pd.merge(result_1, result_2, on='processinstanceid', how='inner')

        reclassifications_df.at[index, column] = len(result)

reclassifications_df.insert(0, 'Nombre', reclassifications_df.index)

print("-------------------------------------")
print(reclassifications_df)
print("-------------------------------------")
