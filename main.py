import sys
#Importamos la Clase QApplicationpara gestionarla  la aplicacion
from PySide6.QtWidgets import QApplication
from gui import MainWindow

if __name__ == "__main__":
    # La aplicación se crea como antes
    app = QApplication(sys.argv)
    
    # Creamos la ventana principal (que ahora contiene los estilos)
    window = MainWindow()
    window.show()
    
    # Ejecutamos la aplicación
    sys.exit(app.exec())
