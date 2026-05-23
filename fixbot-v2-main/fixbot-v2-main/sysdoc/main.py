import os
import re
import sys

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.conversation_memory import ConversationMemory
from core.executor import SysDocExecutor
from core.permission_gate import PermissionGate
from core.report_generator import ReportGenerator
from modules.installer import InstallerModule, extract_app_name
from modules import file_finder
from display.banner import print_banner, print_help, ask_theme, get_theme_color, get_theme_hex, print_welcome_panel
from display.formatter import (
    print_bot_start,
    print_collecting,
    print_data,
    print_err,
    print_info,
    print_ok,
    print_process_table,
    print_browser_tab_table,
    print_bg_process_table,
    print_search_results_table,
    print_file_ops_menu,
    print_file_location_panel,
    print_section,
    print_ticket,
    print_user,
    print_system_scan,
    print_warn,
)
from tickets.ticket_manager import TicketManager

console = Console()

_DRY_RUN = "--dry-run" in sys.argv
_MEMORY_PATH = os.path.join(ROOT_DIR, "memory", "conversation.json")
_REPORTS_DIR = os.path.join(ROOT_DIR, "reports")

COMMANDS = {
    "exit": "exit",
    "quit": "exit",
    "clear": "clear",
    "help": "help",
    "scan": "scan",
    "tickets": "tickets",
    "processes": "processes",
    "ps": "processes",
    "tabs": "tabs",
    "live tabs": "tabs",
    "report": "report",
    "reports": "report",
}

# Matches Windows absolute paths (quoted or unquoted, no embedded spaces)
_PATH_RE = re.compile(
    r'"([A-Za-z]:\\[^"]+)"'                                            # "C:\quoted path"
    r'|([A-Za-z]:\\(?:[^\\\s"\'<>|?*\n]+\\)*[^\\\s"\'<>|?*\n]*)'     # C:\unquoted\path
)

# Matches standalone filenames with a known extension (e.g. thalas.txt, config.json)
_FILENAME_RE = re.compile(
    r'\b([\w\-]+\.(?:txt|py|js|ts|json|csv|md|yaml|yml|xml|html|css|'
    r'java|cpp|c|h|go|rs|sh|bat|ps1|ini|cfg|conf|log|sql|php|rb|kt|swift|env|toml))\b',
    re.IGNORECASE,
)

_EXPLAIN_TRIGGERS = [
    "explain about ", "explain ", "read ", "open ", "show me ",
    "what is in ", "what's in ", "describe ", "analyze ", "analyse ",
    "tell me about ", "look at ", "show ", "display ",
]

_SEARCH_PREFIXES = [
    "find my file ", "find my folder ", "find my app ", "find my ",
    "find file ", "find folder ", "find app ", "find me the ", "find me ",
    "where is the file ", "where is the folder ", "where is my ", "where is the ", "where is ",
    "where my ", "where ",
    "locate file ", "locate folder ", "locate app ", "locate ",
    "search for file ", "search for folder ", "search for app ", "search for ",
    "look for file ", "look for folder ", "look for ", "show me where ",
]

_DELETE_PREFIXES = [
    "delete my file ", "delete my folder ", "delete my app ", "delete my ",
    "delete file ", "delete folder ", "delete app ", "delete ",
    "remove my file ", "remove my folder ", "remove my app ", "remove my ",
    "remove file ", "remove folder ", "remove app ", "remove ",
    "erase my file ", "erase my folder ", "erase my ", "erase ",
    "i want to delete ", "can you delete ", "please delete ",
    "get rid of ", "i need to delete ", "help me delete ",
]


def _extract_search_query(user_input: str) -> str:
    text = user_input.strip()
    lowered = text.lower()
    for prefix in sorted(_SEARCH_PREFIXES, key=len, reverse=True):
        if lowered.startswith(prefix):
            return text[len(prefix):].strip()
    return text


def _extract_delete_query(user_input: str) -> str:
    text = user_input.strip()
    lowered = text.lower()
    for prefix in sorted(_DELETE_PREFIXES, key=len, reverse=True):
        if lowered.startswith(prefix):
            return text[len(prefix):].strip()
    return text


def _location_description(path: str) -> str:
    """Return a human-readable description of a file/folder location."""
    p = path.lower()
    if "\\onedrive\\" in p and "\\desktop" in p:
        return "OneDrive Desktop  (synced — deleting here also removes it from the cloud)"
    if "\\desktop" in p:
        return "Desktop"
    if "\\downloads" in p:
        return "Downloads folder"
    if "\\documents" in p:
        return "Documents folder"
    if "\\onedrive" in p:
        return "OneDrive  (synced to cloud — cloud copy will also be deleted)"
    if "\\appdata\\local\\temp" in p:
        return "Temporary files folder  (safe to delete)"
    if "\\appdata\\local" in p:
        return "AppData\\Local  (app cache / local config data)"
    if "\\appdata\\roaming" in p:
        return "AppData\\Roaming  (app settings / user profile data)"
    if "\\program files (x86)" in p:
        return "Program Files (x86)  (32-bit installed application)"
    if "\\program files" in p:
        return "Program Files  (installed application)"
    if "\\system32" in p:
        return "Windows System32  ⚠ system file — delete only if you are sure"
    if "\\windows" in p:
        return "Windows folder  ⚠ system file — delete only if you are sure"
    if "\\users" in p:
        return "User profile folder"
    return os.path.dirname(path)


def _delete_commands(path: str, item_type: str) -> tuple:
    """Return (cmd_command, powershell_command) for manual deletion."""
    q = f'"{path}"'
    if item_type == "folder":
        return f"rmdir /s /q {q}", f'Remove-Item -Recurse -Force {q}'
    return f"del /f /q {q}", f'Remove-Item -Force {q}'


def _do_file_search(query: str, mem: "ConversationMemory") -> None:
    from prompt_toolkit import prompt as tk_prompt
    from prompt_toolkit.styles import Style as TkStyle

    hex_col = get_theme_hex()
    input_style = TkStyle.from_dict({"prompt": f"{hex_col} bold"})

    with console.status(
        f"  [dim]Searching for '{query}' across all drives...[/dim]", spinner="dots"
    ):
        results = file_finder.search_system(query)

    print_search_results_table(results, query)

    if not results:
        return

    console.print(f"  [dim]Enter a number (1–{len(results)}) to select, or press Enter to skip:[/dim]")
    try:
        idx_raw = tk_prompt("  ❯ ", style=input_style).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not idx_raw:
        return

    try:
        idx = int(idx_raw)
        if not (1 <= idx <= len(results)):
            print_warn("Invalid selection.")
            return
    except ValueError:
        print_warn("Not a number — skipping.")
        return

    selected = results[idx - 1]
    loc_desc = _location_description(selected["path"])
    cmd, ps_cmd = _delete_commands(selected["path"], selected["type"])
    print_file_location_panel(selected, loc_desc, cmd, ps_cmd)

    print_file_ops_menu()

    try:
        action = tk_prompt("  ❯ Select action: ", style=input_style).strip().lower()
    except (KeyboardInterrupt, EOFError):
        return

    if action == "d":
        console.print(f"  [bold red]⚠  Delete:[/bold red] [white]{selected['path']}[/white]")
        try:
            confirm = tk_prompt(
                "  ❯ Type 'yes' to confirm delete: ",
                style=TkStyle.from_dict({"prompt": "#ff4444 bold"}),
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return
        if confirm == "yes":
            msg = file_finder.delete_path(selected["path"])
            (print_ok if "Deleted" in msg else print_err)(msg)
        else:
            print_info("Delete cancelled.")

    elif action == "r":
        console.print(f"  [dim]Enter new name for '{selected['name']}':[/dim]")
        try:
            new_name = tk_prompt("  ❯ New name: ", style=input_style).strip()
        except (KeyboardInterrupt, EOFError):
            return
        if new_name:
            msg = file_finder.rename_path(selected["path"], new_name)
            (print_ok if "Renamed" in msg else print_err)(msg)
        else:
            print_info("Rename cancelled.")

    elif action == "c":
        msg = file_finder.copy_to_clipboard(selected["path"])
        (print_ok if "copied" in msg.lower() else print_err)(msg)

    elif action == "n":
        print_info("No action taken.")
    else:
        print_warn("Unknown action — skipping.")

    mem.add("user", f"find {query}")
    mem.add("model", f"Found {len(results)} result(s). Selected: {selected['path']}")
    console.print()


def _do_file_delete(query: str, mem: "ConversationMemory") -> None:
    """Find a file/folder by name and delete it after confirmation."""
    from prompt_toolkit import prompt as tk_prompt
    from prompt_toolkit.styles import Style as TkStyle

    hex_col = get_theme_hex()
    input_style = TkStyle.from_dict({"prompt": f"{hex_col} bold"})
    danger_style = TkStyle.from_dict({"prompt": "#ff4444 bold"})

    with console.status(
        f"  [dim]Searching for '{query}' to delete...[/dim]", spinner="dots"
    ):
        results = file_finder.search_system(query)

    print_search_results_table(results, query)

    if not results:
        print_info("Nothing found — nothing deleted.")
        return

    console.print(f"  [dim]Enter a number (1–{len(results)}) to select for deletion, or press Enter to cancel:[/dim]")
    try:
        idx_raw = tk_prompt("  ❯ ", style=input_style).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not idx_raw:
        print_info("Delete cancelled.")
        return

    try:
        idx = int(idx_raw)
        if not (1 <= idx <= len(results)):
            print_warn("Invalid selection — nothing deleted.")
            return
    except ValueError:
        print_warn("Not a number — nothing deleted.")
        return

    selected = results[idx - 1]
    loc_desc = _location_description(selected["path"])
    cmd, ps_cmd = _delete_commands(selected["path"], selected["type"])
    print_file_location_panel(selected, loc_desc, cmd, ps_cmd)

    console.print(f"  [bold red]⚠  CONFIRM DELETE[/bold red]  [dim]— This cannot be undone.[/dim]")
    console.print()

    try:
        confirm = tk_prompt(
            "  ❯ Type 'yes' to permanently delete: ", style=danger_style
        ).strip().lower()
    except (KeyboardInterrupt, EOFError):
        print_info("Delete cancelled.")
        return

    if confirm == "yes":
        msg = file_finder.delete_path(selected["path"])
        (print_ok if "Deleted" in msg else print_err)(msg)
        mem.add("user", f"delete {query}")
        mem.add("model", msg)
    else:
        print_info("Delete cancelled.")

    console.print()


def format_ticket_detail(ticket: dict) -> str:
    lines = []
    for key, value in ticket.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


_INTENT_PRIORITY_KEYS = {
    "NETWORK":  ["wifi_ssid", "internet", "download_mbps", "upload_mbps", "dns_status", "ping_ms", "packet_loss_pct", "gateway_ip", "outage_prediction"],
    "STORAGE":  ["drives", "critical_drives", "temp_folder_gb", "recycle_bin_gb", "top_large_files"],
    "DEV_ENV":  ["active_python", "pip_status", "dependency_conflicts", "node_version", "venv_found"],
    "SYSTEM":   ["cpu_percent", "ram_used_pct", "cpu_temp_c", "recent_crashes", "fan_speed_rpm"],
}

_DEFAULT_PRIORITY_KEYS = [
    "wifi_ssid", "cpu_percent", "ram_used_pct", "cpu_temp_c",
    "dns_status", "internet", "outage_prediction", "gateway_ip",
    "packet_loss_pct", "temp_folder_gb", "recycle_bin_gb",
]


def _top_os_data_keys(os_data: dict, intent: str = "") -> list:
    priority_keys = _INTENT_PRIORITY_KEYS.get(intent, _DEFAULT_PRIORITY_KEYS)
    keys = [key for key in priority_keys if key in os_data]
    keys.extend(k for k in os_data.keys() if k not in keys)
    return keys[:5]


def main() -> None:
    if not os.environ.get("GEMINI_API_KEY", "").strip():
        console.print(
            "\n  [bold red]GEMINI_API_KEY is not set.[/bold red]"
            "\n  Add it to your environment or create a .env file with:"
            "\n  [dim]GEMINI_API_KEY=your_api_key_here[/dim]\n"
        )
        return

    if not PermissionGate.has_admin():
        console.print(
            "\n  [bold red]fixbot requires administrator privileges.[/bold red]"
            "\n  Right-click your terminal and choose 'Run as administrator', then try again.\n"
        )
        return

    executor = SysDocExecutor(dry_run=_DRY_RUN)
    prompt_builder = executor.prompt_builder
    ticket_manager = TicketManager()
    memory = ConversationMemory(path=_MEMORY_PATH)
    report_gen = ReportGenerator(reports_dir=_REPORTS_DIR)
    installer = InstallerModule(executor.gemini)

    print_banner()
    ask_theme()
    PermissionGate.ask_initial_permissions()
    print_welcome_panel()



    if _DRY_RUN:
        print_warn("DRY RUN mode — fixes will be previewed but not executed.")

    while True:
        try:
            hex_col = get_theme_hex()
            user_input = prompt(
                "\n  ❯ ",
                style=Style.from_dict({"prompt": f"{hex_col} bold"}),
            ).strip()

        except (KeyboardInterrupt, EOFError):
            console.print("\n  Goodbye.\n")
            break

        if not user_input:
            continue

        user_input_lower = user_input.lower().strip()
        action = None
        filter_arg = ""

        if user_input_lower in COMMANDS:
            action = COMMANDS[user_input_lower]
        elif user_input_lower.startswith("live tabs"):
            action = "tabs"
            filter_arg = user_input[9:].strip()
        else:
            parts = user_input.split(maxsplit=1)
            if parts:
                first_word = parts[0].lower()
                extra = parts[1].strip() if len(parts) == 2 else ""
                # Don't swallow "clear cache" / "clear temp" etc. as the clear-screen command
                if first_word in COMMANDS and not (first_word == "clear" and extra):
                    action = COMMANDS[first_word]
                    if extra:
                        filter_arg = extra

        if action is not None:
            if action == "exit":
                console.print("  Shutting down.\n")
                break
            if action == "clear":
                console.clear()
                print_banner()
                continue
            if action == "help":
                print_help()
                continue
            if action == "scan":
                all_data = {
                    "network": executor.network.collect(),
                    "storage": executor.storage.collect(),
                    "dev_env": executor.dev_env.collect(),
                    "system": executor.system_health.collect(),
                }
                print_system_scan(all_data)
                continue
            if action == "report":
                recent = report_gen.list_recent()
                if not recent:
                    print_info("No reports yet. Reports are saved automatically after each fix.")
                else:
                    print_info(f"Last {len(recent)} reports:")
                    for path in recent:
                        console.print(f"  [dim]{path}[/dim]")
                continue
            if action == "tickets":
                summaries = ticket_manager.list_tickets()
                if not summaries:
                    print_info("No tickets found.")
                    continue
                for summary in summaries:
                    print_ticket(summary)
                continue
            if action == "processes":
                procs = executor.system_health.list_processes(top=20, filter_name=filter_arg)
                print_process_table(procs)
                continue
            if action == "tabs":
                tabs = executor.system_health.list_browser_tabs(filter_name=filter_arg)
                print_browser_tab_table(tabs)
                continue

        if user_input.lower().startswith("ticket "):
            ticket_id = user_input.split(maxsplit=1)[1].strip()
            ticket = ticket_manager.get_ticket(ticket_id)
            if not ticket:
                print_warn(f"Ticket {ticket_id} not found.")
                continue
            print_ticket(ticket)
            console.print(format_ticket_detail(ticket))
            continue

        # --- File finder: "find <query>" direct command ---
        if user_input_lower.startswith("find ") and len(user_input) > 5:
            query = user_input[5:].strip()
            if query:
                _do_file_search(query, memory)
                continue

        # --- File delete: "delete/remove/erase <query>" direct command ---
        _delete_triggers = ("delete ", "remove ", "erase ")
        if any(user_input_lower.startswith(t) for t in _delete_triggers):
            query = _extract_delete_query(user_input)
            if query:
                _do_file_delete(query, memory)
                continue

        if user_input.lower().startswith("kill "):
            parts = user_input.split(maxsplit=1)
            if len(parts) == 2:
                target = parts[1].strip()
                result = executor.system_health.kill_by_index_or_pid(target)
                if "Killed" in result or "Closed" in result:
                    print_ok(result)
                else:
                    print_warn(result)
            else:
                print_warn("Usage: kill <pid_or_name_or_index>   example: kill 1 or kill 1234 or kill whatsapp")
            continue

        # --- close <app> / close all background / close all apps ---
        _close_all_phrases = (
            "close all background", "close all apps", "close all applications",
            "close background", "close background processes", "close all",
        )
        if any(user_input_lower == p or user_input_lower.startswith(p) for p in _close_all_phrases):
            from prompt_toolkit import prompt as tk_prompt
            from prompt_toolkit.styles import Style as TkStyle
            hex_col = get_theme_hex()
            procs = executor.system_health.get_background_processes()
            print_bg_process_table(procs)
            if not procs:
                console.print()
                continue
            important = [p for p in procs if p.get("important")]
            if important:
                print_warn(f"  {len(important)} important app(s) marked ⚠ — closing them may lose unsaved work.")
            try:
                sel = tk_prompt(
                    "  ❯ Close all? [y / n / numbers like 1,3,5]: ",
                    style=TkStyle.from_dict({"prompt": f"{hex_col} bold"}),
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                print_info("Cancelled.")
                console.print()
                continue
            if sel == "n" or not sel:
                print_info("No processes closed.")
            elif sel == "y":
                killed, failed = executor.system_health.close_processes_bulk(procs)
                print_ok(f"Closed {killed} background process(es). {failed} skipped.")
            else:
                indices = []
                for part in sel.replace(" ", "").split(","):
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(procs):
                            indices.append(idx)
                targets = [procs[i] for i in indices]
                killed, failed = executor.system_health.close_processes_bulk(targets)
                print_ok(f"Closed {killed} process(es). {failed} skipped.")
            console.print()
            continue

        if user_input_lower.startswith("close "):
            target_app = user_input[6:].strip()
            if target_app:
                from prompt_toolkit import prompt as tk_prompt
                from prompt_toolkit.styles import Style as TkStyle
                hex_col = get_theme_hex()
                # Find matching processes to show before killing
                matches = [
                    p for p in executor.system_health.get_background_processes(min_ram_mb=0)
                    if target_app.lower() in p["name"].lower()
                ]
                if not matches:
                    print_warn(f"No running process found matching '{target_app}'.")
                    console.print()
                    continue
                print_bg_process_table(matches)
                important_match = any(p.get("important") for p in matches)
                if important_match:
                    print_warn("This is an important app — closing may lose unsaved work.")
                try:
                    confirm = tk_prompt(
                        f"  ❯ Close {len(matches)} instance(s) of '{target_app}'? [y/n]: ",
                        style=TkStyle.from_dict({"prompt": f"{hex_col} bold"}),
                    ).strip().lower()
                except (KeyboardInterrupt, EOFError):
                    print_info("Cancelled.")
                    console.print()
                    continue
                if confirm == "y":
                    killed, failed = executor.system_health.close_processes_bulk(matches)
                    print_ok(f"Closed {killed} instance(s) of '{target_app}'. {failed} skipped.")
                else:
                    print_info("Cancelled.")
            console.print()
            continue

        # --- free memory ---
        _FREE_MEM = ("free memory", "free ram", "free up memory", "free up ram", "release memory")
        if user_input_lower in _FREE_MEM or any(user_input_lower.startswith(p) for p in _FREE_MEM):
            procs = executor.system_health.get_background_processes(min_ram_mb=50)
            print_bg_process_table(procs)
            if procs:
                total_mb = sum(p.get("ram_mb", 0) for p in procs)
                console.print(f"  [dim]Closing these will free up to [bold]{total_mb/1024:.2f} GB[/bold] of RAM.[/dim]")
                from prompt_toolkit import prompt as tk_prompt
                from prompt_toolkit.styles import Style as TkStyle
                hex_col = get_theme_hex()
                try:
                    sel = tk_prompt(
                        "  ❯ Close all non-essential? [y/n]: ",
                        style=TkStyle.from_dict({"prompt": f"{hex_col} bold"}),
                    ).strip().lower()
                except (KeyboardInterrupt, EOFError):
                    sel = "n"
                if sel == "y":
                    safe = [p for p in procs if not p.get("important")]
                    killed, failed = executor.system_health.close_processes_bulk(safe)
                    print_ok(f"Freed RAM: closed {killed} process(es). {failed} skipped.")
                else:
                    print_info("No changes made.")
            console.print()
            continue

        # --- restart explorer ---
        _RESTART_EXP = ("restart explorer", "restart taskbar", "reset taskbar", "fix taskbar", "reload explorer")
        if user_input_lower in _RESTART_EXP:
            with console.status("  [dim]Restarting Windows Explorer...[/dim]", spinner="dots"):
                result = executor.system_health.restart_explorer()
            print_ok(result)
            console.print()
            continue

        # --- optimize system ---
        _OPTIMIZE = ("optimize system", "optimize pc", "optimize", "full optimize", "speed up system")
        if user_input_lower in _OPTIMIZE:
            from prompt_toolkit import prompt as tk_prompt
            from prompt_toolkit.styles import Style as TkStyle
            hex_col = get_theme_hex()
            console.print()
            console.print(f"  [bold {hex_col}]◉ FIXBOT[/bold {hex_col}]  [dim]System Optimization[/dim]")
            console.print(f"  [dim]{'─'*46}[/dim]")
            console.print("  Running all optimizations: cache clear → close background apps → power plan.")
            console.print()
            try:
                confirm = tk_prompt(
                    "  ❯ Proceed with full system optimization? [y/n]: ",
                    style=TkStyle.from_dict({"prompt": f"{hex_col} bold"}),
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                confirm = "n"
            if confirm == "y":
                # Step 1: cache
                console.print(f"\n  [bold {hex_col}]Step 1 — Cache Removal[/bold {hex_col}]")
                result = executor.run_cache_cleanup()
                # Step 2: background processes
                console.print(f"\n  [bold {hex_col}]Step 2 — Background Processes[/bold {hex_col}]")
                procs = executor.system_health.get_background_processes(min_ram_mb=50)
                safe  = [p for p in procs if not p.get("important")]
                if safe:
                    killed, _ = executor.system_health.close_processes_bulk(safe)
                    print_ok(f"Closed {killed} background process(es).")
                else:
                    print_ok("No significant background processes to close.")
                # Step 3: power plan
                console.print(f"\n  [bold {hex_col}]Step 3 — Power Plan[/bold {hex_col}]")
                pwr = executor.system_health.fix_power_balanced()
                print_ok(pwr)
                console.print()
                print_ok("Full system optimization complete.")
            else:
                print_info("Optimization cancelled.")
            console.print()
            continue

        print_user(user_input)

        # --- Auto-detect file path → explain its content ---
        path_match = _PATH_RE.search(user_input)
        if path_match:
            detected_path = (path_match.group(1) or path_match.group(2)).strip()
            if os.path.isfile(detected_path):
                content = file_finder.read_file_safe(detected_path)
                if content is not None:
                    console.print(
                        f"  [dim]Detected file:[/dim] [white]{detected_path}[/white]"
                    )
                    console.print()
                    print_bot_start()
                    full_reply = ""
                    for chunk in executor.gemini.explain_file_stream(detected_path, content):
                        full_reply += getattr(chunk, "text", str(chunk))
                    console.print(Markdown(full_reply))
                    memory.add("user", user_input)
                    memory.add("model", full_reply)
                    console.print()
                    continue

        # --- Filename-only detection: "explain about thalas.txt" / "read config.json" ---
        fn_match = _FILENAME_RE.search(user_input)
        if fn_match:
            filename_query = fn_match.group(1)
            lowered = user_input.lower()
            is_explain = (
                any(t in lowered for t in _EXPLAIN_TRIGGERS)
                or lowered.strip() == filename_query.lower()
            )
            if is_explain:
                with console.status(
                    f"  [dim]Searching for '{filename_query}'...[/dim]", spinner="dots"
                ):
                    results = file_finder.search_system(filename_query)
                if results:
                    detected_path = results[0]["path"]
                    content = file_finder.read_file_safe(detected_path)
                    if content is not None:
                        console.print(
                            f"  [dim]Found:[/dim] [white]{detected_path}[/white]"
                        )
                        console.print()
                        print_bot_start()
                        full_reply = ""
                        for chunk in executor.gemini.explain_file_stream(detected_path, content):
                            full_reply += getattr(chunk, "text", str(chunk))
                        console.print(Markdown(full_reply))
                        memory.add("user", user_input)
                        memory.add("model", full_reply)
                        console.print()
                        continue
                else:
                    print_warn(f"File '{filename_query}' not found. Try: find {filename_query}")
                    continue

        app_name = extract_app_name(user_input)
        if app_name:
            installer.handle(app_name)
            memory.add("user", user_input)
            memory.add("model", f"Handled install request for: {app_name}")
            console.print()
            continue

        # --- Direct cache-clear route (no Gemini round-trip needed) ---
        # Word-level "cache" check catches typos ("cleat cache", "cler cache" etc.)
        _input_words = set(user_input_lower.split())
        _CACHE_TRIGGER_PHRASES = (
            "clear temp", "clean temp", "improve performance", "boost performance",
            "speed up my pc", "speed up pc", "free up space", "clean up pc", "clear junk",
            "clean junk", "clear system", "clean system",
        )
        _is_cache_request = (
            "cache" in _input_words
            or any(phrase in user_input_lower for phrase in _CACHE_TRIGGER_PHRASES)
        )
        if _is_cache_request:
            from prompt_toolkit import prompt as tk_prompt
            from prompt_toolkit.styles import Style as TkStyle
            hex_col = get_theme_hex()
            executor.preview_cache_cleanup()
            try:
                confirm = tk_prompt(
                    "  ❯ Proceed with cleanup? [y/n]: ",
                    style=TkStyle.from_dict({"prompt": f"{hex_col} bold"}),
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                print_info("Cancelled.")
                console.print()
                continue
            if confirm != "y":
                print_info("Skipped — no changes made.")
                console.print()
                continue
            result = executor.run_cache_cleanup()
            os_data = prompt_builder.build_context(user_input, "STORAGE")
            verification = executor.last_verification
            report = report_gen.generate(
                intent="STORAGE",
                problem=user_input,
                os_data=os_data,
                ai_reply="Cache and temp files cleared.",
                fix_applied=result,
                verification_passed=verification.passed if verification else None,
                changes=verification.changes if verification else {},
            )
            saved = report_gen.save(report)
            report_gen.display_summary(report, saved_path=saved)
            memory.add("user", user_input)
            memory.add("model", result)

            # Offer to also close background apps to further free RAM
            try:
                bg_confirm = tk_prompt(
                    "  ❯ Also close background apps to free RAM? [y/n]: ",
                    style=Style.from_dict({"prompt": f"{hex_col} bold"}),
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                bg_confirm = "n"
            if bg_confirm == "y":
                bg_procs = executor.system_health.get_background_processes(min_ram_mb=50)
                safe_procs = [p for p in bg_procs if not p.get("important")]
                print_bg_process_table(safe_procs)
                if safe_procs:
                    try:
                        sel = tk_prompt(
                            "  ❯ Close all non-essential? [y / n / numbers like 1,3,5]: ",
                            style=Style.from_dict({"prompt": f"{hex_col} bold"}),
                        ).strip().lower()
                    except (KeyboardInterrupt, EOFError):
                        sel = "n"
                    if sel == "y":
                        killed, failed = executor.system_health.close_processes_bulk(safe_procs)
                        print_ok(f"Closed {killed} background process(es). {failed} skipped.")
                    elif sel != "n" and sel:
                        indices = [int(p)-1 for p in sel.replace(" ","").split(",") if p.isdigit()]
                        targets = [safe_procs[i] for i in indices if 0 <= i < len(safe_procs)]
                        killed, failed = executor.system_health.close_processes_bulk(targets)
                        print_ok(f"Closed {killed} process(es). {failed} skipped.")
                    else:
                        print_info("No processes closed.")
                else:
                    print_ok("No significant background processes running.")
            console.print()
            continue

        intent = executor.intent_engine.detect_intent(user_input)

        if memory.is_followup(user_input) and intent == "GENERAL":
            recent = memory.get_history(6)
            if recent:
                for entry in reversed(recent):
                    if entry["role"] == "user":
                        prev_intent = executor.intent_engine.detect_intent(entry["parts"][0])
                        if prev_intent != "GENERAL":
                            intent = prev_intent
                            break

        if intent == "GREETING":
            greeting = "Hello! I am Fixbot, your AI-powered system support assistant. How can I help you today?"
            print_bot_start()
            console.print(greeting)
            memory.add("user", user_input)
            memory.add("model", greeting)
            console.print()
            continue

        if intent == "FILE_SEARCH":
            query = _extract_search_query(user_input)
            _do_file_search(query, memory)
            continue

        if intent == "FILE_DELETE":
            query = _extract_delete_query(user_input)
            _do_file_delete(query, memory)
            continue

        if intent == "GENERAL":
            # Send general/unknown questions directly to Gemini — no clarification menu
            pass

        diagnostic_intents = {"NETWORK", "STORAGE", "DEV_ENV", "SYSTEM"}
        if intent in diagnostic_intents:
            print_collecting(intent.lower())
            os_data = prompt_builder.build_context(user_input, intent)
            for key in _top_os_data_keys(os_data, intent):
                print_data(key, str(os_data.get(key, "n/a")))
        else:
            os_data = {}

        console.print()
        print_bot_start()
        full_reply = ""
        theme_col = get_theme_color()
        for chunk in executor.gemini.ask_gemini_stream(user_input, os_data, memory.get_history()):
            text = getattr(chunk, "text", str(chunk))
            console.print(text, style=theme_col, end="", highlight=False)
            full_reply += text
        console.print()

        memory.add("user", user_input)
        memory.add("model", full_reply)

        # Only offer fix actions for intents that have mapped fixes
        actionable_intents = {"NETWORK", "STORAGE", "DEV_ENV", "SYSTEM"}
        if intent in actionable_intents:
            action = PermissionGate.ask_permission(intent)
            if action == "t":
                ticket = ticket_manager.create_ticket(
                    problem=user_input,
                    os_data=os_data,
                    gemini_reply=full_reply,
                    module=intent,
                )
                print_ticket(ticket)
            elif action == "n":
                print_info("Skipped.")
            elif action == "d":
                console.print(full_reply)
            else:
                result, new_data = executor.run(intent, action, os_data)
                os_data = new_data

                verification = executor.last_verification
                report = report_gen.generate(
                    intent=intent,
                    problem=user_input,
                    os_data=os_data,
                    ai_reply=full_reply,
                    fix_applied=result,
                    verification_passed=verification.passed if verification else None,
                    changes=verification.changes if verification else {},
                )
                saved = report_gen.save(report)
                report_gen.display_summary(report, saved_path=saved)

        console.print()


if __name__ == "__main__":
    main()
