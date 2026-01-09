#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from datetime import datetime

class ConversorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Txt2Img")
        self.root.geometry("400x320")
        self.root.configure(bg="#2E2E2E")

        # --- RUTA BASE Y ASSETS ---
        self.ruta_script = os.path.dirname(os.path.abspath(__file__))
        
        # Icono del programa
        try:
            ruta_logo = os.path.join(self.ruta_script, "assets", "logo.png")
            img_logo = Image.open(ruta_logo)
            
            try:
                filtro = Image.Resampling.LANCZOS
            except AttributeError:
                filtro = Image.LANCZOS
                
            img_logo_resized = img_logo.resize((64, 64), filtro)
            self.icon_ventana = ImageTk.PhotoImage(img_logo_resized)
            self.root.iconphoto(True, self.icon_ventana)
        except Exception as e:
            print(f"DEBUG: No se pudo cargar el logo de la ventana: {e}")

        # --- CONFIGURACIÓN DE RUTA Y COLORES ---
        self.ruta_salida = os.path.join(os.path.expanduser("~"), "Pictures")
        if not os.path.exists(self.ruta_salida):
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

        # --- BOTONES ---
        panel_bottom = tk.Frame(root, bg="#2E2E2E")
        panel_bottom.pack(fill="x", pady=5)

        self.centro_botones = tk.Frame(panel_bottom, bg="#2E2E2E")
        self.centro_botones.pack(anchor="center")

        # Botón Configuración (Icono Gear)
        self.icon_config = None
        ruta_icono_cfg = os.path.join(self.ruta_script, "assets", "config_icon.png")
        
        try:
            img_original = Image.open(ruta_icono_cfg)
            try:
                filtro = Image.Resampling.LANCZOS
            except AttributeError:
                filtro = Image.LANCZOS 
            img_resizada = img_original.resize((18, 18), filtro)
            self.icon_config = ImageTk.PhotoImage(img_resizada)
            btn_config = tk.Button(self.centro_botones, image=self.icon_config, bg="#444444", 
                relief="flat", width=26, height=26, borderwidth=0, highlightthickness=0,
                padx=0, pady=0, command=self.abrir_configuracion)
        except Exception:
            btn_config = tk.Button(self.centro_botones, text="⚙", bg="#444444", fg="white", 
                font=("Arial", 9, "bold"), width=5, relief="flat", command=self.abrir_configuracion)

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

    # --- LÓGICA DE CONFIGURACIÓN ---

    def abrir_configuracion(self):
        ventana_cfg = tk.Toplevel(self.root)
        ventana_cfg.title("Configuración")
        ventana_cfg.geometry("450x150")
        ventana_cfg.configure(bg="#2E2E2E")
        ventana_cfg.resizable(False, False)
        ventana_cfg.transient(self.root)
        ventana_cfg.grab_set()

        tk.Label(ventana_cfg, text="Ruta de guardado de las imagenes:", 
                 bg="#2E2E2E", fg="white", font=("Arial", 10, "bold")).pack(pady=(15, 5))

        frame_ruta = tk.Frame(ventana_cfg, bg="#2E2E2E")
        frame_ruta.pack(fill="x", padx=20)

        self.lbl_ruta_actual = tk.Label(frame_ruta, text=self.ruta_salida, 
                                       bg="#1E1E1E", fg="#D4D4D4", font=("Consolas", 9),
                                       relief="flat", anchor="w", padx=5)
        self.lbl_ruta_actual.pack(side="left", expand=True, fill="x")

        btn_cambiar = tk.Button(frame_ruta, text="...", command=self._seleccionar_carpeta,
                               bg="#444444", fg="white", width=3, relief="flat")
        btn_cambiar.pack(side="right", padx=(5, 0))

        btn_cerrar = tk.Button(ventana_cfg, text="ACEPTAR", command=ventana_cfg.destroy,
                              bg="#2A8C55", fg="white", font=("Arial", 9, "bold"), width=10, relief="flat")
        btn_cerrar.pack(pady=20)

    def _seleccionar_carpeta(self):
        nueva_ruta = filedialog.askdirectory(initialdir=self.ruta_salida, title="Seleccionar Carpeta")
        if nueva_ruta:
            self.ruta_salida = nueva_ruta
            self.lbl_ruta_actual.config(text=self.ruta_salida)

    # --- MÉTODOS DE SOPORTE (NO CAMBIAN) ---

    def _actualizar_esquina(self):
        if self.v_scrollbar.winfo_ismapped() and self.h_scrollbar.winfo_ismapped():
            self.esquina.grid(row=1, column=1, sticky="nsew")
        else:
            self.esquina.grid_forget()

    def _gestionar_vbar(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0: self.v_scrollbar.grid_remove()
        else: self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.v_scrollbar.set(first, last)
        self.root.after_idle(self._actualizar_esquina)

    def _gestionar_hbar(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0: self.h_scrollbar.grid_remove()
        else: self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.h_scrollbar.set(first, last)
        self.root.after_idle(self._actualizar_esquina)

    def _recortar_ruta(self, ruta):
        partes = ruta.split(os.sep)
        prefijo = os.sep if ruta.startswith(os.sep) else ""
        clean_parts = [p for p in partes if p]
        if len(clean_parts) > 3:
            return f"{prefijo}{clean_parts[0]}{os.sep}...{os.sep}{clean_parts[-2]}{os.sep}{clean_parts[-1]}"
        return ruta

    def _limpiar_placeholder(self, event):
        if self.texto_input.get("1.0", tk.END).strip() == self.placeholder:
            self.texto_input.delete("1.0", tk.END)
        self.texto_input.config(fg=self.color_texto_normal)

    def _restaurar_placeholder(self, event):
        if not self.texto_input.get("1.0", tk.END).strip():
            self.texto_input.insert("1.0", self.placeholder)
            self.texto_input.config(fg=self.color_placeholder)

    def borrar_texto(self):
        self.texto_input.delete("1.0", tk.END)
        self.status_var.set(self.status_default)
        if self.root.focus_get() != self.texto_input: self._restaurar_placeholder(None)
        else: self.texto_input.config(fg=self.color_texto_normal)

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=(("Todos", "*.*"),))
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8', errors='replace') as f:
                    contenido = f.read()
                self.texto_input.delete("1.0", tk.END)
                self.texto_input.config(fg=self.color_texto_normal)
                self.texto_input.insert("1.0", contenido)
                self.status_var.set(f"Archivo: {self._recortar_ruta(ruta)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def obtener_fuente(self, tamano):
        fuentes = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "arial.ttf"]
        for r in fuentes:
            if os.path.exists(r): return ImageFont.truetype(r, tamano)
        return ImageFont.load_default()

    def convertir(self):
        contenido = self.texto_input.get("1.0", tk.END).strip()
        if not contenido or contenido == self.placeholder:
            messagebox.showwarning("Vacío", "El cuadro de texto está vacío.")
            return
        try:
            font = self.obtener_fuente(48)
            dummy = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            left, top, right, bottom = dummy.textbbox((0, 0), contenido, font=font)
            w, h = (right - left) + 100, (bottom - top) + 100
            img = Image.new('RGB', (int(w), int(h)), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), contenido, font=font, fill=(220, 220, 220))
            if not os.path.exists(self.ruta_salida): os.makedirs(self.ruta_salida)
            ruta_f = os.path.join(self.ruta_salida, f"imgtxt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            img.save(ruta_f, "JPEG", quality=100)
            messagebox.showinfo("Listo", f"Guardado en:\n{self.ruta_salida}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorApp(root)
    root.mainloop()