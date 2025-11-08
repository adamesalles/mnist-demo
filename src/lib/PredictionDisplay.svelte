<script lang="ts">
	import { predictions } from './stores.js';
	
	// Function to get color based on probability (heatmap)
	function getHeatmapColor(probability: number): string {
		// Color scale: dark blue (0) -> cyan -> green -> yellow -> red (1)
		if (probability < 0.2) {
			// Dark blue to blue
			const intensity = Math.floor((probability / 0.2) * 100);
			return `hsl(240, 100%, ${20 + intensity * 0.3}%)`;
		} else if (probability < 0.4) {
			// Blue to cyan
			const t = (probability - 0.2) / 0.2;
			const hue = 240 - t * 60; // 240 to 180
			return `hsl(${hue}, 100%, 50%)`;
		} else if (probability < 0.6) {
			// Cyan to green
			const t = (probability - 0.4) / 0.2;
			const hue = 180 - t * 60; // 180 to 120
			return `hsl(${hue}, 100%, 45%)`;
		} else if (probability < 0.8) {
			// Green to yellow
			const t = (probability - 0.6) / 0.2;
			const hue = 120 - t * 60; // 120 to 60
			return `hsl(${hue}, 100%, 50%)`;
		} else {
			// Yellow to red
			const t = (probability - 0.8) / 0.2;
			const hue = 60 - t * 60; // 60 to 0
			return `hsl(${hue}, 100%, 50%)`;
		}
	}
	
	// Get the digit with highest probability
	$: maxPrediction = $predictions.reduce((max, pred) => 
		pred.probability > max.probability ? pred : max
	, $predictions[0]);
</script>

<div class="prediction-container">
	<h3>Predição em Tempo Real</h3>
	
	<div class="prediction-result">
		<span class="result-label">Dígito Identificado:</span>
		<span class="result-value" style="color: {getHeatmapColor(maxPrediction.probability)}">
			{maxPrediction.digit}
		</span>
		<span class="result-confidence">
			({(maxPrediction.probability * 100).toFixed(1)}%)
		</span>
	</div>
	
	<div class="probabilities-grid">
		{#each $predictions as pred}
			<div class="probability-item">
				<div class="digit-label">{pred.digit}</div>
				<div 
					class="probability-bar" 
					style="background-color: {getHeatmapColor(pred.probability)}; width: {pred.probability * 100}%"
				>
					<span class="probability-text">
						{(pred.probability * 100).toFixed(1)}%
					</span>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.prediction-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20px;
		width: 100%;
		max-width: 600px;
		margin: 0 auto;
		overflow-x: hidden;
	}
	
	h3 {
		margin: 0;
		font-size: 1.4rem;
		font-weight: 400;
		color: #2A5AB3;
	}
	
	.prediction-result {
		display: flex;
		align-items: center;
		gap: 12px;
		background: white;
		padding: 20px 30px;
		border-radius: 12px;
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
		font-size: 1.2rem;
		flex-wrap: wrap;
		justify-content: center;
		width: 100%;
		box-sizing: border-box;
	}
	
	.result-label {
		color: #555;
		font-weight: 400;
	}
	
	.result-value {
		font-size: 2.5rem;
		font-weight: 700;
		line-height: 1;
	}
	
	.result-confidence {
		color: #777;
		font-size: 1rem;
	}
	
	.probabilities-grid {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		gap: 12px;
		width: 100%;
		background: white;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
		box-sizing: border-box;
	}
	
	.probability-item {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	
	.digit-label {
		font-size: 1.2rem;
		font-weight: 600;
		color: #2A5AB3;
		min-width: 25px;
		text-align: center;
	}
	
	.probability-bar {
		flex: 1;
		height: 32px;
		border-radius: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.3s ease;
		min-width: 60px;
		position: relative;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}
	
	.probability-text {
		color: white;
		font-size: 0.85rem;
		font-weight: 600;
		/* text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3); */
	}
	
	@media (max-width: 768px) {
		h3 {
			font-size: 1.2rem;
		}

		.prediction-result {
			padding: 15px 20px;
			font-size: 1rem;
		}

		.result-value {
			font-size: 2rem;
		}

		.probabilities-grid {
			padding: 15px 10px;
			gap: 8px;
		}

		.probability-item {
			gap: 6px;
		}

		.digit-label {
			font-size: 0.9rem;
			min-width: 18px;
		}

		.probability-bar {
			height: 26px;
			min-width: 50px;
		}

		.probability-text {
			font-size: 0.7rem;
		}
	}

	@media (max-width: 480px) {
		.probabilities-grid {
			padding: 12px 8px;
			gap: 6px;
		}

		.probability-item {
			gap: 4px;
		}

		.digit-label {
			font-size: 0.85rem;
			min-width: 16px;
		}

		.probability-bar {
			height: 24px;
			min-width: 40px;
		}

		.probability-text {
			font-size: 0.65rem;
		}
	}
</style>