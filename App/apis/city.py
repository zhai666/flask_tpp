from flask_restful import Resource, fields, marshal_with

from App import dao
from App.models import Letter


class CityApi(Resource):

    # 城市的字段
    city_fields = {
        "id":fields.Integer,
        "parentId":fields.Integer,
        "regionName": fields.String,
        "cityCode": fields.Integer,
        "pinYin": fields.String
    }

    # 城市字母的输出字段
    value_fields = {
        # "A": fields.Nested(city_fields),
        # "B": fields.Nested(city_fields)
    }

    out_fields = {
        "returnCode": fields.String(default='0'),
        "returnValue": fields.Nested(value_fields)
    }

    @marshal_with(out_fields)
    def get(self):
        letters = dao.queryAll(Letter)

        returnValue = {}
        for letter in letters:
            self.value_fields[letter.name] = fields.Nested(self.city_fields)

            returnValue[letter.name] = letter.citys

        return {'returnValue': returnValue}