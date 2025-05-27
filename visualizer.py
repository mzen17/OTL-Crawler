import sqlite3
import tkinter as tk
from tkinter import ttk

DB_PATH = 'datadir/crawl-data.sqlite'

# switch to extension_messages
TABLE_NAME = 'extension_messages'

# columns in extension_messages
COLUMNS = [
    'id',                       # the PK
    'ts',                       # timestamp
    'browser_id',
    'extension_session_uuid',
    'command_sequence_id',
    'type',                     # should be 'js_result' for your entries
    'value'                     # the JS return value
]

class DataExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenWPM Data Explorer")
        self.geometry("1200x600")
        self.conn = sqlite3.connect(DB_PATH)

        # === Filters Frame ===
        filter_frame = ttk.LabelFrame(self, text="Filters (comma-separated)")
        filter_frame.pack(fill='x', padx=5, pady=5)

        # now include the fields you actually have in extension_messages
        filter_cols = ['id', 'browser_id', 'extension_session_uuid', 'command_sequence_id', 'type']
        self.filters = {}
        for col in filter_cols:
            lbl = ttk.Label(filter_frame, text=col)
            ent = ttk.Entry(filter_frame, width=20)
            lbl.pack(side='left', padx=2)
            ent.pack(side='left', padx=2)
            self.filters[col] = ent

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).pack(side='left', padx=5)

        # === Table ===
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show='headings')
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='w')

        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        # load data on startup
        self.apply_filters()

    def apply_filters(self):
        clauses = []
        params = []
        for col, ent in self.filters.items():
            text = ent.get().strip()
            if text:
                vals = [v.strip() for v in text.split(',') if v.strip()]
                ph = ','.join('?' for _ in vals)
                clauses.append(f"{col} IN ({ph})")
                params.extend(vals)

        query = f"SELECT {', '.join(COLUMNS)} FROM {TABLE_NAME}"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " LIMIT 1000;"

        cur = self.conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()

        # refresh tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert('', 'end', values=row)


if __name__ == "__main__":
    app = DataExplorer()
    app.mainloop()
