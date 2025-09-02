// Pokazuj box pobierania podczas kliknięcia przycisku pobierania na stronie Wynik
document.addEventListener('DOMContentLoaded', function() {
	var downloadBtn = document.getElementById('downloadBtn');
	var downloadBox = document.getElementById('downloadBox');
	if(downloadBtn && downloadBox) {
		downloadBtn.addEventListener('click', function(e) {
			downloadBox.style.display = 'block';
			setTimeout(function(){ downloadBox.style.display = 'none'; }, 2500);
		});
	}
	// Statystyki na stronie Wynik
	var statsPunkty = document.getElementById('statsPunkty');
	var statsData = document.getElementById('statsData');
	if(statsPunkty) {
		fetch('/czasy_scenariusze.csv').then(r => r.text()).then(txt => {
			var lines = txt.split('\n').filter(l => l.trim().length > 0);
			// Pomijamy nagłówek, liczymy unikalne indeksy punktów
			var punkty = new Set();
			for(var i=1;i<lines.length;i++){
				var cols = lines[i].split(',');
				if(cols.length>1) punkty.add(cols[1]);
			}
			statsPunkty.textContent = punkty.size;
		});
	}
	if(statsData) {
		var d = new Date();
		statsData.textContent = d.toLocaleString();
	}
});
// Please see documentation at https://learn.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

// Pokazuj box przetwarzania podczas submitu formularza
document.addEventListener('DOMContentLoaded', function() {
	var form = document.querySelector('form');
	var box = document.getElementById('processingBox');
	if(form && box) {
		form.addEventListener('submit', function(e) {
			var activeBtn = document.activeElement;
			if(activeBtn && activeBtn.id === 'workflowBtn') {
				box.style.display = 'block';
			}
		});
	}
});
