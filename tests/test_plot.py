import pytest
from pytest import fixture
from inspect import cleandoc
import os, shutil

from python2latex.plot import Plot, LinePlot, MatrixPlot, _Plot
from python2latex.color import Color
from python2latex.document import Document


class TestPlot:
    def teardown(self):
        _Plot.id_number = -1

    def test_default_plot(self):
        assert Plot(plot_name='plot_test').build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_add_plot_with_legend(self):
        plot = Plot(plot_name='plot_test')
        plot.add_plot(list(range(10)), list(range(10)), 'red', legend='Legend', line_width='2pt')
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[red, line width=2pt] table[x=x0, y=y0, col sep=comma]{./plot_test.csv};
            \addlegendentry{Legend};
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_add_plot_without_legend(self):
        plot = Plot(plot_name='plot_test')
        plot.add_plot(list(range(10)), list(range(10)), 'red', line_width='2pt')
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[red, forget plot, line width=2pt] table[x=x0, y=y0, col sep=comma]{./plot_test.csv};
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_add_plot_with_color_obj(self):
        plot = Plot(plot_name='plot_test')
        color = Color(.1,.2,.3, 'spam')
        plot.add_plot(list(range(10)), list(range(10)), color, legend='Legend', line_width='2pt')
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, every axis plot/.append style={line width=1.25pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=major]
            \addplot[spam, line width=2pt] table[x=x0, y=y0, col sep=comma]{./plot_test.csv};
            \addlegendentry{Legend};
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('plot_test.csv')

    def test_save_csv_to_right_path(self):
        filepath = './some_doc_path/'
        plotpath = filepath + 'plot_path/'
        plot_name = 'plot_name'
        plot = Plot([1,2,3], [1,2,3], plot_name=plot_name, plot_path=plotpath)
        plot.build()
        assert os.path.exists(plotpath + plot_name + '.csv')
        shutil.rmtree(filepath)

    def test_build_pdf_to_other_relative_path(self):
        filepath = './some_doc_path/'
        plotpath = filepath + 'plot_path/'
        doc_name = 'Doc name'
        plot_name = 'plot_name'
        doc = Document(doc_name, filepath=filepath)
        plot = doc.new(Plot([1,2,3], [1,2,3], plot_name=plot_name, plot_path=plotpath))
        try:
            doc.build(show_pdf=False)
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
            assert os.path.exists(plotpath + plot_name + '.csv')
        finally:
            shutil.rmtree('./some_doc_path/')

    def test_add_matrix_plot(self):
        plot = Plot(plot_name='matrix_plot_test', grid=False, lines=False)
        plot.add_matrix_plot(list(range(10)), list(range(10)), [[i for i in range(10)] for _ in range(10)])
        assert plot.build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, colorbar, every axis plot/.append style={line width=0pt, mark size=0pt}, width=.8\textwidth, height=.45\textwidth, grid=none]
            \addplot[matrix plot*, point meta=explicit, mesh/rows=10, mesh/cols=10] table[x=x0, y=y0, meta=z0, col sep=comma]{./matrix_plot_test.csv};
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
        os.remove('matrix_plot_test.csv')

    def test_build_pdf_with_matrix_plot(self):
        filepath = './some_doc_path/'
        plotpath = filepath + 'plot_path/'
        doc_name = 'Doc name'
        plot_name = 'plot_name'
        doc = Document(doc_name, filepath=filepath)
        X = list(range(10))
        Y = list(range(10))
        Z = [[i for i in range(10)] for _ in range(10)]
        plot = doc.new(Plot(plot_name=plot_name, plot_path=plotpath, grid=False, lines=False, enlargelimits='false'))
        plot.add_matrix_plot(X, Y, Z)
        try:
            doc.build(show_pdf=False)
            assert os.path.exists(filepath + doc_name + '.tex')
            assert os.path.exists(filepath + doc_name + '.pdf')
            assert os.path.exists(plotpath + plot_name + '.csv')
        finally:
            # shutil.rmtree('./some_doc_path/')
            pass


class TestLinePlot:
    def teardown(self):
        _Plot.id_number = -1

    def test_build_with_legend(self):
        lineplot = LinePlot([1,2,3], [4,5,6], 'red', 'dashed', legend='Legend', line_width='2pt')
        lineplot.plot_filepath = './some/path/file.csv'
        assert lineplot.build() == cleandoc(
            r"""
            \addplot[red, dashed, line width=2pt] table[x=x0, y=y0, col sep=comma]{./some/path/file.csv};
            \addlegendentry{Legend};
            """)

    def test_build_without_legend(self):
        lineplot = LinePlot([1,2,3], [4,5,6], 'red', 'dashed', line_width='2pt')
        lineplot.plot_filepath = './some/path/file.csv'
        assert lineplot.build() == cleandoc(
            r"""
            \addplot[red, dashed, forget plot, line width=2pt] table[x=x0, y=y0, col sep=comma]{./some/path/file.csv};
            """)


class TestMatrixPlot:
    def teardown(self):
        _Plot.id_number = -1

    def test_build_with_legend(self):
        lineplot = MatrixPlot([1,2,3], [4,5,6], [list(range(3)) for _ in range(3)])
        lineplot.plot_filepath = './some/path/file.csv'
        assert lineplot.build() == cleandoc(
            r"""
            \addplot[matrix plot*, point meta=explicit, mesh/rows=3, mesh/cols=3] table[x=x0, y=y0, meta=z0, col sep=comma]{./some/path/file.csv};
            """)
