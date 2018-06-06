from pathlib import Path

import svgutils.transform as sg

def north_arrow(img_file_in: Path, img_file_out: Path=None, rotation_angle=0):
    if img_file_out is None:
        img_file_out = img_file_in.parent / f"{img_file_in.name[:-4]}_north_arrow.svg"

    arrow_fig_path = Path(__file__).parent.parent / "north_arrow.svg"


    # load matpotlib-generated figures
    fig1 = sg.fromfile(str(img_file_in))
    fig2 = sg.fromfile(str(arrow_fig_path))

    #create new SVG figure
    fig = sg.SVGFigure(fig1.get_size())

    w, h = [float(s[:-2]) for s in fig1.get_size()]

    print(fig1.get_size())

    # get the plot objects
    plot1 = fig1.getroot()
    plot2 = fig2.getroot()
    plot2.moveto(0.9 * w, 0.8 * h, scale=0.05)
    plot2.scale_xy(x=0.5, y=1)


    n_text = sg.TextElement(0.9 * w, 0.7 * h, "N", size=12, weight="bold")

    fig.append([plot1, plot2])
    fig.append([n_text, ])

    fig.save(str(img_file_out))
