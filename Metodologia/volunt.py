import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF

# Conectar a la base de datos MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Tu usuario de MySQL
        password="",  # Tu contraseña de MySQL
        database="control_gastos"
    )

# Función para agregar una transacción
def add_transaction():
    fecha = fecha_entry.get()
    tipo = tipo_combobox.get()
    monto = monto_entry.get()
    categoria = categoria_entry.get()
    descripcion = descripcion_entry.get()
    
    if fecha and tipo and monto and categoria:
        try:
            monto = float(monto)
            conn = connect_db()
            cursor = conn.cursor()
            (fecha, tipo, monto, categoria, descripcion)
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Transacción agregada exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar transacción: {e}")
    else:
        messagebox.showwarning("Input Error", "Por favor ingrese todos los campos.")

# Función para ver resumen de los gastos del mes
def view_monthly_report():
    month = month_entry.get()
    year = year_entry.get()
    
    if not month or not year:
        messagebox.showwarning("Input Error", "Por favor ingrese el mes y el año.")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo, SUM(monto) 
        FROM transacciones 
        WHERE MONTH(fecha) = %s AND YEAR(fecha) = %s 
        GROUP BY tipo
    """, (month, year))
    result = cursor.fetchall()
    
    ingresos = 0
    gastos = 0
    
    for row in result:
        if row[0] == "Ingreso":
            ingresos = row[1]
        elif row[0] == "Gasto":
            gastos = row[1]
    
    cursor.close()
    conn.close()
    
    messagebox.showinfo("Resumen Mensual", f"Ingresos: {ingresos}\nGastos: {gastos}")

    # Mostrar gráfico
    show_expense_chart(ingresos, gastos)

# Función para mostrar gráfico de distribución de gastos
def show_expense_chart(ingresos, gastos):
    categories = ['Ingresos', 'Gastos']
    values = [ingresos, gastos]

    fig, ax = plt.subplots()
    ax.bar(categories, values, color=['green', 'red'])

    ax.set_ylabel('Monto')
    ax.set_title('Distribución de Ingresos y Gastos')

    # Mostrar gráfico en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Función para generar reporte PDF
def generate_pdf_report():
    month = month_entry.get()
    year = year_entry.get()
    
    if not month or not year:
        messagebox.showwarning("Input Error", "Por favor ingrese el mes y el año.")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo, categoria, SUM(monto) 
        FROM transacciones 
        WHERE MONTH(fecha) = %s AND YEAR(fecha) = %s 
        GROUP BY tipo, categoria
    """, (month, year))
    result = cursor.fetchall()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Reporte de Gastos - {month}/{year}", ln=True, align="C")
    
    total_ingresos = 0
    total_gastos = 0
    
    for row in result:
        tipo = row[0]
        categoria = row[1]
        monto = row[2]
        
        if tipo == "Ingreso":
            total_ingresos += monto
        elif tipo == "Gasto":
            total_gastos += monto
        
        pdf.cell(200, 10, txt=f"{tipo} - {categoria}: {monto}", ln=True)

    pdf.cell(200, 10, txt=f"Total Ingresos: {total_ingresos}", ln=True)
    pdf.cell(200, 10, txt=f"Total Gastos: {total_gastos}", ln=True)
    
    pdf.output("reporte_gastos.pdf")
    cursor.close()
    conn.close()

    messagebox.showinfo("Reporte Generado", "El reporte se ha generado correctamente.")

# Crear la ventana de la aplicación
root = tk.Tk()
root.title("Control de Gastos Personales")

# Campos de entrada para agregar transacciones
fecha_entry = tk.Entry(root, width=40)
fecha_entry.pack(pady=5)
fecha_entry.insert(0, "YYYY-MM-DD")

tipo_combobox = ttk.Combobox(root, values=["Ingreso", "Gasto"], width=38)
tipo_combobox.set("Ingreso")
tipo_combobox.pack(pady=5)

monto_entry = tk.Entry(root, width=40)
monto_entry.pack(pady=5)
monto_entry.insert(0, "Monto")

categoria_entry = tk.Entry(root, width=40)
categoria_entry.pack(pady=5)
categoria_entry.insert(0, "Categoría")

descripcion_entry = tk.Entry(root, width=40)
descripcion_entry.pack(pady=5)
descripcion_entry.insert(0, "Descripción")

# Botón para agregar transacción
add_button = tk.Button(root, text="Agregar Transacción", command=add_transaction)
add_button.pack(pady=5)

# Campos de entrada para reporte mensual
month_entry = tk.Entry(root, width=10)
month_entry.pack(pady=5)
month_entry.insert(0, "Mes (1-12)")

year_entry = tk.Entry(root, width=10)
year_entry.pack(pady=5)
year_entry.insert(0, "Año")

# Botón para generar reporte mensual
report_button = tk.Button(root, text="Ver Resumen Mensual", command=view_monthly_report)
report_button.pack(pady=5)

# Marco para mostrar el gráfico
graph_frame = tk.Frame(root)
graph_frame.pack(pady=10)

# Botón para generar el reporte en PDF
pdf_button = tk.Button(root, text="Generar Reporte PDF", command=generate_pdf_report)
pdf_button.pack(pady=5)

# Iniciar la aplicación
root.mainloop()