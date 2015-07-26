from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import loadPrcFileData

WANTPSTATS = False
WANTDEBUGGINGTOOLS = False
# the amount of information written to the out.log logfile
loadPrcFileData("", "notify-level error")
loadPrcFileData("", "default-directnotify-level error")
# the fps counter in the right upper corner
loadPrcFileData("", "show-frame-rate-meter #t")
# do we want some extra debugging tools?
if WANTDEBUGGINGTOOLS or WANTPSTATS:
    # enable pstats for performance monitoring
    loadPrcFileData("", "want-pstats #t")
if WANTDEBUGGINGTOOLS:
    # some debugging tools for panda3d
    loadPrcFileData("", "want-directtools #t")
    loadPrcFileData("", "want-tk #t")

# Some more debugging goodies after we set up the ShowBase (APP/Main)
def setupDebugHelp(APP):
    def toggleOobe():
        """Switch between free camera (steering with the mouse) and
        the camera controled by the game"""
        APP.oobe()

    def explorer():
        """activates the Panda3D halp tool to explore the
        render Nodepath"""
        APP.render.explore()

    def analyze():
        APP.render.analyze()

    def toggleWireframe():
        """Switch between wired model view and normal view"""
        base.toggleWireframe()

    from time import strftime
    def takeScreenshot():
        # make a screenshot
        path = os.path.join(Settings.settingsPath, "screenshots")
        if not os.path.exists(path):
            os.makedirs(path)
        # create the filename with a name and the actual time
        fn = "Screenshot" + strftime("_%a_%d-%m-%Y_%H:%M:%S") + ".png"
        path = os.path.join(path, fn)
        APP.win.saveScreenshot(Filename.fromOsSpecific(path))
        logging.info(str.format("take Screenshot in: {0}", path))

    # create a DirectObject object to handle the key input by the user
    directobject = DirectObject()
    directobject.accept("f2", analyze)
    directobject.accept("f3", explorer)
    directobject.accept("f4", toggleWireframe)
    directobject.accept("f5", takeScreenshot)
    directobject.accept("f12", toggleOobe)
