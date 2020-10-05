import PIL
import cv2
import numpy

import Filter


class DetailEnhanceFilter(Filter.Filter):
    name = "Detail Enhance"

    def apply_filter(self, image, *args):
        img = numpy.array(image)
        # convert the image into grayscale image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur the grayscale image with median blur
        gray_blur = cv2.medianBlur(gray, 3)

        # Apply adaptive thresholding to detect edges
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        # Sharpen the image
        color = cv2.detailEnhance(img, sigma_s=5, sigma_r=0.5)

        # Merge the colors of same images using "edges" as a mask
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        result = PIL.Image.fromarray(cartoon, 'RGB')
        return result


class PencilSketchFilter(Filter.Filter):
    name = "Pencil Sketch"

    def apply_filter(self, image, *args):
        img = numpy.array(image)
        # Convert the image into grayscale image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur the image using Gaussian Blur
        gray_blur = cv2.GaussianBlur(gray, (25, 25), 0)

        # Convert the image into pencil sketch
        cartoon = cv2.divide(gray, gray_blur, scale=250.0)
        result = PIL.Image.fromarray(cartoon, 'RGB')
        return result


class BilateralFilter(Filter.Filter):
    name = "Bilateral"

    def apply_filter(self, image, *args):
        img = numpy.array(image)
        # Convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply median blur
        gray = cv2.medianBlur(gray, 3)

        # Detect edges with adaptive threshold
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        # Apply bilateral filter
        color = cv2.bilateralFilter(img, 5, 50, 5)

        # Merge the colors of same image using "edges" as a mask
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        result = PIL.Image.fromarray(cartoon, 'RGB')
        return result


class PencilEdgesFilter(Filter.Filter):
    name = "Pencil Edges"

    def apply_filter(self, image, *args):
        img = numpy.array(image)
        # Convert the image into grayscale image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur the grayscale image using median blur
        gray = cv2.medianBlur(gray, 25)

        # Detect edges with Laplacian
        edges = cv2.Laplacian(gray, -1, ksize=3)

        # Invert the edges
        edges_inv = 255 - edges

        # Create a pencil edge sketch
        dummy, cartoon = cv2.threshold(edges_inv, 150, 255, cv2.THRESH_BINARY)
        result = PIL.Image.fromarray(cartoon, 'RGB')
        return result


class CartoonFilter(Filter.Filter):
    """
    Based on https://towardsdatascience.com/building-an-image-cartoonization-web-app-with-python-382c7c143b0d
    """
    name = "Cartoon"

    def apply_filter(self, img, *args):
        pencil_sketch_filter = PencilSketchFilter()
        step1 = pencil_sketch_filter.apply_filter(img)
        detail_filter = DetailEnhanceFilter()
        step2 = detail_filter.apply_filter(step1)
        bilateral_filter = BilateralFilter()
        step3 = bilateral_filter.apply_filter(step2)
        pencil_edges_filter = PencilEdgesFilter()
        step4 = pencil_edges_filter.apply_filter(step3)
        return step4
