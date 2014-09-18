# PyChampion on Django

## Attempts at creating a self-contained web application for Desktop use

Web App for reporting on aging of Finding Track reviews and status

Recipe

* Python 2.7
* Django
* SQLite
* PyInstaller

*Tested on Windows*

### Setting Up Python

Follow this [guide](http://docs.python-guide.org/en/latest/starting/install/win/)

##### Setup Virtualenv and Virtualenvwrapper (Optional)

In addition to virtualenv, you can install virtualenvwrapper which makes the use of virtualenv easier.

```
pip install virtualenvwrapper-win
```

If you can't install through pip, go to the [python library](https://pypi.python.org/pypi/virtualenvwrapper-win), download and extract the virtualenvwrapper-win to a directory of your choosing.

Open up a CMD window, CD into the library you unpacked. Most of these libraries are packaged in a tar.gz file, which requires a 3rd party extractor to unpack. I prefer 7-Zip, but there are other options. These tar.gz are basically compressed twice, so you'll have to be sure you unpack to the actual files. 

Once unpacked, CD into the library and type the following command:

```
python setup.py install
```

*Virtualenv and virtualenvwrapper aren't required, but highly recommended as it sets up a virtual environment for installing all of the python libraries specific to your project. When you start working on multiple projects you'll end up having some library dependency conflicts, unless you have a virtual environment for each project*

### Setting Up Project on Your Machine

##### Install GIT

[Download GIT for Windows](http://git-scm.com/download/win)

##### Download Source Code

```
git clone https://[your-username]@bitbucket.org/walexnelson/pychampion.git
```

##### Download Python Libraries

In your CMD window, CD to your project root directory where the ```requirements.txt``` file is located and enter the following command

```
pip install -r requirements.txt
```

This command will install all the libraries that are required for pyChampion. 

In addition to the python libraries installed above, you'll have to install the following two libraries manually:

* PyInstaller ([Development](https://github.com/pyinstaller/pyinstaller/zipball/develop)) 
* PyWin32 ([Build 219](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/)) 

### Packaging Source

##### Package pyChampion

Once you have made the needed changes to the source code you are ready to package the app into a distributable exe.

CD to your project root and type the following command into your terminal:

```
pyinstaller project.spec
```

PyInstaller will create a new directory under `dist`. Once created you'll have to manually copy the `static` and `templates` directories and the `db.sqlite` database file into the `pychamp` directory under `dist`. 

##### Package the ZIP Extractor

The following command will create a single exe file in `dist` next to the `pychamp` directory.

```
pyinstaller zip_extract.spec
```

##### Ready Package for Distribution

Once you have run PyInstaller on both the project and the zip_extractor, you are able to zip up the `pychamp` directory under the `dist` directory. Now you should have the following structure under `dist`:

```
pychamp
pychamp.zip
extract.exe
```

You can now move the ZIP folder and the EXE file to wherever you want for distribution.
