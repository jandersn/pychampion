# PyChampion on Django

## Attempts at creating a self-contained web application for Desktop use

Web App for reporting on aging of Finding Track reviews and status

Recipe

* Python 2.7
* Django
* SQLite
* PyInstaller

*Tested on Windows*

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
