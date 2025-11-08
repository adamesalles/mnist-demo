import * as tf from '@tensorflow/tfjs';

let model: tf.LayersModel | null = null;

/**
 * Creates a simple CNN model for MNIST
 */
function createModel(): tf.LayersModel {
	const model = tf.sequential();

	model.add(tf.layers.conv2d({
		inputShape: [28, 28, 1],
		filters: 16,
		kernelSize: 3,
		activation: 'relu'
	}));
	model.add(tf.layers.maxPooling2d({ poolSize: 2 }));

	model.add(tf.layers.conv2d({
		filters: 32,
		kernelSize: 3,
		activation: 'relu'
	}));
	model.add(tf.layers.maxPooling2d({ poolSize: 2 }));

	model.add(tf.layers.flatten());
	model.add(tf.layers.dense({ units: 64, activation: 'relu' }));
	model.add(tf.layers.dense({ units: 10, activation: 'softmax' }));

	return model;
}

/**
 * Loads the pretrained model
 */
export async function loadModel(): Promise<void> {
	try {
		// Try to load from local static folder (works in both dev and prod)
		const modelPath = import.meta.env.MODE === 'production'
			? '/mnist-demo/model/model.json'
			: '/model/model.json';
		model = await tf.loadLayersModel(modelPath);
		console.log('Local trained model loaded successfully');
	} catch (error) {
		// Load Google's pretrained MNIST model from GitHub as fallback
        console.log(error)
		try {
			model = await tf.loadLayersModel(
				'https://raw.githubusercontent.com/google/tfjs-mnist-workshop/master/model/model.json'
			);
			console.log('Pretrained MNIST model loaded from Google GitHub');
		} catch (cdnError) {
			console.log('Failed to load pretrained model, creating new untrained model');
			model = createModel();
			console.log('Warning: Model is untrained and will give random predictions.');
		}
	}
}

/**
 * Preprocesses canvas image data for prediction
 */
function preprocessImage(imageData: ImageData): tf.Tensor {
	return tf.tidy(() => {
		// Convert to tensor
		let tensor = tf.browser.fromPixels(imageData, 1);

		// Resize to 28x28 if needed
		tensor = tf.image.resizeBilinear(tensor, [28, 28]);

		// Normalize to [0, 1]
		tensor = tensor.div(255.0);

		// Flatten to [784] for the Dense model, or keep as [28, 28, 1] for CNN model
		const inputShape = model?.layers[0].input;
		const shape = Array.isArray(inputShape) ? inputShape[0].shape : inputShape?.shape;
		if (shape && shape.length === 2) {
			// Dense model expects flattened input [batch, 784]
			tensor = tensor.reshape([28 * 28]);
			return tensor.expandDims(0);
		} else {
			// CNN model expects shaped input [batch, 28, 28, 1]
			return tensor.expandDims(0);
		}
	});
}

/**
 * Makes a prediction on the given image data
 */
export async function predict(imageData: ImageData): Promise<number[]> {
	if (!model) {
		throw new Error('Model not loaded');
	}

	const tensor = preprocessImage(imageData);
	const prediction = model.predict(tensor) as tf.Tensor;
	const probabilities = await prediction.data();

	// Clean up tensors
	tensor.dispose();
	prediction.dispose();

	return Array.from(probabilities);
}

/**
 * Checks if model is loaded
 */
export function isModelReady(): boolean {
	return model !== null;
}