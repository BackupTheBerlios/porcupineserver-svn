#===============================================================================
#    Copyright 2005-2008, Tassos Koutsovassilis
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
"Porcupine Server CGI Interface"

def cgi_handler(rh, response):
    # write headers
    for header, value in response._getHeaders().items():
        rh.write_buffer('%s: %s\n' % (header, value))

    sBody = response._getBody()
    if sBody:
        rh.write_buffer('Content-Length: %i\n' % len(sBody))
        
    if len(response.cookies) > 0:
        rh.write_buffer(response.cookies.output() + '\n')

    rh.write_buffer('\n')

    # write body
    rh.write_buffer(sBody)
