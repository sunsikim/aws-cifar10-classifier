import tensorflow as tf
import numpy as np
import pathlib
import logging
import sys

from typing import Tuple, List

formatter = logging.Formatter(
    fmt="%(asctime)s : %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

LOCAL_DIR = "/tmp/cifar10"


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


def define_callbacks(local_dir: pathlib.Path) -> List[tf.keras.callbacks.Callback]:
    local_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=f"{local_dir}/ckpt",
        save_weights_only=True,
        save_best_only=True,
        save_freq="epoch",
        monitor="val_accuracy",
        verbose=1,
    )
    csv_record_callback = tf.keras.callbacks.CSVLogger(
        filename=f"{local_dir}/training_log.csv"
    )
    early_stopping_callback = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=5, mode="max"
    )
    return [checkpoint_callback, csv_record_callback, early_stopping_callback]


def apply_image_augmentation(image: tf.Tensor, label: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    Define series of image augmentation operations to be applied to input image
    :param image: standardized image whose pixel values fall into [0, 1]
    :param label: corresponding label
    :return: tensor of augmented images with its label
    """
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.image.random_hue(image, max_delta=0.2)
    image = tf.image.random_brightness(image, max_delta=0.3)
    image = tf.clip_by_value(image, clip_value_min=0, clip_value_max=1)
    return image, label


def get_tf_dataset(images: np.array, labels: np.array, apply_augmentation: bool) -> tf.data.Dataset:
    """
    wrap dataset into tf.data.Dataset API to be iterated within training loop
    :param images: array of raw images
    :param labels: array of corresponding label
    :param apply_augmentation: whether image augmentation has to be applied
    :return: tensorflow dataset
    """
    if apply_augmentation:
        return (
            tf.data.Dataset.from_tensor_slices((images / 255, labels))
            .map(apply_image_augmentation)
            .shuffle(buffer_size=256)
            .batch(batch_size=64)
        )
    else:
        return (
            tf.data.Dataset.from_tensor_slices((images / 255, labels))
            .shuffle(buffer_size=256)
            .batch(batch_size=64)
        )


if __name__ == '__main__':
    local_dir = pathlib.Path(LOCAL_DIR)
    local_dir.mkdir(exist_ok=True, parents=True)

    logger.info("Load CIFAR10 data from Keras dataset")
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()

    logger.info("Train CNN classifier with augmented data")
    model = define_model_cnn(train_images[0].shape)
    model.fit(
        x=get_tf_dataset(train_images, train_labels, True),
        epochs=30,
        verbose=2,
        callbacks=define_callbacks(local_dir),
        validation_data=get_tf_dataset(test_images, test_labels, False),
    )

    logger.info("Save trained CNN classifier")
    model.load_weights(filepath=f"{local_dir}/ckpt")
    tf.saved_model.save(model, f"{local_dir}/result")
