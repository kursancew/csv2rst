import csv
import sys
import textwrap
from optparse import OptionParser

def build_row_sep(widths, sep_line='-', sep_corner='+'):
    sep = [sep_corner]
    
    for w in widths:
        sep += [sep_line] * w
        sep += [sep_corner]
    return ''.join(sep)

def pad_line_and_add_pipe(line, width, last=False):
    """
    Pads to width or truncate, adding the | in the start
    """
    l = width - len(line)
    last_pipe = '|' if last else ''
    if l > 0:
        return '|' + line + ' ' * l + last_pipe
    else:
        return '|' + line[:width] + last_pipe
    
def write_output(table, widths, out, skip_title=False):
    title_sep = build_row_sep(widths, '=') + '\n'
    row_sep = build_row_sep(widths) + '\n'
    col_count = len(widths)

    out.write(row_sep)
    for table_row_i, row in enumerate(table):
        
        #first pass to sort out word wrapping
        wrapped_columns = []
        wrap_lines_max = 1
        r = 0
        for w, col in zip(widths, row):
            last = r == (col_count - 1)
            r += 1
            wrapped = [pad_line_and_add_pipe(x, w, last) for x in textwrap.wrap(col, w)]
            if len(wrapped) > wrap_lines_max:
                wrap_lines_max = len(wrapped)
            wrapped_columns.append(wrapped)
        
        #not output the table
        for i in range(wrap_lines_max):
            out_row = []
            for j in range(col_count):
                try:
                    out_row += [wrapped_columns[j][i]]
                except IndexError:
                    last_pipe = '|' if j == (col_count - 1) else ''
                    out_row += ['|' + ' ' * widths[j] + last_pipe]
             
            out_row += ['\n']
            
            line_str = ''.join(out_row)
            out.write(line_str)

        if not table_row_i and not skip_title:
            out.write(title_sep)
        else:
            out.write(row_sep)


def get_widths(table):
    
    widths = {}
    for row in table:
        for i, col in enumerate(row):
            w = widths.setdefault(i, 0)
            if len(col) > w:
                widths[i] = len(col)
    return [b for a, b in sorted(widths.items())]

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='i_file',
                      help='Read input from FILE instead of stdin', metavar='FILE')
    parser.add_option('-o', '--output', dest='o_file',
                      help='Write output to FILE instead of stdout', metavar='FILE')
    parser.add_option('-p', '--extrapadding', dest='padding',
                      help='Add N extra spaces after each line', metavar='N')
    parser.add_option('-w', '--wordwrap', dest='wordwrap',
                      help='Word-wrap at N chars', metavar='N')
    options, args = parser.parse_args()

    i_file = sys.stdin
    if options.i_file:
        i_file = open(options.i_file)
    
    o_file = sys.stdout
    if options.o_file:
        o_file = open(options.o_file, 'w')
    
    table = csv.reader(i_file)
    widths = get_widths(table)
    if options.padding:
        widths = [x + int(options.padding) for x in widths]
    
    if options.wordwrap:
        ww = int(options.wordwrap) 
        widths = [min(ww, x) for x in widths]
    
    i_file.seek(0)
    
    table = csv.reader(i_file)
    
    write_output(table, widths, o_file)
    
    
if __name__ == '__main__':
    main()
