from django.db.models import QuerySet
from django.db import reset_queries, connection
import json
import time
from django.core import serializers
from django.core.paginator import Paginator

from .exceptions import NotFound


class BaseQuerySet(QuerySet):
	def detail(self):
		query = self._chain()
		rows = json.loads(serializers.serialize('json', query))
		for index, row in enumerate(rows):
			row['fields']['id'] = row['pk']
			row = row['fields']
			for i in self.model.exclude_fields:
				del row[i]
			for k, v in self.model.process_fields.items():
				row[k] = v(row.get(k, query[index]))
			rows[index] = row
		return rows

	def paginate(self, page_no):
		paginator = Paginator(self._chain(), 10)
		if page_no > paginator.num_pages:
			return paginator.num_pages, self.model.objects.none()
		return paginator.num_pages, paginator.get_page(page_no).object_list

	def get(self, **kwargs):
		try:
			return super().get(**kwargs)
		except self.model.DoesNotExist:
			raise NotFound(f'The {self.model._meta.model_name} requested for does not exist')


def query_debugger(func):
	def inner(*args, **kwargs):
		reset_queries()
		start = time.perf_counter()
		result = func(*args, **kwargs)
		queries = len(connection.queries)
		for i in connection.queries:
			print(f"============================\n{i['sql']}")
			print(f"Time taken: {i['time']}")
		print('============================')
		print(f"Number of Queries : {queries}")
		print('============================')
		return result

	return inner
