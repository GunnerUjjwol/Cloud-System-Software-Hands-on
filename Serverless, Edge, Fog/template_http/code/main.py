import os
import tempfile    # To create temporary file before uploading to bucket
from google.cloud import storage
from flask import escape
# Add any imports that you may need, but make sure to update requirements.txt


def create_file_http(request):
	# TODO: Add logic here
	request_json = request.get_json(silent=True)

    fileid = request_json['fileid']

    return