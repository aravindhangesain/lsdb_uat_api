import rest_framework.pagination
from rest_framework.pagination import _positive_int as _positive_int

class CustomPagination(rest_framework.pagination.LimitOffsetPagination):

    def get_limit(self, request):

        if self.limit_query_param:
            try:
                limit_param = request.query_params.get(self.limit_query_param)
                if limit_param:
                    if int(limit_param) < 0:
                        # limit_param = self.count
                        limit_param = 999999999
                else:
                     limit_param = request.query_params[self.limit_query_param]
                return _positive_int(
                    limit_param,
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit
