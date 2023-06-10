import tensorflow_hub as hub
import tensorflow as tf
import PIL.Image
import numpy as np
import requests
import tempfile
import os


def load_img(path_to_img):
    max_dim = 512
    # Загрузка изображения с сервера Telegram
    response = requests.get(path_to_img)
    # Сохранение байтов во временный файл
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(response.content)
        temp_filename = f.name

    img = tf.io.read_file(temp_filename)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)

    # Удаление временного файла
    os.remove(temp_filename)

    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim

    new_shape = tf.cast(shape * scale, tf.int32)

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img


def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return PIL.Image.fromarray(tensor)


async def styling(content_path, style_path):
    content_image = load_img(content_path)
    style_image = load_img(style_path)

    hub_model = tf.saved_model.load('style_model')
    stylized_image = hub_model(tf.constant(content_image), tf.constant(style_image))[0]
    return tensor_to_image(stylized_image)
