#!/usr/bin/python

import threading
import SocketServer
import BaseHTTPServer
import sys
import optparse
import os
import hashlib


def proc_opts(): 
	usage = "USO: rbackupd.py camino al directorio de backups"
	comlist = optparse.OptionParser(usage=usage)
	comlist.add_option("-b", "--backup", dest='backups', default="./backups", help=u'Directorio para guardar los backups por defecto', metavar="PATH")

	return comlist.parse_args(sys.argv)


def funcHash(fichero):
	f=open(fichero,"r")
	sumaC= hashlib.md5(f.read()).hexdigest()
	f.close()
	return sumaC

def listaFicheros(ruta):
	for rutaDir, nombreDirs, nombreFichs in os.walk(ruta):
		pass
	return nombreFichs

class miManejadorTCP (BaseHTTPServer.BaseHTTPRequestHandler):

	global recibidos
	recibidos = []

	def do_GET(self):
		print "Peticion de: %s -> %s" % (self.client_address[0], self.path.strip("/"))		
		ruta = self.path.strip("/").split("//")[0]
		fich = self.path.split("//")[1]
		recibidos.append(fich)
		hashENcliente = self.path.split("//")[2]
		quiereBorrar = self.path.split("//")[3]
		directorioCliente = os.path.join(opts.backups, self.client_address[0])
		directorioClienteYrutaFich = os.path.join(directorioCliente, ruta)
		if not os.path.exists(directorioCliente):
			os.mkdir(directorioCliente)
		if not os.path.exists(directorioClienteYrutaFich):
			os.mkdir(directorioClienteYrutaFich)			
		if fich in listaFicheros(directorioCliente):
			fichero = os.path.abspath(os.path.join(directorioClienteYrutaFich, fich))	
			hashENservidor = funcHash(fichero)
			if hashENservidor ==  hashENcliente:		
				self.send_response(200)
				print "Existe el fichero %s en el directorio en el SERVIDOR y es identico" % (fich)		
				self.end_headers()
				content="No hay que actualizar %s"% fich		
				self.wfile.write(content)		
			else:
				self.send_response(206)
				print "Existe el fichero %s en el SERVIDOR pero el contenido no coincide" % (fich)
				self.end_headers() 
				content="Hay que actualizar %s porque ha variado"% fich	
				self.wfile.write(content)
		else:
			self.send_response(404)
			print "No existe el fichero %s en el SERVIDOR" % (fich)
			self.end_headers() 
			content="Hay que actualizar %s ya que no existe"% fich		
			self.wfile.write(content)

		if quiereBorrar == "True":
			for fichero in listaFicheros(directorioCliente):
				if fichero not in recibidos:
					os.remove(os.path.abspath(os.path.join(directorioClienteYrutaFich,fichero)))
					print "Borrado %s en el SERVIDOR" % (fichero)
					self.end_headers() 
					content="Borrado %s en el SERVIDOR" % (fichero)
					self.wfile.write(content)


	def do_POST(self):		
		ruta = self.path.strip("/")
		directorioCliente = os.path.join(opts.backups, self.client_address[0])
		directorioClienteYrutaFich = os.path.join(directorioCliente, ruta)
		contenFich = self.rfile.read(int(self.headers["content-length"]))	
		f = open (directorioClienteYrutaFich, "wb")
		f.write(contenFich)
		f.close()
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()


class servidorTCPconHilos(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass

#INICIO DEL PROGRAMA
if __name__ == "__main__":
	opts, args = proc_opts() 
	HOST, PORT = "", 8000
	servidor = servidorTCPconHilos ((HOST, PORT), miManejadorTCP)

	try:
		servidor.serve_forever()
	except KeyboardInterrupt:
		pass
	else:
		sys.exit()

