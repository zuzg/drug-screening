import dash

from .components import make_page_controls_rich_widget


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
        """
        Add a layout to the page layout

        :param layout: new element to add
        :param position: position where element is to be added, defaults to 0, i.e. at the beginning
        """
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
        """
        Build the page layout and register callbacks

        :return: built page layout
        """
        self._regsiter_callbacks()
        return self.layout

    @property
    def elements(self) -> dict[str, str]:
        """
        Get ids of special elements

        :return: dictionary of special elements ids
        """
        return {
            "PAGE_CONTAINER": self.page_container_id,
        }


class ProcessPageBuilder(PageBuilder):
    def __init__(self, name: str):
        super().__init__(name)
        self.stages = []
        self.stage_names = []
        self.stages_container_id = f"stages_container_{self.page_name}"
        self.stages_store_id = f"stages_store_{self.page_name}"
        self.next_stage_btn_id = f"next_stage_{self.page_name}"
        self.previous_stage_btn_id = f"previous_stage_{self.page_name}"
        self.stage_blocker_id = f"stage_blocker_{self.page_name}"
        self.dummy_id = f"dummy_{self.page_name}"
        self.layout.children.extend(
            [
                dash.dcc.Store(id=self.stages_store_id, data=0),
                dash.html.Div(
                    children=[],
                    id=self.stages_container_id,
                    className="flex-grow-1 w-100 mt-4",
                ),
                dash.html.Div(
                    id=self.dummy_id,
                ),
            ]
        )

    def make_stage_blocker(self) -> dash.dcc.Store:
        return dash.dcc.Store(
            id={"type": self.stage_blocker_id, "index": len(self.stages)}, data=True
        )

    def add_stage(self, stage: dash.html.Div, name: str) -> None:
        """
        Register new stage in the process page

        :param stage: stage to be added (layout)
        :param name: name of the stage
        """
        if type(stage.children) is not list:
            stage.children = [stage.children]
        stage.children.insert(0, self.make_stage_blocker())
        self.stages.append(stage)
        self.stage_names.append(name)

    def add_stages(self, stages: list[dash.html.Div], names: list[str]) -> None:
        """
        Register new stages in the process page

        :param stages: stages to be added (layouts)
        :param names: names of the stages
        """
        if len(stages) != len(names):
            raise ValueError("Number of stages and names must be equal")
        for stage, name in zip(stages, names):
            self.add_stage(stage, name)

    def _regsiter_callbacks(self):
        super()._regsiter_callbacks()

        @dash.callback(
            [
                dash.Output(self.stages_container_id, "children"),
                dash.Output(self.stages_store_id, "data"),
                dash.Output(self.next_stage_btn_id, "disabled", allow_duplicate=True),
            ],
            [
                dash.Input(self.next_stage_btn_id, "n_clicks"),
                dash.Input(self.previous_stage_btn_id, "n_clicks"),
            ],
            [
                dash.State(self.stages_store_id, "data"),
            ],
            prevent_initial_call="initial_call",
        )
        def update_stages(next_clicks, previous_clicks, current_stage):
            ctx = dash.callback_context
            triggered = ctx.triggered[0]["prop_id"].split(".")[0]
            disable_next_stage_btn = dash.no_update
            if triggered == self.next_stage_btn_id:
                current_stage = min(current_stage + 1, len(self.stages) - 1)
                disable_next_stage_btn = True
            elif triggered == self.previous_stage_btn_id:
                current_stage = max(current_stage - 1, 0)
            return self.stages[current_stage], current_stage, disable_next_stage_btn

        @dash.callback(
            [
                dash.Output(self.previous_stage_btn_id, "disabled"),
                dash.Output(self.next_stage_btn_id, "disabled", allow_duplicate=True),
            ],
            [
                dash.Input(self.stages_store_id, "data"),
                dash.Input({"type": self.stage_blocker_id, "index": dash.ALL}, "data"),
            ],
            prevent_initial_call=True,
        )
        def update_buttons(current_stage, values):
            blocker = values[0]
            cant_go_backward = current_stage <= 0
            cant_go_forward = (current_stage >= len(self.stages) - 1) or blocker
            return cant_go_backward, cant_go_forward

        dash.clientside_callback(
            """
            function(n_clicks) {
                onStageIndexChange(n_clicks);
            }
            """,
            dash.Output(self.dummy_id, "children"),
            dash.Input(self.stages_store_id, "data"),
            allow_duplicate=True,
        )

    def build(self) -> dash.html.Div:
        """
        Build the page layout and register callbacks

        :return: built page layout
        """
        self.layout.children.insert(
            0,
            make_page_controls_rich_widget(
                previous_stage_btn_id=self.previous_stage_btn_id,
                next_stage_btn_id=self.next_stage_btn_id,
                stage_names=self.stage_names,
            ),
        )
        return super().build()

    @property
    def elements(self) -> dict[str, str]:
        """
        Get ids of special elements

        :return: dictionary of special elements ids
        """
        return {
            "STAGES_CONTAINER": self.stages_container_id,
            "STAGES_STORE": self.stages_store_id,
            "NEXT_BTN": self.next_stage_btn_id,
            "PREV_BTN": self.previous_stage_btn_id,
            "BLOCKER": self.stage_blocker_id,
            **super().elements,
        }
