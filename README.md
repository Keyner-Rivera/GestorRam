Simulador de Gestión de Memoria RAM
Este proyecto es un simulador de escritorio desarrollado en Python con PySide6 que visualiza de manera interactiva cómo un sistema operativo gestiona los procesos en la memoria RAM. La aplicación permite crear, ejecutar y monitorear procesos en tiempo real.

Características
Visualización en Tiempo Real: Observa cómo los procesos son asignados a la memoria, se ejecutan y finalizan.

Creación Dinámica de Procesos: Añade procesos personalizados definiendo su nombre, consumo de memoria (MB) y duración (segundos).

Gestión de Cola de Espera: Los procesos que no caben en la RAM esperan en una cola hasta que se libere espacio suficiente.

Estadísticas del Sistema: Monitorea el uso de la memoria, el número de procesos completados y el tiempo promedio de ejecución.

Controles de Simulación: Pausa, reanuda y reinicia la simulación para analizar el comportamiento del sistema en detalle.

Cancelación de Procesos: Cancela procesos individuales, ya sea en la cola de espera o en plena ejecución, con un diálogo de confirmación para evitar acciones accidentales.

Instalación y Ejecución
Para ejecutar este proyecto en tu máquina local, sigue estos sencillos pasos.

1. Prerrequisitos
Asegúrate de tener instalado Python 3.8 o una versión superior. Puedes verificar tu versión abriendo una terminal y ejecutando:

python --version

2. Clonar el Repositorio
Abre tu terminal, navega a la carpeta donde quieras guardar el proyecto y clona el repositorio:

git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
cd tu-repositorio

Nota: No olvides reemplazar tu-usuario/tu-repositorio con la URL real de tu repositorio en GitHub.

3. Instalar Dependencias
La única dependencia principal es PySide6. Instálala usando el gestor de paquetes pip:

pip install pyside6

4. Ejecutar la Aplicación
Una vez instaladas las dependencias, puedes iniciar la aplicación ejecutando el archivo main.py (o el nombre que le hayas dado a tu archivo principal):

python main.py

Tecnologías Utilizadas
Python: El lenguaje de programación principal del proyecto.

PySide6 (Qt for Python): El framework utilizado para construir la interfaz gráfica de usuario.

Threading: Para ejecutar la lógica de la simulación en un hilo separado, asegurando que la interfaz gráfica se mantenga fluida y receptiva en todo momento.
