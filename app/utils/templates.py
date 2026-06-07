"""
Template utilities for NetPilot AI.

Future Enhancements:
- Jinja2 template engine for dynamically generating configs
- Vendor-specific template directories
- Template versioning and rollback
"""

def render_config_template(vendor: str, template_name: str, context: dict) -> str:
    """
    Temporary placeholder for configuration template rendering.
    This will later use Jinja2 for full template rendering.
    """

    output = [
        f"# Template Rendered by NetPilot AI",
        f"# Vendor: {vendor}",
        f"# Template: {template_name}",
        f"# Context: {context}",
        "",
        "# (Template engine not yet implemented)",
    ]

    return "\n".join(output)
