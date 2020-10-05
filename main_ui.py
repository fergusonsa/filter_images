# Simple enough, just import everything from tkinter.
import functools
import logging
import tkinter
from tkinter import filedialog

from PIL import Image, ImageTk

import utils
import Filter
import CV2Filters

logger = logging.getLogger(__name__)


class ButtonBar(tkinter.Frame):

    def __init__(self, master, filter_map):
        tkinter.Frame.__init__(self, master)
        # creating a button instance
        select_file_button = tkinter.Button(self, text="Open", command=self.master.open, padx=10)
        # placing the button on my window
        select_file_button.grid(row=0, column=0)
        # creating a button instance
        save_filter_button = tkinter.Button(self, padx=10, text="Save ...",
                                            command=self.master.save_file)
        save_filter_button.grid(row=0, column=1)
        reset_button = tkinter.Button(self, padx=10, text="Undo",
                                            command=self.master.reset_modified_image)
        reset_button.grid(row=0, column=2)
        row_index = 0
        column_index = 3
        for (filter_name, filter_class) in filter_map.items():
            logger.debug('Creating button for {} with column index {}'.format(filter_name, column_index))
            filter_button = tkinter.Button(self, padx=10, text=filter_name,
                                           command=functools.partial(self.master.apply_and_show_filter, filter_name,
                                                                     filter_class))
            filter_button.grid(row=row_index, column=column_index)
            column_index += 1
            if column_index > 9:
                row_index += 1
                column_index = 3

        # # creating a button instance
        # fourier_button = Button(button_bar_frame, padx=10, text="Plot Fourier Transform", command=self.show_fourier)
        # fourier_button.grid(row=0, column=column_index)


class Window(tkinter.Frame):
    # Here, we are creating our class, Window, and inheriting from the Frame
    # class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):

        self.filter_map = {x.name: x for x in Filter.Filter.__subclasses__()}

        # parameters that you want to send through the Frame class.
        tkinter.Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        button_bar = ButtonBar(self, self.filter_map)
        button_bar.pack()

        self.selected_path = None

        self.displayed_image_width = 0
        self.displayed_image_height = 0
        self.original_image = None  # Used to keep the actual original image as read from the file
        self.original_image_resized = None  # Used to keep the actual original image
        self.original_canvas = None  # Used to display the Modified Image
        self.modified_image = None  # Used to keep the actual modified image as read from the file
        self.modified_resized_image = None  # Used to keep the actual modified image
        self.modified_canvas = None  # Used to display the original Image

        # with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    # Creation of init_window
    def init_window(self):
        logger.debug('Into init_window()')

        # changing the title of our master widget
        self.master.title("Image Editor")
        self.pack(fill=tkinter.BOTH, expand=1)

        button_bar_frame = tkinter.Frame(self.master, bd=1, relief=tkinter.RAISED, bg='blue',
                                         height=55, width=self.winfo_width())
        button_bar_frame.place(x=0, y=0)
        # button_bar_frame.pack(fill=X, expand=1)
        # button_bar_frame.grid(row=0, columnspan=1)
        frame_horizontal = tkinter.Frame(self.master, bd=1, bg='red',
                                         height=(self.winfo_height() - 60),
                                         width=self.winfo_width())
        frame_horizontal.place(x=0, y=60)

        # allowing the widget to take the full space of the root window
        # frame_horizontal.pack(fill=BOTH, expand=1)

        # # creating a menu instance
        # menu = Menu(self.master)
        # self.master.config(menu=menu)
        #
        # # create the file object)
        # file = Menu(menu)
        #
        # # adds a command to the menu option, calling it exit, and the
        # # command it runs on event is client_exit
        # file.add_command(label="Exit", command=self.client_exit)
        #
        # # added "file" to our menu
        # menu.add_cascade(label="File", menu=file)
        #
        # # allowing the widget to take the full space of the root window
        # self.pack(fill=BOTH, expand=1, ipadx=100)

        logger.debug('maximum image size is {} x {}, calculated from window size {} x {}'.format(
            self.get_displayed_image_width(), self.get_displayed_image_height(),
            self.winfo_width(), self.winfo_height()))

        # The widget to show the original image.
        self.original_canvas = tkinter.Label(frame_horizontal, borderwidth=2, width=self.get_displayed_image_width(),
                                             height=self.get_displayed_image_height(), bg='orange')
        self.original_canvas.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=1)

        # The widget to show the modified image.
        self.modified_canvas = tkinter.Label(frame_horizontal, borderwidth=2, width=self.get_displayed_image_width(),
                                             height=self.get_displayed_image_height(), bg='yellow')
        self.modified_canvas.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=1)

    def get_displayed_image_width(self):
        return int((self.winfo_width() - 100) // 2)

    def get_displayed_image_height(self):
        return self.winfo_height() - 70

    def open(self):
        """
        Present the open file dialog and then open the image and set the variables
        """
        self.selected_path = filedialog.askopenfilename()
        logger.debug("Image to be opened: {}".format(self.selected_path))
        self.show_image(self.selected_path)

    def show_image(self, path):
        """
        Reads the image from the given path and displays the image in the window
        """
        logger.debug('Starting show_image(path="{}"'.format(path))
        load = Image.open(path)
        self.original_image = load
        self.modified_image = load.copy()

        display_image = self.get_modified_image_to_display()
        self.original_image_resized = ImageTk.PhotoImage(display_image)
        self.original_canvas.configure(image=self.original_image_resized)
        # self.original_canvas.create_image(5, 5, image=display_image)
        self.original_canvas["image"] = self.original_image_resized
        self.modified_resized_image = ImageTk.PhotoImage(display_image)
        self.modified_canvas.configure(image=self.modified_resized_image)
        # self.modified_canvas.create_image(5, 5, image=display_image)
        self.modified_canvas["image"] = self.modified_resized_image

        self.master.update_idletasks()
        logger.debug('Completed show_image(path="{}"'.format(path))

    def update_displayed_modified_image(self):
        """
        Shows the edited image on the window
        """
        logger.debug('Started update_displayed_modified_image()')

        display_image = self.get_modified_image_to_display()
        self.modified_resized_image = ImageTk.PhotoImage(display_image)
        self.modified_canvas.configure(image=self.modified_resized_image)
        # self.modified_canvas.create_image(5, 5, image=display_image)
        self.modified_canvas["image"] = self.modified_resized_image

        self.master.update_idletasks()
        logger.debug('Completed update_displayed_modified_image()')

    def get_modified_image_to_display(self):
        image_size_width = self.modified_image.width
        image_size_height = self.modified_image.height
        if image_size_width > self.get_displayed_image_width() or image_size_height > self.get_displayed_image_height():
            width_ratio = image_size_width / self.get_displayed_image_width()
            height_ratio = image_size_height / self.get_displayed_image_height()
            if width_ratio > height_ratio:
                # Use the width as the maximum
                new_width = self.get_displayed_image_width()
                new_height = int(image_size_height // width_ratio)
            else:
                # use the height as the maximum
                new_width = int(image_size_width // height_ratio)
                new_height = self.get_displayed_image_height()

            logger.debug('resizing image from {} x {} to {} x {}'.format(image_size_width, image_size_height,
                                                                         new_width, new_height))
            display_image = self.modified_image.resize((new_width, new_height), Image.ANTIALIAS)
        else:
            logger.debug('Keeping image size at {} x {}'.format(image_size_width, image_size_height))
            display_image = self.modified_image
        return display_image

    # def show_blur_filter(self):
    #     """
    #     Opens the dialog to input the amount of percentage to produce Blur effect on the image
    #     """
    #     logger.debug('Started show_blur_filter()')
    #     f = BlurFilter()
    #     a = simpledialog.askfloat("Blur amount", "Blur percentage", minvalue=0.0, maxvalue=100.0)
    #     self.modified_render = f.apply_filter(self.modified_render, a)
    #     save_img_at_path(self.modified_render, ".test2222.png")
    #     self.update_displayed_modified_image(".test2222.png")
    #     logger.debug('Completed show_blur_filter()')

    def apply_and_show_filter(self, filter_name, filter_class, *args):
        """
        Gets the filter to be applied as input and applies the corresponding filter on the image
        """
        logger.debug('Starting apply_and_show_filter(filter_name="{}", args={})'.format(filter_name, args))
        f = filter_class()
        additional_args = f.request_additional_parameters()
        if additional_args:
            self.modified_image = f.apply_filter(self.modified_image, *additional_args)
        else:
            self.modified_image = f.apply_filter(self.modified_image, *args)
        self.update_displayed_modified_image()
        logger.debug('Completed apply_and_show_filter(filter_name="{}", args={})'.format(filter_name, args))

    # def show_fourier(self):
    #     """
    #     Displays the fourier transform of the modified image
    #     """
    #     plot_fourier(fourier(self.modified_render))

    def save_file(self):
        """
        Saves the edited image in a path
        """
        save_path = filedialog.asksaveasfilename()
        if save_path:
            print("Image will be saved at: ", save_path)
            utils.save_img_at_path(self.modified_resized_image, save_path)

    def reset_modified_image(self):
        self.modified_image = self.original_image.copy()
        self.update_displayed_modified_image()

    def client_exit(self):
        exit()


if __name__ == '__main__':

    utils.setup_logger_to_console_file(log_level=logging.DEBUG)
    # logger.debug(filter_map)

    # root window created. Here, that would be the only window
    root = tkinter.Tk()

    root.geometry("1200x2000+0+0")

    '''
        Attach the Window in to the root
    '''
    app = Window(root)

    # mainloop
    root.mainloop()
