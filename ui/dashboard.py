# ui/dashboard.py
from datetime import timedelta

import flet as ft
import pandas as pd
from ui.filters import Filters
from ui.edit_popup import EditMatchPopup
from db.queries import find_documents, update_document, delete_document, get_unique_teams, get_unique_leagues
from utils.dataframe_tools import mongo_to_dataframe, clean_and_format_dataframe
from api.fetch_matches import simulate_fetch_and_store_dummy_data, fetch_and_store_matches_from_api # Importa las funciones de la API

class Dashboard(ft.Column):
    """
    Vista principal del dashboard que muestra los datos de partidos,
    controles de filtro y botones para acciones.
    """
    def __init__(self):
        super().__init__()
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.expand = True # Para que ocupe todo el espacio disponible

        self.data_table = ft.DataTable(
            columns=[],
            rows=[],
            border=ft.border.all(2, ft.colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            vertical_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.BLUE_GREY_100),
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color=ft.colors.BLUE_GREY_50,
            data_row_color={"hovered": ft.colors.BLUE_GREY_50},
            show_checkbox_column=False,
            divider_thickness=1,
            column_spacing=20,
        )

        self.progress_ring = ft.ProgressRing(width=50, height=50, stroke_width=5, visible=False)
        self.status_text = ft.Text("Cargando datos...", visible=False)

        self.filters_component = Filters(
            on_apply_filters=self.apply_filters,
            on_clear_filters=self.load_data, # Recargar todos los datos al limpiar
            unique_teams=[],
            unique_leagues=[]
        )

        self.controls = [
            ft.Text("Dashboard de Estadísticas de Fútbol", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "Cargar Datos de Prueba (Simulado)",
                    icon=ft.icons.CLOUD_DOWNLOAD,
                    on_click=self.load_dummy_data
                ),
                ft.ElevatedButton(
                    "Cargar Datos de API-Football",
                    icon=ft.icons.API,
                    on_click=self.load_api_data
                ),
                ft.ElevatedButton(
                    "Exportar a CSV",
                    icon=ft.icons.FILE_DOWNLOAD,
                    on_click=self.export_to_csv
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            self.filters_component, # Componente de filtros
            ft.Stack([
                ft.Column([
                    self.progress_ring,
                    self.status_text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True),
                ft.Container(
                    content=self.data_table,
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=10,
                    margin=10,
                    border_radius=ft.border_radius.all(10),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.colors.BLACK_26,
                        offset=ft.Offset(0, 3),
                    ),
                    bgcolor=ft.colors.WHITE
                ),
            ], expand=True)
        ]

    def did_mount(self):
        """Se llama cuando el componente se monta en la página."""
        self.load_data() # Carga los datos iniciales al iniciar el dashboard
        self.page.add(self.filters_component.start_date_picker, self.filters_component.end_date_picker)
        self.filters_component.did_mount() # Asegura que los date pickers se añadan al overlay

    def will_unmount(self):
        """Se llama cuando el componente se desmonta de la página."""
        self.filters_component.will_unmount() # Limpia los date pickers del overlay

    def _set_loading_state(self, loading=True, message=""):
        """Muestra/oculta el indicador de carga y el mensaje de estado."""
        self.progress_ring.visible = loading
        self.status_text.visible = loading
        self.status_text.value = message
        self.data_table.visible = not loading
        self.page.update()

    def load_data(self, filters=None):
        """Carga los datos de partidos desde MongoDB y actualiza la tabla."""
        self._set_loading_state(True, "Cargando datos de partidos...")
        try:
            query = {}
            if filters:
                if "start_date" in filters and "end_date" in filters:
                    query["fecha"] = {
                        "$gte": filters["start_date"],
                        "$lte": filters["end_date"]
                    }
                elif "start_date" in filters:
                    query["fecha"] = {"$gte": filters["start_date"]}
                elif "end_date" in filters:
                    query["fecha"] = {"$lte": filters["end_date"]}

                if "team" in filters:
                    query["$or"] = [
                        {"equipo_local": filters["team"]},
                        {"equipo_visitante": filters["team"]}
                    ]
                if "league" in filters:
                    query["liga"] = filters["league"]

            mongo_docs = find_documents(query)
            df = mongo_to_dataframe(mongo_docs)
            df = clean_and_format_dataframe(df) # Limpiar y formatear los datos

            self._update_data_table(df)

            # Actualizar opciones de filtros después de cargar datos
            unique_teams = get_unique_teams()
            unique_leagues = get_unique_leagues()
            self.filters_component.update_dropdown_options(unique_teams, unique_leagues)

            self._set_loading_state(False)
            self.page.update()
        except Exception as e:
            self._set_loading_state(False)
            self.status_text.value = f"Error al cargar datos: {e}"
            self.status_text.visible = True
            self.page.update()
            print(f"Error al cargar datos: {e}")

    def _update_data_table(self, df):
        """Actualiza las columnas y filas del ft.DataTable con el DataFrame."""
        if df.empty:
            self.data_table.columns = []
            self.data_table.rows = []
            self.status_text.value = "No hay datos para mostrar."
            self.status_text.visible = True
            self.data_table.visible = False
            return

        # Crear columnas
        columns = []
        for col in df.columns:
            # Excluir la columna '_id' de la visualización si no es necesaria
            if col == "_id":
                continue
            columns.append(
                ft.DataColumn(
                    ft.Text(col.replace('_', ' ').title(), weight=ft.FontWeight.BOLD),
                    on_sort=lambda e, col_name=col: self._sort_data_table(e, col_name, df)
                )
            )
        # Añadir columna de acciones
        columns.append(ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)))
        self.data_table.columns = columns

        # Crear filas
        rows = []
        for index, row in df.iterrows():
            cells = []
            row_id = row["_id"] # Guardar el _id para acciones de edición/eliminación

            for col in df.columns:
                if col == "_id":
                    continue
                cells.append(ft.DataCell(ft.Text(str(row[col]))))

            # Añadir botones de acción a la última celda de cada fila
            cells.append(
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Editar",
                            on_click=lambda e, r=row.to_dict(): self.open_edit_popup(r)
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            tooltip="Eliminar",
                            on_click=lambda e, id=row_id: self.confirm_delete(id)
                        ),
                    ])
                )
            )
            rows.append(ft.DataRow(cells))
        self.data_table.rows = rows
        self.data_table.visible = True
        self.status_text.visible = False # Ocultar mensaje de "No hay datos" si hay datos
        self.page.update()

    def _sort_data_table(self, e, column_name, df):
        """Maneja el ordenamiento de la tabla."""
        self.data_table.sort_column_index = e.control.col_index
        self.data_table.sort_ascending = e.control.sort_ascending

        if e.control.sort_ascending:
            df_sorted = df.sort_values(by=column_name, ascending=True)
        else:
            df_sorted = df.sort_values(by=column_name, ascending=False)

        self._update_data_table(df_sorted) # Actualiza la tabla con los datos ordenados

    def load_dummy_data(self, e):
        """Carga datos de prueba simulados en MongoDB."""
        self._set_loading_state(True, "Generando y cargando datos de prueba...")
        simulate_fetch_and_store_dummy_data(num_matches=20)
        self.load_data() # Recarga la tabla después de insertar datos
        self._set_loading_state(False, "Datos de prueba cargados.")
        self.page.update()

    def load_api_data(self, e):
        """Carga datos reales desde la API-Football en MongoDB."""
        self._set_loading_state(True, "Obteniendo datos de API-Football...")
        # Aquí puedes añadir un input para que el usuario especifique fecha, liga, etc.
        # Por ahora, se llama sin parámetros, lo que podría no ser lo ideal para la API.
        # Considera añadir un diálogo o campos de entrada para estos parámetros.
        fetch_and_store_matches_from_api() # Llama a la función real de la API
        self.load_data() # Recarga la tabla después de insertar datos
        self._set_loading_state(False, "Datos de API-Football cargados.")
        self.page.update()

    def export_to_csv(self, e):
        """Exporta los datos actuales de la tabla a un archivo CSV."""
        self._set_loading_state(True, "Exportando a CSV...")
        try:
            # Obtener el DataFrame actual de la tabla (si ya está cargado)
            # Una forma más robusta sería obtener los datos directamente de la DB con los filtros actuales
            current_mongo_docs = find_documents(self._get_current_filters_as_query())
            df_to_export = mongo_to_dataframe(current_mongo_docs)
            df_to_export = clean_and_format_dataframe(df_to_export)

            # Eliminar la columna '_id' antes de exportar si no es necesaria en el CSV
            if '_id' in df_to_export.columns:
                df_to_export = df_to_export.drop(columns=['_id'])

            file_path = "partidos_futbol.csv"
            df_to_export.to_csv(file_path, index=False, encoding='utf-8')
            self._set_loading_state(False, f"Datos exportados a '{file_path}'")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Datos exportados a '{file_path}' exitosamente."),
                open=True
            )
            self.page.update()
        except Exception as ex:
            self._set_loading_state(False, f"Error al exportar CSV: {ex}")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error al exportar CSV: {ex}"),
                open=True
            )
            self.page.update()
            print(f"Error al exportar CSV: {ex}")

    def apply_filters(self, filters):
        """Aplica los filtros seleccionados y recarga los datos."""
        print(f"Aplicando filtros: {filters}")
        self.load_data(filters)

    def _get_current_filters_as_query(self):
        """
        Construye el objeto de consulta de MongoDB basado en los filtros actuales
        del componente Filters.
        """
        filters = {}
        if self.filters_component.selected_start_date:
            filters["start_date"] = self.filters_component.selected_start_date.isoformat() + "Z"
        if self.filters_component.selected_end_date:
            end_of_day = self.filters_component.selected_end_date + timedelta(days=1) - timedelta(microseconds=1)
            filters["end_date"] = end_of_day.isoformat() + "Z"
        if self.filters_component.selected_team:
            filters["team"] = self.filters_component.selected_team
        if self.filters_component.selected_league:
            filters["league"] = self.filters_component.selected_league
        return filters

    def open_edit_popup(self, match_data):
        """Abre el popup para editar un partido."""
        edit_dialog = EditMatchPopup(match_data, self.save_edited_match)
        self.page.dialog = edit_dialog
        edit_dialog.open = True
        self.page.update()

    def save_edited_match(self, match_id, updated_data):
        """Guarda los cambios de un partido editado en MongoDB."""
        self._set_loading_state(True, "Guardando cambios...")
        success = update_document(match_id, updated_data)
        if success:
            self.load_data(self._get_current_filters_as_query()) # Recarga los datos para reflejar el cambio
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Partido actualizado exitosamente."),
                open=True
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Error al actualizar el partido."),
                open=True
            )
        self._set_loading_state(False)
        self.page.update()

    def confirm_delete(self, match_id):
        """Muestra un diálogo de confirmación antes de eliminar un partido."""
        def delete_confirmed(e):
            if e.control.text == "Sí":
                self.delete_match(match_id)
            self.page.dialog.open = False
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro de que quieres eliminar este partido?"),
            actions=[
                ft.TextButton("No", on_click=delete_confirmed),
                ft.TextButton("Sí", on_click=delete_confirmed),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def delete_match(self, match_id):
        """Elimina un partido de MongoDB."""
        self._set_loading_state(True, "Eliminando partido...")
        success = delete_document(match_id)
        if success:
            self.load_data(self._get_current_filters_as_query()) # Recarga los datos
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Partido eliminado exitosamente."),
                open=True
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Error al eliminar el partido."),
                open=True
            )
        self._set_loading_state(False)
        self.page.update()