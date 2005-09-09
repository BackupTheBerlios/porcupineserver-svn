# Filetrack uninstall script

from porcupine.administration import codegen
from schemas.org.innoscript import filetrack

print 'Removing issues from contacts...'
ce = codegen.ItemEditor('schemas.org.innoscript.collab.Contact')
ce.removeProperty('issues')
ce.commitChanges()

print 'Removing issues from documnents...'
ce = codegen.ItemEditor('schemas.org.innoscript.common.Document')
ce.removeProperty('issues')
ce.commitChanges()