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
        self.root.geometry("400x300")
        self.root.configure(bg="#2E2E2E")

        # --- CONFIGURACIÓN DE RUTA Y COLORES ---
        self.ruta_salida = os.path.expanduser("~/Descargas")
        self.placeholder = "Coloca tu texto aqui"
        self.color_placeholder = "#888888"
        self.color_texto_normal = "#D4D4D4"

        # --- ÁREA DE TEXTO ---
        self.texto_input = scrolledtext.ScrolledText(root, wrap=tk.NONE, bg="#1E1E1E", 
            fg=self.color_placeholder, # Inicia con color de placeholder
            font=("Consolas", 10), insertbackground="white", 
            height=8)
        self.texto_input.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Insertar placeholder inicial y configurar eventos
        self.texto_input.insert("1.0", self.placeholder)
        self.texto_input.bind("<FocusIn>", self._limpiar_placeholder)
        self.texto_input.bind("<FocusOut>", self._restaurar_placeholder)

        # --- BOTONES ---
        panel_bottom = tk.Frame(root, bg="#2E2E2E", pady=10)
        panel_bottom.pack(fill="x")

        btn_borrar = tk.Button(panel_bottom, text="Borrar", command=self.borrar_texto,
            bg="#A63434", fg="white", font=("Arial", 9, "bold"), width=8, relief="flat")
        btn_borrar.pack(side="left", padx=10)

        btn_convertir = tk.Button(panel_bottom, text="CONVERTIR", command=self.convertir,
            bg="#2A8C55", fg="white", font=("Arial", 9, "bold"), width=15, relief="flat")
        btn_convertir.pack(side="right", padx=10)

    # --- LÓGICA DEL PLACEHOLDER ---
    def _limpiar_placeholder(self, event):
        """Elimina el texto fantasma cuando el usuario hace clic para escribir."""
        contenido_actual = self.texto_input.get("1.0", tk.END).strip()
        if contenido_actual == self.placeholder:
            self.texto_input.delete("1.0", tk.END)
        self.texto_input.config(fg=self.color_texto_normal)

    def _restaurar_placeholder(self, event):
        """Reinstaura el texto fantasma si el usuario deja el campo vacío."""
        contenido_actual = self.texto_input.get("1.0", tk.END).strip()
        if not contenido_actual:
            self.texto_input.insert("1.0", self.placeholder)
            self.texto_input.config(fg=self.color_placeholder)

    def borrar_texto(self):
        """Limpia el texto y maneja inteligentemente el placeholder."""
        self.texto_input.delete("1.0", tk.END)
        
        # Si el foco NO está en el widget, ponemos el placeholder
        if self.root.focus_get() != self.texto_input:
            self._restaurar_placeholder(None)
        else:
            # Si el usuario está 'dentro', dejamos listo para escribir con color normal
            self.texto_input.config(fg=self.color_texto_normal)

    def obtener_fuente(self, tamano):
        """Busca una fuente monoespaciada en el sistema."""
        fuentes_linux = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
            "arial.ttf"
        ]
        for ruta in fuentes_linux:
            if os.path.exists(ruta):
                return ImageFont.truetype(ruta, tamano)
        return ImageFont.load_default()

    def convertir(self):
        """Procesa el texto y lo guarda como imagen JPG."""
        contenido = self.texto_input.get("1.0", tk.END).strip()
        
        # No permitir conversión si está vacío o si es solo el placeholder
        if not contenido or contenido == self.placeholder:
            messagebox.showwarning("Vacío", "El cuadro de texto está vacío.")
            return

        font_size = 48
        padding = 50

        try:
            font = self.obtener_fuente(font_size)
            dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            
            lines = contenido.split("\n")
            if lines and not lines[-1].strip(): lines.pop()
            texto_procesado = "\n".join(lines)
            
            left, top, right, bottom = dummy_draw.textbbox((0, 0), texto_procesado, font=font)
            w = (right - left) + (padding * 2)
            h = (bottom - top) + (padding * 2)

            img = Image.new('RGB', (int(w), int(h)), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            draw.text((padding, padding), texto_procesado, font=font, fill=(220, 220, 220))

            if not os.path.exists(self.ruta_salida):
                os.makedirs(self.ruta_salida)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"imgtxt_{timestamp}.jpg"
            ruta_completa = os.path.join(self.ruta_salida, nombre_archivo)

            img.save(ruta_completa, "JPEG", quality=100, optimize=True, subsampling=0)
            messagebox.showinfo("Listo", f"Guardado:\n{nombre_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorApp(root)
    root.mainloop()