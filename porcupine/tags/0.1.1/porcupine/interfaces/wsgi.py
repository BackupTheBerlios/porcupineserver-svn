#===============================================================================
#    Copyright 2005-2007, Tassos Koutsovassilis
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
"Porcupine WSGI interface"

from cPickle import dumps

def interfaceHandler(rh, response):
#    print response._getBody()
    rh.write_buffer(response._getBody())
    rh.write_buffer('\n\n---END BODY---\n\n')
    rh.write_buffer(dumps(response._getHeaders()))
    if len(response.cookies) > 0:
        cookies = []
        rh.write_buffer('\n\n---END BODY---\n\n')
        for cookie_name in response.cookies:
            cookies.append( response.cookies[cookie_name].OutputString() )
        rh.write_buffer( dumps(cookies) )
        
