"""System information endpoint for fixbot"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sysdoc.core.executor import SysDocExecutor


def handler(request):
    """
    System information endpoint that returns system details
    
    Query parameters:
    - type: specific info type (cpu, memory, processes, all)
    """
    
    if request.method != "GET":
        return {
            "error": "Method not allowed. Use GET.",
            "allowed_methods": ["GET"]
        }, 405
    
    try:
        info_type = request.args.get("type", "all").lower()
        
        executor = SysDocExecutor()
        
        if info_type == "cpu":
            data = executor.get_cpu_info()
        elif info_type == "memory":
            data = executor.get_memory_info()
        elif info_type == "processes":
            data = executor.get_process_list()
        elif info_type == "all":
            data = {
                "cpu": executor.get_cpu_info(),
                "memory": executor.get_memory_info(),
                "timestamp": str(executor.get_timestamp())
            }
        else:
            return {
                "error": f"Unknown info type: {info_type}",
                "valid_types": ["cpu", "memory", "processes", "all"]
            }, 400
        
        return {
            "success": True,
            "type": info_type,
            "data": data
        }, 200
        
    except Exception as e:
        return {
            "error": f"Internal server error: {str(e)}"
        }, 500
