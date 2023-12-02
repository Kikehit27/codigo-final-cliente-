import socket
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class ArduinoClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Arduino - Cliente")

        # Variables
        self.host_var = tk.StringVar()
        self.host_var.set("192.168.65.171")  # Valor predeterminado para el host
        self.distance_var = tk.StringVar()
        self.speed_var = tk.StringVar()

        # Configuración del cliente
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Hilo para la lectura continua de distancia
        self.read_distance_thread = None

        # Crear elementos de la interfaz
        self.create_tabs()

    def create_tabs(self):
        # Crear un contenedor de pestañas
        notebook = ttk.Notebook(self.root)

        # Pestaña de conexión al servidor
        connection_tab = ttk.Frame(notebook)
        self.create_connection_tab(connection_tab)
        notebook.add(connection_tab, text='Conexión')

        # Pestaña de control de velocidad
        speed_tab = ttk.Frame(notebook)
        self.create_speed_tab(speed_tab)
        notebook.add(speed_tab, text='Control de Velocidad')

        notebook.pack(expand=1, fill="both")

    def create_connection_tab(self, tab):
        # Cuadro de entrada para el host
        host_label = ttk.Label(tab, text="Host:")
        host_entry = ttk.Entry(tab, textvariable=self.host_var)
        host_label.pack()
        host_entry.pack(pady=10)

        # Botón para conectar al servidor
        connect_button = ttk.Button(tab, text="Conectar al Servidor", command=self.connect_to_server)
        connect_button.pack(pady=10)

        # Etiqueta para mostrar la distancia del sensor
        distance_label = ttk.Label(tab, text="Distancia del sensor:")
        distance_value_label = ttk.Label(tab, textvariable=self.distance_var)
        distance_label.pack()
        distance_value_label.pack()

    def create_speed_tab(self, tab):
        # Barra de velocidad para controlar la velocidad de los motores
        speed_label = ttk.Label(tab, text="Velocidad de los motores:")
        self.speed_scale = ttk.Scale(tab, from_=0, to=255, orient="horizontal", command=self.update_speed)
        speed_label.pack()
        self.speed_scale.pack()

    def connect_to_server(self):
        # Conectar al servidor utilizando la dirección del host
        host = self.host_var.get()
        try:
            self.client_socket.connect((host, 12345))  # Cambia el puerto si es necesario
            messagebox.showinfo("Conexión Exitosa", "Conexión establecida correctamente con el servidor.")
            # Iniciar la lectura continua de distancia en un hilo separado
            self.read_distance_thread = threading.Thread(target=self.read_distance_continuous)
            self.read_distance_thread.start()
        except socket.error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor: {e}")

    def update_speed(self, value):
        # Enviar la velocidad al servidor cuando la barra se ajusta
        try:
            speed = int(value)
            print(f"Enviando velocidad al servidor: S{speed}")
            self.client_socket.send(f'S{speed}'.encode())
        except (ValueError, socket.error) as e:
            print(f"Error al actualizar la velocidad: {e}")

    def read_distance_continuous(self):
        # Función para leer continuamente la distancia y reaccionar
        try:
            while True:
                self.client_socket.send(b'M')
                response = self.client_socket.recv(1023).decode().strip()
                
                if not response:
                    print("No se recibieron datos del servidor.")
                    break

                print(f"Respuesta recibida (continuo): {response}")

                try:
                    distance = float(response)
                    self.distance_var.set(f"Distancia: {distance} cm")
                    # Reaccionar a la distancia
                    self.react_to_distance(distance)
                except ValueError:
                    print("La respuesta no es un número válido.")
                
                self.root.update()  # Actualizar la interfaz gráfica
                time.sleep(1)  # Esperar 1 segundo entre lecturas
        except socket.error as e:
            print(f'Error en la lectura continua de distancia: {e}')
            messagebox.showerror("Error de Conexión", "Se perdió la conexión con el servidor.")

    def react_to_distance(self, distance):
        try:
            print(f"Distancia recibida: {distance}")
            # Puedes trabajar directamente con la variable 'distance'
            # Ajusta este umbral según tus necesidades
            if distance < 10:
                print("¡Objeto cercano! Activar motores.")
                # Agrega aquí la lógica para activar los motores (por ejemplo, enviar comando al servidor)
            else:
                print("No se detecta un objeto cercano. Deteniendo motores.")
                # Agrega aquí la lógica para detener los motores (por ejemplo, enviar comando al servidor)
        except ValueError:
            print("Error al convertir la distancia a un número.")

if __name__ == "__main__":
    root = tk.Tk()
    client_app = ArduinoClientGUI(root)
    root.mainloop()
