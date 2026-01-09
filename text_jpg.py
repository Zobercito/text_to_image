#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk  # Añadido ImageTk
import os
from datetime import datetime

class ConversorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Txt2Img")
        self.root.geometry("400x320")
        self.root.configure(bg="#2E2E2E")

        # --- CONFIGURACIÓN DE RUTA Y COLORES ---
        self.ruta_salida = os.path.expanduser("~/Descargas")
        self.placeholder = "Coloca tu texto aqui"
        self.color_placeholder = "#888888"
        self.color_texto_normal = "#D4D4D4"

        # --- ÁREA DE TEXTO CON SCROLLS DINÁMICOS ---
        self.container_texto = tk.Frame(root, bg="#1E1E1E")
        self.container_texto.pack(expand=True, fill="both", padx=10, pady=(10, 0))
        
        self.container_texto.grid_rowconfigure(0, weight=1)
        self.container_texto.grid_rowconfigure(1, weight=0, minsize=16)
        self.container_texto.grid_columnconfigure(0, weight=1)
        self.container_texto.grid_columnconfigure(1, weight=0, minsize=16)

        self.v_scrollbar = tk.Scrollbar(self.container_texto, orient=tk.VERTICAL)
        self.h_scrollbar = tk.Scrollbar(self.container_texto, orient=tk.HORIZONTAL)
        self.esquina = tk.Frame(self.container_texto, bg="#2E2E2E", width=16, height=16)

        self.texto_input = tk.Text(self.container_texto, wrap=tk.NONE, bg="#1E1E1E", 
            fg=self.color_placeholder,
            font=("Consolas", 10), insertbackground="white", 
            height=8, undo=True,
            highlightthickness=1, highlightbackground="#444444",
            yscrollcommand=self._gestionar_vbar,
            xscrollcommand=self._gestionar_hbar)
        
        self.texto_input.grid(row=0, column=0, sticky="nsew")
        
        self.v_scrollbar.config(command=self.texto_input.yview)
        self.h_scrollbar.config(command=self.texto_input.xview)

        self.texto_input.insert("1.0", self.placeholder)
        self.texto_input.bind("<FocusIn>", self._limpiar_placeholder)
        self.texto_input.bind("<FocusOut>", self._restaurar_placeholder)

        # --- BOTONES CENTRADOS ---
        panel_bottom = tk.Frame(root, bg="#2E2E2E")
        panel_bottom.pack(fill="x", pady=5)

        self.centro_botones = tk.Frame(panel_bottom, bg="#2E2E2E")
        self.centro_botones.pack(anchor="center")

# Configuración del icono del botón
        self.icon_config = None
        ruta_script = os.path.dirname(os.path.abspath(__file__))
        ruta_icono = os.path.join(ruta_script, "assets", "config_icon.png")
        
        try:
            img_original = Image.open(ruta_icono)
            
            try:
                filtro = Image.Resampling.LANCZOS
            except AttributeError:
                filtro = Image.LANCZOS 
                
            img_resizada = img_original.resize((18, 18), filtro)
            self.icon_config = ImageTk.PhotoImage(img_resizada)
            
            # Ajuste de dimensiones y eliminación de bordes extra
            btn_config = tk.Button(
                self.centro_botones, 
                image=self.icon_config, 
                bg="#444444", 
                relief="flat", 
                width=26,              # Ancho reducido para estar más pegado
                height=26,             # Alto reducido para estar más pegado
                borderwidth=0,         # Elimina el borde físico
                highlightthickness=0,  # Elimina el marco blanco de selección
                padx=0,                # Elimina espacio interno horizontal
                pady=0                 # Elimina espacio interno vertical
            )
        except Exception as e:
            print(f"DEBUG: No se pudo cargar el icono: {e}")
            btn_config = tk.Button(self.centro_botones, text="⚙", 
                bg="#444444", fg="white", font=("Arial", 9, "bold"), width=5, relief="flat")

        btn_config.pack(side="left", padx=10)

        btn_borrar = tk.Button(self.centro_botones, text="BORRAR", command=self.borrar_texto,
            bg="#A63434", fg="white", font=("Arial", 9, "bold"), width=8, relief="flat")
        btn_borrar.pack(side="left", padx=10)

        btn_abrir = tk.Button(self.centro_botones, text="ABRIR ARCHIVO", command=self.abrir_archivo,
            bg="#3465A4", fg="white", font=("Arial", 9, "bold"), width=12, relief="flat")
        btn_abrir.pack(side="left", padx=10)

        btn_convertir = tk.Button(self.centro_botones, text="CONVERTIR", command=self.convertir,
            bg="#2A8C55", fg="white", font=("Arial", 9, "bold"), width=8, relief="flat")
        btn_convertir.pack(side="left", padx=10)

        self.status_default = "Ningún archivo seleccionado"
        self.status_var = tk.StringVar(value=self.status_default)
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, 
            anchor=tk.CENTER, bg="#1E1E1E", fg="#888888", font=("Arial", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, ipady=3)

    # --- GESTIÓN DE INTERFAZ ---

    def _actualizar_esquina(self):
        if self.v_scrollbar.winfo_ismapped() and self.h_scrollbar.winfo_ismapped():
            self.esquina.grid(row=1, column=1, sticky="nsew")
        else:
            self.esquina.grid_forget()

    def _gestionar_vbar(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.v_scrollbar.grid_remove()
        else:
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.v_scrollbar.set(first, last)
        self.root.after_idle(self._actualizar_esquina)

    def _gestionar_hbar(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.h_scrollbar.grid_remove()
        else:
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.h_scrollbar.set(first, last)
        self.root.after_idle(self._actualizar_esquina)

    # --- LÓGICA DE ARCHIVOS Y TEXTO ---

    def _recortar_ruta(self, ruta):
        partes = ruta.split(os.sep)
        prefijo = os.sep if ruta.startswith(os.sep) else ""
        clean_parts = [p for p in partes if p]
        if len(clean_parts) > 3:
            primera = clean_parts[0]
            padre = clean_parts[-2]
            archivo = clean_parts[-1]
            return f"{prefijo}{primera}{os.sep}...{os.sep}{padre}{os.sep}{archivo}"
        return ruta

    def _limpiar_placeholder(self, event):
        contenido_actual = self.texto_input.get("1.0", tk.END).strip()
        if contenido_actual == self.placeholder:
            self.texto_input.delete("1.0", tk.END)
        self.texto_input.config(fg=self.color_texto_normal)

    def _restaurar_placeholder(self, event):
        contenido_actual = self.texto_input.get("1.0", tk.END).strip()
        if not contenido_actual:
            self.texto_input.insert("1.0", self.placeholder)
            self.texto_input.config(fg=self.color_placeholder)

    def borrar_texto(self):
        self.texto_input.delete("1.0", tk.END)
        self.status_var.set(self.status_default)
        if self.root.focus_get() != self.texto_input:
            self._restaurar_placeholder(None)
        else:
            self.texto_input.config(fg=self.color_texto_normal)

    def abrir_archivo(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=(("Todos los archivos", "*.*"),)
        )
        if ruta_archivo:
            try:
                with open(ruta_archivo, 'r', encoding='utf-8', errors='replace') as f:
                    contenido = f.read()
                self.texto_input.delete("1.0", tk.END)
                self.texto_input.config(fg=self.color_texto_normal)
                self.texto_input.insert("1.0", contenido)
                ruta_final = self._recortar_ruta(ruta_archivo)
                self.status_var.set(f"Archivo: {ruta_final}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{str(e)}")

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
        return ImageFont.load_default()

    def convertir(self):
        contenido = self.texto_input.get("1.0", tk.END).strip()
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