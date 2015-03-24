#!/usr/bin/python

import os
import hashlib
import sys
import optparse


def proc_opts(): 
	usage = "USO: sysinteger.py [-h] | [-r] (-C | -P) directorio"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-r", "--recursivo", action='store_true', default=False, help=u'funciona recursivamente')
	comlist.add_option("-C", "--comprueba", action='store_true', default=False, help=u'comprueba la integridad de todos los ficheros del directorio (accion por defecto, si no se indica ninguna).Los cambios detectados se muestran por la salida estandar de errores.')
	comlist.add_option("-P", "--prepara", action='store_true', default=False, help=u'prepara la comprobacion de integridad de todos los ficheros del directorio')
	comlist.add_option("-f", "--file", dest='hashfile', default="hash.log", help=u'opcion para indicar en que fichero guardar los hashes de los ficheros. Por defecto ./hash.log', metavar="FILE")

	return comlist.parse_args(sys.argv)

#Funcion que recibe la ruta absoluta o relativa de un fichero y devuelve el
#hash en hexadecimal con el metodo sha224
def funcHash(fichero):
	f=open(fichero,"r")
	sumaC= hashlib.sha224(f.read()).hexdigest()
	f.close()
	return sumaC

#Funcion que recibe la ruta absoluta o relativa de un directorio y devuelve 
#una lista con todos los ficheros incluidos en el, incluido dentro subdirect.
#precedido de la ruta absoluta del fichero
def listaRutaFicheros(ruta):
	listaR=[]
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		for fichero in nombreFichs:
			rutaTotal = os.path.join (rutaDir, fichero)
			listaR.append(rutaTotal)
	return listaR

#Funcion que recibe una ruta absoluta o relativa de un directorio y crea un
#fichero que contiene en cada linea el nombre (con su ruta) de un fichero
#mas su correspondiente hash. Incluye tambien los ficheros de los subdirect.
#si la opcion -r esta activa.
def preparaInt(ruta, rec):
	f=open(opts.hashfile,"w")

	if rec:
		for fichero in listaRutaFicheros(ruta):
			suma=funcHash(fichero)
			f.write("\""+fichero+"\""+" "+suma+"\n")	
	
	else:
		for fichero in os.listdir(ruta):
			rutaFichero=os.path.join(ruta,fichero)
			if os.path.isfile(rutaFichero):
				suma=funcHash(rutaFichero)
				f.write("\""+rutaFichero+"\""+" "+suma+"\n")
	f.close()

#Funcion que recibe una ruta absoluta o relativa de un directorio y comprueba
#que los ficheros incluidos en el tienen el mismo hash que los mismos ficheros
#cuando se creo el fichero con la opcion -P. Comprobara tambien los ficheros
#incluidos en su subdirectorios si la opcion -r esta activa.
def vigilaDir(ruta, rec):	
	try:
		f=open(opts.hashfile,"r")
	except:
		print "Aun ningun estado integro con el cual comprobar"
		sys.exit(1)
	
	DiccInt={}
	for linea in f.readlines():
		DiccInt[linea.split('"')[1]] = linea.split()[-1]
	
	if rec:
		print "Comprobacion Recursiva de "+ruta	
		for fichero in listaRutaFicheros(ruta):
			if DiccInt.has_key(fichero):
				if DiccInt[fichero] != funcHash(fichero):
					sys.stderr.write("El contenido de "+fichero+" ha sufrido cambios desde el ultimo estado integro\n")
			else:
				print "No existe un estado integro previo de "+fichero
	else:
		print "Comprobacion NO Recursiva de "+ruta	
		for fichero in os.listdir(ruta):
			rutaFichero=os.path.join(ruta,fichero)
			if os.path.isfile(rutaFichero):
				if DiccInt.has_key(rutaFichero):
					if DiccInt[rutaFichero] != funcHash(rutaFichero):
						sys.stderr.write("El contenido de "+rutaFichero+" ha sufrido cambios desde el ultimo estado integro\n")
				else:
					print "No existe un estado integro previo de "+rutaFichero

#INICIO DEL PROGRAMA
opts, args = proc_opts() 

#Aqui compruebo que no este -P y -C juntas
if opts.comprueba and opts.prepara:
	print "Las opciones -P y -C son incompatibles"
	sys.exit(1)
#Aqui controlo que si no esta activa ni -C ni -P, pues activo -C que es la que
#se hace por defecto
if not opts.comprueba and not opts.prepara:
	opts.comprueba=True

#Dependiendo de las opciones Preparo la comprobacion de integridad de los
#ficheros o compruebo dicha integridad. Tambien segun este activado -r lo 
#hago con o sin recursividad
if opts.comprueba: 
	if opts.recursivo:
		vigilaDir(args[1], True)
	else:
		vigilaDir(args[1], False)
elif opts.prepara:
	if opts.recursivo:
		preparaInt(args[1], True)
	else:
		preparaInt(args[1], False)

