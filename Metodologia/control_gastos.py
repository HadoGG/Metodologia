import tkinter as tk
from tkinter import messagebox
import mysql.connector
import matplotlib.pyplot as plt
from fpdf import FPDF
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Conexión a la base de datos MySQL
def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="control_gastos"
    )

# Función para guardar transacciones
def guardar_transaccion():
    descripcion = entry_descripcion.get()
    monto = entry_monto.get()
    categoria = combo_categoria.get()  # Aquí usamos combo_categoria.get() correctamente

    if descripcion == "" or monto == "" or categoria == "":
        messagebox.showerror("Error", "Todos los campos deben ser completados")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        query = "INSERT INTO transacciones (descripcion, monto, categoria) VALUES (%s, %s, %s)"
        cursor.execute(query, (descripcion, monto, categoria))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Transacción registrada correctamente")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Hubo un problema con la base de datos: {err}")

# Función para mostrar los gastos mensuales
def ver_resumen():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        query = "SELECT categoria, SUM(monto) FROM transacciones GROUP BY categoria"
        cursor.execute(query)
        categorias = cursor.fetchall()
        conn.close()

        # Datos para los gráficos
        categorias_names = [row[0] for row in categorias]
        categorias_sums = [row[1] for row in categorias]

        # Crear gráfico de barras
        fig, ax = plt.subplots()
        ax.bar(categorias_names, categorias_sums)
        ax.set_title("Distribución de gastos por categoría")
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Monto")

        # Mostrar el gráfico en la interfaz
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Hubo un problema con la base de datos: {err}")

# Función para generar reporte en PDF
def generar_reporte():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        query = "SELECT descripcion, monto, categoria FROM transacciones"
        cursor.execute(query)
        transacciones = cursor.fetchall()
        conn.close()

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte de Gastos", ln=True, align='C')

        for transaccion in transacciones:
            pdf.cell(200, 10, txt=f"Descripción: {transaccion[0]}, Monto: {transaccion[1]}, Categoría: {transaccion[2]}", ln=True)

        # Guardar el archivo PDF
        pdf.output("reporte_gastos.pdf")
        messagebox.showinfo("Éxito", "Reporte generado exitosamente")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Hubo un problema con la base de datos: {err}")

# Crear la interfaz gráfica
ventana = tk.Tk()
ventana.title("Control de Gastos Personales")
ventana.geometry("800x600")

# Frame para ingresar transacciones
frame_ingreso = tk.Frame(ventana)
frame_ingreso.pack(pady=20)

tk.Label(frame_ingreso, text="Descripción:").grid(row=0, column=0)
entry_descripcion = tk.Entry(frame_ingreso)
entry_descripcion.grid(row=0, column=1)

tk.Label(frame_ingreso, text="Monto:").grid(row=1, column=0)
entry_monto = tk.Entry(frame_ingreso)
entry_monto.grid(row=1, column=1)

tk.Label(frame_ingreso, text="Categoría:").grid(row=2, column=0)
combo_categoria = tk.StringVar()
combo_categoria.set("Alimentos")  # valor por defecto
categorias = ["Alimentos", "Transporte", "Vivienda", "Salud", "Entretenimiento"]
combo_categoria_menu = tk.OptionMenu(frame_ingreso, combo_categoria, *categorias)
combo_categoria_menu.grid(row=2, column=1)

tk.Button(frame_ingreso, text="Guardar Transacción", command=guardar_transaccion).grid(row=3, columnspan=2)

# Frame para mostrar los gráficos
frame_grafico = tk.Frame(ventana)
frame_grafico.pack(pady=20)

tk.Button(ventana, text="Ver Resumen de Gastos", command=ver_resumen).pack(pady=10)

# Frame para generar reporte PDF
tk.Button(ventana, text="Generar Reporte PDF", command=generar_reporte).pack(pady=10)

# Ejecutar la interfaz
ventana.mainloop()
