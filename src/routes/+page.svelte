<script lang="ts">
	import { onMount } from 'svelte';
	import DrawableCanvas from '$lib/DrawableCanvas.svelte';
	import PredictionDisplay from '$lib/PredictionDisplay.svelte';
	import { predictions, isModelLoaded } from '$lib/stores.js';
	import { loadModel, predict, isModelReady } from '$lib/mnistModel.js';
	
	let loading = true;
	let error = '';
	
	onMount(async () => {
		try {
			await loadModel();
			isModelLoaded.set(true);
			loading = false;
		} catch (e) {
			error = 'Falha ao carregar o modelo. Por favor, recarregue a página.';
			loading = false;
			console.error('Error loading model:', e);
		}
	});
	
	async function handleDraw(imageData: ImageData) {
		if (!isModelReady()) return;

		try {
			const probabilities = await predict(imageData);

			predictions.set(
				probabilities.map((prob, index) => ({
					digit: index,
					probability: prob
				}))
			);
		} catch (e) {
			console.error('Prediction error:', e);
		}
	}

	function handleClear() {
		// Reset predictions to all zeros
		predictions.set(
			Array.from({ length: 10 }, (_, i) => ({
				digit: i,
				probability: 0
			}))
		);
	}
</script>

<svelte:head>
	<title>Classificador de Dígitos MNIST</title>
	<meta name="description" content="Reconhecimento de dígitos manuscritos em tempo real usando redes neurais" />
</svelte:head>

<main>
	<div class="container">
		<header>
			<h1>Classificador de Dígitos</h1>
			<p class="subtitle">Reconhecimento de dígitos manuscritos usando redes neurais</p>
		</header>
		
		{#if loading}
			<div class="loading-container">
				<div class="spinner"></div>
				<p>Carregando modelo neural...</p>
			</div>
		{:else if error}
			<div class="error-container">
				<p class="error-message">{error}</p>
			</div>
		{:else}
			<div class="main-layout">
				<div class="content">
					<DrawableCanvas onDraw={handleDraw} onClear={handleClear} />
					<PredictionDisplay />
				</div>

				<div class="sidebar">
					<div class="info-section">
						<h3>Como usar:</h3>
						<ol>
							<li>Desenhe um dígito de 0 a 9 no quadro preto</li>
							<li>A rede neural irá classificar seu desenho em tempo real</li>
							<li>Observe as probabilidades de cada dígito</li>
							<li>Clique em "Limpar" para desenhar novamente</li>
						</ol>
					</div>

					<div class="footer-card">
						<p>
							Desenvolvido por Eduardo Adame @eduadame<br>@matematicaeparatodos<br>FGV EMAp
						</p>
						<p class="dataset-reference">
							Rede neural treinada por nós utilizando o dataset MNIST (LeCun et al., 1998)
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</main>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		background: #f5f5f5;
		color: #333;
		min-height: 100vh;
	}
	
	main {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		padding: 20px;
		box-sizing: border-box;
	}
	
	.container {
		max-width: 1400px;
		margin: 0 auto;
		flex: 1;
		width: 100%;
	}

	.main-layout {
		display: flex;
		gap: 30px;
		align-items: flex-start;
		justify-content: center;
	}

	.sidebar {
		display: flex;
		flex-direction: column;
		gap: 20px;
		width: 300px;
		flex-shrink: 0;
	}
	
	header {
		text-align: center;
		margin-bottom: 40px;
		color: #2A5AB3;
	}
	
	h1 {
		margin: 0 0 10px 0;
		font-size: 2.5rem;
		font-weight: 600;
		text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}
	
	.subtitle {
		margin: 0;
		font-size: 1.1rem;
		opacity: 0.95;
		font-weight: 300;
	}
	
	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		gap: 20px;
		color: #2A5AB3;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid #BBBBBB;
		border-top-color: #2A5AB3;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.loading-container p {
		font-size: 1.2rem;
		margin: 0;
	}
	
	.error-container {
		background: white;
		padding: 30px;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		text-align: center;
	}
	
	.error-message {
		color: #e74c3c;
		font-size: 1.1rem;
		margin: 0;
	}
	
	.content {
		display: flex;
		flex-direction: column;
		gap: 40px;
		background: rgba(255, 255, 255, 0.95);
		padding: 40px;
		border-radius: 16px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
		flex: 1;
		max-width: 700px;
	}
	
	.info-section {
		background: rgba(255, 255, 255, 0.95);
		padding: 25px 35px;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}
	
	.info-section h3 {
		margin: 0 0 15px 0;
		color: #2A5AB3;
		font-weight: 500;
	}
	
	.info-section ol {
		margin: 0;
		padding-left: 20px;
		color: #555;
		line-height: 1.8;
	}
	
	.info-section li {
		margin-bottom: 8px;
	}

	.footer-card {
		background: #2A5AB3;
		color: white;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		text-align: center;
	}

	.footer-card p {
		margin: 0;
		font-size: 0.85rem;
		line-height: 1.5;
	}

	.footer-card .dataset-reference {
		margin-top: 12px;
		padding-top: 12px;
		border-top: 1px solid rgba(255, 255, 255, 0.3);
		font-size: 0.75rem;
		opacity: 0.9;
	}
	
	@media (max-width: 1100px) {
		.main-layout {
			flex-direction: column;
			align-items: center;
		}

		.content {
			max-width: 100%;
		}

		.sidebar {
			width: 100%;
			max-width: 700px;
		}
	}

	@media (max-width: 768px) {
		main {
			padding: 15px;
		}

		h1 {
			font-size: 1.8rem;
		}

		.subtitle {
			font-size: 0.95rem;
		}

		.content {
			padding: 25px 20px;
			gap: 30px;
		}

		.info-section {
			padding: 20px 25px;
		}

		.footer-card {
			padding: 15px;
		}

		.footer-card p {
			font-size: 0.75rem;
		}
	}
</style>