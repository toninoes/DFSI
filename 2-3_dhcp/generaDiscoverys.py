#!/usr/bin/env python

import time
import optparse
import sys
from scapy.all import RandMAC, sendp, Ether, IP, UDP, BOOTP, DHCP, RandString

#####################################################################################
# 						Necesario tener instalado scapy								#
# 					   sudo apt-get install python-scapy							#
#####################################################################################
# Necesario ejecutar script como administrador, ya que scapy necesita tener control	#
# privilegiado sobre las interfaces.												#
#####################################################################################

def proc_opts(): 
	usage = "USO: sudo ./generaDiscoverys.py -h |  [-n numero_de_Peticiones]  [-i interfaz]"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-n", "--numero", default="5", help=u'numero de DHCP Discovery a generar. Defecto 5', metavar="string")
	comlist.add_option("-i", "--interfaz", default="eth0", help=u'interfaz de salida de peticiones. Defecto eth0', metavar="string")


	return comlist.parse_args(sys.argv)

#####################################################################################
# 								INICIO DEL PROGRAMA									#
#####################################################################################

opts, args = proc_opts()

dhcp_discover =  Ether(src=RandMAC(),dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0",dst="255.255.255.255")/UDP(sport=68,dport=67)/BOOTP(chaddr=RandString(12,'0123456789abcdef'))/DHCP(options=[("message-type","discover"),"end"])

num=0
while num < int(opts.numero):
	sendp(dhcp_discover, iface=opts.interfaz)
	time.sleep(1)
	num += 1

#####################################################################################
# Para crear un paquete DHCPDiscovery necesitamos:									#
#																					#
# -Capa de enlace (Ether):															#
#		src: MAC de origen, o MAC del equipo que hace la peticion dhcp. Gracias a	#
#			 la funcion RandMAC de scapy se crea una MAC aleatoriamente.			#
#																					#
#		dst: MAC de destino, que debe ser "ff:ff:ff:ff:ff:ff", ya que el que hace	#
#			 la peticion dhcp no sabe que MAC tiene el servidor DHCP, con lo que	#
#			 envia una trama broadcast que ven todos los equipos, con el objetivo	#
#			 de descubrir un servidor DHCP.											#
#																					#		
# -Capa de Red (IP):																#
#		src: La IP del equipo que hace la peticion, en este caso debe ser todo		#
#			 a ceros, porque aun no tiene IP.										#
#																					#
#		dst: es la red de difusion, 255.255.255.255, que tambien llega a todos los	#
#			 equipos de la red.														#
#																					#
# -Capa de Transoprte (que use UDP):												#
#		Con puerto origen 68 y destino 67											#
#																					#
# -Capa de Aplicacion (BOOTP, DHCP):												#
#		Donde se definen los parametro necesarios para completar un paquete			#
#		DHCP Discovery																#
#####################################################################################
