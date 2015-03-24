from multiprocessing import Process
import multiprocessing 
import Queue
import os, time, sys
import hashlib
import optparse

def proc_opts(): 
	usage = "USO: hashes-hilos.py [-h] directorio"
	comlist = optparse.OptionParser(usage=usage)

	return comlist.parse_args(sys.argv)

def info(title):
	print title
	print 'Nombre del Script:', __name__
	print 'Proceso padre:', os.getppid()
	print 'Proceso hijo:', os.getpid()    

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

def f(cola):
	while True:
		try:
			fich = q.get(False)				
		except Queue.Empty:
			print "Fin"
			break
		print fich+": "+funcHash(fich)
		time.sleep(1)

if __name__ == '__main__':
	opts, args = proc_opts() 
	q = multiprocessing.Queue()

	for i in listaRutaFicheros(args[1]):
		q.put(i)

	#Creo una lista vacia y la voy rellenando de procesos
	l=[]	
	for i in range(5):
		l.append(Process(target=f, args=(q,)))

	#Lanzo todos los procesos
	for t in l:
		t.start()
		info('Linea Principal')

	#Los espero luego a todos
	for t in l:	
		t.join()


