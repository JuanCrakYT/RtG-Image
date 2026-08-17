# AGENTS.md

## Propósito del proyecto
Este repositorio contiene una aplicación de escritorio en Python para dibujar pixel art, convertirlo a texto RtG y copiar o exportar el resultado como PNG.

## Cómo ejecutar la app
- Ejecuta la aplicación desde la raíz del proyecto con:
  - `python main.py`
  - o `py main.py`
- La entrada principal está en [main.py](main.py), que llama a `build_app()` desde [ui.py](ui.py).

## Arquitectura y responsabilidades
- [ui.py](ui.py): interfaz gráfica con Tkinter/CustomTkinter y los botones de la aplicación.
- [canvas.py](canvas.py): lógica del canvas editable, herramientas de dibujo, borrado, cuentagotas y relleno.
- [converter.py](converter.py): conversión del mapa de píxeles a texto RtG.
- [image_loader.py](image_loader.py): carga de imágenes externas y conversión a una matriz de píxeles de 32x32.
- [clipboard.py](clipboard.py): copia de texto al portapapeles.

## Convenciones importantes
- Mantén los textos y nombres de la interfaz en español para coincidir con la experiencia actual.
- El canvas trabaja con una matriz fija de 32x32 píxeles; si cambias este tamaño, revisa la UI y la lógica asociada.
- La clase `PixelCanvas` en [canvas.py](canvas.py) es el punto central para herramientas y edición; si añades nuevas funciones, mantén la API coherente.
- La conversión en [converter.py](converter.py) está aislada intencionalmente; si cambias el formato de salida, ajusta también la vista de la UI.

## Recomendaciones para cambios
- Prioriza cambios pequeños y localizados en el módulo correspondiente.
- Si modificas comportamiento visual o de herramientas, prueba la interacción en la aplicación.
- No añadas dependencias nuevas sin justificar el motivo y documentarlas.

## Validación rápida
- Tras cambios en Python, valida sintaxis con:
  - `python -m py_compile main.py ui.py canvas.py converter.py image_loader.py clipboard.py`
- No hay pruebas automatizadas configuradas en este proyecto; la validación manual y la compilación son la referencia principal.
