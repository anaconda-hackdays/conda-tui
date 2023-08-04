import json
import random
from functools import cache
from functools import cached_property
from pathlib import Path
from typing import Any

from conda.core.prefix_data import PrefixData
from rich.text import Text

from conda_tui.environment import Environment


class Package:
    """Wrap a conda PrefixRecord, and supplement with custom attributes."""

    def __init__(self, record: PrefixData):
        self._record = record
        # TODO: This should be replaced with a call to the conda repo
        self._update_available = random.random() > 0.8

    def __getattr__(self, item: str) -> Any:
        return getattr(self._record, item)

    @property
    def update_available(self) -> bool:
        return self._update_available

    @update_available.setter
    def update_available(self, value: bool) -> None:
        self._update_available = value

    @property
    def status(self) -> Text:
        return self._get_update_status_icon(self.update_available) + " " + self.version

    @staticmethod
    @cache
    def _get_update_status_icon(update_available: bool) -> Text:
        if update_available:
            return Text.from_markup("[bold #DB6015]\N{UPWARDS ARROW}[/]")
        return Text.from_markup("[bold #43b049]\N{HEAVY CHECK MARK}[/]")

    @cached_property
    def description(self) -> str:
        """Attempt to load the package description."""
        try:
            package_dir = self.extracted_package_dir
        except AttributeError:
            return ""
        info_path = Path(package_dir, "info", "about.json")
        if not info_path.exists():
            return ""
        with info_path.open("r") as fh:
            return json.load(fh).get("summary", "")


@cache
def list_packages_for_environment(env: Environment) -> list[Package]:
    prefix_data = PrefixData(str(env.prefix), pip_interop_enabled=True)
    packages = [Package(record) for record in prefix_data.iter_records()]
    return sorted(packages, key=lambda x: x.name)
