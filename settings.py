import os

PATH = os.path.dirname(__file__) + os.sep
PATH_DATA = PATH + "data" + os.sep

basket = []

PACKING_BOX_VOLUME = 10000
PACKING_BOX_PRICE = 200

FILE_PRODUCTS = "list_products.json"
FILE_RESOURCES = "list_resources.json"
FILE_SELLERS = "sellers.json"
FILE_ORDERS = "orders.json"

DEFAULT_QUANTITY = "1"
SELLER_ID_START = 1001
DATE_FORMAT = "%d.%m.%Y"

WINDOW_SIZE = (350, 700)
WINDOW_CLEAR_COLOR = (0.055, 0.07, 0.09, 1)
WINDOW_LEFT = 450
WINDOW_TOP = 1
