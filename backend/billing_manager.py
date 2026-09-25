#!/usr/bin/env python3
"""
Billing Manager - ระบบจัดการการเรียกเก็บเงิน
Handles clients, invoices, payments, PDF generation & exports — Interactive Console
"""

import os
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Any
from decimal import Decimal, ROUND_HALF_UP
import uuid

# Optional: PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("billing_manager.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration & Paths / การตั้งค่าและที่อยู่ไฟล์"""
    BASE_DIR = Path("./billing_data")
    CLIENTS_FILE = BASE_DIR / "clients.json"
    INVOICES_FILE = BASE_DIR / "invoices.json"
    PDF_DIR = BASE_DIR / "invoices_pdf"
    EXPORT_DIR = BASE_DIR / "exports"

    @classmethod
    def init_dirs(cls):
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.PDF_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORT_DIR.mkdir(parents=True, exist_ok=True)


class ClientManager:
    """Client Management / ระบบจัดการลูกค้า"""

    def __init__(self):
        self.clients: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if Config.CLIENTS_FILE.exists():
            with open(Config.CLIENTS_FILE, "r", encoding="utf-8") as f:
                self.clients = json.load(f)
        else:
            self.clients = []

    def _save(self):
        with open(Config.CLIENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.clients, f, indent=2, ensure_ascii=False)

    def add_client(self, name_en: str, name_th: str = "", email: str = "",
                    phone: str = "", address: str = "", tax_id: str = "") -> Dict:
        client = {
            "id": str(uuid.uuid4())[:8],
            "name_en": name_en,
            "name_th": name_th,
            "email": email,
            "phone": phone,
            "address": address,
            "tax_id": tax_id,
            "created_at": datetime.now().isoformat()
        }
        self.clients.append(client)
        self._save()
        logger.info(f"✅ Client added / เพิ่มลูกค้า: {name_en}")
        return client

    def list_clients(self) -> List[Dict]:
        return self.clients

    def find_client(self, client_id: str) -> Optional[Dict]:
        return next((c for c in self.clients if c["id"] == client_id), None)

    def update_client(self, client_id: str, **kwargs) -> bool:
        client = self.find_client(client_id)
        if not client:
            return False
        for k, v in kwargs:
            if k in ["name_en", "name_th", "email", "phone", "address", "tax_id"]:
                client[k] = v
        self._save()
        logger.info(f"✏️ Client updated / แก้ไขลูกค้า: {client_id}")
        return True


class InvoiceManager:
    """Invoice & Payment Manager / ระบบจัดการใบแจ้งหนี้และการชำระเงิน"""

    VAT_RATE = Decimal("0.07")

    def __init__(self):
        self.invoices: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if Config.INVOICES_FILE.exists():
            with open(Config.INVOICES_FILE, "r", encoding="utf-8") as f:
                self.invoices = json.load(f)
        else:
            self.invoices = []

    def _save(self):
        with open(Config.INVOICES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.invoices, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _round_amount(val: Decimal) -> Decimal:
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def create_invoice(self, client_id: str, items: List[Dict],
                       due_date: str, notes: str = "", currency: str = "THB") -> Dict:
        inv_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{len(self.invoices)+1:04d}"
        subtotal = Decimal("0")
        for item in items:
            line_total = Decimal(str(item["qty"])) * Decimal(str(item["unit_price"]))
            subtotal += line_total
        vat = self._round_amount(subtotal * self.VAT_RATE)
        total = self._round_amount(subtotal + vat)
        invoice = {
            "invoice_no": inv_no,
            "client_id": client_id,
            "issued_date": date.today().isoformat(),
            "due_date": due_date,
            "status": "pending",
            "currency": currency,
            "items": items,
            "subtotal": float(subtotal),
            "vat_rate": float(self.VAT_RATE),
            "vat_amount": float(vat),
            "total": float(total),
            "notes": notes,
            "paid_amount": 0.0,
            "paid_date": None,
            "created_at": datetime.now().isoformat()
        }
        self.invoices.append(invoice)
        self._save()
        logger.info(f"📄 Invoice created / สร้างใบแจ้งหนี้: {inv_no} | Total: {total} {currency}")
        return invoice

    def record_payment(self, invoice_no: str, amount: float,
                       payment_date: Optional[str] = None, method: str = "transfer") -> bool:
        inv = next((i for i in self.invoices if i["invoice_no"] == invoice_no), None)
        if not inv:
            logger.warning(f"⚠️ Invoice not found / ไม่พบใบแจ้งหนี้: {invoice_no}")
            return False
        inv["paid_amount"] += amount
        inv["paid_date"] = payment_date or date.today().isoformat()
        if inv["paid_amount"] >= inv["total"]:
            inv["status"] = "paid"
            logger.info(f"✅ Fully paid / ชำระครบถ้วน: {invoice_no}")
        else:
            inv["status"] = "partially_paid"
            logger.info(f"💰 Partial payment / ชำระบางส่วน: {invoice_no}")
        inv["payment_method"] = method
        self._save()
        return True

    def update_statuses(self):
        today = date.today().isoformat()
        updated = 0
        for inv in self.invoices:
            if inv["status"] in ("pending", "partially_paid") and inv["due_date"] < today:
                inv["status"] = "overdue"
                updated += 1
        if updated:
            self._save()
            logger.info(f"📌 Marked {updated} invoices as overdue")

    def get_invoice(self, invoice_no: str) -> Optional[Dict]:
        return next((i for i in self.invoices if i["invoice_no"] == invoice_no), None)

    def list_by_status(self, status: str) -> List[Dict]:
        return [i for i in self.invoices if i["status"] == status]

    def get_summary(self) -> Dict:
        total_issued = sum(i["total"] for i in self.invoices)
        total_paid = sum(i["paid_amount"] for i in self.invoices)
        pending = sum(i["total"] - i["paid_amount"] for i in self.list_by_status("pending"))
        overdue = sum(i["total"] - i["paid_amount"] for i in self.list_by_status("overdue"))
        return {
            "total_invoices": len(self.invoices),
            "total_issued": round(total_issued, 2),
            "total_paid": round(total_paid, 2),
            "pending_amount": round(pending, 2),
            "overdue_amount": round(overdue, 2),
            "paid_count": len(self.list_by_status("paid")),
            "pending_count": len(self.list_by_status("pending")),
            "overdue_count": len(self.list_by_status("overdue"))
        }

    def export_to_csv(self, filepath: Optional[Path] = None) -> Path:
        if not filepath:
            filepath = Config.EXPORT_DIR / f"invoices_{datetime.now().strftime('%Y%m%d')}.csv"
        import csv
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Invoice No.", "Client ID", "Issued Date", "Due Date",
                "Status", "Currency", "Subtotal", "VAT", "Total",
                "Paid Amount", "Paid Date"
            ])
            for inv in self.invoices:
                writer.writerow([
                    inv["invoice_no"], inv["client_id"], inv["issued_date"], inv["due_date"],
                    inv["status"], inv["currency"], inv["subtotal"], inv["vat_amount"],
                    inv["total"], inv["paid_amount"], inv.get("paid_date", "")
                ])
        logger.info(f"📤 Exported to: {filepath}")
        return filepath

    def generate_pdf(self, invoice_no: str, client: Dict) -> Optional[Path]:
        if not REPORTLAB_AVAILABLE:
            logger.warning("⚠️ Install reportlab: pip install reportlab")
            return None
        inv = self.get_invoice(invoice_no)
        if not inv:
            return None
        pdf_path = Config.PDF_DIR / f"{invoice_no}.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph(f"INVOICE / ใบแจ้งหนี้", styles["Title"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"Number / เลขที่: {inv['invoice_no']}", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        name_line = client['name_en']
        if client.get("name_th"):
            name_line += f" — {client['name_th']}"
        elements.append(Paragraph(f"<b>To / ถึง:</b><br/>{name_line}<br/>{client.get('email', '')}<br/>{client.get('address', '')}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Issued / วันที่ออก: {inv['issued_date']}<br/>Due / กำหนดชำระ: {inv['due_date']}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        data = [["Description / รายการ", "Qty / จำนวน", "Unit / ราคา/หน่วย", "Total / รวม"]]
        for item in inv["items"]:
            line_total = Decimal(str(item["qty"])) * Decimal(str(item["unit_price"]))
            data.append([item["desc"], item["qty"], f"{item['unit_price']:.2f}", f"{line_total:.2f}"])
        data.extend([
            ["", "", "Subtotal / มูลค่าก่อนภาษี", f"{inv['subtotal']:.2f}"],
            ["", "", "VAT 7% / ภาษีมูลค่าเพิ่ม", f"{inv['vat_amount']:.2f}"],
            ["", "", "TOTAL / รวมทั้งสิ้น", f"{inv['total']:.2f} {inv['currency']}"]
        ])
        table = Table(data, colWidths=[280, 60, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("BACKGROUND", (0, -3), (-1, -1), colors.lightgrey),
            ("FONTWEIGHT", (0, -1), (-1, -1), "bold"),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        if inv["notes"]:
            elements.append(Paragraph(f"<b>Notes / หมายเหตุ:</b><br/>{inv['notes']}", styles["Normal"]))
        doc.build(elements)
        logger.info(f"📄 PDF generated: {pdf_path}")
        return pdf_path


# ─── CONSOLE MENU ────────────────────────────────────────────────
class ConsoleMenu:
    """Interactive Console / เมนูแบบโต้ตอบทางคอนโซล"""

    def __init__(self):
        Config.init_dirs()
        self.client_mgr = ClientManager()
        self.invoice_mgr = InvoiceManager()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        self.clear_screen()
        print("=" * 65)
        print(f"  {title}")
        print("=" * 65)

    def show_summary(self):
        self.invoice_mgr.update_statuses()
        s = self.invoice_mgr.get_summary()
        print("\n📊 Financial Summary / สรุปยอดการเงิน")
        print(f"   Total Invoices / ใบทั้งหมด: {s['total_invoices']}")
        print(f"   Total Issued / ยอดออก:     {s['total_issued']:,.2f} THB")
        print(f"   Paid / ชำระแล้ว:           {s['total_paid']:,.2f} THB  ({s['paid_count']})")
        print(f"   Pending / ค้างชำระ:        {s['pending_amount']:,.2f} THB  ({s['pending_count']})")
        print(f"   Overdue / เกินกำหนด:       {s['overdue_amount']:,.2f} THB  ({s['overdue_count']})")

    def menu_clients(self):
        while True:
            self.print_header("👤 Client Management / จัดการลูกค้า")
            print("\n  1. Add New Client / เพิ่มลูกค้า")
            print("  2. List All Clients / แสดงรายการ")
            print("  3. Back / กลับ")
            opt = input("\nEnter choice / เลือก: ").strip()

            if opt == "1":
                print("\n── Add Client ──")
                name_en = input("Name EN: ").strip()
                name_th = input("Name TH: ").strip()
                email = input("Email: ").strip()
                phone = input("Phone: ").strip()
                address = input("Address: ").strip()
                tax_id = input("Tax ID: ").strip()
                if name_en:
                    client = self.client_mgr.add_client(name_en, name_th, email, phone, address, tax_id)
                    print(f"✅ Added. ID: {client['id']}")
                input("\nPress Enter to continue...")

            elif opt == "2":
                clients = self.client_mgr.list_clients()
                print("\n── Clients ──")
                if not clients:
                    print("  No clients yet.")
                for c in clients:
                    print(f"  {c['id']} | {c['name_en']} | {c.get('name_th','-')} | {c.get('email','-')}")
                input("\nPress Enter to continue...")

            elif opt == "3":
                break

    def menu_invoices(self):
        while True:
            self.print_header("📄 Invoice Management / จัดการใบแจ้งหนี้")
            print("\n  1. Create Invoice / สร้างใบ")
            print("  2. List All / แสดงทั้งหมด")
            print("  3. By Status / ตามสถานะ")
            print("  4. Record Payment / บันทึกชำระ")
            print("  5. Generate PDF / สร้าง PDF")
            print("  6. Export CSV / ส่งออก CSV")
            print("  7. Back / กลับ")
            opt = input("\nEnter choice / เลือก: ").strip()

            if opt == "1":
                print("\n── Create Invoice ──")
                client_id = input("Client ID: ").strip()
                if not self.client_mgr.find_client(client_id):
                    print("❌ Client not found.")
                    input("Enter...")
                    continue
                due_date = input("Due Date (YYYY-MM-DD): ").strip()
                if not due_date:
                    due_date = input("Due Date: ").strip()
                items = []
                while True:
                    desc = input("Item desc (empty=done): ").strip()
                    if not desc:
                        break
                    qty = float(input("  Qty: "))
                    price = float(input("  Unit price: "))
                    items.append({"desc": desc, "qty": qty, "unit_price": price})
                if items:
                    inv = self.invoice_mgr.create_invoice(client_id, items, due_date)
                    print(f"✅ Created: {inv['invoice_no']} | Total: {inv['total']}")
                input("\nPress Enter...")

            elif opt == "2":
                self.invoice_mgr.update_statuses()
                print("\n── All Invoices ──")
                for inv in self.invoice_mgr.invoices:
                    print(f"  {inv['invoice_no']} | {inv['status']:15} | {inv['total']:>10,.2f} | Due: {inv['due_date']}")
                input("\nPress Enter...")

            elif opt == "3":
                status = input("Status (pending/paid/overdue): ").strip().lower()
                found = self.invoice_mgr.list_by_status(status)
                print(f"\n── {status} ({len(found)}) ──")
                for inv in found:
                    print(f"  {inv['invoice_no']} | {inv['total']:,.2f} | {inv['due_date']}")
                input("\nPress Enter...")

            elif opt == "4":
                inv_no = input("Invoice No.: ").strip()
                amount = float(input("Amount: "))
                method = input("Method (transfer/cash): ").strip() or "transfer"
                if self.invoice_mgr.record_payment(inv_no, amount, method=method):
                    print("✅ Payment recorded.")
                input("Press Enter...")

            elif opt == "5":
                inv_no = input("Invoice No.: ").strip()
                inv = self.invoice_mgr.get_invoice(inv_no)
                if not inv:
                    print("❌ Not found.")
                else:
                    client = self.client_mgr.find_client(inv["client_id"])
                    if client:
                        path = self.invoice_mgr.generate_pdf(inv_no, client)
                        if path:
                            print(f"✅ PDF: {path}")
                input("Press Enter...")

            elif opt == "6":
                path = self.invoice_mgr.export_to_csv()
                print(f"✅ Exported: {path}")
                input("Press Enter...")

            elif opt == "7":
                break

    def run(self):
        while True:
            self.print_header("🏠 Billing Manager / ระบบจัดการการเรียกเก็บเงิน")
            self.show_summary()
            print("\n── Main Menu ──")
            print("  1. Clients / ลูกค้า")
            print("  2. Invoices / ใบแจ้งหนี้")
            print("  0. Exit / ออก")
            choice = input("\nSelect / เลือก: ").strip()

            if choice == "1":
                self.menu_clients()
            elif choice == "2":
                self.menu_invoices()
            elif choice == "0":
                print("👋 Goodbye / ลาก่อน!")
                break
