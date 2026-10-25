import os
import numpy as np
from PIL import Image
import tensorflow as tf
from sklearn.model_selection import train_test_split

# Store images and labels
X = []
y = []

classes = [
    "FreshApple",
    "RottenApple",
    "FreshBanana",
    "RottenBanana",
    "FreshOrange",
    "RottenOrange"
]

# Read images
for label in classes:

    folder = os.path.join("dataset", label)

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        try:
            img = Image.open(path).convert("RGB")
            img = img.resize((64, 64))

            X.append(np.array(img))
            y.append(classes.index(label))

        except Exception as e:
            print("Error:", path)

# Convert to NumPy arrays
X = np.array(X, dtype="float32") / 255.0
y = np.array(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# CNN Model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(64,64,3)),

    tf.keras.layers.Conv2D(32,(3,3),activation="relu"),
    tf.keras.layers.MaxPooling2D((2,2)),

    tf.keras.layers.Conv2D(64,(3,3),activation="relu"),
    tf.keras.layers.MaxPooling2D((2,2)),

    tf.keras.layers.Flatten(),

    tf.keras.layers.Dense(128,activation="relu"),

    tf.keras.layers.Dense(6,activation="softmax")
])

# Compile
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Train
model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=32,
    validation_data=(X_test,y_test)
)

# Accuracy
loss, accuracy = model.evaluate(X_test, y_test)

print(f"Accuracy : {accuracy*100:.2f}%")

# Save model
model.save("fruit_model.keras")

print("Model Saved Successfully!")