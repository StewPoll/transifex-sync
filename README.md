This library will download .PO files from a Transifex project and convert them to .MO files. 

## Installation

Run the following command to ensure you have the requirements installed on your machine.

```
pip install -r requirements.txt
```

## Usage

### Downloading the .MO files

```
python sync.py --project=project_slug --resource=resource_slug
```

It will then look for auth.txt. 

If the file exists, it will take the first line as the username, and second line as the password.

If it doesn't exist, it will ask for your username and password, and create auth.txt for future use.

### Options

#### Path to save files

If you want to specify a path, add `--path=/desired/path/` to the command. The mo files will be saved in the specified folder. 

For example:

```
python sync.py --project=project_slug --resource=resource_slug --path=/Users/MyName/Desktop/languages
```

~ can be used to specify the users relative path.

```
python sync.py --project=project_slug --resource=resource_slug --path=~/Documents/Project/LanguageFiles/
```

This will save to /path/to/user/Documents/Project/LanguageFiles

#### Excluding specific languages 
 
To exclude a specific language code, add --exclude followed by the languages code `--exclude=en_AU` to the command for each language you want to exclude

For example, to exclude Australian (en_AU) and Norwegian (no):

```
python sync.py --project=project_slug --resource=resource_slug --exclude=en_AU --exclude=no
```

#### Keeping the PO Files

If you wish to keep the PO files, append `--keep=True`. The PO files will then be saved to the path, in a /po/ folder.

```
python sync.py --project=project_slug --resource=resource_slug --keep=True
```