from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Vertical
from textual.reactive import reactive


class MenuItem(Static):
    active = reactive(False)

    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self.label_text = label

    def render(self) -> str:
        if self.active: return f"▶  {self.label_text}  ◀"
        return f"   {self.label_text}   "

    def watch_active(self, active: bool) -> None:
        if active: self.add_class("active")
        else:   self.remove_class("active")


class MainMenuScreen(Screen):
    def __init__(self, logo: str, options: list, version: str, on_select):
        super().__init__()
        self.logo_text = logo
        self.options = options
        self.version_text = version
        self.on_select_callback = on_select
        self.active_index = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="app-container"):
            yield Static(self.logo_text, id="logo")
            with Vertical(id="menu-container"):
                for idx, opt in enumerate(self.options): yield MenuItem(opt["label"], id=f"item_{idx}")
        yield Static(self.version_text, id="version-label")

    def on_mount(self) -> None:
        self.update_selection()

    def update_selection(self) -> None:
        for i in range(len(self.options)):
            try:
                item = self.query_one(f"#item_{i}", MenuItem)
                item.active = (i == self.active_index)
            except Exception:
                pass

        try:
            widget_y = 27 + (self.active_index * 4) + 1
            height = self.size.height
            target_scroll_y = max(0, widget_y - (height // 2))
            self.scroll_to(y=target_scroll_y, animate=False)
        except Exception:
            pass

    def on_key(self, event) -> None:
        if event.key == "up":
            if self.active_index > 0:
                self.active_index -= 1
                self.update_selection()
        elif event.key == "down":
            if self.active_index < len(self.options) - 1:
                self.active_index += 1
                self.update_selection()
        elif event.key == "enter":
            self.select_option()

    def on_click(self, event) -> None:
        if isinstance(event.widget, MenuItem):
            idx = int(event.widget.id.split("_")[1])
            self.active_index = idx
            self.update_selection()
            self.select_option()

    def select_option(self) -> None:
        selected_option = self.options[self.active_index]
        self.on_select_callback(selected_option)


class UniversalApp(App):
    def __init__(self, logo: str, options: list, version: str, theme: dict, on_select):
        super().__init__()
        self.logo_text = logo
        self.options = options
        self.version_text = version

        self.custom_theme = theme
        self.on_select_callback = on_select

        # Динамическая генерация CSS на основе словаря темы
        self.CSS = f"""
        * {{
            scrollbar-size: 0 0 !important;
        }}
        Screen {{
            background: {theme['background']};
            align: center middle;
            overflow-y: auto !important;
        }}
        #app-container {{
            align: center middle;
            width: 50;
            height: auto;
            overflow: hidden;
        }}
        #logo {{
            background: {theme['text']};
            color: {theme['background']};
            width: 50;
            height: 25;
            content-align: center middle;
            margin-bottom: 2;
        }}
        #menu-container {{
            align: center middle;
            width: 100%;
            height: auto;
            overflow: hidden;
        }}
        MenuItem {{
            text-align: center;
            color: {theme['text']};
            background: {theme['background']};
            border: round {theme['text']};
            height: 3;
            margin-bottom: 0;
            width: 32;
            content-align: center middle;
        }}
        MenuItem.active {{
            color: {theme['active']};
            background: {theme['background']};
            border: round {theme['active']};
        }}
        MenuItem:hover {{
            color: {theme['active']};
            background: {theme['background']};
            border: round {theme['active']};
        }}
        #version-label {{
            dock: bottom;
            width: auto;
            margin-left: 3;
            margin-bottom: 1;
            color: {theme['muted']};
        }}
        """

    def on_mount(self) -> None:
        screen = MainMenuScreen(
            logo=self.logo_text,
            options=self.options,
            version=self.version_text,
            on_select=lambda option: self.on_select_callback(self, option)
        )
        self.push_screen(screen)