import logging

import numpy as np
import matplotlib.pyplot as plt
from skimage import img_as_float, io


def rgb2gray(rgb):
    """
    Changes the given Colour Image into GreyScale
    """
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


def fourier(img):
    """
    Returns the Fourier Transform for the given Image
    """
    gray_img = rgb2gray(img)
    four = np.fft.fft2(gray_img)
    shifted_fourier = np.fft.fftshift(four)
    return shifted_fourier


def plot_fourier(fourier):
    """
    Plots the Fourier Transform Represented by the given Matrix
    """
    psd_2d = np.log(np.abs(fourier)**2+1)
    (height, width) = psd_2d.shape
    plt.figure(figsize=(10, 10*height/width), facecolor='white')
    plt.clf()
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.imshow(psd_2d, cmap='Greys_r', extent=[-np.pi, np.pi, -np.pi, np.pi], aspect='auto')
    plt.show()


def read_image_from_path(path):
    """
    Reads Image from the given path
    """
    if path.split('.')[0] == 'png':
        original_image = plt.imread(path).astype(float)
    else:
        original_image = img_as_float(io.imread(path))
    return original_image


def save_img_at_path(img, path):
    """
        Saves the Image at the given path
    """
    plt.imsave(path, img)


def gaussian_filter(img, blur_intensity):
    """
    Given the intensity the Blur Effect is Applied using Gaussian filter
    """
    # Prepare an Gaussian convolution kernel
    # First a 1-D  Gaussian
    t = np.linspace(-10, 10, 30)
    bump = np.exp(-blur_intensity*t**2)
    bump /= np.trapz(bump)  # normalize the integral to 1

    # make a 2-D kernel out of it
    kernel = bump[:, np.newaxis] * bump[np.newaxis, :]

    # Implement convolution via FFT
    # Padded fourier transform, with the same shape as the image
    kernel_ft = np.fft.fftn(kernel, s=img.shape[:2], axes=(0, 1))
    img_ft = np.fft.fftn(img, axes=(0, 1))

    # the 'newaxis' is to match to color direction
    img2_ft = kernel_ft[:, :, np.newaxis] * img_ft

    img2 = np.fft.ifft2(img2_ft, axes=(0, 1)).real

    return img2


def setup_logger_to_console_file(log_file_path=None, log_level=None):
    if not log_level:
        log_level = logging.INFO

    log_formatter = logging.Formatter("%(asctime)s %(levelname)-5.5s %(module)-10.10s %(funcName)-10.10s  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

