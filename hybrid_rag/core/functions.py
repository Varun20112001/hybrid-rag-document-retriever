import logging
import sys
from typing import Optional, Dict, Any
from rest_framework import status
import rest_framework.response as r
logger = logging.getLogger("project")

def unknown_exception_logger(e:Exception):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    logger.error(f"Exception is: {e}\nException type: {str(exception_type)}\nFile name: {str(filename)}\nLine number: {str(line_number)}")
    return f"{e}"


def create_response(
    message: Optional[str] = None, 
    data: Optional[Dict[str,Any]]= None,
    exception: Optional[Exception]= None,
    pagination: Optional[Dict[str,Any]]= None,
    code: Optional[Any] = None
)->Dict[str,Any]:
    code=code if code else status.HTTP_200_OK
    response={"status":True}
    if message:
        response["message"]=message
    if data:
        response["data"]=data
    if exception:
        response["error"]=unknown_exception_logger(exception)
        response["status"]=False
        code=status.HTTP_500_INTERNAL_SERVER_ERROR
    if pagination:
        response["pagination"]=pagination

    return r.Response(data=response, status=code)