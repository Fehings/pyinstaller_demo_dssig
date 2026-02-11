import os
import asyncio
import pandas as pd
from shiny import App, render, ui, reactive
import faicons as fa

# --- 1. MOCK DATA & CONFIGS ---
# Replaces your external YAML loading for the demo
policies = {
    "ALLOCATION_SCORE": {"description": "Score-based allocation", "algorithms": ["NORMAL", "PRIORITY"]},
    "RISK_ADJUSTED": {"description": "Survival benefit focus", "algorithms": ["WEIBULL_ADJUSTED"]}
}

ICONS = {
    "timeline": fa.icon_svg("hourglass-half"),
    "xmark": fa.icon_svg("circle-xmark"),
    "user": fa.icon_svg("user"),
}

# --- 2. UI LAYOUT (Stripped to Essentials) ---
app_ui = ui.page_fluid(
    ui.h2("Transplant Simulator - Lightweight Demo"),
    ui.navset_card_tab(
        ui.nav_panel(
            "Run Simulations",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h4("Configuration"),
                    ui.input_select("policy", "Select Policy:", choices=list(policies.keys())),
                    ui.input_numeric("years", "Years to Simulate:", value=10, min=1, max=50),
                    ui.input_action_button("run_button", "Run Dummy Sim", class_="btn-primary"),
                ),
                ui.page_fillable(
                    ui.layout_columns(
                        ui.value_box(
                            title="Avg Waitlist Deaths",
                            value=ui.output_text("deaths_out"),
                            showcase=ICONS["xmark"],
                            theme="danger",
                        ),
                        ui.value_box(
                            title="Avg Transplants",
                            value=ui.output_text("tx_out"),
                            showcase=ICONS["user"],
                            theme="success",
                        ),
                    ),
                    ui.card(
                        ui.card_header("Simulation Status"),
                        ui.output_text_verbatim("status_log"),
                    )
                ),
            ),
        ),
        ui.nav_panel(
            "User Guide",
            ui.markdown("""
                ### Deployment Test
                This is a stripped-back version of the app to test **PyInstaller** bundling.
                
                * **Server Check:** Does the window open?
                * **Asset Check:** Are the icons visible?
                * **Logic Check:** Does the button trigger the dummy loop?
            """)
        ),
    ),
)

# --- 3. SERVER LOGIC (Dummy Simulations) ---
def server(input, output, session):
    sim_results = reactive.Value({"deaths": 0, "transplants": 0})
    log_messages = reactive.Value("Ready to run...")

    @reactive.Effect
    @reactive.event(input.run_button)
    async def _run_sim():
        log_messages.set("Starting Dummy Simulation...")
        # Simulate an async background task (like your math engine)
        for i in range(1, 4):
            await asyncio.sleep(0.5)
            log_messages.set(f"Processing Batch {i}/3...")
        
        # Set dummy results
        sim_results.set({"deaths": 12, "transplants": 45})
        log_messages.set("Simulation Complete!")

    @render.text
    def deaths_out():
        return f"{sim_results.get()['deaths']}"

    @render.text
    def tx_out():
        return f"{sim_results.get()['transplants']}"

    @render.text
    def status_log():
        return log_messages.get()

app = App(app_ui, server)