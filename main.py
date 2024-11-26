import flet as ft

from pressure_sensor import Sensor
from icecream import ic

import serial.tools.list_ports


def calculate_color(value, max_value=1500, min_green=64):
    value = max(0, min(value, max_value))
    ratio = value / max_value
    red = 0
    green = int(min_green + (255 - min_green) * ratio)
    blue = 0
    color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    return color


def main(page: ft.Page):
    page.title = "压力传感器"

    page.window.width = 500
    page.window.height = 600
    page.window.resizable = False
    page.window.maximizable = False

    sensor: Sensor | None = None

    def set_cell(index, number):
        r = index % 4  # 列
        c = index // 4  # 行
        container = column.controls[c].controls[r]
        container.bgcolor = calculate_color(number)
        container.content = ft.Text(str(number), color=ft.colors.BLACK)
        container.update()

    def set_cells(numbers: list):
        assert numbers.__len__() == 16, "个数不正确"
        for i, number in enumerate(numbers):
            set_cell(i, number)

    rows = []
    for i in range(4):
        columns = []
        for _ in range(4):
            rect = ft.Container(
                width=100,
                height=100,
                border_radius=10,
                bgcolor=ft.colors.BLUE_GREY_100,
                alignment=ft.alignment.center,
            )
            columns.append(rect)
        rows.append(ft.Row(columns))

    options = [
        ft.dropdown.Option("Option 1"),
        ft.dropdown.Option("Option 2"),
        ft.dropdown.Option("Option 3"),
    ]

    def on_dropdown_changed(e):
        nonlocal sensor
        sensor = Sensor(dropdown.value, callback=set_cells)

    devices = [
        ft.dropdown.Option(port.device) for port in serial.tools.list_ports.comports()
    ]

    dropdown = ft.Dropdown(
        options=devices,
        width=200,
        on_change=on_dropdown_changed,
    )

    if devices.__len__() != 0:
        dropdown.value = devices[0]

    page.add(column := ft.Column(rows))
    page.add(ft.Row([ft.Text("串口号:"), dropdown]))

    set_cells([0] * 16)


ft.app(target=main)
