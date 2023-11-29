print("hello worldª")
import pandas as pd

def remove_word_from_column(column_name, word, csv_file):
    # Load data from CSV into pandas dataframe
    df = pd.read_csv(csv_file)

    # Remove word from column values
    df[column_name] = df[column_name].str.replace(word, '', case=False)

    # Save modified dataframe to a new CSV file
    new_csv_file = f"{column_name}_without_{word}.csv"
    df.to_csv(new_csv_file, index=False)

    return new_csv_file

new_csv_file = remove_word_from_column("group", "group", "professors_old.csv")
print(f"New CSV file created: {new_csv_file}")
