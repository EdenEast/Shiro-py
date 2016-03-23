# Shiro
View, Manage, download and stay up to date on your manga library.

I have looked for a manga library application to keep up with all of the manga that I am currently reading and could not find anything
that scarified me. This is how Shiro was born.

Currently in development and is not ready for an official release.

## Development
Shiro is writen in in python 3.4 (writen for what PyQt4 is). To Build KML make sure that you have python 3.4 installed and run shiro.py.
MAKE SURE that you also have the dependencies needed to build it.

## Freezing [.exe] with cx_Freeze
Shiro uses [cx_Freeze](http://cx-freeze.sourceforge.net) to package the application to different platforms. To freeze the application open
up a terminal/console in root folder and run the command
`python setup.py build`

If you want to build an installer run this command the same way that you ran the build command
Windows
`python setup.py bdist_msi`
OSX
`python setup.py bdist_dmg`

## Third Party Dependencies
- [PyQt4](https://pypi.python.org/pypi/PyQt4)
- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4)
- [Pillow](https://pypi.python.org/pypi/Pillow)
- [Requests](https://pypi.python.org/pypi/requests)
