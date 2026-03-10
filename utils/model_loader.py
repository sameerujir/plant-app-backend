import os
import tensorflow as tf
import tf_keras as keras
from config.settings import MODEL_PATH, CLASS_NAMES

_model = None

def get_model():
    global _model
    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    try:
        IMG_SHAPE = (128, 128, 3)

        base_model = keras.applications.MobileNetV2(
            input_shape=IMG_SHAPE,
            include_top=False,
            weights='imagenet',
            alpha=0.35
        )
        base_model.trainable = False

        inputs = keras.Input(shape=IMG_SHAPE)
        x = base_model(inputs, training=False)
        x = keras.layers.GlobalAveragePooling2D()(x)
        x = keras.layers.Dropout(0.2)(x)
        outputs = keras.layers.Dense(len(CLASS_NAMES), activation='softmax')(x)

        _model = keras.Model(inputs, outputs)
        _model.load_weights(MODEL_PATH)

        _model.compile(
            optimizer=keras.optimizers.legacy.Adam(learning_rate=0.001, clipnorm=1.0),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        return _model

    except Exception as e:
        raise Exception(f"Model loading failed: {e}")