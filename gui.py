import sys
import math
from collections import deque
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFrame, QDialog, QSizePolicy
)
from PySide6.QtCore import QTimer, Qt, QRect
from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QIntValidator

#Se importa la lógica real del simulador desde tu archivo core.py
from core import Simulador, Proceso

#Widget para la barra de progreso circular
class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.progress_color = QColor("#22c55e")
        self.bg_color = QColor("#334155")
        self.text_color = QColor("#e2e8f0")
        # Se redujo el tamaño mínimo y máximo para hacer el círculo más pequeño
        self.setMinimumSize(80, 80)
        self.setMaximumSize(80, 80)

    def setValue(self, value):
        self.value = value
        self.update()

    #Este metodo se ejecuta cada vez que la interfaz gráfica necesita pintar el widget 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height())
        # Ajuste del rectángulo para el nuevo tamaño del círculo
        rect = QRect((self.width() - side) // 2, (self.height() - side) // 2, side, side).adjusted(8, 8, -8, -8)
        
        pen = QPen(self.bg_color, 8, Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        pen.setColor(self.progress_color)
        painter.setPen(pen)
        span_angle = -int((self.value / self.max_value) * 360 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)

        font = self.font()
        font.setPointSize(max(8, int(side / 8)))
        font.setBold(True)
        painter.setFont(font)
        pen.setColor(self.text_color)
        painter.setPen(pen)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")

#Ventana de dialogo para los errores
class CustomErrorDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error de Validación")
        self.setModal(True) # Hace que el diálogo sea modal (bloquea la ventana principal)

        #Aplicar estilos similares a la ventana principal
        self.setStyleSheet("""
            QDialog { 
                background-color: #1e293b; 
                color: #e2e8f0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px; 
                border-radius: 12px; 
            }
            QLabel { 
                color: #e2e8f0; 
                font-size: 16px; 
                padding: 10px; 
                text-align: center;
                /* Se agrega para permitir que el texto se ajuste y envuelva */
                qproperty-wordWrap: true; 
            }
            QPushButton { 
                background-color: #ef4444; 
                color: #ffffff; 
                font-weight: bold; 
                border-radius: 8px; 
                padding: 10px 20px; 
                border: none; 
                outline: none;
            }
            QPushButton:hover { 
                background-color: #dc2626; 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        #Se configura la política de tamaño para que el label se expanda verticalmente
        self.message_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(self.message_label)

        self.ok_button = QPushButton("Aceptar")
        self.ok_button.clicked.connect(self.accept) # Cierra el diálogo al hacer clic
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        #Se ajusta el tamaño del diálogo al contenido
        self.adjustSize()

#Configuramos la venta principal
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        #Creamos la instancia del simulador que manejará la lógica interna
        self.simulador = Simulador()
        #Para el titulo
        self.setWindowTitle("Simuladora de RAM")
        self.setGeometry(100, 100, 1400, 800)

        #Aplicamos estilos css
        self.setStyleSheet("""
            QMainWindow, QWidget#centralWidget { background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
            QFrame#card { background-color: #1e293b; border-radius: 12px; padding: 15px; }
            QLabel { color: #cbd5e1; padding-bottom: 5px; }
            QLabel#titleLabel { font-size: 18px; font-weight: bold; color: #e2e8f0; padding-bottom: 10px; }
            /* MODIFICACIÓN: Se ajusta el estilo para el layout horizontal */
            QLabel#titleNoCard { font-size: 16px; font-weight: bold; color: #e2e8f0; }
            QLabel#statLabel { font-size: 14px; color: #94a3b8; }
            QLabel#statValue { font-size: 24px; font-weight: bold; color: #e2e8f0; padding-bottom: 15px; }
            QPushButton { 
                background-color: #22c55e; 
                color: #ffffff; 
                font-weight: bold; 
                border-radius: 8px; 
                padding: 12px; 
                border: none; 
                outline: none; /* Se agrega esta línea para quitar el cuadro de selección */
            }
            QPushButton:hover { background-color: #16a34a; }
            QPushButton#controlButton { background-color: #3b82f6; }
            QPushButton#controlButton:hover { background-color: #2563eb; }
            QPushButton#dangerButton { background-color: #ef4444; }
            QPushButton#dangerButton:hover { background-color: #dc2626; }
            QLineEdit { background-color: #0f172a; color: #e2e8f0; border: 1px solid #334155; padding: 10px; border-radius: 8px; }
            QProgressBar { background-color: #334155; border: none; border-radius: 8px; text-align: center; color: #e2e8f0; height: 16px; }
            QProgressBar::chunk { background-color: #22c55e; border-radius: 8px; }
            QTableWidget { 
                background-color: transparent; 
                color: #e2e8f0; 
                border: none; 
                /* Se eliminó gridline-color: #334155; */
            }
            QHeaderView::section { background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 10px; border: none; }
            QTableWidget::item { padding-left: 10px; }
        """)

        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.left_column, self.center_column, self.right_column = QVBoxLayout(), QVBoxLayout(), QVBoxLayout()
        for col in [self.left_column, self.center_column, self.right_column]: col.setSpacing(20)

        #Estructura de la columna izquierda
        panel_memoria = self.crear_panel_memoria()
        panel_proceso_controles = self.crear_panel_proceso_y_controles()
        layout_carga_sistema = self.crear_panel_carga_sistema()

        self.left_column.addWidget(panel_memoria)
        self.left_column.addWidget(panel_proceso_controles)
        self.left_column.addLayout(layout_carga_sistema)

        self.left_column.addStretch(1)
        
        self.crear_tabla_cola()
        self.crear_tabla_ejecucion()
        #Se elimina el stretch aquí para permitir que la tabla de ejecución se estire
        #self.center_column.addStretch(1)

        self.crear_panel_estadisticas()
        self.crear_tabla_terminados()
        #Se añade un stretch al final de la columna derecha para alinear la parte inferior
        self.right_column.addStretch(1)

        #Se ajustan los factores de estiramiento para las columnas
        self.main_layout.addLayout(self.left_column, 1)
        self.main_layout.addLayout(self.center_column, 2)
        self.main_layout.addLayout(self.right_column, 1)

        self.simulador.iniciar_simulacion()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_ui)
        self.timer.start(500)

    #Creamos los panel base (contenedores) con un diseño y un titulo opcional
    def _crear_panel_base(self, title):
        panel_frame = QFrame()
        panel_frame.setObjectName("card")
        panel_layout = QVBoxLayout(panel_frame)
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("titleLabel")
            panel_layout.addWidget(title_label)
        return panel_frame, panel_layout
    
    #Creamos un panel que muestra el uso de memoria RAM en la simulación
    def crear_panel_memoria(self):
        panel, layout = self._crear_panel_base("Memoria Usada")
        self.barra_memoria = QProgressBar()
        self.barra_memoria.setTextVisible(False)
        self.label_memoria = QLabel("0 MB / 1024 MB")
        layout.addWidget(self.barra_memoria)
        layout.addWidget(self.label_memoria)
        return panel

    #Formulario podriamos decir
    #Creamos el panel que gestione procesos y controles de la simulación
    def crear_panel_proceso_y_controles(self):
        panel, layout = self._crear_panel_base("Gestión de Procesos")
        self.nombre_input = QLineEdit(placeholderText="Nombre del proceso")
        self.memoria_input = QLineEdit(placeholderText="Memoria en MB")
        self.memoria_input.setValidator(QIntValidator(1, 100000, self))
        self.duracion_input = QLineEdit(placeholderText="Duración en segundos")
        self.duracion_input.setValidator(QIntValidator(1, 100000, self))
        self.btn_crear = QPushButton("Crear Proceso")
        self.btn_crear.clicked.connect(self.crear_proceso)
        
        self.btn_pausa_reanudar = QPushButton("Pausar Simulación")
        self.btn_pausa_reanudar.setObjectName("controlButton")
        self.btn_pausa_reanudar.clicked.connect(self.toggle_pausa)
        
        self.btn_reiniciar = QPushButton("Reiniciar Simulación")
        self.btn_reiniciar.setObjectName("dangerButton")
        self.btn_reiniciar.clicked.connect(self.simulador.reiniciar_simulacion)

        for widget in [self.nombre_input, self.memoria_input, self.duracion_input, self.btn_crear, self.btn_pausa_reanudar, self.btn_reiniciar]:
            layout.addWidget(widget)
        
        layout.addStretch(1)
        return panel



    def crear_panel_carga_sistema(self):
        # MODIFICACIÓN: Se cambia a un layout horizontal.
        container_layout = QHBoxLayout()
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Uso de Memoria")
        title_label.setObjectName("titleNoCard")
        
        self.progress_memoria = CircularProgressBar()

        # Se añaden los widgets de izquierda a derecha.
        container_layout.addWidget(title_label)
        container_layout.addWidget(self.progress_memoria)
        
        return container_layout

    #Crea un panel vertical que muestre tres estadísticas 
    def crear_panel_estadisticas(self):
        panel, layout = self._crear_panel_base("Estadísticas")
        
        self.label_ejecutados = QLabel("0")
        self.label_memoria_prom = QLabel("0 MB")
        self.label_tiempo_prom = QLabel("0 s")

        #Agregamos pares de etiquetas: descripción y valor
        for value_label, text in [(self.label_ejecutados, "Procesos ejecutados"), 
                                    (self.label_memoria_prom, "RAM promedio utilizada"), 
                                    (self.label_tiempo_prom, "Tiempo promedio ejecución")]:
            #Textos descriptivos y estilos  
            text_label = QLabel(text)
            text_label.setObjectName("statLabel")
            value_label.setObjectName("statValue")
            layout.addWidget(text_label)
            layout.addWidget(value_label)
        
        #Rellenamos el espacio en blanco para que las estadísticas queden arriba
        layout.addStretch(1)
        self.right_column.addWidget(panel)

    #Para crear el panel que contiene las tablas QTableWidget
    def _crear_tabla(self, headers, parent_layout, title):
        panel, layout = self._crear_panel_base(title)
        table = QTableWidget()
        #Se agrega esta línea para quitar las líneas de la cuadrícula
        table.setShowGrid(False) 
        #Se agrega esta línea para ocultar el encabezado vertical (numeración de filas)
        table.verticalHeader().setVisible(False) 
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        #Agregamos la tabla al panel
        parent_layout.addWidget(panel)
        #Devolvemos la tabla para usarla en otros métodos
        return table

    #Creamos la tabla para mostrar el proceso de cola de espera
    def crear_tabla_cola(self):
        #Añadimos "Accion" a los encabezados
        self.tabla_cola = self._crear_tabla(["PID", "Nombre", "Memoria", "Duración", "Acción"], self.center_column, "Cola de Espera")

    #Creamos la tabla para los procesos de ejecución
    def crear_tabla_ejecucion(self):
        #Añadimos "Accion" a los encabezados
        self.tabla_ejecucion = self._crear_tabla(["PID", "Nombre", "Memoria", "Restante", "Acción"], self.center_column, "En Ejecución")
        
    #Creamos la tabla que muestra los procesos terminados    
    def crear_tabla_terminados(self):
        self.tabla_terminados = self._crear_tabla(["PID", "Nombre", "Memoria", "Duración"], self.right_column, "Procesos Terminados")
        #Ajustamos las columnas al contenido para evitar cortes de texto
        self.tabla_terminados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    #Leemos los datos de los campos de entrada, validamos la información y creamos un nuevo objeto proceso para añadirlo al simulador
    def crear_proceso(self):
        #Ingresamos los valores
        try:
            nombre = self.nombre_input.text().strip() 
            memoria_str = self.memoria_input.text().strip()
            duracion_str = self.duracion_input.text().strip()
            
            #Validamos que no sean datos vacios
            if not nombre:
                dialog = CustomErrorDialog("El campo 'Nombre del proceso' no puede estar vacío.", self)
                dialog.exec()
                return
            if not memoria_str:
                dialog = CustomErrorDialog("El campo 'Memoria en MB' no puede estar vacío.", self)
                dialog.exec()
                return
            if not duracion_str:
                dialog = CustomErrorDialog("El campo 'Duración en segundos' no puede estar vacío.", self)
                dialog.exec()
                return

            #Conversión a enteros
            memoria = int(memoria_str)
            duracion = int(duracion_str)

            #Validamos que no exceda la RAM disponible 
            if memoria > self.simulador.gestor_memoria.ram_total:
                dialog = CustomErrorDialog(
                    f"El proceso excede la RAM total disponible ({self.simulador.gestor_memoria.ram_total:.0f} MB).",
                    self
                )
                dialog.exec()
                return
            
            #Validamos que sean números positivos
            if memoria <= 0 or duracion <= 0:
                dialog = CustomErrorDialog(
                    "La Memoria y Duración deben ser valores numéricos positivos.",
                    self
                )
                dialog.exec()
                return

            #Generamos un nuevo identificador único para el proceso
            self.simulador.proceso_id_counter += 1
            pid = f"P{self.simulador.proceso_id_counter}"
            
            #Creamos un objeto Proceso y lo registramos en el simulador 
            nuevo_proceso = Proceso(pid, nombre, memoria, duracion)
            self.simulador.agregar_proceso(nuevo_proceso)
            
            #limpieza de los campos de entrada
            for input_field in [self.nombre_input, self.memoria_input, self.duracion_input]:
                input_field.clear()
        except ValueError:#Para el manejo de errores
            dialog = CustomErrorDialog(
                "Por favor, ingresa valores numéricos válidos para Memoria y Duración.",
                self
            )
            dialog.exec()

    #Cambiamos el estado del simulador
    def toggle_pausa(self):
        if self.simulador.pausado:#Si esta en ejecución, lo pausa
            self.simulador.reanudar_simulacion()
            self.btn_pausa_reanudar.setText("Pausar Simulación")#Actualizamos el texto del boton
        else:
            self.simulador.pausar_simulacion()#Si esta en pausa lo reanuda
            self.btn_pausa_reanudar.setText("Reanudar Simulación")#Actualizamos el texto del boton

    #Cancelamos el proceso específico desde la UI
    def cancelar_proceso_ui(self, pid):
        #Le decimos al simulador que elimine el proceso pasandole su pid
        self.simulador.cancelar_proceso(pid)
        self.actualizar_ui() #Actualizamos la UI

    #Actualizamos todos los elementos visuales con la información más reciente
    def actualizar_ui(self):
        #Datos de uso de memoria
        mem_usada, ram_total = self.simulador.obtener_uso_memoria()
        self.label_memoria.setText(f"{mem_usada:.0f} MB / {ram_total:.0f} MB")
        self.barra_memoria.setMaximum(int(ram_total))
        self.barra_memoria.setValue(int(mem_usada))

        #Porcentaje de memoria para la barra circular
        uso_memoria_porc = (mem_usada / ram_total) * 100 if ram_total > 0 else 0
        self.progress_memoria.setValue(uso_memoria_porc)

        #Actualizamos la tabla de ejecución añadiendo el boton cancelar
        self._actualizar_tabla(
            self.tabla_ejecucion, 
            self.simulador.procesos_en_ejecucion.values(), 
            lambda p: [p.pid, p.nombre, f"{p.memoria_mb} MB", f"{int(p.tiempo_restante)}s"],
            add_cancel_button=True #Habilitamos el boton cancelar
        )

        #Actualizamos la tabla de cola añadiendo el boton cancelar
        self._actualizar_tabla(
            self.tabla_cola, 
            self.simulador.cola_espera, 
            lambda p: [p.pid, p.nombre, f"{p.memoria_mb} MB", f"{p.duracion_s}s"],
            add_cancel_button=True #Habilitamos el boton cancelar
        )

        #Actualizamos la tabla de procesos terminados
        self._actualizar_tabla(self.tabla_terminados, reversed(self.simulador.procesos_terminados), lambda p: [p.pid, p.nombre, f"{p.memoria_mb} MB", f"{p.duracion_s}s"])

        #Actualizamos las estadisticas
        stats = self.simulador.obtener_estadisticas()
        self.label_ejecutados.setText(f"{stats['procesos_ejecutados']}")
        self.label_memoria_prom.setText(f"{stats['memoria_usada_promedio']:.0f} MB")
        self.label_tiempo_prom.setText(f"{stats['tiempo_vida_promedio']:.1f} s")

    #Llenamos la tabla QTableWidget con nuevos datos
    def _actualizar_tabla(self, table, data, row_formatter, add_cancel_button=False):
        #Para evitar problemas de concurrencia
        with self.simulador.lock:
            items = list(data)
        
        #Limpiamos la tabla
        table.setRowCount(0)
        for item in items:
            #Convertimos el objeto en listas de datos de fila
            row_data = row_formatter(item)
            row = table.rowCount()
            table.insertRow(row)
            for col, text in enumerate(row_data):
                table_item = QTableWidgetItem(str(text))
                table_item.setTextAlignment(Qt.AlignCenter)#Centramos el texto
                table.setItem(row, col, table_item)
            
            if add_cancel_button:#Añade el boton cancelar
                cancel_button = QPushButton("Cancelar")
                cancel_button.setStyleSheet("""
                    QPushButton { 
                        background-color: #ef4444; 
                        color: #ffffff; 
                        font-weight: bold; 
                        border-radius: 8px; 
                        padding: 5px 10px; 
                        border: none; 
                        outline: none;
                    }
                    QPushButton:hover { 
                        background-color: #dc2626; 
                    }
                """)
                #El botón estará en la última columna
                button_col = table.columnCount() - 1 
                #Conectamos el boton a la funcion de cancelación, pasando el PID del proceso
                cancel_button.clicked.connect(lambda _, p=item.pid: self.cancelar_proceso_ui(p))
                table.setCellWidget(row, button_col, cancel_button)

    #Evento ejecutado al cerrar la ventana principal
    def closeEvent(self, event):
        #Detenemos la ejecución para evitar hilos activos
        self.simulador.ejecutando = False
        super().closeEvent(event)

if __name__ == '__main__':
    #Punto de entrada de la aplicación PyQt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())