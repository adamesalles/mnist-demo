<script lang="ts">
	import { onMount } from 'svelte';
	import { isDrawing } from './stores.js';

	export let onDraw: (imageData: ImageData) => void;
	export let onClear: () => void;
	
	let canvas: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D;
	let drawing = false;
	let hasDrawn = false; // Track if user has drawn anything
	let lastX = 0;
	let lastY = 0;

	const canvasSize = 280; // Display size (10x the actual 28x28)
	const brushSize = 20;
	
	onMount(() => {
		const context = canvas.getContext('2d');
		if (!context) return;
		
		ctx = context;
		clearCanvas();
	});
	
	function clearCanvas() {
		if (!ctx) return;

		// Fill with black
		ctx.fillStyle = '#000000';
		ctx.fillRect(0, 0, canvasSize, canvasSize);

		// Reset drawing state
		hasDrawn = false;

		// Reset predictions without sending to model
		onClear();
	}
	
	function startDrawing(e: MouseEvent | TouchEvent) {
		drawing = true;
		hasDrawn = true; // Mark that user has drawn something
		isDrawing.set(true);

		const rect = canvas.getBoundingClientRect();
		const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
		const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

		lastX = (clientX - rect.left) * (canvasSize / rect.width);
		lastY = (clientY - rect.top) * (canvasSize / rect.height);

		// Draw a dot at the start position
		draw(lastX, lastY);
	}
	
	function stopDrawing() {
		if (drawing) {
			drawing = false;
			isDrawing.set(false);

			// Only trigger prediction if user has drawn something
			if (hasDrawn) {
				const imageData = ctx.getImageData(0, 0, canvasSize, canvasSize);
				onDraw(imageData);
			}
		}
	}
	
	function onMouseMove(e: MouseEvent | TouchEvent) {
		if (!drawing) return;
		
		e.preventDefault();
		
		const rect = canvas.getBoundingClientRect();
		const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
		const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;
		
		const x = (clientX - rect.left) * (canvasSize / rect.width);
		const y = (clientY - rect.top) * (canvasSize / rect.height);
		
		drawLine(lastX, lastY, x, y);
		
		lastX = x;
		lastY = y;
	}
	
	function draw(x: number, y: number) {
		if (!ctx) return;
		
		ctx.fillStyle = '#FFFFFF';
		ctx.beginPath();
		ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
		ctx.fill();
	}
	
	function drawLine(x1: number, y1: number, x2: number, y2: number) {
		if (!ctx) return;
		
		ctx.strokeStyle = '#FFFFFF';
		ctx.lineWidth = brushSize;
		ctx.lineCap = 'round';
		ctx.lineJoin = 'round';
		
		ctx.beginPath();
		ctx.moveTo(x1, y1);
		ctx.lineTo(x2, y2);
		ctx.stroke();
	}
</script>

<div class="canvas-container">
	<h2>Desenhe um Dígito (0-9)</h2>
	<div class="canvas-wrapper">
		<canvas
			bind:this={canvas}
			width={canvasSize}
			height={canvasSize}
			on:mousedown={startDrawing}
			on:mouseup={stopDrawing}
			on:mouseleave={stopDrawing}
			on:mousemove={onMouseMove}
			on:touchstart={startDrawing}
			on:touchend={stopDrawing}
			on:touchcancel={stopDrawing}
			on:touchmove={onMouseMove}
		></canvas>
	</div>
	<button class="clear-btn" on:click={clearCanvas}>
		Limpar
	</button>
</div>

<style>
	.canvas-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20px;
	}
	
	h2 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 400;
		color: #2A5AB3;
	}
	
	.canvas-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;
	}
	
	canvas {
		border: 2px solid #2A5AB3;
		border-radius: 8px;
		cursor: crosshair;
		touch-action: none;
		background: #000000;
		max-width: 100%;
		height: auto;
	}
	
	.clear-btn {
		padding: 12px 32px;
		background: #2A5AB3;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 2px 8px rgba(42, 90, 179, 0.3);
	}

	.clear-btn:hover {
		background: #85BDFF;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(133, 189, 255, 0.4);
	}
	
	.clear-btn:active {
		transform: translateY(0);
	}
	
	@media (max-width: 768px) {
		h2 {
			font-size: 1.2rem;
			text-align: center;
		}
		
		.canvas-wrapper {
			padding: 15px;
		}
		
		canvas {
			max-width: 280px;
		}
	}
</style>