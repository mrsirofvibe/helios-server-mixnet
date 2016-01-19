#!/usr/bin/env python
#    Copyright © 2016 RunasSudo (Yingtong Li)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# I love the smell of Python 3 in the morning

import utils
import itertools, json, sys

electionIn = sys.argv[1]
resultIn = sys.argv[2]
question = int(sys.argv[3])
numSeats = int(sys.argv[4])

class Ballot:
	def __init__(self, gamma, candidates):
		self.gamma = gamma
		self.preferences = utils.gamma_decode(gamma, candidates)
		self.value = 1

class Candidate:
	def __init__(self, name):
		self.name = name
		self.ctvv = 0
		self.ballots = []

with open(electionIn, 'r') as electionFile:
	election = json.load(electionFile)
	
	candidates = []
	for candidate in election["questions"][question]["answers"]:
		candidates.append(Candidate(candidate))
	
	with open(resultIn, 'r') as resultFile:
		results = json.load(resultFile)
		
		ballots = []
		for result in results[question]:
			ballots.append(Ballot(result, len(candidates)))

def distributePreferences(ballots, candidates, remainingCandidates):
	for ballot in ballots:
		ballot.value = 1
	for candidate in candidates:
		candidate.ctvv = 0
		candidate.ballots.clear()
	exhausted = 0
	
	for ballot in ballots:
		isExhausted = True
		for preference in ballot.preferences:
			if preference in remainingCandidates:
				candidates[preference].ctvv += ballot.value
				candidates[preference].ballots.append(ballot)
				isExhausted = False
				break
		if isExhausted:
			exhausted += ballot.value
			ballot.value = 0
	
	return exhausted

def totalVote(candidates):
	tv = 0
	for candidate in candidates:
		tv += candidate.ctvv
	return tv

# Return the candidate index to transfer votes to
def surplusTransfer(preferences, fromCandidate, candidates, provisionallyElected, remainingCandidates):
	beginPreference = preferences.index(fromCandidate)
	for index in range(beginPreference + 1, len(preferences)):
		preference = preferences[index]
		if preference in remainingCandidates and candidates[preference] not in provisionallyElected:
			return preference
	return False

def printVotes(candidates, provisionallyElected, remainingCandidates):
	print()
	for candidate in remainingCandidates:
		print("    {}{}: {}".format("*" if candidates[candidate] in provisionallyElected else " ", candidates[candidate].name, candidates[candidate].ctvv))
	print()

def countVotes(ballots, candidates):
	count = 1
	remainingCandidates = list(range(0, len(candidates)))
	while True:
		print()
		print("== COUNT {}".format(count))
		exhausted = 0
		provisionallyElected = []
		
		exhausted += distributePreferences(ballots, candidates, remainingCandidates)
		
		printVotes(candidates, provisionallyElected, remainingCandidates)
		
		quota = totalVote(candidates) / (numSeats + 1)
		print("---- Exhausted: {}".format(exhausted))
		print("---- Quota: {}".format(quota))
		
		for candidate in remainingCandidates:
			if candidates[candidate].ctvv > quota:
				print("**** {} provisionally elected".format(candidates[candidate].name))
				provisionallyElected.append(candidates[candidate])
		
		if len(provisionallyElected) == numSeats:
			return provisionallyElected
		
		mostVotesElected = sorted(provisionallyElected, key=lambda k: k.ctvv, reverse=True)
		
		# While surpluses remain
		while mostVotesElected and mostVotesElected[0].ctvv > quota:
			for candidate in mostVotesElected:
				if candidate.ctvv > quota:
					multiplier = (candidate.ctvv - quota) / candidate.ctvv
					
					for key, group in itertools.groupby(sorted(candidate.ballots, key=lambda k: k.gamma), lambda k: k.gamma):
						transferTo = surplusTransfer(utils.gamma_decode(key, len(candidates)), candidates.index(candidate), candidates, provisionallyElected, remainingCandidates)
						if transferTo == False:
							for ballot in group:
								exhausted += ballot.value
						else:
							transferred = 0
							for ballot in group:
								transferred += ballot.value
								ballot.value *= multiplier
								candidates[transferTo].ctvv += ballot.value
								candidates[transferTo].ballots.append(ballot)
							print("---- Transferred {} votes from {} to {} at value {} via {}".format(transferred, candidate.name, candidates[transferTo].name, multiplier, key))
					
					candidate.ctvv = quota
					
					printVotes(candidates, provisionallyElected, remainingCandidates)
					
					for candidate in remainingCandidates:
						if candidates[candidate].ctvv > quota:
							print("**** {} provisionally elected".format(candidates[candidate].name))
							provisionallyElected.append(candidates[candidate])
					
					if len(provisionallyElected) == numSeats:
						return provisionallyElected
			mostVotesElected = sorted(provisionallyElected, key=lambda k: k.ctvv, reverse=True)
		
		remainingCandidates.sort(key=lambda k: candidates[k].ctvv)
		
		# Check for a tie
		if len(remainingCandidates) > 1:
			if "{:.2f}".format(candidates[remainingCandidates[0]].ctvv) == "{:.2f}".format(candidates[remainingCandidates[1]].ctvv):
				raise Exception("Draw for fewest votes. Manual intervention required.")
		
		print("---- Excluding {}".format(candidates[remainingCandidates[0]].name))
		remainingCandidates.pop(0)
		
		if len(remainingCandidates) == numSeats:
			for candidate in remainingCandidates:
				if candidates[candidate] not in provisionallyElected:
					print("**** {} provisionally elected".format(candidates[candidate].name))
					provisionallyElected.append(candidates[candidate])
			return provisionallyElected
		
		count += 1

provisionallyElected = countVotes(ballots, candidates)
print()
print("== TALLY COMPLETE")
print()
print("The winners are, in order of election:")
for candidate in provisionallyElected:
	print("-- {}".format(candidate.name))