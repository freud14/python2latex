import pytest
from pytest import fixture
from inspect import cleandoc

from py2tex.plot import Plot


class TestPlot:
    def test_default_plot(self):
        assert Plot().build() == cleandoc(
            r'''
            \begin{figure}[h!]
            \centering
            \begin{tikzpicture}
            \begin{axis}[grid style={dashed,gray!50}, axis y line*=left, axis x line*=bottom, no marks, width=.8\textwidth, height=.45\textwidth, grid=major]
            \end{axis}
            \end{tikzpicture}
            \end{figure}
            ''')
