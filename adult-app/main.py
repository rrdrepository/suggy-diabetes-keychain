"""
main.py - the companion app (prototype).

Run it from the adult-app folder with:  python main.py

The app has tabs:
    Home      hello, points, Suggy and the insulin reminder times
    Feeding   the saved feedings
    Insulin   a parent sets the reminder times; shows what the kid pressed
    Shop      spend points on cosmetics for Suggy
    Vouchers  exchange points for demo vouchers
    Quiz      5 questions a day about diabetes
    Link      link (or unlink) the keychain

The keychain is for kids aged 6 to 14. This app is looked after by a
parent or guardian, together with the child.

Without linking there is no app experience: only the Link tab can be
opened, and the keychain is just an educational pet toy. Linking (IC
number + keychain reference number) opens the other tabs.

The look and the animations (the banner with Suggy, numbers that count
up, confetti, buttons that light up) are in fun.py.

The app re-reads data/state.json every second, so whatever happens on
the keychain shows up here, and a cosmetic bought here shows up there.
"""

import tkinter as tk
from tkinter import ttk

import fun
import state_store
from app_pages import HomePage, FeedingPage
from insulin_page import InsulinPage
from link_screen import LinkScreen
from quiz_page import QuizPage
from shop_page import ShopPage
from voucher_page import VoucherPage

CHECK_EVERY_MS = 1000   # how often we re-read state.json


class CompanionApp:
    def __init__(self, root):
        self.root = root
        root.title("Companion app - prototype")
        root.resizable(False, False)

        # The friendly look (colours, tabs, buttons that light up).
        # This must come before any other widget is made.
        fun.apply_theme(root)

        # Honest label: this is a prototype, not a medical product.
        tk.Label(root, text="PROTOTYPE - demo only, not a medical device",
                 font=("Arial", 9), fg="#6b6b6b").pack(pady=(4, 2))
        # The banner: Suggy, the title, who the app is for (kids aged 6
        # to 14, with a parent looking after it) and the points.
        self.header = fun.Header(root)

        self.tabs = ttk.Notebook(root, width=480, height=520)
        self.tabs.pack(padx=10, pady=8)

        # The pages that need a linked keychain.
        self.pages = [HomePage(self.tabs), FeedingPage(self.tabs),
                      InsulinPage(self.tabs), ShopPage(self.tabs),
                      VoucherPage(self.tabs), QuizPage(self.tabs)]
        for page, title in zip(self.pages, ("Home", "Feeding", "Insulin",
                                            "Shop", "Vouchers", "Quiz")):
            self.tabs.add(page.frame, text=title)

        # The Link tab is always there.
        self.link_tab = tk.Frame(self.tabs)
        self.tabs.add(self.link_tab, text="Link")
        LinkScreen(self.link_tab)

        self.was_linked = None
        self.last_balance = None   # to notice when points are earned
        self.check_for_changes()

    def check_for_changes(self):
        """Runs every second: re-read the data and update every page."""
        state = state_store.load_state()

        linked = state["link"]["linked"]
        if linked != self.was_linked:
            # Linking opens the other tabs; unlinking closes them again.
            for page in self.pages:
                self.tabs.tab(page.frame,
                              state="normal" if linked else "disabled")
            self.tabs.select(self.pages[0].frame if linked else self.link_tab)
            self.was_linked = linked

        self.header.refresh(state)
        if linked:
            for page in self.pages:
                page.refresh(state)

        # Points went up (a light food choice on the keychain, or a right
        # quiz answer): celebrate with confetti.
        balance = state["points"]["balance"]
        if (linked and self.last_balance is not None
                and balance > self.last_balance):
            fun.celebrate(self.root,
                          "+%d points!" % (balance - self.last_balance),
                          "Well done!", state["pet"]["accessories"])
        self.last_balance = balance
        self.root.after(CHECK_EVERY_MS, self.check_for_changes)


def main():
    root = tk.Tk()
    CompanionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
