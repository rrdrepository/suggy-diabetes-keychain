"""
link_screen.py - the "Link your keychain" part of the companion app.

A parent or guardian types:
  1. the child's nickname (shown on the keychain as "Hello <nickname>!")
  2. the child's IC number (made-up for the demo)
  3. the reference number printed on the keychain
If the reference number matches, we save ONLY the nickname in
data/state.json. Nothing from the IC is saved: we only check that it
looks like a real IC number, then forget it.

The keychain window reads state.json every second, so it changes mode
by itself after linking.
"""

import tkinter as tk

import fun
import ic_check
import state_store

GREEN = "#2e7d32"
RED = "#b3261e"
GREY = "#6b6b6b"

# The keychain screen is tiny, so nicknames are kept short.
MAX_NICKNAME = 8


class LinkScreen:
    """Builds the link form inside the given parent frame."""

    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text=" Link your keychain ",
                                   padx=12, pady=10)
        self.frame.pack(fill="x", padx=12, pady=8)

        # ---- Nickname ----
        tk.Label(self.frame, text="Child's nickname").grid(row=0, column=0,
                                                   sticky="w")
        self.nick_entry = tk.Entry(self.frame, width=24)
        self.nick_entry.grid(row=0, column=1, sticky="w", pady=2)
        tk.Label(self.frame, text="Shown on the keychain: \"Hello Aiman!\" "
                 "(max %d letters)" % MAX_NICKNAME,
                 fg=GREY, font=("Arial", 8)).grid(row=1, column=1, sticky="w")

        # ---- IC number ----
        tk.Label(self.frame, text="Child's IC number").grid(row=2, column=0,
                                                    sticky="w")
        self.ic_entry = tk.Entry(self.frame, width=24)
        self.ic_entry.grid(row=2, column=1, sticky="w", pady=2)
        tk.Label(self.frame, text="Demo: use a made-up IC, e.g. 150301-10-1234",
                 fg=GREY, font=("Arial", 8)).grid(row=3, column=1, sticky="w")

        # ---- Keychain reference number ----
        tk.Label(self.frame, text="Keychain ref. no.").grid(row=4, column=0,
                                                            sticky="w")
        self.ref_entry = tk.Entry(self.frame, width=24)
        self.ref_entry.grid(row=4, column=1, sticky="w", pady=2)
        tk.Label(self.frame, text="Printed on the keychain, e.g. KC-4821",
                 fg=GREY, font=("Arial", 8)).grid(row=5, column=1, sticky="w")

        # ---- Buttons ----
        buttons = tk.Frame(self.frame)
        buttons.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 2))
        tk.Button(buttons, text="Link keychain",
                  command=self.link).pack(side="left")
        tk.Button(buttons, text="Unlink (demo)",
                  command=self.unlink).pack(side="left", padx=6)

        # Result message after pressing a button.
        self.message = tk.Label(self.frame, text="", wraplength=380,
                                justify="left")
        self.message.grid(row=7, column=0, columnspan=2, sticky="w")

        # Privacy note, always visible.
        tk.Label(self.frame,
                 text="For a parent or guardian to fill in. Privacy: the "
                      "IC number is never saved or sent anywhere.",
                 fg=GREY, font=("Arial", 8), wraplength=380,
                 justify="left").grid(row=8, column=0, columnspan=2,
                                      sticky="w", pady=(6, 0))

    # ---- Actions -----------------------------------------------------------

    def link(self):
        """Check the boxes, then save the link if everything is OK."""
        nickname = self.nick_entry.get().strip()
        if not nickname:
            self.show_message("Please type a nickname for the keychain "
                              "to greet your child with.", RED)
            return
        if len(nickname) > MAX_NICKNAME:
            self.show_message("Please use a nickname of up to %d letters."
                              % MAX_NICKNAME, RED)
            return

        error = ic_check.check_ic(self.ic_entry.get())
        if error:
            self.show_message(error, RED)
            return

        state = state_store.load_state()
        typed_ref = self.ref_entry.get().strip().upper()
        if typed_ref != state["keychain_ref"].upper():
            self.show_message("That reference number doesn't match this "
                              "keychain. Please check the number on it.", RED)
            return

        def save_link(s):
            s["link"]["linked"] = True
            s["link"]["linked_at"] = state_store.now_text()
            s["link"]["nickname"] = nickname
        state_store.update_state(save_link)

        # Forget the IC straight away: clear the box.
        self.ic_entry.delete(0, "end")

        self.show_message("Linked! The keychain will say Hello %s, and "
                          "data from this app will show on it." % nickname,
                          GREEN)
        fun.celebrate(self.frame, "Linked!", "Hello %s!" % nickname)

    def unlink(self):
        """Demo button: remove the link so the flow can be shown again."""
        def clear_link(s):
            s["link"]["linked"] = False
            s["link"]["linked_at"] = None
            s["link"]["nickname"] = None
        state_store.update_state(clear_link)
        self.show_message("Unlinked. The keychain works offline as before.",
                          GREY)

    # ---- Display -----------------------------------------------------------

    def show_message(self, text, colour):
        self.message.config(text=text, fg=colour)
