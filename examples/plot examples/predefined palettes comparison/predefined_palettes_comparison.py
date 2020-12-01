from python2latex.document import Section
from python2latex.tex_base import TexObject, build
from python2latex import Document, TexEnvironment
from python2latex import Plot, Palette, LinearColorMap, predefined_cmaps, predefined_palettes
from python2latex.utils import JCh2rgb, rgb2JCh, hsb2JCh, JCh2hsb
import numpy as np
from matplotlib.colors import hsv_to_rgb


class Node(TexObject):
    def __init__(self, pos, text='', fill=None, minimum_width='.9cm', minimum_height='.9cm'):
        super().__init__(self)
        self.pos = pos
        self.text = text
        self.fill = fill or 'none'
        self.minimum_width = minimum_width
        self.minimum_height = minimum_height

    def build(self):
        return f'\\node[fill={build(self.fill, self)}, minimum width={self.minimum_width}, minimum height={self.minimum_height}] at {self.pos} {{{self.text}}};'


def plot_palette(doc, palette_name):
    # Create plots to compare the cmaps
    plot = doc.new(Plot(plot_path=filepath,
                        plot_name=filename+'_'+palette_name,
                        lines='3pt',
                        height='6cm',
                        ))
    cmap = predefined_cmaps[palette_name]
    palette = predefined_palettes[palette_name]

    n_colors = 25
    interp_param = np.linspace(0, 1, n_colors+1)

    for i, JCh_color in zip(range(n_colors), palette):
        # Plot the hue(h)-lightness(J) space
        cmap.color_model = 'rgb'
        J1, C1, h1 = cmap(interp_param[i])
        J2, C2, h2 = cmap(interp_param[i+1])
        cmap.color_model = 'JCh'
        plot.add_plot([h1, h2], [J1, J2], color=JCh_color, line_cap='round')

    plot.x_label = 'Hue angle $h$'
    plot.y_label = 'Lightness $J$'

    plot.caption = f'The \\texttt{{{palette_name}}} color map'


    for n_colors in [2, 3, 4, 5, 6, 9]:
        doc += f'{n_colors} colors: \\hspace{{10pt}}'
        tikzpicture = doc.new(TexEnvironment('tikzpicture'))
        for i, color in zip(range(n_colors), palette):
            tikzpicture += Node((i,0), fill=color)
        doc += '\n'



if __name__ == "__main__":
    # Create document
    filepath = './examples/plot examples/predefined palettes comparison/'
    filename = 'predefined_palettes_comparison'
    doc = Document(filename, doc_type='article', filepath=filepath)

    # Insert title
    center = doc.new(TexEnvironment('center'))
    center += r"\huge \bf Predefined color maps and palettes"

    doc += """\\noindent
    python2latex provides three color maps natively. They are defined in the JCh axes of the CIECAM02 color model, which is linear to human perception of colors. Moreover, three ``dynamic'' palettes have been defined, one for each color map. They are dynamic in that the range of colors used to produce the palette changes with the number of colors needed. This allows for a good repartition of hues and brightness for all choices of number of colors.

    All three color maps have been designed to be colorblind friendly for all types of colorblindness. To do so, all color maps are only increasing or decreasing in lightness, which helps to distinguish hues that may look similar to a colorblind. This also has the advantage that the palettes are also viable in levels of gray.
    """

    # First section
    sec = doc.new_section(r'The \texttt{holi} color map')
    sec += """
    The holi color map is designed to provide a set of easily distinguishable hues for any needed number of colors. It is optimized for palettes of 5 or 6 colors, but other numbers of color also generate very viable palettes. It is colorblind friendly for all types of colorblindness for up to 5 colors, but can still be acceptable for more colors.

    Below is a graph of the color map in the J-h axes of the CIECAM02 color model, followed by the colors generated according to the number of colors needed.
    """
    plot_palette(doc, 'holi')
    doc += r'\clearpage'

    sec = doc.new_section(r'The \texttt{aube} color map')
    plot_palette(doc, 'aube')
    doc += r'\clearpage'

    sec = doc.new_section(r'The \texttt{aurore} color map')
    plot_palette(doc, 'aurore')
    doc += r'\clearpage'

    tex = doc.build()
