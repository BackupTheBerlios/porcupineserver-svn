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
"""
Porcupine server post processing filters
"""

import os, os.path, glob, gzip, cStringIO

from porcupine.filters import PostProcessingFilter

class Gzip(PostProcessingFilter):
    cacheFolder = None
    staticLevel = 9
    dynamicLevel = 3
    
    def compress(zbuf, stream, level):
        zfile = gzip.GzipFile(mode='wb', fileobj = zbuf, compresslevel = level)
        zfile.write(stream)
        zfile.close()
    compress = staticmethod(compress)
    
    def apply(response, request, registration):
        if not Gzip.cacheFolder:
            config = Gzip.loadConfig()
            Gzip.cacheFolder = config['cache']
            Gzip.staticLevel = int(config['static_compress_level'])
            Gzip.dynamicLevel = int(config['dynamic_compress_level'])
        
        response.setHeader('Content-Encoding', 'gzip')    
        isStatic = (registration.type == 0)
                
        if isStatic:
            fileName = registration.context
            sMod = hex( os.stat(fileName)[8] )[2:]
            
            compfn = fileName.replace(os.path.sep, '_')
            if os.name == 'nt':
                compfn = compfn.replace(os.path.altsep, '_').replace(':', '')
            
            glob_f = Gzip.cacheFolder + '/' + compfn
            compfn = glob_f + '#' + sMod + '.gzip'

            if not(os.path.exists(compfn)):
                # remove old compressed files
                oldFiles = glob.glob(glob_f + '*.gzip')
                res = [os.remove(oldFile) for oldFile in oldFiles]

                zBuf = cStringIO.StringIO()
                Gzip.compress(zBuf, response._getBody(), Gzip.staticLevel)

                response._body = [zBuf.getvalue()]

                cache_file = file(compfn, 'wb')
                cache_file.write(zBuf.getvalue())
                
                zBuf.close()
                cache_file.close()
                
            else:
                cache_file = file(compfn, 'rb')
                response._body = [cache_file.read()]
                cache_file.close()
                
        else:
            zBuf = cStringIO.StringIO()
            Gzip.compress(zBuf, response._getBody(), Gzip.dynamicLevel)
            response._body = [zBuf.getvalue()]
            zBuf.close()
    apply = staticmethod(apply)