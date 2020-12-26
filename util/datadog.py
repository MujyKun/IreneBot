from Utility import Utility
from datadog import initialize, api
import time

class DataDog(Utility):
    @staticmethod
    def initialize_data_dog():
        """Initialize The DataDog Class"""
        initialize()

    def send_metric(self, metric_name, value):
        """Send a metric value to DataDog."""
        # some values at 0 are important such as active games, this was put in place to make sure they are updated at 0.
        metrics_at_zero = ['bias_games', 'guessing_games', 'commands_per_minute', 'n_words_per_minute',
                           'bot_api_idol_calls', 'bot_api_translation_calls', 'messages_received_per_min',
                           'errors_per_minute', 'wolfram_per_minute', 'urban_per_minute']
        if metric_name in metrics_at_zero and not value:
            value = 0
        else:
            if not value:
                return
        if self.test_bot:
            metric_name = 'test_bot_' + metric_name
        else:
            metric_name = 'irene_' + metric_name
        api.Metric.send(metric=metric_name, points=[(time.time(), value)])

