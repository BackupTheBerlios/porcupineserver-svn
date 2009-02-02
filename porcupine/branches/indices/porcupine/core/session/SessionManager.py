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
"Porcupine Server session manager singleton"

sm = None

def open(sm_type, session_timeout):
    global sm
    sm = sm_type(session_timeout)
    
def create(userid):
    # create new session
    new_session = sm.create_session(userid)
    return(new_session)
   
def fetch_session(sessionid):
    session = sm.get_session(sessionid)
    if session:
        # update last access time
        sm.revive_session(session)
    return(session)

def terminate_session(session):
    sm.remove_session(session.sessionid)
    session.remove_temp_files()
    
def close():
    sm.close()
