from __future__ import print_function
from __future__ import division
# load libraries
from builtins import str
from builtins import range
from past.utils import old_div
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd
import sys
import os
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import shapely
import geopy
import argparse
import io 
import unicodedata
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import glob 
import pickle 
from os.path import expanduser
import pdb 
import unidecode 
import importlib 

importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

#####################################################
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d) 


################################################
def string_2_bool(string):
    if  string in ['true', 'TRUE' , 'True' , '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        return  True
    else:
        return False

################################################
def saveplot(appellations_domain,vin,metropole,bassins):

    #to set extent
    appellations_domain = gpd.GeoDataFrame(pd.DataFrame(appellations_domain), crs=appellations.crs)
    if len(appellations_domain)>0: 
        xmin,ymin, xmax,ymax = appellations_domain.total_bounds
    elif len(bassins.loc[bassins.nom == vin.Bassin]) == 0: 
        xmin,ymin,xmax,ymax = 0, 0, 0, 0 
    else:
        xmin,ymin,xmax,ymax = bassins.loc[bassins.nom == vin.Bassin].total_bounds
                              #vin.geometry.coords.xy[0][0]-1.e5, vin.geometry.coords.xy[0][0]+1.e5,\
                              #vin.geometry.coords.xy[1][0]-1.e5, vin.geometry.coords.xy[1][0]+1.e5
    if vin.Bassin == 'Bourgogne': buffer_lim = 130.e3
    elif u'domainedelamordor' in vin.DomaineChateau.replace('&','').replace(' ','').lower()  : buffer_lim = 50.e3
    else: buffer_lim = 200.e3

    '''
    for side in ax.spines.keys():  # 'top', 'bottom', 'left', 'right'
        ax.spines[side].set_linewidth(1)
    
    for side in bx.spines.keys():  # 'top', 'bottom', 'left', 'right'
        bx.spines[side].set_linewidth(1)
    '''

    xx = xmax-xmin;  yy = ymax-ymin
    xc = xmin+.5*xx; yc = ymin+.5*yy
    dd = max([xx,yy,buffer_lim])
    xmin = xc-.5*dd;  xmax = xc+.5*dd
    ymin = yc-.5*dd;  ymax = yc+.5*dd
    bufferZone_map = 10.e3
    
    ax.set_xlim(xmin-bufferZone_map, xmax+bufferZone_map)
    ax.set_ylim(ymin-bufferZone_map, ymax+bufferZone_map)

    #ax.legend(handles = LegendElement_domain, loc='upper right', labelspacing=1.1, handlelength=2.5, handleheight=1.9)
    ax.legend(handles = LegendElement_domain, labelspacing=.7, handlelength=2.5, handleheight=1.9, ncol=int(vin['legend_nbreColumn']), loc=vin['legend_loc'], 
              fancybox=True, framealpha=0.9 )
    # for multiple column
    # probably need to add column in excel file to tell where to put the legend and the number of columns
    #https://stackoverflow.com/questions/42103144/how-to-align-rows-in-matplotlib-legend-with-2-columns
    
    # frame of left plot is not good. try better framing
    #chateauAmpuis is doing weird stuff on the legend
    # find a solution for alsace appellations
    #add igp 

    if (vin.Pays == 'France') | (vin.Pays == 'Hongrie'):
        #add prefecture
        if vin.DomaineChateau == u'Ch\xe2teau La Borie':
            selectedCommune = ['Nice', 'Marseille', 'Montpellier', 'Avignon', 'Gap', 'Valence', 'Bastia', 'Ajaccio'] 
        elif vin.DomaineChateau == u'Les Vignobles de Seyssuel':
            selectedCommune = ['Lyon', 'Saint-Étienne', 'Grenoble', 'Valence', 'Chambéry', ] 
        else:
            selectedCommune = prefectures.Commune.to_list() 
        prefectures.loc[prefectures.Commune.isin(selectedCommune)].plot(ax=ax, color='k', markersize=20,)
        prefectures.loc[prefectures.Commune.isin(selectedCommune)].apply(lambda x: ax.annotate(text=str(x.Commune),\
                                            xy=[x.geometry.centroid.x + x.add_to_name_position.coords.xy[0][0],\
                                                x.geometry.centroid.y + x.add_to_name_position.coords.xy[1][0] ], ha=x.LabelLoc_ha,va=x.LabelLoc_va,zorder=5),axis=1);

    try:
        minx, miny, maxx, maxy =  metropole.geometry.total_bounds
        xx = maxx-minx;  yy = maxy-miny
        xc = minx+.5*xx; yc = miny+.5*yy
        dd = max([xx,yy])
        minx = xc-.5*dd;  maxx = xc+.5*dd
        miny = yc-.5*dd;  maxy = yc+.5*dd
    except: 
        minx = 0;  maxx = 0
        miny = 0;  maxy = 0

    buffer_lim = 50.e3
    bx.set_xlim(minx-buffer_lim,maxx+buffer_lim)
    bx.set_ylim(miny-buffer_lim,maxy+buffer_lim)

    # add image location and France map 
    rect = mpatches.Rectangle((xmin-bufferZone_map,ymin-bufferZone_map),(xmax-xmin)+2*bufferZone_map,\
                                                                       (ymax-ymin)+2*bufferZone_map, linewidth=1, edgecolor='k', facecolor='none')
    bx.add_patch(rect)

    fig.savefig(map_domain, dpi=dpi_map, facecolor=fig.get_facecolor())
    plt.close(fig)


def simple_appelation(appelation):
    if appelation == 'Alsace Gewurztraminer': return 'Alsace'
    if appelation == 'Alsace Riesling'      : return 'Alsace'
    if appelation == 'Alsace Pinot Noir'    : return 'Alsace'
    return appelation



##########################
if __name__ == '__main__':
##########################
    
    parser = argparse.ArgumentParser(description='draw wine map')
    parser.add_argument('-s','--flag_start', help='False if input files needed to be reloaded',required=False)
    parser.add_argument('-v','--flag_vin',   help='True if only wine list need to be reloaded',required=False)
    parser.add_argument('-b','--flag_border',   help='True if reload border shapefile',required=False)
    args = parser.parse_args()

    home = expanduser("~")
    # where are the input data
    dir_in = home+'/Dropbox/CarteVin/'

    # where to generate vin.tex
    dir_out = './'
    wkdir =  dir_out + 'VinData/'
    ensure_dir(wkdir)

    #listDesVins
    file_listDesVins = home+'/Dropbox/CarteVin/MaCave/ListeDesVins.xlsx'

    dpi_largePlot = 100
    dpi_map = 100

    #define Input
    if args.flag_start is None:
        flag_restart =  True
    else:
        flag_restart = string_2_bool(args.flag_start)

    if args.flag_vin is None:
        flag_vin =  False
    else:
        flag_vin = string_2_bool(args.flag_vin)
    
    if args.flag_border is None:
        flag_border =  False
    else:
        flag_border = string_2_bool(args.flag_border)

    ######################
    # france border contour
    ######################
    if ((flag_border) or (not(os.path.isfile(wkdir+"metropole.shp")))):
        print('france border contour ...')
        fp = dir_in+'communes-20150101-5m-shp/communes-20150101-5m.shp'
        map_dfCommune = gpd.read_file(fp)
        map_dfCommune = map_dfCommune.rename(columns={'nom':'Commune'})
        map_dfCommune['metropole'] = 0 
        map_dfCommune.loc[ pd.to_numeric(map_dfCommune['insee'], errors='coerce') < 97000, 'metropole'] = 1 
        map_dfCommune.loc[map_dfCommune['insee'].str.contains('2A'), 'metropole'] = 1
        map_dfCommune.loc[map_dfCommune['insee'].str.contains('2B'), 'metropole'] = 1 
        map_dfCommune.to_file(wkdir+"map_df_communes.shp")

        metropole_geometry = map_dfCommune[['metropole','geometry']].dissolve(by='metropole')
        metropole = gpd.GeoDataFrame(pd.DataFrame({'countryMainLand': ['France,']}),geometry=[metropole_geometry.geometry[1]],crs=metropole_geometry.crs)
        metropole = metropole.to_crs(epsg=3395)
        metropole.to_file(wkdir+"metropole.shp")
    else: 
        metropole     = gpd.read_file(wkdir+"metropole.shp")
        map_dfCommune = gpd.read_file(wkdir+"map_df_communes.shp")



    ######################
    #load appelation
    ######################
    listAppellations = pd.read_csv(dir_in+'liste-AOC-vins-wikipedia.csv')
    listAppellations['Appellation'] = listAppellations['Appellation'].str.strip()
    listAppellations['Bassin'] = listAppellations['Bassin'].str.strip()


    ######################
    #load bassins color code
    ######################
    listBassinColor = pd.read_csv(dir_in+'bassins-colors.csv')
    listBassinColor['Bassin'] = [str(xx) for xx in listBassinColor['Bassin']]


    ######################
    #load vines list
    ######################
    if ((flag_vin) or (not(flag_restart)) or (not(os.path.isfile(wkdir+"listVins.gpkg")))):
        print('list vins de la cave ...')
        print('le fichier est ici : ', file_listDesVins)
        
        vins_ = pd.read_excel(file_listDesVins, sheet_name='france - Liste des vins', header=2)
        vins_ = vins_.loc[ (vins_['Couleur'].str.strip()=='Blanc') |
                           (vins_['Couleur'].str.strip()==u'Blanc p\xe9tillant') |
                           (vins_['Couleur'].str.strip()=='Rouge') |
                           (vins_['Couleur'].str.strip()==u'Ros\xe9') |
                           (vins_['Couleur'].str.strip()==u'Pommeau') 
                         ]
        
        vins_2_ = pd.read_excel(file_listDesVins, sheet_name='international - Liste des vins ', header=1)
        vins_2_ = vins_2_.loc[ (vins_['Couleur'].str.strip()=='Blanc') |
                           (vins_['Couleur'].str.strip()==u'Blanc p\xe9tillant') |
                           (vins_['Couleur'].str.strip()=='Rouge') |
                           (vins_['Couleur'].str.strip()==u'Ros\xe9') |
                           (vins_['Couleur'].str.strip()==u'Pommeau') 
                         ]

        cidres_ = pd.read_excel(file_listDesVins, sheet_name='cidre - Liste des Cidres', header=1)
        cidres_.index = list(range(len(vins_),len(vins_)+len(cidres_)))
       


        listVins = pd.concat([ vins_, cidres_, vins_2_ ], sort=True,
                ignore_index=True)
        #listVins = pd.concat([ vins_2_ ], sort=True)
        
        #clean data
        listVins = listVins.loc[ (listVins['Couleur'].str.strip()=='Blanc') |
                                 (listVins['Couleur'].str.strip()==u'Blanc p\xe9tillant') |
                                 (listVins['Couleur'].str.strip()=='Rouge') |
                                 (listVins['Couleur'].str.strip()==u'Ros\xe9') |
                                 (listVins['Couleur'].str.strip()==u'Cidre') |
                                 (listVins['Couleur'].str.strip()==u'Pommeau') 
                                 ]
         
        geocoder = geopy.geocoders.BANFrance()
        geocoder_bing = None
        cave = geocoder.geocode('4 rue Coat Tanguy 29890 Brignogan-Plages')
        listVins['latlong'] = [cave.point]*listVins.shape[0]
        for index, row in listVins.iterrows():
            address1 = row['Adresse'].split(' ')
            address2 = []
            for address_ in address1:
                tmp_ = address_.rstrip(',').rstrip(' ')
                if tmp_ != '':
                    address2.append(tmp_)
            address3 = '{:s} {:05.0f} {:s} {:s}'.format( ' '.join(address2[:-1]), row['Code postal'], address2[-1], row['Pays'])
            try:
                if row['Pays'] == 'France':
                    listVins.at[index,'latlong'] = geocoder.geocode(address3,timeout=3).point
                else:
                    if geocoder_bing == None:
                        key_bing = 'AiyOW-9p89aIFYUSZqLTAyCZlIfxDUENcUBqnZ6YB7muWDTF7-QBeZet_R0dw7cB'
                        geocoder_bing = geopy.geocoders.Bing(key_bing)
                    listVins.at[index,'latlong'] = geocoder_bing.geocode(address3,timeout=3).point

            except geopy.exc.GeocoderTimedOut : 
                print('geopy timeout on :', address3)
                sys.exit()
            #print address3, ' | ', listVins.at[index,'latlong']
        
        lats = [pt.latitude for pt in listVins['latlong']]
        lons = [pt.longitude for pt in listVins['latlong']]
        listVins = gpd.GeoDataFrame( listVins.loc[:,listVins.columns!='latlong'] ,geometry= gpd.points_from_xy(x=lons,y=lats), crs={'init': 'epsg:4326'})
        #listVins = gpd.GeoDataFrame( listVins.loc[:,:] ,geometry= gpd.points_from_xy(x=lons,y=lats), crs={'init': 'epsg:4326'})
        listVins = listVins.to_crs(epsg=3395)
        listVins['DomaineChateau'] = [ str(xx) for xx in  listVins['DomaineChateau'] ]


        listVins['Pays_order'] = listVins['Pays'].str.replace('France','AAA')

        #load local legend info
        legendParam = pd.read_csv(dir_in+'domaineChateau_legend_location.csv')
        legendParam['DomaineChateau'] = [ str(xx) for xx in  legendParam['DomaineChateau'] ]
        
        listVins = pd.merge(listVins, legendParam, how='left', on='DomaineChateau')
        listVins.loc[listVins['legend_nbreColumn'].isnull(),'legend_nbreColumn'] = np.int64(1)
        listVins.loc[listVins['legend_loc'].isnull(),'legend_loc'] = 'upper right'
        print('{:d} vins ont ete charge'.format(listVins.shape[0]))
        listVins.to_file(wkdir+"listVins.gpkg", driver="GPKG")


    else:
        listVins = gpd.read_file(wkdir+"listVins.gpkg", driver="GPKG")


    #################### 
    # neighbourg borders
    ####################
    #data from https://wambachers-osm.website/boundaries/
    coasts_borders = gpd.read_file(dir_in+'Borders/neighbourgCountries.shp')
    coasts_borders = coasts_borders.to_crs(epsg=3395)


    #################### 
    # river and lake
    #################### 
    clc12 = gpd.read_file(dir_in+'CLC12/CLC12_FR_RGF_SHP/CLC12_FR_RGF.shp')
    inlandWater = clc12.loc[\
                           #(clc12['CODE_12']=='511')|(clc12['CODE_12']=='522')\
                           #|(clc12['CODE_12']=='411')\
                           (clc12['CODE_12']=='521')]
    inlandWater_river =  gpd.read_file(dir_in+'Wise_WaterData/EuropeanRiver.shp') # for large plot
    
    inlandWater_lake = clc12.loc[(clc12['CODE_12']=='512')]
    inlandWater_lake = inlandWater_lake.loc[inlandWater_lake.geometry.area>.5e6]

    seaWater    = clc12.loc[(clc12['CODE_12']=='423')|(clc12['CODE_12']=='523')\
                           |(clc12['CODE_12']=='421')|(clc12['CODE_12']=='331')]
    
    inlandWater = inlandWater.to_crs(epsg=3395)
    seaWater = seaWater.to_crs(epsg=3395)
    inlandWater_river = inlandWater_river.to_crs(epsg=3395) 
    
    rivers_hydroFrance = gpd.read_file(dir_in+'ROUTE120_1-1_SHP_LAMB93_000_2012-11-26/ROUTE120/1_DONNEES_LIVRAISON_2012-11-00377/R120_1-1_SHP_LAMB93_FR-ED121/HYDROGRAPHIE/TRONCON_HYDROGRAPHIQUE.SHP')
    rivers_hydroFrance = rivers_hydroFrance.to_crs(epsg=3395)
    
    country_pakage = {}
    paysCode = {}; 
    paysCode['Hongrie'] = 'HUN'
    paysCode['France']  = 'FRA'
        
    pays = 'France'
    country_pakage[pays] = {}
    country_pakage[pays]['inlandWater']       = inlandWater
    country_pakage[pays]['inlandWater_river'] = rivers_hydroFrance
    country_pakage[pays]['inlandWater_lake']  = inlandWater_lake
    country_pakage[pays]['seaWater']          = seaWater
    country_pakage[pays]['coasts_borders']    = coasts_borders
    country_pakage[pays]['metropole']         = metropole
    


    ######################
    # border contour international
    ######################
    for pays in listVins['Pays']:
        if pays == 'France': continue
        country_pakage[pays] = {}
   

        if pays in [u'Nouvelle Z\xe9lande ', u'Italie']:
            empty_ = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:4326")
            country_pakage[pays]['inlandWater']       = empty_
            country_pakage[pays]['inlandWater_river'] = empty_ 
            country_pakage[pays]['inlandWater_lake']  = empty_ 
            country_pakage[pays]['seaWater']          = empty_ 
            country_pakage[pays]['coasts_borders']    = empty_ 
            country_pakage[pays]['metropole']         = empty_ 
            continue

        clc12_ = gpd.read_file(dir_in+'CLC12/CLC12_{:s}/CLC12_{:s}.shp'.format(paysCode[pays],paysCode[pays]))
    
        inlandWater_ = clc12_.loc[(clc12_['Code_12']=='521')]
        
        inlandWater_river_ =  gpd.read_file(dir_in+'river/{:s}/{:s}_water_lines_dcw.shp'.format(paysCode[pays],paysCode[pays]))
    
        inlandWater_lake_ = gpd.read_file(dir_in+'river/{:s}/{:s}_water_areas_dcw.shp'.format(paysCode[pays],paysCode[pays]))
        #inlandWater_lake_ = clc12_.loc[(clc12_['Code_12']=='512')]
        #inlandWater_lake_ = inlandWater_lake_.loc[inlandWater_lake_.geometry.area>.5e6]

        seaWater_         = clc12_.loc[(clc12_['Code_12']=='423')|(clc12_['Code_12']=='523')\
                                        |(clc12_['Code_12']=='421')|(clc12_['Code_12']=='331')]
        
        inlandWater_ = inlandWater_.to_crs(epsg=3395)
        seaWater_= seaWater_.to_crs(epsg=3395)
        inlandWater_river_ = inlandWater_river_.to_crs(epsg=3395) 
        inlandWater_lake_  = inlandWater_lake_.to_crs(epsg=3395)

        coasts_borders_ = gpd.read_file(dir_in+'Borders/International/{:s}/neighbourgCountries.geojson'.format(pays))
        coasts_borders_ = coasts_borders_.to_crs(epsg=3395)
        
        metropole_ = gpd.read_file(dir_in+'Borders/International/{:s}/metropole.geojson'.format(pays))
        metropole_ = metropole_.to_crs(epsg=3395)

        country_pakage[pays]['inlandWater']       = inlandWater_
        country_pakage[pays]['inlandWater_river'] = inlandWater_river_
        country_pakage[pays]['inlandWater_lake']  = inlandWater_lake_
        country_pakage[pays]['seaWater']          = seaWater_
        country_pakage[pays]['coasts_borders']    = coasts_borders_
        country_pakage[pays]['metropole']         = metropole_



    ######################
    #load insee / postal code
    ######################
    #insee_cp_commune = pd.read_csv(dir_in+'laposte_hexasmal.csv')   
    #insee_cp_commune = insee_cp_commune.rename(columns={'Code_postal':'CI'})


    ######################
    #load insee / postal code
    ######################
    prefectures = pd.read_csv(dir_in+'hotels-de-prefectures-fr.csv')
    prefectures = gpd.GeoDataFrame( prefectures.loc[:,(prefectures.columns!='LonDD')&(prefectures.columns!='LatDD')] ,
                                   geometry= gpd.points_from_xy(x=prefectures['LonDD'],y=prefectures['LatDD']), crs={'init': 'epsg:4326'})
    prefectures = prefectures.to_crs(epsg=3395)
    prefectures['add_to_name_position'] = shapely.geometry.Point(0,0)

    ######################
    # Merge geo commune info and appellation
    ######################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"map_df_communes_appellation_bassin.shp")))):
    
        #load appelation par communes
        allAppellation_per_communes = pd.read_csv(dir_in+'2020-02-26-comagri-communes-aires-ao_ronan.csv')
        allAppellation_per_communes.rename(columns=lambda x: x.replace('Aire geographique','Appellation'), inplace=True)
        allAppellation_per_communes.Appellation = allAppellation_per_communes.Appellation.str.lower().str.replace(' ','-')
        allAppellation_per_communes = allAppellation_per_communes.rename(columns={'CI':'insee'})

        print('merge commune and appellations ...')
        #join df
        appellation_bassin_per_communes = allAppellation_per_communes.set_index('Appellation').join(listAppellations.set_index('Appellation'))
        #deal with Alsace
        appellation_bassin_per_communes.loc[['alsace' in s for s in appellation_bassin_per_communes.index],'Bassin'] = 'Alsace'
        #fiefs vendees
        appellation_bassin_per_communes.loc[['fiefs-vend\xc3\xa9ens' in s for s in appellation_bassin_per_communes.index],'Bassin'] = 'Vall\xc3\xa9e de la Loire'
        #gaillac
        appellation_bassin_per_communes.loc[['gaillac' in s for s in appellation_bassin_per_communes.index],'Bassin'] = 'Sud-Ouest'
        #saumur
        appellation_bassin_per_communes.loc[['saumur' in s for s in appellation_bassin_per_communes.index],'Bassin'] = 'Vall\xc3\xa9e de la Loire'
        #vosne-romanee
        appellation_bassin_per_communes.loc[['vosne-roman\xc3\xa9e' in s for s in appellation_bassin_per_communes.index],'Bassin'] = 'Bourgogne'
        #vougeot
        appellation_bassin_per_communes.loc[['vougeot' in s for s in appellation_bassin_per_communes.index],'Bassin'] = 'Bourgogne'

        appellation_bassin_per_communes = appellation_bassin_per_communes.loc[appellation_bassin_per_communes['Bassin'].notna()] 
        appellation_bassin_per_communes = appellation_bassin_per_communes.reset_index()
       
        #convert CI to insee format
        idx_notCorsica = appellation_bassin_per_communes.loc[pd.to_numeric(appellation_bassin_per_communes['insee'], errors='coerce').notna()].index
        tmp_ = pd.to_numeric(appellation_bassin_per_communes.loc[idx_notCorsica,'insee'], errors='coerce').map('{:05g}'.format)
        appellation_bassin_per_communes.loc[idx_notCorsica,'insee'] = tmp_
        
        map_df = map_dfCommune.merge(appellation_bassin_per_communes, on='insee') 
        map_df.Bassin = [ str(xx) for xx in map_df.Bassin]
        map_df.to_file(wkdir+"map_df_communes_appellation_bassin.shp")
    else: 
        map_df = gpd.read_file(wkdir+"map_df_communes_appellation_bassin.shp")


    ######################
    # bassins shapefile
    ######################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"bassins.shp")))):
        print('bassins ...')
        bassins =  map_df[['Bassin','geometry']].dissolve(by='Bassin').reset_index()
        bassins = bassins.merge(listBassinColor,on='Bassin')
        #sort by area to help plotting
        bassins['area']=bassins.geometry.area
        bassins = bassins.sort_values(by='area', ascending=False)
        bassins = bassins.to_crs(epsg=3395)
        bassins = bassins.rename(columns={'Bassin':'nom'})
        bassins.to_file(wkdir+"bassins.shp")
    else:
        bassins = gpd.read_file(wkdir+"bassins.shp")
        bassins = bassins.sort_values(by='area', ascending=False)
    country_pakage['France']['bassins'] = bassins

    
    ######################
    # appellations shapefile
    ######################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"appellations.shp")))):
        print('appellations ...')
        appellations =  map_df[['Appellation','geometry','Bassin']].dissolve(by='Appellation').reset_index()
        appellations = appellations.rename(columns={'Bassin':'bassin'})
        #sort by area to help plotting
        appellations['area']=appellations.geometry.area
        appellations = appellations.sort_values(by='area', ascending=False)
        appellations = appellations.rename(columns={'Appellation':'nom'})
        appellations = appellations.to_crs(epsg=3395)
        appellations.to_file(wkdir+"appellations.shp")
    else:
        appellations = gpd.read_file(wkdir+"appellations.shp")
        appellations = appellations.sort_values(by='area', ascending=False)


    ########################################
    #Add IGP stored locally in appellations:
    ########################################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"appellations_igp.shp")))):
        dir_igp = dir_in+'IGP/'
        appellations_igp = []
        for csvFile in glob.glob(dir_igp+'*.csv'):
            igp_ = pd.read_csv(csvFile)
            igp_.rename(columns=lambda x: x.replace('Aire geographique','Appellation'), inplace=True)
            igp_.Appellation = igp_.Appellation.str.lower().str.replace(' ','-')
            igp_ = igp_.rename(columns={'CI':'insee'})
            igp_.insee = [str(xx) for xx in igp_.insee]
            igp_.Bassin = [ str(xx) for xx in igp_.Bassin]

            map_df_ = map_dfCommune.merge(igp_, on='insee') 
            map_df_.Bassin = [ str(xx) for xx in map_df_.Bassin]
            
            igp_gpd = map_df_[['Appellation','geometry','Bassin']].dissolve(by='Appellation').reset_index()
            igp_gpd['area']=igp_gpd.geometry.area
            
            igp_gpd = igp_gpd.to_crs(epsg=3395)
            igp_gpd = igp_gpd.rename(columns={'Appellation':'nom'})
            igp_gpd = igp_gpd.rename(columns={'Bassin':'bassin'})
            
            appellations_igp.append(igp_gpd)

        appellations_igp = pd.concat(appellations_igp, ignore_index=True)
        appellations_igp.to_file(wkdir+"appellations_igp.shp")
    
    else:
        appellations_igp = gpd.read_file(wkdir+"appellations_igp.shp")
        appellations_igp = appellations_igp.sort_values(by='area', ascending=False)
    
    
    ########################################
    #replace geographic zone for alsace grand cru to production zone stored locally in CarteVin/GrandCruAslace:
    ########################################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"appellations_AlsaceGrandCru.shp")))):
        dir_agc = dir_in+'GrandCruAlsace/'
        appellations_agc = []
        for csvFile in glob.glob(dir_agc+'*.csv'):
            try: 
                agc_ = pd.read_csv(csvFile, sep=';', encoding = "ISO-8859-1")
            except: 
                pdb.set_trace()
            agc_.rename(columns=lambda x: x.replace('Aire g\xe9ographique','Appellation'), inplace=True)
            agc_.Appellation = agc_.Appellation.str.lower().str.replace(' ','-')
            agc_ = agc_.rename(columns={'CI':'insee'})
            agc_.insee = [str(xx) for xx in agc_.insee]
            agc_['Bassin'] = ['Alsace']*len(agc_)
            
            agc_ = agc_.loc[agc_['Zone'] == 'Zone de production des raisins']

            map_df_ = map_dfCommune.merge(agc_, on='insee') 
            map_df_.Bassin = [ str(xx) for xx in map_df_.Bassin]
            
            agc_gpd = map_df_[['Appellation','geometry','Bassin']].dissolve(by='Appellation').reset_index()
            agc_gpd['area']=agc_gpd.geometry.area
            
            agc_gpd = agc_gpd.to_crs(epsg=3395)
            agc_gpd = agc_gpd.rename(columns={'Appellation':'nom'})
            agc_gpd = agc_gpd.rename(columns={'Bassin':'bassin'})
            
            appellations_agc.append(agc_gpd)

        appellations_agc = pd.concat(appellations_agc, ignore_index=True)
        appellations_agc.to_file(wkdir+"appellations_AlsaceGrandCru.shp")
        
    else:
        appellations_agc = gpd.read_file(wkdir+"appellations_AlsaceGrandCru.shp")
        appellations_agc = appellations_agc.sort_values(by='area', ascending=False)


    ########################################
    #Add particular zone stored locally in appellations: (ex: cidre fouesnantais)
    ########################################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"appellations_other.shp")))):
        dir_other = dir_in+'AutreAppellation/'
        appellations_other = []
        for csvFile in glob.glob(dir_other+'*.csv'):
            other_ = pd.read_csv(csvFile)
            other_.rename(columns=lambda x: x.replace('Aire geographique','Appellation'), inplace=True)
            other_.Appellation = other_.Appellation.str.lower().str.replace(' ','-')
            other_ = other_.rename(columns={'CI':'insee'})
            other_.insee = [str(xx) for xx in other_.insee]
            other_.Bassin = [ str(xx) for xx in other_.Bassin]

            map_df_ = map_dfCommune.merge(other_, on='insee') 
            map_df_.Bassin = [ str(xx) for xx in map_df_.Bassin]
            
            other_gpd = map_df_[['Appellation','geometry','Bassin']].dissolve(by='Appellation').reset_index()
            other_gpd['area']=other_gpd.geometry.area
            
            other_gpd = other_gpd.to_crs(epsg=3395)
            other_gpd = other_gpd.rename(columns={'Appellation':'nom'})
            other_gpd = other_gpd.rename(columns={'Bassin':'bassin'})
            
            appellations_other.append(other_gpd)

        appellations_other = pd.concat(appellations_other, ignore_index=True)
        appellations_other.to_file(wkdir+"appellations_other.shp")
    
    else:
        appellations_other = gpd.read_file(wkdir+"appellations_other.shp")
        appellations_other = appellations_other.sort_values(by='area', ascending=False)


    ######################
    # international appellations shapefile
    ######################
    if ((not(flag_restart)) or (not(os.path.isfile(wkdir+"appellations_international.shp")))):
        print('international appellations ...')
        shpFiles = glob.glob(dir_in + 'AppellationInternational/wineRegion*.shp')
        appellations_international = []
        bassins_international = {} 
        for shpFile in shpFiles:
            pays_ = shpFile.split('wineRegion')[1].split('.')[0]
            wineRegion = gpd.read_file(shpFile)
            
            if pays_ == 'Hongrie':
                wineRegion['Name'] = [xx.encode('latin-1').decode('utf-8') for xx in wineRegion['Name'] ]


            wineRegion = wineRegion.rename(columns={'Name':'nom'})
            wineRegion['nom'] = wineRegion['nom'].str.replace('wine region','').str.strip()
            wineRegion['bassin'] = wineRegion['nom']

            #sort by area to help plotting
            wineRegion['area']=wineRegion.geometry.area
            wineRegion = wineRegion.sort_values(by='area', ascending=False)
            wineRegion = wineRegion.to_crs(epsg=3395)
           
            wineRegion = wineRegion[['nom','bassin','geometry','area']]

            bassins_international[pays_] = wineRegion.copy()
            
            wineRegion['nom'] =  wineRegion['nom'].str.lower().str.replace(' ','-')
            wineRegion['bassin'] =  wineRegion['bassin'].str.lower().str.replace(' ','-')
            appellations_international.append(wineRegion)

        appellations_international = pd.concat(appellations_international, ignore_index=True)
        appellations_international.to_file(wkdir+"appellations_international.shp")
    
        pickle.dump(bassins_international,open(wkdir+'bassins_international.pickle','wb')) 

    else:
        appellations_international = gpd.read_file(wkdir+"appellations_international.shp")
        appellations_international = appellations_international.sort_values(by='area', ascending=False)

        bassins_international = pickle.load(open(wkdir+'bassins_international.pickle', 'rb'))


    #collect international bassins from appellation
    for key in list(country_pakage.keys()):
        if key == 'France': 
            continue
        elif key in [u'Nouvelle Z\xe9lande ', u'Italie']:
            empty_ = gpd.GeoDataFrame(columns = [u'nom', u'geometry', u'color', u'area', u'add_to_name_position'], crs="EPSG:4326") 
            country_pakage[key]['bassins']       = empty_
        else:
            bassins_ = bassins_international[key].copy()
            listBassinColor_ = pd.read_csv(dir_in+'AppellationInternational/bassins-colors-{:s}.csv'.format(key)) 
            listBassinColor_['bassin'] = [str(xx) for xx in listBassinColor_['bassin']]
        
            country_pakage[key]['bassins'] = bassins_.merge(listBassinColor_,on='bassin')


    dir_maps = dir_out + 'VinMaps/' 
    ensure_dir(dir_maps)

    ######################
    # Large Plot
    ######################
    bassins['add_to_name_position'] = shapely.geometry.Point(0,0)
    bassins.at[bassins[bassins['nom']=='Savoie-Bugey'].index[0],'add_to_name_position'] = shapely.geometry.Point(40.e3,-40.e3) #Savoie
    bassins.at[bassins[bassins['nom']=='Languedoc-Roussillon'].index[0],'add_to_name_position'] = shapely.geometry.Point(-90.e3,-30.e3) #Lamguedoc
    bassins.at[bassins[bassins['nom']==u'Vall\xe9e du Rh\xf4ne'].index[0],'add_to_name_position'] = shapely.geometry.Point(0.,30.e3) #Vallee Rhone
    bassins.at[bassins[bassins['nom']=='Jura'].index[0],'add_to_name_position'] = shapely.geometry.Point(40.e3,0.) #Jura
    bassins.at[bassins[bassins['nom']=='Lyonnais'].index[0],'add_to_name_position'] = shapely.geometry.Point(-60.e3,-20.e3) #Lyonnais
    bassins.at[bassins[bassins['nom']=='Alsace'].index[0],'add_to_name_position'] = shapely.geometry.Point(-50.e3,0.) #Alsace
    
    bassins.at[bassins[bassins['nom']=='Cidre de Bretagne'].index[0],'add_to_name_position'] = shapely.geometry.Point(-20.e3,-5.e3) 
    bassins.at[bassins[bassins['nom']=='Cidre de Bretagne'].index[0],'nom'] = 'Cidre de\nBretagne'
    
    bassins.at[bassins[bassins['nom']=='Cidre de Normandie'].index[0],'add_to_name_position'] = shapely.geometry.Point(100.e3,-100.e3) 
    bassins.at[bassins[bassins['nom']=='Cidre de Normandie'].index[0],'nom'] = 'Cidre de\nNormandie'
    
    if ((not(flag_restart)) or (not(os.path.isfile(dir_maps+"bassinViticoleFrance.png")))):
        print('plot large map')
        xmin, ymin, xmax, ymax =  metropole.geometry.total_bounds
        xx = xmax-xmin;  yy = ymax-ymin
        xc = xmin+.5*xx; yc = ymin+.5*yy
        dd = max([xx,yy]) + 50.e3
        xmin = xc-.5*dd;  xmax = xc+.5*dd
        ymin = yc-.5*dd;  ymax = yc+.5*dd
         
        ratio= old_div((ymax-ymin),(xmax-xmin))
        x_image = 8
        mpl.rcdefaults()
        mpl.rcParams['mathtext.fontset'] = 'stix'
        mpl.rcParams['font.family'] = 'STIXGeneral'
        mpl.rcParams['font.size'] = 13
        mpl.rcParams['legend.fontsize'] = 9
        mpl.rcParams['figure.subplot.hspace'] = 0.0
        mpl.rcParams['figure.subplot.wspace'] = 0.0
        fig = plt.figure(figsize=(x_image,x_image*ratio),facecolor='.8')
        ax = fig.add_axes([0.002,0.002, 0.996,.996])
        #ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])

        seaWater.plot(ax=ax, antialiased=True,zorder=0,facecolor='.8')
        ax.patch.set_facecolor('.8')
        metropole.plot(ax=ax, facecolor='white', edgecolor='none',linewidth=.0,zorder=0)
        
        bassins.plot( ax=ax, cmap=plt.cm.colors.ListedColormap(bassins['color']),zorder=1,alpha=.5)
        #bassins.apply(lambda x: ax.annotate(s=str(x.nom),\
        bassins.apply(lambda x: ax.annotate(str(x.nom),\
                                            xy=[x.geometry.centroid.x + x.add_to_name_position.coords.xy[0][0],\
                                                x.geometry.centroid.y + x.add_to_name_position.coords.xy[1][0] ], ha='center',zorder=5),axis=1);
        
        inlandWater.plot(ax=ax, antialiased=True,zorder=3,facecolor='.8',edgecolor='.8',linewidth=.15)
        inlandWater_river.plot(ax=ax, antialiased=True,zorder=3,facecolor='none',edgecolor='.45',linewidth=.15)
        #inlandWater_lake.plot(ax=ax, antialiased=True,zorder=2,facecolor='.8',edgecolor='.8',linewidth=.15)
        
        metropole.plot(ax=ax, facecolor='none', edgecolor='k',linewidth=.4,zorder=4);
        coasts_borders.plot(ax=ax, facecolor='white', edgecolor='k', antialiased=True,linewidth=.4,zorder=2)
     

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        #plt.show()
        fig.savefig(dir_maps+'bassinViticoleFrance.png', dpi=dpi_largePlot,)# acecolor=fig.get_facecolor())
        plt.close(fig)
    
    bassins.at[bassins[bassins['nom']=='Cidre de\nBretagne'].index[0],'nom'] = 'Cidre de Bretagne'
    bassins.at[bassins[bassins['nom']=='Cidre de\nNormandie'].index[0],'nom'] = 'Cidre de Normandie'
    
    ######################
    # single Plot
    ######################
    
    #load template
    f = open(dir_out+'InputTex/vin_template.tex','r')
    lines_ori = f.readlines()
    f.close()

    lineXX = np.where(np.array(lines_ori)=='XX\n')[0][0]
    final1_lines = lines_ori[:lineXX]
    final2_lines = []
    final3_lines = lines_ori[lineXX+1:]

    listVins = listVins.sort_values(by=['Pays_order', 'Bassin','DomaineChateau','Couleur','Appelation','Cuvee']).reset_index()
    section_bassin = 'mm'
    section_domain = 'mm'
    section_couleur = 'mm'
    vinDictionary = {}
    try: 
        vinDictionary2 = pickle.load(open(dir_out+'vinDictionary_fromWebSiteParsing.pickle', 'rb'))
    except: 
        vinDictionary2 = {}
    list_vin_noRecipies = []

    for index, vin in listVins.iterrows():
        
        flag_igp = 0
        flag_other = 0
        flag_international = 0
        #select appellation from vin 
        appellations_containing_vin = gpd.tools.sjoin(appellations,listVins.loc[[index]],how='inner')

        #select appellations that contains this appellation
        
        #select appellations at the same level
        
        #select river from ROUTE120_1-1_SHP_LAMB93_000_2012-11-26/
        #https://stackoverflow.com/questions/16992038/inline-labels-in-matplotlib
        
        #select topo?
       

        #plot
        
        #add in vin.tex
        #--------------
        
        newBassin = 0
        if (section_bassin != vin.Bassin) & (section_bassin!='International'):
            #add subsection
            final2_lines.append('\n')
            final2_lines.append('\\newpage')
            newBassin = 1 
            if vin.Pays == 'France':
                section_bassin = vin.Bassin
            else:
                section_bassin = 'International'
            print(section_bassin)
            final2_lines.append( u'\\fakesubsection{{{:s}}}\n'.format(section_bassin))

        newDomain = 0
        if section_domain != vin.DomaineChateau:
            print('  ', vin.DomaineChateau)
            tmp_ = '\\newpage' if (newBassin == 0) else ''
            final2_lines.append('\n')
            final2_lines.append('%##########\n')
            if vin.Pays == 'France':
                final2_lines.append(u'\\vinSection[{:s}]{{{:s}}}\n'.format(tmp_,vin.DomaineChateau.replace('&','\&')))
            else:
                final2_lines.append(u'\\vinSection[{:s}]{{{:s} - {:s}}}\n'.format(tmp_,vin.Pays,vin.DomaineChateau.replace('&','\&')))

            final2_lines.append('\\label{{sec:{:s}}}\n'.format(\
                                   vin.DomaineChateau.replace('&','').replace(' ','').lower() ))
            final2_lines.append('%##########\n')
            address1 = vin['Adresse'].split(' ')
            address2 = []
            for address_ in address1:
                tmp_ = address_.rstrip(',').rstrip(' ')
                if tmp_ != '':
                    address2.append(tmp_)
            if ''.join(address2[:-1]) == '':
                address3 = '{:s} {:05.0f}'.format(  address2[-1], vin['Code postal'] )
            else:
                address3 = '{:s} \\newline {:s} {:05.0f}'.format( ' '.join(address2[:-1]),  address2[-1], vin['Code postal'])
            
            if section_bassin == 'International':
                address3 += '\\newline {:s}'.format(vin.Pays)

            #plot
            if (section_domain != 'mm'):
                if ((not(flag_restart)) or (not(os.path.isfile(map_domain)))): 
                    try:
                        saveplot(appellations_domain, vin_prev, metropole_prev, bassins_prev) 
                    except: 
                        print('pass -- no save plot')
                        pass
            section_domain = vin.DomaineChateau
            map_domain = dir_maps+'{:s}.png'.format(''.join(section_domain.split(' '))).replace("'",'')
            map_domain = unicodedata.normalize('NFD', str(map_domain)).encode('ascii', 'ignore')
            
            #print map_domain

            final2_lines.append(u'\\vinShowInfoDomain{{{:s}}}{{{:s}}}{{{:s}}}\n'.format(vin['Nom Producteur'].replace('&','\&'), address3, map_domain.decode("utf-8")))
            newDomain = 1
            section_couleur = 'mm' 
            
            if (((not(flag_restart)) or (not(os.path.isfile(map_domain))))):
                
                ratio= 1. 
                x_image = 8
                mpl.rcdefaults()
                mpl.rcParams['mathtext.fontset'] = 'stix'
                mpl.rcParams['font.family'] = 'STIXGeneral'
                mpl.rcParams['font.size'] = 20
                mpl.rcParams['legend.fontsize'] = 18
                mpl.rcParams['figure.subplot.left'] = .0
                mpl.rcParams['figure.subplot.right'] = 1.
                mpl.rcParams['figure.subplot.top'] = 1.
                mpl.rcParams['figure.subplot.bottom'] = .0
                mpl.rcParams['figure.subplot.hspace'] = 0.02
                mpl.rcParams['figure.subplot.wspace'] = 0.02
                fig = plt.figure(figsize=(x_image,x_image*ratio))#,facecolor='.8')
                #plt.subplots_adjust(left=0.0,right=.66,top=1,bottom=0.0,wspace=0.15,hspace=0.05)
                
                ax = fig.add_axes([0.01,0.01, 0.98,.98])
                ax.set_xticks([])
                ax.set_yticks([])
                #--
                if vin.DomaineChateau == u'Ch\xe2teau La Borie':
                    bx = fig.add_axes([0.02,0.02, 0.26,0.26])
                elif vin.DomaineChateau == u'Les Vignobles de Seyssuel':
                    bx = fig.add_axes([0.02,0.02, 0.26,0.26])
                elif vin.DomaineChateau == u'Ch\xe2teau Haut-Marbuzet':
                    bx = fig.add_axes([0.02,0.02, 0.26,0.26])
                elif vin.DomaineChateau == u'Cidre S\xe9h\xe9dic':
                    bx = fig.add_axes([0.02,0.02, 0.26,0.26])
                elif vin.DomaineChateau == u'Domaine Philippe Girard':
                    bx = fig.add_axes([0.02,0.72, 0.26,0.26])
                else:
                    bx = fig.add_axes([0.72,0.02, 0.26,0.26])
                
                bx.set_xticks([])
                bx.set_yticks([])

                try:
                    country_pakage[vin['Pays']]['seaWater'].plot(ax=ax, antialiased=True,zorder=0,facecolor='.8')
                    ax.patch.set_facecolor('.8')
                    country_pakage[vin['Pays']]['metropole'].plot(ax=ax, facecolor='white', edgecolor='None',linewidth=.1,zorder=0)
                    #--
                    country_pakage[vin['Pays']]['seaWater'].plot(ax=bx, antialiased=True,zorder=0,facecolor='.8')
                    bx.patch.set_facecolor('.8')
                    country_pakage[vin['Pays']]['metropole'].plot(ax=bx, facecolor='white', edgecolor='None',linewidth=.1,zorder=0)
                    
                    bassins_ = country_pakage[vin['Pays']]['bassins']
                    bassins_.loc[bassins_.nom == vin.Bassin].plot( ax=ax, color= bassins_.loc[bassins_.nom==vin.Bassin,'color'],zorder=1, alpha=.5)
                    bassins_.loc[bassins_.nom != vin.Bassin].plot( ax=ax, color= bassins_.loc[bassins_.nom!=vin.Bassin,'color'],zorder=1, alpha=.5)
                    #--
                    bassins_.plot( ax=bx, color= bassins_.color, zorder=1, alpha=.5)
                    
                    country_pakage[vin['Pays']]['inlandWater'].plot(ax=ax, antialiased=True,zorder=3,facecolor='.8',edgecolor='.8',linewidth=.15)
                    country_pakage[vin['Pays']]['inlandWater_river'].plot(ax=ax, antialiased=True,zorder=2,facecolor='none',edgecolor='.1',linewidth=.15)
                    country_pakage[vin['Pays']]['inlandWater_lake'].plot(ax=ax, antialiased=True,zorder=3,facecolor='.85',edgecolor='.1',linewidth=.15)
                    #--
                    #country_pakage[vin['Pays']]['inlandWater'].plot(ax=bx, antialiased=True,zorder=3,facecolor='.8',edgecolor='.8',linewidth=.15)
                    #country_pakage[vin['Pays']]['inlandWater_river'].plot(ax=bx, antialiased=True,zorder=3,facecolor='none',edgecolor='.1',linewidth=.15)
                    
                    country_pakage[vin['Pays']]['metropole'].plot(ax=ax, facecolor='none', edgecolor='k',linewidth=.8,zorder=4);
                    #--
                    #metropole.plot(ax=bx, facecolor='none', edgecolor='k',linewidth=.1,zorder=4);
                    #coasts_borders.plot(ax=ax, facecolor='white', edgecolor='k', antialiased=True,linewidth=.8,zorder=2)
                 
                    listVins.loc[[index],'geometry'].plot(ax=ax, zorder=6, color='k', markersize=30, marker='s')
                    
                    country_pakage[vin['Pays']]['coasts_borders'].plot(ax=ax,facecolor='.9', edgecolor='.4', linewidth= 1, zorder=1)
                    #--
                    country_pakage[vin['Pays']]['coasts_borders'].plot(ax=bx,facecolor='.9', edgecolor='.4', linewidth=.5, zorder=1)
                except: 
                    pass

                appellations_domain = []
                appellations_domainName = []
                LegendElement_domain = [Line2D([0], [0], marker='s', color='None', label=section_domain, markerfacecolor='k', markersize=10)]

                #ax.set_xlim(vin.geometry.coords.xy[0][0]-buffer_lim,vin.geometry.coords.xy[0][0]+buffer_lim)
                #ax.set_ylim(vin.geometry.coords.xy[1][0]-buffer_lim,vin.geometry.coords.xy[1][0]+buffer_lim)
           
        
        newCouleur = 0
        if section_couleur != vin.Couleur:
            print('    ', vin.Couleur)
            final2_lines.append('\n')
            
            #if Daumas Rouge add page break
            if (vin.DomaineChateau.replace(' ','').lower() == 'masdedaumas-gassac') & (vin.Couleur == 'Rouge') :  final2_lines.append(u'\n\\newpage')
            #if Cezin Rouge add page break
            if (vin.DomaineChateau.replace(' ','').lower() == 'domainedecézin') & (vin.Couleur == 'Rouge') :  final2_lines.append(u'\n\\newpage')
            #if mordoree Rose add page break
            if (vin.DomaineChateau.replace(' ','').lower() == 'domainedelamordorée') & (vin.Couleur == 'Rosé') :  final2_lines.append(u'\n\\newpage')
            
            final2_lines.append(u'\n\\vinShowCouleur{{{:s}}}\n'.format(vin.Couleur))
            final2_lines.append(u'%--------------\n')
            section_couleur = vin.Couleur
            newCouleur = 1
            
        
        #add appellation to plot
        print('      ', vin.Appelation)
        appellation_ = appellations.loc[appellations.nom == '-'.join(vin.Appelation.lower().split(' ')) ]
        vin_prev       = vin # to get right name in the saveplot fct
        metropole_prev = country_pakage[vin['Pays']]['metropole']
        bassins_prev    = country_pakage[vin['Pays']]['bassins'] 
        flag_need_more = False
        if (len(appellation_) == 0):
            flag_need_more = True
        else: 
            if ('alsace-grand-cru' in  appellation_.nom.item()):
                flag_need_more = True

        if flag_need_more:
            tmp_= '-'.join(vin.Appelation.lower().split(' ')) 
            if 'maury' in tmp_  : appellation_ = appellations.loc[appellations.nom == 'maury']                     # tous les maury sont sur la meme zone
            if 'gaillac' in tmp_: appellation_ = appellations.loc[appellations.nom == u'gaillac-rouge-et-ros\xe9'] # tout les gaillac sont sur la meme zone
            
            if 'cotentin' in tmp_: appellation_ = appellations.loc[appellations.nom == u'cidre-cotentin-ou-cotentin'] # tout les gaillac sont sur la meme zone
          
            #alsace
            appellation_agc_ = appellations_agc.loc[appellations_agc.nom == '-'.join(vin.Appelation.lower().split(' ')) ]
            if len(appellation_agc_) != 0:
                appellation_ = appellation_agc_
            else:
                if tmp_ ==  'alsace' :                appellation_ = appellations.loc[appellations.nom.str.contains('alsace-suivi-ou-non')]
                if tmp_ ==  'alsace-pinot-noir':      appellation_ = appellations.loc[appellations.nom.str.contains('alsace-suivi-ou-non')]
                if tmp_ ==  'alsace-gewurztraminer' : appellation_ = appellations.loc[appellations.nom.str.contains('alsace-suivi-ou-non')]
                if tmp_ ==  'alsace-riesling' :       appellation_ = appellations.loc[appellations.nom.str.contains('alsace-suivi-ou-non')]

            #igp
            appellation_igp_ = appellations_igp.loc[appellations_igp.nom == '-'.join(vin.Appelation.lower().split(' ')) ]
            if len(appellation_igp_) != 0:
                appellation_ = appellation_igp_
                flag_igp = 1
            
            #other
            appellation_other_ = appellations_other.loc[appellations_other.nom == '-'.join(vin.Appelation.lower().split(' ')) ]
            if len(appellation_other_) != 0:
                appellation_ = appellation_other_
                flag_other = 1
            
            # international
            appellation_international_ = appellations_international.loc[appellations_international.nom == '-'.join(vin.Bassin.lower().split(' ')) ]
            if len(appellation_international_) != 0:
                appellation_ = appellation_international_
                flag_international = 1

            if len(appellation_) == 0:
                print('      ****  missing appellation:', '-'.join(vin.Appelation.lower().split(' ')))
                #if (vin.Bassin == 'Alsace') : pdb.set_trace()
                #if (u'H\xe9rault' in vin.Appelation): continue  
                #if (u'Caume'      in vin.Appelation): continue 
                #if (u'Vin de France'      in vin.Appelation): continue 
                #if (u"Pineau d'Aunis"      in vin.Appelation): continue 
        
        key = vin.Couleur.replace(' ', '').lower()+vin.Appelation.replace(' ', '').lower()+\
              vin.DomaineChateau.replace(' ', '').lower()+vin.Cuvee.replace(' ', '').lower()

        listRecipies_here = ''
        if key in list(vinDictionary2.keys()):
            for recipe in vinDictionary2[key]:
                listRecipies_here += '{:s}, '.format(recipe)
        listRecipies_here = listRecipies_here[:-2]+'.'
        if listRecipies_here == '.':
            list_vin_noRecipies.append([vin.DomaineChateau, vin.Couleur, vin.Appelation, vin.Cuvee])
        if (flag_igp == 1): 
            vin_Appelation = vin.Appelation + ' (IGP)'
        elif (flag_other == 1): 
            vin_Appelation = vin.Appelation + u' (Appellation Locale)'
        else:
            vin_Appelation = vin.Appelation  

        end_cepage = '.'
        if vin.Cepages == '-': end_cepage = ''

        if False: #newCouleur == 1: 
            final2_lines.append(u'\\vinShowInfoAppellation{{{:s}}}{{{:s}}}{{{:s}}}{{{:s}}}{{{:s}}} \n'.format(vin_Appelation, vin.Cuvee, vin.Cepages.replace('%','\%'), listRecipies_here,vin.Couleur))
        else:
            final2_lines.append(u'\\vinShowInfoAppellation{{{:s}}}{{{:s}}}{{{:s}}}{{{:s}}} \n'.format(vin_Appelation, vin.Cuvee, vin.Cepages.replace('%','\%')+end_cepage, listRecipies_here))
        #final2_lines.append(u'\n \\vspace{.05cm} \n')
     
        #create_dictionary
        vinDictionary[key] = []

        #pdb.set_trace()
        if (((not(flag_restart)) or (not(os.path.isfile(map_domain))))):
            if len(appellation_) != 0:
                hash_patterns = ('..', '//', 'o', '\\\\', 'O', '*', '-')
                hash_colors   = ('.5', '.5', '.5', '.5', '.5', '.5', '.5')
                facecolor = 'none'
                if u'domainedelamordor' in vin.DomaineChateau.replace('&','').replace(' ','').lower()  : 
                    hash_patterns = ('oo', '....', 'O', '//', '-')
                    hash_colors   = ('.5', '0.1', '0.5', '.5', '.5', '.5', '.5')
                    facecolor     = ''
                
                if simple_appelation(appellation_.reset_index().nom[0]) not in appellations_domainName:
                    
                    appellation_.plot(ax=ax, zorder=5, facecolor='none', edgecolor=hash_colors[len(appellations_domain)], hatch=hash_patterns[len(appellations_domain)])
                    
                    appellations_domainName.append(simple_appelation(appellation_.reset_index().nom[0]))
                   
                    if flag_international == 0:
                        LegendElement_domain.append( mpatches.Patch(facecolor='w', hatch=hash_patterns[len(appellations_domain)], \
                                                                    edgecolor=hash_colors[len(appellations_domain)], label=simple_appelation(vin.Appelation) ) )
                    else:
                        LegendElement_domain.append( mpatches.Patch(facecolor='w', hatch=hash_patterns[len(appellations_domain)], \
                                                                    edgecolor=hash_colors[len(appellations_domain)], label=simple_appelation(vin.Bassin) ) )

                    appellations_domain = appellation_ if len(appellations_domain)==0 else pd.concat([appellations_domain,appellation_])

        
        flag_checkVinIng = False
        if index == len(listVins)-1 : 
            flag_checkVinIng = True 
        else:
            if section_domain != listVins.DomaineChateau[index+1]:
                flag_checkVinIng = True 
        if flag_checkVinIng:
            domainChateau_ = unidecode.unidecode(vin.DomaineChateau.replace('&','').replace(' ','').lower())
            imgVinFiles = glob.glob( dir_out + 'VinImg/' + domainChateau_ + '.png')
            imgVinFiles.extend(glob.glob( dir_out + 'VinImg/' + domainChateau_ + '.jpg'))
            imgVinFiles.extend(glob.glob( dir_out + 'VinImg/' + domainChateau_ + '.jpeg'))
            imgVinFiles.extend(glob.glob( dir_out + 'VinImg/' + domainChateau_ + '-extra*.png'))
            imgVinFiles.extend(glob.glob( dir_out + 'VinImg/' + domainChateau_ + '-extra*.jpg'))
            imgVinFiles.extend(glob.glob( dir_out + 'VinImg/' + domainChateau_ + '-extra*.jpeg'))
            for imgVinFile in imgVinFiles:
                configImgFile = os.path.dirname(imgVinFile)+'/'+os.path.basename(imgVinFile).split('.')[0]+'.txt'
                if os.path.isfile(configImgFile):
                    with open(configImgFile,'r') as f:
                        lines_confImg = f.readlines()
                        widthImg = float(lines_confImg[0].split(':')[1])
                        vertivalSpaveImg = float(lines_confImg[1].split(':')[1])
                else:
                    widthImg = 0.6
                    vertivalSpaveImg = 2
                final2_lines.append(u'\\showExtraVinImg{{{:s}}}{{{:3.1f}}}{{{:3.1f}mm}}\n'.format(imgVinFile,widthImg,vertivalSpaveImg))

    #for the last plot
    if (((not(flag_restart)) or (not(os.path.isfile(map_domain)))) & (section_domain != 'mm')): 
        try: 
            saveplot(appellations_domain, vin_prev, metropole_prev, bassins_prev )
        except: 
            print('pass -- no saveplot')
            pass
   
    #scan vin to remove wine with no recipies in reference
    #remove no recipes
    final22_lines = []
    for line in final2_lines:
        if '{.}' not in line: final22_lines.append(line)

    if True:
        #remove empty colour
        final222_lines = []
        for iline, line in enumerate(final22_lines):
            if 'vinShowCouleur' in line: 
                flag_ok = False
                ii = iline+1
                while ii < len(final22_lines):
                    if 'vinShowInfoAppellation' in final22_lines[ii]:
                        flag_ok = True
                        final222_lines.append(line)
                        break
                    if 'vinShowCouleur' in final22_lines[ii]: 
                        break
                    ii += 1
                continue

            final222_lines.append(line)
    else:
        final222_lines = final22_lines

    if True:
        #remove empty wine
        final2222_lines = []
        ii_no = -999
        for iline, line in enumerate(final222_lines):
            
            if 'vinSection' in line: 
                ii = iline+1
                while ii < len(final222_lines):
                    if 'vinShowCouleur' in final222_lines[ii]:
                        final2222_lines.append(line)
                        ii_no = -999
                        break
                    if ('vinSection' in final222_lines[ii]) | ('newpage' in final222_lines[ii]): 
                        ii_no = ii -1
                        break
                    if ii == len(final222_lines)-1:  
                        ii_no = ii -1
                        break
                    ii += 1
                continue
            
            #print(ii_no)
            #if 'Cabelier' in line: pdb.set_trace()
            if iline <= ii_no: continue
            final2222_lines.append(line)
    else:
        final2222_lines = final222_lines
   
    #save file
    f= io.open(dir_out+"vin.tex","w")
    for line in final1_lines+final2222_lines+final3_lines:
        f.write( line )
    f.close()

    #save file with wine that did not get recipies
    f= io.open(dir_out+"LogError/listVin_noRecipies.csv","w",)
    f.write( '{:s}, {:s}, {:s}, {:s}, \n'.format('domaine', 'couleur', 'appellation', 'cuvee') )
    for [domain, couleur, app, cuvee] in list_vin_noRecipies :
        line = '{:s}, {:s}, {:s}, {:s}, \n'.format(domain, couleur, app, cuvee)
        f.write( line )
    f.close()

    pickle.dump(vinDictionary,open(dir_out+'vinDictionary_fromExcelFile.pickle','wb')) 
    
    sys.exit()







    #listVins.plot(ax=ax,facecolor='.1',zorder=4, markersize=5)

    #get location from address
    mm = geopy.geocoders.BANFrance()
    mm.geocode('34 Route de Rosenwiller, 67560 Rosheim')

    map_df[map_df['insee']<97000 | map_df['insee']]

    pd.to_numeric(map_df['insee'], errors='coerce')
    rdf = gpd.GeoDataFrame(pd.concat(dataframesListmap_df, ignore_index=True), crs=dataframesList[0].crs)

    disolve


    sys.exit()

# load in new csv file
    df = pd.read_csv("datasets/london-borough-profile.csv", header=0)

    df.head()
