#!/usr/bin/env python
# -- coding: utf-8 --

import pandas as pd
from wmf import wmf
import numpy as np 
import glob 
import pylab as pl
import json
import MySQLdb
import csv
import matplotlib
import matplotlib.font_manager
from datetime import timedelta
import datetime as dt
import pickle
import matplotlib.dates as mdates
import netCDF4
import textwrap


import matplotlib 
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager

font_dirs = ['/home/socastillogi/jupyter/fuentes/AvenirLTStd-Book']
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)

matplotlib.rcParams['font.family'] = 'Avenir LT Std'
matplotlib.rcParams['font.size']=12.5
import pylab as pl 
#COLOR EDGES
pl.rc('axes',labelcolor='#4f4f4f')
pl.rc('axes',linewidth=1.5)
pl.rc('axes',edgecolor='#bdb9b6')
pl.rc('text',color= '#4f4f4f')

import os
import datetime
import hydroeval
import hidrologia
#paquetes toxicos
# from cprv1 import cprv1

#---------------
#Funciones que se van pasando a py3.
#---------------

#---------------
#Funciones base.
#---------------

def get_rutesList(rutas):
    ''' Abre el archivo de texto en la ruta: rutas, devuelve una lista de las lineas de ese archivo.
        Funcion base.
        #Argumentos
        rutas: string, path indicado.
    '''
    f = open(rutas,'r')
    L = f.readlines()
    f.close()
    return L

def set_modelsettings(ConfigList):
    ruta_modelset = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_modelset')
    # model settings  Json
    with open(ruta_modelset, 'r') as f:
        model_set = json.load(f)
    # Model set
    wmf.models.max_aquifer = wmf.models.max_gravita * 10
    wmf.models.retorno = model_set['retorno']
    wmf.models.show_storage = model_set['show_storage']
    wmf.models.separate_fluxes = model_set['separate_fluxes']
    wmf.models.dt = model_set['dt']


def round_time(date = dt.datetime.now(),round_mins=5):
    '''
    Rounds datetime object to nearest 'round_time' minutes.
    If 'dif' is < 'round_time'/2 takes minute behind, else takesminute ahead.
    Parameters
    ----------
    date         : date to round
    round_mins   : round to this nearest minutes interval
    Returns
    ----------
    datetime object rounded, datetime object
    '''    
    dif = date.minute % round_mins

    if dif <= round_mins/2:
        return dt.datetime(date.year, date.month, date.day, date.hour, date.minute - (date.minute % round_mins))
    else:
        return dt.datetime(date.year, date.month, date.day, date.hour, date.minute - (date.minute % round_mins)) + dt.timedelta(minutes=round_mins)
    
    
def get_credentials(ruta_credenciales):
    credentials = json.load(open(ruta_credenciales))
    mysqlServer = credentials['MySql_Siata']
    for key in np.sort(list(credentials['MySql_Siata'].keys()))[::-1]: #1:hal, 2:sal
        try:
            connection = MySQLdb.connect(host=mysqlServer[key]['host'],
                                         user=mysqlServer[key]['user'],
                                         password=mysqlServer[key]['password'],
                                         db=mysqlServer[key]['db'])
            print('SERVER_CON: Succesful connection to %s'%(key))
            host=mysqlServer[key]['host']
            user=mysqlServer[key]['user']
            password=mysqlServer[key]['password']
            db=mysqlServer[key]['db']
            break #si conecta bien a SAL para.
        except:
            print('SERVER_CON: No connection to %s'%(key))
            pass
    return host,user,password,db
    
    
def coord2hillID(ruta_nc, df_coordxy):
    #lee simubasin pa asociar tramos, saca topologia basica
    cu = wmf.SimuBasin(rute= ruta_nc)
    cu.GetGeo_Cell_Basics()
    cu.GetGeo_Parameters()
    #saca coordenadas de todo el simubasin y las distancias entre ellas
    coordsX = wmf.cu.basin_coordxy(cu.structure,cu.ncells)[0]
    coordsY = wmf.cu.basin_coordxy(cu.structure,cu.ncells)[1]
    disty = np.unique(np.diff(np.unique(np.sort(coordsY))))
    distx = np.unique(np.diff(np.unique(np.sort(coordsX))))

    df_ids = pd.DataFrame(index = df_coordxy.index,columns=['id'])
    #identifica el id de la ladera donde caen los ptos
    for index in df_coordxy.index:
        df_ids.loc[index]=cu.hills_own[np.where((coordsY+disty[0]/2>df_coordxy.loc[index].values[1]) & (coordsY-disty[0]/2<df_coordxy.loc[index].values[1]) & (coordsX+distx[0]/2>df_coordxy.loc[index].values[0]) & (coordsX-distx[0]/2<df_coordxy.loc[index].values[0]))[0]].data
    return df_ids
    
#-----------------------------------
#-----------------------------------
#Funciones de lectura del configfile
#-----------------------------------
#-----------------------------------

def get_ruta(RutesList, key):
    ''' Busca en una lista 'RutesList' la linea que empieza con el key indicado, entrega rutas.
        Funcion base.
        #Argumentos
        RutesList: Lista que devuelve la funcion en este script get_rutesList()
        key: string, key indicado para buscar que linea en la lista empieza con el.
    '''
    if any(i.startswith('- **'+key+'**') for i in RutesList):
        for i in RutesList:
            if i.startswith('- **'+key+'**'):
                return i.split(' ')[-1][:-1]
    else:
        return 'Aviso: no existe linea con el key especificado'
    
def get_line(RutesList, key):
    ''' Busca en una lista 'RutesList' la linea que empieza con el key indicado, entrega lineas.
        Funcion base.
        #Argumentos
        RutesList: Lista que devuelve la funcion en este script get_rutesList()
        key: string, key indicado para buscar que linea en la lista empieza con el.
    '''
    if any(i.startswith('- **'+key+'**') for i in RutesList):
        for i in RutesList:
            if i.startswith('- **'+key+'**'):
                return i[:-1].split(' ')[2:]
    else:
        return 'Aviso: no existe linea con el key especificado'

def get_modelPlot(RutesList, PlotType = 'Qsim_map'):
    ''' #Devuelve un diccionario con la informacion de la tabla Plot en el configfile.
        #Funcion operacional.
        #Argumentos:
        - RutesList= lista, es el resultado de leer el configfile con al.get_ruteslist.
        - PlotType= boolean, tipo del plot? . Default= 'Qsim_map'.
    '''
    for l in RutesList:
        key = l.split('|')[1].rstrip().lstrip()
        if key[3:] == PlotType:
            EjecsList = [i.rstrip().lstrip() for i in l.split('|')[2].split(',')]
            return EjecsList
    return key

def get_modelPars(RutesList):
    ''' #Devuelve un diccionario con la informacion de la tabla Calib en el configfile.
        #Funcion operacional.
        #Argumentos:
        - RutesList= lista, es el resultado de leer el configfile con al.get_ruteslist.
    '''
    DCalib = {}
    for l in RutesList:
        c = [float(i) for i in l.split('|')[3:-1]]
        name = l.split('|')[2]
        DCalib.update({name.rstrip().lstrip(): c})
    return DCalib

def get_modelPaths(List):
    ''' #Devuelve un diccionario con la informacion de la tabla Calib en el configfile.
        #Funcion operacional.
        #Argumentos:
        - RutesList= lista, es el resultado de leer el configfile con al.get_ruteslist.
    '''
    DCalib = {}
    for l in List:
        c = [i for i in l.split('|')[3:-1]]
        name = l.split('|')[2]
        DCalib.update({name.rstrip().lstrip(): c[0]})
    return DCalib

def get_modelStore(RutesList):
    ''' #Devuelve un diccionario con la informacion de la tabla Store en el configfile.
        #Funcion operacional.
        #Argumentos:
        - RutesList= lista, es el resultado de leer el configfile con al.get_ruteslist.
    '''
    DStore = {}
    for l in RutesList:
        l = l.split('|')
        DStore.update({l[1].rstrip().lstrip():
            {'Nombre': l[2].rstrip().lstrip(),
            'Actualizar': l[3].rstrip().lstrip(),
            'Tiempo': float(l[4].rstrip().lstrip()),
            'Condition': l[5].rstrip().lstrip(),
            'Calib': l[6].rstrip().lstrip(),
            'BackSto': l[7].rstrip().lstrip(),
            'Slides': l[8].rstrip().lstrip()}})
    return DStore

def get_modelStoreLastUpdate(RutesList):
    ''' #Devuelve un diccionario con la informacion de la tabla Update en el configfile.
        #Funcion operacional.
        #Argumentos:
        - RutesList= lista, es el resultado de leer el configfile con al.get_ruteslist.
    '''
    DStoreUpdate = {}
    for l in RutesList:
        l = l.split('|')
        DStoreUpdate.update({l[1].rstrip().lstrip():
            {'Nombre': l[2].rstrip().lstrip(),
            'LastUpdate': l[3].rstrip().lstrip()}})
    return DStoreUpdate

def get_ConfigLines(RutesList, key, keyTable = None, PlotType = None):
    ''' #Devuelve un diccionario con la informacion de las tablas en el configfile: Calib, Store, Update, Plot.
        #Funcion operacional.
        #Argumentos:
        - RutesList= lista, es el resultado de leer el configfile con al.get_ruteslist.
        - key= string, palabra clave de la tabla que se quiere leer. Puede ser: -s,-t.
        - Calib_Storage= string, palabra clave de la tabla que se quiere leer. Puede ser: Calib, Store, Update, Plot.
        - PlotType= boolean, tipo del plot? . Default= None.
    '''
    List = []
    for i in RutesList:
        if i.startswith('|'+key) or i.startswith('| '+key):
            List.append(i)
    if len(List)>0:
        if keyTable == 'Pars':
            return get_modelPars(List)
        if keyTable == 'Paths':
            return get_modelPaths(List)
        if keyTable == 'Store':
            return get_modelStore(List)
        if keyTable == 'Update':
            return get_modelStoreLastUpdate(List)
        if keyTable == 'Plot':
            return get_modelPlot(List, PlotType=PlotType)
        return List
    else:
        return 'Aviso: no se encuentran lineas con el key de inicio especificado.'

#-----------------------------------
#-----------------------------------
#Funciones generacion de radar
#-----------------------------------
#-----------------------------------

def file_format(start,end):
    '''
    Returns the file format customized for siata for elements containing
    starting and ending point
    Parameters
    ----------
    start        : initial date
    end          : final date
    Returns
    ----------
    file format with datetimes like %Y%m%d%H%M
    Example
    ----------
    '''
    start,end = pd.to_datetime(start),pd.to_datetime(end)
    format = '%Y%m%d%H%M'
    return '%s-%s'%(start.strftime(format),end.strftime(format))

def hdr_to_series(path):
    '''
    Reads hdr rain files and converts it into pandas Series
    Parameters
    ----------
    path         : path to .hdr file
    Returns
    ----------
    pandas time Series with mean radar rain
    '''
    s =  pd.read_csv(path,skiprows=5,usecols=[2,3]).set_index(' Fecha ')[' Lluvia']
    s.index = pd.to_datetime(list(map(lambda x:x.strip()[:10]+' '+x.strip()[11:],s.index)))
    return s

def hdr_to_df(path):
    '''
    Reads hdr rain files and converts it into pandas DataFrame
    Parameters
    ----------
    path         : path to .hdr file
    Returns
    ----------
    pandas DataFrame with mean radar rain
    '''
    if path.endswith('.hdr') != True:
        path = path+'.hdr'
    df = pd.read_csv(path,skiprows=5).set_index(' Fecha ')
    df.index = pd.to_datetime(list(map(lambda x:x.strip()[:10]+' '+x.strip()[11:],df.index)))
    df = df.drop('IDfecha',axis=1)
    df.columns = ['record','mean_rain']
    return df

def bin_to_df(path,ncells,start=None,end=None,**kwargs):
    '''
    Reads rain fields (.bin) and converts it into pandas DataFrame
    Parameters
    ----------
    path         : path to .hdr and .bin file
    start        : initial date
    end          : final date
    Returns
    ----------
    pandas DataFrame with mean radar rain
    Note
    ----------
    path without extension, ejm folder_path/file not folder_path/file.bin,
    if start and end is None, the program process all the data
    '''
    start,end = pd.to_datetime(start),pd.to_datetime(end)
    records = df['record'].values
    rain_field = []
    for count,record in enumerate(records):
        if record != 1:
            rain_field.append(wmf.models.read_int_basin('%s.bin'%path,record,ncells)[0]/1000.0)
            count = count+1
#             format = (count*100.0/len(records),count,len(records))
        else:
            rain_field.append(np.zeros(ncells))
    return pd.DataFrame(np.matrix(rain_field),index=df.index)


def get_radar_rain(start,end,Dt,cuenca,codigos,rutaNC,accum=False,path_tif=None,all_radextent=False,
                    mask=None,meanrain_ALL=True,path_masks_csv=None,complete_naninaccum=False,save_bin=False,
                   save_class = False,path_res=None,umbral=0.005,
                   verbose=True):

    start,end = pd.to_datetime(start),pd.to_datetime(end)
    #hora UTC
    startUTC,endUTC = start + pd.Timedelta('5 hours'), end + pd.Timedelta('5 hours')
    fechaI,fechaF,hora_1,hora_2 = startUTC.strftime('%Y-%m-%d'), endUTC.strftime('%Y-%m-%d'),startUTC.strftime('%H:%M'),endUTC.strftime('%H:%M')

    #Obtiene las fechas por dias para listar archivos por dia
    datesDias = pd.date_range(fechaI, fechaF,freq='D')

    a = pd.Series(np.zeros(len(datesDias)),index=datesDias)
    a = a.resample('A').sum()
    Anos = [i.strftime('%Y') for i in a.index.to_pydatetime()]

    datesDias = [d.strftime('%Y%m%d') for d in datesDias.to_pydatetime()]

    #lista los .nc existentes de ese dia: rutas y fechas del nombre del archivo
    ListDatesinNC = []
    ListRutas = []
    for d in datesDias:
        try:
            L = glob.glob(rutaNC + d + '*.nc')
            ListRutas.extend(L)
            ListDatesinNC.extend([i.split('/')[-1].split('_')[0] for i in L])
        except:
            print ('Sin archivos para la fecha %s'%d)

    # Organiza las listas de rutas y la de las fechas a las que corresponde cada ruta.
    ListRutas.sort()
    ListDatesinNC.sort()#con estas fechas se asignaran los barridos a cada timestep.

    #index con las fechas especificas de los .nc existentes de radar
    datesinNC = [dt.datetime.strptime(d,'%Y%m%d%H%M') for d in ListDatesinNC]
    datesinNC = pd.to_datetime(datesinNC)

    #Obtiene el index con la resolucion deseada, en que se quiere buscar datos existentes de radar, 
    textdt = '%d' % Dt
    #Agrega hora a la fecha inicial
    if hora_1 != None:
            inicio = fechaI+' '+hora_1
    else:
            inicio = fechaI
    #agrega hora a la fecha final
    if hora_2 != None:
            final = fechaF+' '+hora_2
    else:
            final = fechaF
    datesDt = pd.date_range(inicio,final,freq = textdt+'s')

    #Obtiene las posiciones de acuerdo al dt para cada fecha, si no hay barrido en ese paso de tiempo se acumula 
    #elbarrido inmediatamente anterior.
    #Saca una lista con las pos de los barridos por cada timestep, y las pega en PosDates
    #Si el limite de completar faltantes con barrido anterior es de 10 min, solo se completa si dt=300s
    #limite de autocompletar : 10m es decir, solo repito un barrido.
    PosDates = []
    pos1 = []
    pos_completed = []
    lim_completed = 3 #ultimos 3 barridos - 15min
    for ind,d1,d2 in zip(np.arange(datesDt[:-1].size),datesDt[:-1],datesDt[1:]):
            pos2 = np.where((datesinNC<d2) & (datesinNC>=d1))[0].tolist()

            # si no hay barridos en el dt de inicio sellena con zero - lista vacia
            #y no esta en los primero 3 pasos : 15min.
            # si se puede completar 
            # y si en el los lim_completed pasos atras no hubo más de lim_completed-1 pos con pos_completed=2, lim_completed-1 para que deje correr sólo hasta el lim_completed.
            #asi solo se pueded completar y pos_completed=2 una sola vez.
            if len(pos2) == 0 and ind not in np.arange(lim_completed) and complete_naninaccum == True and Dt == 300. and np.where(np.array(pos_completed[ind-lim_completed:])==2)[0].size <= lim_completed-1 : #+1 porque coge los ultimos n-1 posiciones.
                    pos2 = pos1
                    pos_completed.append(2)
            elif len(pos2) == 0:
                    pos2=[]
                    pos_completed.append(0)
            else:
                pos_completed.append(1)
            #si se quiere completar y hay barridos en este dt, guarda esta pos para si es necesario completar las pos de dt en el sgte paso 
            if complete_naninaccum == True and len(pos2) != 0 and Dt == 300. and np.where(np.array(pos_completed[ind-lim_completed:])==2)[0].size <= lim_completed-1 : 
                pos1 = pos2
            else:
                pos1 = []   

            PosDates.append(pos2)

    # paso a hora local
    datesDt = datesDt - dt.timedelta(hours=5)
    datesDt = datesDt.to_pydatetime()
    #Index de salida en hora local
    rng= pd.date_range(start.strftime('%Y-%m-%d %H:%M'),end.strftime('%Y-%m-%d %H:%M'), freq=  textdt+'s')
    df = pd.DataFrame(index = rng,columns=codigos)

    #mascara con shp a parte de wmf
    if mask is not None:
        #se abre un barrido para sacar la mascara
        g = netCDF4.Dataset(ListRutas[PosDates[0][0]])
        field = g.variables['Rain'][:].T/(((len(pos)*3600)/Dt)*1000.0)#g['Rain'][:]#
        RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]
        g.close()
        longs=np.array([RadProp[2]+0.5*RadProp[4]+i*RadProp[4] for i in range(RadProp[0])])
        lats=np.array([RadProp[3]+0.5*RadProp[5]+i*RadProp[5] for i in range(RadProp[1])])
        x,y =  np.meshgrid(longs,lats)
        #mask as a shp
        if type(mask) == str:
            #boundaries
            shp = gpd.read_file(mask)
            poly = shp.geometry.unary_union
            
            shp_mask = np.zeros([len(lats),len(longs)])
            for i in range(len(lats)):
                for j in range(len(longs)):
                     if (poly.contains(Point(longs[j],lats[i])))==True:
                        shp_mask[i,j] = 1# Rain_mask es la mascara

            l = x[shp_mask==1].min()
            r = x[shp_mask==1].max()
            d = y[shp_mask==1].min()
            a = y[shp_mask==1].max()
        #mask as a list with coordinates whithin the radar extent
        elif type(mask) == list:
            l = mask[0] ; r = mask[1] ; d = mask[2] ; a = mask[3] 
            x,y = x.T,y.T #aun tengo dudas con el recorte, si en nc queda en la misma pos que los lats,longs.

        #boundaries position
        x_wh,y_wh = np.where((x>l)&(x<r)&(y>d)&(y<a))
        #se redefine sfield con size que corresponde
        field = field[np.unique(x_wh)[0]:np.unique(x_wh)[-1],np.unique(y_wh)[0]:np.unique(y_wh)[-1]]

        if save_bin and len(codigos)==1 and path_res is not None:
            #open nc file
            f = netCDF4.Dataset(path_res,'w', format='NETCDF4') #'w' stands for write

            tempgrp = f.createGroup('rad_data') # as folder for saving files
            lon = longs[np.unique(x_wh)[0]:np.unique(x_wh)[-1]]
            lat = lats[np.unique(y_wh)[0]:np.unique(y_wh)[-1]]
            #set name and leght of dimensions
            tempgrp.createDimension('lon', len(lon))
            tempgrp.createDimension('lat', len(lat))
            tempgrp.createDimension('time', None)
            #building variables
            longitude = tempgrp.createVariable('longitude', 'f4', 'lon')
            latitude = tempgrp.createVariable('latitude', 'f4', 'lat')  
            rain = tempgrp.createVariable('rain', 'f4', (('time', 'lat', 'lon')))
            time = tempgrp.createVariable('time', 'i4', 'time')
            #adding globalattributes
            f.description = "Radar rainfall dataset containing one group"
            f.history = "Created " + dt.datetime.now().strftime("%d/%m/%y")
            #Add local attributes to variable instances
            longitude.units = 'degrees east - wgs4'
            latitude.units = 'degrees north - wgs4'
            time.units = 'minutes since 2020-01-01 00:00'
            rain.units = 'mm/h'
            #passing data into variables
            # use proper indexing when passing values into the variables - just like you would a numpy array.
            longitude[:] = lon #The "[:]" at the end of the variable instance is necessary
            latitude[:] = lat

    else:
        # acumular dentro de la cuenca.
        cu = wmf.SimuBasin(rute= cuenca)
        if save_class:
            cuConv = wmf.SimuBasin(rute= cuenca)
            cuStra = wmf.SimuBasin(rute= cuenca)

    #accumulated in basin
    if accum:
        if mask is not None:
            rvec_accum = np.zeros(field.shape)
            dfaccum = pd.DataFrame(index = rng) #este producto no da con mask.
        else:
            rvec_accum = np.zeros(cu.ncells)
    #             rvec = np.zeros(cu.ncells)
            dfaccum = pd.DataFrame(np.zeros((cu.ncells,rng.size)).T,index = rng)
    else:
        pass

    #all extent
    if all_radextent:
        radmatrix = np.zeros((1728, 1728))


    #ITERA SOBRE LOS BARRIDOS DEL PERIODO Y SE SACAN PRODUCTOS
    # print ListRutas
    for ind,dates,pos in zip(np.arange(len(datesDt[1:])),datesDt[1:],PosDates):
            #escoge como definir el size de rvec
            if mask is not None:
                rvec = np.zeros(shape = field.shape)
            else: 
                rvec = np.zeros(cu.ncells)
                if save_class:
                    rConv = np.zeros(cu.ncells, dtype = int)   
                    rStra = np.zeros(cu.ncells, dtype = int)   
            try:
                    #se lee y agrega lluvia de los nc en el intervalo.
                    for c,p in enumerate(pos):
                            #lista archivo leido
                            if verbose:
                                print (ListRutas[p])
                            #Lee la imagen de radar para esa fecha
                            g = netCDF4.Dataset(ListRutas[p])
                            rainfield = g.variables['Rain'][:].T/(((len(pos)*3600)/Dt)*1000.0)
                            RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]
                            #if all extent
                            if all_radextent:
                                radmatrix += rainfield

                            #if mask
                            if mask is not None and type(mask) == str:
                                rvec += (rainfield*shp_mask)[np.unique(x_wh)[0]:np.unique(x_wh)[-1],np.unique(y_wh)[0]:np.unique(y_wh)[-1]]
                            elif mask is not None and type(mask) == list:
                                rvec += rainfield[np.unique(x_wh)[0]:np.unique(x_wh)[-1],np.unique(y_wh)[0]:np.unique(y_wh)[-1]]
                            # on WMF.
                            else:
                                #Agrega la lluvia en el intervalo 
                                rvec += cu.Transform_Map2Basin(rainfield,RadProp)
                                if save_class:
                                    ConvStra = cu.Transform_Map2Basin(g.variables['Conv_Strat'][:].T, RadProp)
                                    # 1-stra, 2-conv
                                    rConv = np.copy(ConvStra) 
                                    rConv[rConv == 1] = 0; rConv[rConv == 2] = 1
                                    rStra = np.copy(ConvStra)
                                    rStra[rStra == 2] = 0 
                                    rvec[(rConv == 0) & (rStra == 0)] = 0
                                    Conv[rvec == 0] = 0
                                    Stra[rvec == 0] = 0
                            #Cierra el netCDF
                            g.close()
                    #muletilla
                    path = 'bla'
            except:
                    print ('error - no field found ')
                    path = ''
                    if accum:
                        if mask is not None:
                            rvec += np.zeros(shape = field.shape)
                            rvec = np.zeros(shape = field.shape)
                        else:
                            rvec_accum += np.zeros(cu.ncells)
                            rvec = np.zeros(cu.ncells)
                    else:
                        if mask is not None:
                            rvec = np.zeros(shape = field.shape)
                        else:
                            rvec = np.zeros(cu.ncells)
                            if save_class:
                                rConv = np.zeros(cu.ncells)
                                rStra = np.zeros(cu.ncells)
                    if all_radextent:
                        radmatrix += np.zeros((1728, 1728))
            #acumula dentro del for que recorre las fechas
            if accum:
                rvec_accum += rvec
                if mask is None: #esto para mask no sirve
                    dfaccum.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]= rvec
            else:
                pass

            # si se quiere sacar promedios de lluvia de radar en varias cuencas definidas en 'codigos'
            #subbasins defined for WMF
            if meanrain_ALL and mask is None:
                mean = []
                df_posmasks = pd.read_csv(path_masks_csv,index_col=0)
                for codigo in codigos:
                        if path == '': # si no hay nc en ese paso de tiempo.
                            mean.append(np.nan)
                        else:
                             mean.append(np.sum(rvec*df_posmasks['%s'%codigo])/float(df_posmasks['%s'%codigo][df_posmasks['%s'%codigo]==1].size))
                # se actualiza la media de todas las mascaras en el df.
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean             
            else:
                pass

            #guarda binario y df, si guardar binaria paso a paso no me interesa rvecaccum
            if mask is None and save_bin == True and len(codigos)==1 and path_res is not None:
                mean = []
                #guarda en binario 
                dentro = cu.rain_radar2basin_from_array(vec = rvec,
                    ruta_out = path_res,
                    fecha = dates,
                    dt = Dt,
                    umbral = umbral)

                #si guarda nc de ese timestep guarda clasificados
                if dentro == 0: 
                    hagalo = True
                else:
                    hagalo = False
                #mira si guarda o no los clasificados
                if save_class:
                    #Escribe el binario convectivo
                    aa = cuConv.rain_radar2basin_from_array(vec = rConv,
                        ruta_out = path_res+'_conv',
                        fecha = dates,
                        dt = Dt,
                        doit = hagalo)
                    #Escribe el binario estratiforme
                    aa = cuStra.rain_radar2basin_from_array(vec = rStra,
                        ruta_out = path_res+'_stra',
                        fecha = dates,
                        dt = Dt,
                        doit = hagalo)

                #guarda en df meanrainfall.
                try:
                    mean.append(rvec.mean())
                except:
                    mean.append(np.nan)
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean
                
            elif mask is None and save_bin == True and len(codigos)==1 and path_res is None: #si es una cuenca pero no se quiere guardar binarios.
                mean = []
                #guarda en df meanrainfall.
                try:
                    mean.append(rvec.mean())
                except:
                    mean.append(np.nan)
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean

            #guardar .nc con info de recorte de radar: mask.
            if mask is not None and save_bin and len(codigos)==1 and path_res is not None:
                mean = []
                #https://pyhogs.github.io/intro_netcdf4.html
                rain[ind,:,:] = rvec.T
                time[ind] = int((dates - pd.to_datetime('2010-01-01 00:00')).total_seconds()/60) #min desde 2010
                if ind == np.arange(len(datesDt[1:]))[-1]:
                    f.close()
                    print ('.nc saved')
                #guarda en df meanrainfall.
                if path == '': # si no hay nc en ese paso de tiempo.
                    mean.append(np.nan)
                else:
                    mean.append(np.sum(rvec)/float(shp_mask[shp_mask==1].size))
                #save
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean

    if mask is None and save_bin == True and len(codigos)==1 and path_res is not None:
        #Cierrra el binario y escribe encabezado
        cu.rain_radar2basin_from_array(status = 'close',ruta_out = path_res)
        print ('.bin & .hdr saved')
        if save_class:
            cuConv.rain_radar2basin_from_array(status = 'close',ruta_out = path_res+'_conv')
            cuStra.rain_radar2basin_from_array(status = 'close',ruta_out = path_res+'_stra')
            print ('.bin & .hdr escenarios saved')
    else:
        print ('.bin & .hdr NOT saved')
        pass

    #elige los retornos.
    if accum == True and path_tif is not None:
        cu.Transform_Basin2Map(rvec_accum,path_tif)
        return df,rvec_accum,dfaccum
    elif accum == True and mask is not None:
        return df,rvec_accum
    elif accum == True and mask is None:
        return df,rvec_accum,dfaccum
    elif all_radextent:
        return df,radmatrix
    else:
        return df     

def get_radar_rain_OP(start,end,Dt,cuenca,codigos,rutaNC,accum=False,path_tif=None,all_radextent=False,
                      meanrain_ALL=True,complete_naninaccum=False, evs_hist=False,save_bin=False,save_class = False,
                      path_res=None,umbral=0.005,include_escenarios = None,
                      verbose=True):
    '''
    Read .nc's file forn rutaNC:101Radar_Class within assigned period and frequency.
    Por ahora solo sirve con un barrido por timestep, operacional a 5 min, melo.

    0. It divides by 1000.0 and converts from mm/5min to mm/h.
    1. Get mean radar rainfall in basins assigned in 'codigos' for finding masks, if the mask exist.
    2. Write binary files if is setted.
    - Cannot do both 1 and 2.
    - To saving binary files (2) set: meanrain_ALL=False, save_bin=True, path_res= path where to write results, 
      len('codigos')=1, nc_path aims to the one with dxp and simubasin props setted.

    Parameters
    ----------
    start:        string, date&time format %Y-%m%-d %H:%M, local time.
    end:          string, date&time format %Y-%m%-d %H:%M, local time.
    Dt:           float, timedelta in seconds. For this function it should be lower than 3600s (1h).
    cuenca:       string, simubasin .nc path with dxp and format from WMF. It should be 260 path if whole catchment analysis is needed, or any other .nc path for saving the binary file.
    codigos:       list, with codes of stage stations. Needed for finding the mask associated to a basin.
    rutaNC:       string, path with .nc files from radar meteorology group. Default in amazonas: 101Radar_Class

    Optional Parameters
    ----------
    accum:        boolean, default False. True for getting the accumulated matrix between start and end.
                  Change returns: df,rvec (accumulated)
    path_tif:     string, path of tif to write accumlated basin map. Default None.
    all_radextent:boolean, default False. True for getting the accumulated matrix between start and end in the
                  whole radar extent. Change returns: df,radmatrix.
    meanrain_ALL: boolean, defaul True. True for getting the mean radar rainfall within several basins which mask are defined in 'codigos'.
    save_bin:     boolean, default False. True for saving .bin and .hdr files with rainfall and if len('codigos')=1.
    save_class:  boolean,default False. True for saving .bin and .hdr for convective and stratiform classification. Applies if len('codigos')=1 and save_bin = True.
    path_res:     string with path where to write results if save_bin=True, default None.
    umbral:       float. Minimum umbral for writing rainfall, default = 0.005.

    Returns
    ----------
    - df whith meanrainfall of assiged codes in 'codigos'.
    - df,rvec if accum = True.
    - df,radmatrix if all_radextent = True.
    - save .bin and .hdr if save_bin = True, len('codigos')=1 and path_res=path.

    '''
    

    #### FECHAS Y ASIGNACIONES DE NC####

    start,end = pd.to_datetime(start),pd.to_datetime(end)
    #hora UTC
    startUTC,endUTC = start + pd.Timedelta('5 hours'), end + pd.Timedelta('5 hours')
    fechaI,fechaF,hora_1,hora_2 = startUTC.strftime('%Y-%m-%d'), endUTC.strftime('%Y-%m-%d'),startUTC.strftime('%H:%M'),endUTC.strftime('%H:%M')

    #Obtiene las fechas por dias para listar archivos por dia
    datesDias = pd.date_range(fechaI, fechaF,freq='D')

    a = pd.Series(np.zeros(len(datesDias)),index=datesDias)
    a = a.resample('A').sum()
    Anos = [i.strftime('%Y') for i in a.index.to_pydatetime()]

    datesDias = [d.strftime('%Y%m%d') for d in datesDias.to_pydatetime()]

    #lista los .nc existentes de ese dia: rutas y fechas del nombre del archivo
    ListDatesinNC = []
    ListRutas = []
    for d in datesDias:
        try:
            L = glob.glob(rutaNC + d + '*.nc')
            ListRutas.extend(L)
            ListDatesinNC.extend([i.split('/')[-1].split('_')[0] for i in L])
        except:
            print ('Sin archivos para la fecha %s'%d)

    # Organiza las listas de dias y de rutas
    ListDatesinNC.sort()
    ListRutas.sort()

    #index con las fechas especificas de los .nc existentes de radar
    datesinNC = [dt.datetime.strptime(d,'%Y%m%d%H%M') for d in ListDatesinNC]
    datesinNC = pd.to_datetime(datesinNC)

    #Obtiene el index con la resolucion deseada, en que se quiere buscar datos existentes de radar, 
    textdt = '%d' % Dt
    #Agrega hora a la fecha inicial
    if hora_1 != None:
            inicio = fechaI+' '+hora_1
    else:
            inicio = fechaI
    #agrega hora a la fecha final
    if hora_2 != None:
            final = fechaF+' '+hora_2
    else:
            final = fechaF
    datesDt = pd.date_range(inicio,final,freq = textdt+'s')

    #Obtiene las posiciones de acuerdo al dt para cada fecha, si no hay barrido en ese paso de tiempo se acumula 
    #elbarrido inmediatamente anterior.
    PosDates = []
    pos1 = [0]
    for d1,d2 in zip(datesDt[:-1],datesDt[1:]):
            pos2 = np.where((datesinNC<d2) & (datesinNC>=d1))[0].tolist()
            if len(pos2) == 0 and complete_naninaccum == True: # si no hay barridos en el dt de inicio ellena con cero
                    pos2 = pos1
            elif complete_naninaccum == True: #si hay barridos en este dt guarda esta pos para si es necesario completar las pos de dt en el sgte paso 
                    pos1 = pos2
            elif len(pos2) == 0:
                    pos2=[]
            PosDates.append(pos2)

    paths_inperiod  = [[ListRutas[p] for c,p in enumerate(pos)] for dates,pos in zip(datesDt[1:],PosDates)]
    pospaths_inperiod  = [[p for c,p in enumerate(pos)] for dates,pos in zip(datesDt[1:],PosDates)]

    ######### LISTA EN ORDEN CON ARCHIVOS OBSERVADOS Y ESCENARIOS#############3

    ##### buscar el ultimo campo de lluvia observado ######
    datessss  = []
    nc010 = []
    for date,l_step,lpos_step in zip(datesDt[1:],paths_inperiod,pospaths_inperiod):
        for path,pospath in zip(l_step[::-1],lpos_step[::-1]): # que siempre el primer nc leido sea el observado si lo hay
            #siempre intenta buscar en cada paso de tiempo el observado, solo si no puede, busca escenarios futuros.
            if path.split('/')[-1].split('_')[-1].split('.')[0].endswith('120'):
                nc010.append(path)
                datessss.append(date)

    ######punto a  partir del cual usar escenarios
    #si dentro del periodo existe alguno len(date)>1, sino = 0 (todo el periodo corresponde a forecast)
    #si no existe pos_lastradarfield = pos del primer paso de tiempo paraque se cojan todos los archivos
    if len(datessss)>0:
        pos_lastradarfield = np.where(datesDt[1:]==datessss[-1])[0][0]
    else:
        pos_lastradarfield = 0

    list_paths= []

    # escoge rutas y pos organizados para escenarios, por ahora solo sirve con 1 barrido por timestep.
    for ind,date,l_step,lpos_step in zip(np.arange(datesDt[1:].size),datesDt[1:],paths_inperiod,pospaths_inperiod):
    #     pos_step = []; paths_step = []
        if len(l_step) == 0:
            list_paths.append('')
        else:
            # ordenar rutas de ncs
            for path,pospath in zip(l_step[::-1],lpos_step[::-1]): # que siempre el primer nc leido sea el observado si lo hay
    #             print (ind,path,pospath)

                #si es un evento viejo
                if evs_hist:
                    #primero escanarios futuros.

                    if include_escenarios is not None and path.split('/')[-1].split('_')[-1].startswith(include_escenarios): 
                        list_paths.append(path)
                        break
                    #despues observados.
                    elif path.split('/')[-1].split('_')[-1].split('.')[0].endswith('120'):
                        list_paths.append(path)
                #si es rigth now
                else:
                    #primero observados y para ahi si se lo encontro
                    if path.split('/')[-1].split('_')[-1].split('.')[0].endswith('120'):
                        list_paths.append(path)
                        break
                    #despues escenarios futuros, y solo despues que se acaban observados
                    elif include_escenarios is not None and path.split('/')[-1].split('_')[-1].startswith(include_escenarios) and ind > pos_lastradarfield: 
                        list_paths.append(path)

    ######### LECTURA DE CUENCA, DATOS Y GUARDADO DE BIN.###########

    # acumular dentro de la cuenca.
    cu = wmf.SimuBasin(rute= cuenca)
    if save_class:
        cuConv = wmf.SimuBasin(rute= cuenca)
        cuStra = wmf.SimuBasin(rute= cuenca)
    # paso a hora local
    datesDt = datesDt - dt.timedelta(hours=5)
    datesDt = datesDt.to_pydatetime()
    #Index de salida en hora local
    rng= pd.date_range(start.strftime('%Y-%m-%d %H:%M'),end.strftime('%Y-%m-%d %H:%M'), freq=  textdt+'s')
    df = pd.DataFrame(index = rng,columns=codigos)

    #accumulated in basin
    if accum:
        rvec_accum = np.zeros(cu.ncells)
        rvec = np.zeros(cu.ncells)
        dfaccum = pd.DataFrame(np.zeros((cu.ncells,rng.size)).T,index = rng)
    else:
        pass

    #all extent
    if all_radextent:
        radmatrix = np.zeros((1728, 1728))

    #itera sobre ncs abre y guarda ifnfo
    for dates,path in zip(datesDt[1:],list_paths):

            if verbose:
                print (dates,path)

            rvec = np.zeros(cu.ncells)   

            if path != '': #sino hay archivo pone cero.
                try:
                    #Lee la imagen de radar para esa fecha
                    g = netCDF4.Dataset(path)
                    #if all extent
                    if all_radextent:
                        radmatrix += g.variables['Rain'][:].T/(((1*3600)/Dt)*1000.0) 
                    #on basins --> wmf.
                    RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]
                    #Agrega la lluvia en el intervalo 
                    rvec += cu.Transform_Map2Basin(g.variables['Rain'][:].T/(((1*3600)/Dt)*1000.0),RadProp)
                    if save_class:
                        ConvStra = cu.Transform_Map2Basin(g.variables['Conv_Strat'][:].T, RadProp)
                        # 1-stra, 2-conv
                        rConv = np.copy(ConvStra) 
                        rConv[rConv == 1] = 0; rConv[rConv == 2] = 1
                        rStra = np.copy(ConvStra)
                        rStra[rStra == 2] = 0 
                        rvec[(rConv == 0) & (rStra == 0)] = 0
                        rConv[rvec == 0] = 0
                        rStra[rvec == 0] = 0
                    #Cierra el netCDF
                    g.close()
                except:
                    print ('error - zero field ')
                    if accum:
                        rvec_accum += np.zeros(cu.ncells)
                        rvec = np.zeros(cu.ncells)
                    else:
                        rvec = np.zeros(cu.ncells) 
                        if save_class:
                            rConv = np.zeros(cu.ncells)
                            rStra = np.zeros(cu.ncells)
                    if all_radextent:
                        radmatrix += np.zeros((1728, 1728))
            else:
                print ('error - zero field ')
                if accum:
                    rvec_accum += np.zeros(cu.ncells)
                    rvec = np.zeros(cu.ncells)
                else:
                    rvec = np.zeros(cu.ncells) 
                    if save_class:
                        rConv = np.zeros(cu.ncells)
                        rStra = np.zeros(cu.ncells)
                if all_radextent:
                    radmatrix += np.zeros((1728, 1728))

            #acumula dentro del for que recorre las fechas
            if accum:
                rvec_accum += rvec
                dfaccum.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]= rvec
            else:
                pass
            # si se quiere sacar promedios de lluvia de radar en varias cuencas definidas en 'codigos'
            if meanrain_ALL:
                mean = []
                #para todas
                for codigo in codigos:
                    if '%s.tif'%(codigo) in os.listdir('/media/nicolas/Home/nicolas/01_SIATA/info_operacional_cuencas_nivel/red_nivel/tif_mascaras/'):
                        mask_path = '/media/nicolas/Home/nicolas/01_SIATA/info_operacional_cuencas_nivel/red_nivel/tif_mascaras/%s.tif'%(codigo)
                        mask_map = wmf.read_map_raster(mask_path)
                        mask_vect = cu.Transform_Map2Basin(mask_map[0],mask_map[1])
                    else:
                        mask_vect = None
                    if mask_vect is not None:
                        if path == '': # si no hay nc en ese paso de tiempo.
                            mean.append(np.nan)
                        else:
                            try:
                                mean.append(np.sum(mask_vect*rvec)/float(mask_vect[mask_vect==1].size))
                            except: # para las que no hay mascara.
                                mean.append(np.nan)
                # se actualiza la media de todas las mascaras en el df.
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean             
            else:
                pass

            #guarda binario y df, si guardar binaria paso a paso no me interesa rvecaccum
            if save_bin == True and len(codigos)==1 and path_res is not None:
                #guarda en binario 
                dentro = cu.rain_radar2basin_from_array(vec = rvec,
                    ruta_out = path_res,
                    fecha = dates,
                    dt = Dt,
                    umbral = umbral)

                #guarda en df meanrainfall.
                mean = []
                if path != '':
                    mean.append(rvec.mean())
                else:
                    mean.append(np.nan)
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean

    if save_bin == True and len(codigos)==1 and path_res is not None:
        #Cierrra el binario y escribe encabezado
        cu.rain_radar2basin_from_array(status = 'close',ruta_out = path_res)
        print ('.bin & .hdr saved')
        if save_class:
            cuConv.rain_radar2basin_from_array(status = 'close',ruta_out = path_res+'_conv')
            cuStra.rain_radar2basin_from_array(status = 'close',ruta_out = path_res+'_stra')
            print ('.bin & .hdr escenarios saved')
    else:
        print ('.bin & .hdr NOT saved')

    #elige los retornos.
    if accum == True and path_tif is not None:
        cu.Transform_Basin2Map(rvec_accum,path_tif)
        return df,rvec_accum,dfaccum
    elif accum == True:
        return df,rvec_accum,dfaccum
    elif all_radextent:
        return df,radmatrix
    else:
        return df 
    
def get_radar_rain_OP_newmasks(start,end,Dt,cuenca,codigos,rutaNC,accum=False,path_tif=None,all_radextent=False,
                              meanrain_ALL=True,complete_naninaccum=False, evs_hist=False,save_bin=False,save_class = False,
                              path_res=None,umbral=0.005,include_escenarios = None, 
                              path_masks_csv = None,verbose=True):

    '''
    Read .nc's file forn rutaNC:101Radar_Class within assigned period and frequency.
    Por ahora solo sirve con un barrido por timestep, operacional a 5 min, melo.

    0. It divides by 1000.0 and converts from mm/5min to mm/h.
    1. Get mean radar rainfall in basins assigned in 'codigos' for finding masks, if the mask exist.
    2. Write binary files if is setted.
    - Cannot do both 1 and 2.
    - To saving binary files (2) set: meanrain_ALL=False, save_bin=True, path_res= path where to write results, 
      len('codigos')=1, nc_path aims to the one with dxp and simubasin props setted.

    Parameters
    ----------
    start:        string, date&time format %Y-%m%-d %H:%M, local time.
    end:          string, date&time format %Y-%m%-d %H:%M, local time.
    Dt:           float, timedelta in seconds. For this function it should be lower than 3600s (1h).
    cuenca:       string, simubasin .nc path with dxp and format from WMF. It should be 260 path if whole catchment analysis is needed, or any other .nc path for saving the binary file.
    codigos:       list, with codes of stage stations. Needed for finding the mask associated to a basin.
    rutaNC:       string, path with .nc files from radar meteorology group. Default in amazonas: 101Radar_Class

    Optional Parameters
    ----------
    accum:        boolean, default False. True for getting the accumulated matrix between start and end.
                  Change returns: df,rvec (accumulated)
    path_tif:     string, path of tif to write accumlated basin map. Default None.
    all_radextent:boolean, default False. True for getting the accumulated matrix between start and end in the
                  whole radar extent. Change returns: df,radmatrix.
    meanrain_ALL: boolean, defaul True. True for getting the mean radar rainfall within several basins which mask are defined in 'codigos'.
    save_bin:     boolean, default False. True for saving .bin and .hdr files with rainfall and if len('codigos')=1.
    save_class:  boolean,default False. True for saving .bin and .hdr for convective and stratiform classification. Applies if len('codigos')=1 and save_bin = True.
    path_res:     string with path where to write results if save_bin=True, default None.
    umbral:       float. Minimum umbral for writing rainfall, default = 0.005.
    include_escenarios: string wth the name of scenarios to use for future.
    path_masks_csv: string with path of csv with pos of masks, pos are related tu the shape of the simubasin designated.

    Returns
    ----------
    - df whith meanrainfall of assiged codes in 'codigos'.
    - df,rvec if accum = True.
    - df,radmatrix if all_radextent = True.
    - save .bin and .hdr if save_bin = True, len('codigos')=1 and path_res=path.

    '''


    #### FECHAS Y ASIGNACIONES DE NC####

    start,end = pd.to_datetime(start),pd.to_datetime(end)
    #hora UTC
    startUTC,endUTC = start + pd.Timedelta('5 hours'), end + pd.Timedelta('5 hours')
    fechaI,fechaF,hora_1,hora_2 = startUTC.strftime('%Y-%m-%d'), endUTC.strftime('%Y-%m-%d'),startUTC.strftime('%H:%M'),endUTC.strftime('%H:%M')

    #Obtiene las fechas por dias para listar archivos por dia
    datesDias = pd.date_range(fechaI, fechaF,freq='D')

    a = pd.Series(np.zeros(len(datesDias)),index=datesDias)
    a = a.resample('A').sum()
    Anos = [i.strftime('%Y') for i in a.index.to_pydatetime()]

    datesDias = [d.strftime('%Y%m%d') for d in datesDias.to_pydatetime()]

    #lista los .nc existentes de ese dia: rutas y fechas del nombre del archivo
    ListDatesinNC = []
    ListRutas = []
    for d in datesDias:
        try:
            L = glob.glob(rutaNC + d + '*.nc')
            ListRutas.extend(L)
            ListDatesinNC.extend([i.split('/')[-1].split('_')[0] for i in L])
        except:
            print ('Sin archivos para la fecha %s'%d)

    # Organiza las listas de dias y de rutas
    ListDatesinNC.sort()
    ListRutas.sort()

    #index con las fechas especificas de los .nc existentes de radar
    datesinNC = [dt.datetime.strptime(d,'%Y%m%d%H%M') for d in ListDatesinNC]
    datesinNC = pd.to_datetime(datesinNC)

    #Obtiene el index con la resolucion deseada, en que se quiere buscar datos existentes de radar, 
    textdt = '%d' % Dt
    #Agrega hora a la fecha inicial
    if hora_1 != None:
            inicio = fechaI+' '+hora_1
    else:
            inicio = fechaI
    #agrega hora a la fecha final
    if hora_2 != None:
            final = fechaF+' '+hora_2
    else:
            final = fechaF
    datesDt = pd.date_range(inicio,final,freq = textdt+'s')

    #Obtiene las posiciones de acuerdo al dt para cada fecha, si no hay barrido en ese paso de tiempo se acumula 
    #elbarrido inmediatamente anterior.
    PosDates = []
    pos1 = [0]
    for d1,d2 in zip(datesDt[:-1],datesDt[1:]):
            pos2 = np.where((datesinNC<d2) & (datesinNC>=d1))[0].tolist()
            if len(pos2) == 0 and complete_naninaccum == True: # si no hay barridos en el dt de inicio ellena con cero
                    pos2 = pos1
            elif complete_naninaccum == True: #si hay barridos en este dt guarda esta pos para si es necesario completar las pos de dt en el sgte paso 
                    pos1 = pos2
            elif len(pos2) == 0:
                    pos2=[]
            PosDates.append(pos2)

    paths_inperiod  = [[ListRutas[p] for c,p in enumerate(pos)] for dates,pos in zip(datesDt[1:],PosDates)]
    pospaths_inperiod  = [[p for c,p in enumerate(pos)] for dates,pos in zip(datesDt[1:],PosDates)]

    ######### LISTA EN ORDEN CON ARCHIVOS OBSERVADOS Y ESCENARIOS#############3

    ##### buscar el ultimo campo de lluvia observado ######
    datessss  = []
    nc010 = []
    for date,l_step,lpos_step in zip(datesDt[1:],paths_inperiod,pospaths_inperiod):
        for path,pospath in zip(l_step[::-1],lpos_step[::-1]): # que siempre el primer nc leido sea el observado si lo hay
            #siempre intenta buscar en cada paso de tiempo el observado, solo si no puede, busca escenarios futuros.
            if path.split('/')[-1].split('_')[-1].split('.')[0].endswith('120'):
                nc010.append(path)
                datessss.append(date)

    ######punto a  partir del cual usar escenarios
    #si dentro del periodo existe alguno len(date)>1, sino = 0 (todo el periodo corresponde a forecast)
    #si no existe pos_lastradarfield = pos del primer paso de tiempo paraque se cojan todos los archivos
    if len(datessss)>0:
        pos_lastradarfield = np.where(datesDt[1:]==datessss[-1])[0][0]
    else:
        pos_lastradarfield = 0

    list_paths= []

    # escoge rutas y pos organizados para escenarios, por ahora solo sirve con 1 barrido por timestep.
    for ind,date,l_step,lpos_step in zip(np.arange(datesDt[1:].size),datesDt[1:],paths_inperiod,pospaths_inperiod):
    #     pos_step = []; paths_step = []
        if len(l_step) == 0:
            list_paths.append('')
        else:
            # ordenar rutas de ncs
            for path,pospath in zip(l_step[::-1],lpos_step[::-1]): # que siempre el primer nc leido sea el observado si lo hay
    #             print (ind,path,pospath)

                #si es un evento viejo
                if evs_hist:
                    #primero escanarios futuros.

                    if include_escenarios is not None and path.split('/')[-1].split('_')[-1].startswith(include_escenarios): 
                        list_paths.append(path)
                        break
                    #despues observados.
                    elif path.split('/')[-1].split('_')[-1].split('.')[0].endswith('120'):
                        list_paths.append(path)
                #si es rigth now
                else:
                    #primero observados y para ahi si se lo encontro
                    if path.split('/')[-1].split('_')[-1].split('.')[0].endswith('120'):
                        list_paths.append(path)
                        break
                    #despues escenarios futuros, y solo despues que se acaban observados
                    elif include_escenarios is not None and path.split('/')[-1].split('_')[-1].startswith(include_escenarios) and ind > pos_lastradarfield: 
                        list_paths.append(path)

    ######### LECTURA DE CUENCA, DATOS Y GUARDADO DE BIN.###########

    # acumular dentro de la cuenca.
    cu = wmf.SimuBasin(rute= cuenca)
    if save_class:
        cuConv = wmf.SimuBasin(rute= cuenca)
        cuStra = wmf.SimuBasin(rute= cuenca)
    # paso a hora local
    datesDt = datesDt - dt.timedelta(hours=5)
    datesDt = datesDt.to_pydatetime()
    #Index de salida en hora local
    rng= pd.date_range(start.strftime('%Y-%m-%d %H:%M'),end.strftime('%Y-%m-%d %H:%M'), freq=  textdt+'s')
    df = pd.DataFrame(index = rng,columns=codigos)

    #accumulated in basin
    if accum:
        rvec_accum = np.zeros(cu.ncells)
        rvec = np.zeros(cu.ncells)
        dfaccum = pd.DataFrame(np.zeros((cu.ncells,rng.size)).T,index = rng)
    else:
        pass

    #all extent
    if all_radextent:
        radmatrix = np.zeros((1728, 1728))
        

    #itera sobre ncs abre y guarda ifnfo
    for dates,path in zip(datesDt[1:],list_paths):

            if verbose:
                print (dates,path)

            rvec = np.zeros(cu.ncells)   

            if path != '': #sino hay archivo pone cero.
                try:
                    #Lee la imagen de radar para esa fecha
                    g = netCDF4.Dataset(path)
                    #if all extent
                    if all_radextent:
                        radmatrix += g.variables['Rain'][:].T/(((1*3600)/Dt)*1000.0) 
                    #on basins --> wmf.
                    RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]
                    #Agrega la lluvia en el intervalo 
                    rvec += cu.Transform_Map2Basin(g.variables['Rain'][:].T/(((1*3600)/Dt)*1000.0),RadProp)
                    if save_class:
                        ConvStra = cu.Transform_Map2Basin(g.variables['Conv_Strat'][:].T, RadProp)
                        # 1-stra, 2-conv
                        rConv = np.copy(ConvStra) 
                        rConv[rConv == 1] = 0; rConv[rConv == 2] = 1
                        rStra = np.copy(ConvStra)
                        rStra[rStra == 2] = 0 
                        rvec[(rConv == 0) & (rStra == 0)] = 0
                        rConv[rvec == 0] = 0
                        rStra[rvec == 0] = 0
                    #Cierra el netCDF
                    g.close()
                except:
                    print ('error - zero field ')
                    if accum:
                        rvec_accum += np.zeros(cu.ncells)
                        rvec = np.zeros(cu.ncells)
                    else:
                        rvec = np.zeros(cu.ncells) 
                        if save_class:
                            rConv = np.zeros(cu.ncells)
                            rStra = np.zeros(cu.ncells)
                    if all_radextent:
                        radmatrix += np.zeros((1728, 1728))
            else:
                print ('error - zero field ')
                if accum:
                    rvec_accum += np.zeros(cu.ncells)
                    rvec = np.zeros(cu.ncells)
                else:
                    rvec = np.zeros(cu.ncells) 
                    if save_class:
                        rConv = np.zeros(cu.ncells)
                        rStra = np.zeros(cu.ncells)
                if all_radextent:
                    radmatrix += np.zeros((1728, 1728))

            #acumula dentro del for que recorre las fechas
            if accum:
                rvec_accum += rvec
                dfaccum.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]= rvec
            else:
                pass
            # si se quiere sacar promedios de lluvia de radar en varias cuencas definidas en 'codigos'
            if meanrain_ALL:
                mean = []
                #para todas
                df_posmasks = pd.read_csv(path_masks_csv,index_col=0)
                for codigo in codigos:
                        if path == '': # si no hay nc en ese paso de tiempo.
                            mean.append(np.nan)
                        else:
                            try:
                                mean.append(np.sum(rvec*df_posmasks[codigo])/float(df_posmasks[codigo][df_posmasks[codigo]==1].size))
                            except: # para las que no hay mascara.
                                mean.append(np.nan)
                # se actualiza la media de todas las mascaras en el df.
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean             
            else:
                pass

            #guarda binario y df, si guardar binaria paso a paso no me interesa rvecaccum
            if save_bin == True and len(codigos)==1 and path_res is not None:
                #guarda en binario 
                dentro = cu.rain_radar2basin_from_array(vec = rvec,
                    ruta_out = path_res,
                    fecha = dates,
                    dt = Dt,
                    umbral = umbral)

                #guarda en df meanrainfall.
                mean = []
                if path != '':
                    mean.append(rvec.mean())
                else:
                    mean.append(np.nan)
                df.loc[dates.strftime('%Y-%m-%d %H:%M:%S')]=mean

    if save_bin == True and len(codigos)==1 and path_res is not None:
        #Cierrra el binario y escribe encabezado
        cu.rain_radar2basin_from_array(status = 'close',ruta_out = path_res)
        print ('.bin & .hdr saved')
        if save_class:
            cuConv.rain_radar2basin_from_array(status = 'close',ruta_out = path_res+'_conv')
            cuStra.rain_radar2basin_from_array(status = 'close',ruta_out = path_res+'_stra')
            print ('.bin & .hdr escenarios saved')
    else:
        print ('.bin & .hdr NOT saved')

    #elige los retornos.
    if accum == True and path_tif is not None:
        cu.Transform_Basin2Map(rvec_accum,path_tif)
        return df,rvec_accum,dfaccum
    elif accum == True:
        return df,rvec_accum,dfaccum
    elif all_radextent:
        return df,radmatrix
    else:
        return df   

def get_rainfall2sim(ConfigList,cu,path_ncbasin,starts_m,end, #se corre el bin mas largo.
                     Dt= float(wmf.models.dt),include_escenarios=None,
                     evs_hist= False,
                     check_file=True,stepback_start = '%ss'%int(wmf.models.dt *1),
                     complete_naninaccum=True,verbose=False):
    
    #generacion o lectura de lluvia
    start,end = starts_m[-1],end
    start,end = (pd.to_datetime(start)- pd.Timedelta(stepback_start)),pd.to_datetime(end) #start siempre con 1 stepback porque codigo que genera lluvia empieza siempre en paso 1 y no en paso 0.
    #se leen rutas
    codefile = get_ruta(ConfigList,'name_proj')
    rain_path = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_rain')
    ruta_rain = '%s%s_%s-%s'%(rain_path,start.strftime('%Y%m%d%H%M'),end.strftime('%Y%m%d%H%M'),codefile)
    ruta_out_rain = '%s%s_%s-%s.bin'%(rain_path,start.strftime('%Y%m%d%H%M'),end.strftime('%Y%m%d%H%M'),codefile)
    #set model dt
    set_modelsettings(ConfigList)

    if check_file:
        file = os.path.isfile(ruta_rain+'.bin') 
    else:
        file = False

    #si ya existe el binario lo abre y saca el df.
    if file:
        obj =  hdr_to_series(ruta_rain+'.hdr')
        obj = obj.loc[start:end]
    #si no existe el binario
    else:
        if include_escenarios is not None:
    #             print ('include escenarios %s'%include_escenarios)
            ruta_rain = ruta_out_rain.split('rain_op_py2')[0]+'rain_op_esc/rain_op_esc_%s'%include_escenarios

        codigos=[codefile]
        print ('WARNING: converting rain data, it may take a while ---- dt:%s'%(Dt))
    #         obj = get_radar_rain_OP(start,end,Dt,nc_basin,codigos,
    #                              meanrain_ALL=False,save_bin=True,
    #                              path_res=ruta_out_rain,
    #                              umbral=0.005,verbose=verbose,
    #                              evs_hist= evs_hist,complete_naninaccum = complete_naninaccum,
    #                              include_escenarios = include_escenarios)

        obj = get_radar_rain(start,end,Dt,path_ncbasin,codigos,rutaNC=get_ruta(ConfigList,'ruta_radardbz'),
                             meanrain_ALL=False,save_bin=True,
                             path_res=ruta_rain,
                             umbral=0.005,verbose=verbose,
                             complete_naninaccum = complete_naninaccum)

        obj = obj.loc[start:end]
    
    return obj, ruta_out_rain
#-----------------------------------
#-----------------------------------
#Funciones de ejecucion modelo
#-----------------------------------
#-----------------------------------

def get_executionlists_all4all(ConfigList,ruta_out_rain,cu,starts_m,end,windows,warming_steps=48,dateformat_starts = '%Y-%m-%d %H:%M'):
    
    # pars + ci's
    DicCI=get_ConfigLines(ConfigList,'-CIr','Paths')
    #pars by ci.
    DicPars = {}
    for name in list(DicCI.keys()):
        DicPars.update({'%s'%name:get_ConfigLines(ConfigList,'-par%s'%name,'Pars')})

    #rutas denpasos salida (configfile)
    ruta_StoOp = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_sto_op')
    ruta_QsimOp = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_qsim_op')
    ruta_QsimH = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_qsim_hist')
    ruta_MS_H = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_MS_hist')
    pm = wmf.read_mean_rain(ruta_out_rain.split('.')[0]+'.hdr')

    #Prepara las listas para setear las configuraciones
    ListEjecs = []

    for window,start_m in zip(windows,starts_m): 
        pos_start = pm.index.get_loc(start_m.strftime(dateformat_starts)) 
        npasos = int((end-start_m).total_seconds()/wmf.models.dt)
        STARTid = window #;print STARTid
        #CIs
        for CIid in np.sort(list(DicCI.keys())):
            with open(DicCI[CIid], 'r') as f:
                CI_dic = json.load(f)
            #pars
            for PARid in DicPars[CIid]:
                ListEjecs.append([cu, CIid, CI_dic, ruta_out_rain, PARid, DicPars[CIid][PARid], npasos, pos_start, STARTid, ruta_StoOp+PARid+CIid+'-'+STARTid, ruta_QsimOp+PARid+CIid+'-'+STARTid+'.csv', ruta_QsimH+PARid+CIid+'-'+STARTid+'.csv', ruta_MS_H+PARid+CIid+'-'+STARTid+'.csv',warming_steps])
        
    return ListEjecs

def get_executionlists_fromdf(ConfigList,ruta_out_rain,cu,starts_m,end,df_executionprops,
                              warming_steps=48,dateformat_starts = '%Y-%m-%d %H:%M',
                              path_pant4rules = None):
    #rutas denpasos salida (configfile)
    ruta_StoOp = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_sto_op')
    ruta_QsimOp = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_qsim_op')
    ruta_QsimH = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_qsim_hist')
    ruta_MS_H = get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_MS_hist')
    pm = wmf.read_mean_rain(ruta_out_rain.split('.')[0]+'.hdr')

    #Prepara las listas para setear las configuraciones
    ListEjecs = []

    for STARTid,start_m,CIpath,CIid,PARvar,PARid in zip(df_executionprops.start_names.values,starts_m,df_executionprops.CIs.values,df_executionprops.CI_names.values,df_executionprops.pars.values,df_executionprops.pars_names.values):

        #define inicio y npasos de simulacion
        pos_start = pm.index.get_loc(start_m.strftime(dateformat_starts)) 
        npasos = int((end-start_m).total_seconds()/float(wmf.models.dt))+1 # para que cuadren los pasos del index entre lluvia y qsim

        #define condiciones iniciales de ejecucion de acuerdo al tipo
        if CIpath == 0.0: #pone ci en ceros
            CIvar = [0]*5
        elif CIpath[-5:] == '.json': #si se la da la ruta de un .json lo lee
            with open(CIpath, 'r') as f:
                CIvar = json.load(f)
                CIvar = list(CIvar.values())        
        elif CIpath == 'reglas_pant' and path_pant4rules is not None: #si se asigna, lee escenarios r_rules
            #leer paths de CI.
            paths_reglaspant = np.sort(glob.glob(get_ruta(ConfigList,'ruta_proj')+get_ruta(ConfigList,'ruta_CI_reglaspant')+'*'))
            #lee la lluvia del t_ant que corresponde
            pant = wmf.read_mean_rain(path_pant4rules.split('.')[0]+'.hdr')
            tws_tanks = [pd.Timedelta(tw) for tw in ['11d','13d','21d','30d','17d']]
            pants_sum = [pant.loc[pant.index[-1]- tw_pant:pant.index[-1]].sum() for tw_pant in tws_tanks]
            #escoge CI para cada tanque en funcion de la lluvia : rain_CIrules.
            CIvar = []
            for index,pant_sum,path_ci in zip(np.arange(1,6),pants_sum,paths_reglaspant):
                df_tank = df_tank = pd.read_csv(path_ci,index_col=0)
                if index == 4: #t4, subte
                    CIvar.append(df_tank.loc[end.month][0]) # no se escoge por intervalos porque ndias nunca converge. por ahora, se toma la media del mes: cliclo anual.
                else:
                    pos_bin = np.searchsorted(df_tank.index,pant_sum) - 1
                    CIvar.append(df_tank.loc[df_tank.index[pos_bin]].P50)
        elif CIpath[-7:] == '.StOhdr': #si se asinga
            f=open(CIpath.split('.')[0]+'.StOhdr')
            filelines=f.readlines()
            f.close()
            IDs=np.array([int(i.split(',')[0]) for i in filelines[5:]])
            fechas=np.array([i.split(',')[-1].split(' ')[1] for i in filelines[5:]])
            #ultima pos
            v,r = wmf.models.read_float_basin_ncol(CIpath.split('.')[0]+'.StObin',IDs[-1], cu.ncells, 5)
            CIvar = v
        #Guarda listas de ejecucion
        ListEjecs.append([cu, CIid, CIvar, ruta_out_rain, PARid, PARvar, npasos, pos_start, STARTid, ruta_StoOp+PARid+'-'+CIid+'-'+STARTid, ruta_QsimOp+PARid+'-'+CIid+'-'+STARTid+'.csv', ruta_QsimH+PARid+'-'+CIid+'-'+STARTid+'.csv', ruta_MS_H+PARid+'-'+CIid+'-'+STARTid+'.csv',warming_steps])

    return ListEjecs

def get_qsim(ListEjecs,set_CI=True,save_hist=True,verbose = True):
    '''
    Nota: 
    - No esta guardando St0bin.
    - falta agregar la parte de guardar MS en las pos de las estaciones de humedad.
    '''
    for L in ListEjecs:
        #read nc_basin
        cu=L[0]
        #if assigned, set CI.
        if set_CI:
            cu.set_Storage(L[2][0], 0)
            cu.set_Storage(L[2][1], 1)
            cu.set_Storage(L[2][2], 2)
            cu.set_Storage(L[2][3], 3)
            cu.set_Storage(L[2][4], 4)
        
        #run model
        res = cu.run_shia(L[5],L[3],L[6],L[7],kinematicN=12,
                          ruta_storage=L[9], ) # se guardan condiciones para la sgte corrida.

        #save df_simresults
        #operational qsim - without warming steps
        df = res[1].loc[res[1].index[L[13]:]]
        df.to_csv(L[10])
        
#         print('start: %s, start_index_qsim: %s,start_pos: %s'%(L[7],res[1].index[L[13]:],L[13]))
        
        # saving historical data
        if save_hist == False:#se crea
            # qsim
            df.to_csv(L[11])
            # hs_sim
            df_hs = pd.read_csv(L[9].split('.')[0]+'.StOhdr', header = 4, index_col = 5, parse_dates = True, usecols=(1,2,3,4,5,6))
            df_hs.columns = ['t1','t2','t3','t4','t5']
            df_hs.index.name = 'fecha'
            df_hs.to_csv(L[12])
        else:#if save_hist == True: #s lo actualiza
            # qsim_hist
            df0 = pd.read_csv(L[11], index_col=0, parse_dates= True) #abre archivo hist ya creado (con una corrida guardada.)
            df0.index = pd.to_datetime(df0.index)
            df.index = pd.to_datetime(df.index)
            df.columns = list(map(str,df.columns))
            df0= df0.append(df)#se agrega corrida actual
            df0 = df0.reset_index().drop_duplicates(subset='index',keep='last').set_index('index')
            df0 = df0.dropna(how='all')
            df0 = df0.sort_index()
            df0.to_csv(L[11]) # se guarda archivo hist. actualizado
            
            # qsim_hist
            df_hs0 = pd.read_csv(L[12], index_col=0, parse_dates= True) #abre archivo hist ya creado (con una corrida guardada.)
            df_hs0.index = pd.to_datetime(df_hs0.index)
            df_hs = pd.read_csv(L[9].split('.')[0]+'.StOhdr', header = 4, index_col = 5, parse_dates = True, usecols=(1,2,3,4,5,6))#la nueva
            df_hs.columns = ['t1','t2','t3','t4','t5']
            df_hs.index.name = 'fecha'
            df_hs.index = pd.to_datetime(df_hs.index)
            df_hs.columns = list(map(str,df_hs.columns))
            df_hs0= df_hs0.append(df_hs)#se agrega corrida actual
            df_hs0 = df_hs0.reset_index().drop_duplicates(subset='fecha',keep='last').set_index('fecha')
            df_hs0 = df_hs0.dropna(how='all')
            df_hs0 = df_hs0.sort_index()
            df_hs0.to_csv(L[12]) # se guarda archivo hist. actualizado
        if verbose:
            print ('Config. '+L[4]+L[1]+'-'+L[-6]+' ejecutado')

    return res

#------------------------
#Funciones de despliegue
#------------------------

def n2q(level,a,b):
    Df_Q = a*(level**b)
    return Df_Q

def plot_Q(start,end,Dt,server,user,passwd,dbname,
           ListEjecs,cu,ests,colors_d,path_r,path_masks_csv,df_bd,df_est_features,ylims,rutafig=None):
     #qobs
#     levels=[]
#     for est in ests:
#         selfn = cprv1.Nivel(codigo=est, user='soraya', passwd='12345') 
#         level=selfn.level(start,end)
#         levels.append(level)
    #consulta
    res = hidrologia.nivel.consulta_nivel(list(map(str,ests)),start,end,server,user,passwd,dbname,
                                          retorna_niveles_riesgo=False)
    #cuadrar index y type
    levels = res.apply(pd.to_numeric, errors='coerce')
    levels.index = pd.to_datetime(levels.index)
    levels = levels[~levels.index.duplicated(keep='first')]
    rng = pd.date_range(levels.index[0],levels.index[-1],freq='1T')
    df_levels = levels.reindex(rng)
    #array-like
    levels = df_levels.T.values

    qs = []
    for est,l in zip(ests,levels):
        qs.append(n2q(l,df_est_features.loc[est].a,df_est_features.loc[est].b))


    df_qobs = pd.DataFrame(qs).T
    df_qobs.columns = ests; df_qobs.index = df_levels.index
    df_qobs = df_qobs.resample(Dt).mean()

    # PMEAN basins
    # abrir bin y records para recorrerlo
    pstruct = wmf.read_rain_struct(path_r)
    pstruct = pstruct.loc[start:end]#quitar el wupt
    df_pbasins = pd.DataFrame(index=pstruct.index,columns=ests)
    path_bin = path_r.split('.')[0]+'.bin'
    records = pstruct[' Record'].values

    df_posmasks = pd.read_csv(path_masks_csv, index_col=0)

    for index,record in zip(pstruct.index,records):
        v,r = wmf.models.read_int_basin(path_bin,record,cu.ncells)
        rvec = v/1000.

        mean = []
        #para todas

        for est in ests:
                if rvec == '': # si no hay nc en ese paso de tiempo.
                    mean.append(np.nan)
                else:
                    mean.append(np.sum(rvec*df_posmasks['%s'%est])/float(df_posmasks['%s'%est][df_posmasks['%s'%est]==1].size))
        # se actualiza la media de todas las mascaras en el df.
        df_pbasins.loc[index]=mean         

    #graficas
    for ylim,est in zip(ylims[:],ests[:]):
        #grafica
        fig=pl.figure(dpi=90)
        ax=fig.add_subplot(111)
        df_qobs[est].plot(ax=ax,c='k',lw=3,label='Qobs')
        ax.set_ylabel(u'Caudal (m³/s)',fontsize=16)
        ax.set_ylim(0,ylim)
        pl.locator_params(axis='y', nbins=4)
    #     qsim pars
        for color,l_ej in zip(colors_d,ListEjecs):
            #qsim
            qsim = pd.read_csv(l_ej[-4], index_col=0, parse_dates= True)
            df_qsim = qsim[df_est_features.tramo]
            df_qsim.columns = ests

            df2kge= pd.DataFrame([df_qobs[est].values,df_qsim[est].values],index=['obs','sim']).T
            nse = wmf.__eval_nash__(df2kge.obs.values,df2kge.sim.values)
            kge = hydroeval.kge(df2kge.dropna().sim.values,df2kge.dropna().obs.values)[0][0]
#             corrsp = scp.stats.spearmanr(df2kge.dropna().sim.values,df2kge.dropna().obs.values)[0]
            ax = df_qsim[est].plot(c=color,lw=1.75,label='Qsim_%s%s \nNSE: %s \nKGE: %s'%(l_ej[1],l_ej[4],round(nse,2),round(kge,2)))#0.2,0.5))

        ax2=ax.twinx()
        df_pbasins[est].plot.area(ax=ax2,color=['#164cc8'],alpha=0.2,lw=1)
        ax2.set_ylim(12*3,0)
        ax2.set_ylabel(u'Precipitación (mm/h)',fontsize=16)
        legend = ax.legend(loc=(1.15,-0.01), fontsize=13.15)
        ax.set_title('Est %s | %s'%(est,df_bd.loc[est].nombreestacion), fontsize=17.5)
        pl.locator_params(axis='y', nbins=4)

        if rutafig is not None:
            fig.savefig(rutafig+'qsim_%s.png'%(est),dpi=100,
                    bbox_extra_artists=(legend,),bbox_inches='tight')
            
            