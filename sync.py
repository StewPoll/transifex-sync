#!/usr/bin/env python2
import codecs
import getopt
import os
import polib
import requests
import shutil
import sys
from transifex.api import TransifexAPI, TransifexAPIException


def base_encode(string):
    return codecs.encode(string.encode(), "base-64").decode()


def base_decode(string):
    return codecs.decode(string.encode(), "base-64").decode()

class Transifex(TransifexAPI):
    """
    The TransifexAPI is great, only need to overwrite method
    """
    def get_translation(self, project_slug, resource_slug, language_code,
                        path_to_pofile):
        """
        Returns the requested translation, if it exists. The translation is
        returned as a serialized string, unless the GET parameter file is
        specified.

        @param project_slug
            The project slug
        @param resource_slug
            The resource slug
        @param language_code
            The language_code of the file.
            This should be the *Transifex* language code
        @param path_to_pofile
            The path to the pofile which will be saved

        @return None

        @raises `TransifexAPIException`
        @raises `IOError`
        """
        url = '%s/project/%s/resource/%s/translation/%s/?onlyreviewed' % (
            self._base_api_url, project_slug, resource_slug, language_code
        )
        output_path = path_to_pofile
        query = {
            'file': ''
        }
        response = requests.get(url, auth=self._auth, params=query)
        if response.status_code != requests.codes['OK']:
            raise TransifexAPIException(response)
        else:
            handle = open(output_path, 'w')
            for line in response.iter_content():
                handle.write(line)
            handle.close()


class AuthenticationError(Exception):
    pass


def main(username, password, project_slug, resource_slug, path, exclude, keep):
    print "Initialising"
    trans = Transifex(username, password, "http://transifex.com")
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
        print "Deleting /PO files"
        shutil.rmtree("{}/po/".format(path))
    else:
        print "Keeping PO Files in {}/po/".format(path)

    return

if __name__ == "__main__":
    save_path = "language_files"
    exclude = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["project=", "resource=", "path=", "exclude=", "keep="])
    except getopt.GetoptError:
        print getopt.GetoptError
        print "Usage:python sync.py --project=project_slug --resource=resource_slug [--path=<dir> --exclude=lang_code --keep=True]"
        print "E.G. python sync.py --project=my_app --resource=core --path=/usr/bin/language_files/ --exclude=en_AU"
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
        with open("auth.txt", "r") as f:
            auth=f.readlines()
            username = base_decode(auth[0])
            password = base_decode(auth[1])
    except IOError:
        username = raw_input("Please enter your Transifex username: ")
        password = raw_input("Please enter your Transifex password: ")
        with open("auth.txt", "w+") as f:
            f.writelines([base_encode(username), base_encode(password)])

    if not project_slug:
        print("Please specify your project using --project=project_slug")
        sys.exit(2)

    if not resource_slug:
        print("Please specify your resource using --resource=resource_slug")
        sys.exit(2)

    main(username,
         password,
         project_slug,
         resource_slug,
         save_path,
         exclude,
         keep)
