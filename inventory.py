#!/usr/bin/env python3
"""
Домашняя инвентаризация: консольное приложение, данные в JSON.

Файл данных по умолчанию — inventory.json в той же папке, что и этот скрипт.
Его можно открыть в любом текстовом редакторе или скопировать для резервной копии.
Формат — массив объектов, например:
[
  {"id": 1, "name": "Дрель", "category": "Инструменты", "storage": "Кладовка/шкаф", "comment": "Bosch"}
]

Переменная окружения INVENTORY_FILE задаёт другой путь к файлу (опционально).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent / "inventory.json"
if os.environ.get("INVENTORY_FILE", "").strip():
    DATA_FILE = Path(os.environ["INVENTORY_FILE"].strip())


def load_items() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        raw = DATA_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"Ошибка чтения {DATA_FILE}: {e}", file=sys.stderr)
        return []


def save_items(items: list[dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(items, ensure_ascii=False, indent=2)
    DATA_FILE.write_text(text, encoding="utf-8")


def next_id(items: list[dict[str, Any]]) -> int:
    if not items:
        return 1
    return max(int(x.get("id", 0)) for x in items) + 1


def print_menu() -> None:
    print()
    print("=== Домашняя инвентаризация ===")
    print("1 — Добавить вещь")
    print("2 — Показать весь список")
    print("3 — Поиск по названию (подстрока)")
    print("4 — Поиск по категории")
    print("5 — Редактировать вещь")
    print("6 — Удалить вещь")
    print("0 — Выход")
    print("-------------------------------")


def input_line(prompt: str) -> str:
    return input(prompt).strip()


def show_item(it: dict[str, Any]) -> None:
    print(
        f"  id: {it.get('id')} | {it.get('name', '')}\n"
        f"     категория: {it.get('category', '')}\n"
        f"     место: {it.get('storage', '')}\n"
        f"     комментарий: {it.get('comment', '')}"
    )


def add_item(items: list[dict[str, Any]]) -> None:
    name = input_line("Название: ")
    if not name:
        print("Название не может быть пустым.")
        return
    category = input_line("Категория: ")
    storage = input_line("Место хранения (комната/шкаф/полка): ")
    comment = input_line("Комментарий (можно пусто): ")
    new = {
        "id": next_id(items),
        "name": name,
        "category": category,
        "storage": storage,
        "comment": comment,
    }
    items.append(new)
    save_items(items)
    print(f"Добавлено, id={new['id']}")


def list_all(items: list[dict[str, Any]]) -> None:
    if not items:
        print("Список пуст.")
        return
    for it in sorted(items, key=lambda x: int(x.get("id", 0))):
        show_item(it)
        print()


def find_by_name(items: list[dict[str, Any]], needle: str) -> list[dict[str, Any]]:
    n = needle.casefold()
    return [x for x in items if n in str(x.get("name", "")).casefold()]


def find_by_category(items: list[dict[str, Any]], needle: str) -> list[dict[str, Any]]:
    n = needle.casefold()
    return [x for x in items if n in str(x.get("category", "")).casefold()]


def search_name(items: list[dict[str, Any]]) -> None:
    q = input_line("Подстрока для поиска в названии: ")
    if not q:
        print("Пустой запрос.")
        return
    found = find_by_name(items, q)
    if not found:
        print("Ничего не найдено.")
        return
    for it in found:
        show_item(it)
        print()


def search_category(items: list[dict[str, Any]]) -> None:
    q = input_line("Подстрока для поиска в категории: ")
    if not q:
        print("Пустой запрос.")
        return
    found = find_by_category(items, q)
    if not found:
        print("Ничего не найдено.")
        return
    for it in found:
        show_item(it)
        print()


def pick_item_by_id(items: list[dict[str, Any]], iid: int) -> dict[str, Any] | None:
    for x in items:
        if int(x.get("id", -1)) == iid:
            return x
    return None


def edit_item(items: list[dict[str, Any]]) -> None:
    raw = input_line("id вещи для редактирования: ")
    if not raw.isdigit():
        print("Нужно целое число.")
        return
    iid = int(raw)
    it = pick_item_by_id(items, iid)
    if it is None:
        print("Вещь с таким id не найдена.")
        return
    print("Текущие значения (Enter — оставить без изменений):")
    show_item(it)
    name = input_line(f"Название [{it.get('name')}]: ")
    if name:
        it["name"] = name
    category = input_line(f"Категория [{it.get('category')}]: ")
    if category:
        it["category"] = category
    storage = input_line(f"Место хранения [{it.get('storage')}]: ")
    if storage:
        it["storage"] = storage
    comment = input_line(f"Комментарий [{it.get('comment')}]: ")
    if comment:
        it["comment"] = comment
    save_items(items)
    print("Сохранено.")


def delete_item(items: list[dict[str, Any]]) -> None:
    raw = input_line("id вещи для удаления: ")
    if not raw.isdigit():
        print("Нужно целое число.")
        return
    iid = int(raw)
    before = len(items)
    items[:] = [x for x in items if int(x.get("id", -1)) != iid]
    if len(items) == before:
        print("Вещь с таким id не найдена.")
        return
    save_items(items)
    print("Удалено.")


def main() -> None:
    print(f"Файл данных: {DATA_FILE}")
    items = load_items()

    while True:
        print_menu()
        choice = input_line("Выберите пункт: ")

        if choice == "1":
            add_item(items)
        elif choice == "2":
            list_all(items)
        elif choice == "3":
            search_name(items)
        elif choice == "4":
            search_category(items)
        elif choice == "5":
            edit_item(items)
        elif choice == "6":
            delete_item(items)
        elif choice == "0":
            print("До свидания.")
            break
        else:
            print("Неизвестный пункт, попробуйте снова.")


if __name__ == "__main__":
    main()
