"FileTrack reports"
from threading import currentThread

from porcupine.core.servlet import HTTPServlet, XULServlet
from porcupine.oql.command import OqlCommand
from porcupine.utils import xmlUtils, date
from resources.system.ui import PorcupineDesktopServlet
from resources.filetrack.strings import resources

SEARCH_FIELDS = ('displayName', 'sender', 'receiver', 'entryDate')

class FileTrackReport(PorcupineDesktopServlet):
    def getQuery(self):
        oql = 'select entryType, displayName, entryDate, sender.displayName' + \
              ' as sender, receiver.displayName as receiver from '
        qs = self.request.queryString
        oql += "'" + "','".join(qs['scope']) + "'"

        conditions = []
        for field in SEARCH_FIELDS:
            if qs.has_key(field):
                if field != 'entryDate':
                    conditions.append( "'%s' in %s" % (qs[field][0], field) )
                else:
                    conditions.append( "entryDate between date('%s') and date('%s')" % \
                        (qs[field][0], qs[field][1]) )
        if conditions:
            oql += ' where ' + ' and '.join(conditions)
            
        if qs.has_key('orderby'):
            oql += ' order by ' + qs['orderby'][0]

        return oql
    
    def getCriteria(self, locale):
        criteria = ''
        res_contains = resources.getResource('CONTAINS', locale)
        res_scopes = resources.getResource('SEARCH_SCOPE', locale)
        qs = self.request.queryString
        scopes = [
                self.server.store.getItem(scopeid).displayName.value
                for scopeid in qs['scope']
            ]
        criteria += '<tr><td style="white-space:nowrap">%s:</td><td width="100%%">%s</td></tr>' % \
            ( res_scopes, ', '.join(scopes) )
        for field in SEARCH_FIELDS:
            if qs.has_key(field):
                res_field = resources.getResource(field, locale)
                if field!='entryDate':
                    criteria += '<tr><td style="white-space:nowrap">%s %s:</td><td>%s</td></tr>' % \
                        (res_field, res_contains, qs[field][0])
                else:
                    res_from = resources.getResource('FROM', locale)
                    res_to = resources.getResource('TO', locale)
                    date_from = date.Date.fromIso8601(qs[field][0])
                    date_from = date_from.format('dd/mm/yyyy')
                    date_to = date.Date.fromIso8601(qs[field][1])
                    date_to = date_to.format('dd/mm/yyyy')
                    criteria += '<tr><td colspan="2">%s %s %s %s %s</td></tr>' % \
                        (res_field, res_from, date_from, res_to, date_to)
        return criteria

class Report1(FileTrackReport):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = resources.getLocale(sLang).copy()
        self.params['NOW'] = date.Date().format('ddd, dd mmm yyyy h12:min:sec MM', sLang)
        self.params['CRITERIA'] = self.getCriteria(sLang)

        def getentrylocale(iType):
            if iType==1:
                return(self.params['INBOUND'])
            else:
                return(self.params['OUTBOUND'])

        oCmd = OqlCommand()
        sOql = self.getQuery()
        rs = oCmd.execute(sOql)
        rows = [ 
            '''<tr><td>%s</td><td>%s</td>
            <td>%s</td><td>%s</td><td>%s</td></tr>''' % \
            (
                getentrylocale(rec['entryType']), rec['displayName'], rec['sender'],
                rec['receiver'], rec['entryDate'].format('dd/mm/yyyy', sLang)
            )
            for rec in rs
        ]   
        
        self.params['ROWS'] = ''.join(rows)
        self.params['COUNT'] = len(rs)

class Report1_Excel(HTTPServlet):
    def execute(self):
        report = Report1(self.server, self.session, self.request)
        report.setParams()
        currentThread().response = self.response
        self.response.content_type = 'application/excel'
        self.response.setHeader('Content-Disposition', 'attachment;filename=report1.xls')
        oFile = file(report.xul_file)
        self.response.write('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
    <body>''')
        self.response.write(oFile.read() % report.params)
        self.response.write('</body></html>')
        oFile.close()
        
        