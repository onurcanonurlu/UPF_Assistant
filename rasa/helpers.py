import csv
def transform_name(name):
    # split the name into individual parts
    parts = name.split(", ")
    # handle the case where the name has only one part (e.g., "Cher")
    if len(parts) == 1:
        return parts[0].title()
    # handle the case where the name has two parts (e.g., "John Smith")
    elif len(parts) == 2:
        first_names, surnames = parts
        # split the first names into individual parts
        name_parts = first_names.split(" ")
        # capitalize the first letter of each name part
        name_parts = [part.capitalize() for part in name_parts]
        # join the name parts with a space
        first_names = " ".join(name_parts)
        # split the surnames into individual parts
        surname_parts = surnames.split(" ")
        # capitalize the first letter of each surname part
        surname_parts = [part.capitalize() for part in surname_parts]
        # join the surname parts with a space
        surnames = " ".join(surname_parts)
        # combine the first names and surnames with a space
        return f"{surnames} {first_names} "
    # handle the case where the name has more than two parts (e.g., "Juan Carlos Perez Rodriguez")
    else:
        first_names = " ".join(parts[:-1])
        surnames = parts[-1]
        # split the surnames into individual parts
        surname_parts = surnames.split(" ")
        # capitalize the first letter of each surname part
        surname_parts = [part.capitalize() for part in surname_parts]
        # join the surname parts with a space
        surnames = " ".join(surname_parts)
        # combine the first names and surnames with a space
        return f"{surnames} {first_names}"
'''
# open the input and output CSV files
with open('professors_old.csv', newline='') as input_file, \
     open('professors_old1.csv', 'w', newline='') as output_file:

    # create a CSV reader and writer
    reader = csv.DictReader(input_file)
    writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)

    # write the header row to the output file
    writer.writeheader()

    # loop over each row in the input file
    for row in reader:
        # transform the name column and update the row
        row['name'] = transform_name(row['name'])

        # write the updated row to the output file
        writer.writerow(row)
'''
import pandas as pd


def clean_csv(input_file, output_file):
    # Load data into pandas dataframe
    df = pd.read_csv(input_file)

    # Remove trailing whitespaces from 'name' column
    df['name'] = df['name'].str.strip()

    # Save cleaned dataframe to CSV
    df.to_csv(output_file, index=False)

clean_csv('professors_old1.csv', 'professors.csv')
