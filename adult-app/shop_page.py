"""
shop_page.py - the Shop tab: spend points on cosmetics for Suggy.

At the top: the points and Suggy as it looks now. Then three category
buttons (Head, Eyes, Neck). Each category shows 5 items, each with a
picture of Suggy wearing it, its price and one button:

    Buy       not owned yet (greyed out if the points are not enough)
    Wear      owned, but Suggy is not wearing it
    Take off  Suggy is wearing it

The list of items and prices is in shop.py.
"""

import tkinter as tk

import fun
import pet_drawing
import shop
import state_store
from app_pages import SuggyView, GREEN, RED, GREY


class ShopPage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=12, pady=8)
        tk.Label(self.frame, text="Shop",
                 font=("Arial", 13, "bold")).pack(anchor="w")
        # Honest label: the team has not decided the real shop yet.
        tk.Label(self.frame, text="Placeholder items and prices "
                 "(to be confirmed).", fg=GREY).pack(anchor="w")

        top = tk.Frame(self.frame)
        top.pack(fill="x", pady=(4, 0))
        self.suggy = SuggyView(top)
        self.suggy.canvas.pack(side="left")
        self.points = tk.Label(top, text="", font=("Arial", 15, "bold"),
                               fg=GREEN, justify="left")
        self.points.pack(side="left", padx=14)
        self.points_count = fun.CountUp(self.points, "You have\n%d points")

        # Category buttons.
        self.category = tk.StringVar(value=shop.SHOP[0][0])
        bar = tk.Frame(self.frame)
        bar.pack(anchor="w", pady=(10, 4))
        for name, _items in shop.SHOP:
            tk.Radiobutton(bar, text=name, value=name, width=10,
                           variable=self.category, indicatoron=False,
                           command=self.show_category).pack(side="left",
                                                            padx=2)

        self.cards = tk.Frame(self.frame)
        self.cards.pack(anchor="w")
        self.buttons = {}          # item id -> its button

        self.message = tk.Label(self.frame, text="", wraplength=430,
                                justify="left")
        self.message.pack(anchor="w", pady=(8, 0))
        self.show_category()

    def show_category(self):
        """Build the 5 item cards of the chosen category."""
        for old in self.cards.winfo_children():
            old.destroy()
        self.buttons = {}
        for name, items in shop.SHOP:
            if name != self.category.get():
                continue
            for column, (item_id, item_name, price) in enumerate(items):
                card = tk.Frame(self.cards, bg=fun.CARD, padx=3, pady=3,
                                highlightthickness=1,
                                highlightbackground="#e6cfae")
                card.grid(row=0, column=column, padx=2, sticky="n")
                # The picture: Suggy wearing just this item.
                picture = tk.Canvas(card, width=78, height=88,
                                    bg=pet_drawing.SCREEN_BG,
                                    highlightthickness=0)
                picture.pack()
                pet_drawing.draw_pet(picture, 41, 58, "happy",
                                     accessories=[item_id])
                tk.Label(card, text=item_name, font=("Arial", 8, "bold"),
                         wraplength=78, height=2, bg=fun.CARD).pack()
                tk.Label(card, text="%d points" % price, bg=fun.CARD,
                         font=("Arial", 8)).pack()
                button = tk.Button(card, text="Buy", width=8,
                                   font=("Arial", 8))
                button.pack(pady=(2, 0))
                self.buttons[item_id] = button
        self.refresh(state_store.load_state())

    def refresh(self, state):
        balance = state["points"]["balance"]
        self.points_count.set(balance)             # counts up or down
        self.suggy.refresh(state)
        owned = shop.owned_items(state)
        worn = state["pet"]["accessories"]
        for item_id, button in self.buttons.items():
            _category, _name, price = shop.find_item(item_id)
            if item_id in worn:
                button.config(text="Take off",
                              command=lambda i=item_id: self.take_off(i))
                fun.set_enabled(button, True)
            elif item_id in owned:
                button.config(text="Wear",
                              command=lambda i=item_id: self.wear(i))
                fun.set_enabled(button, True)
            else:
                button.config(text="Buy",
                              command=lambda i=item_id: self.buy(i))
                fun.set_enabled(button, balance >= price)

    def buy(self, item_id):
        ok, message = shop.buy(item_id)
        self.message.config(text=message, fg=GREEN if ok else RED)
        self.refresh(state_store.load_state())
        if ok:
            # A happy pop-up, with Suggy wearing the new item.
            _category, name, _price = shop.find_item(item_id)
            fun.celebrate(self.frame, "New look!", name, [item_id])

    def wear(self, item_id):
        shop.wear(item_id)
        self.message.config(text="")
        self.refresh(state_store.load_state())
        self.suggy.bouncer.jump()        # Suggy jumps to show it off

    def take_off(self, item_id):
        shop.take_off(item_id)
        self.message.config(text="")
        self.refresh(state_store.load_state())
