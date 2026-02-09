"""
Arcane.Http - HTTP Server Module
A Flask-like HTTP server framework for DataForge.
Built on Python's http.server with routing, middleware, JSON, and static files.
"""

import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class _DFRouter:
    """Route registry for the HTTP server."""
    def __init__(self):
        self.routes = {}       # {method: {path: handler}}
        self.middleware = []
        self.static_dir = None
        self.template_dir = None

    def add_route(self, method, path, handler):
        method = method.upper()
        if method not in self.routes:
            self.routes[method] = {}
        self.routes[method][path] = handler

    def find_route(self, method, path):
        method = method.upper()
        if method in self.routes:
            # Exact match
            if path in self.routes[method]:
                return self.routes[method][path], {}
            # Parametric match: /users/:id
            for pattern, handler in self.routes[method].items():
                params = self._match_pattern(pattern, path)
                if params is not None:
                    return handler, params
        return None, {}

    def _match_pattern(self, pattern, path):
        """Match /users/:id style patterns."""
        pat_parts = pattern.strip('/').split('/')
        path_parts = path.strip('/').split('/')
        if len(pat_parts) != len(path_parts):
            return None
        params = {}
        for pp, rp in zip(pat_parts, path_parts):
            if pp.startswith(':'):
                params[pp[1:]] = rp
            elif pp != rp:
                return None
        return params


class _DFRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for DataForge server."""
    router = None

    def _handle_request(self, method):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Static files
        if self.router.static_dir and path.startswith('/static/'):
            self._serve_static(path[8:])
            return

        handler, params = self.router.find_route(method, path)
        if handler is None:
            self._send_json(404, {"error": "Not Found", "path": path})
            return

        # Build request object
        body = ""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')

        req = {
            "method": method,
            "path": path,
            "query": {k: v[0] if len(v) == 1 else v for k, v in query.items()},
            "params": params,
            "headers": dict(self.headers),
            "body": body,
        }

        # Try to parse JSON body
        if body and self.headers.get('Content-Type', '').startswith('application/json'):
            try:
                req["json"] = json.loads(body)
            except json.JSONDecodeError:
                req["json"] = None

        # Build response helper
        response_data = {"status": 200, "headers": {"Content-Type": "application/json"}, "body": ""}

        def send(data, status=200):
            response_data["status"] = status
            if isinstance(data, dict) or isinstance(data, list):
                response_data["body"] = json.dumps(data, ensure_ascii=False, indent=2)
                response_data["headers"]["Content-Type"] = "application/json"
            else:
                response_data["body"] = str(data)
                if "<html" in str(data).lower():
                    response_data["headers"]["Content-Type"] = "text/html; charset=utf-8"
                else:
                    response_data["headers"]["Content-Type"] = "text/plain; charset=utf-8"

        def send_json(data, status=200):
            response_data["status"] = status
            response_data["body"] = json.dumps(data, ensure_ascii=False, indent=2)
            response_data["headers"]["Content-Type"] = "application/json"

        def send_html(html, status=200):
            response_data["status"] = status
            response_data["body"] = html
            response_data["headers"]["Content-Type"] = "text/html; charset=utf-8"

        def set_header(key, value):
            response_data["headers"][key] = value

        def status(code):
            response_data["status"] = code

        res = {
            "send": send,
            "json": send_json,
            "html": send_html,
            "header": set_header,
            "status": status,
        }

        # Run middleware
        for mw in self.router.middleware:
            try:
                mw(req, res)
            except Exception:
                pass

        # Run handler
        try:
            result = handler(req, res)
            if isinstance(result, dict) or isinstance(result, list):
                if not response_data["body"]:
                    send_json(result)
            elif isinstance(result, str):
                if not response_data["body"]:
                    send(result)
        except Exception as e:
            self._send_json(500, {"error": "Internal Server Error", "detail": str(e)})
            return

        # Send response
        self.send_response(response_data["status"])
        for k, v in response_data["headers"].items():
            self.send_header(k, v)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_data["body"].encode('utf-8'))

    def _serve_static(self, filepath):
        """Serve static files."""
        if not self.router.static_dir:
            self._send_json(404, {"error": "Static dir not configured"})
            return
        full_path = os.path.join(self.router.static_dir, filepath)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            self._send_json(404, {"error": f"File not found: {filepath}"})
            return
        ext = os.path.splitext(filepath)[1].lower()
        content_types = {
            '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
            '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
            '.gif': 'image/gif', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
            '.txt': 'text/plain', '.pdf': 'application/pdf',
        }
        ct = content_types.get(ext, 'application/octet-stream')
        with open(full_path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def do_PUT(self):
        self._handle_request('PUT')

    def do_DELETE(self):
        self._handle_request('DELETE')

    def do_PATCH(self):
        self._handle_request('PATCH')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def log_message(self, format, *args):
        method = args[0].split()[0] if args else '?'
        path = args[0].split()[1] if args and len(args[0].split()) > 1 else '?'
        status = args[1] if len(args) > 1 else '?'
        colors = {'2': '\033[1;32m', '3': '\033[1;33m', '4': '\033[1;31m', '5': '\033[1;31m'}
        color = colors.get(str(status)[0], '\033[0m')
        print(f"  {color}{method}\033[0m {path} → \033[1m{status}\033[0m")


class ArcaneHttp:
    """HTTP Server module for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Http",

            # Server creation
            "create": cls._create,
            "listen": cls._listen,
            "stop": cls._stop,

            # Routing
            "get": cls._get,
            "post": cls._post,
            "put": cls._put,
            "delete": cls._delete,
            "patch": cls._patch,
            "route": cls._route,

            # Middleware
            "use": cls._use,
            "cors": cls._cors,
            "logger": cls._logger_middleware,
            "json_parser": cls._json_parser,

            # Config
            "static": cls._static,
            "templates": cls._templates,

            # Utilities
            "json_response": cls._json_response,
            "html_response": cls._html_response,
        }

    @staticmethod
    def _create(name="DataForge App"):
        """Create a new HTTP application."""
        router = _DFRouter()
        return {
            "__type__": "HttpApp",
            "name": name,
            "_router": router,
            "_server": None,
        }

    @staticmethod
    def _get(app, path, handler):
        """Register a GET route."""
        app["_router"].add_route("GET", path, handler)

    @staticmethod
    def _post(app, path, handler):
        """Register a POST route."""
        app["_router"].add_route("POST", path, handler)

    @staticmethod
    def _put(app, path, handler):
        """Register a PUT route."""
        app["_router"].add_route("PUT", path, handler)

    @staticmethod
    def _delete(app, path, handler):
        """Register a DELETE route."""
        app["_router"].add_route("DELETE", path, handler)

    @staticmethod
    def _patch(app, path, handler):
        """Register a PATCH route."""
        app["_router"].add_route("PATCH", path, handler)

    @staticmethod
    def _route(app, method, path, handler):
        """Register a route with any HTTP method."""
        app["_router"].add_route(method, path, handler)

    @staticmethod
    def _use(app, middleware):
        """Add middleware to the app."""
        app["_router"].middleware.append(middleware)

    @staticmethod
    def _cors(app):
        """Add CORS middleware."""
        def cors_mw(req, res):
            res["header"]("Access-Control-Allow-Origin", "*")
            res["header"]("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
            res["header"]("Access-Control-Allow-Headers", "Content-Type, Authorization")
        app["_router"].middleware.append(cors_mw)

    @staticmethod
    def _logger_middleware(app):
        """Add request logging middleware."""
        def logger_mw(req, res):
            print(f"  \033[1;36m→\033[0m {req['method']} {req['path']}")
        app["_router"].middleware.append(logger_mw)

    @staticmethod
    def _json_parser(app):
        """Add JSON body parser middleware (already built-in)."""
        pass  # JSON parsing is built into the handler

    @staticmethod
    def _static(app, directory):
        """Set static files directory."""
        app["_router"].static_dir = directory

    @staticmethod
    def _templates(app, directory):
        """Set templates directory."""
        app["_router"].template_dir = directory

    @staticmethod
    def _listen(app, port=3000, host="0.0.0.0"):
        """Start the HTTP server."""
        _DFRequestHandler.router = app["_router"]
        server = HTTPServer((host, port), _DFRequestHandler)
        app["_server"] = server

        name = app.get("name", "DataForge App")
        print(f"\n\033[1;32m  🔥 {name} running!\033[0m")
        print(f"  \033[1;36m   → http://localhost:{port}\033[0m")
        print(f"  \033[0;90m   Press Ctrl+C to stop\033[0m\n")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\033[1;33m  ⚡ Server stopped.\033[0m")
            server.shutdown()

    @staticmethod
    def _stop(app):
        """Stop the HTTP server."""
        if app.get("_server"):
            app["_server"].shutdown()
            print("\033[1;33m  ⚡ Server stopped.\033[0m")

    @staticmethod
    def _json_response(data, status=200):
        """Create a JSON response dict."""
        return {"__json__": True, "data": data, "status": status}

    @staticmethod
    def _html_response(html, status=200):
        """Create an HTML response."""
        return html
