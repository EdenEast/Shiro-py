# Shiro
**View, Manage, Download and stay up to date on your manga library.**

## Table of Contents
* [Inspiration](#inspiration)
* [Shortcut Keys](#shortcut-key)
* [Supported Sites](#supperted-sites)
* [Development](#development)
* [Freezing with cx_Freeze](#freezing)
* [Third Party Dependencies](#dependencies)

## <a name="inspiration"></a> Inspiration
I have looked around for a manga library application to keep up with all of the manga that I am reading and could not find anything that satified me. This is how Shiro was born.

![split](http://i.imgur.com/8rCchO2.png)
![main_window](http://i.imgur.com/Zj8Xd2i.png)
![reading_window](http://i.imgur.com/ZqdwRKz.png)

## <a name="shortcut-key"><a/> Shortcut Keys

#### Main Window
| Key           | Action                                                   |
| :------------ | :------------------------------------------------------- |
| Escape        | Close window                                             |
| Q             | Close window                                             |
| R             | Read next unread chapter / Read current selected chapter |
| Ctrl + R      | Read next unread chapter                                 |
| U             | Update selected manga                                    |
| Ctrl + U      | Update all manga in library                              |
| D             | Start downloading currently selected manga               |
| Ctrl + D      | Abort downloading                                        |
| Backspace     | Show manga list                                          |
| Enter / Space | Show chapter list / Read current selected chapter        |

### Reading View
| Key                     | Action                                                               |
| :---------------------- | :------------------------------------------------------------------- |
| Q                       | Close window                                                         |
| F                       | Toggle full screen                                                   |
| Right / Space           | Move down / Next page / Next chapter                                 |
| Ctrl + Right / Ctrl + E | Jump to last page                                                    |
| Ctrl + Shift + Right    | Next chapter                                                         |
| Left                    | Move up / Previous page / Previous chapter                           |
| Ctrl + Left / Ctrl + B  | Jump to first page                                                   |
| Ctrl + Shift + Left     | Previous chapter                                                     |
| S                       | Toggle double page reading direction right -> left and vice versa    |
| D                       | Toggle between single and double page viewing                        |
| M                       | Toggle viewing modes from offline to online and vice versa           |
| 1                       | Scale page to the original size (only available in single page mode) |
| 2                       | Scale page to fit vertically in window                               |
| 3                       | Scale page to fit horizontally in window                             |
| 4                       | Scale page to the bets fit for image and window                      |

## <a name="supperted-sites"></a> Supported Sites
- [MangaLife](http://manga.life)

More supperted websites to come

## <a name="development"></a> Development
Shiro is writen in in python 3.4 (writen for what PyQt4 is). To Build Shiro make sure that you have python 3.4 installed and run shiro.py. **Make sure** that you also have the dependencies needed to build it.

## <a name="freezing"></a> Freezing [.exe] with cx_Freeze
Shiro uses [cx_Freeze](http://cx-freeze.sourceforge.net) to package the application to different platforms.
Note: before freezing you have to make sure that the location is correct in `main_window.py`
```python
class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        # @NOTE: toggle these two lines depending on how you are running. The first one is for develop 2nd for building
        # location = 'shiro/ui/main_window.ui'
        location = 'main_window.ui'
        uic.loadUi(location, self)
```
Once you have made sure that the location is set to the above example you are ready to freeze the application.
To freeze the application open up a terminal/console in root folder and run the command
`python setup.py build`

If you want to build an installer run this command the same way that you ran the build command

#### Windows
`python setup.py bdist_msi`

#### OSX
`python setup.py bdist_dmg`

## <a name="dependencies"></a> Third Party Dependencies
- [PyQt4](https://pypi.python.org/pypi/PyQt4)
- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4)
- [Pillow](https://pypi.python.org/pypi/Pillow)
- [Requests](https://pypi.python.org/pypi/requests)
