The source of the list of human kinases is taken from Uniprot 
(https://www.uniprot.org/docs/pkinfam). The list is saved as a csv in 
clean_human_kinase.csv. The file contains the family, gene_name, 
uniprot_identifier and the uniprot_number for each kinase.

The protein names and uniprot entry name for the kinases as well as other synonyms for the genes were 
then retrieved programmatically using the library bioservices, available 
through python3.7. The codes are in the Jupyter notebook, Protein_name_and_aliases.ipynb. The output is meta_names.csv.

It is then discovered that there are duplicates within protein aliases. 

The information for the phosphosites in DreamTeam/Data_mining/Phosphosites were taken from PhosphoSitePlus(https://www.phosphosite.org/staticDownloads). The file is clean_human_kinase_substrates.csv. However, it was found that that the kinases in the data do not match the list of kinases retrieved from Uniprot. The list of unmatched kinases are saved in unavailable_mo_kinase.csv. Upon inspection, those kinases that did not match the uniprot's list were found to be either mutation or protein that are not kinases. These entries were then dropped from the data. The new dataframe is then saved as mohan_kinase_substrate.csv.