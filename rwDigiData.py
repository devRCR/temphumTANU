import time, os
import pandas as pd
import numpy as np
from datetime import datetime
from digi.xbee.devices import XBeeDevice

remoteNodes = []
labID = ['0013A200414E5F9E','0013A200414E5FA7','0013A200414E6030']
labName = ['Lab18','Lab19','Lab31'] 
parameters= ['temp','hum']
count = 0
# Creando variables Auxiliares
auxIndex = 0
auxPayload = "200/500"
auxData = [20.0,50.0]

xbee = XBeeDevice("/dev/ttyUSB0",9600)
xbee.open()
prevTime = time.time()

while(True):
    xbee_message = xbee.read_data()

    # Cada 5 minutos calculamos el promedio y desviación estandar de los datos almacenados
    if (time.time()-prevTime > 30):
        prevTime = time.time() # actualizamos el tiempo previo
        for n in remoteNodes:
            dTemp = {'Temp': locals()['temp'+n]}
            dHum = {'Hum': locals()['hum'+n]}

            dfTemp = pd.DataFrame(dTemp)
            mean_dfTemp = dfTemp.mean().round(2)
            std_dfTemp = dfTemp.std().round(2)

            dfHum = pd.DataFrame(dHum)
            mean_dfHum = dfHum.mean().round(2)
            std_dfHum = dfHum.std().round(2)
                       
            timestamp = time.time()
            print(n, mean_dfTemp[0],std_dfTemp[0],len(dfTemp),mean_dfHum[0],std_dfHum[0],len(dfHum),datetime.now().strftime("%d%m%Y %H:%M:%S"))

            filename = datetime.now().strftime("%d%m%Y")

            # Vaciar los arrays
            locals()['temp'+n] = []
            locals()['hum'+n] = []

            # Guardamos los datos en ficheros tipo txt 
            with open('/home/lde/Share/'+n+'/'+str(datetime.now().month)+'/'+filename+'.txt','a') as f:
                f.write(str(mean_dfTemp[0])+","+str(std_dfTemp[0])+","+str(len(dfTemp))+","+str(mean_dfHum[0])+","+str(std_dfHum[0])+","+str(len(dfHum))+","+datetime.now().strftime("%H:%M:%S")+"\r\n")    
        remoteNodes = []    
    else:
        if xbee_message != None:
            remoteID = str(xbee_message.remote_device.get_64bit_addr())
            
            for n in labID:
                if remoteID==n:
                    print("El dato viene del %s",n)
                               
            if len(remoteNodes) == 0:
                remoteNodes.append(remoteID)
                locals()['temp'+remoteID] = []
                locals()['hum'+remoteID] = []
            else:
                for i in remoteNodes:
                    if (remoteID  == i):
                        count = count + 1
                        #auxIndex = remoteNodes.index(i)
                if (count == 0):
                    remoteNodes.append(remoteID)
                    locals()['temp'+remoteID] = []
                    locals()['hum'+remoteID] = []
                    #auxIndex = remoteNodes.index(i) + 1
                else:
                    count = 0
            try:
                payload = xbee_message.data.decode("utf8")  
                #print(payload+' '+remoteID)    
            except UnicodeDecodeError:
                #payload = auxPayload
                print ('utf-8 codec can not decode data'+remoteID)           
            #print(payload)
            try: 
                dataSensor = payload.split("/")
            except :
                print('An error has been caught')
                #dataSensor = auxData    
                     
            try:
                for x in range(len(dataSensor)):
                    dataSensor[x] = int(dataSensor[x])/10
                    locals()[parameters[x]+remoteID].append(dataSensor[x])
            except ValueError:
                print ('Invalid literal for int() with base 10: '+dataSensor[x])
            
            # Actualizando el valor de las variables auxiliares en caso de error
            auxPayload = payload
            auxData = dataSensor
            
            
            
            # creamos las carpetas para cada Nodo           
            if not os.path.exists('/home/lde/Share/'+remoteID):
                os.mkdir('/home/lde/Share/'+remoteID) # Creamos la carpeta para un nodo nuevo
            else:
                None
            # creamos la carpeta del mes de medición, dentro de la carpeta de cada Nodo          
            if not os.path.exists('/home/lde/Share/'+remoteID+'/'+str(datetime.now().month)):
                os.mkdir('/home/lde/Share/'+remoteID+'/'+str(datetime.now().month))
                #print("Directory ", remoteID, " created")
            else:
                None

        
