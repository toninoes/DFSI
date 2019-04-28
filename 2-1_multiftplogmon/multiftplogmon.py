#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import os
import sys
import time
import Queue
import optparse
import pyinotify
import threading 
import multiprocessing

def proc_opts(): 
	usage = "uso: %prog [opciones]"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-v", "--completo", action='store_true', default=True, help=u'muestra los registros(lineas) completos. Es el comportamiento por defecto.')
	comlist.add_option("-q", "--filtrables", action='store_true', default=False, help=u'muestra unicamente los campos filtrables de los registros')
	comlist.add_option("-f", "--fich", help=u'filtra los registros que coincidan total o parcialmente con el nombre del fichero', metavar="STRING")
	comlist.add_option("-u", "--usuario", help=u'filtra los registros que coincidan total o parcialmente con el usuario indicado', metavar="STRING")
	comlist.add_option("-r", "--host", help=u'filtra los registros que coincidan total o parcialmente con el host indicado.	(Observación: para forzar una dirección, se debe usar $ ;ej. 192.168.1.1$ para excluir 192.168.1X[X])', metavar="STRING")
	comlist.add_option("-H", "--hour", help=u'filtra los registros que coincidan con la hora indicada', metavar="HH")
	comlist.add_option("-d", "--day", help=u'filtra los registros que coincidan con el dia indicado', metavar="DD")
	comlist.add_option("-m", "--month", help=u'filtra los registros que coincidan con el mes indicado', metavar="MM")
	comlist.add_option("-y", "--year", help=u'filtra los registros que coincidan con el anyo indicado', metavar="AAAA")	
	comlist.add_option("-L", "--LOGS", dest='dirLogs', default="logs_ftp", help=u'directorio donde se ubican los logs. Por defecto el actual', metavar="FILE")
	comlist.add_option("-n", "--numero", type="int", default=4, help=u'numero de hilos procesos ha lanzar. Por defecto 4', metavar="Entero")
	comlist.add_option("-p", "--procesos", action='store_true', default=False, help=u'Utiliza procesos, por defecto hilos')
	return comlist.parse_args(sys.argv)

#######################################################################################
# Función que crea y devuelve un diccionario por cada linea de log recibida:
#  -Clave: bien 'hour', 'day', 'host',...
#  -Valor: El correspondiente al encontrado en la posición de esa linea.
#######################################################################################

def logfields(l):	
	fecha = time.strptime(l[:24], "%a %b %d %H:%M:%S %Y")
	dfields = {}
	dfields['hour'] = time.strftime("%H", fecha)
	dfields['day'] = time.strftime("%d", fecha)
	dfields['month'] = time.strftime("%m", fecha)
	dfields['year'] = time.strftime("%Y", fecha)
	dfields['host'] = l.split()[6]
	dfields['usuario'] = l.split()[-5]
	dfields['fich'] = l.split()[8]
	
	return dfields 	

#######################################################################################
# Función que compara 2 dicci., uno creado con las opciones del usuario (dfilters)
# y que se crea más abajo del código y otro diccionario que se acaba de crear
# arriba y que se crea segun el contenido de la cada linea del log. Devolverá True
# si todos las opciones del usuario se encuentran en esa linea. Y False si al menos
# una de esas opciones no se encuentra en esa linea.
#######################################################################################

def logfilter(dfields, dfilters):
	for e in dfilters: 
		if dfilters[e] not in dfields[e]:
			return False

	return True			

#######################################################################################
# Defino la clase MiHilo, la cual hereda de la clase Thread, su misión es cojer de
# la cola (si hay algo) y quedarse con una lista, la cual contendra las últimas lineas
# que se han generado en el log ftp, a las cuales posteriormente les aplicará los
# correspondientes filtros. Cada vez que imprima algo por la salida de errores dirá
# además que hilo se ha encargado de ello.
# El diccionario (dicc) contiene:
#  -Clave: nombre y ruta absoluta de un fichero
#  -Valor: Objeto fichero abierto y con el puntero situado en la ultima posición de
#		   lectura realizada.
#######################################################################################

class MiHilo(threading.Thread):
	def __init__(self, q, dicc):
		self.q = q
		self.dicc = dicc
		threading.Thread.__init__(self)

	def run(self):
		while True:
			try:
				fichero = q.get()
				ultimasL = dicc[fichero].readlines()
				for l in ultimasL:
					dfields = logfields(l)
					if logfilter(dfields, dfilters):
						if opts.filtrables:
							sys.stderr.write(self.getName()+": "+l[:24]+" "+l.split()[6]+" "+l.split()[8]+" "+l.split()[13]+"\n")
						elif opts.completo: 
							sys.stderr.write(self.getName()+": "+l)
			except KeyboardInterrupt:
				print "Fin"

#######################################################################################
# Defino la clase MiProceso, la cual hereda de la clase Process, su misión es cojer de
# la cola (si hay algo) y quedarse con una lista, la cual contendra las últimas lineas
# que se han generado en el log ftp, a las cuales posteriormente les aplicará los
# correspondientes filtros. Cada vez que imprima algo por la salida de errores dirá
# además que hilo se ha encargado de ello.
# El diccionario (dicc) contiene:
#  -Clave: nombre y ruta absoluta de un fichero
#  -Valor: Objeto fichero abierto y con el puntero situado en la ultima posición de
#		   lectura realizada.
#######################################################################################

class MiProceso(multiprocessing.Process):
	def __init__(self, q, dicc):
		self.q = q
		self.dicc = dicc
		multiprocessing.Process.__init__(self)

	def run(self):
		while True:
			try:
				fichero = q.get()
				ultimasL = dicc[fichero].readlines()
				for l in ultimasL:
					dfields = logfields(l)
					if logfilter(dfields, dfilters):
						if opts.filtrables:
							sys.stderr.write(self.name+": "+l[:24]+" "+l.split()[6]+" "+l.split()[8]+" "+l.split()[13]+"\n")
						elif opts.completo: 
							sys.stderr.write(self.name+": "+l)							
			except KeyboardInterrupt:
				print "Fin"

#######################################################################################
# INICIO DEL PROGRAMA
#######################################################################################
# Importante: los módulos no deberían ejecutar código al ser importados por eso está:
# if __name__ == '__main__':
#######################################################################################

if __name__ == '__main__':

	opts, args = proc_opts() 
	
#######################################################################################
# Diccionario creado con las opciones del usuario y el servirá para comparar con
# el otro diccionario formado en cada lectura de linea de log.
#######################################################################################

	dfilters = {}
	if opts.hour :
		dfilters['hour'] = opts.hour 
	if opts.day: 
		dfilters['day'] = opts.day 
	if opts.month:
		dfilters['month'] = opts.month 
	if opts.host:
		dfilters['host'] = opts.host 
	if opts.usuario:
		dfilters['usuario'] = opts.usuario 
	if opts.fich:
		dfilters['fich'] = opts.fich 
	if opts.year:
		dfilters['year'] = opts.year

#######################################################################################
# El diccionario (dicc) contiene:
#  -Clave: nombre y ruta absoluta de un fichero
#  -Valor: Objeto fichero abierto y con el puntero situado al final del fichero (EOF)
#		   eso lo hago con el .seek(0,2)
#######################################################################################

	dicc={}
	for f in os.listdir(opts.dirLogs):
		fichero = os.path.abspath(os.path.join(opts.dirLogs, f))
		dicc[fichero]=open(fichero,"r")
		dicc[fichero].seek(0,2)

#######################################################################################
# Creo una cola que utilizaré para ir añadiendo los nombres y rutas absoluta de los
# ficheros que generan el evento buscado.
# Utilizo multiprocessing.Queue() para los procesos, ya que aunque no los utilizo,
# implementa algunos métodos más que Queue.Queue() y se adapta mejor que a este
# último.
#######################################################################################

	if opts.procesos:
		q = multiprocessing.Queue()		
	else:
		q = Queue.Queue()

#######################################################################################
# Creo un objeto WatchManager, que provee funciones de vigilancia
#######################################################################################	

	wm = pyinotify.WatchManager() 

#######################################################################################	
# Aquí establezco la máscara o los eventos de los que voy a estar pendiente
#######################################################################################	

	mask = pyinotify.IN_MODIFY 

#######################################################################################
# aqui defino una clase, la cual hereda de ProcessEvent y manejará las notificaciones
# especificamente cuando detecte una modificacion "_IN_MODIFY", simplemente lo que
# Hace cuando detecta una modificación en un fichero será meter en la cola "q", el
# nombre y ruta del fichero que ha generado ese evento.
#######################################################################################

	class EventHandler(pyinotify.ProcessEvent):		
		def process_IN_MODIFY(self, event):
			q.put(event.pathname)

#######################################################################################
# Ahora instancio la clase ThreadedNotifier, que creará un objeto notificador a modo
# de hilo. Luego comienza el notificador (se crea el hilo con notifier.start()),
# aunque todavía no va a monitorizar ningún fichero ni directorio.
#######################################################################################

	notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
	notifier.start()

#######################################################################################
# Seguidamente le añado algo para monitorizar con wm.add_watch(), en este caso le
# añado lo que me pasa optparse que en mi caso por defecto es el directorio ./logs_ftp
# que es donde se encuentran los supuestos diferentes logs de los servidores FTP.
# Si quiero dejar de vigilar ese directorio/fichero haría:
#																					  #
#	wm.rm_watch(wdd[opts.dirLogs])
#																					  #
# Si ademas quiero dejar de vigilar los subdirectorios:
#																					  #
#	wm.rm_watch(wdd[opts.dirLogs], rec=True)
#																					  #
# También puedo hacer esto para eliminar todo lo que se estaba vigilando:
#																					  #
#	wm.rm_watch(wdd.values())
# 																					  #
# En este caso vamos a vigilar sólo lo indicado en la máscara (mask)
# Le indico también que vigile en los subdirectorios (rec=True)
#######################################################################################

	wdd = wm.add_watch(opts.dirLogs, mask, rec=True)

#######################################################################################
# Me creo una lista vacia para luego ir añadiendo procesos o hilos, tantos como me
# recoga el optparse en la opción opts.numero (con la opcion -n), que por
# defecto es 4. A medida que los meto en la lista los voy lanzando.
# Por defecto el script trabaja con hilos a no ser que opts.procesos sea True
# Este caso se dará con la opción -p
#######################################################################################

	lista=[]	
	try:
		if opts.procesos:
			print "Monitorizando directorio de logs FTP en: %s, con %s Procesos"% (opts.dirLogs, opts.numero)
			for i in range (opts.numero):
				proceso=MiProceso(q, dicc)
				lista.append(proceso)
				proceso.start()
		else:
			print "Monitorizando directorio de logs FTP en: %s, con %s Hilos"% (opts.dirLogs, opts.numero)
			for i in range (opts.numero):
				hilo=MiHilo(q, dicc)
				lista.append(hilo)
				hilo.start()
	except KeyboardInterrupt:
		wm.rm_watch(wdd.values())
		notifier.stop()

#######################################################################################
# Esto último lo que hace es borrar todo lo que se esté vigilando y luego parar el
# notificador-chivato
#######################################################################################
