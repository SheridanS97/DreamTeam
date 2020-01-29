# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 21:04:17 2020

@author: sheri
"""

#calling library
from kinase_functions import *
from kinase_declarative import *
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from pprint import pprint
import csv #loading csv package
import pandas as pd #loading pandas package
import re #loading regex package
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import math
import plotly.express as px
from scipy.stats import norm
from scipy.stats import hypergeom 
from bokeh.models import Span
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.plotting import figure, ColumnDataSource, output_notebook, show, output_file
from bokeh.models import HoverTool, WheelZoomTool, PanTool, BoxZoomTool, ResetTool, TapTool, SaveTool
from bokeh.palettes import brewer
from bokeh.resources import CDN
from bokeh.embed import file_html

engine = create_engine("sqlite:///kinase_database.db")
Base.metadata.bind = engine
session = sessionmaker(bind=engine)
s = session()


def ReadDataInput(userDataInput):

    #read in txt file
    df_input_original = pd.read_csv(userDataInput,  sep='\t')

    #There are 86 columns in the dataframe, but only 7 columns have values, the rest are empty
    #Need to remove the empty columns
    input_original_subset = df_input_original.iloc[:, 0:7]

    #Make columns 2-7 type float instead of string
    input_original_subset.iloc[:, 1:7] = input_original_subset.iloc[:, 1:7].astype(float)

    #Need to separate the phosphosite from the substrate in the first column into 2 separate columns
    input_original_subset[['Substrate','Phosphosite']] = input_original_subset.Substrate.str.split('\(|\)', expand=True).iloc[:,[0,1]]

    #Remove any rows where there are NaN in any of the columns
    input_original_subset=input_original_subset.dropna()
    #input_original_subset=input_original_subset.head(100)
    return input_original_subset

input_original_subset=ReadDataInput('az20.txt')


def Substrate_Phosphosite_List_Dict(input_original_subset):
    Sub_phosp_list=[]
    for i, j, k in zip(input_original_subset['Substrate'], input_original_subset['Phosphosite'],range(len(input_original_subset))):
        Sub_phosp_list.append([])
        Sub_phosp_list[k].append(i)
        Sub_phosp_list[k].append(j)

    return Sub_phosp_list

#print (case_list)        
Sub_Phospho_list=Substrate_Phosphosite_List_Dict(input_original_subset)


def Fetch_Kinase(Sub_Phospho_List):
    KinaseList=[]
    for i in Sub_Phospho_list:
        Sub = i[0]
        Pho = i[1]
        KinaseList.append(get_kinase_substrate_phosphosite(Sub, Pho))
          
    return KinaseList

fetched_kinase=Fetch_Kinase(Sub_Phospho_list)

def convert_dict_df(fetched_kinase):
    input_original_subset['Kinase']=fetched_kinase

    df_final = pd.concat([input_original_subset, input_original_subset['Kinase'].apply(pd.Series)], axis = 1).drop('Kinase', axis = 1)
    df_final1=df_final.drop(['substrate', 'phosphosite'], axis=1)

    df_final2=df_final1.dropna()
    df_final3=df_final2.explode('kinase')
    return df_final3

df_final3=convert_dict_df(fetched_kinase)

def NegLog10(df_final3):
    
    #Take -log10 of the corrected p-value.
    uncorrected_p_values=df_final2.iloc[ :,3].astype(np.float64)
    log10_corrected_pvalue = (-np.log10(uncorrected_p_values))

    #Append -log10(P-values) to a new column in data frame.
    df_final3["-Log10 Corrected P-Value"]=log10_corrected_pvalue
    NegLog10kinase=df_final3
    return NegLog10kinase

NegLog10KinaseDF=NegLog10(df_final3)


def log2FC(NegLog10KinaseDF):
    log2FC=np.log2(NegLog10KinaseDF.iloc[:, 1])
    NegLog10KinaseDF["Log2 Fold Change"]=log2FC
    return NegLog10KinaseDF
log2FCKinase = log2FC(NegLog10KinaseDF)
print (log2FCKinase.iloc[:,9])

def KSEA_Mean(log2FCKinase):#mS calculation
    mS = log2FCKinase.groupby('kinase')['Log2 Fold Change'].mean()
    mP = log2FCKinase['Log2 Fold Change'].mean()
    delta = log2FCKinase['Log2 Fold Change'].std()

    m=[]
    Kinase_phosphosite=log2FCKinase.groupby('kinase')['Phosphosite']
    for key, item in Kinase_phosphosite:
        m.append(len(item))

    Z_Scores=[]    
    for i, j in zip(mS, m):
        Z_Scores.append((i-mP)*math.sqrt(j)*1/delta)

    p_means=[]
    for i in Z_Scores:
        p_means.append(norm.sf(abs(i)))

    calculations_dict={'mS': mS, 'mP':mP, 'm':m, 'Delta':delta, 'Z_Scores':Z_Scores,"P_value":p_means}

    calculations_df=pd.DataFrame(calculations_dict)
    calculations_df=calculations_df.reset_index(level=['kinase'])
    return calculations_df

calculations_df=KSEA_Mean(log2FCKinase)


def KSEA_alt_mean(log2FCKinase):
    #First, need to set cut off for -log10 corrected p values
    #the cut off will be -log10 transformed 0.05 significance 
    cutOff = -np.log10(0.05)
    #Filter kinase-phosphosites by the significance cut off
    new_kinaseList=log2FCKinase.loc[log2FCKinase.iloc[:,9] > cutOff]

    mP =log2FCKinase['Log2 Fold Change'].mean()
    delta=log2FCKinase['Log2 Fold Change'].std()
    
    #Calculate m for reduced dataset
    alt_m=[]
    Kinase_phosphosite_alt=new_kinaseList.groupby('kinase')['Phosphosite']
    for key, item in Kinase_phosphosite_alt:
        alt_m.append(len(item))

    #Calculation alternative mS
    alt_mS=new_kinaseList.groupby('kinase')['Log2 Fold Change'].mean()

    #Calculate Z score:
    alt_z_scores=[]    
    for i, j in zip(alt_mS, alt_m):
        alt_z_scores.append((i-mP)*math.sqrt(j)*1/delta)

    #calculate alternative p value mean from z score
    alt_p_means=[]
    for i in alt_z_scores:
        alt_p_means.append(norm.sf(abs(i)))

    #Make dataframe for calculations
    alt_calculations_dict={'mS': alt_mS, 'mP':mP, 'm':alt_m, 'Delta':delta, 'Z_Scores':alt_z_scores,"P_value":alt_p_means}

    alt_calculations_df=pd.DataFrame(alt_calculations_dict)
    alt_calculations_df=alt_calculations_df.reset_index(level=['kinase'])
    return alt_calculations_df

alt_calculations=KSEA_alt_mean(log2FCKinase)


def VolcanoPlot(log2FCKinase):
    plot=log2FCKinase
    FC_T=1
    FC_TN=-1
    PV_T=-np.log10(0.05)

    plot.loc[(log2FCKinase['Log2 Fold Change'] > FC_T) & (log2FCKinase['-Log10 Corrected P-Value'] > PV_T), 'color' ] = "Green"  # upregulated
    plot.loc[(log2FCKinase['Log2 Fold Change'] < FC_TN) & (log2FCKinase['-Log10 Corrected P-Value'] > PV_T), 'color' ] = "Red"   # downregulated
    plot['color'].fillna('grey', inplace=True)

    output_notebook()

    category = 'Substrate'

    category_items = plot[category].unique()
    title="Volcano Plot"

    #title = Inhibitor + " :Data with identified kinases"
    #feeding data into ColumnDataSource

    source = ColumnDataSource(log2FCKinase)

    hover = HoverTool(tooltips=[('Kinase','@kinase'),
                                ('Substrate', '@Substrate'),
                                ('Phosphosite', '@Phosphosite'),
                                ('Fold_change', '@{Log2 Fold Change}'),
                                ('p_value', '@{-Log10 Corrected P-Value}')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    
    p = figure(tools=tools,title=title,plot_width=700,plot_height=400,toolbar_location='right',
           toolbar_sticky=False)
   
    p.scatter(x = 'Log2 Fold Change', y = '-Log10 Corrected P-Value',source=source,size=10,color='color')
   
    p_sig = Span(location=PV_T,dimension='width', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_over=Span(location=FC_T,dimension='height', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_under=Span(location=FC_TN,dimension='height', line_color='black',line_dash='dashed', line_width=3)

    p.add_layout(p_sig)   
    p.add_layout(fold_sig_over)   
    p.add_layout(fold_sig_under)   

    volcano = p
    return volcano

volcano=VolcanoPlot(log2FCKinase)


def html_volcano(volcano):
    html=file_html(volcano, CDN, "Volcano Plot" )
    return html
   
volc_html=html_volcano(volcano)


def kinase_activity_bar_mean(calculations_df):
    sorted_df=calculations_df.sort_values(by='mS', ascending=False).head(25)
    fig = px.bar(sorted_df, x="mS", y="kinase", orientation='h',
             hover_data=["mS", "kinase"],
             height=600,
             title='Kinase Substrate Enrichment (Mean Method)')
    
    html=file_html(fig, CDN, "Kinase Activity" )
    return html

kin_act_mean= kinase_activity_bar_mean(calculations_df)


def kinase_activity_bar_mean_alt(alt_calculations):
    alt_sorted_df = alt_calculations.sort_values(by='mS', ascending=False).head(25)

    fig = px.bar(alt_sorted_df, x="mS", y="kinase", orientation='h',
                 hover_data=["mS", "kinase"],
                 height=400,
                 title='Kinase Substrate Enrichment')
    html=file_html(kin_act, CDN, "Kinase Activity" )
    return html

kin_act_mean_alt= kinase_activity_bar_mean_alt(alt_calculations)  



