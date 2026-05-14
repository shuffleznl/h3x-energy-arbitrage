#!/usr/bin/env python3
"""Validate Home Assistant sensor metadata for recorder/statistics compatibility."""

from __future__ import annotations

import ast
from pathlib import Path


SENSOR_PATH = Path("custom_components/h3x_energy_arbitrage/sensor.py")


def keyword_name(node: ast.keyword) -> str:
    if node.arg is None:
        raise AssertionError("unexpected **kwargs in sensor description")
    return node.arg


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{dotted_name(node.value)}.{node.attr}"
    return ast.unparse(node)


def main() -> None:
    tree = ast.parse(SENSOR_PATH.read_text(), filename=str(SENSOR_PATH))
    source = ast.unparse(tree)

    if "_unrecorded_attributes = UNRECORDED_PLAN_ATTRIBUTES" not in source:
        raise AssertionError("large chart arrays must be excluded from recorder")

    descriptions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and dotted_name(node.func).endswith("H3XArbitrageSensorDescription")
    ]
    if not descriptions:
        raise AssertionError("no sensor descriptions found")

    for description in descriptions:
        kwargs = {keyword_name(keyword): keyword.value for keyword in description.keywords}
        key_node = kwargs.get("key")
        key = ast.literal_eval(key_node) if key_node is not None else None
        device_class = kwargs.get("device_class")
        state_class = kwargs.get("state_class")
        if (
            device_class is not None
            and dotted_name(device_class) == "SensorDeviceClass.ENERGY"
            and state_class is not None
            and dotted_name(state_class) == "SensorStateClass.MEASUREMENT"
        ):
            raise AssertionError(
                f"{key} uses energy device class with invalid measurement state class"
            )

    decision = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_decision_attributes"
    )
    decision_source = ast.unparse(decision)
    for token in ("price_slots", "today_slots", "tomorrow_slots", "dispatch_plan"):
        if token in decision_source:
            raise AssertionError(f"decision sensor must not expose {token}")


if __name__ == "__main__":
    main()
