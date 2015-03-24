#!/usr/bin/python

import os
import hashlib
import sys
import optparse
import dbm
import time
from select import select
from gamin import WatchMonitor, GAMChanged

def proc_opts(): 
	usage = "USO: sysinteger.py [-h] [-f] directorio"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-d", "--dir", dest='directorio', default="./", help=u'opcion para indicar en que BD guardar los hashes de los ficheros. Por defecto ./hashes.db', metavar="FILE")
	comlist.add_option("-f", "--file", dest='hashfile', default="hashes", help=u'opcion para indicar en que BD guardar los hashes de los ficheros. Por defecto ./hashes.db', metavar="FILE")

	return comlist.parse_args(sys.argv)


def funcHash(fichero):
	f=open(fichero,"r")
	sumaC= hashlib.sha224(f.read()).hexdigest()
	f.close()
	return sumaC

def listaRutaFicheros(ruta):
	listaR=[]
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		for fichero in nombreFichs:
			rutaTotal = os.path.join (rutaDir, fichero)
			listaR.append(rutaTotal)
	return listaR

def preparaInt(ruta):
	d=dbm.open(opts.hashfile,"n")
	for fichero in listaRutaFicheros(ruta):	
		d[fichero]=funcHash(fichero)
	d.close()

#INICIO DEL PROGRAMA
opts, args = proc_opts() 

preparaInt(opts.directorio)
d=dbm.open(opts.hashfile,"r")

def monitor(fichero, event):
	if event == GAMChanged:
		if d.has_key(os.path.join(opts.directorio,fichero)):
			if d[os.path.join(opts.directorio,fichero)] != funcHash(os.path.join(opts.directorio,fichero)):
				print "Ha cambiado el contenido de "+fichero+" el "+time.strftime("%d/%b/%Y - %H:%M:%S")
		else:
			None
	return True
  		
if __name__ == "__main__":
	mon = WatchMonitor()
	mon.watch_directory(opts.directorio, monitor)
	time.sleep(1)
	fd = mon.get_fd()
	while True:
		select([fd],[],[])
		if mon.event_pending():
			mon.handle_events() 
	mon.stop_watch(fichero)
	del mon





