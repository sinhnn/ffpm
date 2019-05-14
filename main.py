from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from tkinter.messagebox import *
from database import *
from datetime import datetime
from shutil import copyfile
import gettext
import locale
import constants
import os

import subprocess
import configparser

if locale.getdefaultlocale()[0] == 'pl_PL':
    pl = gettext.translation('main', localedir='locale', languages=['pl'])
    pl.install()
else:
    _ = lambda f: f


_FIREFOX = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
_FIELDS = {
        "name" : "Profdile name",
        "path" : "Location of Profile",
        "startup_page" : "Startup Page",
        "tag" : "Custom tags"
}

_EMPTY_ENTRY_DATA = {
        "name" : "",
        "path" : "",
        "startup_page" : "",
        "tag" : ""
}


_MENUS = {
    "save" : {"name": "Save", "icon" : "icons/save.png"},
    "add" : {"name": "Add", "icon" : "icons/add.png"},
    "run" : {"name": "Run", "icon" : "icons/run.png"},
    "edit" : {"name": "Edit", "icon" : "icons/edit.png"},
    "remove" : {"name": "Remove", "icon" : "icons/remove.png"},
    "find" : {"name": "Find", "icon" : "icons/find.png"},
    "clear" : {"name": "Clear", "icon" : "icons/clear.png"},
}

def brower_path(o, parrrent_w = None,ext=None,dir=False):
    if dir:
        oo = filedialog.askdirectory()
        o.set(oo)
    if parrrent_w:
        parrrent_w.focus_force()
    return str(oo)

class Application(Frame):

    db = None
    icons = []
    buttons = []
    def __init__(self):
        super().__init__()

        global item_list
        global button_save
        global entry_find

        self.button_save_icon = PhotoImage(file='icons/save.png')
        self.button_add_icon = PhotoImage(file='icons/add.png')
        self.button_run_icon = PhotoImage(file='icons/add.png')
        self.button_edit_icon = PhotoImage(file='icons/edit.png')
        self.button_remove_icon = PhotoImage(file='icons/remove.png')
        self.button_find_icon = PhotoImage(file='icons/find.png')
        self.button_clear_icon = PhotoImage(file='icons/clear.png')
        self.button_cancel_icon = PhotoImage(file='icons/cancel.png')


        button_export = Button(self, text=_('Export'), image=self.button_save_icon, compound='left', width=0,
                             command=lambda: self.export())
        button_save = Button(self, text=_('Save'), image=self.button_save_icon, compound='left', width=0,
                             command=lambda: self.save())
        button_add = Button(self, text=_('Add'), image=self.button_add_icon, compound='left', width=0,
                            command=lambda: self.add())
        button_run = Button(self, text=_('Run'), image=self.button_add_icon, compound='left', width=0,
                            command=lambda: self.run())
        button_edit = Button(self, text=_('Edit'), image=self.button_edit_icon, compound='left', width=0,
                             command=lambda: self.edit())
        button_remove = Button(self, text=_('Remove'), image=self.button_remove_icon, compound='left', width=0,
                               command=lambda: self.remove())
        button_find = Button(self, text=_('Find'), image=self.button_find_icon, compound='left', width=0,
                             command=lambda: self.find(entry_find.get()))
        button_clear = Button(self, text=_('Clear'), image=self.button_clear_icon, compound='left', width=0,
                              command=lambda: self.clear())

        label_about = Label(self, text=constants.programname + ' ' + constants.version + ' - ' + constants.copyright)

        item_list = Treeview(self)
        item_list.bind("<Button-3>", self.popup)
        item_list.bind("<Double-1>", self.douleClick)
        # item_list.bind("<Enter>", self.douleClick)
        item_list.bind("<Return>", self.douleClick)
        item_list.bind("<Escape>", self.clear_key)
        item_list.bind("<Control-l>", self.focus_find)
        item_list.bind("<Control-s>", self.save_key)
        item_list.focus_force()

        entry_find = Entry(self)
        entry_find.bind("<Enter>", self.entry_find_from_enter)
        entry_find.bind("<Return>", self.entry_find_from_enter)
        entry_find.bind("<Escape>", self.clear_key)

        self.contextMenu = Menu(self, tearoff=0)
        self.contextMenu.add_command(label="Run", command=self.run)
        self.contextMenu.add_command(label="Edit", command=self.edit)
        self.contextMenu.add_command(label="Remove", command=self.remove)

        button_export.grid(column=0, row=0)
        button_save.grid(column=1, row=0)
        button_add.grid(column=2, row=0)
        button_edit.grid(column=3, row=0)
        button_remove.grid(column=4, row=0)
        entry_find.grid(column=6, row=0)
        button_find.grid(column=7, row=0)
        button_clear.grid(column=8, row=0)
        button_run.grid(column=9, row=0)
        item_list.grid(column=0, row=1, columnspan=10, sticky=NSEW, pady=5)
        label_about.grid(column=0, row=2, columnspan=9)

        item_list['columns'] = tuple(_FIELDS.keys())
        item_list.heading("#0", text='STT')
        item_list.column("#0", width=48, stretch=NO)
        for k, v in _FIELDS.items():
            item_list.heading(k, text=v)
            if k == "path":
                item_list.column(k, width=276, stretch=NO, anchor='w')
            elif k == "startup_page":
                item_list.column(k, width=276, stretch=NO, anchor='w')
            else:
                item_list.column(k, width=100, stretch=NO, anchor='w')

        for num, weight in enumerate([0, 0, 0, 0,0, 1, 0, 0, 0, 0]):
            self.grid_columnconfigure(num, weight=weight)

        for num, weight in enumerate([0, 1, 0]):
            self.grid_rowconfigure(num, weight=weight)

        try:
            self.db = Database(configfile=constants.filename)
        except Exception as e:
            showerror(_('Error'), _('An error occurred when opening file:\n\n') + str(e))
            sys.exit()
        try:
            self.refresh()
        except Exception as e:
            print(e)

    # =======================================================================
    def refresh(self, pattern=None):
        try:
            item_list.delete(*item_list.get_children())
            for num, item in enumerate(self.db.items, 1):
                values = []
                for label in _FIELDS.keys():
                    values.append(item[label])
                if ( not pattern 
                        or pattern.lower() in item["tag"].lower()
                        or pattern.lower() in item["startup_page"].lower()
                    ):
                    item_list.insert('', 'end', text=num, values=tuple(values), tags="1")

            if self.db.changed is True:
                button_save.configure(state='enabled')
            else:
                button_save.configure(state='disabled')
            item_list.tag_configure('NOT_FOUND', foreground='silver')
        except AttributeError as e:
            pass
        except Exception as e:
            showerror(e)

        # =========================================================================
    def add(self):
        self.entry_form()
        return

    def edit(self):
        id = self.get_focus_item()
        if id < 0: 
            showinfo("No focusing item!")
            return False
        idata = self.db.items[id]
        self.entry_form(id, idata)
        return

    def entry_form(self, id=None, init_data=None):
        if id == None and init_data == None:
            init_data = _EMPTY_ENTRY_DATA
        else:
            init_data = self.db.items[id]
        window = Toplevel()
        ppath = StringVar()
        ppath.set(init_data['path'])
        labels = [
            Label(window, text=_('Path')),
            Label(window, text=_('Name')),
            Label(window, text=_('Startup Page')),
            Label(window, text=_('Tags'))
        ]
        entries = [
            Entry(window, textvariable=ppath),
            Entry(window),
            Entry(window),
            Entry(window)
        ]
        entries[1].insert(0, init_data['name'])
        entries[2].insert(0, init_data['startup_page'])
        entries[3].insert(0, init_data['tag'])

        labels[0].grid(column=0, row=0, sticky=W, padx=5)
        entries[0].grid(column=1, row=0, columnspan=3, sticky=EW, padx=5, pady=5)
        button_choose_dir = Button(window, text=_('Broswer'),
                image=self.button_save_icon, compound='left', width=0,
                command=lambda: brower_path(parrrent_w=window,dir=True,o=ppath))
        button_choose_dir.grid(column=4, row=0, sticky=W, padx=5)
        for i, label in enumerate(labels[1:], 1):
            label.grid(column=0, row=i, sticky=W, padx=5)
            entries[i].grid(column=1, row=i, columnspan=2, sticky=EW, padx=5, pady=5)

        button_save = Button(
                window,
                text=_('Save'),
                image=self.button_save_icon,
                compound='left',
                command=lambda: self.edit_db(window, entries, id)
            )
        button_save.grid(column=1, row=len(labels), padx=5, pady=5)
        button_cancel = Button(window,
                text=_('Cancel'),
                image=self.button_cancel_icon,
                compound='left',
                command=window.destroy
            )
        button_cancel.grid(column=2, row=len(labels), padx=5, pady=5)
        return

    # =========================================================================
    def popup(self, event):
        iid = item_list.identify_row(event.y)
        if iid:
            item_list.selection_set(iid)
            self.contextMenu.post(event.x_root, event.y_root)
        else:
            pass
    def douleClick(self, event):
        self.run()
    def entry_find_from_enter(self, event):
        self.find(entry_find.get())
        return
    def clear_key(self,event):
        self.clear()
    def save_key(self,event):
        self.save()
    def focus_find(self, event):
        entry_find.focus()

    # =========================================================================
    def run(self):
        try:
            id = int(item_list.item(item_list.focus())['text']) - 1
        except ValueError:
            # edit_window.destroy()
            return
        item = self.db.items[id]
        subprocess.Popen([_FIREFOX, "--no-remote", "--profile", item["path"], item["startup_page"]])
    
    def remove(self):
        id = self.get_focus_item()
        print("Removing item {}".format(id))
        if id >= 0:
            self.db.rm(id)
            self.refresh()
        return

    def find(self, string):
        self.refresh(string)

    def clear(self):
        self.db.tag('')
        self.refresh()

    def save(self):
        try:
            x = os.path.splitext(constants.filename)
            backupname = "{}_backup{}".format(x[0],x[1])
            copyfile(constants.filename, backupname)
            self.db.save()
            # showinfo(_('Save'), _('File saved successfully'))
            self.refresh()
        except Exception as e:
            showerror(_('Error'), _('An error occurred when saving file:\n\n') + str(e))
    def export(self):
        ofile = filedialog.asksaveasfilename(
                confirmoverwrite=True,
                filetypes=(("JSON", "*.json"),("All Files", "*.*")),
                defaultextension=".json")
        if ofile:
            self.db.export(ofile)
        return True


    # =========================================================================
    def get_focus_item(self):
        try:
            return int(item_list.item(item_list.focus())['text']) - 1
        except Exception as e:
            showerror(e)
            return -1

    def entry_form_to_item(self, entries):
        data = {
            'path' : entries[0].get(),
            'name' : entries[1].get(),
            'startup_page' : entries[2].get(),
            'tag' : entries[3].get()
        }
        if not data['name'] or data['name'] == _FIELDS['name']:
            data['name'] = os.path.basename(data['path'])
        data["id"] = data["name"]
        return data

    def edit_db(self, window, entries, id):
        try:
            data = self.entry_form_to_item(entries)
            if id == None or id > len(self.db.items) or len(self.db.items) == 0:
                self.db.add(data)
            else:
                self.db.set(id, data)
            window.destroy()
            self.refresh()
        except ValueError:
            showerror(_('Error'), _('An error occurred when editing item:\n\n') + _('Empty or invalid value'))
        except Exception as e:
            showerror(_('Error'), _('An error occurred when editing item:\n\n') + str(e))

def main():
    root = Tk()
    root.title(constants.programname)
    #root.geometry("800x480")

    if not os.path.exists(constants.filename):
        if askquestion(_('Welcome'), _('It seems like you\'ve started this program for the first time. Do you want to '
                       'create a new database? All existing data will be overwritten.')) == 'yes':
            try:
                open(constants.filename, 'w').close()
            except Exception as e:
                showerror(_('Error'), _('An error occurred when creating file:\n\n') + str(e))
                sys.exit()
        else:
            sys.exit()

    app = Application()
    app.grid(sticky=NSEW, padx=5, pady=5)
    app.focus_force()
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.mainloop()

if __name__ == '__main__':
    main()
