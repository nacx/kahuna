#!/usr/bin/env jython

from datetime import datetime


class PTable:
    """ Table with pretty formatting """
    def __init__(self, headers=[]):
        self._headers = headers
        self._rows = []
        self._separators = []

    def headers(self, headers):
        """ Sets the table headers """
        self._headers = headers

    def add(self, row):
        """ Adds a row to the table """
        self._rows.append(row)

    def separator(self, position=-1):
        """ Appends a separator to the table """
        # A None row is considered a separator
        if position > 0:
            self._rows.insert(position, None)
        else:
            self._rows.append(None)

    def pprint(self):
        """ Pretty printstable """
        # Get the column paddings
        col_paddings = []
        for column in range(len(self._headers)):
            col_paddings.append(self._max_width(column))

        self._pprint_header(col_paddings)
        for row in self._rows:
            if row:     # None rows are considered separators
                self._pprint_row(row, col_paddings)
            else:
                self._pprint_separator(col_paddings)

    def _max_width(self, column):
        """ Get the maximum width of the given column index """
        lengths = [len(str(self._headers[column]))]
        for row in self._rows:
            if row:     # Ignore separators
                lengths.append(len(str(row[column])))
        return max(lengths)

    def _pprint_row(self, row, col_paddings):
        """ Pretty prints the given row """
        for column in range(len(row)):
            value = str(row[column])
            col = value.ljust(col_paddings[column] + 1)
            print col,
        print

    def _pprint_header(self, col_paddings):
        """ Pretty prints the table header """
        self._pprint_row(self._headers, col_paddings)
        self._pprint_separator(col_paddings)

    def _pprint_separator(self, col_paddings):
        """ Prints a separator line """
        for column in range(len(self._headers)):
            print "-" * col_paddings[column], "",
        print


def pprint_vms(vms, verbose=False):
    """ Pretty prints the given virtual machine list """
    table = PTable(["id", "name", "cpu", "ram", "hd", "state", "vnc",
        "template", "virtual datacenter"])
    if verbose:
        table.headers.extend(["virtual appliance", "enterprise"])
    for vm in vms:
        state = vm.getState()
        row = [vm.getId(), vm.getInternalName(), vm.getCpu(),
                str(vm.getRam()) + " MB",
                str(vm.getHdInBytes() / 1024 / 1024) + " MB", state]
        if not state.existsInHypervisor():
            row.append("-")
        else:
            row.append(vm.getVncAddress() + ":" + str(vm.getVncPort()))
        row.extend([vm.getTemplate().getName(),
            vm.getVirtualDatacenter().getName()])
        if verbose:
            row.extend([vm.getVirtualAppliance().getName(),
                vm.getEnterprise().getName()])
        table.add(row)
    table.pprint()


def pprint_templates(templates):
    """ Pretty prints the given template list """
    table = PTable(["id", "name", "disk type", "cpu", "ram", "hd",
        "disk file size"])
    for template in templates:
        row = [template.getId(), template.getName(),
                template.getDiskFormatType(), template.getCpuRequired(),
                str(template.getRamRequired()) + " MB",
                str(template.getHdRequired() / 1024 / 1024) + " MB",
                str(template.getDiskFileSize() / 1024 / 1024) + " MB"]
        table.add(row)
    table.pprint()


def pprint_vdcs(vdcs):
    """ Pretty prints the given virtual datacenter list """
    table = PTable(["id", "name", "type"])
    [table.add([v.getId(), v.getName(), v.getHypervisorType()]) for v in vdcs]
    table.pprint()


def pprint_vapps(vapps):
    """ Pretty prints the given virtual appliance list """
    table = PTable(["id", "name"])
    [table.add([vapp.getId(), vapp.getName()]) for vapp in vapps]
    table.pprint()


def pprint_enterprises(enterprises):
    """ Pretty prints the given enterprise list """
    table = PTable(["id", "name"])
    [table.add([e.getId(), e.getName()]) for e in enterprises]
    table.pprint()


def pprint_volumes(volumes):
    """ Pretty prints the given volume list """
    table = PTable(["id", "name", "size", "status", "virtual datacenter",
        "virtual machine"])
    for vol in volumes:
        row = [vol.getId(), vol.getName(), str(vol.getSizeInMb()) + " MB",
                vol.getState(), vol.getVirtualDatacenter().getName()]
        link = vol.unwrap().searchLink("virtualmachine")
        if link:
            row.append(link.getTitle())
        else:
            row.append("-")
        table.add(row)
    table.pprint()


def pprint_machines(machines):
    """ Pretty printd the given machine list """
    table = PTable(["id", "name", "address", "hypervisor", "state",
        "cpu (used/total)", "ram (used/total)"])
    for machine in machines:
        row = [machine.getId(), machine.getName(), machine.getIp(),
                machine.getType().name(), machine.getState().name(),
                str(machine.getVirtualCpusUsed()) + " / " +
                str(machine.getVirtualCpuCores()),
                str(machine.getVirtualRamUsedInMb()) + " / " +
                str(machine.getVirtualRamInMb()) + " MB"]
        table.add(row)
    table.pprint()


def pprint_tasks(tasks):
    """ Pretty prints the given task with its job list """
    date_format = "%d-%m-%Y %H:%M"
    table = PTable(["task/job", "id", "type", "status", "rollback status",
        "date"])
    for task, jobs in tasks:
        task_date = datetime.fromtimestamp(long(task['timestamp']))
        table.add(["task", task['taskId'], task['type'], task['state'], "-",
            task_date.strftime(date_format)])
        for job in jobs:
            job_date = datetime.fromtimestamp(long(job['timestamp']))
            row = ["job", job['id'], job['type'], job['state'],
                    job['rollbackState'], job_date.strftime(date_format)]
            table.add(row)
        table.separator()
    table.pprint()
