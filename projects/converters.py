# projects/converters.py
class ProjectIDConverter:
    regex = r'[^/]+(/[^/]+)*'  # Allows slashes
    
    def to_python(self, value):
        return value
    
    def to_url(self, value):
        return str(value)