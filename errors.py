import json


OK = json.dumps({'errno': 0, 'info': 'OK'}), 200
BadRequest = json.dumps({'errno': 400, 'info': 'Bad Request'}), 400
Unauthorized = json.dumps({'errno': 401, 'info': 'Unauthorized'}), 401
NotFound = json.dumps({'errno': 404, 'info': 'Not Found'}), 404
