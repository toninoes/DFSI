#!/usr/bin/python

#Script que realiza la vigilancia de un directorio recursivamente, o un fichero
#Toma como argumento la ruta absoluta del directorio o fichero solamente
#El script se carga en segundo plano a modo de demonio y escribira en el
#fichero especificado en -f log los cambios producidos en el fichero o bien
#en el directorio. Tambien indica si se ha agregado algun fichero nuevo al
#directorio.
#Para parar el script teclear en una terminal pkill cambios.py

import sys, os, time
import hashlib, optparse


def proc_opts(): 
	usage = "USO: cambios.py [-h] [-f fichero] fichero | directorio"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-f", "--file", dest='hashfile', default="cambios.log", help=u'opcion para indicar donde guardar los cambio de los ficheros. Por defecto ./cambios.log', metavar="FILE")

	return comlist.parse_args(sys.argv)

#Lo primero es hacer fork(). AL hacer esto se crea una copia del proceso que
#se esta ejecutando dicha copia es el proceso hijo y el original es el padre.
#Cuando se crea el hijo, el padre puede salir
#El codigo de retorno de la llamada a fork() devuelve 0 en el hijo y el id
#del proceso en el padre.
#Por tanto solo el padre tendra un codigo diferente a 0 y sera el que termine.
#para ver el proceso en segundo plano teclear 'ps aux | grep -E cambios.py' en
#la terminal.

try:
	pid=os.fork()
	if pid > 0:
		sys.exit(0)
except:
	sys.exit(1)

def funcHash(fichero):
	f=open(fichero,"r")
	sumaC= hashlib.md5(f.read()).hexdigest()
	f.close()
	return sumaC

def listaRutaFicheros(ruta):
	listaR=[]
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		for fichero in nombreFichs:
			rutaTotal = os.path.join (rutaDir, fichero)
			listaR.append(rutaTotal)
	return listaR

def listaFicheros(ruta):
	listaF=[]
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		for fichero in nombreFichs:
			listaF.append(fichero)
	return listaF

def listaDirectorios(ruta):
	listaD=[]
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		for directorio in nombreDirs:
			listaD.append(directorio)
	return listaD

def vigilaFile(ruta, fich):
	suma1=funcHash(ruta)
	g=open(fich,"a+")
	while True:
		time.sleep(5)
		suma2=funcHash(ruta)
		if suma1 != suma2:
			x = "El fichero "+ruta+" ha cambiado el "
			y = time.strftime("%d de %b del %Y a las %H:%M:%S\n")
			g.write (x+y)
			g.close()	
			g=open(fich,"a+")	
			suma1=funcHash(ruta)

def vigilaDir(ruta, fich):
	d={}
	for fichero in listaRutaFicheros(ruta):
		d[fichero]=funcHash(fichero)
	g=open(fich,"a+")
	while True:
		time.sleep(5)
		for fichero in listaRutaFicheros(ruta):
			if d.has_key(fichero):			
				if d[fichero]!=funcHash(fichero):
					x = "Mod "+fichero+"\n"
					y = time.strftime("%d/%b/%Y %H:%M:%S ")
					g.write (y+x)
					g.close()		
					g=open(fich,"a+")	
					d[fichero]=funcHash(os.path.join(fichero))
			else:		
					d[fichero]=funcHash(fichero)
					x = "Add "+fichero+"\n"
					y = time.strftime("%d/%b/%Y %H:%M:%S ")
					g.write (y+x)
					g.close()		
					g=open(fich,"a+")

#INICIO DEL PROGRAMA
opts, args = proc_opts() 

if len(args) > 1:
	if os.path.isdir(args[1]):
		vigilaDir(args[1], opts.hashfile)
	elif os.path.isfile(args[1]):
		vigilaFile(args[1], opts.hashfile)
	elif not os.path.exists(args[1]):
		print "ERROR: La ruta indicada no existe"
else:
	print "Debe escribir al menos un argumento"
	sys.exit(1)
