import unittest

from cdf.core.insights import (
    Aggregator,
    PositiveTrend,
    Insight,
    ComparisonAwareInsight,
    InsightValue,
    InsightTrendPoint
)
from cdf.query.filter import EqFilter
from cdf.query.sort import AscendingSort
from cdf.query.aggregation import MaxAggregation, SumAggregation


class TestInsight(unittest.TestCase):
    def setUp(self):
        self.identifier = "foo"
        self.name = "Foo"
        self.positive_trend = PositiveTrend.UP
        self.eq_filter = EqFilter("bar", 5)
        self.max_agg = MaxAggregation("depth")

    def test_query_nominal_case(self):
        insight = Insight(self.identifier,
                          self.name,
                          self.positive_trend,
                          self.eq_filter,
                          self.max_agg)
        expected_query = {
            "filters": {
                "field": "bar",
                "predicate": "eq",
                "value": 5
            },
            "aggs": [
                {"metrics": [{"max": "depth"}]}
            ]
        }
        self.assertEqual(expected_query, insight.query)

    def test_query_default_aggregation(self):
        insight = Insight(self.identifier,
                          self.name,
                          self.positive_trend,
                          self.eq_filter)
        expected_query = {
            "filters": {
                "field": "bar",
                "predicate": "eq",
                "value": 5
            },
            "aggs": [
                {"metrics": [{"count": "url"}]}
            ]
        }
        self.assertEqual(expected_query, insight.query)

    def test_query_no_filter(self):
        insight = Insight(self.identifier,
                          self.name,
                          self.positive_trend,
                          metric_agg=self.max_agg)
        expected_query = {
            "aggs": [
                {"metrics": [{"max": "depth"}]}
            ]
        }
        self.assertEqual(expected_query, insight.query)

    def test_aggregator(self):
        max_insight = Insight(self.identifier,
                              self.name,
                              self.positive_trend,
                              metric_agg=self.max_agg)
        self.assertEqual(Aggregator.MAX, max_insight.aggregator)

        sum_insight = Insight(self.identifier,
                              self.name,
                              self.positive_trend,
                              metric_agg=SumAggregation("foo"))
        self.assertEqual(Aggregator.SUM, sum_insight.aggregator)


    def test_repr(self):
        insight = Insight(self.identifier, self.name, self.positive_trend)
        self.assertEqual(
            "foo: {'aggs': [{'metrics': [{'count': 'url'}]}]}",
            repr(insight)
        )


class TestComparisonAwareInsight(unittest.TestCase):
    def setUp(self):
        self.identifier = "foo"
        self.name = "Foo"
        self.positive_trend = PositiveTrend.UP
        self.eq_filter = EqFilter("bar", 5)

    def test_nominal_case(self):
        insight = Insight(self.identifier,
                          self.name,
                          self.positive_trend,
                          self.eq_filter)
        insight = ComparisonAwareInsight(insight)
        expected_query = {
            "filters": {
                "and": [
                    {"or": [
                        {"not": {
                            "predicate": "exists",
                            "field": "disappeared"
                        }
                        },
                        {
                            "predicate": "eq",
                            "field": "disappeared",
                            "value": False
                        }
                    ]
                    },
                    {
                        "field": "bar",
                        "predicate": "eq",
                        "value": 5
                    }
                ]
            },
            "aggs": [
                {"metrics": [{"count": "url"}]}
            ]
        }
        self.assertEqual(expected_query, insight.query)
        expected_query_to_display = {
            "filters": {
                "field": "bar",
                "predicate": "eq",
                "value": 5
            },
            "aggs": [
                {"metrics": [{"count": "url"}]}
            ]

        }
        self.assertEqual(expected_query_to_display, insight.query_to_display)

    def test_no_filter(self):
        insight = Insight(self.identifier,
                          self.name,
                          self.positive_trend)
        insight = ComparisonAwareInsight(insight)
        expected_query = {
            "filters": {
                "or": [
                    {
                        "not": {
                            "predicate": "exists",
                            "field": "disappeared"
                        }
                    },
                    {
                        "predicate": "eq",
                        "field": "disappeared",
                        "value": False
                    }
                ]
            },
            "aggs": [
                {"metrics": [{"count": "url"}]}
            ]
        }
        self.assertEqual(expected_query, insight.query)
        expected_query_to_display = {
            "aggs": [
                {"metrics": [{"count": "url"}]}
            ]

        }
        self.assertEqual(expected_query_to_display, insight.query_to_display)

    def test_attribute_delegation(self):
        insight = Insight(self.identifier,
                          self.name,
                          self.positive_trend,
                          self.eq_filter)
        insight = ComparisonAwareInsight(insight)

        #getter is delegated to Insight
        self.assertEqual(self.positive_trend, insight.positive_trend)
        #but there should be an error if the field does not exist in Insight.
        self.assertRaises(
            AttributeError,
            getattr,
            insight,
            "foo"
        )


class TestInsightValue(unittest.TestCase):
    def setUp(self):
        self.insight = Insight(
            "foo",
            "Foo insight",
            PositiveTrend.UP,
            EqFilter("foo_field", 1001)
        )

        trend = [
            InsightTrendPoint(1001, 3.14),
            InsightTrendPoint(2008, 2.72)
        ]

        self.insight_value = InsightValue(self.insight,
                                          "foo_feature",
                                          trend)

    def test_to_dict(self):
        expected_dict = {
            "identifier": "foo",
            "name": "Foo insight",
            "positive_trend": "up",
            "feature": "foo_feature",
            "type": "integer",
            "unit": "url",
            "aggregator": "count",
            "query":  {
                'aggs': [{'metrics': [{'count': 'url'}]}],
                'filters': {'field': 'foo_field', 'predicate': 'eq', 'value': 1001}
            },
            "trend": [
                {"crawl_id": 1001, "score": 3.14},
                {"crawl_id": 2008, "score": 2.72}
            ]
        }
        self.assertEqual(
            expected_dict,
            self.insight_value.to_dict()
        )

    def test_additional_fields(self):
        self.insight.additional_fields = ["bar", "baz"]

        expected_value = ["bar", "baz"]
        self.assertEqual(
            expected_value,
            self.insight_value.to_dict()["additional_fields"]
        )

    def test_additional_filter(self):
        self.insight.additional_filter = EqFilter("bar_field", "bar")

        expected_value = {
            "field": "bar_field",
            'predicate': 'eq',
            'value': 'bar'
        }

        self.assertEqual(
            expected_value,
            self.insight_value.to_dict()['additional_filter']
        )

    def test_sort_by(self):
        self.insight.sort_by = AscendingSort("bar")

        expected_value = {"asc": "bar"}

        self.assertEqual(
            expected_value,
            self.insight_value.to_dict()["sort_by"]
        )


class TestInsightTrendPoint(unittest.TestCase):
    def test_to_dict(self):
        self.assertEqual(
            {"crawl_id": 1001, "score": 3.14},
            InsightTrendPoint(1001, 3.14).to_dict()
        )
