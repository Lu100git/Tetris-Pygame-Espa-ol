import pygame
import os
import random
from time import sleep
from colores import *
from tetrominos import *

MEDIDA_MOSAICO = 30
colores = [0, rojo, naranja, amarillo, verde, azul_cielo, azul, morado]

pygame.init()
ventana = pygame.display.set_mode((300, 600))
pygame.display.set_caption("Tetris By: Lu")

class Cuadricula:
	def __init__(self):
		self.filas = 20
		self.columnas = 10
		self.contador = 0
		
		# creando la matriz
		self.matrix = []
		for i in range(self.filas):
		    fila = []
		    for j in range(self.columnas):
		        fila.append(0) 
		    self.matrix.append(fila)

		# esta variable guarda una superficie que guarda un cuadro y se le asigna color despues
		self.superficie = pygame.Surface((MEDIDA_MOSAICO - 2, MEDIDA_MOSAICO - 2))

	# este metodo dibuja la pieza que ya no se mueve de acuerdo al valor de la matriz
	def dibujar(self):
		for i in range(self.filas):
			for j in range(self.columnas):

				# asignando el color del bloque caido de acuerdo al valor dentro de la matiz
				color_matrix = self.matrix[i][j]
				self.superficie.fill(colores[color_matrix])

				#funcion para dibujar sprites o superficies de pygame 
				ventana.blit(self.superficie, (j * MEDIDA_MOSAICO + 1, i * MEDIDA_MOSAICO + 1))

	# este metodo checa si cualquier fila se llega a llenar en la matriz
	def filaLlena(self, fila):
		contador_columnas = 0
		for i in range(self.columnas):
			if self.matrix[fila][i] != 0:
				contador_columnas += 1
		if contador_columnas > 9:
			return True

		return False

	# este metodo se encarga de limpiar las filas si alguna fila esta llena en la matriz
	def limpiaFila(self, fila):
		for i in range(self.columnas):
			self.matrix[fila][i] = 0

	# este metodo se encarga de bajar las piezas despues que la fila llena se limpia
	def desciendeFila(self, fila):
		for i in range(self.columnas):
			if fila == 0:
				break
			self.matrix[fila][i] = self.matrix[fila - 1][i]

	# este metodo se llamara en el bucle principal del juego
	def checaFilasLlenas(self):
		filas_llenas = 0

		# se recorre la matriz de mayor a menor valor de abajo hacia arriba
		for i in range(self.filas):	
			fila_actual = (self.filas - 1) - i

			# checando las filas, y limpialas si esta llena
			if self.filaLlena(fila_actual):
				self.limpiaFila(fila_actual)
				filas_llenas += 1

			# se cuentan las filas, y de acuerdo a la cantidad que se limpian, ese mismo numero se bajan
			if filas_llenas > 0:
				self.desciendeFila(fila_actual)

		# reinicia los valores de cuantas filas hay llenas cuando termina el bucle
		filas_llenas = 0

	# muestra los datos de la matriz en la consola
	def imprimeDatosConsola(self):
		self.contador += 1
		self.contador %= 12
		clear = 'cls'
		if os.name == "posix":
			clear = "clear"
		if self.contador == 0:
			os.system(clear)
			for i in range(self.filas):
				for j in range(self.columnas):
					print(self.matrix[i][j], " ", end = "")
				print()
			print("\n")
	

class Bloque:
	def __init__(self):
		self.tetrominos = [L,J,T,I,O,Z,S]
		self.pieza = self.asignaPiezaAleatoria()
		self.colorId = self.checaFormaTetromino()
		

		# variables para desplazar la pieza en ventana
		self.fila_desplazada = 0
		self.columna_desplazada = MEDIDA_MOSAICO * 3

		# variables para desplazar la pieza en la matriz
		self.fila_matrix = 0
		self.columna_matrix = 3

		# esta lista captura las coordenadas de la pieza en la matriz
		self.coordenadas = []

		# esta variable determina el indice de la matriz 2D de cada tetromino 
		self.rotacion = 0

		self.superficie = pygame.Surface((MEDIDA_MOSAICO - 2, MEDIDA_MOSAICO - 2))

		# estas variables determinan la velocidad a la que bajara la pieza
		self.contador = 0
		self.reinicio_contador = 15

	# asigna pieza aleatoria
	def asignaPiezaAleatoria(self):
		if len(self.tetrominos) == 0:
			self.tetrominos = [L,J,T,I,O,Z,S]
		pieza = random.choice(self.tetrominos)
		self.tetrominos.remove(pieza)
		return pieza

	# desplaza la pieza a la derecha cuando al presionar la flecha derecha
	def movimientoDerecho(self, matrix):
		self.columna_matrix += 1
		self.columna_desplazada += 1 * MEDIDA_MOSAICO
		# obten las coordenadas antes de mover la pieza
		self.coordenadas = self.obtenerCoordenadas()
		if self.estaDentro() == False:
			for i in range(4):
				# si se sale, regresala
				if self.coordenadas[i][0] > 9:
					self.columna_matrix -= 1
					self.columna_desplazada -= MEDIDA_MOSAICO
					break
		# si hay un bloque alado, rechaza el movimiento
		elif self.celdaOcupada(matrix, self.coordenadas):
			self.columna_matrix -= 1
			self.columna_desplazada -= MEDIDA_MOSAICO

	# desplaza la pieza a la izquierda cuando al presionar la flecha izquierda, lo mismo del metodo de arriba
	# pero hacia la izquierda
	def movimientoIzquierdo(self, matrix):
		self.columna_matrix -= 1
		self.columna_desplazada -= 1 * MEDIDA_MOSAICO
		self.coordenadas = self.obtenerCoordenadas()
		
		if self.estaDentro() == False:
			
			for i in range(4):
				if self.coordenadas[i][0] < 0:
					self.columna_matrix += 1
					self.columna_desplazada += MEDIDA_MOSAICO
					break

		elif self.celdaOcupada(matrix, self.coordenadas):
			self.columna_matrix += 1
			self.columna_desplazada += MEDIDA_MOSAICO

	# gira la pieza
	def gira(self):
		self.rotacion += 4
		if self.rotacion > 12:
			self.rotacion = 0
		# obten las cordenadas despues de girar la pieza para determinar si es vallida la rotacion
		# si no es valida, regresa la rotacion previa, 
		self.coordenadas = self.obtenerCoordenadas()
		if self.estaDentro() == False:
			self.rotacion -= 4
		
	# dibuja la pieza en la ventana
	def dibujar(self):
		for i in range(4): # 16
			for j in range(4): # 4
				if self.pieza[i + self.rotacion][j] == 'x':
					self.superficie.fill(colores[self.colorId])
					ventana.blit(self.superficie, (self.columna_desplazada + MEDIDA_MOSAICO * j , self.fila_desplazada + MEDIDA_MOSAICO * i))

	# este metodo se encargara de mover la pieza y checar las colisiones para prevenir movimientos no validos, generlmente en programacion a esta funcion le llaman update()
	def actualizar(self, matrix):		
		# incrementa el contador
		self.contador += 1

		# demora el movimiento de la pieza 
		self.contador %= self.reinicio_contador
		if self.contador == 0:
			self.fila_desplazada += MEDIDA_MOSAICO
			self.fila_matrix += 1

		# se llamaran las coordenadas constantemente para verificar la colision, OJO, este metodo ya lo habia llamado antes en otros metodos, eso se debe a que
		# no hay que depender del bucle principal para checar coordenadas, eso me dio muchos glitches en el juego y no me dejaba regresar el giro de la pieza
		self.coordenadas = self.obtenerCoordenadas()
		
		# si la pieza cae al fondo
		if self.estaAbajo():
			# obten las coordenadas
			self.coordenadas = self.obtenerCoordenadas()
			# regresa la pieza 1 valor hacia arriba, ya que el metodo checara si la pieza se pasa de la zona de juego
			for i in range(4):
				self.coordenadas[i][1] -= 1

			# cuando se regresa la pieza hacia arriba, copia las coordenadas en la matriz con los valores del color 1 2 3 4... etc
			for i in range(4):
				matrix[self.coordenadas[i][1]][self.coordenadas[i][0]] = self.colorId

			# reinicia los valores y regresa la pieza hacia arriba
			self.fila_desplazada = 0
			self.columna_desplazada = MEDIDA_MOSAICO * 3
			self.fila_matrix = 0
			self.columna_matrix = 3
			
			self.rotacion = 0
			self.pieza = self.asignaPiezaAleatoria()
			self.colorId = self.checaFormaTetromino()

		# lo mismo de arriba pero checka si las celdas estan ocupadas
		elif self.celdaOcupada(matrix, self.coordenadas):
			self.coordenadas = self.obtenerCoordenadas()
			for i in range(4):
				self.coordenadas[i][1] -= 1

			for i in range(4):
				matrix[self.coordenadas[i][1]][self.coordenadas[i][0]] = self.colorId

			self.fila_desplazada = 0
			self.columna_desplazada = MEDIDA_MOSAICO * 3
			self.fila_matrix = 0
			self.columna_matrix = 3

			self.rotacion = 0
			self.pieza = self.asignaPiezaAleatoria()
			self.colorId = self.checaFormaTetromino()		

	# regresa las coordenadas de la pieza en formato de lista 2D p
	def obtenerCoordenadas(self):
		indice_matrix = []
		for i in range(4):
			for j in range(4):
				if self.pieza[i + self.rotacion][j] == 'x':
					indice_matrix.append([self.columna_matrix + j, self.fila_matrix + i])
		return indice_matrix

	# sin albur, checa si la pieza esta dentro de la zona de juego hacia los lados
	def estaDentro(self):
		for i in range(4):
			if self.coordenadas[i][0] < 0 or self.coordenadas[i][0] > 9:
				return False
		return True

	# checa si la pieza se salio de la zona de juego hacia abajo
	def estaAbajo(self):
		for i in range(4):
			if self.coordenadas[i][1] > 19:
				return True
		return False

	# checa si la celda en las coordenadas que se den esta ocupada
	def celdaOcupada(self, matrix, position):
		for i in range(4):
			if matrix[self.coordenadas[i][1]][self.coordenadas[i][0]] > 0:
				return True
		return False

	# asigna el color de la pieza de acuerdo al indice de colores
	def checaFormaTetromino(self):
		if self.pieza == L:
			return 1
		elif self.pieza == J:
			return 2
		elif self.pieza == T:
			return 3
		elif self.pieza == I:
			return 4
		elif self.pieza == O:
			return 5
		elif self.pieza == Z:
			return 6
		elif self.pieza == S:
			return 7

# se crean objetos
cuadricula = Cuadricula()
bloque = Bloque()

#inicia bucle principal
ejecutando = True
while ejecutando:
	# eventos
	for event in pygame.event.get():
		
		# controles
		if event.type == pygame.QUIT:
			ejecutando = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				ejecutando = False
			elif event.key == pygame.K_SPACE:
				bloque.gira()
			elif event.key == pygame.K_LEFT:
				bloque.movimientoIzquierdo(cuadricula.matrix)
			elif event.key == pygame.K_RIGHT:
				bloque.movimientoDerecho(cuadricula.matrix)
			elif event.key == pygame.K_DOWN:
				bloque.reinicio_contador = 1
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_DOWN:
				bloque.reinicio_contador = 15

	# imprime datos de la matriz en consola
	cuadricula.imprimeDatosConsola()

	# si se acomulan las piezas hasta el tope fin del juego
	for i in range(cuadricula.columnas):
		if cuadricula.matrix[0][i] > 0:
			ventana.fill(0)
			ejecutando = False

	# update()
	cuadricula.checaFilasLlenas()
	bloque.actualizar(cuadricula.matrix)

	# render
	ventana.fill(0)
	cuadricula.dibujar()
	bloque.dibujar()
	pygame.display.update()
	# esto se puede remplazar por el pygame.Clock, pero me dio flojera hack de 60FPS
	sleep(10/1000)
