import re
import csv

def segmenter(raw_text):
    '''
    Reads the line in the txt to see it's header.
    If is_header, then it'll get the family.
    Else, it'll continue, unless the row is not an empty line.
    converts the line into dictionary and then append into a list.
    '''
    segments = []
    is_header = False
    family = ""
    for line in raw_text.split("\n"):
        if not line:  # If it's a blank line skip
            continue
        if line.startswith("===="):  # If it starts with it's either the end of a header or the start of a header
            if is_header == False:  # If is_header was false then the earlier if must have indicated the start of a header
                is_header = True
                continue  # skip to next line
            else: # If the is_header was true then the outer if indicates the end of a header
                is_header = False
                continue  # skip to next line
                
        if is_header==True: #if is_header is True, then that line is the family of the kinase
            family = line
            continue  # skip to next line
        # family | gene_name | uniprot_identifier | uniprot_number
        raw_row =  re.split(r"(\w\w*)(?:\W*)", line)
        try:
            gene_name = raw_row[1]
            uniprot_identifier = raw_row[3]
            if 'HUMAN' not in uniprot_identifier: #some line contain mouse entry only 
                continue
            uniprot_number = raw_row[5]
            segments.append({
                "family":family, 
                "gene_name":gene_name, 
                "uniprot_identifier":uniprot_identifier, 
                "uniprot_number":uniprot_number
            })
        except:
            pass
    return segments

def csv_writer(segments): 
    '''
    This function writes the the list into a csv file. 
    '''
    with open('clean_human_kinase.csv', 'w', newline='') as csvfile:
        fieldnames = ["family", "gene_name", "uniprot_identifier", "uniprot_number"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in segments:
            writer.writerow(row)


with open("raw_human_kinase.txt", "r") as f:
    raw_text = f.read()
    segments = segmenter(raw_text)
    csv_writer(segments)
