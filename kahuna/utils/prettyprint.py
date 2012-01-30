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
    [pprint_row(row, col_paddings) for row in table[1:]]

def pprint_vms(vms, verbose=False):
    """ Pretty prints the given virtual machine list. """
    table = [["id", "name", "cpu", "ram", "hd", "state", "vnc", "template"]]
    if verbose:
        table[0].extend(["virtual appliance", "virtual datacenter", "enterprise"])
    for vm in vms:
        state = vm.getState()
        row = [vm.getId(), vm.getName(), vm.getCpu(), str(vm.getRam()) + " MB",
                str(vm.getHdInBytes() / 1024 / 1024) + " MB", state]
        if not state.existsInHypervisor():
            row.append("-")
        else:
            row.append(vm.getVncAddress() + ":" + str(vm.getVncPort()))
        row.append(vm.getTemplate().getName())
        if verbose:
            row.extend([vm.getVirtualAppliance().getName(),
                vm.getVirtualDatacenter().getName(), vm.getEnterprise().getName()])
        table.append(row)
    pprint_table(table)

def pprint_templates(templates):
    """ Pretty prints the given template list. """
    table = [["id", "name", "disk type", "cpu", "ram", "hd", "disk file size"]]
    for template in templates:
        row = [template.getId(), template.getName(), template.getDiskFormatType(),
                template.getCpuRequired(), str(template.getRamRequired()) + " MB",
                str(template.getHdRequired() / 1024 / 1024) + " MB",
                str(template.getDiskFileSize() / 1024 / 1024) + " MB"]
        table.append(row)
    pprint_table(table)

def pprint_vdcs(vdcs):
    """ Pretty prints the given virtual datacenter list. """
    table = [["id", "name", "type"]]
    for vdc in vdcs:
        row = [vdc.getId(), vdc.getName(), vdc.getHypervisorType()]
        table.append(row)
    pprint_table(table)

def pprint_vapps(vapps):
    """ Pretty prints the given virtual appliance list. """
    table = [["id", "name"]]
    for vapp in vapps:
        row = [vapp.getId(), vapp.getName()]
        table.append(row)
    pprint_table(table)

def pprint_enterprises(enterprises):
    """ Pretty prints the given enterprise list. """
    table = [["id", "name"]]
    for enterprise in enterprises:
        row = [enterprise.getId(), enterprise.getName()]
        table.append(row)
    pprint_table(table)

def pprint_machines(machines):
    """ Pretty printd the given machine list. """
    table = [["name", "hypervisor", "state"]]
    for machine in machines:
        row = [machine.getName(), machine.getType().name(), machine.getState().name()]
        table.append(row)
    pprint_table(table)
