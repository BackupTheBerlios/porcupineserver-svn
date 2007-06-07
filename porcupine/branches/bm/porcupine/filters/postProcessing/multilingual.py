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
"""
Porcupine multi-lingual post processing filter
"""
import re

from porcupine.filters import PostProcessingFilter
from porcupine.utils import misc

TOKEN = re.compile('(@@([\w\.]+)@@)')

class Multilingual(PostProcessingFilter):
    @staticmethod
    def apply(response, request, registration, args):
        language = request.getLang()
        resources = misc.getCallableByName( args['using'] )
        output = response._getBody()
        tokens = frozenset(re.findall(TOKEN, output, re.DOTALL))
        for token, key in tokens:
            output = output.replace(token, resources.getResource(key, language))
        response._body = [output]
