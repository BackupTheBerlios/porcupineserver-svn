from porcupine.datatypes import Reference1
from porcupine.administration import offlinedb
from porcupine.oql.command import OqlCommand

from org.innoscript.desktop.schema.handlers import PersonalFolderHandler

print 'opening porcupine database...'
db = offlinedb.getHandle()

print 'finding all users...'
cmd = OqlCommand()
recs = cmd.execute("select id from 'users' where instanceof('org.innoscript.desktop.schema.security.User')")

print 'adding personal folders...'
txn = offlinedb.OfflineTransaction()

for rec in recs:
    user = db.getItem(rec['id'], txn)
    if not hasattr(user, 'personalFolder'):
        setattr(user, 'personalFolder', Reference1())
    #user.personalFolder.value = ''
    PersonalFolderHandler.on_create(user, txn)
    db.putItem(user, txn)
    
txn.commit()

print 'closing database...'
offlinedb.close()

print 'finished'
