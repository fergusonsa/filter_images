from tkinter import simpledialog

import PIL
import PIL.ImageDraw
import PIL.ImageFilter
import numpy as np


class Filter:
    """
    Base Class for all Filters
    """
    name = "base filter"
    kernel = None

    def channel_adjust(self, channel, values):
        """
        Changes the channel with respect to given value
        """
        orig_size = channel.shape
        flat_channel = channel.flatten()
        adjusted = np.interp(flat_channel, np.linspace(0, 1, len(values)), values)

        return adjusted.reshape(orig_size)

    def apply_kernel(self, original_image):
        input_pixels = original_image.load()

        # Middle of the kernel
        offset = len(self.kernel) // 2

        # Create output image
        output_image = PIL.Image.new("RGB", original_image.size)
        draw = PIL.ImageDraw.Draw(output_image)

        # Compute convolution between intensity and kernels
        for x in range(offset, original_image.width - offset):
            for y in range(offset, original_image.height - offset):
                acc = [0, 0, 0]
                for a in range(len(self.kernel)):
                    for b in range(len(self.kernel)):
                        xn = x + a - offset
                        yn = y + b - offset
                        pixel = input_pixels[xn, yn]
                        acc[0] += pixel[0] * self.kernel[a][b]
                        acc[1] += pixel[1] * self.kernel[a][b]
                        acc[2] += pixel[2] * self.kernel[a][b]

                draw.point((x, y), (int(acc[0]), int(acc[1]), int(acc[2])))
        return output_image

    def apply_filter(self, img, *args):
        """
            function applies the the according filter
        """
        raise NotImplementedError

    def request_additional_parameters(self):
        return []


# class GothamFilter(Filter):
#     """
#     Implementation of an Instagram Filter named Gotham filter
#         -> Channels down the r-channel
#             and increases the b-channel
#         -> Blurs the given Image to an appropriate Proportion
#     """
#     name = 'gotham'
#
#     def apply_filter(self, original_image, *args):
#         """
#         Applies the default filter
#         """
#         r = original_image[:, :, 0]
#         b = original_image[:, :, 2]
#         r_boost_lower = self.channel_adjust(r, [
#             0, 0.05, 0.1, 0.2, 0.3,
#             0.5, 0.7, 0.8, 0.9,
#             0.95, 1.0])
#         b_more = np.clip(b + 0.03, 0, 1.0)
#         merged = np.stack([r_boost_lower, original_image[:, :, 1], b_more], axis=2)
#
#         '''
#             Blurs the image. FFT is used here.
#         '''
#         blurred = gaussian_filter(merged, 0.001)
#
#         final = np.clip(merged * 1.3 - blurred * 0.3, 0, 1.0)
#         b = final[:, :, 2]
#         b_adjusted = self.channel_adjust(b, [
#             0, 0.047, 0.198, 0.251, 0.318,
#             0.392, 0.42, 0.439, 0.475,
#             0.561, 0.58, 0.627, 0.671,
#             0.733, 0.847, 0.925, 1])
#
#         final[:, :, 2] = b_adjusted
#         return final


# class RiverdaleFilter(Filter):
#     name = 'riverdale'
#
#     def apply_filter(self, original_image, *args):
#         r = original_image[:, :, 0]
#         b = original_image[:, :, 2]
#         r_boost_lower = self.channel_adjust(r, [
#             0, 0.05, 0.1, 0.2, 0.3,
#             0.5, 0.7, 0.8, 0.9,
#             0.95, 1.0])
#         b_more = np.clip(b + 0.2, 0, 1.0)
#         merged = np.stack([r_boost_lower, original_image[:, :, 1], b_more], axis=2)
#
#         # Note: This has been changed to use the custom-defined Gaussian filter using FFT
#         blurred = gaussian_filter(merged, 0.1)
#
#         final = np.clip(merged + blurred*0.3, 0, 1.0)
#         # b = final[:, :,1]
#         return final


# class RandomFilter(Filter):
#     name = 'random'
#
#     def apply_filter(self, original_image, *args):
#         r = original_image[100:, :, 0]
#         b = original_image[100:, :, 2]
#         r_boost_lower = self.channel_adjust(r, [
#             0, 0.05, 0.1, 0.2, 0.3,
#             0.5, 0.7, 0.8, 0.9,
#             0.95, 1.0])
#         # b_more = np.clip(b + 0.2, 0, 1.0)
#         merged = np.stack([r_boost_lower, original_image[100:, :, 1], b], axis=2)
#
#         # Apply the Gaussian Filter in the frequency domain to average the color values
#         blurred = gaussian_filter(merged, 0.1)
#
#         final = np.clip(merged + blurred*0.3, 0, 1.0)
#         # b = final[100:, :,1]
#         return final


# class GrayscaleFilter(Filter):
#     name = 'gray'
#
#     def apply_filter(self, original_image, *args):
#         # r = original_image[:, :, 0]
#         # g = original_image[:, :, 1]
#         # b = original_image[:, :, 2]
#         gray = rgb2gray(original_image)
#         r = g = b = gray
#         merged = np.stack([r, g, b], axis=2)
#
#         # Apply the Gaussian Filter in the frequency domain to average the color values
#         blurred = gaussian_filter(merged, 0.1)
#
#         final = np.clip(merged + blurred*0.3, 0, 1.0)
#         return final


class BlurFilter(Filter):
    name = 'blur'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.BLUR)

    # def request_additional_parameters(self):
    #     amount = simpledialog.askfloat("Blur amount", "Blur percentage", minvalue=0.0, maxvalue=100.0)
    #     return [amount]


class GaussianFilter(Filter):
    name = 'gaussian'

    def apply_filter(self, original_image, *args):
        radius = args[0]
        return original_image.filter(PIL.ImageFilter.GaussianBlur(radius))

    def request_additional_parameters(self):
        radius = simpledialog.askinteger("Radius", "Radius", minvalue=1, maxvalue=10)
        return [radius]


class SharpenFilter(Filter):
    name = 'sharpen'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.SHARPEN)


class SmoothFilter(Filter):
    name = 'smooth'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.SMOOTH)


class SmoothMoreFilter(Filter):
    name = 'smooth more'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.SMOOTH_MORE)


class ContourMoreFilter(Filter):
    name = 'contour'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.CONTOUR)


class ContourFilter(Filter):
    name = 'contour'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.CONTOUR)


class DetailFilter(Filter):
    name = 'detail'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.DETAIL)


class EdgeEnhanceFilter(Filter):
    name = 'edge enhance'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.EDGE_ENHANCE)


class EdgeEnhanceMoreFilter(Filter):
    name = 'edge enhance more'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.EDGE_ENHANCE_MORE)


class EmbossFilter(Filter):
    name = 'emboss'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.EMBOSS)


class FindEdgesFilter(Filter):
    name = 'find edges'

    def apply_filter(self, original_image, *args):
        return original_image.filter(PIL.ImageFilter.FIND_EDGES)


# class MultipleFilter(Filter):
#     name = 'multiple'
#
#     def apply_filter(self, original_image, *args):
#         final = original_image
#         for custom_filter in args:
#             f = custom_filter()
#             additional_args = f.request_additional_parameters()
#             if additional_args:
#                 final = f.apply_filter(final, *additional_args)
#             else:
#                 final = f.apply_filter(final)
#
#         return final


# class FourierFilter(Filter):
#     name = 'fourier'
#
#     def apply_filter(self, original_image, *args):
#         final = original_image
#         for custom_filter in args:
#             f = custom_filter()
#             additional_args = f.request_additional_parameters()
#             if additional_args:
#                 final = f.apply_filter(final, *additional_args)
#             else:
#                 final = f.apply_filter(final)
#         utils.plot_fourier(utils.fourier(self.modified_render))
#         return final
#
#
