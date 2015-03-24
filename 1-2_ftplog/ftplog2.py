#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import sys
import optparse
import time

def proc_opts(): 
	usage = "uso: %prog [opciones] arg1 arg2"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-v", "--completo", action='store_true', default=False, help=u'muestra los registros(lineas) completos. Es el comportamiento por defecto.')
	comlist.add_option("-q", "--filtrables", action='store_true', default=False, help=u'muestra unicamente los campos filtrables de los registros')
	comlist.add_option("-t", "--neto", action='store_true', default=False, help=u'muestra unicamente el total neto de registros que cumplen el filtro sobre el total de registros')
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

opts, args = proc_opts() 

try:
	f = open(opts.logfile)
	
except:
	print "Error al abrir el fichero"
	sys.exit()

vsftpdlog = f.readlines()
f.close()

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

cont=0
for l in vsftpdlog:
	dfields = logfields(l)
	if logfilter(dfields, dfilters):
		if opts.completo: 
		    print l
		elif opts.filtrables:
			print l[:24], l.split()[6], l.split()[8], l.split()[13]
		elif opts.neto:
			cont+=1
	
if opts.neto:
	print "El total de registros que coinciden es:",cont	




