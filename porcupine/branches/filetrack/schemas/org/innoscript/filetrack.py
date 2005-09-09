"Porcupine classes for FileTrack"

from porcupine import serverExceptions
from porcupine import datatypes
from schemas.org.innoscript import properties
from porcupine import systemObjects as system

#===============================================================================
# BEGIN Filetrack properties
#===============================================================================

class issueItems(datatypes.RelatorN):
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.collab.Contact',
        'schemas.org.innoscript.common.Document',
        'schemas.org.innoscript.filetrack.LogEntry',
    )
    relAttr = 'issues'

class issues(datatypes.RelatorN):
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.filetrack.Issue',
    )
    relAttr = 'issueItems'
    
class issueClosed(datatypes.Boolean):
    __slots__ = ()

class aa(datatypes.String):
    __slots__ = ()
    
class senderDate(datatypes.Date):
    __slots__ = ()
    
class senderCode(datatypes.String):
    __slots__ = ()
    
class comments(datatypes.Text):
    __slots__ = ()
    
class entryDate(datatypes.Date):
    __slots__ = ()
    isRequired = True
    
class entryType(datatypes.Integer):
    __slots__ = ()
    isRequired = True
    
class sender(datatypes.Reference1):
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.collab.Contact',
        'schemas.org.innoscript.security.User',
    )
    isRequired = True
    
class receiver(datatypes.Reference1):
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.collab.Contact',
        'schemas.org.innoscript.security.User',
    )
    isRequired = True
    
class cc(datatypes.ReferenceN):
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.collab.Contact',
        'schemas.org.innoscript.security.User',
    )
    
class logEntryDocuments(datatypes.Composition):
    __slots__ = ()
    compositeClass = 'schemas.org.innoscript.filetrack.LogEntryDocument'
    #isRequired = True

class currentOwner(datatypes.Reference1):
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.collab.Contact',
        'schemas.org.innoscript.security.User',
    )

#===============================================================================
# END Filetrack properties
#===============================================================================

class FiletrackRoot(system.Container):
    "Filetrack root folder"
    __image__ = "filetrack/images/root16.gif"
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.filetrack.LogEntries',
        #'schemas.org.innoscript.filetrack.LogArchive',
    )
    
class LogEntries(system.Container):
    "Protocol entries container"
    __image__ = "filetrack/images/entries16.gif"
    __slots__ = ('in_counter', 'out_counter')
    containment = (
        'schemas.org.innoscript.filetrack.LogEntry',
    )
    def __init__(self):
        system.Container.__init__(self)
        self.in_counter = 0
        self.out_counter = 0
        
    def getCodeFor(self, item):
        if item.entryType.value==1:
            self.in_counter += 1
            code = 'IN-%05d' % self.in_counter
        else:
            self.out_counter += 1
            code = 'OUT-%05d' % self.out_counter
        return code


class LogEntry(system.Item):
    "Log entry"
    __userprops__ = [
        'entryDate', 'entryType', 'aa', 'sender', 'receiver',
        'cc', 'senderDate', 'senderCode', 'currentOwner',
        'logEntryDocuments', 'comments', 'categories', 'issues'
    ]
    __slots__ = __userprops__ + ['isArchived']
    __props__ = system.Item.__props__ + tuple(__userprops__)

    def __init__(self):
        system.GenericItem.__init__(self)
        self.isArchived = False
        
        self.entryDate = entryDate()
        self.entryType = entryType()
        self.aa = aa()
        self.sender = sender()
        self.receiver = receiver()
        self.cc = cc()
        self.categories = properties.categories()
        self.issues = issues()
        self.senderDate = senderDate()
        self.senderCode = senderCode()
        self.logEntryDocuments = logEntryDocuments()
        self.comments = comments()
        self.currentOwner = currentOwner()
                
    def getImage(self):
        if self.entryType.value==1:
            return "filetrack/images/inbound.gif"
        else:
            return "filetrack/images/outbound.gif"
    __image__ = property(getImage)
    
    # a log entry is not cloneable, so we need to override copyTo
    def copyTo(self, targetId, trans):
        raise serverExceptions.InternalServerError, 'Log entries cannot be copied'
    

class LogEntryDocument(system.Composite):
    "Log entry document"
    __image__ = "/images/document.gif"
    __slots__ = ('file',)
    __props__ = system.Composite.__props__ + __slots__
    def __init__(self):
        system.Composite.__init__(self)
        self.file = properties.file()

class LogArchive(system.Container):
    "Log entries archive folder"
    __image__ = "filetrack/images/archive16.gif"
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.filetrack.LogArchiveSet',
    )
    
class LogArchiveSet(system.Container):
    "Log entries archive set"
    __image__ = "filetrack/images/archive16.gif"
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.filetrack.LogEntry',
    )

class IssueFolder(system.Container):
    "Issues Folder"
    __image__ = "filetrack/images/issue_folder.gif"
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.filetrack.Issue',
    )
    
class Issue(system.Item):
    "Issue"
    __image__ = "filetrack/images/issue.gif"
    __slots__ = ('issueClosed', 'issueItems')
    __props__ = system.Item.__props__ + __slots__
    def __init__(self):
        system.Item.__init__(self)
        self.issueClosed = issueClosed()
        self.issueItems = issueItems()

