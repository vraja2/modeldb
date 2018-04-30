"""
Event indicating that a metric has been computed for a model's prediction.
"""
from modeldb.events.Event import Event
from ..thrift.modeldb import ttypes as modeldb_types


class MetricEvent(Event):
    """
    Class for creating and storing MetricEvents
    """

    def __init__(
            self, df, model, labelCol, predictionCol, metricType, metricValue, metadata=None):
        self.df = df
        self.model = model
        self.metric_type = metricType
        self.metric_value = metricValue
        self.label_col = labelCol
        self.prediction_col = predictionCol
        self.metadata = metadata

    def make_event(self, syncer):
        """
        Constructs a thrift MetricEvent object with appropriate fields.
        """
        model_id = self.metadata['MODELDB_model_id'] if 'MODELDB_model_id' in self.metadata else None
        syncable_transformer = syncer.convert_model_to_thrift(self.model, model_id=model_id)
        syncable_dataframe = syncer.convert_df_to_thrift(self.df, self.metadata)
        me = modeldb_types.MetricEvent(
            syncable_dataframe,
            syncable_transformer,
            self.metric_type,
            self.metric_value,
            self.label_col,
            self.prediction_col,
            syncer.experiment_run.id)
        return me

    def associate(self, res, syncer):
        """
        Stores the server response ids into dictionary.
        """
        syncer.store_object(self.df, res.dfId)
        syncer.store_object(self.model, res.modelId)
        syncer.store_object(self, res.eventId)

    def sync(self, syncer):
        """
        Stores MetricEvent on the server.
        """
        me = self.make_event(syncer)
        thrift_client = syncer.client
        res = thrift_client.storeMetricEvent(me)
        self.associate(res, syncer)
