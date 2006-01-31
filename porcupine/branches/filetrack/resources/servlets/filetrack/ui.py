"FileTrack interfaces"

from porcupine.config.resources import Locale
from porcupine.core.servlet import XULServlet
from resources.servlets.ui import PorcupineDesktopServlet
from resources.servlets.filetrack.strings import resources
from schemas.org.innoscript import filetrack
from porcupine.security import objectAccess
from porcupine.oql.command import OqlCommand
from porcupine.utils import xmlUtils, date

PROTOCOL_ROOT_ID = 'JHwXTIaq'
CATEGORIES_ID = 'categories'
ISSUES_ID = '84L6aTcf'

class Frm_LogEntryNew(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        oEntry = filetrack.LogEntry()
        self.params = {
            'entryDate': resources.getResource('entryDate', sLang),
            'entryType': resources.getResource('entryType', sLang),
            'description': resources.getResource('description', sLang),
            'sender': resources.getResource('sender', sLang),
            'receiver': resources.getResource('receiver', sLang),
            'cc': resources.getResource('cc', sLang),
            'aa': resources.getResource('aa', sLang),
            'senderDate': resources.getResource('senderDate', sLang),
            'senderCode': resources.getResource('senderCode', sLang),
            'currentOwner': resources.getResource('currentOwner', sLang),
            'logEntryDocuments': resources.getResource('logEntryDocuments', sLang),
            'issues': resources.getResource('issues', sLang),
            'categories': resources.getResource('categories', sLang),
            'comments': resources.getResource('comments', sLang),

            'CREATE': resources.getResource('CREATE', sLang),
            'CLOSE': resources.getResource('CLOSE', sLang),

            'TITLE': self.item.displayName.value + ' - ' + resources.getResource('NEW_PROTOCOL_ENTRY', sLang),
            'ADD': resources.getResource('ADD', sLang),
            'REMOVE': resources.getResource('REMOVE', sLang),

            'INBOUND': resources.getResource('INBOUND', sLang),
            'OUTBOUND': resources.getResource('OUTBOUND', sLang),

            'SENDER_RELCC': '|'.join(oEntry.sender.relCc),
            'RECEIVER_RELCC': '|'.join(oEntry.receiver.relCc),
            'CURRENT_OWNER_RELCC': '|'.join(oEntry.currentOwner.relCc),
            
            'CC_RELCC': '|'.join(oEntry.cc.relCc),
            
            'CATEGORIES_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + CATEGORIES_ID,
            'CATEGORIES_CC': '|'.join(oEntry.categories.relCc),
            
            'ISSUES_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + ISSUES_ID,
            'ISSUES_CC': '|'.join(oEntry.issues.relCc),
            
            'TODAY': oEntry.entryDate.toIso8601(),
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'ROOTURI': self.request.serverVariables['SCRIPT_NAME']
        }
        
class Frm_LogEntryReply(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        sender = self.item.sender.getItem()
        receiver = self.item.receiver.getItem()
        self.params = {
            'entryDate': resources.getResource('entryDate', sLang),
            'entryType': resources.getResource('entryType', sLang),
            'description': resources.getResource('description', sLang),
            'sender': resources.getResource('sender', sLang),
            'receiver': resources.getResource('receiver', sLang),
            'cc': resources.getResource('cc', sLang),
            'aa': resources.getResource('aa', sLang),
            'senderDate': resources.getResource('senderDate', sLang),
            'senderCode': resources.getResource('senderCode', sLang),
            'currentOwner': resources.getResource('currentOwner', sLang),
            'logEntryDocuments': resources.getResource('logEntryDocuments', sLang),
            'issues': resources.getResource('issues', sLang),
            'categories': resources.getResource('categories', sLang),
            'comments': resources.getResource('comments', sLang),

            'REPLY': resources.getResource('REPLY', sLang),
            'CLOSE': resources.getResource('CLOSE', sLang),

            'TITLE': resources.getResource('REPLY_TO', sLang) + ' ' + \
                        self.item.displayName.value,
            'ADD': resources.getResource('ADD', sLang),
            'REMOVE': resources.getResource('REMOVE', sLang),

            'INBOUND': resources.getResource('INBOUND', sLang),
            'OUTBOUND': resources.getResource('OUTBOUND', sLang),

            'SENDER_RELCC': '|'.join(self.item.sender.relCc),
            'RECEIVER_RELCC': '|'.join(self.item.receiver.relCc),
            'CURRENT_OWNER_RELCC': '|'.join(self.item.currentOwner.relCc),
            'CC_RELCC': '|'.join(self.item.cc.relCc),
            
            'CATEGORIES_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + CATEGORIES_ID,
            'CATEGORIES_CC': '|'.join(self.item.categories.relCc),
            
            'ISSUES_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + ISSUES_ID,
            'ISSUES_CC': '|'.join(self.item.issues.relCc),
            
            'TODAY': date.Date().toIso8601(),
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.getParent().id,
            
            'SENDER_ID': receiver.id,
            'SENDER_NAME': receiver.displayName.value,
            'RECEIVER_ID': sender.id,
            'RECEIVER_NAME': sender.displayName.value,
            'ROOTURI': self.request.serverVariables['SCRIPT_NAME'],
        }
        
class Frm_LogEntryProperties(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.response.setHeader('Cache-Control', 'no-cache')
        
        sender = self.item.sender.getItem()
        if sender:
            sender_dn = sender.displayName.value
        else:
            sender_dn = self.item.sender.value
            
        receiver = self.item.receiver.getItem()
        if receiver:
            receiver_dn = receiver.displayName.value
        else:
            receiver_dn = self.item.receiver.value
            
        current_owner = self.item.currentOwner.getItem()
        if current_owner:
            current_owner_dn = current_owner.displayName.value
        else:
            current_owner_dn = self.item.currentOwner.value
            
        readonly = (self.item.isArchived or \
            objectAccess.getAccess(self.item, self.session.user) < objectAccess.AUTHOR)
        
        self.params = {
            'entryDate': resources.getResource('entryDate', sLang),
            'entryType': resources.getResource('entryType', sLang),
            'description': resources.getResource('description', sLang),
            'sender': resources.getResource('sender', sLang),
            'receiver': resources.getResource('receiver', sLang),
            'cc': resources.getResource('cc', sLang),
            'aa': resources.getResource('aa', sLang),
            'senderDate': resources.getResource('senderDate', sLang),
            'senderCode': resources.getResource('senderCode', sLang),
            'currentOwner': resources.getResource('currentOwner', sLang),
            'logEntryDocuments': resources.getResource('logEntryDocuments', sLang),
            'issues': resources.getResource('issues', sLang),
            'categories': resources.getResource('categories', sLang),
            'comments': resources.getResource('comments', sLang),

            'READONLY': self.getStringFromBoolean(readonly),

            'UPDATE': resources.getResource('UPDATE', sLang),
            'CLOSE': resources.getResource('CLOSE', sLang),

            'TITLE': self.item.displayName.value,
            'IMAGE': self.item.__image__,
            'ADD': resources.getResource('ADD', sLang),
            'REMOVE': resources.getResource('REMOVE', sLang),

            'INBOUND': resources.getResource('INBOUND', sLang),
            'OUTBOUND': resources.getResource('OUTBOUND', sLang),
            
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'PROTOCOL_ROOT_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + PROTOCOL_ROOT_ID,
            'ENTRY_DATE': self.item.entryDate.toIso8601(),
            'IS_INBOUND': self.getStringFromBoolean( self.item.entryType.value == 1 ),
            'NOT_IS_INBOUND': self.getStringFromBoolean ( not(self.item.entryType.value == 1) ),
            'DESCRIPTION': self.item.description.value,
            
            'SENDER_RELCC': '|'.join( self.item.sender.relCc ),
            'SENDER_ID': self.item.sender.value,
            'SENDER_DN': sender_dn,
            
            'RECEIVER_RELCC': '|'.join( self.item.receiver.relCc ),
            'RECEIVER_ID': self.item.receiver.value,
            'RECEIVER_DN': receiver_dn,
            
            'AA': self.item.aa.value,
            'SENDER_DATE': self.item.senderDate.toIso8601(),
            'SENDER_CODE': self.item.senderCode.value,
            
            'CURRENT_OWNER_RELCC': '|'.join( self.item.currentOwner.relCc ),
            'CURRENT_OWNER_ID': self.item.currentOwner.value,
            'CURRENT_OWNER_DN': current_owner_dn,
            
            'CC_RELCC': '|'.join(self.item.cc.relCc),
            
            'CATEGORIES_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + CATEGORIES_ID,
            'CATEGORIES_CC': '|'.join(self.item.categories.relCc),

            'ISSUES_URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + ISSUES_ID,
            'ISSUES_CC': '|'.join(self.item.issues.relCc),
            
            'COMMENTS': xmlUtils.XMLEncode(self.item.comments.value),
            'ROOTURI': self.request.serverVariables['SCRIPT_NAME'],
        }
                
        self.params['CC_OPTIONS'] = ''
        ccs = self.item.cc.getItems()
        for cc in ccs:
            self.params['CC_OPTIONS'] += \
                '<a:option value="%s" img="%s" caption="%s" ondblclick="autoform.displayRelated"></a:option>' \
                % (cc.id, cc.__image__, cc.displayName.value)
        
        self.params['DOCUMENTS'] = ''
        documents = self.item.logEntryDocuments.getItems()
        for doc in documents:
            self.params['DOCUMENTS'] += '<a:mfile filename="%s" id="%s"></a:mfile>' % (doc.file.filename, doc.id)
        
        self.params['CATEGORIES'] = ''
        categories = self.item.categories.getItems()
        for category in categories:
            self.params['CATEGORIES'] += \
                '<a:option value="%s" img="%s" caption="%s" ondblclick="autoform.displayRelated"></a:option>' \
                % (category.id, category.__image__, category.displayName.value)
        
        self.params['ISSUES'] = ''
        issues = self.item.issues.getItems()
        for issue in issues:
            self.params['ISSUES'] += \
                '<a:option value="%s" img="%s" caption="%s" ondblclick="autoform.displayRelated"></a:option>' \
                % (issue.id, issue.__image__, issue.displayName.value)
        
        self.params['SECURITY_TAB'] = self.getSecurity(self.item)

class Dlg_SelectPersons(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = Locale(resources.getLocale(sLang).copy())
        self.params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']

class Frg_LogEntries(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        params = Locale(resources.getLocale(sLang).copy())
        params['TITLE'] = self.item.displayName.value
        params['PID'] = self.item.id
        params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']
        self.params = params
        
class Frg_Issues(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = Locale(resources.getLocale(sLang).copy())
        self.params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']
        
class Frg_Search(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = Locale(resources.getLocale(sLang).copy())
        self.params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']

class Frg_Contacts(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = Locale(resources.getLocale(sLang).copy())
        self.params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']
        
class Frg_Reports(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = Locale(resources.getLocale(sLang).copy())
        self.params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']
        
class Dlg_Report(XULServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = Locale(resources.getLocale(sLang).copy())
        self.params['ROOTURI'] = self.request.serverVariables['SCRIPT_NAME']
    