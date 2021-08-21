"""Data collectors."""
import itertools

from mesa.datacollection import DataCollector
import pandas as pd

from geocovid.constants import STEPS_PER_DAY


class AggDataCollector(DataCollector):
    """Data Collector with aggregation."""

    def get_agent_vars_dataframe(self):
        """
        Create a pandas DataFrame from the agent variables.

        The DataFrame has one column for each variable, with two additional
        columns for tick and agent_id.
        """
        subset_records = [
            record
            for step, record in self._agent_records.items()
            if step % STEPS_PER_DAY == 0
        ]
        records_iterable = itertools.chain.from_iterable(subset_records)
        rep_names = [rep_name for rep_name in self.agent_reporters]

        df_agents = pd.DataFrame.from_records(
            data=records_iterable, columns=["Step", "AgentID"] + rep_names,
        )
        df_agents = df_agents.set_index(["Step", "AgentID"])
        return df_agents
