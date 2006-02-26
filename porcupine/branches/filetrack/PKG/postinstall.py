# Filetrack post installation script
import os

from porcupine.administration import codegen
from schemas.org.innoscript import filetrack

def _deltree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)

print 'Adding issues to contacts...'
ce = codegen.ItemEditor('schemas.org.innoscript.collab.Contact')
ce.addProperty('issues', filetrack.issues())
ce.commitChanges()

print 'Adding issues to documnents...'
ce = codegen.ItemEditor('schemas.org.innoscript.common.Document')
ce.addProperty('issues', filetrack.issues())
ce.commitChanges()

if os.path.exists('resources/servlets/filetrack'):
    _deltree('resources/servlets/filetrack')