__author__ = 'stewartpolley'

import sys
import polib
import getopt
from transifex.api import TransifexAPI
import shutil
import os

class AuthenticationError(Exception):
    pass

def main(username, password, project_slug, resource_slug, path, exclude, keep):
    print "Initialising"
    trans = TransifexAPI(username, password, "http://transifex.com")
    print "Testing connection"
    if not trans.ping():
        raise AuthenticationError("Whoops, please check the username/password")
    print "Getting languages"
    languages = trans.list_languages(project_slug, resource_slug)
    if exclude != []:
        print "Removing excluded languages from language list, {}".format(exclude)
        for language in exclude:
            try:
                languages.remove(language)
                print("{} will be ignored".format(language))
            except ValueError:
                print "{} not a valid language".format(language)


    directory = os.path.dirname("{}/po/".format(path))
    if not os.path.exists(directory):
        os.makedirs(directory)

    print "Downloading Po Files."
    for language in languages:
        print "Downloading {}. {} of {}".format(language, languages.index(language) + 1, len(languages))
        po_path = "{}/po/{}.po".format(path,language)
        mo_path = "{}/{}.mo".format(path, language)
        trans.get_translation(project_slug, resource_slug, language, po_path)
        print "{} downloaded, converting to MO, saving to {}".format(language, mo_path)
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        print "{} converted".format(language)

    print "All languages downloaded and converted"
    if not keep:
        print "Deleting /PO file"
        shutil.rmtree("{}/po/".format(path))
    else:
        print "Keeping PO Files in {}/po/".format(path)

    return

if __name__ == "__main__":
    project_slug = ""
    resource_slug = ""
    save_path = "language_files"
    exclude = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["project=", "resource=", "path=", "exclude=", "keep="])
    except getopt.GetoptError:
        print getopt.GetoptError
        print("""Usage:python sync.py --project=project_slug --resource=resource_slug [--path=<dir>, --exclude=lang_code, --keep=True]\n
        E.G. python sync.py user pass --project=my_app --resource=core --path=/usr/bin/language_files/ --exclude=en_AU""")
        sys.exit(2)

    keep = False

    for opt, arg in opts:
        if opt == "--project":
            project_slug = arg
        elif opt == "--resource":
            resource_slug = arg
        elif opt == "--path":
            save_path = arg
            if save_path[0] == "~":
                save_path = os.path.expanduser(save_path)
        elif opt == "--exclude":
            exclude.append(arg)
        elif opt == "--keep":
            keep = arg

    try:
        with open("auth.txt", "r") as f: auth=f.readlines()
    except IOError:
        auth =[]
        auth.append(raw_input("Please enter your Transifex username: "))
        auth.append(raw_input("Please enter your Transifex password: "))
        auth[0] += "\n"
        with open("auth.txt", "w+") as f: f.writelines(auth)
        

    if project_slug == "":
    	raw_input("Please specify your project using --project=project_slug")
    	sys.exit(2)
    	
    if resource_slug == "":
    	raw_input("Please specify your resource using --resource=resource_slug")
    	sys.exit(2)

    main(auth[0].strip(),
         auth[1],
         project_slug, 
         resource_slug,
         save_path,
         exclude,
         keep)