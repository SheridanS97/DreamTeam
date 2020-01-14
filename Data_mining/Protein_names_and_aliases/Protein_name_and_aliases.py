#!/usr/bin/env python
# coding: utf-8

# # Getting protein name and other synonyms 

# ## Source: uniprot

# In[21]:


#import library
import pandas as pd
import re


# In[8]:


#install the library i fyour don't have it
# !pip install bioservices
from bioservices import UniProt


# In[2]:


#read csv file into dataframe
kinase_df = pd.read_csv('../Human_kinase_list/clean_human_kinase.csv', index_col=0)
kinase_df.head()


# In[53]:


#unprocessed uniprot_number
unprocessed_list = kinase_df['Uniprot_number'].tolist()
unprocessed_list


# In[5]:


#turn gene name into a list
up_num_list = kinase_df['Uniprot_number'].str.rstrip().tolist() #rstrip to remove the white spaces
up_num_list


# In[19]:


#using bioservices
u = UniProt(verbose=False)
u.search("id:P31751", limit=1, columns="id,protein names")


# In[22]:


#split the output by multiple seps
example = u.search("id:P31751", limit=1, columns="id,protein names")
re.split('\t|\n', example)


# In[27]:


#retrieve the protein names
ex_str = re.split('\t|\n', example)
ex_str[3].split('(')[0].rstrip()


# In[78]:


#create a function to get the uniprot_number, gene_name, protein_name, gene_aliases
def get_meta(uniprot_num):
    """
    Takes in a uniprot number.
    Returns the uniprot_number, gene_name, protein_name, gene_aliases as a tuple.
    """
    query = "id:{}".format(uniprot_num)
    output = u.search(query, limit=1, columns="id,protein names, genes(PREFERRED), genes")
    tmp = re.split('\t|\n', output)
    protein_name = tmp[5].split('(')[0].rstrip()
    gene_name = tmp[6]
    gene_aliases = tmp[7].split()
    return(uniprot_num, gene_name, protein_name, gene_aliases)
get_meta('Q5VT25')


# In[83]:


#get all the protein names
total = []
for num in up_num_list:
    tmp = get_meta(num)
    if len(tmp) < 4:
        print(tmp)
    else:
        total.append(tmp)
total


# In[84]:


#convert the list into dataframe
meta_df = pd.DataFrame(total, columns=['Uniprot_number','Gene_name','Protein_name','Gene_aliases'])
meta_df.head()


# In[86]:


#turn the meta df into csv file
meta_df.to_csv('meta_names.csv', header=True, index=False)


# The metadata is now available
