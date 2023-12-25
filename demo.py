import streamlit as st
import pandas as pd
import tensorflow as tf
import numpy as np
import pathlib
import matplotlib.pyplot as plt

from model import LOCAL_DIR
from typing import Tuple

local_dir = pathlib.Path(LOCAL_DIR)
label_names = [
    "airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"
]
label_decoder = dict(enumerate(label_names))


@st.cache_resource
def load_pretrained_model() -> tf.keras.Model:
    return tf.saved_model.load(str(local_dir.joinpath("result")))


@st.cache_data
def load_train_history() -> pd.DataFrame:
    return pd.read_csv(local_dir.joinpath("training_log.csv"))


def load_test_data() -> Tuple[np.array, np.array]:
    _, (images, labels) = tf.keras.datasets.cifar10.load_data()
    return images, labels


def decode_labels(labels: np.array) -> np.array:
    labels = labels.flatten()
    names = list(map(lambda x: label_decoder[x], labels))
    return np.array(names)


model = load_pretrained_model()
train_history = load_train_history()
images, labels = load_test_data()
labels = labels.flatten()
result_indices = list(label_decoder.values())
st.title("Pretrained Image Classifiers Demo")

if st.sidebar.button("Refresh"):
    random_index = np.random.randint(0, images.shape[0])
    sample_image = images[random_index][np.newaxis, :, :, :] / 255.
    sample_image = sample_image.astype(np.float32)
    sample_image_label = labels[random_index]
    text_column, sample_image_column = st.columns(spec=[0.85, 0.15])
    with text_column:
        """
        As displayed example, each image in CIFAR10 dataset consists of 32x32 shaped RGB image with corresponding label 
        of the image. Each of classifier will pass the image into the model to calculate softmax values for each label.
        Decision rule is to pick label whose softmax value is highest compared to others.
        """
    with sample_image_column:
        fig, ax = plt.subplots(1, 1)
        ax.imshow(images[random_index])
        ax.set_xticks([])
        ax.set_yticks([])
        st.pyplot(fig)
        st.caption(f"label: {label_decoder[sample_image_label]}")

    st.header("CNN Model Prediction Result")
    cnn_scores = model(sample_image)[0]
    cnn_prediction = np.argmax(cnn_scores)
    predicted_label = label_decoder[int(cnn_prediction)]
    if cnn_prediction == sample_image_label:
        st.success(f"Prediction result of CNN model is correct(label: {predicted_label})", icon="✅")
    else:
        st.warning(f"CNN model failed to give correct prediction(label: {predicted_label})", icon="⚠️")
    st.bar_chart(pd.DataFrame({"softmax scores(CNN)": cnn_scores}, index=result_indices))
else:
    st.text("Click `Refresh` button on the sidebar")

st.caption("Plots of loss and metrics over training epoch")
loss_tab, acc_tab = st.tabs(["loss", "accuracy"])
with loss_tab:
    st.line_chart(
        data=train_history[["loss", "val_loss", "epoch"]],
        x="epoch", y=["loss", "val_loss"]
    )
with acc_tab:
    st.line_chart(
        data=train_history[["accuracy", "val_accuracy", "epoch"]],
        x="epoch", y=["accuracy", "val_accuracy"]
    )
