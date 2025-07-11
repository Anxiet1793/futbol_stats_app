# main.py

import flet as ft
from db.mongo_config import connect_to_mongodb, close_mongodb_connection
from ui.dashboard import Dashboard

def main(page: ft.Page):
    """
    Función principal de la aplicación Flet.
    Configura la página y añade el Dashboard.
    """
    page.title = "Futbol Stats App"
    page.vertical_alignment = ft.CrossAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT # Puedes cambiar a DARK si prefieres

    # Conectar a MongoDB al iniciar la aplicación
    print("Intentando conectar a MongoDB...")
    db_instance = connect_to_mongodb()
    if not db_instance:
        page.add(ft.Text("Error: No se pudo conectar a la base de datos. Verifique su MONGO_URI.", color=ft.colors.RED_500))
        page.update()
        return

    # Crear una instancia del Dashboard
    dashboard = Dashboard()

    # Añadir el Dashboard a la página
    page.add(
        ft.Container(
            content=dashboard,
            expand=True,
            alignment=ft.alignment.center,
            padding=20
        )
    )

    # Función para manejar el cierre de la aplicación
    def on_page_close(e):
        print("Cerrando aplicación Flet y conexión a MongoDB...")
        close_mongodb_connection()
        page.window_destroy() # Cierra la ventana de la aplicación

    page.on_window_event = on_page_close
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
    # Para ejecutar como una aplicación web en el navegador, usa:
    # ft.app(target=main, view=ft.WEB_BROWSER)