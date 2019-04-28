#!/usr/bin/env python

import sys
import optparse
from scapy.all import sniff

#####################################################################################
# Necesario tener instalado scapy: sudo apt-get install python-scapy
#####################################################################################
# Necesario ejecutar script como administrador, ya que scapy necesita tener control
# privilegiado sobre las interfaces.
#####################################################################################

def proc_opts(): 
	usage = "USO: sudo ./ips.py -h |  [-i numero]  [-s subred] [-f fichero] [-I interfaz] [-g Puerta_enlace] [-f fichero conf] [-r rango inferior dinamica] [-R rango superior dinamica]"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-i", "--inicio", default="101", help=u'permite definir el inicio de asignacion de IPs estaticas. Por defecto 101', metavar="string")
	comlist.add_option("-r", "--rangoInf", default="1", help=u'permite definir el rango inferior de IPs dinamicas. Por defecto 1', metavar="string")
	comlist.add_option("-R", "--rangoSup", default="100", help=u'permite definir el rango superior de IPs dinamicas. Por defecto 100', metavar="string")
	comlist.add_option("-s", "--subred", default="192.168.1.", help=u'permite definir la subred. Por defecto 192.168.1.', metavar="string")
	comlist.add_option("-I", "--interfaz", default="eth0", help=u'Interfaz de escucha. Por defecto eth0', metavar="string")
	comlist.add_option("-g", "--gateway", default="254", help=u'Puerta de enlace. Por defecto 254', metavar="string")
	comlist.add_option("-f", "--dhcpd", default="dhcpd.conf", help=u'opcion para indicar en que fichero guardar la configuracion. Por defecto ./dhcpd.conf', metavar="FILE")

	return comlist.parse_args(sys.argv)

#####################################################################################
# 	INICIO DEL PROGRAMA
#####################################################################################

opts, args = proc_opts() 

f = open (opts.dhcpd, "w")

num = int(opts.inicio)

listaMacs=[]

try:
	f.write ("subnet %s0 netmask 255.255.255.0 {\n" % opts.subred )
	f.write ("range %s%s %s%s;\n" % (opts.subred, opts.rangoInf, opts.subred, opts.rangoSup) )	
	f.write ("option routers %s%s;\n" % (opts.subred, opts.gateway ) )
	f.write ("option broadcast-address %s255;\n}\n\n" % opts.subred )


#####################################################################################
# Ahora con la funcion sniff de scapy voy capturando en la interfaz que yo defina
# , por defecto eth0 los paquetes que cumplan el filtro "filter", es decir, que
# usen UDP y el puerto 67. En principio no distingue entre puerto origen y destino
# pero en este caso nos da igual, ya que solo va ha capturar un paquete, en mi
# caso, el que me interesa (DHCP Discovery).
# La funcion sniff, devuelve una lista, en este caso de 1 elemento (a[0]), el cual
# tiene una serie de atributos. El que me interesa tomar es 'src', donde esta la
# MAC de origen del equipo que hace la peticion. Esa MAC la voy agregando a una
# lista para que si detecta un nuevo pauete con esa MAC, la descarte.
# Con las MACs de los equipos solicitantes y aumentando en 1 cada vez en las IPs,
# voy generando el fichero dhcp.conf
#####################################################################################

	while True:
		a=sniff(iface=opts.interfaz, filter="udp and port 67", count=1)
		if a[0].src not in listaMacs:
			f.write ("host %s{\n" % str(num))
			f.write ("hardware ethernet %s;\n" % a[0].src)
			f.write ("fixed-address %s%s;\n}\n\n" % (opts.subred, str(num)))	

			print "Asignada la IP: %s%s al equipo con MAC: %s" % (opts.subred, str(num), a[0].src)
			listaMacs.append(a[0].src)
		num += 1

except IndexError:
	f.close()
	sys.exit()



