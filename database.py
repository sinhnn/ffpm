import csv
import json
# import configparser


class Database():
    changed = False
    def __init__(self, configfile):
        if configfile:
            self.load(configfile)
            self.configfile = configfile
        else: self.items = []

    def load(self, configfile):
        try:
            with open(configfile, 'r') as f:
                self.items = json.load(f)
        except:
            self.items = []
        self.changed = True

    def tag(self, string):
        pass
        # for item in self.items:
        #     if (string.lower() in item.index.lower() 
        #             or string.lower() in item.desc.lower()
        #         ):
        #         item["tag"] = 'FOUND'
        #     else:
        #         item["tag"] = 'NOT_FOUND'
        # return 

    def add(self, data):
        self.items.append(data)
        self.changed = True
        return data

    def rm(self, id):
        self.changed = True
        return self.items.pop(id)

    def set(self, id, data):
        self.changed = True
        self.items[id] = data

    def export (self, ofile):
        with open(ofile, 'w') as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)
        return True

    def save(self):
        self.export(self.configfile)
