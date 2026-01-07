#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class ConversorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Txt2Img")
        # Ventana compacta
        self.root.geometry("400x300")
        self.root.configure(bg="#2E2E2E") 

        # --- RUTA DE SALIDA ---
        self.ruta_salida = os.path.expanduser("~/Descargas")

        # --- ÁREA DE TEXTO ---
        # Height=8 mantiene la ventana pequeña
        self.texto_input = scrolledtext.ScrolledText(root, wrap=tk.NONE, bg="#1E1E1E", fg="#D4D4D4", 
            font=("Consolas", 10), insertbackground="white", 
            height=8) 
        self.texto_input.pack(expand=True, fill="both", padx=10, pady=10)
        self.texto_input.focus_set()

        # --- BOTONES ---
        panel_bottom = tk.Frame(root, bg="#2E2E2E", pady=10)
        panel_bottom.pack(fill="x")

        # Botón Borrar
        btn_borrar = tk.Button(panel_bottom, text="Borrar", command=self.borrar_texto,
            bg="#A63434", fg="white", font=("Arial", 9, "bold"), width=8, relief="flat")
        btn_borrar.pack(side="left", padx=10)

        # Botón Convertir
        btn_convertir = tk.Button(panel_bottom, text="CONVERTIR", command=self.convertir,
            bg="#2A8C55", fg="white", font=("Arial", 9, "bold"), width=15, relief="flat")
        btn_convertir.pack(side="right", padx=10)

    def borrar_texto(self):
        self.texto_input.delete("1.0", tk.END)

    def obtener_fuente(self, tamano):
        fuentes_linux = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
            "arial.ttf"
        ]
        for ruta in fuentes_linux:
            if os.path.exists(ruta):
                return ImageFont.truetype(ruta, tamano)
        # Fallback si no encuentra ninguna
        return ImageFont.load_default()

    def convertir(self):
        contenido = self.texto_input.get("1.0", tk.END)
        
        # Validación: Si solo hay espacios o está vacío
        if len(contenido.strip()) == 0:
            messagebox.showwarning("Vacío", "El cuadro de texto está vacío.")
            return

        # --- CONFIGURACIÓN DE ALTA CALIDAD ---
        font_size = 48 
        padding = 50    

        try:
            # 1. Preparar recursos
            font = self.obtener_fuente(font_size)
            dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            
            # Limpiar líneas vacías finales que agrega el widget de texto
            lines = contenido.split("\n")
            if lines and not lines[-1].strip(): lines.pop()
            
            texto_procesado = "\n".join(lines)
            
            # 2. Calcular dimensiones exactas
            left, top, right, bottom = dummy_draw.textbbox((0, 0), texto_procesado, font=font)
            w = (right - left) + (padding * 2)
            h = (bottom - top) + (padding * 2)

            # 3. Dibujar Imagen (Fondo oscuro #1E1E1E)
            img = Image.new('RGB', (int(w), int(h)), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            draw.text((padding, padding), texto_procesado, font=font, fill=(220, 220, 220))

            # 4. Guardar archivo
            if not os.path.exists(self.ruta_salida):
                os.makedirs(self.ruta_salida)

            # Formato de nombre: imgtxt_AÑO MES DÍA_HORA MIN SEGUNDO
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"imgtxt_{timestamp}.jpg"
            ruta_completa = os.path.join(self.ruta_salida, nombre_archivo)

            # Guardar con máxima calidad JPG
            img.save(ruta_completa, "JPEG", quality=100, optimize=True, subsampling=0)
            
            messagebox.showinfo("Listo", f"Guardado:\n{nombre_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorApp(root)
    root.mainloop()