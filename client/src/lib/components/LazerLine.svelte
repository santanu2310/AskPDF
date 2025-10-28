<div class="text-center">
	<h1 class="text-4xl font-bold text-white mb-4">Converting Document To Vectors</h1>
	<p class="text-base text-gray-400 mb-12">Generally takes 15 to 20 secounds</p>
	<div
		class="
            laser-line
            h-2
            w-full
            max-w-4xl
            rounded-full
            shadow-xl
            shadow-cyan-500/40
            transition-shadow
            border border-cyan-700/50
        "
	></div>
</div>

<style>
	@keyframes laser-flow {
		0% {
			background-position: 100% 0;
		}
		100% {
			background-position: 0% 0;
		}
	}

	.laser-line {
		background: linear-gradient(
			to right,
			#1e293b 0%,
			/* Dark Slate */ #1e293b 5%,
			#38bdf8 25%,
			/* Light Blue Glow */ #00ffff 30%,
			/* Pure Cyan Peak */ #38bdf8 35%,
			/* Light Blue Glow */ #1e293b 60%,
			#1e293b 100%
		);
		background-size: 400% 100%;
		animation: laser-flow 3s linear infinite;
		user-select: none;
		background-color: #1e293b;
	}
</style>
