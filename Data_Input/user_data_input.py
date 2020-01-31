# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 18:37:16 2020

@author: sheri
"""

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

input_original_subset=ReadDataInput('Ipatasertib.tsv')

##Carry out -log10 transform on P values
def NegLog10(input_original_subset):
    
    #Take -log10 of the corrected p-value.
    uncorrected_p_values=input_original_subset.iloc[ :,4].astype(np.float64)
    log10_corrected_pvalue = (-np.log10(uncorrected_p_values))

    #Append -log10(P-values) to a new column in data frame.
    input_original_subset["-Log10 Corrected P-Value"]=log10_corrected_pvalue
    NegLog10kinase=input_original_subset
    return NegLog10kinase

NegLog10KinaseDF=NegLog10(input_original_subset)


#Calculate log2FC and add as new column
def log2FC(NegLog10KinaseDF):
    log2FC=np.log2(NegLog10KinaseDF.iloc[:, 3])
    NegLog10KinaseDF["Log2 Fold Change"]=log2FC
    return NegLog10KinaseDF
log2FCKinase= log2FC(NegLog10KinaseDF)

def Substrate_Phosphosite_List_Dict(log2FCKinase):
    Sub_phosp_list=[]
    for i, j, k in zip(log2FCKinase['Substrate'], log2FCKinase['Phosphosite'],range(len(log2FCKinase))):
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

def KSEA_Mean(df_final3):#mS calculation
    df_final3=df_final3.dropna(subset = ["kinase"])
    
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
    
    return calculations_df
calculations_df=KSEA_Mean(df_final3)
calculations_df

def VolcanoPlot_Sub(kinaseList):

    FC_T=1
    FC_TN=-1
    PV_T=-np.log10(0.05)

    kinaseList.loc[(kinaseList['Log2 Fold Change'] > FC_T) & (kinaseList['-Log10 Corrected P-Value'] > PV_T), 'color' ] = "Green"  # upregulated
    kinaseList.loc[(kinaseList['Log2 Fold Change'] < FC_TN) & (kinaseList['-Log10 Corrected P-Value'] > PV_T), 'color' ] = "Red"   # downregulated
    kinaseList['color'].fillna('grey', inplace=True)

    output_notebook()

    category = 'Substrate'

    category_items = kinaseList[category].unique()
    title="Volcano Plot"

    #title = Inhibitor + " :Data with identified kinases"
    #feeding data into ColumnDataSource

    source = ColumnDataSource(kinaseList)

    hover = HoverTool(tooltips=[
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

    return p
VolcanoPlotSub=VolcanoPlot_Sub(log2FCKinase)


def VolcanoPlot(kinaseList):

    FC_T=1
    FC_TN=-1
    PV_T=-np.log10(0.05)

    kinaseList.loc[(kinaseList['Log2 Fold Change'] > FC_T) & (kinaseList['-Log10 Corrected P-Value'] > PV_T), 'color' ] = "Green"  # upregulated
    kinaseList.loc[(kinaseList['Log2 Fold Change'] < FC_TN) & (kinaseList['-Log10 Corrected P-Value'] > PV_T), 'color' ] = "Red"   # downregulated
    kinaseList['color'].fillna('grey', inplace=True)

    output_notebook()

    category = 'Substrate'

    category_items = kinaseList[category].unique()
    title="Volcano Plot"

    #title = Inhibitor + " :Data with identified kinases"
    #feeding data into ColumnDataSource

    source = ColumnDataSource(kinaseList)

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

    
    return p

volcano_plot=VolcanoPlot(df_final3)



from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

def EnrichmentPlot(calculations_df):

    reduc_calculations_df=calculations_df[calculations_df['m']>= 4]
    reduc_calculations_df=reduc_calculations_df.sort_values(by='Enrichment')

    reduc_calculations_df.loc[(reduc_calculations_df['P_value'] < 0.05), 'color'] = "Orange"  # significance 0.05# significance 0.01
    reduc_calculations_df.loc[(reduc_calculations_df['P_value'] > 0.05), 'color' ] = "Black"

    kinase=reduc_calculations_df['kinase']

    enrichment=reduc_calculations_df['Enrichment']
    source = ColumnDataSource(reduc_calculations_df)



    hover = HoverTool(tooltips=[('Enrichment)','@Enrichment'),
                                ('Number of Substrates', '@m'),
                                ('P-value', 'P_value')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    p = figure(tools=tools, y_range=kinase, x_range=((enrichment.min()-5), (enrichment.max()+5)), plot_width=600, plot_height=800, toolbar_location=None,
           title="Kinase Substrate Enrichment",)
    p.hbar(y="kinase", left=0, right='Enrichment', height=0.3, color= 'color', source=source)

    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = "Enrichment (mS/mP)"
    p.yaxis.axis_label = "Kinase"
    p.outline_line_color = None

    return p
#df_final3.head(25)

enrich_plot=EnrichmentPlot(calculations_df)
show(enrich_plot)

from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6

###Total serine phophorylated
#Total significantly upregulated
#total significantly downregulated
phos_ser_sig=phos_ser_list[phos_ser_list.iloc[:,8]>np.log(0.05)]
phos_ser_nonsig=sum(phos_ser_list.iloc[:,8]<np.log(0.05))


phos_tyr_sig=phos_tyr_list[phos_tyr_list.iloc[:,8]>np.log(0.05)]
phos_tyr_nonsig=sum(phos_tyr_list.iloc[:,8]<np.log(0.05))

phos_thr_sig=phos_thr_list[phos_thr_list.iloc[:,8]>np.log(0.05)]
phos_thr_nonsig=sum(phos_thr_list.iloc[:,8]>np.log(0.05))

ser_upreg=sum(phos_ser_sig.iloc[:,9]>0)
ser_downreg=sum(phos_ser_sig.iloc[:,9]<0)
thr_upreg=sum(phos_thr_sig.iloc[:,9]>0)
thr_downreg=sum(phos_thr_sig.iloc[:,9]<0)
tyr_upreg=sum(phos_tyr_sig.iloc[:,9]>0)
tyr_downreg=sum(phos_tyr_sig.iloc[:,9]<0)

#print phos_ser_list
residues=["Serine","Threonine", "Tyrosine"]

data = {'Residues': ["Serine", "Threonine", "Tyrosine"],
        'Upregulated': [ser_upreg, thr_upreg, tyr_upreg],
        'Downregulated': [ser_downreg, thr_downreg, tyr_downreg],
        'Nonsignificant': [phos_ser_nonsig, phos_ser_nonsig, phos_thr_nonsig]}


regulation = ['Upregulated', 'Downregulated', 'Non-Significant']


x = [ (residue, reg) for residue in residues for reg in regulation ]
counts = sum(zip(data['Upregulated'], data['Downregulated'], data['Nonsignificant']), ()) # like an hstack

source = ColumnDataSource(data=dict(x=x, counts=counts))

p = figure(x_range=FactorRange(*x), plot_height=500, title="Residue phosphorylation",
           toolbar_location=None, tools="")

p.vbar(x='x', top='counts', width=0.9, source=source,line_color="white",
       fill_color=factor_cmap('x', palette=Spectral6, factors=regulation, start=1, end=2))
p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None
p.yaxis.axis_label = "Number of Residues Phosphorylated"

show(p)

residuePlot=p


def html_volcano(volcano):
    html=file_html(volcano, CDN, "Volcano Plot of Substrates" )
    return html
   
volcSub_html=html_volcano(VolcanoPlotSub)
 

def html_volcano(volcano):
    html=file_html(volcano, CDN, "Volcano Plot of Filtered Kinases" )
    return html
   
volcKin_html=html_volcano(volcano_plot)


def html_volcano(volcano):
    html=file_html(volcano, CDN, "Kinase Substrate Enrichment" )
    return html
   
enrich_html=html_volcano(enrich_plot)

def html_volcano(volcano):
    html=file_html(volcano, CDN, "Phosphorylated Residues Plot" )
    return html
   
res_html=html_volcano(residuePlot)








