import uuid #Nos permite generar identificadores únicos
import random
import time #Para trabajar con funciones relaciones con el tiempo.
import threading #Nos permite trabajar con multiples hilos

#Esta clase es como la plantilla para cada proceso que creamos
#Contiene toda la información relevante de un proceso individual
class Proceso:
    def __init__(self, pid, nombre=None, memoria_mb=None, duracion_s=None):
        self.pid = pid #Identificador único del proceso
        #Si no se da un nombre, se genera uno por defecto
        self.nombre = nombre if nombre else f"Proceso-{self.pid}"
        # Si no se especifican, la memoria y duración son aleatorias
        self.memoria_mb = memoria_mb if memoria_mb else random.randint(50, 250)
        self.duracion_s = duracion_s if duracion_s else random.randint(5, 20)
        # El tiempo restante se irá decrementando en la simulación
        self.tiempo_restante = self.duracion_s
        self.estado = "Listo" # Estado inicial del proceso
        # Atributos para calcular estadísticas de tiempo
        self.tiempo_inicio = None
        self.tiempo_fin = None
        self.tiempo_duracion_real = 0 # Para saber cuánto tiempo realmente estuvo en ejecución

#Se encarga de todo lo relacionado con la RAM.
#Asigna y libera memoria de forma segura, evitando que dos procesos la modifiquen a la vez
class GestorMemoria:
    def __init__(self, ram_total_gb=1):
        self.ram_total = ram_total_gb * 1024 #Convertimos GB a MB
        self.memoria_disponible = self.ram_total
        #Un 'Lock' es como un semáforo. Solo un hilo puede "tener" el lock a la vez
        #Esto previene condiciones de carrera al modificar la memoria disponible
        self.lock = threading.Lock()

    def asignar_memoria(self, proceso):
        # 'with self.lock:' asegura que el bloque de código se ejecute de forma atómica
        # El lock se adquiere al entrar y se libera automáticamente al salir
        with self.lock:
            if self.memoria_disponible >= proceso.memoria_mb:
                self.memoria_disponible -= proceso.memoria_mb
                return True# Hay memoria suficiente.
            return False# No hay memoria.

    # También se usa un lock para liberar memoria de forma segura
    def liberar_memoria(self, proceso):
        with self.lock:
            self.memoria_disponible += proceso.memoria_mb

#Es el cerebro de la operación, la memoria, los procesos,
#la ejecución en hilos y las estadísticas
class Simulador:
    def __init__(self):
        self.gestor_memoria = GestorMemoria()
        self.cola_espera = [] # Procesos esperando por RAM
        self.procesos_en_ejecucion = {} #Diccionario para acceso rápido por PID
        self.procesos_terminados = [] #Historial de procesos completados
        self.proceso_id_counter = 0 #Para generar PIDs secuenciales
        self.ejecutando = False #Flag para controlar el bucle principal del hilo
        self.pausado = False #Flag para pausar/reanudar la simulación
        self.estadisticas = {
            "procesos_ejecutados": 0,
            "memoria_usada_promedio": 0,
            "tiempo_vida_promedio": 0,
        }
        # Este lock es para el simulador, para proteger el acceso a las listas de procesos
        self.lock = threading.Lock()
        # Se define el hilo que correrá la simulación. 'daemon=True' significa que
        # el hilo se cerrará automáticamente cuando el programa principal termine
        self.hilo_ejecucion = threading.Thread(target=self.ejecutar_simulacion, daemon=True)

    # Añade un nuevo proceso a la cola de espera de forma segura
    def agregar_proceso(self, proceso):
        with self.lock:
            self.cola_espera.append(proceso)
            self.intentar_ejecutar_procesos()

    #Revisa la cola de espera y mueve procesos a ejecución si hay RAM disponible
    #Es como promover el proceso si lo quieren ver asi
    def intentar_ejecutar_procesos(self):
        procesos_a_ejecutar = []
        for proceso in self.cola_espera:
            if self.gestor_memoria.asignar_memoria(proceso):
                proceso.estado = "En ejecución"
                proceso.tiempo_inicio = time.time()
                self.procesos_en_ejecucion[proceso.pid] = proceso
                procesos_a_ejecutar.append(proceso)
        
        #Se sacan de la cola los procesos que ya se movieron a ejecución
        for proceso in procesos_a_ejecutar:
            self.cola_espera.remove(proceso)

    # Este es el bucle principal que corre en el hilo secundario
    def ejecutar_simulacion(self):
        self.ejecutando = True
        while self.ejecutando:
            if not self.pausado:
                with self.lock:
                    procesos_terminados_pids = []
                    #Se itera sobre una copia de los items para poder modificar el diccionario
                    for pid, proceso in list(self.procesos_en_ejecucion.items()):
                        proceso.tiempo_restante -= 1
                        if proceso.tiempo_restante <= 0:
                            # El proceso ha terminado su ejecución
                            proceso.estado = "Terminado"
                            proceso.tiempo_fin = time.time()
                            if proceso.tiempo_inicio:
                                proceso.tiempo_duracion_real = proceso.tiempo_fin - proceso.tiempo_inicio
                            self.gestor_memoria.liberar_memoria(proceso)
                            procesos_terminados_pids.append(pid)
                    
                    #Se mueven los procesos terminados a su lista correspondiente
                    for pid in procesos_terminados_pids:
                        proceso_terminado = self.procesos_en_ejecucion.pop(pid)
                        self.procesos_terminados.append(proceso_terminado)
                        self.actualizar_estadisticas()

                    #Después de liberar memoria, se intenta ejecutar nuevos procesos
                    self.intentar_ejecutar_procesos()
            
            #Pausa de 1 segundo para simular el paso del tiempo
            time.sleep(1)

    #Inicia el hilo de simulación si no está ya corriendo
    def iniciar_simulacion(self):
        if not self.hilo_ejecucion.is_alive():
            self.hilo_ejecucion.start()

    #Pausa el hilo de simulación si ya está corriendo
    def pausar_simulacion(self):
        self.pausado = True

    #Reanuda el hilo de simulación si está ya en pausa
    def reanudar_simulacion(self):
        self.pausado = False
        
    #Restablece el simulador a su estado inicial
    def reiniciar_simulacion(self):
        self.gestor_memoria = GestorMemoria()
        self.cola_espera.clear()
        self.procesos_en_ejecucion.clear()
        self.procesos_terminados.clear()
        self.proceso_id_counter = 0
        self.estadisticas = {
            "procesos_ejecutados": 0,
            "memoria_usada_promedio": 0,
            "tiempo_vida_promedio": 0,
        }
    
    # Lógica para cancelar un proceso, ya sea en cola o en ejecución.
    # Los procesos cancelados no cuentan para las estadísticas
    def cancelar_proceso(self, pid):
        with self.lock:
            # Primero busca en la cola de espera
            for i, p in enumerate(self.cola_espera):
                if p.pid == pid:
                    self.cola_espera.pop(i)
                    return

            #Si no está en la cola, busca en los procesos en ejecución
            if pid in self.procesos_en_ejecucion:
                #Guardamos en la variable el proceso a elimnar
                proceso_cancelado = self.procesos_en_ejecucion.pop(pid)
                #Liberamos el espacio en memoria
                self.gestor_memoria.liberar_memoria(proceso_cancelado)
                return

    # Método para que la GUI pueda obtener las estadísticas
    def obtener_estadisticas(self):
        return self.estadisticas

    #Método para que la GUI pueda obtener el uso de memoria actual
    def obtener_uso_memoria(self):
        total = self.gestor_memoria.ram_total
        usada = total - self.gestor_memoria.memoria_disponible
        return usada, total

    #Recalcula las estadísticas basadas en los procesos que han terminado
    def actualizar_estadisticas(self):
        #Cuenta cuantos procesos terminaron 
        num_terminados = len(self.procesos_terminados)
        #Actualizamos la estadística del total de procesos ejecutados
        self.estadisticas["procesos_ejecutados"] = num_terminados
        
        #Si hay procesos terminados
        if num_terminados > 0:
            #Sumamos la memoria de todos los procesos terminados
            memoria_total = sum(p.memoria_mb for p in self.procesos_terminados)
            #Lo dividimos entre el numero total de procesos terminados y obtenemos el promedio
            self.estadisticas["memoria_usada_promedio"] = memoria_total / num_terminados
            
            #Creamos una lista con todos los tiempos de duración de todos los procesos terminados
            tiempos_vida = [p.tiempo_duracion_real for p in self.procesos_terminados if p.tiempo_duracion_real is not None]
            #Si la lista no es vacia
            if tiempos_vida:
                #Suma todos los tiempos y los divide entre por la cantidad de procesos terminados
                self.estadisticas["tiempo_vida_promedio"] = sum(tiempos_vida) / len(tiempos_vida)
        else:
            self.estadisticas["memoria_usada_promedio"] = 0
            self.estadisticas["tiempo_vida_promedio"] = 0