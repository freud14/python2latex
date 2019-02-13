import numpy as np
from py2tex import TexEnvironment


class Table(TexEnvironment):
    """
    Implements a floating 'table' environment. Wraps many features for easy usage and flexibility, such as:
        - Supports slices to set items.
        - Easy and automatic multirow and multicolumn cells.
        - Automatically highlights best value inside a region of the table.
    To do so, the brackets access ("__getitem__") have been repurposed to select an area and returns the table with the selected area. To access the actual data inside the table, use the 'data' attribute.

    TODO:
        - Split 'highlight_best' into a 'highlight' method to allow manual highlighting.
        - Maybe: Add a 'insert_row' and 'insert_column' methods.
    """
    def __init__(self, shape=(1,1), alignment='c', float_format='.2f', position='h!', as_float_env=True, **kwargs):
        """
        Args:
            shape (tuple of 2 ints): Shape of the table.
            alignment (str or sequence of str, either 'c', 'r', or 'l'): Alignment of the text inside the columns. If a sequence, it should be the same length as the number of columns. If only a string, it will be used for all columns.
            float_format (str): Standard Python float formating available.
            as_float_env (bool): If True (default), will wrap a 'tabular' environment with a floating 'table' environment. If False, only the 'tabular' is constructed.
            position (str, either 'h', 't', 'b', with optional '!'): Position of the float environment. Default is 't'. Combinaisons of letters allow more flexibility. Only valid if as_float_env is True.
            kwargs: See TexEnvironment keyword arguments.
        """
        self.as_float_env = as_float_env
        super().__init__('table', options=position, label_pos='bottom', **kwargs)
        if self.as_float_env:
            self.body.append(r'\centering')
        else:
            self.head, self.tail = '', ''
        self.tabular = TexEnvironment('tabular')
        self.add_package('booktabs')
        self.body.append(self.tabular)
        self.caption = ''

        self.shape = shape
        self.alignment = [alignment]*shape[1] if len(alignment) == 1 else alignment
        self.float_format = float_format
        self.data = np.full(shape, '', dtype=object)

        self.rules = {}
        self.multicells = []
        self.highlights = []

    def __getitem__(self, idx):
        return SelectedArea(self, idx)

    def __setitem__(self, idx, value):
        selected_area = self[idx]
        if isinstance(value, (str, int, float)) and selected_area.size > 1:
            # There are multirows or multicolumns to treat
            selected_area.multicell(value)
        else:
            self.data[idx] = value

    def _build_rule(self, start, end, trim):
        if start is None and end is None and not trim:
            rule = "\midrule"
        else:
            rule = "\cmidrule"
            if trim:
                rule += f"({trim})"
            # start, end, step = slice(start, end).indices(self.shape[1])
            rule += f"{{{start+1}-{end}}}"
        return rule

    def _apply_multicells(self, table_format):
        for idx, v_align, h_align, v_shift in self.multicells:

            start_i, stop_i, step = idx[0].indices(self.shape[0])
            start_j, stop_j, step = idx[1].indices(self.shape[1])

            table_format[start_i, slice(start_j, stop_j-1)] = ''
            cell_shape = table_format[idx].shape

            if start_i == stop_i - 1:
                self.data[start_i, start_j] = f"\multicolumn{{{cell_shape[1]}}}{{{h_align}}}{{{self.data[start_i, start_j]}}}"
            else:
                shift = ''
                if v_shift:
                    shift = f'[{v_shift}]'
                self.data[start_i, start_j] = f"\multirow{{{cell_shape[0]}}}{{{v_align}}}{shift}{{{self.data[start_i, start_j]}}}"

            if start_j < stop_j - 1 and start_i < stop_i - 1:
                self.data[start_i, start_j] = f"\multicolumn{{{cell_shape[1]}}}{{{h_align}}}{{{self.data[start_i, start_j]}}}"

        return table_format

    def build(self):
        row, col = self.data.shape
        self.tabular.head += f"{{{''.join(self.alignment)}}}\n\\toprule"
        self.tabular.tail = '\\bottomrule\n' + self.tabular.tail

        # Format floats
        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, float):
                    entry = f'{{value:{self.float_format}}}'.format(value=value)
                else:
                    entry = str(value)
                self.data[i,j] = entry

        # Apply highlights
        for i, j, highlight in self.highlights:
            if highlight == 'bold':
                command = "\\textbf{{{0}}}"
            elif highlight == 'italic':
                command = "\\textit{{{0}}}"
            self.data[i,j] = command.format(self.data[i,j])

        # Build the tabular
        table_format = np.array([[' & ']*(self.shape[1]-1) + ['\\\\']]*self.shape[0], dtype=str)
        table_format = self._apply_multicells(table_format)
        for i, (row, row_format) in enumerate(zip(self.data, table_format)):
            self.tabular.body.append(''.join(item for pair in zip(row, row_format) for item in pair))
            if i in self.rules:
                for rule in self.rules[i]:
                    rule = self._build_rule(*rule)
                    self.tabular.body.append(rule)
        self.tabular.build()

        if self.caption and self.as_float_env:
            self.body.append(f"\caption{{{self.caption}}}")
        return super().build()


class SelectedArea:
    """
    Represents a selected area in a table. Contains a reference to the actual table and methods to apply on an area of the table.
    """
    def __init__(self, table, idx):
        self.table = table
        self.slices = self._convert_idx_to_slice(idx)

    def _convert_idx_to_slice(self, idx):
        if isinstance(idx, tuple):
            i, j = idx
        else:
            i, j = idx, slice(None)
        if isinstance(i, int):
            i = slice(i, i+1)
        if isinstance(j, int):
            j = slice(j, j+1)
        return i, j

    @property
    def size(self):
        return self.table.data[self.slices].size

    @property
    def idx(self):
        start_i, stop_i, step_i = self.slices[0].indices(self.table.shape[0])
        start_j, stop_j, step_j = self.slices[1].indices(self.table.shape[1])
        return (start_i, start_j), (stop_i, stop_j)

    def add_rule(self, position='below', trim_right=False, trim_left=False):
        """
        Adds a rule below or above the selected area of the table.

        Args:
            position (str, either 'below' or 'above'): Position of the rule below or above the selected area.
            trim_left (bool or str): Whether to trim the left end of the rule or not. If True, default trim length is used ('.5em'). If a string, can be any valid LaTeX distance.
            trim_right (bool or str): Same a trim_left, but for the right end.
        """
        r = 'r' if trim_right else ''
        if isinstance(trim_right, str):
            r += f"{{{trim_right}}}"
        l = 'l' if trim_left else ''
        if isinstance(trim_left, str):
            l += f"{{{trim_left}}}"

        (i_start, j_start), (i_stop, j_stop) = self.idx
        if position == 'below':
            i = i_stop - 1
        else:
            i = i_start - 1

        if i not in self.table.rules:
            self.table.rules[i] = []
        self.table.rules[i].append((j_start, j_stop, r+l))

    def multicell(self, value, v_align='*', h_align='c', v_shift=None):
        """
        Merges the selected area into a single cell.

        Args:
            value (str, int or float): Value of the cell.
            v_align (str, ex. '*'): '*' means the same alignment of the other cells in the row. See LaTeX 'multirow' documentation.
            h_align (str, ex. 'c', 'l' or 'r'): See LaTeX 'multicolumn' documentation.
            v_shift (str, any valid length of LaTeX): Vertical shift of the text position of multirow merging.
        """
        self.table.add_package('multicol')
        self.table.add_package('multirow')

        self.table.data[self.slices] = '' # Erase old value
        multicell_params = (self.slices, v_align, h_align, v_shift)
        self.table.multicells.append(multicell_params) # Save position of multiple cells span

        self.table.data[self.idx[0]] = value

    def highlight_best(self, mode='high', highlight='bold', atol=5e-3, rtol=0):
        """
        Highlights the best value(s) inside the selected area of the table. Ignores text. If multiple values are equal to an absolute tolerance of atol and relative tolerance of rtol, both are highlighted.

        Args:
            mode (str, either 'high' or 'low'): Determines what is the best value.
            highlight (str, either 'bold' or 'italic'): The best value will be highlighted following this parameter.
            atol (float): Absolute tolerance when comparing best.
            atol (float): Relative tolerance when comparing best.
        """
        best_idx = [(None, None)]
        if mode == 'high':
            best = -np.inf
            value_is_better_than_best = lambda value, best: value > best
        elif mode == 'low':
            best = np.inf
            value_is_better_than_best = lambda value, best: value < best

        for i, row in enumerate(self.table.data[self.slices]):
            for j, value in enumerate(row):
                if isinstance(value, (float, int)) and value_is_better_than_best(value, best):
                    best_idx = [(i, j)]
                    best = value
                elif isinstance(value, (float, int)) and np.isclose(value, best, rtol, atol):
                    best_idx.append((i, j))

        if best_idx[0][0] is None: return # No best have been found (i.e. no floats or ints in selected area)
        start_i, start_j = self.idx[0]
        for i, j in best_idx:
            self.table.highlights.append((i + start_i, j + start_j, highlight))


if __name__ == "__main__":
    from py2tex import Document
    doc = Document(filename='Test', doc_type='article', options=('12pt',))

    sec = doc.new_section('Testing tables')
    sec.add_text("This section tests tables.")

    col, row = 4, 4
    data = np.random.rand(row, col)

    table = sec.new(Table(shape=(row+1, col+1), alignment='c', float_format='.2f'))
    table.caption = 'test' # Set a caption if desired
    table[1:,1:] = data # Set entries with a slice
    table[1,1] = 1.0
    table[1,2] = 0.995

    table[2:4,2:4] = 'test' # Set multicell areas with a slice too
    table[0,1:].multicell('Title', h_align='c') # Set a multicell with custom parameters
    table[1:,0].multicell('Types', v_align='*', v_shift='-2pt')

    table[0,1:3].add_rule(trim_left=True, trim_right='.3em') # Add rules with parameters where you want
    table[0,3:].add_rule(trim_left='.3em', trim_right=True)

    table[1].highlight_best()
    table[4].highlight_best('low')

    tex = doc.build()
    # print(tex)
