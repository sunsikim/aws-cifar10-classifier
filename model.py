import tensorflow as tf
import pathlib

from typing import Tuple, List


def define_model_cnn(input_shape: Tuple[int, int, int]) -> tf.keras.Model:
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Conv2D(
                filters=32,
                kernel_size=(3, 3),
                activation="relu",
                padding="SAME",
                name="convolution_1",
                input_shape=input_shape
            ),
            tf.keras.layers.Conv2D(
                filters=32,
                kernel_size=(3, 3),
                activation="relu",
                padding="SAME",
                name="convolution_2"
            ),
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2), name="max_pool_1"),
            tf.keras.layers.BatchNormalization(name="batch_normalization_1"),
            tf.keras.layers.Dropout(0.5, name="dropout_1"),
            tf.keras.layers.Conv2D(
                filters=64,
                kernel_size=(3, 3),
                activation="relu",
                padding="SAME",
                name="convolution_3"
            ),
            tf.keras.layers.Conv2D(
                filters=64,
                kernel_size=(3, 3),
                activation="relu",
                padding="SAME",
                name="convolution_4"
            ),
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2), name="max_pool_2"),
            tf.keras.layers.BatchNormalization(name="batch_normalization_2"),
            tf.keras.layers.Dropout(0.5, name="dropout_2"),
            tf.keras.layers.Conv2D(
                filters=128,
                kernel_size=(3, 3),
                activation="relu",
                padding="SAME",
                name="convolution_5"
            ),
            tf.keras.layers.Conv2D(
                filters=128,
                kernel_size=(3, 3),
                activation="relu",
                padding="SAME",
                name="convolution_6"
            ),
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2), name="max_pool_3"),
            tf.keras.layers.BatchNormalization(name="batch_normalization_3"),
            tf.keras.layers.Dropout(0.5, name="dropout_3"),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(10, activation="sigmoid"),
        ],
        name="cifar10_classifier_cnn"
    )
    model.compile(
        optimizer=tf.keras.optimizers.legacy.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    return model


def define_callbacks(local_dir: pathlib.Path, prefix: str) -> List[tf.keras.callbacks.Callback]:
    model_dir = local_dir.joinpath(prefix)
    model_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=f"{model_dir}/ckpt",
        save_weights_only=True,
        save_best_only=True,
        save_freq="epoch",
        monitor="val_accuracy",
        verbose=1,
    )
    csv_record_callback = tf.keras.callbacks.CSVLogger(
        filename=f"{model_dir}/training_log.csv"
    )
    early_stopping_callback = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=5, mode="max"
    )
    return [checkpoint_callback, csv_record_callback, early_stopping_callback]


