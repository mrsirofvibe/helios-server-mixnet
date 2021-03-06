//    Copyright © 2016 RunasSudo (Yingtong Li)
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.

function _onStart(evt) {
	if (evt.item.classList.contains("gvt")) {
		// Prevent moving GVTs to second level
		var preferencesList = document.querySelectorAll(".gvt-preferences");
		for (var i = 0; i < preferencesList.length; i++) {
			preferencesList[i].sortable.options.group.put = false;
		}
	} else {
		var preferencesList = document.querySelectorAll(".gvt-preferences");
		for (var i = 0; i < preferencesList.length; i++) {
			preferencesList[i].sortable.options.group.put = true;
		}
	}
}

function _onAdd(evt) {
	// Trying to add something to a GVT
	if (evt.to.classList.contains("gvt-preferences")) {
		if (!evt.item.dataset.gvt || evt.item.dataset.gvt !== evt.to.parentNode.dataset.name) {
			// Break up the GVT
			var preferences = evt.to.querySelectorAll(".preference");
			for (var i = 0; i < preferences.length; i++) {
				var preference = preferences[i];
				
				// Add the GVT name to the candidate's name
				if (preference.dataset.gvt)
					preference.textContent = preference.dataset.index + " - " + preference.dataset.name + " (" + preference.dataset.gvt + ")";
				
				evt.to.parentNode.parentNode.insertBefore(preference, evt.to.parentNode);
			}
			evt.to.parentNode.parentNode.removeChild(evt.to.parentNode);
		} else {
			// Remove the GVT name when adding back
			evt.item.textContent = evt.item.dataset.index + " - " + evt.item.dataset.name;
		}
	}
}

function _onRemove(evt) {
	if (evt.from.classList.contains("gvt-preferences")) {
		if (evt.item.dataset.gvt)
			evt.item.textContent = evt.item.dataset.index + " - " + evt.item.dataset.name + " (" + evt.item.dataset.gvt + ")";
		
		if (evt.from.children.length === 0) {
			// No more preferences in GVT
			evt.from.parentNode.parentNode.removeChild(evt.from.parentNode);
		}
	}
}

function updateAnswerBox(evt) {
	var answerBox = document.getElementById("stv_answer");
	answerBox.value = "";
	var choices = document.getElementById("stv_choices_selected").querySelectorAll(".preference");
	for (var i = 0; i < choices.length; i++) {
		if (answerBox.value !== "")
			answerBox.value += ",";
		answerBox.value += choices[i].dataset.index;
	}
}

function initAnswers(questionnum) {
	if (BOOTH.stv_store && BOOTH.stv_store[questionnum]) {
		// Try to restore answers
		var stv_choices = document.getElementById("stv_choices");
		stv_choices.parentNode.replaceChild(BOOTH.stv_store[questionnum], stv_choices);
	} else {
		// No saved answers. Rebuild answers from scratch
		var answers = [];
		
		for (var i = 0; i < BOOTH.election.questions[questionnum]["answers"].length; i++) {
			// Record each candidate
			var bits = BOOTH.election.questions[questionnum]["answers"][i].split("/");
			
			var candidate = {};
			candidate.type = "candidate";
			candidate.name = bits[0];
			candidate.index = i;
			
			if (bits.length >= 3) {
				var gvt = answers.find(function(e, index, a) {
					return e.type === "gvt" && e.name === bits[1];
				});
				if (!gvt) {
					gvt = {};
					gvt.type = "gvt";
					gvt.name = bits[1];
					gvt.candidates = [];
					answers.push(gvt);
				}
				
				candidate.gvtorder = parseFloat(bits[2]);
				candidate.gvt = gvt;
				
				gvt.candidates.push(candidate);
			} else {
				answers.push(candidate);
			}
		}
		
		// Randomise answers if requested
		if (BOOTH.election_metadata && BOOTH.election_metadata.randomize_answer_order) {
			shuffleArray(answers);
		}
		
		for (var answer of answers) {
			if (answer.type === "gvt") {
				var gvtLi = document.createElement("li");
				gvtLi.className = "gvt";
				
				gvtLi.dataset.name = answer.name;
				
				var gvtName = document.createElement("div");
				gvtName.textContent = answer.name;
				gvtName.className = "gvt-name";
				gvtLi.appendChild(gvtName);
				
				var gvtUl = document.createElement("ul");
				gvtUl.className = "gvt-preferences";
				gvtLi.appendChild(gvtUl);
				
				answer.candidates.sort(function(a, b) {
					return b.gvtoder - a.gvtorder;
				});
				
				for (var i = 0; i < answer.candidates.length; i++) {
					var candidate = answer.candidates[i];
					
					var answerLi = document.createElement("li");
					answerLi.textContent = (candidate.index + 1) + " - " + candidate.name;
					answerLi.className = "preference";
					answerLi.dataset.index = candidate.index + 1;
					
					answerLi.dataset.name = candidate.name;
					answerLi.dataset.gvt = answer.name;
					
					gvtUl.appendChild(answerLi);
				}
				
				document.getElementById("stv_choices_available").appendChild(gvtLi);
			} else {
				var answerLi = document.createElement("li");
				answerLi.textContent = (answer.index + 1) + " - " + answer.name;
				answerLi.className = "preference";
				answerLi.dataset.index = answer.index + 1;
				
				answerLi.dataset.name = candidate.name;
				
				document.getElementById("stv_choices_available").appendChild(answerLi);
			}
		}
	}
	
	// Setup Sortable
	var stvs = document.querySelectorAll(".stv-toplevel, .gvt-preferences");
	for (var i = 0; i < stvs.length; i++) { // for..of on NodeList's is not portable
		stvs[i].sortable = Sortable.create(stvs[i], {
			group: {name: "stv_choices"},
			onStart: _onStart,
			onAdd: _onAdd,
			onRemove: _onRemove,
			onSort: updateAnswerBox
		});
	}
}
