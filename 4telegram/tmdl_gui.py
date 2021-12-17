"""
*  TMDL - Telegram DL - TK INTER GUI                                                                                               *
*                                                                                                                       *
*  VERSION 0.0.1                                                                                                        *
*                                                                                                                       *
*  Idea/Written by Sebastian Vivian Gresser                                                                             *
*                                                                                                                       *
*  install modules: tkinter tkcalendar subprocess
"""


from tkinter import *
import os
import subprocess
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from tkcalendar import Calendar, DateEntry
from tkinter import ttk
import datetime
import json


root = Tk()
root.title("tmdl-tkinter")

class ProgressDialog:
    def __init__(self, parent):

        top = self.top = Toplevel(parent)
        Label(top, text="Progress").pack()
        self.value = ""
        self.text = Text(top)
        self.text.pack()

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def updateview(self, value):
        self.value = value
        self.text.insert(INSERT, value)

    def ok(self):
        print("value is", self.value)
        self.top.destroy()

class DownloadQueue:
    queue = []
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path
        self.queue = self.ffp(path)

    def ffp(self, path):
        try:
            f=open(path, "r")
            js=f.read()
            f.close()
            return json.loads(js)
        except:
            print("Queue file not existing")
            return []
    def add(self, data):
        if self.sanitize(data):
            self.queue.append(data)
        self.dump()
    def rm(self, i):
        del self.queue[i]
        self.dump()
    def read(self, i=-1):
        if i != -1:
            return self.queue[i]
        else:
            return self.queue
    def sanitize(self, data):
        return True

    def dump(self):
        try:
            f=open(self.path, "w")
            js = json.dumps(self.queue)
            f.write(js)
            f.close()
        except Exception:
            print("Could not save queue.")


class App:
    id = IntVar()
    hash = StringVar()
    target = StringVar()
    output = StringVar()
    mnum = IntVar()
    fnum = IntVar()
    date_start = StringVar()
    date_end = StringVar()
    date_last = IntVar()
    search_term = StringVar()
    search_target = StringVar()
    mime = StringVar()
    reverse = BooleanVar()
    loop = StringVar()

    queue = Listbox(root)

    label_id = Label(root, text="APP ID").grid(row=1, column=0)
    grid_app_id = Entry(root, textvariable=id)
    grid_app_id.grid(row=1, column=1)

    label_hash = Label(root, text="APP HASH").grid(row=1, column=2)
    grid_app_hash = Entry(root, textvariable=hash)
    grid_app_hash.grid(row=1, column=3)

    label_output = Label(root, text="Target Folder: ").grid(row=2, column=0)
    grid_output = Entry(root, textvariable=output)
    grid_output.grid(row=2, column=1)

    label_target = Label(root, text="Channel Id/Name: ").grid(row=3, column=0)
    grid_target = Entry(root, textvariable=target)
    grid_target.grid(row=3, column=1)

    label_filters = Label(root, text="Filters: ").grid(row=4, column=0)

    label_mnum = Label(root, text="Maximum Messages: ").grid(row=5, column=0)
    grid_mnum = Entry(root, textvariable=mnum)
    grid_mnum.grid(row=5, column=1)

    label_fnum = Label(root, text="Maximum Files: ").grid(row=5, column=2)
    grid_fnum = Entry(root, textvariable=fnum)
    grid_fnum.grid(row=5, column=3)

    label_date_start = Label(root, text="Date Start: ").grid(row=6, column=0)
    grid_date_start = Entry(root, textvariable=date_start)
    grid_date_start.grid(row=6, column=1)

    label_date_end = Label(root, text="Date End: ").grid(row=6, column=2)
    grid_date_end = Entry(root, textvariable=date_end)
    grid_date_end.grid(row=6, column=3)

    label_date_last = Label(root, text="Date Last: ").grid(row=8, column=0)
    grid_date_last = Entry(root, textvariable=date_last)
    grid_date_last.grid(row=8, column=1)

    label_search_term = Label(root, text="Search Term: ").grid(row=9, column=0)
    grid_search_term = Entry(root, textvariable=search_term)
    #grid_search_term.columnconfigure(0, weight=30)
    grid_search_term.grid(row=9, column=1)

    label_search_target = Label(root, text="Search Target: ").grid(row=9, column=2)
    grid_search_target = OptionMenu(root, search_target, "any", "message", "filename")
    grid_search_target.grid(row=9, column=3)

    label_mime = Label(root, text="Mime Type: ").grid(row=10, column=0)
    grid_mime = Entry(root, textvariable=mime)
    grid_mime.grid(row=10, column=1)

    label_reverse = Label(root, text="Reverse: ").grid(row=11, column=0)
    grid_reverse = OptionMenu(root, reverse, True, False)
    grid_reverse.grid(row=11, column=1)

    label_loop = Label(root, text="Loop: ").grid(row=11, column=2)
    grid_loop = Entry(root, textvariable=loop)
    grid_loop.grid(row=11, column=3)

    # Initialize
    def __init__(self, master):

        self.downloadqueue = DownloadQueue(self, "./tmdl_queue")
        if len(self.downloadqueue.read()) > 0:
            for item in self.downloadqueue.read():
                self.queue.insert(END, item['target'])
        self.search_term.set("^.*[word1|word2|word3].*?\.fileextension$")
        #self.queue.bind('<Double-1>', self.edit)
        self.queue.grid(column=0, row=0, columnspan=3, sticky=W+E)
        self.delete = Button(master, text="Delete", command=self.delete)
        self.delete.grid(row=0, column=6)
        self.start = Button(master, text="Start", command=self.start)
        self.start.grid(row=0, column=4)
        self.edit = Button(master, text="Edit", command=self.edit)
        self.edit.grid(row=0, column=5)
        #self.queue.grid(fill=BOTH, expand=1)

        # Create Add Button
        self.command = Button(master, text="Add", command=self.add)
        self.command.grid(column=5, row=6)

        # Create File Path Button :v
        self.command = Button(master, text="...", command=self.pickfolder)
        self.command.grid(column=2, row=2)

        self.command = Button(master, text="select", command=lambda:self.select_date(self.date_start))
        self.command.grid(column=1, row=7)

        self.command = Button(master, text="select", command=lambda:self.select_date(self.date_end))
        self.command.grid(column=3, row=7)

    def pickfolder(self):
        print("tmdl-tkinter: Choosing File Destination")
        Tk().withdraw()
        filename = askdirectory()
        self.output.set(filename)

    def start(self):
        print("tmdl-tkinter: Initializing download of url {} to destination {}".format(self.target.get(),
        self.output.get()))
        pos = self.queue.curselection()[0]
        d = ProgressDialog(root)
        if os.name == "posix":
            shellcmd = "python3"
        else:
            shellcmd = "python"
        shellcmd += " ./tmdl.py"
        data = self.downloadqueue.read(pos)
        for k in data:
            if isinstance(data[k], str) and data[k] != "":
                shellcmd += ' --{} "{}"'.format(k, data[k])
            elif (isinstance(data[k], int) and data[k] != 0) or isinstance(data[k], bool):
                shellcmd += ' --{} {}'.format(k, data[k])
        result = subprocess.check_output(shellcmd, shell=True)
        d.updateview(result)
        root.wait_window(d.top)

    def select_date(self, target):
        top = Toplevel(root)
        ttk.Label(top, text='Choose date').pack(padx=10, pady=10)
        year = int(datetime.datetime.now(datetime.timezone.utc).strftime("%Y"))
        month = int(datetime.datetime.now(datetime.timezone.utc).strftime("%m"))
        day = int(datetime.datetime.now(datetime.timezone.utc).strftime("%d"))
        cal = DateEntry(top, width=12, background='darkblue',foreground='white', borderwidth=2, year=year, month=month, day=day)
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="ok", command=lambda:self.set_date(cal,target)).pack()

    def set_date(self, cal, target):
        target.set(cal.get_date().strftime("%Y-%m-%d %H:%M:%S"))


    def delete(self):
        pos = self.queue.curselection()[0]
        self.downloadqueue.rm(pos)
        self.queue.delete(ANCHOR)
    def edit(self):
        pos = self.queue.curselection()[0]
        data = self.downloadqueue.read(i=pos)
        self.id.set(data['id'])
        self.hash.set(data['hash'])
        self.target.set(data['target'])
        self.output.set(data['output'])
        self.mnum.set(data['mnum'])
        self.fnum.set(data['fnum'])
        self.date_start.set(data['date_start'])
        self.date_end.set(data['date_end'])
        self.date_last.set(data['date_last'])
        self.search_term.set(data['search_term'])
        self.search_target.set(data['search_target'])
        self.mime.set(data['mime'])
        self.reverse.set(data['reverse'])
        self.loop.set(data['loop'])

    def add(self):
        app_id=self.id.get()
        if app_id == None or app_id == "":
            print("APP ID may not be None or empty")
            return
        if not isinstance(app_id, int):
            print("APP ID must be a integer value")
            return
        app_hash=self.hash.get()
        if app_hash == None or app_hash == "":
            print("APP HASH may not be None or empty")
            return
        if not isinstance(app_hash, str):
            print("APP HASH must be a string value")
            return
        target=self.target.get()
        if target == None or target == "":
            print("Channel may not be None or empty")
            return
        if not (isinstance(target, str) and isinstance(target, str)):
            print("Channel must be a string/int value")
            return
        output=self.output.get()
        if target == None or target == "":
            print("Output directory may not be None or empty")
            return

        mnum=self.mnum.get()
        fnum=self.fnum.get()
        date_start=self.date_start.get()
        date_end=self.date_end.get()
        date_last=self.date_last.get()
        search_term=self.search_term.get()
        search_target=self.search_target.get()
        mime=self.mime.get()
        reverse=self.reverse.get()
        loop=self.loop.get()
        channel_vars={"id": app_id,"hash":app_hash, "target":target, "output":output, "mnum":mnum, "fnum":fnum, "date_start":date_start, "date_end":date_end, "date_last":date_last, "search_term":search_term, "search_target": search_target, "mime":mime, "reverse":reverse, "loop":loop}
        self.queue.insert(END, self.target.get())
        self.downloadqueue.add(channel_vars)
        print("tmdl-tkinter: Channel {} added to queue!".format(self.target.get()))

app = App(root)
root.mainloop()
