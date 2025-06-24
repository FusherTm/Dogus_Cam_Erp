diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..9c0a83a80f7860c64ca1369b33408f2a9db1701d
--- /dev/null
+++ b/README.md
@@ -0,0 +1,39 @@
+# Doğuş ERP
+
+A desktop ERP (Enterprise Resource Planning) application built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). The project contains multiple modules for finance, inventory, invoices, personnel management and more. Data is stored in a local SQLite database.
+
+## Directory layout
+
+```
+main.py            # Application entry point
+database.py        # SQLite helper used across the modules
+envanter/          # Inventory management UI
+muhasebe/          # Accounting/finance related UI
+faturalar/         # Invoice management UI
+personel/          # Personnel management UI
+uretim/            # Work order tracking UI
+temper/            # Temper order tracking UI
+erp_database.db    # Default database file
+```
+
+## Installation
+
+Install the required Python packages:
+
+```bash
+pip install customtkinter tkcalendar
+# Optional - for charts in the report screen
+pip install matplotlib
+```
+
+## Usage
+
+Run the main script to start the GUI:
+
+```bash
+python main.py
+```
+
+## Database file
+
+The repository includes a pre-populated `erp_database.db` SQLite file which contains sample tables and data. You may keep using it, or delete/rename the file to start with a fresh database (it will be recreated automatically on first run).
