import { writable } from 'svelte/store';

export interface Prediction {
	digit: number;
	probability: number;
}

export const predictions = writable<Prediction[]>(
	Array.from({ length: 10 }, (_, i) => ({ digit: i, probability: 0 }))
);

export const isModelLoaded = writable(false);
export const isDrawing = writable(false);
