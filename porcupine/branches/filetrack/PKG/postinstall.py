# Filetrack post installation script

from porcupine.administration import codegen
from schemas.org.innoscript import filetrack

print 'Adding issues to contacts...'
ce = codegen.ItemEditor('schemas.org.innoscript.collab.Contact')
ce.addProperty('issues', filetrack.issues())
ce.commitChanges()

print 'Adding issues to documnents...'
ce = codegen.ItemEditor('schemas.org.innoscript.common.Document')
ce.addProperty('issues', filetrack.issues())
ce.commitChanges()

