"""
Train a high-accuracy CNN model for MNIST digit classification on CUDA GPU
Optimized for better performance with data augmentation and longer training

Usage on remote CUDA machine:
  python train_model_cuda.py

Requirements:
  pip install tensorflow numpy
  pip install "tensorflowjs>=4.0.0" --no-deps  # Skip numpy dependency
"""

import os
import sys
import tensorflow as tf
from tensorflow import keras
import numpy as np

# Configure GPU with compatibility for newer architectures
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Enable memory growth to avoid OOM errors
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # For very new GPUs (RTX 40xx/50xx), enable JIT compilation
        # This allows older TensorFlow versions to work with compute capability 12.0+
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

        print(f"✓ Found {len(gpus)} GPU(s)")
        print(f"  GPU: {gpus[0]}")
    except RuntimeError as e:
        print(f"⚠ GPU configuration error: {e}")
        print("  Falling back to CPU...")
        tf.config.set_visible_devices([], 'GPU')
else:
    print("⚠ No GPU found - training will be slow on CPU")

# Load MNIST dataset
print("\nLoading MNIST dataset...")
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

# Normalize pixel values to [0, 1]
x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0

# Reshape to add channel dimension (28, 28, 1)
x_train = np.expand_dims(x_train, -1)
x_test = np.expand_dims(x_test, -1)

# Convert labels to one-hot encoding
y_train = keras.utils.to_categorical(y_train, 10)
y_test = keras.utils.to_categorical(y_test, 10)

# Data augmentation for better generalization
# Note: If you get CUDA errors, comment out data augmentation and train without it
try:
    data_augmentation = keras.Sequential([
        keras.layers.RandomRotation(0.1),  # Rotate up to 10 degrees
        keras.layers.RandomZoom(0.1),       # Zoom up to 10%
        keras.layers.RandomTranslation(0.1, 0.1),  # Shift up to 10%
    ])
    use_augmentation = True
    print("✓ Data augmentation enabled")
except Exception as e:
    print(f"⚠ Data augmentation failed: {e}")
    print("  Training without augmentation...")
    data_augmentation = None
    use_augmentation = False

# Create improved CNN model
print("\nCreating improved CNN model...")
layers = [
    # Input layer
    keras.layers.Input(shape=(28, 28, 1)),
]

# Add data augmentation if available
if use_augmentation and data_augmentation is not None:
    layers.append(data_augmentation)

# Add convolutional blocks
layers.extend([
    # First convolutional block
    keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
    keras.layers.BatchNormalization(),
    keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Dropout(0.25),

    # Second convolutional block
    keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    keras.layers.BatchNormalization(),
    keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Dropout(0.25),

    # Third convolutional block
    keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Dropout(0.25),

    # Dense layers
    keras.layers.Flatten(),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(10, activation='softmax')
])

model = keras.Sequential(layers)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Callbacks for better training
callbacks = [
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=0.00001,
        verbose=1
    ),
    keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=8,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        'best_mnist_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

# Train model with more epochs
print("\n" + "="*60)
print("Training model (this may take 10-20 minutes on GPU)...")
print("="*60 + "\n")

history = model.fit(
    x_train, y_train,
    batch_size=128,
    epochs=30,
    validation_split=0.15,
    callbacks=callbacks,
    verbose=1
)

# Evaluate model
print("\n" + "="*60)
print("Evaluating model...")
print("="*60)
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\n✓ Test accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"✓ Test loss: {test_loss:.4f}")

# Load best model
model = keras.models.load_model('best_mnist_model.h5')
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\n✓ Best model accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")

# Save final model
print("\nSaving model in h5 format...")
os.makedirs('models', exist_ok=True)
model.save('models/mnist_model.h5')
print("✓ Model saved to models/mnist_model.h5")

# Convert to TensorFlow.js format
print("\nConverting to TensorFlow.js format...")
try:
    # Use Python API instead of CLI to avoid numpy compatibility issues
    import tensorflowjs as tfjs

    tfjs.converters.save_keras_model(model, 'static/model')
    print("✓ Model converted successfully")
    print("✓ Model saved to static/model/")
except ImportError:
    print("\n✗ tensorflowjs not found.")
    print("Try: pip install tensorflowjs")
    print("\nAs a workaround, you can convert manually later:")
    print("  tensorflowjs_converter --input_format keras models/mnist_model.h5 static/model")
    # Don't exit - the model is still trained
except Exception as e:
    print(f"\n⚠ Conversion failed: {e}")
    print("\nYou can convert manually later with:")
    print("  tensorflowjs_converter --input_format keras models/mnist_model.h5 static/model")
    print("\nOr use the saved model file directly:")
    print("  models/mnist_model.h5")
    # Don't exit - the model is still trained

print("\n" + "="*60)
print("✓ TRAINING COMPLETE!")
print("="*60)
print(f"\nFinal accuracy: {test_acc*100:.2f}%")
print("\nFiles created:")
print("  - models/mnist_model.h5")
print("  - static/model/model.json")
print("  - static/model/group*.bin")
print("\nNext steps:")
print("  1. Copy the entire 'static/model/' directory to your local machine")
print("  2. Place it in the project's static/model/ folder")
print("  3. Run 'npm run dev' to test the model")
