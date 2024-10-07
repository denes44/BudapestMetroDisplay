import logging
import math
import os
import tkinter as tk
from tkinter import ttk
from typing import Optional

from BudapestMetroDisplay import bkk_opendata

logger = logging.getLogger(__name__)


def on_closing():
    """Handle the GUI window close event."""
    logger.info("GUI window closed, stopping application...")
    root.destroy()


# Create the main window
root = tk.Tk()
root.title("BudapestMetroDisplay LED Test GUI")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create a Canvas to draw on
canvas = tk.Canvas(root, width=700, height=1000)
canvas.pack()

# Background image
background_image_path = "../../resources/gui_bg.png"
if os.path.exists(background_image_path):
    background_image = tk.PhotoImage(file=background_image_path)
    # Set the image as the background on the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)

# Example positions for LEDs (list of tuples: (x, y))
led_positions = [
    (418.06, 960.43, -3),  # (376.26 * 1.1111, 864.39 * 1.1111, -3)
    (380.00, 848.43, -25),  # (342.00 * 1.1111, 763.59 * 1.1111, -25)
    (345.91, 780.33, -28),  # (310.32 * 1.1111, 702.30 * 1.1111, -28)
    (308.60, 894.78, -2),  # (277.74 * 1.1111, 805.50 * 1.1111, -2)
    (305.23, 752.33, -7),  # (274.71 * 1.1111, 677.70 * 1.1111, -7)
    (290.93, 698.94, -25),  # (261.24 * 1.1111, 628.05 * 1.1111, -25)
    (46.86, 810.36, -346),  # (42.18 * 1.1111, 729.33 * 1.1111, -346)
    (101.56, 802.86, -22),  # (91.41 * 1.1111, 722.58 * 1.1111, -22)
    (164.00, 737.57, -79),  # (147.60 * 1.1111, 663.81 * 1.1111, -79)
    (170.43, 713.11, -73),  # (153.39 * 1.1111, 641.70 * 1.1111, -73)
    (204.13, 675.03, -58),  # (183.72 * 1.1111, 607.53 * 1.1111, -58)
    (219.99, 651.00, -53),  # (197.49 * 1.1111, 585.90 * 1.1111, -53)
    (243.00, 628.83, -55),  # (218.70 * 1.1111, 565.95 * 1.1111, -55)
    (289.43, 603.56, -14),  # (260.49 * 1.1111, 543.21 * 1.1111, -14)
    (317.43, 582.60, -340),  # (285.69 * 1.1111, 524.70 * 1.1111, -340)
    (60.10, 543.24, -90),  # (54.09 * 1.1111, 489.81 * 1.1111, -90)
    (60.07, 502.76, -58),  # (54.06 * 1.1111, 452.49 * 1.1111, -58)
    (126.21, 504.40, -340),  # (114.09 * 1.1111, 453.96 * 1.1111, -340)
    (164.43, 511.73, -354),  # (147.99 * 1.1111, 460.56 * 1.1111, -354)
    (204.35, 568.00, -270),  # (183.45 * 1.1111, 511.20 * 1.1111, -270)
    (231.72, 592.00, -5),  # (208.53 * 1.1111, 532.80 * 1.1111, -5)
    (284.00, 571.00, -23),  # (255.60 * 1.1111, 514.80 * 1.1111, -23)
    (326.40, 554.12, -15),  # (293.76 * 1.1111, 499.74 * 1.1111, -15)
    (457.96, 550.43, -9),  # (411.15 * 1.1111, 495.39 * 1.1111, -9)
    (524.00, 543.00, -8),  # (471.60 * 1.1111, 488.70 * 1.1111, -8)
    (600.00, 530.76, -9),  # (540.00 * 1.1111, 477.57 * 1.1111, -9)
    (668.34, 518.94, -10),  # (602.10 * 1.1111, 467.04 * 1.1111, -10)
    (127.66, 454.77, -2),  # (114.90 * 1.1111, 409.29 * 1.1111, -2)
    (136.32, 358.90, -342),  # (122.79 * 1.1111, 323.01 * 1.1111, -342)
    (152.50, 325.54, -323),  # (137.25 * 1.1111, 293.19 * 1.1111, -323)
    (162.33, 285.92, -2),  # (146.10 * 1.1111, 257.31 * 1.1111, -2)
    (161.91, 208.88, -30),  # (145.71 * 1.1111, 186.99 * 1.1111, -30)
    (155.51, 169.87, -340),  # (139.65 * 1.1111, 151.89 * 1.1111, -340)
    (168.77, 99.99, -25),  # (151.59 * 1.1111, 89.19 * 1.1111, -25)
    (160.45, 48.83, -359),  # (144.15 * 1.1111, 43.50 * 1.1111, -359)
    (372.00, 117.71, -176),  # (336.00 * 1.1111, 105.54 * 1.1111, -176)
    (326.43, 126.00, -210),  # (293.79 * 1.1111, 113.40 * 1.1111, -210)
    (296.60, 198.77, -255),  # (266.91 * 1.1111, 178.59 * 1.1111, -255)
    (276.00, 273.98, -254),  # (248.40 * 1.1111, 246.60 * 1.1111, -254)
    (264.16, 316.54, -254),  # (237.84 * 1.1111, 284.79 * 1.1111, -254)
    (247.17, 374.21, -253),  # (222.54 * 1.1111, 336.75 * 1.1111, -253)
    (231.10, 426.43, -255),  # (208.29 * 1.1111, 383.79 * 1.1111, -255)
    (209.17, 476.00, -253),  # (188.25 * 1.1111, 428.40 * 1.1111, -253)
    (205.74, 532.06, -268),  # (185.16 * 1.1111, 478.65 * 1.1111, -268)
    (212.13, 600.93, -289),  # (190.92 * 1.1111, 540.84 * 1.1111, -289)
    (279.79, 652.03, -330),  # (251.82 * 1.1111, 587.73 * 1.1111, -330)
    (324.00, 677.56, -333),  # (291.60 * 1.1111, 609.15 * 1.1111, -333)
    (372.36, 702.26, -332),  # (335.70 * 1.1111, 632.04 * 1.1111, -332)
    (419.33, 727.78, -332),  # (377.40 * 1.1111, 654.00 * 1.1111, -332)
    (480.43, 760.00, -331),  # (432.39 * 1.1111, 684.00 * 1.1111, -331)
    (510.00, 775.31, -331),  # (459.00 * 1.1111, 698.79 * 1.1111, -331)
    (552.16, 798.82, -338),  # (496.95 * 1.1111, 718.95 * 1.1111, -338)
    (663.08, 811.83, -335),  # (597.03 * 1.1111, 730.65 * 1.1111, -335)
    (186.00, 571.52, -30),  # (168.00 * 1.1111, 515.37 * 1.1111, -30)
    (210.21, 550.66, -44),  # (189.81 * 1.1111, 495.60 * 1.1111, -44)
    (226.56, 535.76, -45),  # (203.82 * 1.1111, 482.13 * 1.1111, -45)
    (247.00, 515.00, -45),  # (222.30 * 1.1111, 464.40 * 1.1111, -45)
    (262.42, 500.56, -45),  # (236.19 * 1.1111, 450.51 * 1.1111, -45)
    (275.38, 486.56, -45),  # (248.46 * 1.1111, 437.91 * 1.1111, -45)
    (292.43, 470.33, -45),  # (263.19 * 1.1111, 423.00 * 1.1111, -45)
    (313.50, 449.33, -45),  # (282.15 * 1.1111, 404.40 * 1.1111, -45)
    (335.81, 425.88, -358),  # (301.23 * 1.1111, 383.49 * 1.1111, -358)
    (388.16, 414.16, -347),  # (349.35 * 1.1111, 371.73 * 1.1111, -347)
]
stop_names = {
    "BKK_F00965": "Vörösmarty tér",
    "BKK_F00963": "Deák Ferenc tér",
    "BKK_F00997": "Bajcsy-Zsilinszky út",
    "BKK_F01080": "Opera",
    "BKK_F01086": "Oktogon",
    "BKK_F01093": "Vörösmarty utca",
    "BKK_F01096": "Kodály körönd",
    "BKK_F01101": "Bajza utca",
    "BKK_F01103": "Hősök tere",
    "BKK_F02697": "Széchenyi fürdő",
    "BKK_F02888": "Mexikói út",
    "BKK_F00094": "Déli pályaudvar",
    "BKK_F02481": "Szél Kálmán tér",
    "BKK_F00063": "Batthyány tér",
    "BKK_F00959": "Kossuth Lajos tér",
    "BKK_F00961": "Deák Ferenc tér",
    "BKK_F01019": "Astoria",
    "BKK_F01292": "Blaha Lujza tér",
    "BKK_F01336": "Keleti pályaudvar",
    "BKK_F01325": "Puskás Ferenc Stadion",
    "BKK_F01743": "Pillangó utca",
    "BKK_F01749": "Örs vezér tere",
    "BKK_F00913": "Újpest-központ",
    "BKK_F00898": "Újpest-városkapu",
    "BKK_F02685": "Gyöngyösi utca",
    "BKK_F02683": "Forgách utca",
    "BKK_F02638": "Göncz Árpád városközpont",
    "BKK_F02681": "Dózsa György út",
    "BKK_F02614": "Lehel tér",
    "BKK_F00937": "Nyugati pályaudvar",
    "BKK_F00957": "Arany János utca",
    "BKK_F00955": "Deák Ferenc tér",
    "BKK_F00953": "Ferenciek tere",
    "BKK_F01290": "Kálvin tér",
    "BKK_F01189": "Corvin-negyed",
    "BKK_F01233": "Klinikák",
    "BKK_F01253": "Nagyvárad tér",
    "BKK_F01283": "Népliget",
    "BKK_F01494": "Ecseri út",
    "BKK_F01879": "Pöttyös utca",
    "BKK_F01542": "Határ út",
    "BKK_F01544": "Kőbánya-Kispest",
    "BKK_056215": "Kelenföldi pályaudvar",
    "BKK_056217": "Bikás park",
    "BKK_056219": "Újbuda-Központ",
    "BKK_056221": "Móricz Zsigmond körtér",
    "BKK_056223": "Szent Gellért tér",
    "BKK_056225": "Fővám tér",
    "BKK_056227": "Kálvin tér",
    "BKK_056229": "Rákóczi tér",
    "BKK_056231": "II. János Pál pápa tér",
    "BKK_056233": "Keleti pályaudvar",
    "BKK_09001187": "Batthyány tér",
    "BKK_09019190": "Margit híd",
    "BKK_09043192": "Szépvölgyi út",
    "BKK_09050194": "Tímár utca",
    "BKK_09068196": "Szentlélek tér",
    "BKK_09118198": "Filatorigát",
    "BKK_09084200": "Kaszásdűlű",
    "BKK_09100202": "Aquincum",
    "BKK_09159204": "Rómaifürdő",
    "BKK_19720236": "Közvágóhíd",
    "BKK_19726238": "Kén utca",
    "BKK_19729241": "Pesterzsébet felső",
    "BKK_09220224": "Boráros tér",
    "BKK_09221226": "Müpa",
    "BKK_09223229": "Szabadkikötő",
    "BKK_19795278": "Örs vezér tere",
    "BKK_19798281": "Rákosfalva",
    "BKK_F00964": "Vörösmarty tér",
    "BKK_F00962": "Deák Ferenc tér",
    "BKK_F00996": "Bajcsy-Zsilinszky út",
    "BKK_F01079": "Opera",
    "BKK_F01085": "Oktogon",
    "BKK_F01092": "Vörösmarty utca",
    "BKK_F01095": "Kodály körönd",
    "BKK_F01100": "Bajza utca",
    "BKK_F01102": "Hősök tere",
    "BKK_F02696": "Széchenyi fürdő",
    "BKK_F02887": "Mexikói út",
    "BKK_F00093": "Déli pályaudvar",
    "BKK_F02480": "Szél Kálmán tér",
    "BKK_F00062": "Batthyány tér",
    "BKK_F00958": "Kossuth Lajos tér",
    "BKK_F00960": "Deák Ferenc tér",
    "BKK_F01018": "Astoria",
    "BKK_F01291": "Blaha Lujza tér",
    "BKK_F01335": "Keleti pályaudvar",
    "BKK_F01324": "Puskás Ferenc Stadion",
    "BKK_F01742": "Pillangó utca",
    "BKK_F00912": "Újpest-központ",
    "BKK_F00897": "Újpest-városkapu",
    "BKK_F02684": "Gyöngyösi utca",
    "BKK_F02682": "Forgách utca",
    "BKK_F02637": "Göncz Árpád városközpont",
    "BKK_F02680": "Dózsa György út",
    "BKK_F02613": "Lehel tér",
    "BKK_F00936": "Nyugati pályaudvar",
    "BKK_F00956": "Arany János utca",
    "BKK_F00954": "Deák Ferenc tér",
    "BKK_F00952": "Ferenciek tere",
    "BKK_F01289": "Kálvin tér",
    "BKK_F01188": "Corvin-negyed",
    "BKK_F01232": "Klinikák",
    "BKK_F01252": "Nagyvárad tér",
    "BKK_F01282": "Népliget",
    "BKK_F01493": "Ecseri út",
    "BKK_F01878": "Pöttyös utca",
    "BKK_F01541": "Határ út",
    "BKK_F01543": "Kőbánya-Kispest",
    "BKK_056216": "Kelenföldi pályaudvar",
    "BKK_056218": "Bikás park",
    "BKK_056220": "Újbuda-Központ",
    "BKK_056222": "Móricz Zsigmond körtér",
    "BKK_056224": "Szent Gellért tér",
    "BKK_056226": "Fővám tér",
    "BKK_056228": "Kálvin tér",
    "BKK_056230": "Rákóczi tér",
    "BKK_056232": "II. János Pál pápa tér",
    "BKK_056234": "Keleti pályaudvar",
    "BKK_09001188": "Batthyány tér",
    "BKK_09019191": "Margit híd",
    "BKK_09043193": "Szépvölgyi út",
    "BKK_09050195": "Tímár utca",
    "BKK_09068197": "Szentlélek tér",
    "BKK_09118199": "Filatorigát",
    "BKK_09084201": "Kaszásdűlű",
    "BKK_09100203": "Aquincum",
    "BKK_09159205": "Rómaifürdő",
    "BKK_19720237": "Közvágóhíd",
    "BKK_19726239": "Kén utca",
    "BKK_19729240": "Pesterzsébet felső",
    "BKK_09220225": "Boráros tér",
    "BKK_09221227": "Müpa",
    "BKK_09223228": "Szabadkikötő",
    "BKK_19795279": "Örs vezér tere",
    "BKK_19798282": "Rákosfalva",
    "BKK_09001189": "Batthyány tér",
    "BKK_19795280": "Örs vezér tere",
}

led_rectangles: list[Optional[int]] = [None] * len(led_positions)

# Width and height of the rectangles (LEDs)
RECT_WIDTH = 10
RECT_HEIGHT = 10


# Function to convert the LED's RGB state to a color string
def rgb_to_color_string(color):
    # Converts RGB values to hex format
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


# Function to get rotated points of a rectangle
def get_rotated_rectangle(x, y, width, height, rotation):
    # Calculate half-width and half-height
    hw, hh = width / 2, height / 2

    # Define the four corners of the rectangle (relative to center)
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]

    # Convert rotation from degrees to radians
    angle_rad = math.radians(rotation)

    # Apply rotation to each corner using a rotation matrix
    rotated_corners = [
        (
            x + (corner[0] * math.cos(angle_rad) - corner[1] * math.sin(angle_rad)),
            y + (corner[0] * math.sin(angle_rad) + corner[1] * math.cos(angle_rad)),
        )
        for corner in corners
    ]

    return rotated_corners


# Function to draw the LEDs as circles
def draw_leds():
    from BudapestMetroDisplay.led_control import get_led_color

    for i, (x, y, rotation) in enumerate(led_positions):
        # Get the color from led_states (convert from flat list to RGB)
        color = rgb_to_color_string(get_led_color(i))

        # Get the rotated rectangle coordinates
        points = get_rotated_rectangle(x, y, RECT_WIDTH, RECT_HEIGHT, rotation)

        # Draw the rectangle with rotation
        led_rectangles[i] = canvas.create_polygon(points, fill=color, outline="white")
    logging.debug("Drawing of the LED on the GUI is finished")


def change_gui_led_color(led_index, color):
    canvas.itemconfig(led_rectangles[led_index], fill=rgb_to_color_string(color))


def filter_jobs_by_route(job_table, scheduler, route_id):
    """Filter and update job table with jobs for the given route_id."""
    for row in job_table.get_children():
        job_table.delete(row)

    for job in scheduler.get_jobs():
        args = job.args if job.args else (None, None, None, None, None)
        if args[1] == route_id:  # Check if the route_id matches
            job_table.insert(
                "",
                "end",
                values=(
                    job.id,
                    job.name,
                    job.next_run_time,
                    job.trigger,
                    # args[0],
                    stop_names[args[0]],
                    args[1],
                    args[2],
                    args[3],
                    args[4],
                ),
            )


def create_filtered_job_table(scheduler, route_id):
    """Create a job schedule window filtered by route_id."""
    job_window = tk.Toplevel(root)
    job_window.title(f"Job Schedule for {route_id}")

    columns = (
        "ID",
        "Name",
        "Next Run Time",
        "Trigger",
        "stop_id",
        "route_id",
        "trip_id",
        "job_time",
        "delay",
    )
    job_table = ttk.Treeview(job_window, columns=columns, show="headings")
    job_table.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        job_table.heading(col, text=col)
        job_table.column(col, width=100, anchor=tk.CENTER)

    filter_jobs_by_route(job_table, scheduler, route_id)


def create_route_buttons(my_canvas):
    """Create buttons for each route_id in ROUTE_COLORS."""
    from BudapestMetroDisplay.led_control import ROUTE_COLORS

    row, col = 0, 0
    x_offset, y_offset = (
        10,
        10,
    )  # Offset to position buttons with some space from the top-left corner
    for route_id, color in ROUTE_COLORS.items():
        color_hex = rgb_to_color_string(color)
        btn = tk.Button(
            my_canvas,
            text=route_id,
            bg=color_hex,
            command=lambda rid=route_id:  # type: ignore[misc]
            create_filtered_job_table(
                bkk_opendata.departure_scheduler, rid
            ),
        )
        my_canvas.create_window(
            x_offset + col * 110, y_offset + row * 40, window=btn, anchor="nw"
        )  # Positioning buttons
        col += 1
        if col == 1:  # Adjust for buttons per row
            col = 0
            row += 1


def start_gui():
    draw_leds()
    create_route_buttons(canvas)
    root.mainloop()
    logging.debug("GUI started")
