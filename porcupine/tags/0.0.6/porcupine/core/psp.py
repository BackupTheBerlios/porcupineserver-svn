#===============================================================================
#    Copyright 2005, Tassos Koutsovassilis
#
#    This file is part of Porcupine.
#    Porcupine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2.1 of the License, or
#    (at your option) any later version.
#    Porcupine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#    You should have received a copy of the GNU Lesser General Public License
#    along with Porcupine; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#===============================================================================
"Porcupine Python Server Pages"

import os, re, marshal

from porcupine.core.servlet import HTTPServlet
from porcupine import serverExceptions

PSP_TAGS = re.compile('(<%.*?%>)', re.DOTALL)
PSP_DECREASE_INDENT = re.compile('else|elif|except|finally')
PSP_REMOVE_EXTENSION = re.compile('(.*)\.(.*)')
TRANS_REQUIRED = re.compile('<!--\s*transaction:(\S*)\s*-->')
NT_UTF_8_IDENTIFIER = chr(239)+chr(187)+chr(191)

class PspExecutor(HTTPServlet):
    def execute(self, fileName):
        try:
            # get modification date
            sMod = os.stat(fileName)[8]
        except OSError:
            # TODO: What is fn?????
            fn = fileName.split('/')[-1]
            raise serverExceptions.InvalidRegistration
        sMod = hex(sMod)[2:]

        sFileWithoutExtension = re.search(PSP_REMOVE_EXTENSION, fileName).groups()[0]
        compiledFileName = sFileWithoutExtension + '#' + sMod + '.bin'
        
        try:
            pspBinaryFile = open(compiledFileName, 'rb')
        except IOError:
            # remove old compiled files
            import glob
            oldFiles = glob.glob(sFileWithoutExtension + '*.bin')
            for oldFile in oldFiles:
                os.remove(oldFile)
            # start compilation
            oFile = open(fileName, 'rU')
            pspCode = oFile.read()

            # truncate utf-8 file encoding identifier for NT            
            if pspCode[:3]==NT_UTF_8_IDENTIFIER:
                pspCode = pspCode[3:]
            
            execCode=''
            # see if is transactional
            oMatch = re.search(TRANS_REQUIRED, pspCode)
            if oMatch and bool(oMatch.group()):
                execCode += 'servlet.requiresTransaction = True\n'

            pspCode = re.split(PSP_TAGS, pspCode)
            intend = ''
            for codeFragment in pspCode:
                if codeFragment!='':
                    codeMatch = re.match(PSP_TAGS, codeFragment)
                    if codeMatch == None:
                        # pure HTML
                        # remove whitespaces
                        #codeFragment = codeFragment.strip() + '\n'
                        codeFragment = codeFragment.replace("'", "\\'")
                            
                        execCode += intend + 'response.write(\'\'\'%s\'\'\')\n' % codeFragment
                    else:
                        # pure Python
                        # remove PSP tags
                        codeFragment = codeFragment[2:len(codeFragment)-2]
                        linesOfCode = codeFragment.split('\n')
                        formattedCode = ''
                        for line in linesOfCode:
                            # remove whitespaces
                            line = line.strip()
                            # set intendation
                            if line!='':
                                if line!='end':
                                    if re.match(PSP_DECREASE_INDENT, line) != None:
                                        intend = intend[0:len(intend)-1]
                                    formattedCode += intend + line + '\n'
                                    if line[-1] == ':':
                                        intend += '\t'
                                else:
                                    intend = intend[0:len(intend)-1]
                        execCode += formattedCode

#            pspSourceFile = open(sFileWithoutExtension + '.py', 'w')
#            pspSourceFile.write(execCode)
#            pspSourceFile.close()

            oCode = compile(execCode, '<string>', 'exec')
            pspBinaryFile = open(compiledFileName, 'w+b')
            marshal.dump(oCode, pspBinaryFile)
            pspBinaryFile.seek(0)

        pspDir = {
            'server':self.server,
            'session':self.session,
            'response':self.response,
            'request':self.request,
            'item':self.item,
            'include':self.include,
            'servlet':self
        }
        oCode = marshal.load(pspBinaryFile)
        try:
            exec oCode in pspDir
        finally:
            pspBinaryFile.close()