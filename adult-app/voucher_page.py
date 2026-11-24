"""
voucher_page.py - the Vouchers tab: exchange points for demo vouchers.

Top: the MAIN reward, a doctor consultation, in a highlighted box.
Middle: the price-off vouchers. Three buttons (Pharmacy, Equipment,
Food swaps) choose which group is shown.
Bottom: "My vouchers", the ones already claimed, with their code.

Everything here is a mock-up. The list is in vouchers.py.
"""

import tkinter as tk
from tkinter import ttk

import fun
import state_store
import vouchers
from app_pages import nice_time, GREEN, RED, GREY

HIGHLIGHT = "#fff1c2"        # soft yellow behind the main reward
HIGHLIGHT_EDGE = "#e0a800"


class VoucherPage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, padx=12, pady=6)
        tk.Label(self.frame, text="Vouchers",
                 font=("Arial", 13, "bold")).pack(anchor="w")
        # Honest label: nothing here is real yet.
        tk.Label(self.frame,
                 text="DEMO ONLY. Vendors and prices are not confirmed. The "
                      "codes are made up, nothing is booked. A parent or "
                      "guardian would use the voucher.",
                 fg=RED, wraplength=450, justify="left",
                 font=("Arial", 8)).pack(anchor="w")

        self.points = tk.Label(self.frame, text="", font=("Arial", 13, "bold"),
                               fg=GREEN)
        self.points.pack(anchor="w", pady=(2, 2))
        self.points_count = fun.CountUp(self.points, "You have %d points")

        self.buttons = {}          # voucher id -> (button, cost)

        # ---- The main reward, highlighted ----
        main_box = tk.Frame(self.frame, bg=HIGHLIGHT, padx=8, pady=5,
                            highlightthickness=2,
                            highlightbackground=HIGHLIGHT_EDGE)
        main_box.pack(fill="x")
        tk.Label(main_box, text="MAIN REWARD: SEE A DOCTOR", bg=HIGHLIGHT,
                 font=("Arial", 10, "bold")).grid(row=0, column=0,
                                                  columnspan=3, sticky="w")
        row = 1
        for voucher_id, kind, title, _note, cost in vouchers.VOUCHERS:
            if kind != vouchers.MAIN_KIND:
                continue
            tk.Label(main_box, text=title, bg=HIGHLIGHT, anchor="w", width=34,
                     font=("Arial", 10, "bold")).grid(row=row, column=0,
                                                      sticky="w", pady=2)
            tk.Label(main_box, text="%d pts" % cost, bg=HIGHLIGHT, width=7,
                     anchor="e", font=("Arial", 10)).grid(row=row, column=1)
            button = tk.Button(main_box, text="Claim", width=7,
                               font=("Arial", 9, "bold"),
                               command=lambda v=voucher_id: self.claim(v))
            button.grid(row=row, column=2, padx=6)
            self.buttons[voucher_id] = (button, cost)
            row += 1

        # ---- The price-off vouchers, one group at a time ----
        self.kind = tk.StringVar(value=vouchers.kinds()[0])
        bar = tk.Frame(self.frame)
        bar.pack(anchor="w", pady=(8, 2))
        tk.Label(bar, text="Price off:").pack(side="left")
        for kind in vouchers.kinds():
            tk.Radiobutton(bar, text=kind, value=kind, width=11,
                           variable=self.kind, indicatoron=False,
                           command=self.show_kind).pack(side="left", padx=2)
        self.rows = tk.Frame(self.frame, height=150)
        self.rows.pack(anchor="w", fill="x")
        self.rows.grid_propagate(False)      # keep the page from jumping
        self.other_ids = []

        self.message = tk.Label(self.frame, text="", wraplength=450,
                                justify="left")
        self.message.pack(anchor="w")

        tk.Label(self.frame, text="My vouchers",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.table = ttk.Treeview(self.frame, show="headings", height=3,
                                  columns=("title", "code", "when"))
        for key, title, width in (("title", "Voucher", 215),
                                  ("code", "Demo code", 140),
                                  ("when", "Claimed", 95)):
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="w")
        self.table.pack(pady=2)
        self.last_seen = None
        self.show_kind()

    def show_kind(self):
        """Build the rows of the chosen group."""
        for old in self.rows.winfo_children():
            old.destroy()
        for voucher_id in self.other_ids:
            self.buttons.pop(voucher_id, None)
        self.other_ids = []
        row = 0
        for voucher_id, kind, title, note, cost in vouchers.VOUCHERS:
            if kind != self.kind.get():
                continue
            tk.Label(self.rows, text=title, anchor="w", width=29,
                     font=("Arial", 9)).grid(row=row, column=0, sticky="w")
            # A short note, e.g. "instead of white rice".
            tk.Label(self.rows, text=note, anchor="w", fg=GREEN, width=23,
                     font=("Arial", 7)).grid(row=row, column=1, sticky="w")
            tk.Label(self.rows, text="%d pts" % cost, width=6,
                     anchor="e").grid(row=row, column=2)
            button = tk.Button(self.rows, text="Claim", width=6,
                               font=("Arial", 7), pady=0,
                               command=lambda v=voucher_id: self.claim(v))
            button.grid(row=row, column=3, padx=6)
            self.buttons[voucher_id] = (button, cost)
            self.other_ids.append(voucher_id)
            row += 1
        self.refresh(state_store.load_state())

    def claim(self, voucher_id):
        ok, message, code = vouchers.claim(voucher_id)
        self.message.config(text=message, fg=GREEN if ok else RED)
        self.refresh(state_store.load_state())
        if ok:
            fun.celebrate(self.frame, "Voucher claimed!",
                          "Demo code: %s" % code)

    def refresh(self, state):
        balance = state["points"]["balance"]
        self.points_count.set(balance)             # counts up or down
        for button, cost in self.buttons.values():
            fun.set_enabled(button, balance >= cost)

        claimed = state["vouchers"]
        seen = (len(claimed), claimed[-1]["code"] if claimed else None)
        if seen == self.last_seen:
            return
        self.last_seen = seen
        self.table.delete(*self.table.get_children())
        for voucher in reversed(claimed):                # newest first
            self.table.insert("", "end", values=(
                voucher.get("title", ""), voucher.get("code", ""),
                nice_time(voucher.get("claimed_at"))))
