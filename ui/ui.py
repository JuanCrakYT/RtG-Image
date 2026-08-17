import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional
import webbrowser

import customtkinter as ctk

from canvas import PixelCanvas, export_pixels_to_index_file, export_pixels_to_text
from convert.converter import convert_to_rtg
from load_img.image_loader import load_image_to_pixels
from ui.clipboard import copy_text_to_clipboard

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class RtGApp(ctk.CTk):
    def __init__(self, master: ctk.CTk | None = None) -> None:
        super().__init__(master)
        self.title("RtG Pixel Art Generator")
        self.geometry("1180x780")
        self.minsize(980, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self._set_window_icon()

        self.canvas_widget: Optional[PixelCanvas] = None
        self._recent_colors: list[tuple[int, int, int, int]] = []
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        main_frame.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=0)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(0, weight=0)
        left_panel.grid_rowconfigure(1, weight=1)

        right_panel = ctk.CTkFrame(main_frame)
        right_panel.grid(row=0, column=1, sticky="ns", padx=0, pady=0)
        right_panel.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(left_panel, text="RtG Pixel Art Generator", font=("Segoe UI", 24, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        canvas_container = ctk.CTkFrame(left_panel)
        canvas_container.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        canvas_container.grid_columnconfigure(0, weight=1)
        canvas_container.grid_rowconfigure(0, weight=1)
        self.canvas_widget = PixelCanvas(canvas_container, width=640, height=640)
        self.canvas_widget.pack(anchor="center", pady=8)

        toolbar = ctk.CTkFrame(right_panel)
        toolbar.grid(row=0, column=0, sticky="n", padx=16, pady=16)
        toolbar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(toolbar, text="Color", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.color_button = ctk.CTkButton(toolbar, text="Color: (255, 255, 255)", command=self._pick_color, width=180)
        self.color_button.grid(row=1, column=0, columnspan=2, pady=(0, 6))
        self.color_preview = ctk.CTkFrame(toolbar, width=180, height=24, fg_color="white")
        self.color_preview.grid(row=2, column=0, columnspan=2, pady=(0, 12))

        self._color_palette_frame = ctk.CTkFrame(toolbar)
        self._color_palette_frame.grid(row=3, column=0, columnspan=2, pady=(0, 12))
        self._palette_buttons = []
        self._render_recent_colors()

        ctk.CTkLabel(toolbar, text="Herramientas", font=("Segoe UI", 14, "bold")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.tool_var = tk.StringVar(value="paint")
        ctk.CTkOptionMenu(toolbar, values=["paint", "eraser", "eyedropper", "fill"], variable=self.tool_var, width=180, command=self._on_tool_change).grid(row=5, column=0, columnspan=2, pady=(0, 12))

        ctk.CTkLabel(toolbar, text="Tamaño del lienzo", font=("Segoe UI", 14, "bold")).grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.canvas_width_var = tk.IntVar(value=32)
        self.canvas_height_var = tk.IntVar(value=32)
        self.canvas_width_label = ctk.CTkLabel(toolbar, text="X: 32 px", font=("Segoe UI", 13))
        self.canvas_width_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 2))
        ctk.CTkSlider(toolbar, from_=5, to=128, number_of_steps=124, variable=self.canvas_width_var, command=self._update_canvas_size_label).grid(row=8, column=0, columnspan=2, pady=(0, 6))
        self.canvas_height_label = ctk.CTkLabel(toolbar, text="Y: 32 px", font=("Segoe UI", 13))
        self.canvas_height_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 2))
        ctk.CTkSlider(toolbar, from_=5, to=128, number_of_steps=124, variable=self.canvas_height_var, command=self._update_canvas_size_label).grid(row=10, column=0, columnspan=2, pady=(0, 6))
        ctk.CTkButton(toolbar, text="Generar Canvas", command=self._generate_canvas).grid(row=11, column=0, columnspan=2, pady=(0, 8))

        ctk.CTkLabel(toolbar, text="Color de fondo", font=("Segoe UI", 14, "bold")).grid(row=12, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.transparent_color_var = tk.StringVar(value="black")
        ctk.CTkOptionMenu(toolbar, values=["black", "white"], variable=self.transparent_color_var, width=180, command=self._on_transparent_color_change).grid(row=13, column=0, columnspan=2, pady=(0, 12))

        ctk.CTkButton(toolbar, text="Importar imagen", command=self._import_image).grid(row=14, column=0, columnspan=2, pady=(0, 8))
        ctk.CTkButton(toolbar, text="Limpiar", command=self._clear_canvas).grid(row=15, column=0, columnspan=2, pady=(0, 8))
        ctk.CTkButton(toolbar, text="Convertir a RtG", command=self._convert_to_rtg).grid(row=16, column=0, columnspan=2, pady=(0, 8))
        ctk.CTkButton(toolbar, text="Copiar", command=self._copy_output).grid(row=17, column=0, columnspan=2, pady=(0, 8))
        ctk.CTkButton(toolbar, text="Guardar PNG", command=self._save_png).grid(row=18, column=0, columnspan=2, pady=(0, 8))
        ctk.CTkButton(toolbar, text="Unirse a RtG", command=self._open_share_link).grid(row=19, column=0, columnspan=2, pady=(0, 8))

        self.output_box = ctk.CTkTextbox(right_panel, width=260, height=220)
        self.output_box.grid(row=1, column=0, sticky="n", padx=16, pady=(0, 16))
        self._display_chunk_size = 100
        self._display_index = 0
        self.show_more_button = ctk.CTkButton(right_panel, text="Mostrar más", command=self._show_more_output)
        self.show_more_button.grid(row=2, column=0, sticky="s", padx=16, pady=(0, 8))
        self.show_more_button.configure(state="disabled")
        self._display_label = ctk.CTkLabel(right_panel, text="Mostrando 0/0")
        self._display_label.grid(row=3, column=0, sticky="n", padx=16, pady=(0, 8))

        self.canvas_widget.set_tool("paint")
        self._selected_color = (255, 255, 255, 255)
        self._current_output = ""
        self._transparent_output_color = (0, 0, 0, 255)
        self._update_color_preview()
        self._update_canvas_size_label(0)

    def _set_window_icon(self) -> None:
        icon_path = PROJECT_ROOT / "Design" / "logotipe.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

    def _pick_color(self) -> None:
        self._show_color_entry()

    def _show_color_entry(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ingresar color")
        dialog.geometry("360x150")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Escribe RGB como 255,0,0 o HEX como #ff0000:").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))
        color_entry = ctk.CTkEntry(dialog, width=320)
        color_entry.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12))
        color_entry.focus()

        ctk.CTkButton(dialog, text="Aceptar", command=lambda: self._apply_text_color(dialog, color_entry.get())).grid(row=2, column=0, padx=(12, 6), pady=(0, 12))
        ctk.CTkButton(dialog, text="Cancelar", command=dialog.destroy).grid(row=2, column=1, padx=(6, 12), pady=(0, 12))

    def _apply_text_color(self, dialog: ctk.CTkToplevel, value: str) -> None:
        parsed = self._parse_color_string(value)
        if parsed is None:
            messagebox.showerror("Color inválido", "Ingresa un color válido en formato RGB o HEX.")
            return

        self._selected_color = parsed
        self._add_recent_color(parsed)
        self._render_recent_colors()
        self._update_color_preview()
        self.color_button.configure(text=f"Color: {parsed[:3]}")
        self.canvas_widget.set_color(parsed)
        dialog.destroy()

    def _parse_color_string(self, value: str) -> tuple[int, int, int, int] | None:
        text = value.strip().lower()
        if text.startswith("#"):
            text = text[1:]
            if len(text) == 6:
                try:
                    r = int(text[0:2], 16)
                    g = int(text[2:4], 16)
                    b = int(text[4:6], 16)
                    return (r, g, b, 255)
                except ValueError:
                    return None
            return None

        parts = [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]
        if len(parts) == 3:
            try:
                r, g, b = (int(part) for part in parts)
                if all(0 <= value <= 255 for value in (r, g, b)):
                    return (r, g, b, 255)
            except ValueError:
                return None
        return None

    def _add_recent_color(self, color: tuple[int, int, int, int]) -> None:
        if color in self._recent_colors:
            self._recent_colors.remove(color)
        self._recent_colors.insert(0, color)
        self._recent_colors = self._recent_colors[:12]

    def _render_recent_colors(self) -> None:
        for widget in self._palette_buttons:
            widget.destroy()
        self._palette_buttons.clear()

        if not self._recent_colors:
            label = ctk.CTkLabel(self._color_palette_frame, text="No hay colores recientes.")
            label.grid(row=0, column=0, padx=2, pady=2)
            self._palette_buttons.append(label)
            return

        for index, color in enumerate(self._recent_colors):
            button = ctk.CTkButton(
                self._color_palette_frame,
                width=24,
                height=24,
                fg_color=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                text="",
                command=lambda selected=color: self._select_palette_color(selected),
            )
            button.grid(row=index // 6, column=index % 6, padx=2, pady=2)
            self._palette_buttons.append(button)

    def _open_share_link(self) -> None:
        webbrowser.open("https://www.roblox.com/share?code=a3361cfb79949e43b22c1299c102fbe8&type=Server")

    def _select_palette_color(self, color: tuple[int, int, int, int]) -> None:
        self._selected_color = color
        self.canvas_widget.set_color(self._selected_color)
        self._add_recent_color(color)
        self._render_recent_colors()
        self.color_button.configure(text=f"Color: {self._selected_color[:3]}")
        self._update_color_preview()

    def _on_tool_change(self, value: str) -> None:
        self.canvas_widget.set_tool(value)

    def _on_transparent_color_change(self, value: str) -> None:
        self._transparent_output_color = (0, 0, 0, 255) if value == "black" else (255, 255, 255, 255)

    def _update_canvas_size_label(self, value: int) -> None:
        width = self.canvas_width_var.get()
        height = self.canvas_height_var.get()
        self.canvas_width_label.configure(text=f"X: {width} px")
        self.canvas_height_label.configure(text=f"Y: {height} px")

    def _generate_canvas(self) -> None:
        width = self.canvas_width_var.get()
        height = self.canvas_height_var.get()
        try:
            from assets.canvas.canvas import generate_canvas_files
            generate_canvas_files(width=width, height=height, output_dir=PROJECT_ROOT / "assets" / "canvas")
            self.canvas_widget.set_size(width, height)
            self.canvas_widget.clear()
            messagebox.showinfo("Listo", f"Canvas generado con tamaño {width}×{height}")
        except Exception as exc:  # pragma: no cover - UI level
            messagebox.showerror("Error", f"No se pudo generar el canvas: {exc}")

    def _import_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Importar imagen",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if not path:
            return
        try:
            pixels = load_image_to_pixels(path, width=self.canvas_widget.size_x, height=self.canvas_widget.size_y)
            self.canvas_widget.load_pixels(pixels)
        except Exception as exc:  # pragma: no cover - UI level
            messagebox.showerror("Error", f"No se pudo importar la imagen: {exc}")

    def _clear_canvas(self) -> None:
        self.canvas_widget.clear()
        # reset output pagination
        self._current_output = ""
        self._display_index = 0
        self.output_box.delete("0.0", tk.END)
        self.show_more_button.configure(state="disabled")
        self._display_label.configure(text=f"Mostrando 0/0")

    def _convert_to_rtg(self) -> None:
        pixels = self.canvas_widget.get_pixels()
        asset_path = PROJECT_ROOT / "assets" / "canvas" / "canvas.json"
        asset_index_path = PROJECT_ROOT / "assets" / "canvas" / "canvas_index.txt"
        if not asset_path.exists():
            asset_path = PROJECT_ROOT / "assets" / "default" / "output_converted_asset.txt"
        if not asset_index_path.exists():
            asset_index_path = PROJECT_ROOT / "assets" / "index.txt"
        result = convert_to_rtg(pixels, transparent_color=self._transparent_output_color, asset_path=asset_path, asset_index_path=asset_index_path)
        self._current_output = result or ""
        # reset pagination and show first chunk
        self._display_index = 0
        self.output_box.delete("0.0", tk.END)
        first = self._current_output[self._display_index:self._display_index + self._display_chunk_size]
        self.output_box.insert("0.0", first)
        self._display_index += len(first)
        total = len(self._current_output)
        self._display_label.configure(text=f"Mostrando {self._format_count(self._display_index)}/{self._format_count(total)}")
        if self._display_index < total:
            self.show_more_button.configure(state="normal")
        else:
            self.show_more_button.configure(state="disabled")


    def _show_more_output(self) -> None:
        if not self._current_output or self._display_index >= len(self._current_output):
            self.show_more_button.configure(state="disabled")
            return
        start = self._display_index
        end = min(start + self._display_chunk_size, len(self._current_output))
        chunk = self._current_output[start:end]
        self.output_box.insert(tk.END, chunk)
        self._display_index = end
        total = len(self._current_output)
        self._display_label.configure(text=f"Mostrando {self._format_count(self._display_index)}/{self._format_count(total)}")
        if self._display_index >= total:
            self.show_more_button.configure(state="disabled")

    def _copy_output(self) -> None:
        if not self._current_output:
            messagebox.showinfo("Sin contenido", "Convierte primero el dibujo para generar texto RtG.")
            return
        if copy_text_to_clipboard(self._current_output):
            messagebox.showinfo("Listo", "Texto RtG copiado al portapapeles.")
        else:
            messagebox.showerror("Error", "No se pudo copiar al portapapeles.")

    def _save_png(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        self.canvas_widget.save_png(path, background_color=self._transparent_output_color)
        messagebox.showinfo("Listo", f"Imagen guardada en {path}")

    def _normalize_color(self, color: tuple[float, float, float]) -> tuple[int, int, int, int]:
        r, g, b = color
        return (int(r), int(g), int(b), 255)

    def _format_count(self, n: int) -> str:
        if n < 1000:
            return str(n)
        for unit in ["k", "M", "B"]:
            n /= 1000.0
            if n < 1000:
                if n >= 100:
                    return f"{int(n)}{unit}"
                return f"{n:.1f}{unit}"
        return f"{n:.1f}T"

    def _update_color_preview(self) -> None:
        r, g, b, _ = self._selected_color
        self.color_preview.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")


def build_app() -> None:
    app = RtGApp()
    app.mainloop()

