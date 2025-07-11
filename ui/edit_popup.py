# ui/edit_popup.py
from datetime import datetime

import flet as ft

class EditMatchPopup(ft.AlertDialog):
    """
    Un componente de diálogo (popup) para editar los detalles de un partido.
    Permite al usuario ingresar nuevos valores para los campos de un partido.
    """
    def __init__(self, match_data, on_save):
        super().__init__()
        self.modal = True
        self.match_data = match_data
        self.on_save = on_save
        self.title = ft.Text("Editar Partido")
        self.content = self._build_content()
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.ElevatedButton("Guardar", on_click=self._save),
        ]

        # Diccionario para almacenar las referencias a los campos de entrada
        self.input_fields = {}

    def _build_content(self):
        """
        Construye el contenido del diálogo con campos de entrada para cada propiedad del partido.
        """
        items = []
        # Excluir _id y fixture_id de la edición directa si no es necesario
        excluded_fields = ["_id", "fixture_id"]

        for key, value in self.match_data.items():
            if key in excluded_fields:
                continue

            # Determinar el tipo de control de entrada basado en el tipo de dato
            if isinstance(value, bool):
                control = ft.Checkbox(label=key.replace('_', ' ').title(), value=value)
            elif isinstance(value, (int, float)):
                control = ft.TextField(
                    label=key.replace('_', ' ').title(),
                    value=str(value),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]", replacement_string=""),
                    on_change=lambda e, k=key: self._validate_numeric_input(e, k)
                )
            elif isinstance(value, str) and "T" in value and "Z" in value: # Posible fecha ISO
                control = ft.TextField(
                    label=key.replace('_', ' ').title(),
                    value=value.split('T')[0], # Mostrar solo la parte de la fecha
                    hint_text="YYYY-MM-DD",
                    on_change=lambda e, k=key: self._validate_date_input(e, k)
                )
            else:
                control = ft.TextField(label=key.replace('_', ' ').title(), value=str(value))

            self.input_fields[key] = control
            items.append(control)
        return ft.Column(items, scroll=ft.ScrollMode.ADAPTIVE)

    def _validate_numeric_input(self, e, key):
        """Valida que la entrada sea numérica para campos int/float."""
        try:
            # Intenta convertir a int o float, si no es posible, borra el valor
            if isinstance(self.match_data[key], int):
                int(e.control.value)
            elif isinstance(self.match_data[key], float):
                float(e.control.value)
        except ValueError:
            e.control.value = "" # Borra el valor si no es un número válido
        self.page.update()

    def _validate_date_input(self, e, key):
        """Valida que la entrada sea una fecha en formato YYYY-MM-DD."""
        try:
            datetime.strptime(e.control.value, "%Y-%m-%d")
            e.control.error_text = None
        except ValueError:
            e.control.error_text = "Formato de fecha inválido (YYYY-MM-DD)"
        self.page.update()

    def _save(self, e):
        """
        Recopila los datos de los campos de entrada y llama a la función on_save.
        """
        updated_data = {}
        for key, control in self.input_fields.items():
            if isinstance(control, ft.Checkbox):
                updated_data[key] = control.value
            elif isinstance(control, ft.TextField):
                try:
                    # Intenta convertir al tipo original
                    if isinstance(self.match_data[key], int):
                        updated_data[key] = int(control.value)
                    elif isinstance(self.match_data[key], float):
                        updated_data[key] = float(control.value)
                    elif isinstance(self.match_data[key], str) and "T" in self.match_data[key] and "Z" in self.match_data[key]:
                        # Si es una fecha, reconstruir el formato ISO
                        updated_data[key] = f"{control.value}T00:00:00Z" # Asume medianoche UTC
                    else:
                        updated_data[key] = control.value
                except ValueError:
                    # Si la conversión falla, usa el valor original o maneja el error
                    updated_data[key] = self.match_data[key]
            else:
                updated_data[key] = control.value # Para otros tipos de control si los hubiera

        # Pasa el ID del documento y los datos actualizados a la función on_save
        self.on_save(self.match_data["_id"], updated_data)
        self.open = False
        self.page.update()

    def _cancel(self, e):
        """Cierra el diálogo sin guardar."""
        self.open = False
        self.page.update()