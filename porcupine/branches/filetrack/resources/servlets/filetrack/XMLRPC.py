"XMLRPC Servlets for the FileTrack application"

import os

from porcupine.security import objectAccess
from porcupine.security.policy import policymethod
from porcupine import serverExceptions
from resources.servlets.XMLRPC import ContainerGeneric, ItemGeneric
from porcupine.oql.command import OqlCommand
from schemas.org.innoscript import filetrack
from schemas.org.innoscript import security

POLICY_RESET_COUNTERS = 'meSiv7EL'
POLICY_ARCHIVE = 'UlBfswkL'

class LogEntryUpdater(object):
    def updateLogEntry(self, log_entry, data):
        # set props
        log_entry.entryDate.value = data['entryDate'].value
        log_entry.entryType.value = int(data['entryType'])
        log_entry.description.value = data['description']
        log_entry.sender.value = data['sender']
        log_entry.receiver.value = data['receiver']
        log_entry.cc.value = data['cc']
        log_entry.aa.value = data['aa']
        log_entry.senderDate.value = data['senderDate'].value
        log_entry.senderCode.value = data['senderCode']
        log_entry.currentOwner.value = data['currentOwner']
        log_entry.categories.value = data['categories']
        log_entry.issues.value = data['issues']
        log_entry.comments.value = data['comments']
        
        # assign as readers the users involved with this new entry
        oPersonsInvolved = [log_entry.sender.getItem()] + \
            [log_entry.receiver.getItem()] + \
            [self.server.store.getItem(sid) for sid in log_entry.cc.value]
        # we need to get only users and not contacts
        # in order to set the ACL
        oUsers = [person for person in oPersonsInvolved
            if isinstance(person, security.User)]

        if log_entry.security.has_key('everyone'):
            del log_entry.security['everyone']
        # assign the users the reader role
        for oUser in oUsers:
            # assign the reader role only if the user
            # has not been assigned another role
            if not(log_entry.security.has_key(oUser.id)):
                log_entry.security[oUser.id] = objectAccess.READER 

        # create files uploaded
        filesuploaded = data['logEntryDocuments']
        log_entry.logEntryDocuments.value = []
        
        for oFileInfo in filesuploaded:
            if oFileInfo['id']:
                # if it is an exising file get it from the store
                oFile = self.server.store.getItem(oFileInfo['id'])
            else:
                # if it's a new file create the composite
                # LogEntryDocument and load the file from the file system
                oFile = filetrack.LogEntryDocument()
                oFile.displayName.value = oFileInfo['filename']
                oFile.file.filename = oFileInfo['filename']
                sPath = self.server.temp_folder + '/' + oFileInfo['temp_file']
                oFile.file.loadFromFile(sPath)
            
            log_entry.logEntryDocuments.value.append(oFile)


class LogEntries(ContainerGeneric, LogEntryUpdater):
    def create(self, data):
        oUser = self.session.user
        self.runAsSystem()
        
        # because we run as system we need to check ourselves
        # for write permissions. We run under the system account because
        # this servlet needs to set the log entry permisssions according
        # to the sender, receiver and cc field values
        if objectAccess.getAccess(self.item, oUser) < objectAccess.AUTHOR:
            raise serverExceptions.PermissionDenied
        
        # create new item
        oNewItem = filetrack.LogEntry()
        
        oNewItem.inheritRoles = False
        oNewItem.security = self.item.security

        self.updateLogEntry(oNewItem, data)

        txn = self.server.store.getTransaction()
        # compute log entry code
        container = self.server.store.getItem(self.item.id, txn)
        oNewItem.displayName.value = container.getCodeFor(oNewItem)
        
        oNewItem.appendTo(container, txn)
        txn.commit()

        # remove temporary uploaded files
        dummy_list = [
            os.remove(self.server.temp_folder + '/' + oFileInfo['temp_file'])
            for oFileInfo in data['logEntryDocuments']
        ]
        return True
        
    def resetCounters(self):
        if self.item.hasChildren():
            return False
        else:
            txn = self.server.store.getTransaction()
            container = self.server.store.getItem(self.item.id, txn)
            container.in_counter = 0
            container.out_counter = 0
            container.update(txn)
            txn.commit()
            return True
            
    resetCounters = policymethod(resetCounters, POLICY_RESET_COUNTERS)
        
    def archive(self, destination, dateRange):
        oCmd = OqlCommand()
        sOql = "select id from '" + self.item.id + \
            "' where entryDate between " + \
            "date('" + dateRange[0].toIso8601() + "') and " + \
            "date('" + dateRange[1].toIso8601() + "')"
        oRes = oCmd.execute(sOql)
        
        txn = self.server.store.getTransaction()
        itemlist = [self.server.store.getItem(rec['id'], txn) for rec in oRes]
        for item in itemlist:
            item.isArchived = True
        dummyList = [x.moveTo(destination, txn) for x in itemlist]
        txn.commit()
        # return the number of log items archived
        return len(oRes)
        
    archive = policymethod(archive, POLICY_ARCHIVE)

class LogEntry(ItemGeneric, LogEntryUpdater):
    def update(self, data):
        self.item.inheritRoles = False
        self.item.security = self.item.getParent().security
        
        self.updateLogEntry(self.item, data)

        txn = self.server.store.getTransaction()
        self.item.update(txn)
        txn.commit()

        # remove temporary uploaded files
        dummy_list = [
            os.remove(self.server.temp_folder + '/' + oFileInfo['temp_file'])
            for oFileInfo in data['logEntryDocuments'] if oFileInfo['temp_file']
        ]

        return True
        