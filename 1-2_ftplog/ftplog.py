#!/usr/bin/python

import getopt, time, sys, re

def uso():
	print """
	USO: ftplog.py [-h] [-q | -v | -t] [-f fichero][-r host] [-u usuario] [-y YY] [-m MM] [-d DD] [-H HH] [fichero...]
    -h: muestra esta misma ayuda
	-v: muestra los registros(lineas) completos. Es el comportamiento por defecto. Incompatible con -q y -t	
	-q: muestra unicamente los campos filtrables (fecha, host, fichero, usuario) de los registros. Incompatible con -v y -t 	
	-t: muestra unicamente el total neto de registros que cumplen el filtro sobre el total de registros. Incompatible con -q y -v 
	-f fichero: filtra los registros que coincidan total o parcialmente con el nombre del fichero.
	-r host: filtra los registros que coincidan total o parcialmente con el host indicado.		
	-u usuario: filtra los registros que coincidan total o parcialmente con el usuario indicado
	-y YY: filtra los registros que coincidan con el anyo indicado
	-m MM: filtra los registros que coincidan con el mes indicado
	-d DD: filtra los registros que coincidan con el dia indicado
	-H HH: filtra los registros que coincidan con la hora indicada
	============OTRAS OPCIONES===============
	-D (o|i|d): Filtra los registros segun la direccion de la transferencia: o->outgoing, saliente; i->incoming, entrante; d->deleted, borrado.
	-s num bytes: Filtra los registros que coincidan al menos con la cantidad de bytes transferidos indicados.
	-i dd/mm/yyyy-hh: muestra las lineas que ademas de cumplir los filtros anteriores, esten entre las fechas indicadas con -d -m -y -H y la indicada con -i 		dd/mm/yyyy-hh. Esta opcion anula a -v, -q, -t
	"""


def imprimirseleccion(V, Q, T, F, R, U, Y, M, D, H, log, Dir, byt, I):
	
	try:	
		f=open(log,"r")
	except: 
		print "Error el fichero no existe"
		sys.exit(2)

	lista_lineas=f.readlines()#una vez que abro el fichero, lo convierto en una lista de cadenas
	cont = 0

	if I==None: #significa que no queremos intervalo de fichas. Bloque para las -v -q -t y los demas filtros
		for linea in lista_lineas:#itero por cada linea del fichero
			FyH=time.strptime(linea[:24], "%a %b %d %H:%M:%S %Y")
			if re.match(D,str(FyH[2])) and re.match(M, str(FyH[1])) and re.match(Y, str(FyH[0])) and re.match(H,str(FyH[3])) and re.search(R, linea.split()[6]) and re.search (F, linea.split()[8]) and re.search (U, linea.split()[13]) and re.match (Dir, linea.split()[11]) and byt <= int(linea.split()[7]):
#La linea que haya superado todos los filtros se imprimira de una u otra forma 
#dependiendo de la opcion de visuali
				if V:			
					print linea
				elif Q:
					print linea[:24], linea.split()[6], linea.split()[8], linea.split()[13]
				elif T:
					cont += 1
		if T:
			print "El total de registros que coinciden es:",cont

	else:#bloque para mostrar intervalos entre 2 fechas. -i. Y los filtros deseados
		#Le quito los $ ya que aqui no hacen falta.		
		D=D.strip("$")
		M=M.strip("S")
		Y=Y.strip("$")
		H=H.strip("$")
		#Si alguna delas opciones de fecha no la indico, se tomara la que se indique con el -i
		if Y=="":
			Y=time.strftime("%Y", I)
		if M=="":
			M=time.strftime("%m", I)
		if D=="":
			D=time.strftime("%d", I)
		if H=="":
			H=time.strftime("%H", I)
		#paso a sg las fechas
		sgsA=time.mktime(time.strptime (Y+M+D+H, "%Y%m%d%H"))
		sgsB=time.mktime(I)
		for linea in lista_lineas:
			sgs=time.mktime(time.strptime(linea[:24], "%a %b %d %H:%M:%S %Y")) #cada linea la paso a sg, para luego ver si esta entre el intervalo
			if re.search(R, linea.split()[6]) and re.search (F, linea.split()[8]) and re.search (U, linea.split()[13]) and re.match (Dir, linea.split()[11]) and byt <= int(linea.split()[7]):
				if sgs>sgsA and sgs<sgsB:
					print linea	

#por aqui empieza el script
try:
	opts, args = getopt.getopt(sys.argv[1:], "hvqtf:r:u:y:m:d:H:D:s:i:")
except getopt.GetoptError:
	uso()
	sys.exit(2)

#Lo siguiente es para averiguar si se selecciona mas de una de las opciones incompatibles
if opts.count(('-v',''))==1 and (opts.count(('-q',''))==1 or opts.count(('-t',''))==1):
	print "ERROR: Las opciones -v -q -t son incompatibles, seleccione solo una de ellas"
	sys.exit(2)

if opts.count(('-q',''))==1 and (opts.count(('-v',''))==1 or opts.count(('-t',''))==1):
	print "ERROR: Las opciones -v -q -t son incompatibles, seleccione solo una de ellas"
	sys.exit(2)
#A continuacion los valores por defecto de las variables
completosV=True
solicitadosQ=False
netoT=False
ficheroF=""
hostR=""
usuarioU=""
anyo=""
mes=""
dia=""
hora=""
direccion=""
bytes=0
interv=None
#Empiezo a procesar las opciones
for o, a in opts:
	if o == '-h':
		uso()
		sys.exit()
	elif o == '-v':
		completosV=True
	elif o == '-q':
		solicitadosQ=True
		completosV=False
	elif o == '-t':
		netoT=True
		completosV=False
	elif o == '-f':
		ficheroF=a
	elif o == '-r':
		hostR=a
	elif o == '-u':
		usuarioU=a
	elif o == '-y':
		if int(a)>1970:
			anyo=a+"$"#Le concateno el dolar para que al enviarselo al match como patron haya coincidencia completa
		else:
			print "El campo anyo es incorrecto"
			sys.exit(2)
	elif o == '-m':
		if int(a)>0 and int(a) < 13:
			mes=a+"$"
		else:
			print "El campo mes es incorrecto"
			sys.exit(2)
	elif o == '-d':
		if int(a)>0 and int(a) < 32:
			dia=a+"$"
		else:
			print "El campo dia es incorrecto"
			sys.exit(2)
	elif o == '-H':
		if int(a)>=0 and int(a)<24:
			hora=a+"$"
		else:
			print "El campo hora es incorrecto"
			sys.exit(2)
	elif o == '-D':
		direccion=a
	elif o == '-s':
		bytes=int(a)
	elif o == '-i':
		if re.match ("\d\d/\d\d/\d\d\d\d-\d\d", a): #para que solo la coja si esta con ese formato
			interv=time.strptime(a, "%d/%m/%Y-%H")
		else:
			print "El formato fecha introducido en -i debe ser dd/mm/yyyy-hh. Ejemplo 01/01/2001-05" 
			sys.exit(2)

if len(args) == 1:
	imprimirseleccion (completosV, solicitadosQ, netoT, ficheroF, hostR, usuarioU, anyo, mes, dia, hora, args[0], direccion, bytes, interv)
elif len(args) == 0:#Si no recibe ningun argumento analiza el log situado en /var/log/vsftp.log
	imprimirseleccion (completosV, solicitadosQ, netoT, ficheroF, hostR, usuarioU, anyo, mes, dia, hora, "/var/log/vsftp.log", direccion, bytes, interv)
else:
	print "ERROR: Este script recibe 0 o 1 argumentos"

