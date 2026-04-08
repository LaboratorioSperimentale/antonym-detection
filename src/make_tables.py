import pandas as pd 

df = pd.read_csv("data/cancella1.tsv", sep="\t", dtype = str)
new_file = "data/cancella3.csv"


df_table = pd.DataFrame(columns = df["pattern"].unique())

for index, row in df.iterrows():
    # print(index)
    # print(row["pattern"])
    
    df_table.loc[row["pair"], row["pattern"]] = row["count"]
    
df_table.to_csv(new_file, sep = "\t")
