# ============ frontend/gradio_app/styles/theme.py ============
import gradio as gr


def get_custom_theme():
    """Create custom Gradio theme"""
    return gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate",
        spacing_size="md",
        radius_size="md",
        text_size="md",
        font=[
            gr.themes.GoogleFont("Inter"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ],
        font_mono=[
            gr.themes.GoogleFont("JetBrains Mono"),
            "ui-monospace",
            "Consolas",
            "monospace",
        ],
    ).set(
        body_background_fill="*neutral_50",
        body_text_color="*neutral_800",
        button_primary_background_fill="*primary_600",
        button_primary_background_fill_hover="*primary_700",
        button_primary_text_color="white",
        button_secondary_background_fill="*neutral_100",
        button_secondary_background_fill_hover="*neutral_200",
        block_background_fill="white",
        block_border_color="*neutral_200",
        block_border_width="1px",
        block_border_width_dark="1px",
        block_radius="8px",
        input_background_fill="white",
        input_border_color="*neutral_300",
        input_border_width="1px",
    )
