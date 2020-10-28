# from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
# from qgis.PyQt.QtGui import QIcon
# from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *

from qgis.PyQt import *
from qgis.core import *
import requests
import numpy as np
import multiprocessing

# from PyQt5.QtWidgets import QAction, QMessageBox,QFileDialog
# from qgis.core import (QgsCoordinateReferenceSystem,
#                        QgsCoordinateTransform,
#                        QgsProject,
#                        QgsRectangle,
#                        QgsPointXY,
#                        QgsGeometry,
#                        QgsVectorLayer,
#                        QgsFeature,
#                        QgsMessageLog)
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .SAR_Tools_dialog import MRSLabDialog
import os.path
from osgeo import gdal
import time
import os.path


class DpRVI(QtCore.QObject):
    '''DpRVI '''
    def __init__(self,iFolder,T3,ws):
        QtCore.QObject.__init__(self)

        self.iFolder = iFolder
        self.T3 = T3
        self.ws=ws
        self.killed = False
        # self.mainObj = MRSLab()
    def run(self):
        finish_cond = 0
        try:
            def NM3CF_fn(T3_stack,ws):
        
                t11_T1 = T3_stack[:,:,0]
                t12_T1 = T3_stack[:,:,1]
                t13_T1 = T3_stack[:,:,2]
                t21_T1 = T3_stack[:,:,3]
                t22_T1 = T3_stack[:,:,4]
                t23_T1 = T3_stack[:,:,5]
                t31_T1 = T3_stack[:,:,6]
                t32_T1 = T3_stack[:,:,7]
                t33_T1 = T3_stack[:,:,8]
                
                nrows  = np.shape(T3_stack)[1]
                ncols = np.shape(T3_stack)[0]
                # nrows  = 100
                # ncols = 100
               
                theta_FP = np.zeros((ncols,nrows))
                Pd_FP = np.zeros((ncols,nrows))
                Pv_FP = np.zeros((ncols,nrows))
                Ps_FP = np.zeros((ncols,nrows))
                
                # D = (1/np.sqrt(2))*np.array([[1,0,1], [1,0,-1],[0,np.sqrt(2),0]])
                # %% for window processing
                wsi=wsj=ws
                
                inci=int(np.fix(wsi/2)) # Up & down movement margin from the central row
                incj=int(np.fix(wsj/2)) # Left & right movement from the central column
                # % Starting row and column fixed by the size of the patch extracted from the image of 21/10/1999
                
                starti=int(np.fix(wsi/2)) # Starting row for window processing
                startj=int(np.fix(wsj/2)) # Starting column for window processing
                
                stopi= int(nrows-inci)-1 # Stop row for window processing
                stopj= int(ncols-incj)-1 # Stop column for window processing
                        # %% Elementary targets
                             
                for ii in np.arange(startj,stopj+1):
        
                    # self.progress.emit(str(ii)+'/'+str(nrows))
                    self.pBar.emit(int((ii/ncols)*100))
                    for jj in np.arange(starti,stopi+1):
                
                        t11s = np.nanmean(t11_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        t12s = np.nanmean(t12_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        t13s = np.nanmean(t13_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        
                        t21s = np.nanmean(t21_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        t22s = np.nanmean(t22_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        t23s = np.nanmean(t23_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        
                        t31s = np.nanmean(t31_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        t32s = np.nanmean(t32_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                        t33s = np.nanmean(t33_T1[ii-inci:ii+inci+1,jj-incj:jj+incj+1])#i sample
                
                        T_T1 = np.array([[t11s, t12s, t13s], [t21s, t22s, t23s], [t31s, t32s, t33s]])
                        
                        m1 = np.real(np.sqrt(1-(27*(np.linalg.det(T_T1)/(np.trace(T_T1)**3)))))
                        h = (t11s - t22s - t33s)
                        g = (t22s + t33s)
                        span = t11s + t22s + t33s
                        val = (m1*span*h)/(t11s*g+m1**2*span**2);
                        thet = np.real(np.arctan(val))
                        # thet = np.rad2deg(thet)
                        theta_FP[ii,jj] = np.rad2deg(thet)
                        Ps_FP[ii,jj] = (((m1*(span)*(1+np.sin(2*thet))/2)))
                        Pd_FP[ii,jj] = (((m1*(span)*(1-np.sin(2*thet))/2)))
                        Pv_FP[ii,jj] = (span*(1-m1))
                        
                
                # # %% GRVI
                # f[f==0]=np.NaN
                # vi = np.power(beta, GD_t1_rv)*(1 - (1/f)*GD_t1_rv);
                
                # x1 = np.power(beta, GD_t1_rv);
                # x2 = (1 - GD_t1_rv);
                
                # f =  np.nan_to_num(f)
                # idx1 = np.argwhere(GD_t1_rv>f)
                # vi[idx1] = 0;
                # vi[~idx1] = vi[~idx1];
                
                # # %% RVI scaled (0 - 1)
                
                # rvi = temp_rvi;
                
                # idx = np.argwhere(rvi>1)
                
                # rvi[idx] = (3/4)*rvi[idx];
                # rvi[~idx] = rvi[~idx];
                # rvi[rvi==0] = np.NaN
                
                """Write files to disk"""
                # ofilervi = self.iFolder+'/RVI.bin'
                infile = self.iFolder+'/T11.bin'
                # write_bin(ofilervi,rvi,infile)
                ofilegrvi = self.iFolder+'/Theta_FP.bin'
                write_bin(ofilegrvi,theta_FP,infile)
                ofilegrvi1 = self.iFolder+'/Pd_FP.bin'
                write_bin(ofilegrvi1,Pd_FP,infile)
                ofilegrvi2 = self.iFolder+'/Ps_FP.bin'
                write_bin(ofilegrvi2,Ps_FP,infile)
                ofilegrvi3 = self.iFolder+'/Pv_FP.bin'
                write_bin(ofilegrvi3,Pv_FP,infile)     
                self.pBar.emit(100)
                self.progress.emit('>>> Finished NM3CF calculation!!')
                # self.pBar.emit(0)
                # self.iface.addRasterLayer(self.inFolder+'\RVI.bin')
                # self.iface.addRasterLayer(self.inFolder+'\GRVI.bin')
                # return rvi,vi 
            
            
            
            
            def dop_fp(T3):
        
                DOP = np.zeros([np.size(T3,0),np.size(T3,1)])
                for i in range(np.size(T3,0)):
                    # self.progress.emit('Processed column '+str(i))
                    # stdout.write("\r[%.2f/%d] DOP" % ((i/np.size(T3,0))*100, 100)) 
                    # self.progress.emit(str(i))
                    self.pBar.emit((i/np.size(T3,0))*100)
                    for j in range(np.size(T3,1)):
                        det = np.abs(np.linalg.det(T3[i,j,:].reshape((3, 3))))
                        trace = np.abs(np.trace(T3[i,j,:].reshape((3, 3))))
                        if trace==0:
                            DOP[i][j]=0
                        # elif((27*det/trace**3)>1.0):
                        #     DOP[i][j]=0
                        else:
                            DOP[i][j] = np.sqrt(1-((27*det)/trace**3))
                            # print(DOP[i][j])
                    # stdout.flush()# clear the screen
                        #%%
                # self.progress.connect(self.showmsg)
                dop=DOP
                fname = 'DOP.bin'
                # f1= open(folder+'/'+fname, 'wb')
                # f1.write(bytearray(dop))
                # f1.close()
                dop.astype('float32').tofile(self.inFolder+'/'+fname)
                f2= open(self.inFolder+'/'+fname+'.hdr', 'w')
                header = ["ENVI\n",\
                          "description = {\n",\
                          " File Imported into ENVI.}\n",\
                          "samples = %d\n"%np.size(dop,1),\
                          "lines   = %d\n"%np.size(dop,0),\
                          "bands   = 1\n",\
                          "header offset = 0\n",\
                          "file type = ENVI Standard\n",\
                          "data type = 4\n",\
                          "interleave = bsq\n",\
                          "sensor type = Unknown\n",\
                          "byte order = 0\n",\
                          "wavelength units = Unknown\n"]
                f2.writelines(header)
                f2.close()
                # self.iface.addRasterLayer(self.inFolder+'\DOP.bin')
                self.progress.emit('Finished DOP calculation!!')
            # return DOP
                
            def read_bin(file):
            
                # data, geodata=load_data(file_name, gdal_driver='GTiff')
                ds = gdal.Open(file)
                band = ds.GetRasterBand(1)
                arr = band.ReadAsArray()
                # [cols, rows] = arr.shape
                return arr
            
            def write_bin(file,wdata,refData):
                
                ds = gdal.Open(refData)
                [cols, rows] = wdata.shape
            
                driver = gdal.GetDriverByName("ENVI")
                outdata = driver.Create(file, rows, cols, 1, gdal.GDT_Float32)
                outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
                outdata.SetProjection(ds.GetProjection())##sets same projection as input
                
                outdata.SetDescription(file)
                outdata.GetRasterBand(1).WriteArray(wdata)
                # outdata.GetRasterBand(1).SetNoDataValue(np.NaN)##if you want these values transparent
                outdata.FlushCache() ##saves to disk!!    
        
            # self.dop_fp(self.T3)
            NM3CF_fn(self.T3,self.ws)
            
            finish_cond = 1
            
        
        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
            
        self.finished.emit(finish_cond)
        
    # def kill(self):
    #     self.killed = True
        

        
    """***************************************"""
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception, str)
    progress = QtCore.pyqtSignal(str)     
    pBar =  QtCore.pyqtSignal(int)             