#!/usr/bin/env python3

"""
This server facilitates the acquisition and disclosure of 
seismic activity data from an array of nationally distributed 
seismological stations. Each station is precisely tied to a 
specific geographic coordinate, defined by its latitude and 
longitude. The dataset transmitted by these stations is 
categorized into two distinct types:

- **Public Stations:** Data from these stations is openly 
  accessible, allowing unrestricted retrieval and processing 
  of seismic information by any client.

- **Private Stations:** Data from these stations is classified 
  and requires user authentication for access. Only users with 
  the appropriate credentials can retrieve and analyze this 
  seismic data.
"""

import sys
import cmd
import os
import plotext as plt
import subprocess
import datetime
import numpy
import math
import random
import glob
import re
from itertools import islice, chain, repeat


class Seisfile:
    header_data = []
    data = []
    header_fields = [
        "delta",
        "depmin",
        "depmax",
        "unused",
        "odelta",
        "b",
        "e",
        "o",
        "a",
        "internal",
        "t0",
        "t1",
        "t2",
        "t3",
        "t4",
        "t5",
        "t6",
        "t7",
        "t8",
        "t9",
        "f",
        "resp0",
        "resp1",
        "resp2",
        "resp3",
        "resp4",
        "resp5",
        "resp6",
        "resp7",
        "resp8",
        "resp9",
        "stla",
        "stlo",
        "stel",
        "stdp",
        "evla",
        "evlo",
        "evel",
        "evdp",
        "mag",
        "auth",
        "lat",
        "long",
        "user3",
        "user4",
        "user5",
        "user6",
        "user7",
        "user8",
        "user9",
        "dist",
        "az",
        "baz",
        "gcarc",
        "sb",
        "sdelta",
        "depmen",
        "cmpaz",
        "cmpinc",
        "xminimum",
        "xmaximum",
        "yminimum",
        "ymaximum",
        "adjtm",
        "unused",
        "unused",
        "unused",
        "unused",
        "unused",
        "unused",
        "nzyear",
        "nzjday",
        "nzhour",
        "nzmin",
        "nzsec",
        "nzmsec",
        "nvhdr",
        "norid",
        "nevid",
        "npts",
        "nsnpts",
        "nwfid",
        "nxsize",
        "nysize",
        "unused",
        "iftype",
        "idep",
        "iztype",
        "unused",
        "iinst",
        "istreg",
        "ievreg",
        "ievtyp",
        "iqual",
        "isynth",
        "imagtyp",
        "imagsrc",
        "ibody",
        "unused",
        "unused",
        "unused",
        "unused",
        "unused",
        "unused",
        "unused",
        "leven",
        "lpspol",
        "lovrok",
        "lcalda",
        "unused",
        "kstnm",
        "kevnm",
        " ",
        " ",
        " ",
        "khole",
        "ko",
        "ka",
        " ",
        " ",
        "kt0",
        "kt1",
        "kt2",
        " ",
        " ",
        "kt3",
        "kt4",
        "kt5",
        " ",
        " ",
        "kt6",
        "kt7",
        "kt8",
        " ",
        " ",
        "kt9",
        "kf",
        "kuser0",
        " ",
        " ",
        "kuser1",
        "kuser2",
        "kcmpnm",
        " ",
        " ",
        "knetwk",
        "kdatrd",
        "kinst",
    ]
    filename = ""

    def __init__(self, filename):
        self.header_data = []
        self.data = []
        self.filename = filename

    def get_header_value(self, label):
        try:
            index = self.header_fields.index(label.lower())
            row = math.floor(index / 5)
            col = index % 5
            if label == " ":
                return "-12345"
            else:
                return self.header_data[row][col]
        except:
            print(f"{label} not a valid field, returned undefined value")
            return "-12345"

    def get_start_time(self):
        dateheader = self.header_data[14]
        year = int(dateheader[0])
        day = int(dateheader[1])
        hour = int(dateheader[2])
        minute = int(dateheader[3])
        second = int(dateheader[4])

        start_date = datetime.datetime.strptime(
            f"{year}/{day} {hour}:{minute}:{second}", "%Y/%j %H:%M:%S"
        )
        return start_date

    def set_header_value(self, label, value):
        try:
            index = self.header_fields.index(label.lower())
            row = math.floor(index / 5)
            col = index % 5
            cell_length = len(self.header_data[row][col])
            left_or_right = True if self.header_data[row][col][0] == " " else False
            if left_or_right:
                self.header_data[row][col] = str(value).ljust(cell_length)
            else:
                self.header_data[row][col] = str(value).rjust(cell_length)
            return True
        except:
            print(
                "Something went wrong writing header value, did you put in a legal header field name?"
            )
            return False


class Seismic(cmd.Cmd):
    auth = False
    data_path = os.path.join("/", "data")

    seis_files = []

    def catch_keyboard_interrupt(self):
        doQuit = False
        while doQuit != True:
            try:
                self.cmdloop(
                    """

📈SEISMIC [ONLINE]📈 

Type "help" for a list of commands.

Type "tutorial" for a quick tutorial.
"""
                )
                doQuit = True
            except KeyboardInterrupt:
                print("")
                print(
                    'please use the "EOF", "quit" or "exit" commands to end the program'
                )
                print("")

    def do_tutorial(self, line):
        print(
            """
SEISMIC Tutorial
================

List all the files:
    list

Read all monitoring station files:
    read

Plot all monitoring station files:
    plot

Generate a sine function:
    funcgen sine

Plot the result:
    plot
"""
        )

    def do_fft(self, line):
        for sac in self.seis_files:
            sac.data = numpy.fft.fft(sac.data)
            sac.set_header_value("user3", "fft")
        print("Data of all files transformed using FFT")

    def help_fft(self):
        print(
            "\n".join(
                [
                    "===fft===",
                    "Applies FFT on all files loaded in memory",
                    "",
                ]
            )
        )

    def do_f(self, line):
        """Abbreviation of the funcgen function, please see 'help funcgen' for more details."""
        self.do_funcgen(line)

    def do_funcgen(self, line):
        commands = line.split(" ")

        newData = Seisfile("funcgen")
        label = "test"

        if len(line) > 0:
            if commands[0] == "impulse":
                newData.data = self.gen_impluse_data()
                newData.header_data = self.gen_header(newData.data, "IMP")
            elif commands[0] == "step":
                newData.data = self.gen_step_data()
                newData.header_data = self.gen_header(newData.data, "STEP")
            elif commands[0] == "boxcar":
                newData.data = self.gen_boxcar_data()
                newData.header_data = self.gen_header(newData.data, "BOX")
            elif commands[0] == "seismogram":
                newData = self.gen_seismogram(line)
            elif commands[0] == "triangle":
                newData.data = self.gen_triangle_data()
                newData.header_data = self.gen_header(newData.data, "TRI")
            else:
                newData.data = self.gen_sine_data()
                newData.header_data = self.gen_header(newData.data, "SINE")
        else:
            newData.data = self.gen_sine_data()
            newData.header_data = self.gen_header(newData.data, "SINE")

        self.seis_files = []
        self.seis_files.append(newData)
        print(f"{label} data generated")

    def help_funcgen(self):
        print(
            "\n".join(
                [
                    "",
                    "===funcgen===",
                    "Generates example data, unloads all previously loaded data",
                    "Syntax:",
                    "funcgen (sine|triangle|impulse|seismogram|step|boxcar)",
                    "",
                ]
            )
        )

    def do_auth(self, line):
        """Authenticate with password"""
        password_file = "seismic.password"
        password_loc = os.path.join(self.data_path, password_file)
        with open(password_loc, newline="\n") as fp:
            password = fp.read()
            fp.close()
        if len(line) and line in password:
            self.auth = True
            print("You are now logged in!")
        else:
            print("Sorry that is not correct")

    def help_auth(self):
        print(
            "\n".join(
                [
                    "",
                    "===auth===",
                    "Login using password",
                    "Syntax:",
                    "auth (password)",
                    "",
                ]
            )
        )

    def do_copyhdr(self, line):
        if line == "":
            print("syntax error, use 'help copyhdr' for examples")
        else:
            commands = line.split(" ")
            source_file_index = int(commands[0])
            if source_file_index > len(self.seis_files):
                print("index out of range, not enough files loaded")
            else:
                source_file = self.seis_files[source_file_index]
                del commands[0]
                if len(commands) == 0:
                    for file in self.seis_files:
                        file.header_data = source_file.header_data.copy()
                else:
                    for command in commands:
                        label = command
                        if re.search("^[0-9]$", command):
                            label = self.seis_files[source_file_index].header_fields[
                                int(command)
                            ]
                        value = source_file.get_header_value(label)
                        for file in self.seis_files:
                            file.set_header_value(label, value)

    def help_copyhdr(self):
        print(
            "\n".join(
                [
                    "",
                    "===copyheader===",
                    "Copies the header variables of one file to all other files loaded in memory",
                    "Syntax:",
                    "copyheader (index) [hdr] eg: copyheader 0 delta depmin",
                    "",
                ]
            )
        )

    def do_lh(self, line):
        """Abbreviation of the listhdr function, please see 'help listhdr' for more details."""
        self.do_listhdr(line)

    def do_listhdr(self, line):
        if len(self.seis_files) == 0:
            print("No files loaded, please load files before reading headers.")
            return
        if line == "":
            for file in self.seis_files:
                if int(file.get_header_value("auth")) == 1 and self.auth == 0:
                    print(
                        f"{file.filename}: protected file, use the auth command to login."
                    )
                    continue
                for header in file.header_fields:
                    value = file.get_header_value(header)
                    if "12345" not in value:
                        print(f"{file.filename} {header}: {value.strip()}")
        else:
            commands = line.split(" ")
            if len(commands) > 0:
                file_index = -1
                try:
                    file_index = int(commands.index("files"))
                except ValueError:
                    file_index = -1

                files_array = range(len(self.seis_files))

                command_array = commands

                if file_index > -1:
                    files_array = commands[(file_index + 1) :]
                    command_array = commands[:file_index]

                for file_index in files_array:
                    file_index = int(file_index)
                    if file_index >= len(self.seis_files):
                        print(f"index {file_index} out of range")
                    else:
                        file = self.seis_files[file_index]
                        if int(file.get_header_value("auth")) == 1 and self.auth == 0:
                            print(
                                f"{file.filename}: protected file, use the auth command to login."
                            )
                            continue
                        for command in command_array:
                            if re.search("^[0-9]*$", command):
                                label = file.header_fields[int(command)]
                                value = file.get_header_value(label)
                                print(
                                    f"file: {file.filename} header:{command} ({label}): {value.strip()}"
                                )
                            else:
                                value = file.get_header_value(command)
                                print(
                                    f"file: {file.filename} header:{command}: {value.strip()}"
                                )

    def help_listhdr(self):
        print(
            "\n".join(
                [
                    "",
                    "===listhdr===",
                    "Prints all defined header fields",
                    "Syntax:",
                    "listhdr (INDEX) eg: listhdr 1 2 3 4",
                    "listhdr (LABEL) eg: listhdr khole depmin",
                    "listhdr (INDEX|LABEL) files (INDEX) eg: listhdr depmax files 2 3",
                    "",
                ]
            )
        )

    def do_markvalue(self, line):
        commands = line.split(" ")

        for sac in self.seis_files:
            cellindex = None
            if re.search("^(G|L)E$", commands[0]):
                value = commands[1]
                for index, cell in enumerate(sac.data):
                    if commands[0] == "GE":
                        if cell >= float(value):
                            cellindex = index
                            break
                    else:
                        if cell <= float(value):
                            cellindex = index
                            break
                if len(commands) > 2:
                    if commands[2].lower() == "to":
                        if cellindex == None:
                            cellindex = -12345
                        sac.set_header_value(commands[3], cellindex)

                if int(sac.get_header_value("auth")) == 1 and self.auth == 0:
                    print(
                        f"{sac.filename} is a protected file, use the auth command to login."
                    )
                else:
                    if cellindex == None or cellindex == -12345:
                        print(
                            f"{sac.filename}: no value matching {commands[0]} {commands[1]} found."
                        )
                    else:
                        start_date = sac.get_start_time()
                        measurement_date = start_date + datetime.timedelta(
                            seconds=0.05 * cellindex
                        )
                        print(
                            f'{sac.filename}: first value matching {commands[0]} {commands[1]} found in cell {cellindex} (time of cell measurement: {measurement_date.strftime("%d/%m/%Y %H:%M:%S")})'
                        )
            else:
                print("incorrect syntax")
                break

    def help_markvalue(self):
        print(
            "\n".join(
                [
                    "",
                    "===markvalue===",
                    "Find first value matching conditional",
                    "Prints cell index + time of measurement OR writes cellindex to t1-t9 header field",
                    "Syntax:",
                    "markvalue (GE|LE) (VALUE) eg: markvalue GE 200",
                    "markvalue (GE|LE) (VALUE) to (t1|t2|t3|t4|t5|t6|t7|t8|t9) eg: markvalue LE -100 to t1",
                    "",
                ]
            )
        )

    def do_p(self, line):
        """Abbreviation of the plot function, please see 'help plot' for more details."""
        self.do_plot(line)

    def do_plot(self, line):
        files = self.seis_files
        if line != "":
            commands = line.split(" ")

            files = []

            for command in commands:
                if re.search("^[0-9]$", command):
                    command = int(command)
                    if command < len(self.seis_files):
                        files.append(self.seis_files[command])
                    else:
                        print(f"file index {command} out of range")
                elif re.search("\\.SAC", command):
                    files.append(
                        self.parsefile(os.path.join(self.data_path, command), False)
                    )

        if len(files) == 0:
            print(
                'No files to print, load some files using the "read" command or generate using funcgen.'
            )
            return

        for file in files:
            if int(file.get_header_value("auth")) == 1 and self.auth == 0:
                print(
                    f"{file.filename} is a protected file, use the auth command to login."
                )
            else:
                plt.cld()
                plt.clf()

                if "-12345.00" in file.get_header_value("user3"):

                    plt.date_form("d/m/Y H:M:S")
                    header = file.header_data
                    start_date = file.get_start_time()
                    start_date_graph = start_date - datetime.timedelta(hours=2)

                    date_list = []

                    for i in range(0, len(file.data)):
                        delta = file.get_header_value("delta")
                        delta = float(delta)
                        date_point = start_date_graph + datetime.timedelta(
                            seconds=delta * i
                        )
                        date_list.append(date_point)
                    dates = plt.datetimes_to_string(date_list)

                    print(f"Plotting {file.filename}")
                    plt.plot(dates, file.data)
                    plt.ylabel("Counts")
                    plt.title(
                        f'{header[29][0].strip()}_{header[22][0].strip()}_00_{header[28][-1]}, {len(file.data)} samples, {1.0/float(header[0][0])} sps, {start_date.strftime("%Y-%m-%dT%H:%M:%S.%f")}'
                    )
                    plt.show()
                else:
                    plt.plot(numpy.abs(file.data), label="Real")
                    plt.plot(numpy.angle(file.data), label="Imaginary")
                    # Display the plot
                    plt.show()

    def help_plot(self):
        print(
            "\n".join(
                [
                    "",
                    "===plot===",
                    "Plots a graph for every file loaded in memory or file array of files loaded in memory",
                    "Syntax:",
                    "plot [filesindex] eg: plot 1 2 3",
                    "",
                ]
            )
        )

    def do_read(self, line):
        sac_files = []
        dir_path = self.data_path
        if line == "":
            sac_files = glob.glob(f"{dir_path}/*.SAC")
        else:
            commands = line.split(" ")
            for file in commands:
                sac_files.append(os.path.join(dir_path, file))

        for sac in sac_files:
            if sac in [f.filename for f in self.seis_files]:
                print(f"Already loaded {sac}")
                continue

            newData = self.parsefile(sac, True)
            if newData:
                self.seis_files.append(newData)
                print(f"file {sac} loaded into memory!")
            else:
                print(
                    f"Couldn't load file {sac}, use list command to see available files"
                )

    def help_read(self):
        print(
            "\n".join(
                [
                    "",
                    "===read===",
                    "Read files into memory, default is all files in current directory, but specific files can also be loaded",
                    "Syntax:",
                    "read [files] eg: read signal1.SAC signal2.SAC",
                    "",
                ]
            )
        )

    def parsefile(self, file, authcheck):
        newData = Seisfile(file)
        try:
            with open(file, newline="\n") as fp:
                for i, line in enumerate(fp):
                    if i < 14:
                        linesArray = self.splitline(line.rstrip(), 15)
                        if i == 8:
                            authFile = int(linesArray[0])
                            if authcheck:
                                if authFile == 1 and self.auth == 0:
                                    print(
                                        f"=== WARNING === {file} is a protected file, to see the contents of this file, log in using the auth command."
                                    )
                            else:
                                linesArray[0] = linesArray[0].replace("1", "0")
                        newData.header_data.append(linesArray)
                    elif i >= 14 and i < 22:
                        linesArray = self.splitline(line.rstrip(), 10)
                        newData.header_data.append(linesArray)
                    elif i >= 22 and i < 30:
                        linesArray = self.splitline(line.rstrip(), 8)
                        newData.header_data.append(linesArray)
                    elif i >= 30:
                        linesArray = self.splitline(line.rstrip(), 15)
                        linesFloatArray = [float(x) for x in linesArray]
                        newData.data += linesFloatArray
                return newData
        except IOError:
            return False

    def do_list(self, line):
        """List SAC files in the data directory"""
        dir = self.data_path
        if line != "":
            dir = line
        os.system(f"ls {dir} | grep .SAC")

    def do_hdrfieldlabels(self, line):
        """Lists all header field labels"""
        if len(self.seis_files) > 0:
            print(self.seis_files[0].header_fields)
        else:
            file = Seismic("list")
            print(file.header_fields)

    def help_hdrfieldlabels(self):
        print(
            "\n".join(
                [
                    "",
                    "===hdrfieldlabels===",
                    "Shows all available header fields",
                    "for a description of these fields please visit https://ds.iris.edu/files/sac-manual/manual/file_format.html",
                    "",
                ]
            )
        )

    def do_printdatapoint(self, line):
        if line == "":
            print("invalid syntax, check help printdatapoint for valid syntax")
        else:
            commands = line.split(" ")
            cellIndex = int(commands[0])
            del commands[0]
            files = range(len(self.seis_files))
            if len(commands) > 0:
                try:
                    file_index = commands.index("files")
                    del commands[file_index]
                    files = commands
                except:
                    print(
                        f"invalid syntax printing index {cellIndex} of all files instead. Check help printdatapoint for valid syntax"
                    )

            print("")
            for index in files:
                try:
                    index = int(index)
                except:
                    continue
                if index >= len(self.seis_files):
                    print(f"file index {index} out of range")
                else:
                    file = self.seis_files[index]
                    if cellIndex == -1:
                        print(f"{file.filename} cell {cellIndex}: {file.data}")
                    elif cellIndex < len(file.data):
                        print(
                            f"{file.filename} cell {cellIndex}: {file.data[cellIndex]}"
                        )
                    else:
                        print(
                            f"{file.filename} cell {cellIndex} out of range. Only {len(file.data)} cells in file."
                        )
            print("")

    def help_printdatapoint(self):
        print(
            "\n".join(
                [
                    "",
                    "===printdatapoint===",
                    "Prints cell value at given index (index -1 prints all cells)",
                    "Syntax:",
                    "printdatapoint (INDEX) files (FILELIST) eg: printdatapoint 2 files 1 2 4",
                ]
            )
        )

    #def do_shell(self, line):
    #    "Runs a shell command, only useful for debugging"
    #    print("running shell command:", line)
    #    sub_cmd = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE)
    #    output = sub_cmd.communicate()[0].decode("utf-8")
    #    print(output)

    def do_EOF(self, line):
        """Exits the program"""
        return True

    def do_exit(self, line):
        """Exits the program"""
        return True

    def do_quit(self, line):
        """Exits the program"""
        return True

    def gen_impluse_data(self, pulse=50):
        data = []
        length = 500
        for i in range(length):
            signal = 0
            if (i / length * 100) == pulse:
                signal = self.auth = 1
            data.append(signal)
        return data

    def gen_step_data(self):
        data = []
        length = 2000
        for i in range(length):
            signal = 0
            if i > length / 2:
                signal = 1
            data.append(signal)
        return data

    def gen_seismogram(self, line):
        if re.search("^[0-9]{1}", line):
            line = int(line[0])
        else:
            line = random.randrange(0, 1000)
        files = glob.glob(f"{self.data_path}/*.SAC")
        seed = line % len(files)
        return self.parsefile(files[seed], False)

    def gen_boxcar_data(self):
        data = []
        length = 2000
        for i in range(length):
            signal = 0
            if i > length * 0.33 and i < length * 0.66:
                signal = 1
            data.append(signal)
        return data

    def gen_header(self, seis_data, stationname="test"):
        seis_header_data = list(range(30))
        delta = 0.05000000
        minp = min(seis_data)
        maxp = max(seis_data)
        empty = -12345.00
        odelta = empty
        seis_header_data[0] = [
            f"{delta:>15.8f}",
            f"{minp:>15.3f}",
            f"{maxp:>15.3f}",
            f"{empty:>15.2f}",
            f"{odelta:>15.2f}",
        ]
        b = random.uniform(0, 0.0009)
        e = random.uniform(200, 1250)
        seis_header_data[1] = [
            f"{b:>15.10f}",
            f"{e:>15.3f}",
            f"{empty:>15.2f}",
            f"{empty:>15.2f}",
            f"{empty:>15.2f}",
        ]
        for i in range(2, 8):
            seis_header_data[i] = [
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
            ]
        seis_header_data[8] = [
            f"{0:>15}",
            f"{0:>15.6f}",
            f"{0:>15.6f}",
            f"{empty:>15.2f}",
            f"{empty:>15.2f}",
        ]
        for i in range(9, 14):
            seis_header_data[i] = [
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
                f"{empty:>15.2f}",
            ]
        now = datetime.datetime.now()
        seis_header_data[14] = [
            f"{now.strftime('%Y'):>10}",
            f"{now.strftime('%j'):>10}",
            f"{now.strftime('%H'):>10}",
            f"{now.strftime('%M'):>10}",
            f"{now.strftime('%S'):>10}",
        ]
        headerNumber = 6
        miliseconds = now.strftime("%f")[:3]
        seis_header_data[15] = [
            f"{miliseconds:>10}",
            f"{headerNumber:>10}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{len(seis_data):>10}",
        ]
        seis_header_data[16] = [
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
        ]
        iftype = 1
        seis_header_data[17] = [
            f"{iftype:>10}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
        ]
        for i in range(18, 21):
            seis_header_data[i] = [
                f"{empty:>10.0f}",
                f"{empty:>10.0f}",
                f"{empty:>10.0f}",
                f"{empty:>10.0f}",
                f"{empty:>10.0f}",
            ]
        level = 1
        seis_header_data[21] = [
            f"{level:>10}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
            f"{empty:>10.0f}",
        ]
        seis_header_data[22] = [f"{stationname:<8}", f"{empty:<8.0f}"]
        khole = "00"
        seis_header_data[23] = [f"{khole:<8}", f"{empty:<8.0f}", f"{empty:<8.0f}"]
        for i in range(24, 28):
            seis_header_data[i] = [f"{empty:<8.0f}", f"{empty:<8.0f}", f"{empty:<8.0f}"]
        kcmpnm = "TEST"
        seis_header_data[28] = [f"{empty:<8.0f}", f"{empty:<8.0f}", f"{kcmpnm:<8}"]
        knetwk = "IU"
        seis_header_data[29] = [f"{knetwk:<8}", f"{empty:<8.0f}", f"{empty:<8.0f}"]
        return seis_header_data

    def gen_sine_data(self, cycles=2):
        resolution = 2000
        length = numpy.pi * 2 * cycles
        return numpy.sin(numpy.arange(0, length, length / resolution))

    def gen_square_data(self, tempo=1):
        data = []
        for i in range(2000):
            data.append(round(math.sin((i / 100) * tempo) / 2 + 0.5))
        return data

    def gen_triangle_data(self):
        length = 2000
        data = []
        middlepoint = length / 2
        for i in range(length):
            if i < length * 0.25 or i > length * 0.75:
                signal = 0
            else:
                if i < length / 2:
                    signal = (i - length * 0.25) / ((length / 2) - length * 0.25)
                if i > length / 2:
                    signal = 1.0 - ((i - length / 2) / ((length * 0.75) - length / 2))
            data.append(signal)
        return data

    def splitline(self, line, cell_width):
        cells = []
        step = cell_width
        for i in range(0, len(line), cell_width):
            slice = line[i : i + cell_width]
            cells.append(slice)
        return cells


if __name__ == "__main__":
    Seismic().catch_keyboard_interrupt()
