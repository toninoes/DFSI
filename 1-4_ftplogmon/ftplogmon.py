#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import sys
import optparse
import time
from select import select
from gamin import WatchMonitor, GAMChanged, GAMExists

def proc_opts(): 
	usage = "uso: %prog [opciones] arg1 arg2"
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
	comlist.add_option("-F", "--file", dest='logfile', default="vsftpd.log", help=u'fichero log, por defecto /var/log/vsftp.log', metavar="FILE")

	return comlist.parse_args(sys.argv)


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


def logfilter(dfields, dfilters):
	for e in dfilters: 
		if dfilters[e] not in dfields[e]:
			return False

	return True

#Inicio del Programa
opts, args = proc_opts() 

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

#Abro el fichero a monitorizar, por defecto ./vsftpd.log
g=open(opts.logfile, "r")


#funcion monitor, lo primero que hace es llegar hasta el final de fichero, tras
#GAMExist (se genera tras activar un monitor sobre un fichero).
#Luego cada GAMChanged, se agregan las demas lineas nuevas, a las cuales
#se les aplicaran los filtros correspondientes.
def monitor(path, event):
	if event == GAMExists:
		g.readlines()
	if event == GAMChanged:
		ultimasL=g.readlines()
		for l in ultimasL:
			dfields = logfields(l)
			if logfilter(dfields, dfilters):
				if opts.filtrables:
					sys.stderr.write(l[:24]+" "+l.split()[6]+" "+l.split()[8]+" "+l.split()[13]+"\n")
				elif opts.completo: 
					sys.stderr.write(l)
						
	return True

mon = WatchMonitor()
mon.watch_file(opts.logfile, monitor)
time.sleep(1)
fd = mon.get_fd()

while True:
	select([fd],[],[])
	if mon.event_pending():
		mon.handle_events() 

mon.stop_watch(fichero)
del mon

#para probarlo abro otra terminal y hago echo "xxxx" >> vsftpd.log
#Si quiero meter varias lineas en bloque hago echo "xxxx" >> vsftpd.log && echo "yyyyy" >> vsftpd.log
