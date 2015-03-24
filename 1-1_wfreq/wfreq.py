#!/usr/bin/python
import re
import getopt
import sys
import os

def uso():
	print """USO: wfreq.py [-h] [-q] [-r] [-n N] [-g glosario]
		-h: muestra esta misma ayuda
		-q: no se muestra el total de palabras distintas del texto y el tanto por ciento de
		    ellas que no estaba en el glosario (por defecto, se muestra)
		-r: se ordena las frecuencias de menor a mayor (por defecto, de mayor a menor)
		-n N: se muestra las N palabras mas (o menos si -r) frecuentes (por defecto todas)
		-g glosario: fichero que contiene el glosario de palabras a ignorar en el analisis"""


def frecuencias (cadena, glosario, quitar, MayorAMenor, n):

	texto=cadena

	#primero meto en un lista todas las palabras de la cadena, previamente tratadas	
	lista = re.split( "\W+", texto.lower())

	if glosario == None:
		None
	else:
		fG = open(glosario, "r") 
		textoG = fG.read()
		fG.close()
		#en listaG meto cada una de las palabras del glosario
		listaG = textoG.split()

	#primero meto en un lista todas las palabras del fichero, previamente tratadas	
	lista = re.split( "\W+", texto.lower())

	#declaro 2 diccionarios uno para luego meter ahi las palabras no incluidas en Glosario (dicc) y otro para meter 	#ahi todas las del glosario
	dicc={}

	
	if glosario == None:
		None
	else:
		diccG={}
		#introduzco todas las palabras del glosario que estan en listaG en diccG, con sus valores a cero
		for nodo in listaG:
			diccG[nodo] = 0	
	
	numpalabrasTotales=0


	if glosario == None:
		for palabra in lista:
			if palabra.isalpha():
				if dicc.has_key (palabra):			
					dicc [palabra] += 1
				else:
					dicc [palabra] = 1
			numpalabrasTotales += 1
	else:
		#meto todas las palabras de lista en dicc, pero solo las que no estan en diccG
		for palabra in lista:
			if palabra.isalpha():
				if not diccG.has_key (palabra): 
					if dicc.has_key (palabra):			
						dicc [palabra] += 1
					else:
						dicc [palabra] = 1
				else:
					diccG [palabra] += 1
			numpalabrasTotales += 1

	lista = [] #borro la lista anterior, para incluir solo en ella las que entraron en dicc
	for elem in dicc:
		lista.append( (dicc[elem], elem) )

	lista.sort()

	if MayorAMenor == True:
		lista.reverse()
	
	cont=0
	print "LA FRECUENCIA DE PALABRAS DEL TEXTO ES:"
	for nodo in lista:
		cont += 1
		porcentaje = (100.0 * nodo[0]) / numpalabrasTotales
		print cont, " "+ nodo[1] + ": ",nodo[0]," veces - ",porcentaje,"%"
		if cont == int(n): 
			break

	if quitar == False:
		#total palabras que se encuentran en el glosario
		cont=0
		if glosario != None:
			for elem in diccG:
				if diccG[elem] > 0: #del diccionario_Glosario (diccG) solo cuento las May. de 0
					cont += 1

		#al total anterior le sumo todas las entradas de dicc, ya que todas se repiten al menos 1 vez
		cont2=0
		for elem in dicc:
			cont2 += 1
		palabrasdistintas = cont + cont2

		print "TOTAL PALABRAS DISTINTAS ",palabrasdistintas, " PALABRAS"
		if glosario == None:
			print ""
		else:
			print "DE ELLAS, EL ", (cont2*100.0)/palabrasdistintas ,"% NO ESTABA EN EL GLOSARIO"




def main():

	num=-1
	glosario=None
	quitar=False
	MAYORmenor=True

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hqrn:g:")
	except getopt.GetoptError:
		uso()
		sys.exit(2)
	
	for o, a in opts:
		if o == '-h':
			uso()
			sys.exit()
		elif o == '-q':
			quitar=True
		elif o == '-r':
			MAYORmenor=False
		elif o == '-n':
			num=a
		elif o == '-g':
			glosario=a
	if args:
		cadena=""
		for fichero in args:
			if os.path.exists (fichero):
				f = open(fichero, "r") 
				texto = f.read()
				cadena = cadena + texto
				f.close()
			else:
				print "No existe el fichero ",fichero
				sys.exit(2)
	else:
		cadena=sys.stdin.read()
		#cadena = raw_input ("No has indicado ningun fichero. Introduce una cadena a analizar: ")
	
	frecuencias(cadena, glosario, quitar, MAYORmenor, num)

if __name__ == "__main__":
    main()
	



