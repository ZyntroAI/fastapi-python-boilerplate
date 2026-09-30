
Manifest Schema (manifest.json): ข้อมูลพื้นฐานของปลั๊กอิน
{
  "id": "data-editor-helper",
  "name": "Data & Editor Helper",
  "version": "1.0.0",
  "minAppVersion": "1.4.0",
  "description": "แปลงข้อมูล CSV/JSON และเพิ่มเครื่องมือช่วยแก้ไข",
  "author": "YourName",
  "isDesktopOnly": false
}
Settings Schema (การตั้งค่า): กำหนด Interface สำหรับเก็บค่าการตั้งค่าของผู้ใช้ (มักเก็บใน data.json)
interface PluginSettings {
  defaultFolderPath: string;      // โฟลเดอร์ปลายทางสำหรับไฟล์ที่แปลง
  enableAutoFormat: boolean;      // เปิดใช้งานการจัดรูปแบบอัตโนมัติ
  csvDelimiter: string;           // ตัวคั่นข้อมูล CSV (เช่น ",", ";")
  toolbarPosition: "top" | "bottom"; // ตำแหน่งของแถบเครื่องมือช่วยแก้ไข
}
const DEFAULT_SETTINGS: PluginSettings = { /* ... */ };
Data/Frontmatter Schema: โครงสร้างข้อมูลที่จะถูกแปลงเป็น Markdown (เช่น การแปลง Column ใน CSV ให้เป็น YAML Frontmatter)
---
id: "123"
title: "ชื่อเรื่อง"
tags: ["imported", "data"]
createdAt: "2026-09-30"
---
2. Core Features (คุณสมบัติหลัก)
ฟีเจอร์หลักที่ปลั๊กอินนี้จะมอบให้กับผู้ใช้ Obsidian

Data Import & Conversion:
รองรับการใช้งานไฟล์ CSV, JSON หรือ API Response
แปลงข้อมูลแต่ละแถว (Row) หรือออบเจกต์ (Object) ให้กลายเป็นไฟล์ Markdown แยกกันอัตโนมัติ
จับคู่ (Map) คอลัมน์ข้อมูลกับ YAML Frontmatter ของ Obsidian
Editor Enhancement (ตัวช่วยแก้ไข):
Custom Toolbar: แถบเครื่องมือแบบ Floating หรือ Fixed สำหรับแทรก Markdown Syntax (Bold, Italic, Table, Code Block) ได้ด้วยการคลิกเดียว
Text Snippets: ระบบแทรกข้อความสำเร็จรูป (เช่น วันที่ปัจจุบัน, Template โครงสร้างบทความ)
Auto-Formatting: จัดระยะห่าง, แปลง Text เป็น Table, หรือจัดระเบียบ List อัตโนมัติ
UI/UX Integration:
ปุ่ม Ribbon Icon สำหรับเรียกใช้งานด่วน
Command Palette (Ctrl/Cmd + P) สำหรับสั่งงานทุกฟังก์ชัน
Modal Dialog สำหรับแสดงตัวอย่างข้อมูล (Preview) ก่อนทำการแปลง
3. Core Functions (ฟังก์ชันการทำงานหลัก)
ฟังก์ชันสำคัญที่ต้องเขียนโดยใช้ Obsidian API และ TypeScript

import { Plugin, Notice, TFile, TFolder, Editor } from "obsidian";

export default class MyPlugin extends Plugin {
    settings: PluginSettings;

    // 1. Lifecycle: เริ่มต้นและทำลายปลั๊กอิน
    async onload() {
        await this.loadSettings();
        this.addRibbonIcon("database", "Import Data", () => this.importData());
        this.addCommand({ id: "open-toolbar", name: "Toggle Editor Toolbar", callback: () => this.toggleToolbar() });
        this.addSettingTab(new MySettingTab(this.app, this));
    }

    onunload() {
        // ทำความสะอาด Event Listeners หรือ UI ที่เพิ่มเข้ามา
    }

    // 2. Data Processing: ฟังก์ชันแปลงข้อมูล
    async convertCSVToNotes(csvContent: string): Promise<void> {
        const rows = this.parseCSV(csvContent, this.settings.csvDelimiter);
        for (const row of rows) {
            const fileName = `${row.title || "Untitled"}.md`;
            const content = this.generateMarkdown(row);
            
            // สร้างไฟล์ใน Vault
            await this.app.vault.create(`${this.settings.defaultFolderPath}/${fileName}`, content);
        }
        new Notice("แปลงข้อมูลเสร็จสิ้น!");
    }

    // 3. Editor Manipulation: ฟังก์ชันช่วยแก้ไข
    insertTextAtCursor(editor: Editor, text: string) {
        const cursor = editor.getCursor();
        editor.replaceRange(text, cursor);
        editor.setCursor({ line: cursor.line, ch: cursor.ch + text.length });
    }

    // Helper Functions
    parseCSV(content: string, delimiter: string): Record<string, string>[] { /* ... */ }
    generateMarkdown(data: Record<string, string>): string { /* ... */ }
}
