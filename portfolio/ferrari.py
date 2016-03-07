import jinja2
import os
import json
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import Image


if __name__=="__main__":
    galDir = os.path.join(os.curdir, "_gallery")

    categories = [f for f in os.listdir(galDir) if os.path.isdir(os.path.join(galDir, f))]

    output = []

    for cat in categories:
        #Create category object
        catDict = {}
        catDict['title'] = cat.replace("_","-").replace("-"," ")
        catDict['id']= cat.replace("_","").lower()
        catDict['description'] = None
        #Find whole path relative to gallery.py
        catDir = os.path.join(galDir, cat)
        #Get more information about category
        yml_file = os.path.join(catDir, "category.yaml")
        if os.path.isfile(yml_file):
            f = open(yml_file)
            fo = f.read()
            data = load(fo, Loader=Loader)
            if data.has_key("Category"):
                for i in data["Category"]:
                    if i.has_key("title"):
                        catDict["title"] =i["title"]
                    if i.has_key("description"):
                        catDict["description"] = i["description"]
            f.close()
        catDict["collections"] = []
        #Find collections
        collections = [f for f in os.listdir(catDir) if os.path.isdir(os.path.join(catDir,f))]
        for col in collections:
            # 1 Collection
            colDict = {}
            colDict['title'] = col.replace("_"," ").replace("-"," ")
            colDict['id'] = colDict['title'].lower().replace(" ","-")
            colDict['description'] = None
            colDict["imageFile"] = {}
            colDict['type']="images"

            colDir = os.path.join(catDir, col)
            yml_file = os.path.join(colDir, "collection.yaml")
            if os.path.isfile(yml_file):
                f = open(yml_file)
                fo = f.read()
                data = load(fo, Loader=Loader)
                if data.has_key("Collection"):
                    for i in data["Collection"]:
                        if i.has_key("title"):
                            colDict["title"] =i["title"]
                        else:
                            print("[warning]: Collection's title is not specified, default is '{}' ".format(colDict['title']))
                        if i.has_key("description"):
                            colDict["description"] = i["description"]
                        else:
                            print("[warning]: Collection's description is not specified")
                        if i.has_key("type"):
                            colDict["type"] = i["type"]
                        else:
                            print("[warning]: Collection's type is not specified, default is 'images' ")
                        if i.has_key("link"):
                            colDict["link"] = i["link"]
                        else:
                            print("[warning]: Collection's link is not specified, I guess there isn't any link ")
                f.close()
            else:
                print("[warning]: 'collection.yaml' is missing in '{}'".format(colDict['title']))

            medias = [f for f in os.listdir(colDir) if os.path.isfile(os.path.join(colDir,f))]
            media_list = []
            for media in medias:
                d = {}
                d['title']=media.split('.')[0].replace("_"," ").replace("-"," ")

                fi = os.path.join(colDir,media)

                d["ext"]=os.path.splitext(fi)[1].lower()

                accepted_exts = [".png",".jpg",".jpeg",".gif"]
                print d['ext']

                if d['ext'] in accepted_exts and media.startswith(".")==False:
                    size = 860, 860
                    outfile =os.path.join(colDir,".thumbnail."+ media)
                    if fi != outfile:
                        print outfile
                        try:
                            im = Image.open(fi)
                            im.thumbnail(size, Image.ANTIALIAS)
                            im.save(outfile, "JPEG")

                            fi = outfile
                        except IOError:
                            print "cannot create thumbnail for '%s'" % fi


                    if fi.startswith("./"):
                        fi= fi.replace("./","")
                    d['file']=fi

                    #Set Last image as collection's image
                    colDict["imageFile"] = d

                    media_list.append(d)
                else:
                    pass
            colDict["media"] = media_list
            catDict["collections"].append(colDict)
        #back to category
        output.append(catDict)
    #back to gallery


    print json.dumps(output, indent=4)

    #The HTML
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(''))
    template = env.get_template('templates/template.html')
    output_from_parsed_template = template.render(categories = output)

    f = open("index.html","w")
    f.write(output_from_parsed_template)
    print("- - - - - ")
    print("OK, your portfolio is good to go!")
