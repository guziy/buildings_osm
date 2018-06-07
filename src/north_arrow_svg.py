from pathlib import Path

import svgutils.transform as sg


def get_fig_size(fig):
    return [float(s[:-2]) for s in fig.get_size()]


def north_arrow(img_file_in: Path, img_file_out: Path=None, rotation_angle=0):
    if img_file_out is None:
        img_file_out = img_file_in.parent / f"{img_file_in.name[:-4]}_north_arrow.svg"

    arrow_fig_path = Path(__file__).parent.parent / "north_arrow.svg"


    # load matpotlib-generated figures
    fig1 = sg.fromfile(str(img_file_in))
    fig2 = sg.fromfile(str(arrow_fig_path))

    #create new SVG figure
    fig = sg.SVGFigure(fig1.get_size())

    w, h = get_fig_size(fig1)



    # get the plot objects
    plot1 = fig1.getroot()
    plot2 = fig2.getroot()



    print(fig2.get_size())
    x_label = 0.9 * w
    y_label = 0.8 * h
    plot2.scale_xy(x=0.5 * 0.05, y=0.05)

    w_fig2, h_fig2 = get_fig_size(fig2)
    plot2.moveto(x_label - w_fig2 / 2, y_label)

    print(fig2.get_size())


    n_text = sg.TextElement(0.9 * w, 0.8 * h, "N", size=12,
                            weight="bold", anchor="middle")

    fig.append([plot1, plot2])
    fig.append([n_text, ])

    fig.save(str(img_file_out))
