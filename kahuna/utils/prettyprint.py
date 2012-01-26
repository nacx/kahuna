#!/usr/bin/env jython

def max_width(table, index):
    """ Get the maximum width of the given column index. """
    return max([len(str(row[index])) for row in table])

def pprint_row(row, col_paddings):
    """ Pretty prints the given row. """
    for i in range(len(row)):
        value = str(row[i])
        col = value.ljust(col_paddings[i] + 1)
        print col,
    print

def pprint_header(table, col_paddings):
    """ Pretty prints the table header. """
    pprint_row(table[0], col_paddings)
    for i in range(len(table[0])):
        print "-" * col_paddings[i], "",
    print

def pprint_table(table):
    """ Pretty prints the given table. """
    # Get the column paddings
    col_paddings = []
    for i in range(len(table[0])):
        col_paddings.append(max_width(table, i))

    pprint_header(table, col_paddings)
    for row in table[1:]:
        pprint_row(row, col_paddings)

def pprint_vms(vms):
    """ Pretty prints the given virtual machine list. """
    table = [["id", "name", "cpu", "ram", "hd", "state", "vnc"]]
    for vm in vms:
        state = vm.getState()
        row = [vm.getId(), vm.getName(), vm.getCpu(), str(vm.getRam()) + " MB", state,
                str(vm.getHdInBytes() / 1024 / 1024) + " MB"]
        if not state.existsInHypervisor():
            row.append("-")
        else:
            row.append(vm.getVncAddress() + ":" + str(vm.getVncPort()))
        table.append(row)
    pprint_table(table)

def pprint_templates(templates):
    """ pretty prints the given template list. """
    table = [["id", "name", "disk type", "cpu", "ram", "hd", "disk file size"]]
    for template in templates:
        row = [template.getId(), template.getName(), template.getDiskFormatType(),
                template.getCpuRequired(), str(template.getRamRequired()) + " MB",
                str(template.getHdRequired() / 1024 / 1024) + " MB",
                str(template.getDiskFileSize() / 1024 / 1024) + " MB"]
        table.append(row)
    pprint_table(table)

