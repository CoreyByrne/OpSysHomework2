import json
import datetime
import random
import math

debug = False

class timeGetter:
	def __init__(self):
		self.steptime = 0
		self.dt = 1
		
	def getTime(self):
		return self.steptime
	
	def step(self):
		self.steptime += 1
			
time = timeGetter()		

class process:
	def __init__(self, processData, processId, mode):
		self.processId = processId
		self.core = -1
		self.schedulerMode = mode
		self.priority = math.floor(random.random()*5)
		self.waitTime = 0
		self.mode = None
		self._startTime = None
		self._waitTime = time.getTime()
		self._burstwaittime = 0
		self.arrived = False
		self.lastWaitTime = time.getTime()
		self.contextSwitch = None
		self.preempted = False
		#self.arrivalTime
		#self.burstCount
		#self.burstMin
		#self.burstMax
		#self.interactive
		#self.IOmin
		#self.IOmax
		#self.running
		
		if "interactive" not in processData:
			if debug:
				print processId, "was not labeled interactive, defaulting to false"
			processData["interactive"] = True if random.random() < .8 else False;
		self.interactive = processData["interactive"]
		
		if "arrivalTime" not in processData: 
			if debug:
				print processId, "does not have a arrivalTime, defaulting to 0"
			processData["arrivalTime"] = 0
		self.arrivalTime = processData["arrivalTime"]
		if self.arrivalTime == 0:
			self.arrived = True
	
		if "burstCount" not in processData:
			if debug:
				print processId, "does not have a burstCount, defaulting to 8"
			processData["burstCount"] = 8
		if "burstMax" not in processData:
			if debug:
				print processId, "does not have a burstMax, defaulting to 3000"
			processData["burstMax"] = 3000
			if self.interactive:
				processData["burstMax"] = 200
		if "burstMin" not in processData:
			if debug: 
				print processId, "does not have a burstMin, defaulting to 200"
			processData["burstMin"] = 200
			if self.interactive:
				processData["burstMin"] = 20
		self.burstCount = processData["burstCount"]
		self.burstMax = processData["burstMax"]
		self.burstMin = processData["burstMin"]
	
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
	
		self.running = not self.interactive
		if "IOmax" not in processData:
			if debug: 
				print processId, "was labeled as interactive, but has no IOmax, defaulting to 3200"
			processData["IOmax"] = 3200
			if self.interactive:
				processData["IOmax"] = 4500
		if "IOmin" not in processData:
			if debug:
				print processId, "was labeled as interactive, but has no IOmin, defaulting to 100"
			processData["IOmin"] = 1200
			if self.interactive:
				processData["IOmin"] = 1000
		self.IOmax = processData["IOmax"]
		self.IOmin = processData["IOmin"]
		
		if self.arrived:
			print "[time 0ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time" + (")" if self.schedulerMode != 3 is None else "; priority " + str(self.priority) + ")")
			
	def isInteractive(self):
		return self.interactive
	
	def IOwait(self):
		self._startTime = time.getTime()
		self.burst = math.floor(self.IOmin + (self.IOmax - self.IOmin) * random.random())
		self.mode = False
			
	def IOstop(self):
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
		self._waitTime = time.getTime()
		self._startTime = None
		self.mode = None
		print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time" + (")" if self.schedulerMode != 3 is None else "; priority " + str(self.priority) + ")")
					
	def canIOstop(self):
		return self.mode is False and time.getTime() - self.burst > self._startTime
	
	def start(self):
		self._startTime = time.getTime()
		if self._waitTime is not None: # protect against initial condition
			self.waitTime += self._startTime - self._waitTime 
			self._burstwaittime += self._startTime - self._waitTime
		self.mode = True
		if self.contextSwitch is None:
			print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "starting on core", self.core + 1
				
	def preempt(self):
		self.contextSwitch = time.getTime()
		self._startTime = None
		self._waitTime = time.getTime()
		self.mode = None
		self.preempted = True
	
	def contextSwitching(self):
		self.contextSwitch = time.getTime()
	
	def stop(self):
		print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "finished", "(turnaround time", str(time.getTime() - self._startTime) + "ms, wait time", str(self._burstwaittime) + "ms)"
		self._burstwaittime = 0
		self._startTime = None
		self.mode = None
		self.burstCount -= 1
		self.burst = math.floor(self.burstMin + (self.burstMax - self.burstMin) * random.random())
		if self.burstCount is 0:
			self.running = False
		
	def runningTime(self):
		return time.getTime() - self._startTime
	
	def waitingTime(self):
		if self.lastWaitTime > self._waitTime:
			return time.getTime() - self.lastWaitTime > 1200
		else:
			return time.getTime() - self._waitTime > 1200
	
	def waitIncremented(self):
		self.lastWaitTime = time.getTime()
		self.priority -= 1
		print "[time " + str(time.getTime()) + "ms]", "Increased priority of", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "to", self.priority, "due to aging"
	
	def step(self):
		if self.contextSwitch is not None and time.getTime() - self.contextSwitch >= 1:
			self.contextSwitch = None
			self._startTime = time.getTime()
			print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "starting on core", self.core + 1
		elif self.preempted:
			self.preempted = False
			self._startTime = time.getTime()
		elif self.mode is not None:
			self.burst -= time.dt
			
	def isRunning(self):
		return (self.running or self.interactive)
	
	def isWaiting(self):
		if not self.arrived and time.getTime() > self.arrivalTime:
			self.arrived = True
			self._waitTime = time.getTime()
			print "[time " + str(time.getTime()) + "ms]", ("Interactive" if self.interactive else "CPU-bound"), "process ID", self.processId, "entered ready queue", "(requires", str(self.burst) + "ms CPU time" + (")" if self.schedulerMode != 3 is None else "; priority " + str(self.priority) + ")")
			return True
		return self._startTime is None and self.arrived and self.isRunning()
	
	def isBursting(self):
		return self._startTime is not None and self.mode
		
	def canStop(self):
		if self.contextSwitch is not None and time.getTime() - self.contextSwitch >= 1 and self.mode is None:
			self.contextSwitch = None
			self._waitTime = time.getTime()
		return self.isBursting() and self.burst <= 0
		
	def timeLeft(self):    # note, only can be called is canStart is false
		return self.burst
	 
	
class scheduler:
	def __init__(self, scheduleData):
		self.jobs = []
		self.freeCores = []
		if "mode" not in scheduleData:
			if debug:
				print "Mode not listed in data, defaulting to 0 (SJF non-preemtive)"
			scheduleData["mode"] = 0
		self.mode = scheduleData["mode"]
		print self.mode
		if "cores" not in scheduleData:
			if debug:
				print "Cores not listed in data, defauling to 4 cores"
			scheduleData["cores"] = 4
		self.cores = scheduleData["cores"]
		self.freeCores = range(self.cores)
		if self.mode == 2:
			if "timeSlice" not in scheduleData:
				if debug:
					print "TimeSlice not listed in data, defaulting to 100ms"
				scheduleData["timeSlice"] = 100
			self.timeSlice = scheduleData["timeSlice"]
		self.processes = []
		if "processes" not in scheduleData:
			if debug:
				print "No processes supplied, making 5 defaults"
			for i in range(5):
				self.processes.append(process({}, i, self.mode))
		else:
			for i in range(len(scheduleData["processes"])):
				self.processes.append(process(scheduleData["processes"][i], i, self.mode))
		
		self.main()
		
	def main(self):
		finished = False
		if self.mode is 3: # Aging
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						process.priority = math.floor(random.random()*5) # give it a new priority (wont be used until it reenters the queue)
						if process.isRunning():
							process.IOwait()			# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif debug:
						print process.burst, "time remaining on process", process.processId
						
						
				for process in self.processes:
					if process.isWaiting() and process.waitingTime():
						process.waitIncremented()
					elif process.canIOstop():
						process.IOstop()
				
				all = []
				
				for process in self.processes:
					if not process.isBursting() and not process.isWaiting():
						continue
					i = 0								# start at 0
					#ordered insertion
					while True:							# loop up
						if i >= len(all):				# if were at the end
							all.append(process)			# insert and break
							break
						if debug:
							print "loop", i, "checking priority", process.priority, "against", all[i].priority
						if process.priority < all[i].priority: # if were greater then the one were looking at
							all.insert(i, process) #insert us infront of it
							break
						i+=1
				
				freed = []
				
				for i in range(len(all)):					# add all the new free cores
					if all[i] in self.jobs and i >= self.cores: # for processes that no longer quailify 
						freed.append(all[i].processId)
						all[i].preempt()					# preempt the process
						self.jobs.remove(all[i])
						self.freeCores.append(all[i].core)	# add the core we just freed	
							
				for process in all:
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if debug:
						print "process", process.processId, "being added"
					if process in self.jobs:
						continue
					if(len(freed) != 0):
						print "[time " + str(time.getTime()) + "ms]", "Context switch", "(swapping out process ID", freed.pop(0), "for process ID", str(process.processId) + ")"
						process.contextSwitching()
					self.jobs.append(process)			# and add it to the job list
					process.core = self.freeCores.pop(0)# add it to a free core
					process.start()						# otherwise start this job
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
		if self.mode is 2: # RR
			tempTime = self.timeSlice							# ready a list of ready job
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				freed = []
				queue = []
				ready = []	
				
				for process in self.processes:
					if process.isWaiting():
						ready.append(process)
					elif process.canIOstop():
						process.IOstop()
						ready.append(process)	
				
				for process in self.jobs:
					process.step()						# step the job
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						if process.isRunning():
							process.IOwait()				# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif process.runningTime() >= tempTime and len(ready) > 0:
						freed.append(process.processId)
						process.preempt()					# preempt the process
						self.jobs.remove(process)
						self.freeCores.append(process.core) # add the core we just freed					
						queue.append(ready.pop(0))
					elif debug:
						print process.burst, "time remaining on process", process.processId
				
				i = 0
				while len(queue) + len(self.jobs) < self.cores:
					process = self.processes[i]
					if process not in queue and process not in self.jobs:
						queue.append(process)
					i+=1
					if i == len(self.processes):
						break
						
				if len(queue) == 0:						# if we have an empty queue
					continue							# stop this loop
					
				for process in queue:
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if debug:
						print "process", process.processId, "being added"
					if process in self.jobs:
						continue 
					if(len(freed) != 0):
						print "[time " + str(time.getTime()) + "ms]", "Context switch", "(swapping out process ID", freed.pop(0), "for process ID", str(process.processId) + ")"
						process.contextSwitching()
					self.jobs.append(process)			# and add it to the job list
					process.core = self.freeCores.pop(0)# add it to a free core
					process.start()						# otherwise start this job
				
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
			
		if self.mode is 0: # SJF non-preemptive
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						if process.isRunning():
							process.IOwait()			# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif debug:
						print process.burst, "time remaining on process", process.processId
				for process in self.processes:
					if process.canIOstop():
						process.IOstop()
				if len(self.jobs) == self.cores:		# if we have a full queue
					continue							# stop this loop
				'''
				new jobs
				'''
				ready = []								# ready a list of ready job
				for process in self.processes:
					if process.isWaiting():				# if the job can start
						if debug:						
							print "process", process.processId, "ready to begin"
						i = 0							# start at 0
						#ordered insertion
						while True:						# loop up
							if i >= len(ready):			# if were at the end
								ready.append(process)	# insert and break
								break
							if debug:
								print "loop", i, "checking burst", process.burst, "against", ready[i].burst
							if process.burst < ready[i].burst: # if were less then the one were looking at
								ready.insert(i, process) #insert us infront of it
								break
							i+=1
				for process in ready:
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if debug:
						print "process", process.processId, "being added"
					self.jobs.append(process)			# and add it to the job list
					process.core = self.freeCores.pop(0)# add it to a free core
					process.start()						# otherwise start this job
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
		if self.mode is 1: # SJF preemptive
			while not finished:
				time.step()
				if debug:
					print "starting step," , len(self.jobs) , "jobs"
				'''
				current jobs
				'''
				for process in self.jobs:
					process.step()						# step the job
					
					if process.canStop(): 				# job can stop
						if debug:
							print "stopping process", process.processId
						process.stop()    				# stop the job
						if process.isRunning():
							process.IOwait()				# start IO
						self.jobs.remove(process)		# remove process from jobs
						self.freeCores.append(process.core) # add free core
					elif debug:
						print process.burst, "time remaining on process", process.processId
				for process in self.processes:
					if process.canIOstop():
						process.IOstop()
				'''
				new jobs
				'''	
				
				all = []								# ready a list of all jobs
				for process in self.processes:
					if not process.isBursting() and not process.isWaiting():
						continue
					i = 0								# start at 0
					#ordered insertion
					while True:							# loop up
						if i >= len(all):				# if were at the end
							all.append(process)			# insert and break
							break
						if debug:
							print "loop", i, "checking burst", process.burst, "against", all[i].burst
						if process.burst < all[i].burst: # if were less then the one were looking at
							all.insert(i, process) #insert us infront of it
							break
						i+=1
				freed = []
				for i in range(len(all)):					# add all the new free cores
					if all[i] in self.jobs and i >= self.cores: # for processes that no longer quailify 
						freed.append(all[i].processId)		# log the freed ID for a later print statement
						all[i].preempt()					# preempt the process
						self.jobs.remove(all[i])			# remove from running list
						self.freeCores.append(all[i].core) 	# add the core we just freed	
						
				for process in all:
					if len(self.jobs) == self.cores:	# when we've filled up the queue
						break							# stop
					if process in self.jobs:			# if this job is already running
						continue						# continue
					if debug:
						print "process", process.processId, "being added"
					if(len(freed) != 0):
						print "[time " + str(time.getTime()) + "ms]", "Context switch", "(swapping out process ID", freed.pop(0), "for process ID", str(process.processId) + ")"
						process.contextSwitching()
					self.jobs.append(process)			# and add it to the job list
					process.core = self.freeCores.pop(0)# add it to a free core
					process.start()						# otherwise start this job
				'''
				check for end condition
				'''
				finished = True							# assume were done
				for process in self.processes:			# for each process
					finished = finished and not process.running # ask if they're done
		
s = scheduler({
	"mode": 2,
	"cores": 4,
	"timeSlice": 100,
	"processes": [
		{
			"arrivalTime": 0,
			"interactive": True,
			"burstCount": 8,
			"burstMax": 3000,
			"burstMin": 200,
			"IOmin": 1200,
			"IOmax": 3200
		},
		{
			"arrivalTime": 400,
			"interactive": True,
			"burstCount": 5,
			"burstMax": 3000,
			"burstMin": 200,
			"IOmin": 1200,
			"IOmax": 3200
		},
		{
			"arrivalTime": 600,
			"interactive": True,
			"burstCount": 4,
			"burstMax": 3000,
			"burstMin": 200,
			"IOmin": 1200,
			"IOmax": 3200
		},
		{
			"arrivalTime": 1000,
			"interactive": True,
			"burstCount": 1,
			"burstMax": 3000,
			"burstMin": 200,
			"IOmin": 1200,
			"IOmax": 3200
		},
		{
			"arrivalTime": 5000,
			"interactive": False,
			"burstCount": 8,
			"burstMax": 3000,
			"burstMin": 200,
			"IOmin": 1200,
			"IOmax": 3200
		}
	]
})
