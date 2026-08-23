import os

os.environ["KIVY_NO_MULTITOUCH"] = "1"
import json
from settings import *
from resources import *
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.checkbox import CheckBox
from datetime import datetime
from kivy.utils import platform
from kivy.lang import Builder


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_products():
    with open(PATH_DATA + "list_products.json", "r", encoding="utf8") as file:
        data = json.load(file)
    return data


def reset_quantities():
    products = read_products()

    for name in products:
        products[name]["quantity"] = "1"

    write_json(PATH_DATA + "list_products.json", products)


class BoxRow(BoxLayout):
    product_name = StringProperty("")
    product_price = StringProperty("")
    product_volume = StringProperty("")
    product_quantity = StringProperty("")
    cb_active = BooleanProperty(False)

    def on_touch_up(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]) and self.product_name:
            app = App.get_running_app()
            product_screen = app.root.get_screen("product_screen")
            product_screen.load_product(self.product_name)
            app.root.current = "product_screen"
        return super().on_touch_up(touch)

    def on_checkbox_active(self, instanse):
        if instanse.active:
            if self.product_name not in basket:
                basket.append(self.product_name)
        else:
            if self.product_name in basket:
                basket.remove(self.product_name)


class OrderRow(BoxLayout):
    product_name = StringProperty("")
    product_price = StringProperty("")
    product_volume = StringProperty("")
    quantity_box = StringProperty("0")
    box_count = StringProperty("0")

    def on_touch_up(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]) and self.product_name:
            app = App.get_running_app()
            screen = app.root.get_screen("order")
            screen.load_orders()

        return super().on_touch_up(touch)


class MainLabel(Label):
    pass


class MainImage(Image):
    pass


class BasketRow(BoxLayout):
    product_name = StringProperty("")
    product_price = StringProperty("")
    product_volume = StringProperty("")
    quantity_box = StringProperty("0")

    def on_touch_up(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]) and self.product_name:
            app = App.get_running_app()
            item_screen = app.root.get_screen("basket_item")
            item_screen.load_item(self.product_name)
            app.root.current = "basket_item"
            app.root.transition.direction = "left"
        return super().on_touch_up(touch)


class BasketScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def load_basket(self):
        products = read_products()
        self.ids.basket_container.clear_widgets()

        for name in basket:
            if name in products:
                info = products[name]

                row = BasketRow(
                    product_name=name,
                    product_price=info["price"],
                    product_volume=info["volume"],
                    quantity_box=info["quantity"],
                )
                self.ids.basket_container.add_widget(row)

    def goto_main(self):
        self.manager.current = "main"
        self.manager.transition.direction = "up"

    def goto_order(self):
        screen = self.manager.get_screen("order")
        screen.load_orders()
        self.manager.current = "order"
        self.manager.transition.direction = "up"


class BasketItemScreen(Screen):
    product_name = StringProperty("")
    product_image = StringProperty("")

    def load_item(self, name):
        products = read_products()

        self.product_name = name
        self.product_image = RESOURCES[name]

        if name in products:
            self.quantity_box = products[name]["quantity"]

    def goto_basket(self):
        screen = self.manager.get_screen("basket")
        screen.load_basket()
        self.manager.current = "basket"
        self.manager.transition.direction = "right"


class ProductScreen(Screen):
    product_name = StringProperty("")
    product_image = StringProperty("")
    product_quantity = StringProperty("0")
    product_price = StringProperty("")
    product_volume = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)

    def write_products(self, products):
        with open(PATH_DATA + "list_products.json", "w", encoding="utf8") as file:
            json.dump(products, file, ensure_ascii=False, indent=4)

    def load_product(self, name):
        products = read_products()

        self.product_name = name
        self.product_image = RESOURCES[self.product_name]
        self.product_quantity = "0"
        self.product_price = ""
        self.product_volume = ""

        if name in products:
            info = products[name]
            self.product_quantity = info["quantity"]
            self.product_price = info["price"]
            self.product_volume = info["volume"]

    def save_quantity(self):
        products = read_products()

        if self.product_name in products:
            products[self.product_name]["quantity"] = self.product_quantity

        self.write_products(products)

    def add_quantity(self):
        quantity = int(self.product_quantity)
        quantity += 1

        self.product_quantity = str(quantity)
        self.save_quantity()

    def delete_quantity(self):
        quantity = int(self.product_quantity)
        if quantity >= 1:
            quantity -= 1

            self.product_quantity = str(quantity)
            self.save_quantity()

    def delete_product(self):
        products = read_products()

        if self.product_name in products:
            del products[self.product_name]

        self.write_products(products)

        if self.product_name in basket:
            basket.remove(self.product_name)

        self.goto_main()

    def goto_main(self):
        self.manager.current = "main"
        self.manager.transition.direction = "down"


class MenuScreen(Screen):
    def goto_main(self):
        reset_quantities()
        self.manager.current = "main"
        self.manager.transition.direction = "up"


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.load_resources()

    def load_resources(self):
        with open(PATH_DATA + "list_resources.json", "r", encoding="utf8") as file:
            data = json.load(file)
            RESOURCES.update(data)

    def load_products(self):
        products = read_products()
        self.ids.main_container.clear_widgets()
        cb_active = False

        for name in products:
            if name in basket:
                cb_active = True
            else:
                cb_active = False

            bl = BoxRow(
                product_name=name,
                product_price=products[name]["price"],
                product_volume=products[name]["volume"],
                product_quantity=products[name]["quantity"],
                cb_active=cb_active,
            )

            self.ids.main_container.add_widget(bl)

    def on_pre_enter(self, *args):
        self.load_products()
        return super().on_pre_enter(*args)

    def goto_main(self):
        self.manager.current = "menu"
        self.manager.transition.direction = "up"

    def goto_basket(self):
        screen = self.manager.get_screen("basket")
        screen.load_basket()
        self.manager.current = "basket"
        self.manager.transition.direction = "down"


class Order(Screen):
    total_price = StringProperty("0")
    buyer_name = StringProperty("")
    buyer_surname = StringProperty("")
    pack_order = BooleanProperty(False)
    total_volume = StringProperty("0")
    volume_fits = BooleanProperty(True)
    volume_status = StringProperty("")
    box_count_status = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.get_volume_products()

    def buyer_details(self, key: str, text: str):
        if key == "name":
            self.buyer_name = text
        elif key == "Фамилия":
            self.buyer_surname = text

    def get_full_name(self):
        full_name = f"{self.buyer_name} {self.buyer_surname}".strip()
        return full_name

    def seller_id(self, full_name):
        sellers_path = PATH_DATA + "sellers.json"
        sellers = read_json(sellers_path)

        if full_name in sellers:
            return sellers[full_name]

        used_ids = []
        for seller in sellers:
            used_ids.append(sellers[seller])

        new_id = 1001
        while new_id in used_ids:
            new_id += 1

        sellers[full_name] = new_id
        write_json(sellers_path, sellers)
        return new_id

    def number_order(self):
        data = read_json(PATH_DATA + "orders.json")
        count = 0
        for seller in data:
            count += len(data[seller])
        return count + 1

    def goto_basket(self):
        screen = self.manager.get_screen("basket")
        screen.load_basket()
        self.manager.current = "basket"
        self.manager.transition.direction = "down"

    def toggle_packing(self, active):
        self.pack_order = active

        if active:
            box_quantity = self.fill_box()
            self.box_count_status = f"Используется коробок: {box_quantity}"
        else:
            self.box_count_status = ""

    def confirm_order(self):
        full_name = self.get_full_name()
        if not full_name:
            return False

        if self.pack_order and not self.volume_fits:
            return False

        items = {}

        seller_id = self.seller_id(full_name)
        date = datetime.now().strftime("%d.%m.%Y")
        order_number = self.number_order()

        orders_path = PATH_DATA + "orders.json"
        data = read_json(orders_path)
        seller_key = str(seller_id)
        if seller_key not in data:
            data[seller_key] = {}

        data[seller_key][date] = {
            "order_number": order_number,
            "items": items,
        }
        write_json(orders_path, data)

        products = read_products()
        receipt_items = []
        total = 0
        for name, box_count in items.items():
            if name in products:
                info = products[name]
                price = int(info["price"])
                quantity = int(info["quantity"])
                subtotal = price * quantity * box_count
                total += subtotal
                receipt_items.append(
                    {
                        "name": name,
                        "box_count": str(box_count),
                        "subtotal": str(subtotal),
                    }
                )

        confirm_screen = self.manager.get_screen("order_confirmed")
        confirm_screen.load_item(
            order_number=order_number,
            full_name=full_name,
            date=date,
            items=receipt_items,
            total=str(total),
        )

        basket.clear()
        self.buyer_name = ""
        self.buyer_surname = ""
        self.pack_order = False
        self.total_volume = "0"
        self.volume_fits = True

        self.manager.current = "order_confirmed"
        self.manager.transition.direction = "left"
        return True

    def load_orders(self):
        products = read_products()
        self.ids.order_products.clear_widgets()
        for name in basket:
            if name in products:
                info = products[name]

                row = OrderRow(
                    product_name=name,
                    product_price=info["price"],
                    product_volume=info["volume"],
                    quantity_box=info["quantity"],
                )
                self.ids.order_products.add_widget(row)

        self.total_price = self.sum_price()

    def sum_price(self) -> str:
        products = read_products()
        total = 0

        for name in basket:
            if name in products:
                total += int(products[name]["quantity"]) * int(products[name]["price"])

        return str(total)

    def get_volume_products(self):
        all_products = read_products()
        products = {}
        for name in basket:
            if name in all_products:
                products[name] = all_products[name]

        result = {}
        for name, item in products.items():
            quantity = int(item["quantity"])
            volume = int(item["volume"])
            result[name] = {
                "quantity": quantity,
                "volume": volume,
            }

        sorted_items = sorted(
            result.items(), key=lambda x: x[1]["volume"], reverse=True
        )
        return sorted_items

    def fill_box(self):
        box_volume = 10000
        box_quantity = 1
        product_items = self.get_volume_products()

        while True:
            placed = False

            for name, data in product_items:
                if data["quantity"] > 0 and data["volume"] <= box_volume:
                    box_volume -= data["volume"]
                    data["quantity"] -= 1
                    placed = True
                    break

            if placed:
                continue

            remaining = False
            for name, data in product_items:
                if data["quantity"] > 0:
                    remaining = True
                    break
            if not remaining:
                break

            box_quantity += 1
            box_volume = 10000

        return box_quantity


class OrderConfirmedScreen(Screen):
    order_number = StringProperty("")
    buyer_full_name = StringProperty("")
    order_date = StringProperty("")
    total_price = StringProperty("0")

    def load_item(self, order_number, full_name, date, items, total):
        self.order_number = str(order_number)
        self.buyer_full_name = full_name
        self.order_date = date
        self.total_price = total

    def goto_main(self):
        self.manager.current = "main"
        self.manager.transition.direction = "up"


class CompositionApp(App):
    resources = RESOURCES

    def build(self):
        self.scr_sm = ScreenManager()
        self.scr_sm.add_widget(MenuScreen(name="menu"))
        self.scr_sm.add_widget(MainScreen(name="main"))
        self.scr_sm.add_widget(ProductScreen(name="product_screen"))
        self.scr_sm.add_widget(BasketScreen(name="basket"))
        self.scr_sm.add_widget(BasketItemScreen(name="basket_item"))
        self.scr_sm.add_widget(Order(name="order"))
        self.scr_sm.add_widget(OrderConfirmedScreen(name="order_confirmed"))

        if platform == "android":
            Window.clearcolor = (0.0, 0.0, 0.0, 1)
            Window.fullscreen = True
        else:
            Window.size = (350, 700)
            Window.clearcolor = (0, 0, 0, 1)
            Window.left = 450
            Window.top = 1

        Builder.load_file("composition.kv")
        return self.scr_sm


if __name__ == "__main__":
    CompositionApp().run()
    print("Hello")
