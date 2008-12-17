#!/usr/bin/env python
"""
Utility for installing and controlling Porcupine
as an NT service.
"""
import os
import sys
import time
import imp

try:
	os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
	pass
import win32serviceutil
import win32service

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

class PorcupineServerService(win32serviceutil.ServiceFramework):
	_svc_name_ = 'Porcupine'
	_svc_display_name_ = 'Porcupine Server'

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		sys.stdout = open('nul', 'w')
		sys.stderr = open('nul', 'w')
		self.controller = None

	def SvcDoRun(self):
		try:
			if '' not in sys.path:
				sys.path = [''] + sys.path
			if main_is_frozen():
				os.chdir( os.path.dirname(sys.executable) )
			from porcupineserver import Controller
			self.controller = Controller()
			self.controller.start()
			self.controller.shutdownEvt.wait()
		except Exception, e:
			print e
			if self.controller:
				self.controller.initiateShutdown()
			raise

	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		while self.controller is None:
			time.sleep(1.0)
		self.controller.initiateShutdown()
		while self.controller.shutdowninprogress:
			time.sleep(1.0)

if __name__=='__main__':
	win32serviceutil.HandleCommandLine(PorcupineServerService)
