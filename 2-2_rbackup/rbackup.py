#!/usr/bin/python

import os
import hashlib
import sys
import optparse
import urllib
import socket


def proc_opts(): 
	usage = "USO: rbackup.py [-h |-rd] camino al archivo o directorio"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-r", "--recursivo", action='store_true', default=False, help=u'funciona recursivamente')
	comlist.add_option("-d", "--borrar", action='store_true', default=False, help=u'borra los archivos en el servidor que no estan en el cliente')

	return comlist.parse_args(sys.argv)

#Funcion que recibe la ruta absoluta o relativa de un fichero y devuelve el
#hash en hexadecimal con el metodo md5
def funcHash(rutaFichero):
	f=open(rutaFichero,"r")
	sumaC= hashlib.md5(f.read()).hexdigest()
	f.close()

	return sumaC

#Funcion que recibe la ruta absoluta o relativa de un directorio y devuelve 
#una lista con todos los ficheros incluidos en el, incluido dentro subdirect.

def listaFicheros(ruta):
	listaR=[]
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		for fichero in nombreFichs:
			rutaTotal = os.path.join (rutaDir, fichero)
			listaR.append(rutaTotal)
	return listaR



#INICIO DEL PROGRAMA
if __name__ == "__main__":
	opts, args = proc_opts() 
	if os.path.isdir(args[1]):
		if opts.recursivo:
			for fich in listaFicheros(args[1]):
				fichero = os.path.abspath(fich)
				suma = funcHash(fichero)
				f=urllib.urlopen("http://localhost:8000/%s" % args[1]+"/"+os.path.basename(fich)+"//"+suma+"//"+"False")
				print "Codigo respuesta del Servidor: %s %s" % (f.getcode(), f.read())
				if f.getcode() == 206 or f.getcode() == 404:
					f = urllib.urlopen("http://localhost:8000/"+args[1]+os.path.basename(fich),open(os.path.abspath(fich),"rb").read())
			if opts.borrar:
				f=urllib.urlopen("http://localhost:8000/%s" % args[1]+"/"+os.path.basename(fich)+"//"+suma+"//"+str(opts.borrar))
				print "Codigo respuesta del Servidor: %s %s" % (f.getcode(), f.read())
				
		else:
			for fich in os.listdir(args[1]):
				fichero = os.path.abspath(os.path.join(args[1], fich))
				if os.path.isfile(fichero):
					suma = funcHash(fichero)
					f=urllib.urlopen("http://localhost:8000/%s" % args[1]+"/"+fich+"//"+suma+"//"+"False")
					print "Codigo respuesta del Servidor: %s %s" % (f.getcode(), f.read())	
					if f.getcode()==206 or f.getcode()==404:
						f = urllib.urlopen("http://localhost:8000/"+args[1]+os.path.basename(fichero),open(os.path.abspath(fichero),"rb").read())
			if opts.borrar:
				f=urllib.urlopen("http://localhost:8000/%s" % args[1]+"/"+fich+"//"+suma+"//"+str(opts.borrar))
				print "Codigo respuesta del Servidor: %s %s" % (f.getcode(), f.read())
	else:
		fichero = os.path.abspath(args[1])
		suma = funcHash(args[1])
		f=urllib.urlopen("http://localhost:8000/%s" % args[1]+"//"+suma+"//"+str(opts.borrar))
		print "Codigo respuesta del Servidor: %s %s" % (f.getcode(), f.read())
		if f.getcode()==206 or f.getcode()==404:
			f = urllib.urlopen("http://localhost:8000/",open(args[1],"rb").read())
	f.close()


