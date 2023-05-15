import dash

from .components import make_page_controls


class PageBuilder:
    def __init__(
        self,
        name: str,
    ):
        self.page_name = name.lower().replace(" ", "_")
        self.page_container_id = f"page_container_{self.page_name}"
        self.page_load_trigger_button_id = f"page_load_trigger_button_{self.page_name}"
        self.layout = dash.html.Div(
            children=[
                dash.html.Button(
                    id=self.page_load_trigger_button_id, style={"display": "none"}
                ),
            ],
            id=self.page_container_id,
            className="page dflex flex-column align-items-center",
        )

    def extend_layout(self, layout: dash.html.Div, position: int = 0) -> None:
        self.layout.children.insert(position, layout)

    def _regsiter_callbacks(self) -> None:
        dash.clientside_callback(
            """
            function(n_clicks) {
                onPageLoad();
                return 0;
            }
            """,
            dash.dependencies.Output(self.page_load_trigger_button_id, "n_clicks"),
            dash.dependencies.Input(self.page_load_trigger_button_id, "n_clicks"),
        )

    def build(self) -> dash.html.Div:
        self._regsiter_callbacks()
        return self.layout

    @property
    def elements(self) -> dict[str, str]:
        return {
            "PAGE_CONTAINER": self.page_container_id,
        }


class ProcessPageBuilder(PageBuilder):
    def __init__(self, name: str):
        super().__init__(name)
        self.stages = []
        self.stages_container_id = f"stages_container_{name}"
        self.stages_store_id = f"stages_store_{name}"
        self.next_stage_btn_id = f"next_stage_{name}"
        self.previous_stage_btn_id = f"previous_stage_{name}"
        self.stage_blocker_id = f"stage_blocker_{self.page_name}"
        self.layout.children.extend(
            [
                dash.html.Div(children=[], id=self.stages_container_id),
                dash.dcc.Store(id=self.stages_store_id, data=0),
                make_page_controls(
                    previous_stage_btn_id=self.previous_stage_btn_id,
                    next_stage_btn_id=self.next_stage_btn_id,
                ),
            ]
        )

    def make_stage_blocker(self) -> dash.dcc.Store:
        return dash.dcc.Store(
            id={"type": self.stage_blocker_id, "index": len(self.stages)}, data=False
        )

    def add_stage(self, stage: dash.html.Div) -> None:
        if type(stage.children) is not list:
            stage.children = [stage.children]
        stage.children.insert(0, self.make_stage_blocker())
        self.stages.append(stage)

    def add_stages(self, stages: list[dash.html.Div]) -> None:
        for stage in stages:
            self.add_stage(stage)

    def _regsiter_callbacks(self):
        super()._regsiter_callbacks()

        @dash.callback(
            [
                dash.Output(self.stages_container_id, "children"),
                dash.Output(self.stages_store_id, "data"),
            ],
            [
                dash.Input(self.next_stage_btn_id, "n_clicks"),
                dash.Input(self.previous_stage_btn_id, "n_clicks"),
            ],
            [
                dash.State(self.stages_store_id, "data"),
            ],
        )
        def update_stages(next_clicks, previous_clicks, current_stage):
            ctx = dash.callback_context
            triggered = ctx.triggered[0]["prop_id"].split(".")[0]
            if triggered == self.next_stage_btn_id:
                current_stage = min(current_stage + 1, len(self.stages) - 1)
            elif triggered == self.previous_stage_btn_id:
                current_stage = max(current_stage - 1, 0)
            return self.stages[current_stage], current_stage

        @dash.callback(
            [
                dash.Output(self.previous_stage_btn_id, "disabled"),
                dash.Output(self.next_stage_btn_id, "disabled"),
            ],
            [
                dash.Input(self.stages_store_id, "data"),
                dash.Input({"type": self.stage_blocker_id, "index": dash.ALL}, "data"),
            ],
        )
        def update_buttons(current_stage, values):
            blocker = values[0]
            cant_go_backward = current_stage <= 0
            cant_go_forward = (current_stage >= len(self.stages) - 1) or blocker
            return cant_go_backward, cant_go_forward

    @property
    def elements_raw(self) -> dict[str, str]:
        return {
            "STAGES_CONTAINER": self.stages_container_id,
            "STAGES_STORE": self.stages_store_id,
            "NEXT_BTN": self.next_stage_btn_id,
            "PREV_BTN": self.previous_stage_btn_id,
            "BLOCKER": self.stage_blocker_id,
            **super().elements_raw,
        }

    def build(self) -> dash.html.Div:
        return super().build()
