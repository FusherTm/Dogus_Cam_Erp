# Doğuş ERP

A desktop ERP (Enterprise Resource Planning) application built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). The project contains multiple modules for finance, inventory, invoices, personnel management and more. Data is stored in a PostgreSQL database.

## Directory layout

```
main.py            # Application entry point
database.py        # Database helper using PostgreSQL
envanter/          # Inventory management UI
muhasebe/          # Accounting/finance related UI
faturalar/         # Invoice management UI
personel/          # Personnel management UI
uretim/            # Work order tracking UI
temper/            # Temper order tracking UI
```

## Installation

Install the required Python packages:

```bash
pip install customtkinter tkcalendar
# Optional - for charts in the report screen
pip install matplotlib
```

## Usage

Run the main script to start the GUI:

```bash
python main.py
```

## Database file

The application expects a PostgreSQL database named `dogus_erp_db` and a user `dogus_erp_user` (password `Dogus1234`). Ensure the database is created before running the program.
