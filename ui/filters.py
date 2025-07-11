# ui/filters.py

import flet as ft
from datetime import datetime, date, timedelta

class Filters(ft.Column):
    """
    Componente de UI para aplicar filtros a los datos de partidos.
    Incluye filtros por rango de fechas y por equipo.
    """
    def __init__(self, on_apply_filters, on_clear_filters, unique_teams=None, unique_leagues=None):
        super().__init__()
        self.on_apply_filters = on_apply_filters
        self.on_clear_filters = on_clear_filters
        self.unique_teams = unique_teams if unique_teams is not None else []
        self.unique_leagues = unique_leagues if unique_leagues is not None else []

        self.start_date_picker = ft.DatePicker(
            on_change=self._on_start_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        self.end_date_picker = ft.DatePicker(
            on_change=self._on_end_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )

        self.start_date_button = ft.ElevatedButton(
            "Fecha Inicio",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.start_date_picker.present(),
        )
        self.end_date_button = ft.ElevatedButton(
            "Fecha Fin",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.end_date_picker.present(),
        )

        self.start_date_text = ft.Text("Seleccionar fecha de inicio")
        self.end_date_text = ft.Text("Seleccionar fecha de fin")

        self.team_dropdown = ft.Dropdown(
            label="Filtrar por Equipo",
            options=[ft.dropdown.Option(team) for team in sorted(self.unique_teams)],
            hint_text="Selecciona un equipo",
            width=200,
            on_change=self._on_team_selected
        )

        self.league_dropdown = ft.Dropdown(
            label="Filtrar por Liga",
            options=[ft.dropdown.Option(league) for league in sorted(self.unique_leagues)],
            hint_text="Selecciona una liga",
            width=200,
            on_change=self._on_league_selected
        )

        self.selected_start_date = None
        self.selected_end_date = None
        self.selected_team = None
        self.selected_league = None

        self.controls = [
            ft.Row([
                ft.Column([
                    self.start_date_button,
                    self.start_date_text
                ]),
                ft.Column([
                    self.end_date_button,
                    self.end_date_text
                ]),
            ]),
            ft.Row([
                self.team_dropdown,
                self.league_dropdown,
            ]),
            ft.Row([
                ft.ElevatedButton("Aplicar Filtros", on_click=self._apply_filters),
                ft.OutlinedButton("Limpiar Filtros", on_click=self._clear_filters),
            ]),
        ]

    def _on_start_date_change(self, e):
        """Maneja el cambio de la fecha de inicio seleccionada."""
        if self.start_date_picker.value:
            self.selected_start_date = self.start_date_picker.value
            self.start_date_text.value = self.selected_start_date.strftime("%Y-%m-%d")
        self.page.update()

    def _on_end_date_change(self, e):
        """Maneja el cambio de la fecha de fin seleccionada."""
        if self.end_date_picker.value:
            self.selected_end_date = self.end_date_picker.value
            self.end_date_text.value = self.selected_end_date.strftime("%Y-%m-%d")
        self.page.update()

    def _on_team_selected(self, e):
        """Maneja la selección de un equipo en el dropdown."""
        self.selected_team = e.control.value
        self.page.update()

    def _on_league_selected(self, e):
        """Maneja la selección de una liga en el dropdown."""
        self.selected_league = e.control.value
        self.page.update()

    def _apply_filters(self, e):
        """
        Recopila los filtros seleccionados y los pasa a la función de callback.
        """
        filters = {}
        if self.selected_start_date:
            filters["start_date"] = self.selected_start_date.isoformat() + "Z"
        if self.selected_end_date:
            # Para incluir todo el día de la fecha final, sumar 1 día y usar <
            end_of_day = self.selected_end_date + timedelta(days=1) - timedelta(microseconds=1)
            filters["end_date"] = end_of_day.isoformat() + "Z"
        if self.selected_team:
            filters["team"] = self.selected_team
        if self.selected_league:
            filters["league"] = self.selected_league

        self.on_apply_filters(filters)

    def _clear_filters(self, e):
        """
        Limpia todos los filtros seleccionados y llama a la función de callback.
        """
        self.selected_start_date = None
        self.selected_end_date = None
        self.selected_team = None
        self.selected_league = None

        self.start_date_text.value = "Seleccionar fecha de inicio"
        self.end_date_text.value = "Seleccionar fecha de fin"
        self.team_dropdown.value = None
        self.league_dropdown.value = None

        self.on_clear_filters()
        self.page.update()

    def did_mount(self):
        """Se llama cuando el componente se monta en la página."""
        self.page.overlay.append(self.start_date_picker)
        self.page.overlay.append(self.end_date_picker)
        self.page.update()

    def will_unmount(self):
        """Se llama cuando el componente se desmonta de la página."""
        self.page.overlay.remove(self.start_date_picker)
        self.page.overlay.remove(self.end_date_picker)
        self.page.update()

    def update_dropdown_options(self, unique_teams, unique_leagues):
        """Actualiza las opciones de los dropdowns de equipos y ligas."""
        self.unique_teams = unique_teams
        self.unique_leagues = unique_leagues

        self.team_dropdown.options = [ft.dropdown.Option(team) for team in sorted(self.unique_teams)]
        self.league_dropdown.options = [ft.dropdown.Option(league) for league in sorted(self.unique_leagues)]
        self.page.update()