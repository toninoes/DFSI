import threading, Queue
import hashlib
import os, sys, time
import optparse

def proc_opts(): 
	usage = "USO: hashes-hilos.py [-h] directorio"
	comlist = optparse.OptionParser(usage=usage)

	return comlist.parse_args(sys.argv)

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



class MiThread(threading.Thread):

	def __init__(self, q):
		self.q = q
		threading.Thread.__init__(self)

	def run(self):
		while True:
			try:
				fich = q.get(False)				
			except Queue.Empty:
				print "Fin"
				break
			print fich+": "+funcHash(fich)
			time.sleep(1)
			


#INICIO DEL PROGRAMA
opts, args = proc_opts() 

q = Queue.Queue()

for i in listaRutaFicheros(args[1]):
	q.put(i)

#Creo una lista vacia y la voy rellenando de hilos
l=[]
for i in range(5):
	l.append(MiThread(q))

#Lanzo todos los hilos
for t in l:	
	t.start()

#Los espero luego a todos
for t in l:	
	t.join()


