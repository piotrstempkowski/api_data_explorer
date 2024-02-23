from rest_framework import serializers


class CompanyStockSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    name = serializers.CharField()
    currency = serializers.CharField()
    stockExchange = serializers.CharField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        filtered_data = [record for record in ret if record['currency'] == 'USD']
        return filtered_data
