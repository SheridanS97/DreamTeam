# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 18:37:16 2020

@author: sheri
"""

from Database.kinase_functions import *
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
from bokeh.models import Span
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.plotting import figure, ColumnDataSource, output_notebook, show, output_file
from bokeh.models import HoverTool, WheelZoomTool, PanTool, BoxZoomTool, ResetTool, TapTool, SaveTool
from bokeh.palettes import brewer


#FC=2
#p_val=0.01
#CV=100

def data_analysis(filename, CV):
    
    #read in txt file
   # df_input_original = pd.read_csv(filename, sep='\t')
   df_input_original = pd.read_csv("../app/instance/Data_Upload/"+ filename,  sep='\t')
    
    #There are 86 columns in the dataframe, but only 7 columns have values, the rest are empty
    #Need to remove the empty columns
    input_original_subset = df_input_original.iloc[:, 0:7]
    
    col_number=  input_original_subset.shape[1]

    if col_number == 5:
        input_original_subset["control_cv"] = 1
        input_original_subset["condition_cv"] = 1        
        
    df_cols=["Substrate", "control_mean", "inhibitor_mean", "fold_change", "p_value", "ctrlCV", "treatCV" ]

    input_original_subset.columns=df_cols
    
    #Make columns 2-7 type float instead of string
    input_original_subset.iloc[:, 1:7] = input_original_subset.iloc[:, 1:7].astype(float)

    #Need to separate the phosphosite from the substrate in the first column into 2 separate columns
    input_original_subset[['Substrate','Phosphosite']] = input_original_subset.Substrate.str.split('\(|\)', expand=True).iloc[:,[0,1]]

    #Remove any rows where there are NaN in any of the columns
    input_original_subset=input_original_subset.dropna()
    #input_original_subset=input_original_subset.head(100)
   
    #Take -log10 of the corrected p-value.
    uncorrected_p_values=input_original_subset.iloc[ :,4].astype(np.float64)
    log10_corrected_pvalue = (-np.log10(uncorrected_p_values))

    #Append -log10(P-values) to a new column in data frame.
    input_original_subset["-Log10 Corrected P-Value"]=log10_corrected_pvalue
    NegLog10Kinase=input_original_subset
    
    log2FC=np.log2(NegLog10Kinase.iloc[:, 3])
    NegLog10Kinase["Log2 Fold Change"]=pd.Series(log2FC)
    
    log2FCKinase = NegLog10Kinase
   
    log2FCKinase.loc[:, "Log2 Fold Change"].replace([np.inf, -np.inf], np.nan, inplace=True)
    final_substrate=log2FCKinase
   
    # Replace nan with 0.
    log2FCKinase.loc[:, "Log2 Fold Change"] =log2FCKinase.loc[:,"Log2 Fold Change"].fillna(0)
   
    Final_substrate=log2FCKinase
    Sub_phosp_list=[]
    for i, j, k in zip(log2FCKinase['Substrate'], log2FCKinase['Phosphosite'],range(len(log2FCKinase))):
        Sub_phosp_list.append([])
        Sub_phosp_list[k].append(i)
        Sub_phosp_list[k].append(j)
        
    KinaseList=[]
    for i in Sub_phosp_list:
        Sub = i[0]
        Pho = i[1]
        KinaseList.append(get_kinase_substrate_phosphosite(Sub, Pho))
          
    input_original_subset['Kinase']=KinaseList

    df_final = pd.concat([input_original_subset, input_original_subset['Kinase'].apply(pd.Series)], axis = 1).drop('Kinase', axis = 1)
    df_final1=df_final.drop(['substrate', 'phosphosite'], axis=1)

    df_final2=df_final1.dropna()
    df_final2=df_final2.explode('kinase')
    df_final3=df_final2.dropna(subset = ["kinase"])
    
    df_final3= df_final3[(df_final3['ctrlCV'] <=  CV) & (df_final3['treatCV'] <= CV)]  
    
    mS = df_final3.groupby('kinase')['Log2 Fold Change'].mean()
    mP = df_final3['Log2 Fold Change'].mean()
    delta=df_final3['Log2 Fold Change'].std()

    m=[]
    Kinase_phosphosite=df_final3.groupby('kinase')['Phosphosite']
    for key, item in Kinase_phosphosite:
        m.append(len(item))

    Z_Scores=[]    
    for i, j in zip(mS, m):
        Z_Scores.append((i-mP)*math.sqrt(j)*1/delta)

    p_means=[]
    for i in Z_Scores:
        p_means.append(norm.sf(abs(i)))
        
    enrichment=mS/mP
    
    calculations_dict={'mS': mS, 'mP':mP, 'm':m, 'Delta':delta, 'Z_Scores':Z_Scores,"P_value":p_means,"Enrichment":enrichment}

    calculations_df=pd.DataFrame(calculations_dict)
    calculations_df=calculations_df.reset_index(level=['kinase'])
    final_substrate=final_substrate.drop(['Kinase'], axis=1)
    
    #user define CV value: Rows Above CV filtered out
    
    return (calculations_df, final_substrate ,df_final3) #calculations_df)

#calculations, final_substrate, df_final3=data_analysis('AZD5438.tsv', CV)

def VolcanoPlot_Sub(filename, CV, p_val, FC):
    calculations_df, final_substrate, df_final3=data_analysis(filename, CV)
    
    
    FC_N = -FC
    PV=-np.log10(p_val)

    final_substrate.loc[(final_substrate['Log2 Fold Change'] > FC) & (final_substrate['-Log10 Corrected P-Value'] > PV), 'color' ] = "Green"  # upregulated
    final_substrate.loc[(final_substrate['Log2 Fold Change'] < FC_N) & (final_substrate['-Log10 Corrected P-Value'] > PV), 'color' ] = "Red"   # downregulated
    final_substrate['color'].fillna('grey', inplace=True)

    output_notebook()

    category = 'Substrate'

    category_items = final_substrate[category].unique()
    title="Volcano Plot"

    source = ColumnDataSource(final_substrate)

    hover = HoverTool(tooltips=[
                                ('Substrate', '@Substrate'),
                                ('Phosphosite', '@Phosphosite'),
                                ('Fold_change', '@{Log2 Fold Change}'),
                                ('p_value', '@{-Log10 Corrected P-Value}')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    
    p = figure(tools=tools,title=title,plot_width=700,plot_height=400,toolbar_location='right',
           toolbar_sticky=False)
   
    p.scatter(x = 'Log2 Fold Change', y = '-Log10 Corrected P-Value',source=source,size=10,color='color')
   
    p_sig = Span(location=PV,dimension='width', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_over=Span(location=FC,dimension='height', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_under=Span(location=FC_N,dimension='height', line_color='black',line_dash='dashed', line_width=3)

    p.add_layout(p_sig)   
    p.add_layout(fold_sig_over)   
    p.add_layout(fold_sig_under)   

    html=file_html(p, CDN, "Volcano Plot of Substrates" )
    return html

#VolcanoPlotSub=VolcanoPlot_Sub('AZD5438.tsv', CV, p_val, FC)


def VolcanoPlot(filename, CV, p_val, FC):
    calculations_df, final_substrate, df_final3=data_analysis(filename, CV)
    
    FC_N=-FC
    PV=-np.log10(p_val)

    df_final3.loc[(df_final3['Log2 Fold Change'] > FC) & (df_final3['-Log10 Corrected P-Value'] > PV), 'color' ] = "Green"  # upregulated
    df_final3.loc[(df_final3['Log2 Fold Change'] < FC_N) & (df_final3['-Log10 Corrected P-Value'] > PV), 'color' ] = "Red"   # downregulated
    df_final3['color'].fillna('grey', inplace=True)

    output_notebook()

    category = 'Substrate'

    category_items =df_final3[category].unique()
    title="Volcano Plot"

    #title = Inhibitor + " :Data with identified kinases"
    #feeding data into ColumnDataSource

    source = ColumnDataSource(df_final3)

    hover = HoverTool(tooltips=[('Kinase','@kinase'),
                                ('Substrate', '@Substrate'),
                                ('Phosphosite', '@Phosphosite'),
                                ('Fold_change', '@{Log2 Fold Change}'),
                                ('p_value', '@{-Log10 Corrected P-Value}')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    
    p = figure(tools=tools,title=title,plot_width=700,plot_height=400,toolbar_location='right',
           toolbar_sticky=False)
   
    p.scatter(x = 'Log2 Fold Change', y = '-Log10 Corrected P-Value',source=source,size=10,color='color')
   
    p_sig = Span(location=PV,dimension='width', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_over=Span(location=FC,dimension='height', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_under=Span(location=FC_N,dimension='height', line_color='black',line_dash='dashed', line_width=3)

    p.add_layout(p_sig)   
    p.add_layout(fold_sig_over)   
    p.add_layout(fold_sig_under)   

    html=file_html(p, CDN, "Volcano Plot of Filtered Kinases" )
    return html
#Volc_plot=VolcanoPlot('AZD5438.tsv',CV, p_val, FC)

def EnrichmentPlot(filename, CV, p_val, FC):
    calculations_df, df_final2, df_final3=data_analysis(filename,CV)
    
    reduc_calculations_df=calculations_df[calculations_df['m']>= 4]
    reduc_calculations_df=reduc_calculations_df.sort_values(by='Enrichment')

    reduc_calculations_df.loc[(reduc_calculations_df['P_value'] < p_val), 'color'] = "Orange"  # significance 0.05# significance 0.01
    reduc_calculations_df.loc[(reduc_calculations_df['P_value'] > p_val), 'color' ] = "Black"

    kinase=reduc_calculations_df['kinase']

    enrichment=reduc_calculations_df['Enrichment']
    source = ColumnDataSource(reduc_calculations_df)

    hover = HoverTool(tooltips=[('Enrichment)','@Enrichment'),
                                ('Number of Substrates', '@m'),
                                ('P-value', '@P_value')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    p = figure(tools=tools, y_range=kinase, x_range=((enrichment.min()-5), (enrichment.max()+5)), plot_width=600, plot_height=800, toolbar_location=None,
           title="Kinase Substrate Enrichment",)
    p.hbar(y="kinase", left=0, right='Enrichment', height=0.3, color= 'color', source=source)

    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = "Enrichment (mS/mP)"
    p.yaxis.axis_label = "Kinase"
    p.outline_line_color = None

    html=file_html(p, CDN, "Kinase Substrate Enrichment" )
    return html

#enrich=EnrichmentPlot('AZD5438.tsv',CV, p_val, FC)


def df_html(filename, CV):
    calculations_df, final_substrate, df_final3=data_analysis(filename,CV)
    df_calc=calculations_df.to_html()
    return df_calc
#df1_html=df_html('AZD5438.tsv', CV)


def df2_html(filename,CV):
    calculations_df, final_substrate, df_final3=data_analysis(filename,CV)
    df_final_html=df_final3.to_html()
    return df_final_html
#df2_html=df_final_html('AZD5438.tsv', CV)  