// Toggle de visibilidade de senha
(function () {
	function togglePasswordVisibility(buttonId) {
		var btn = document.getElementById(buttonId);
		if (!btn) return;
		btn.addEventListener('click', function () {
			var targetId = btn.getAttribute('data-target');
			var input = document.getElementById(targetId);
			if (!input) return;
			var isPassword = input.getAttribute('type') === 'password';
			input.setAttribute('type', isPassword ? 'text' : 'password');
			var icon = btn.querySelector('i');
			if (icon) {
				icon.classList.toggle('fa-eye');
				icon.classList.toggle('fa-eye-slash');
			}
		});
	}

	function passwordStrengthMeter(inputId, barId) {
		var input = document.getElementById(inputId);
		var bar = document.getElementById(barId);
		if (!input || !bar) return;
		function evaluateStrength(value) {
			var score = 0;
			if (!value) return 0;
			if (value.length >= 8) score += 25;
			if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 25;
			if (/\d/.test(value)) score += 25;
			if (/[^A-Za-z0-9]/.test(value)) score += 25;
			return Math.min(score, 100);
		}
		function updateBar() {
			var score = evaluateStrength(input.value);
			bar.style.width = score + '%';
			bar.setAttribute('aria-valuenow', String(score));
			bar.classList.remove('bg-danger', 'bg-warning', 'bg-success');
			if (score < 50) bar.classList.add('bg-danger');
			else if (score < 75) bar.classList.add('bg-warning');
			else bar.classList.add('bg-success');
		}
		input.addEventListener('input', updateBar);
		updateBar();
	}

	document.addEventListener('DOMContentLoaded', function () {
		togglePasswordVisibility('togglePassword');
		togglePasswordVisibility('togglePassword2');
		passwordStrengthMeter('password', 'passwordStrength');
	});
})();

