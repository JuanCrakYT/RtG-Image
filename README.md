# RtG Image

Aplicación de escritorio para crear pixel art y convertirlo a un asset compatible con RtG.
Permite dibujar desde cero, importar una imagen y exportar el resultado como texto RtG o
como PNG.

## Funciones

- Lienzo ajustable entre 5x5 y 128x128 píxeles.
- Herramientas de pintura, borrador, cuentagotas y relleno.
- Selección de color mediante RGB o hexadecimal.
- Importación de imágenes y conversión automática a píxeles.
- Conversión a un payload RtG en Base64.
- Copia del resultado al portapapeles.
- Exportación del dibujo como PNG.

## Requisitos

- Python 3.10 o posterior.
- Tkinter, incluido normalmente con Python para Windows.
- `customtkinter`.

Instala la dependencia con:

```powershell
python -m pip install customtkinter
```

## Ejecución

Desde la raíz del repositorio, ejecuta:

```powershell
python main.py
```

La ventana permite editar el lienzo, convertirlo a RtG y copiar o guardar el resultado.

## Estructura

- `main.py`: punto de entrada de la aplicación.
- `canvas.py`: lienzo, herramientas de dibujo y exportación PNG.
- `convert/converter.py`: conversión de píxeles al formato RtG.
- `load_img/image_loader.py`: carga y adaptación de imágenes.
- `ui/ui.py`: interfaz gráfica.
- `assets/`: plantillas y datos usados durante la conversión.
- `tests/`: pruebas automatizadas del canvas y del conversor.

## Pruebas

Puedes ejecutar las pruebas con:

```powershell
python -m unittest discover -s tests
```

También puedes comprobar la sintaxis de los módulos principales con:

```powershell
python -m py_compile main.py canvas.py convert/converter.py load_img/image_loader.py ui/ui.py
```

